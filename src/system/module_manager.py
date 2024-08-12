import sys
sys.dont_write_bytecode = True
from typing import Callable
from discord.ext.commands.errors import NoEntryPointError
from src.connector import shared

from xRedUtilsAsync.type_hints import SIMPLE_ANY
from xRedUtilsAsync.modules.reloader import load_module, unload_module

class ModuleManager:
    async def _plugin_load(self, cls: Callable, config: dict[Callable, list[str]], tasks: list[Callable] = None) -> None:
        """Helper method to deal with Rexus plugins"""
        # load/overwrite plugin class into the memory
        shared.plugins[cls.__module__] = cls
        
        # iterates the config
        for callable, events_list in config.items():
            for event in events_list:
                # check if event exist, otherwise creates one
                if not shared.plugin_filter.get(event):
                    shared.plugin_filter[event] = []
                
                # checks if it already exists, otherwise adds it
                if callable not in shared.plugin_filter.get(event):
                    shared.plugin_filter[event].append(callable)

        # starting plugin tasks
        for task in tasks or []:
            shared.plugin_tasks.append(shared.loop.create_task(task(), name=f"{task.__module__}.{task.__qualname__}"))

    async def _module_load(self, cls: Callable, config: dict[str, str | Callable]) -> None:
        """Helper method to deal with normal modules"""
        # overwrite/create to the specified location
        if (location := config.get("location")) and (var := config.get("var")):
            setattr(location, var, cls)

        ### NOTE: more configs can be added
    
    async def load(self, cls: Callable | str, config: dict = None, tasks: list[Callable] = None) -> None:
        # loading into system
        path: str = cls if isinstance(cls, str) else cls.__module__
        if not sys.modules.get(path):
            try:
                return await shared.bot.load_extension(path) # NOTE: Return: None
            except NoEntryPointError:
                cls = await load_module(path) # NOTE: Return: module

        # setups
        if config:
            if config.get("module"):
                await self._module_load(cls, config)
            else:
                await self._plugin_load(cls, config, tasks)

    async def unload(self, path: str) -> None:
        # if plugin
        if (plugin := shared.plugins.get(path)):
            # kill tasks
            for task in shared.plugin_tasks:
                if task.get_name().startswith(f"{plugin.__class__.__module__}.{plugin.__class__.__name__}"):
                    task.cancel()
                    shared.plugin_tasks.remove(task)
                    try:
                        await task
                    except: pass

            # update filter
            for listener, callables in shared.plugin_filter.items():
                for func in callables:
                    if func.__self__ == plugin:
                        shared.plugin_filter[listener].remove(func)

            # removing from the plugins dict
            shared.plugins.pop(path)

        # laoded by discord.py
        if shared.bot.extensions.get(path):
            await shared.bot.unload_extension(path)
        else:
            await unload_module(path)

    async def reload(self, path: str) -> Callable:
        # check if the module exist
        if not (module := sys.modules.get(path)):
            return

        # save important data to RAM db - ig plugin
        old_data: dict[str, SIMPLE_ANY] = dict()
        
        if plugin := shared.plugins.get(path):
            for var in getattr(module, "SAVE", []):
                old_data[var] = getattr(plugin, var)

        # unload and load back from the Rexus system, sys.modules and discord.py library
        await self.unload(path)
        await self.load(path)

        # migrating saved data - if plugin
        if plugin := shared.plugins.get(path):
            for var, data in old_data.items():
                setattr(plugin, var, data)

async def setup(bot) -> None:
    await shared.module_manager.load(ModuleManager(),
        config={
            "module": True,
            "location": shared,
            "var": "reloader"
        }
    )

