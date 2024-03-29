import discord, sys, asyncio, typing
sys.dont_write_bytecode = True
import src.connector as con


class ExecReport:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    def _create_report(self, data: dict[str, typing.Any]) -> discord.Embed:
        return discord.Embed(title=data.get("title"), description=data.get("description"), color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())

    async def send(self, embed: discord.Embed, guild: bool = False) -> None:
        if guild:
            await self.shared.bot.get_channel(1084932863314624662).send(embed=embed)
        else:
            await self.shared.bot.get_user(333588605748510721).send(embed=embed)

    def report(self, data: dict[str, typing.Any]) -> None:
        embed: discord.Embed = self._create_report(data)
        task: asyncio.Task[None] = self.loop.create_task(self.send(embed))

        try:
            task.result()
        except Exception as error:
            self.shared.logger.log(f"@ExecReport.report > Failed to .send() message. {type(error).__name__}: {error}")
