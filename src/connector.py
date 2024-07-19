import sys, aiohttp, asyncio, schedule, re
sys.dont_write_bytecode = True
from discord.ext import commands
from typing import Callable

from xRedUtilsAsync import (
    system,
    typehints
)
from xRedUtilsAsync.colors import Foreground16 as FG

class Shared:
    bot: commands.Bot = None
    path: str = None
    OS: str = system.OS
    session: aiohttp.ClientSession = None

    plugins: dict[str, Callable] = {}
    plugin_filter: dict[str, list[Callable]] = {}
    plugin_tasks: list[asyncio.Task] = []

    system_modules: dict[str, dict[str, typehints.SIMPLE_ANY]] = {
        "logger": {
            "levels": {
                "CRITICAL": (50, FG.RED),
                "ERROR": (40, FG.BRIGHT_RED),
                "WARNING": (30, FG.BRIGHT_YELLOW),
                "UPDATE": (25, FG.GREEN),
                "SYSTEM": (22, None),
                "INFO": (20, FG.BLUE),
                "TESTING": (18,  FG.MAGENTA),
                "DEBUG": (10, FG.BRIGHT_WHITE),
                "NOTSET": (0, None)
            },
            "handlers": {
                "Console": (18, None, "\x1b[30;1m%(asctime)s\x1b[0m {lvl_c}%(levelname)-10s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s\x1b[0m"),
                "Testing": (1, f"./logs/testing.log", "[%(asctime)s] [%(levelname)-10s] %(name)s: %(message)s"),
            }
        }
    }

    schedule_jobs: list[schedule.Job] = []
    global_db: dict[str, typehints.SIMPLE_ANY] = {
        "returned_events": {},
        "invite_links": {
            "regex": re.compile(r"(?:https?\:\/\/)?discord(?:\.gg|(?:app)?\.com\/invite)\/[^/]+", re.IGNORECASE),
            "simon": {},
            "scam_guilds": {}
        }
    }

    # system required
    def system_load(self) -> None:
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        # system modules
        from src.system.database import Database
        from src.system.logging import Logger
        from src.system.reloader import Reloader

        self.db = Database()
        self.logger: Logger = Logger()
        self.reloader = Reloader()

        # main modules
        from src.core.queue import QueueSystem

        self.queue = QueueSystem()

        # security modules
        from src.core.root.execution_reports import ExecReport
        self.execution_reports = ExecReport()

        # helper modules
        from src.core.helpers.string_formats import StringFormats
        self.string_formats = StringFormats()

    async def add_plugin(self, cls: Callable, config: dict[Callable, list[str]], tasks: list[Callable] = None) -> None:
        # check if plugin module even exist
        if not sys.modules.get(cls.__module__):
            return await self.bot.load_extension(cls.__module__)
        
        # load/overwrite plugin class into the memory
        self.plugins[cls.__module__] = cls
        plugin: Callable = self.plugins[cls.__module__]

        # iterates the config
        for func, events_list in config.items():
            for event in events_list:
                # check if event exist, otherwise creates one
                if not self.plugin_filter.get(event):
                    self.plugin_filter[event] = []
                
                # gets callable and check if it already exists, otherwise adds it
                if (callable := getattr(plugin, func.__name__, None)) and callable not in self.plugin_filter.get(event):
                    self.plugin_filter[event].append(callable)

        # starting plugin tasks
        for task in tasks or []:
            if plugin_task := getattr(plugin, task.__name__, None):
                self.plugin_tasks.append(self.loop.create_task(plugin_task(), name=plugin_task.__qualname__))

    async def remove_plugin(self, cls: Callable, listeners: list[str]) -> None:
        path_id: str = cls.__module__

        # remove plugin callables from event listeners        
        for event in listeners:
            for callable in self.plugin_filter.get(event).copy():
                if callable.__class__.__module__== path_id:
                    self.plugin_filter[event].remove(callable)

        # stop tasks
        for task in self.plugin_tasks.copy():
            if task.get_name() == path_id:
                # removes and ends task
                task.cancel()
                self.plugin_tasks.remove(task)
                try:
                    await task
                except: pass

#making global class var, so data is presistent
shared: Shared = Shared()

"""
plugin_filter = {
    "on_message": [(callable, "impersonator"), (callable, None), ()]
}
"""