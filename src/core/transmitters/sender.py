import discord, sys, typing, asyncio
sys.dont_write_bytecode = True
import src.connector as con

class Sender:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

        self.events: list[list[dict[typing.Any, dict[str, typing.Any]]]] = []
        self.rate_limited: dict[int, float] = {}

    def resolver(self, data: list[dict[typing.Any, dict[str, typing.Any]]] | None) -> None:
        if data and isinstance(data, list):
            self.events.append(data)
            self.shared.logger.log(f"@Sender.resolver > Added events to the sender queue list", "NP_DEBUG")

    async def countdown(self, id: int) -> None:
        self.shared.logger.log(f"@Sender.countdown > Started countdown for {id}. Time: {self.rate_limited[id]} seconds.", "NP_DEBUG")
        while self.rate_limited[id] <= 0:
            await asyncio.sleep(1)
            self.rate_limit_handler[id] -= 1
        
        self.rate_limited.pop(id)
        self.shared.logger.log(f"@Sender.countdown > Removed {id} from ratelimit.", "NP_DEBUG")

    async def rate_limit_handler(self, error: discord.HTTPException, event: typing.Callable) -> None:
        self.shared.logger.log(f"@Sender.rate_limit_handler > Checking for ratelimit exception..", "NP_DEBUG")
        try:
            json_response: dict[str, typing.Any] = await error.response.json()
            response_header: dict[str, typing.Any] = dict(error.response.headers)
            self.shared.logger.log(f"@Sender.rate_limit_handler > Retrieved response headers and json data.", "NP_DEBUG")
        
            if error.response.status_code == 429:
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
            self.shared.logger.log(f"@Sender.rate_limit_handler: {type(error).__name__}: {error}", "ERROR")


    async def start(self) -> None:
        while True:
            while self.events:
                event_group: list[dict[typing.Any, dict[str, typing.Any]]] = self.events[0]
                
                for event in event_group:
                    try:
                        event_obj: str = tuple(event.keys())[0]
                        event_data: dict = event[event_obj]

                        if getattr(event_obj, "id") in self.rate_limited:
                            self.shared.logger.log(f"@Sender.start[sender] > Requested event endpoint under rate limit, adding back to queue.", "NP_DEBUG")
                            self.events.append([{event_obj: event_data}])
                        else:
                            function: typing.Callable = getattr(event_obj, event_data.get("action"))
                            if not event_data.get("kwargs"):
                                event_data["kwargs"] = {}

                            if not event_data.get("args"):
                                event_data["args"] = ()

                            self.shared.logger.log(f"@Sender.start[sender] > Executing API event.", "NP_DEBUG")
                            await function(*event_data.get("args"), **event_data.get("kwargs"))
                    
                    except Exception as error:
                        if isinstance(error, discord.HTTPException):
                            if await self.rate_limit_handler(error, event_obj):
                                self.shared.logger.log(f"@Sender.start[sender] > Under rate limit. Adding back to queue.", "NP_DEBUG")
                                self.events.append([{event_obj: event_data}])
                            else:
                                self.shared.logger.log(f"@Sender.execution.discord.HTTPException: {type(error).__name__}: {error}", "ERROR")
                        else:
                            self.shared.logger.log(f"@Sender.execution: {type(error).__name__}: {error}", "ERROR")

                self.events.remove(event_group)

            await asyncio.sleep(0.5)

#NOTE: test ratelimit handler