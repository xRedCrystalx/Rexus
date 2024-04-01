import sys, datetime, uuid, typing, platform, os, aiohttp, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands


class Shared:
    bot: commands.Bot = None ##ADD IT
    path: str = None
    OS: str = platform.system()
    session: aiohttp.ClientSession = None
    
    import src.system.colors as colors_module
    colors: colors_module.C | colors_module.CNone = colors_module.auto_color_handler()
    
    # system required
    def system_load(self) -> None:
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        
        # system modules
        import src.system.database as db_module
        import src.system.logging as logger_module
        import src.system.reloader as reload_module

        self.db: db_module.Database = db_module.Database()
        self.logger: logger_module.Logger = logger_module.Logger().main()
        self.reloader: reload_module.Reloader = reload_module.Reloader()

        # main modules
        import src.core.transmitters.sender as sender_module
        import src.core.transmitters.queue as queue_module

        self.sender: sender_module.Sender = sender_module.Sender()
        self.queue: queue_module.QueueSystem = queue_module.QueueSystem()

        # security modules
        import src.core.root.execution_reports as exec_report

        self.execution_reports: exec_report.ExecReport = exec_report.ExecReport()

    def plugin_load(self) -> None:
        from src.core.plugins.impersonator_detection import ImpersonatorDetection
        from src.core.plugins.AI import AI
        from src.core.plugins.ping_protection import PingProtection
        from src.core.plugins.auto_slowmode import AutoSlowmode
        from src.core.plugins.message_handlers import MessageHandlers
        from src.core.plugins.QOFTD import QOFTD
        from src.core.plugins.auto_deleter import AutoDeleter
        from src.core.plugins.miscellaneous_handlers import MiscellaneousHandlers
        from src.core.plugins.reaction_filter import ReactionFilter
        from src.core.plugins.spy import Spy
        from src.core.helpers.images import Images

        self.imper_detection = ImpersonatorDetection()
        self.AI = AI()    
        self.ping_prot = PingProtection()
        self.message_handlers = MessageHandlers()
        self.auto_deleter = AutoDeleter()
        self.QOFTD = QOFTD()
        self.auto_slowmode = AutoSlowmode()
        self.miscellaneous = MiscellaneousHandlers()
        self.reaction_filter = ReactionFilter()
        self.spy = Spy()
        self.images = Images()

        loader: tuple[typing.Callable] = (self.auto_slowmode.start, self.QOFTD.start, self.auto_deleter.start, self.reaction_filter.start, self.sender.start)
        self.plugin_tasks: list[asyncio.Task] = [self.loop.create_task(func(), name=func.__qualname__) for func in loader]

        self.queue.reload_filters()

    def _datetime(self) -> datetime:
        return datetime.datetime.now()

    def _create_id(self) -> str:
        return str(uuid.uuid1())

    def _completion_bar(self, total: int, completed: int, _len: int = 15) -> str:
        percentage: float = (completed / total) * 100
        completed_bar = int(_len * percentage / 100)
        remaining_bar: int = _len - completed_bar
        bar: str = "[" + "#" * completed_bar + "-" * remaining_bar + "]"
 
        return f"{bar} {percentage:.1f}%"

    def seconds_to_string(self, seconds) -> str:
        units: list[tuple[str, int]] = [("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
        time_str = []

        for unit, value in units:
            if seconds >= value:
                count, seconds = divmod(seconds, value)
                time_str.append(f"{count} {unit}{'s' if count != 1 else ''}")

        return ", ".join(time_str) if time_str else "0 seconds"


#making global class var, so data is presistent
shared: Shared = Shared()
