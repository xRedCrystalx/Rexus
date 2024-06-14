import sys, typing
sys.dont_write_bytecode = True
import src.connector as con
from .event import Event

from xRedUtils.strings import string_split
from xRedUtils.errors import simple_error, full_traceback
from xRedUtils.general import generate_uuid

def report_error(error: Exception | ExceptionGroup, _caller: typing.Callable = None, option: typing.Literal["simple", "full"] = "full", discord: int = 1234547496454459432) -> str:
    error: str = full_traceback() if option == "full" else simple_error(error) if option == "simple" and error else None
    if not error:
        return
    
    error_id: str = generate_uuid()
    con.shared.logger.log(f"{f"@{_caller.__qualname__.removeprefix("src.core.")}" if _caller else "An error has occured. "}[{error_id}] > {error}", "ERROR")

    if con.shared.bot and (channel := con.shared.bot.get_channel(discord)):
        for sliced in string_split(error, 1994, option="smart"):
            con.shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"content": f"```{sliced}```"}}))

    return error_id