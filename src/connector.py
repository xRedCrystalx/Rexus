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

        loader: tuple[typing.Callable] = (self.auto_slowmode.start, self.QOFTD.start, self.auto_deleter.start, self.reaction_filter.start, self.sender.start)
        self.plugin_tasks: list[asyncio.Task] = [self.loop.create_task(func(), name=func.__qualname__) for func in loader]

        self.queue.reload_filters()

    def _datetime(self) -> datetime:
        return datetime.datetime.now()

    def _create_id(self) -> str:
        return str(uuid.uuid1())






















    def _math(self) -> None:
        delta, delta_a, delta_b = (0, 0, 0)

        levels: list[int] = [1,2,3]
        xp_values: list[int] = [100, 155, 220]

        for i in range(3):
            k: int = (i + 1) % 3
            delta += ((i+1) ** 2) * (k+1 - levels[(i + 2) % 3])
            delta_a += xp_values[i] * (k+1 - levels[(i + 2) % 3])
            delta_b += ((i+1) ** 2) * (xp_values[k] - xp_values[(i + 2) % 3])

        self.level_value_a: float = delta_a / delta
        self.level_value_b: float = delta_b / delta
        self.level_value_c: float = xp_values[0] - self.level_value_a * (levels[0] ** 2) - self.level_value_b * levels[0]

    def _get_members_lvl_ranks(self, members_db: dict[str, dict[str, dict[str, int]]], type: typing.Literal["message", "voice", "reaction"]) -> dict[str, int]:
        sort_members_by_xp: dict[str, int] = {str(k): v[type]["global_xp"] for k, v in sorted(members_db.items(), key=lambda item: item[1][type]["global_xp"], reverse=True)}
        for rank, name in enumerate(sort_members_by_xp.copy().keys(), start=1):
            sort_members_by_xp[name] = rank
        return {type: sort_members_by_xp}

    def _completion_bar(self, total: int, completed: int, _len: int = 15) -> str:
        percentage: float = (completed / total) * 100
        completed_bar = int(_len * percentage / 100)
        remaining_bar: int = _len - completed_bar
        bar: str = "[" + "#" * completed_bar + "-" * remaining_bar + "]"
 
        return f"{bar} {percentage:.1f}%"

   #returns datetime


    def return_true(self, var1: typing.Any, var2: typing.Any) -> typing.Any:
        if var1:
            return var1
        elif var2:
            return var2
        else:
            return None

    #returns ID


    def _calculate_xp(self, level: int) -> int:
        return int(self.level_value_a * level ** 2 + self.level_value_b * level + self.level_value_c)


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
