from __future__ import annotations
import sys, aiohttp, asyncio, schedule, types
sys.dont_write_bytecode = True
from typing import Callable, TYPE_CHECKING
from discord.ext import commands

from xRedUtilsAsync import typehints

if TYPE_CHECKING:
    from .system.database import DatabaseManager
    from .system.logging import Logger
    from .system.module_manager import ModuleManager
    from .system.queue import QueueSystem

class Shared:
    path: str = None
    session: aiohttp.ClientSession = None
    loop: asyncio.AbstractEventLoop = None
    bot: commands.AutoShardedBot = None

    plugins: dict[str, Callable] = {}
    plugin_filter: dict[str, list[types.MethodType]] = {}
    plugin_tasks: list[asyncio.Task] = []

    scheduled_jobs: list[schedule.Job] = []
    global_db: dict[str, typehints.SIMPLE_ANY] = {}
    system_tasks: list[asyncio.Task] = []

    logger: Logger = None
    module_manager: ModuleManager =  None
    queue: QueueSystem = None
    db_read: DatabaseManager = None
    db_write: DatabaseManager = None

shared: Shared = Shared()