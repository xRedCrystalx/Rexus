import sys, typing, asyncio
sys.dont_write_bytecode = True
from src.connector import shared

from src.core.helpers.errors import report_error

class QueueSystem:
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
                    
                    await task

                except (asyncio.CancelledError, asyncio.InvalidStateError, asyncio.TimeoutError):
                    await report_error(f"QueueSystem.Task.{task.get_name()}[{guild_id}]", "Task killed.")
                except Exception:
                    await report_error(f"QueueSystem.Task.{task.get_name()}[{guild_id}]", "full")

        except Exception:
            await report_error(self._event_runner, "full")
    
    # main queue adder
    async def add_to_queue(self, e: str, guild_id: int, **kwargs) -> None:
        functions: tuple[typing.Callable] | None = shared.plugin_filter.get(e)

        if functions and guild_id:
            shared.loop.create_task(self._event_runner(guild_id=guild_id, funcs=functions, **kwargs))
        return None

# TODO: support of non-guild events, new database system, other.
async def setup(bot) -> None:
    await shared.reloader.load(QueueSystem(),
        config={
            "module": True,
            "location": shared,
            "var": "queue"
        }
    )