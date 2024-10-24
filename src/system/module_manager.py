import sys, asyncio, gc as garbage_collector
sys.dont_write_bytecode = True
from src.connector import shared, BaseTemplate
from typing import Literal
from types import MethodType, ModuleType

from discord.ext.commands import Cog, Bot
from discord.ext.commands.errors import ExtensionNotFound, NoEntryPointError, ExtensionAlreadyLoaded

from xRedUtilsAsync.type_hints import SIMPLE_ANY
from xRedUtilsAsync.strings import levenshtein_distance
from xRedUtilsAsync.objects import get_full_object_path
from xRedUtilsAsync.iterables import compare_iterables

"""
#r Manager rules:

each module requires:
async def setup(bot) -> None: ...

#a SAVE variable
SAVE = {
    CallableObject: list[str]
}

#g if listener or command
.load(
    cls = CalledObject
    option = "discord"
    config = .add_cog kwargs
)

#g if plugin
.load(
    cls = CalledObject
    option = "plugin"
    config = {
        CallableMethod: list[str]
    }
    tasks = Optional[list[CallableMethod]]
)

#g if normal class
.load(
    cls = CalledObject
    option = "normal"
    config = {
        "var": str
        "location": CalledObject
    }
)
"""

OPTIONS = Literal["system", "discord", "plugin"]

