import sys, typing, asyncio
sys.dont_write_bytecode = True
from src.connector import shared

from src.core.helpers.errors import report_error

from xRedUtilsAsync.iterables import remove_items
from xRedUtilsAsync.type_hints import SIMPLE_ANY

class QueueSystem:
    FILTER: dict[str, list[typing.Callable]] = {}

    async def _event_runner(self, funcs: tuple[typing.Callable], guild_id: int, **kwargs) -> None:        
        try:
            bot_database: dict[str, typing.Any] = shared.db.load_data()
            if guild_id in bot_database["blacklisted_guilds"]:
                return

            guild_database: dict = shared.db.load_data(guild_id)
            if not guild_database["general"]["status"]:
                return

            # if not fully configured
            if not (guild_database["general"]["staffRole"] and 
                    guild_database["general"]["staffChannel"] and 
                    guild_database["general"]["adminRole"] and 
                    guild_database["general"]["adminChannel"]):
                return

            tasks: list[asyncio.Task] = [
                shared.loop.create_task(
                    func(guild_id=guild_id, guild_db=guild_database, bot_db=bot_database, **kwargs), 
                    name=func.__name__
                ) 
                for func in funcs]

            done, pending = await asyncio.wait(tasks, timeout=2.5)

            for task in [*done, *pending]:
                try:                
                    if not task.done():
                        task.cancel("Forcefully cancelled task.")
                        await asyncio.sleep(0)
                    
                    _resp: SIMPLE_ANY = await task

                except (asyncio.CancelledError, asyncio.InvalidStateError, asyncio.TimeoutError):
                    await report_error(f"QueueSystem.Task.{task.get_name()}[{guild_id}]", "Task killed.")
                except Exception:
                    await report_error(f"QueueSystem.Task.{task.get_name()}[{guild_id}]", "full")

        except Exception:
            await report_error(self._event_runner, "full")
    
    # main queue adder
    async def add_to_queue(self, e: str, guild_id: int, **kwargs) -> None:
        functions: tuple[typing.Callable] | None = self.FILTER.get(e)

        if functions and guild_id:
            shared.loop.create_task(self._event_runner(guild_id=guild_id, funcs=functions, **kwargs))
        return None

    # filter updater
    async def update_filter(self, event: str, func: typing.Callable, option: typing.Literal["add", "remove"]) -> None:
        if not self.FILTER.get(event):
            self.FILTER[event] = []

        if func in self.FILTER.get(event):
            # removing duplicates aswell
            self.FILTER[event] = await remove_items(self.FILTER[event], func)

        if option == "add":
            self.FILTER[event].append(func)

# TODO: support of non-guild events, new database system, other.
