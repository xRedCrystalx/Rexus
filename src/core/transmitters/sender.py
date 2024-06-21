import discord, sys, typing, asyncio
sys.dont_write_bytecode = True
import src.connector as con

from src.core.helpers.event import Event
from src.core.helpers.errors import report_error, full_traceback

from xRedUtils.type_hints import ITERABLE, SIMPLE_ANY

class Sender:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

        self.events: list[Event] = []
        self.rate_limited: dict[int, float] = {}

    def resolver(self, e: list[Event] | Event) -> None:
        if isinstance(e, Event):
            self.events.append(e)
        
        if isinstance(e, list):
            for event in e:
                if isinstance(event, Event):
                    self.events.append(event)

    async def countdown(self, id: int) -> None:
        self.shared.logger.log(f"@Sender.countdown > Started countdown for {id}. Time: {self.rate_limited[id]} seconds.", "TESTING")
        while self.rate_limited[id] <= 0:
            await asyncio.sleep(1)
            self.rate_limited[id] -= 1
        
        self.rate_limited.pop(id)
        self.shared.logger.log(f"@Sender.countdown > Removed {id} from ratelimit.", "NP_DEBUG")

    async def rate_limit_handler(self, error: discord.HTTPException, event: typing.Callable) -> None:
        try:
            try:
                json_error: dict[str, SIMPLE_ANY] = await error.response.json()
            except:
                json_error: dict[str, SIMPLE_ANY] = dict(error.response.headers)

            if error.status == 429:
                if json_error.get("global") and (retry_after := (json_error.get("retry_after") or json_error.get("Retry-After"))):
                    self.shared.logger.log(f"@Sender.rate_limit_handler > Detected global rate limit. Waiting {retry_after} seconds.", "SYSTEM")
                    # this should block `start` task for x seconds - global ratelimit ?? if safe
                    return await asyncio.sleep(retry_after)

                elif retry_after := (json_error.get("retry_after") or json_error.get("Retry-After")):
                    self.rate_limited.update(ID := getattr(event, "id"), retry_after)
                    self.shared.loop.create_task(self.countdown(ID), name=f"ratelimit_countdown_{ID}")

                    self.shared.logger.log(f"@Sender.rate_limit_handler > Detected endpoint specific rate limit. Waiting {retry_after} seconds on that endpoint.", "SYSTEM")

        except Exception as error:
            report_error(error, self.rate_limit_handler, "full")

    async def start(self) -> None:
        while True:
            while self.events:
                event: Event = self.events[0]
                try:
                    if getattr(event.event_obj, "id", None) not in self.rate_limited:
                        if function := getattr(event.event_obj, event.action, None):
                            args: ITERABLE = event.event_data.get("args", ())
                            kwargs: dict[str, SIMPLE_ANY] = event.event_data.get("kwargs", {})

                            res: SIMPLE_ANY = await function(*args, **kwargs) if event._async else function(*args, **kwargs)
                            if res and event._ret_id:
                                self.shared.global_db["returned_events"][event._ret_id] = res
                    else:
                        self.shared.logger.log(f"@Sender.start > Requested event endpoint under rate limit, adding back to queue.", "NP_DEBUG")
                        self.events.append(event)

                except Exception as error:
                    if isinstance(error, discord.HTTPException):
                        if await self.rate_limit_handler(error, event.event_obj):
                            self.events.append(event)
                        else:
                            self.shared.logger.log(f"@Sender.execution.discord.HTTPException[Event]: {"await" if event._async else ""} {event.event_obj.__class__.__name__}.{event.action}() {event.event_data}\n{full_traceback()}", "ERROR")
                    else:
                        report_error(error, self.start, "simple")

                self.events.remove(event)
            await asyncio.sleep(0.5)
