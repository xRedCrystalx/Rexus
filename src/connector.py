from __future__ import annotations
import sys, aiohttp, asyncio, schedule, types
sys.dont_write_bytecode = True
from typing import Callable, TYPE_CHECKING
from discord.ext import commands

from xRedUtilsAsync import typehints
from xRedUtilsAsync.colors import (
    Foreground16 as FG,
    Style as ST
)

if TYPE_CHECKING:
    from src.system.database import Database
    from src.system.logging import Logger
    from src.system.reloader import Reloader
    from src.core.root.queue import QueueSystem

class Shared:
    path: str = None
    session: aiohttp.ClientSession = None
    loop: asyncio.AbstractEventLoop = None
    bot: commands.AutoShardedBot = None

    plugins: dict[str, Callable] = {}
    plugin_filter: dict[str, list[types.MethodType]] = {}
    plugin_tasks: list[asyncio.Task] = []

    schedule_jobs: list[schedule.Job] = []
    global_db: dict[str, typehints.SIMPLE_ANY] = {}

    db: Database = None
    logger: Logger = None
    reloader: Reloader =  None
    queue: QueueSystem = None

shared: Shared = Shared()