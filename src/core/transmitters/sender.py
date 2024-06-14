import discord, sys, typing, asyncio
sys.dont_write_bytecode = True
import src.connector as con

from src.core.helpers.event import Event
from src.core.helpers.errors import report_error, full_traceback

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
        self.shared.logger.log(f"@Sender.rate_limit_handler > Checking for ratelimit exception..", "NP_DEBUG")
        try:
            json_response: dict[str, typing.Any] = await error.response.json()
            response_header: dict[str, typing.Any] = dict(error.response.headers)
            self.shared.logger.log(f"@Sender.rate_limit_handler > Retrieved response headers and json data.", "NP_DEBUG")
        
            if error.response.status == 429:
                if json_response.get("global") and (retry_after := json_response.get("retry_after") or response_header.get("Retry-After")):
                    self.shared.logger.log(f"@Sender.rate_limit_handler > Detected global rate limit. Waiting {retry_after} seconds.", "SYSTEM")
                    # this should block `start` task for x seconds - global ratelimit ?? if safe
                    return await asyncio.sleep(retry_after)
                
                elif retry_after := (json_response.get("retry_after") or response_header.get("Retry-After")):
                    self.rate_limited.update(ID := getattr(event, "id"), retry_after)
                    self.shared.logger.log(f"@Sender.rate_limit_handler > Detected endpoint specific rate limit. Waiting {retry_after} seconds on that endpoint.", "SYSTEM")
                    return self.shared.loop.create_task(self.countdown(ID), name=f"ratelimit_countdown_{ID}")
            else:
                self.shared.logger.log(f"@Sender.rate_limit_handler > Not a rate limit error, returning.", "NP_DEBUG")

        except Exception as error:
            report_error(error, self.rate_limit_handler, "simple")

    async def start(self) -> None:
        while True:
            while self.events:
                event: Event = self.events[0]

                try:
                    event_data: dict = event.event_data

                    if getattr(event.event_obj, "id", None) in self.rate_limited:
                        self.shared.logger.log(f"@Sender.start > Requested event endpoint under rate limit, adding back to queue.", "NP_DEBUG")
                        self.events.append(event)
                    else:
                        if not event_data.get("kwargs"):
                            event_data["kwargs"] = {}

                        if not event_data.get("args"):
                            event_data["args"] = ()

                        self.shared.logger.log(f"@Sender.start > Executing API event.", "NP_DEBUG")
                        if function := getattr(event.event_obj, event.action, None):
                            if event._async:
                                await function(*event_data.get("args"), **event_data.get("kwargs"))
                            else:
                                function(*event_data.get("args"), **event_data.get("kwargs"))
                
                except Exception as error:
                    if isinstance(error, discord.HTTPException):
                        if await self.rate_limit_handler(error, event.event_obj):
                            self.shared.logger.log(f"@Sender.start > Under rate limit. Adding back to queue.", "NP_DEBUG")
                            self.events.append(event)
                        else:
                            self.shared.logger.log(f"@Sender.execution.discord.HTTPException[Event]: {"await" if event._async else ""} {event.event_obj.__name__}.{event.action}() {event.event_data}\n{full_traceback()}", "ERROR")
                    else:
                        report_error(error, self.start, "simple")

                self.events.remove(event)
            await asyncio.sleep(0.5)
