import discord, asyncio, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con


class AutoDeleter:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot
        self.database: dict[discord.Message, int] = {}

    async def add_to_queue(self, guild_db: dict[str, typing.Any], message: discord.Message, **OVERFLOW) -> None:
        if str(message.channel.id) in guild_db["auto_delete"]["monitored"] and guild_db["auto_delete"]["status"]:
            try:
                self.database.update({message: guild_db["AutoDelete"][str(message.channel.id)]})
            except Exception as error:
                self.shared.logger.log(f"@AutoDeleter.add_to_queue: {type(error).__name__}: {error}", "ERROR")

    async def start(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for msg in self.database.copy().keys():
                self.database[msg] = self.database[msg] - 1
                if self.database[msg] <= 0:
                    await self.shared.sender.resolver([{msg : {"action" : "delete"}}])
                    self.database.pop(msg)

            await asyncio.sleep(1)
