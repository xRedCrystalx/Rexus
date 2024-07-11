import sys, typing, discord
sys.dont_write_bytecode = True
from src.connector import shared, Event

from .embeds import create_base_embed

from xRedUtilsAsync.strings import string_split
from xRedUtilsAsync.errors import simple_error, full_traceback
from xRedUtilsAsync.general import generate_uuid

async def report_error(caller: typing.Callable | str = None, option: typing.Literal["simple", "full"] = "full", discord: int = 1234547496454459432) -> str:
    """
    |async|

    Generates and formats error.

    ### Returns:
    - `error_id` as a `string`.
    """

    error: str = f"\n{await full_traceback()}" if option == "full" else await simple_error() if option == "simple" else error
    error_id: str = await generate_uuid()

    formatted_error: str = f"@{caller if isinstance(caller, str) else caller.__qualname__}[{error_id}] > {error} "

    await shared.logger.log("ERROR", formatted_error)

    if shared.bot and (channel := shared.bot.get_channel(discord)):
        for sliced in await string_split(formatted_error, 1994, option="smart"):
            await shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"content": f"```{sliced}```"}}))

    return error_id

def new_error_embed(error_id: str) -> discord.Embed:
    """|sync|"""
    return create_base_embed(
        title="Error",
        description=f"An error has occured. Please report this to the developer.\n**Error code:** `{error_id}`"
    )