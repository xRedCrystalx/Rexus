import sys, typing
sys.dont_write_bytecode = True
from src.connector import shared

from xRedUtilsAsync.type_hints import SIMPLE_ANY

class Reloader:
    async def load(self, cls: typing.Callable | str, config: dict[typing.Callable, list[str]], tasks: list[typing.Callable] = None) -> object:
        # check if plugin module even exist
        if not sys.modules.get(cls if isinstance(cls, str) else cls.__module__):
            return await shared.bot.load_extension(cls if isinstance(cls, str) else cls.__module__)

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
            shared.plugin_tasks.append(shared.loop.create_task(task(), name=f"{task.__class__.__module__}.{task.__qualname__}"))
        return cls

    async def unload(self, path: str) -> None:
        # plugin - running class instance
        if not (plugin := shared.plugins.get(path)):
            return

        # removing from the plugins dict
        shared.plugins.pop(path)

        # kill tasks
        for task in shared.plugin_tasks:
            if task.get_name().startswith(f"{plugin.__module__}.{plugin.__name__}"):
                task.cancel()
                shared.plugin_tasks.remove(task)
                try:
                    await task
                except: pass

        # update filter
        for listener, callables in shared.plugin_filter.items():
            for func in callables:
                if func.__class__ == plugin:
                    shared.plugin_filter[listener].remove(func)
        
        # call discord.py finisher
        await shared.bot.unload_extension(path)

    async def reload(self, path: str) -> object:
        # check if the plugin exist
        if not (plugin := shared.plugins.get(path)):
            return

        # save important data to RAM db
        old_data: dict[str, SIMPLE_ANY] = dict()
        for var in getattr(plugin, "CLS_SAVE"):
            old_data[var] = getattr(plugin, var.__name__)

        # unload and load back from the Rexus system and discord.py library
        await self.unload(path)
        cls: object = await self.load(path, config=dict())

        # migrating saved data
        for var, data in old_data.items():
            setattr(cls, var, data)

        return cls