class ModuleManager:
    def __init__(self) -> None:
        self.resolver: dict[str, list[asyncio.Task]] = {
            "system": shared.system_tasks,
            "plugins": shared.plugin_tasks
        }


    def _get_classes_of_module(self, module: ModuleType) -> list[type]:
        return [obj for obj in module.__dict__.values() if isinstance(obj, type)]
    
    def _get_running_objects(self, cls: type) -> list[object]:
        return [obj for obj in garbage_collector.get_objects() or [] if isinstance(obj, cls)]

    async def _guess_path(self, path: str) -> str:
        """ Checks the levenshtein distance - simple way of trying to find out matches """
        for p in sys.modules.keys():
            distance: int = await levenshtein_distance(path, p)
            
            if distance <= 3:
                return p
    

    async def create_tasks(self, tasks: list[MethodType], _o: OPTIONS) -> None:
        """Creates asyncio task @ _o option"""
        for task in tasks or []:
            self.resolver[_o].append(
                shared.loop.create_task(task(), name=await get_full_object_path(task))
            )
    
    async def terminate_tasks(self, module_path: str, _o: OPTIONS) -> None:
        """Terminates all tasks from the module (all object's tasks)"""
        for task in self.resolver.get(_o, []):

            # if it matches module path, cancel and remove task
            if task.get_name().startswith(module_path):
                try:
                    task.cancel()
                    await asyncio.sleep(0)

                    await task
                except: pass

                self.resolver[_o].remove(task)

    async def update_plugin_filter(self, config: dict[MethodType, list[str]] | str) -> None:
        """Adds/removes methods from plugin filter"""

        if isinstance(config, dict):
            # iterates the config
            for callable, events_list in config.items():
                for event in events_list:
                    # check if event exist, otherwise creates one
                    if not shared.plugin_filter.get(event):
                        shared.plugin_filter[event] = []
                    
                    # checks if it already exists, otherwise adds it
                    if callable not in shared.plugin_filter.get(event):
                        shared.plugin_filter[event].append(callable)
        else:
            if not sys.modules.get(config):
                return

            # removes callables with matching module path
            for listener, callables in shared.plugin_filter.items():
                [shared.plugin_filter[listener].remove(func)
                    for func in callables
                    if func.__module__ == config
                ] 

    
    async def load(self, obj: BaseTemplate | str, option: OPTIONS = None,  config: dict[str, SIMPLE_ANY] = None, tasks: list[MethodType] = None) -> None:
        """
        Loads module into the runtime. 

        ### Arguments:
        - `obj` - ModulePath or CalledObject
        - `option` - type of class object
        - `config` - configuration of how module should be loaded
        - `tasks` - background tasks
        """

        #d pre-requirement - str can only be ModulePath
        if isinstance(obj, str):
            module_path: str = obj
            try:
                await shared.bot.load_extension(module_path)

            # error loggers
            except ExtensionNotFound:
                guessed_path: str = await self._guess_path(module_path)
                shared.logger.log("ERROR", f"@ModuleManager.load > Could not resolve `{module_path}`  -  Did you mean `{guessed_path}`?")

            except NoEntryPointError:
                shared.logger.log("ERROR", f"@ModuleManager.load > Missing entry point (setup function) in module `{module_path}`. ")
            
            except ExtensionAlreadyLoaded:
                shared.logger.log("WARNING", f"@ModuleManager.load > Module already loaded. Reload or unload it.")
            
            except Exception as error:
                shared.logger.log("ERROR", f"@ModuleManager.load > {type(error).__name__}: {error}")

        # object - manipulation
        else:
            if option == "discord" and isinstance(obj, Cog):
                await shared.bot.add_cog(obj, **(config or dict())) # NOTE: could potentially error out

            elif option == "plugin":
                shared.plugins[obj._full_self_path] = obj

                await self.update_plugin_filter(config)
                await self.create_tasks(tasks, option)

            elif option in "system":
                if not ( (location := config.get("location")) and (var := config.get("var")) ):
                    setattr(location, var, obj)
                
                    await self.create_tasks(tasks, option)
                else:
                    shared.logger.log("ERROR", f"@ModuleManager.load > System module requires `location` and `var`. Missing: {obj._full_self_path}")
                    return
            
            else:
                shared.logger.log("WARNING", f"@ModuleManager.load > Nothing happened. Please check object configuration. Path: `{obj._full_self_path}`")
                return
            
            # running build method, if any
            if build_method := getattr(obj, "build", None):
                try:
                    await build_method()
                except Exception as error:
                    shared.logger.log("ERROR", f"@ModuleManager.load > {type(error).__name__}: {error}")
                    
                    # unload - safety
                    await self.unload(obj.__module__)

    async def unload(self, path_or_module: str | ModuleType) -> None:
        """
        Unloads module in the running instance. 

        ### Arguments:
        - `path_or_module` - ModulePath or ModuleType
        """
        # NOTE: module can have multiple objects

        # checks if its path and gets the module
        if isinstance(path_or_module, str):
            path_or_module: MethodType = sys.modules.get(path_or_module)

        if not path_or_module:
            return
        
        # tries to get all classes in module and all running objects of those classes
        for object_type in self._get_classes_of_module(path_or_module):
            for obj in self._get_running_objects(object_type):
                obj: BaseTemplate

                option: str = obj._type             # INFO: BaseTemplate attribute
                path: str = obj._full_self_path     # INFO: BaseTemplate attribute

                # custom termination
                if terminate_method := getattr(obj, "terminate", None):
                    try:
                        await terminate_method()
                    except Exception as error:
                        shared.logger.log("ERROR", f"@ModuleManager.unload > {type(error).__name__}: {error}")

                # terminate tasks
                await self.terminate_tasks(path, option)

                if option == "plugin":
                    await self.update_plugin_filter(path)
                    shared.plugins.pop(path)

                elif option == "discord":
                    await shared.bot.remove_cog(obj)

                #d pre-condition: system module must be in `shared` object
                elif option == "system":
                    delattr(shared, str(obj._var))  # INFO: SystemTemplate attribute

        #d pre-condition: has to be loaded with discord.py
        return await shared.bot.unload_extension(path)

    async def reload(self, path: str) -> None:
        """
        Reloads module in the running instance. 

        ### Arguments:
        - `path` - ModulePath
        """
         
        if not (module := sys.modules.get(path)):
            return
        
        old_data: dict[str, dict[str, SIMPLE_ANY]] = dict()
        save_config: dict[type, list[str]] = getattr(module, "SAVE", {})
        
        # saving data of each object
        for object_type in self._get_classes_of_module(path):
            for obj in self._get_running_objects(object_type):
                obj: BaseTemplate
                
                if obj.__class__ not in save_config:
                    continue

                for var in save_config[obj.__class__]:
                    old_data[obj.ID][var] = getattr(obj, var)   # INFO: BaseTemplate attribute

        # unload and load back from the Rexus runtime and discord.py library
        await self.unload(path)
        await self.load(path)

        # migrating saved data
        for object_type in self._get_classes_of_module(path):
            for obj in self._get_running_objects(object_type):
                obj: BaseTemplate

                if obj.ID not in old_data:
                    continue

                for var, data in old_data[obj.ID].items():
                    setattr(obj, var, data)


SAVE: dict[type, list[str]] = {
    ModuleManager: ["cache"]
}

async def setup(bot: Bot) -> None:
    await shared.module_manager.load(ModuleManager(), option="system",
        config={
            "location": shared,
            "var": "module_manager"
        }
    )
