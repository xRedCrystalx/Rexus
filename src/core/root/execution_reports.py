import discord, sys, asyncio, typing
sys.dont_write_bytecode = True
import src.connector as con
from xRedUtils.dates import get_datetime
from xRedUtils.strings import string_split


class ExecReport:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    def _create_report(self, data: dict[str, typing.Any]) -> discord.Embed:
        return discord.Embed(title=data.get("title"), description=data.get("description"), color=discord.Colour.dark_embed(), timestamp=get_datetime())

    async def send(self, embed: discord.Embed, guild: bool = False) -> None:
        if guild:
            if sys_channel := self.shared.bot.get_channel(1234544560852697209):
                await sys_channel.send(embed=embed)
        else:
            if red_dm := self.shared.bot.get_user(333588605748510721):
                await red_dm.send(embed=embed)

    def report(self, data: dict[str, typing.Any]) -> None:
        embed: discord.Embed = self._create_report(data)
        task: asyncio.Task[None] = self.shared.loop.create_task(self.send(embed))

        try:
            task.result()
        except Exception as error:
            self.shared.logger.log(f"@ExecReport.report > Failed to .send() message. {self.shared.errors.simple_error(error)}")
