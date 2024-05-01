import sys, traceback, typing
sys.dont_write_bytecode = True
import src.connector as con

if typing.TYPE_CHECKING:
    from discord.ext import commands
class ErrorHelper:
    def __init__(self) -> None:
        self.shared: con.Shared =  con.shared
        self.bot: commands.Bot = self.shared.bot
        
    def full_traceback(self, dc: bool = True) -> str:
        error: str = traceback.format_exc()
        if dc:
            self.report_to_discord(error)
        return error
    
    def simple_error(self, error: Exception, dc: bool = True) -> str:
        error: str = f"{type(error).__name__}: {error}"
        if dc: 
            self.report_to_discord(error)
        return error

    def report_to_discord(self, error: str) -> None:
        if self.bot and (errors_channel := self.bot.get_channel(1234547496454459432)):
            for sliced_error in [error[i:i+1994] for i in range(0, len(error), 1994)]:
                self.shared.sender.resolver(con.Event(errors_channel, "send", event_data={"kwargs": {"content": f"```{sliced_error}```"}}))