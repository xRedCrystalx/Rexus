import discord, asyncio, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class AutoDeleter:
    def __init__(self) -> None:
        self.database: dict[discord.Message, int] = {}

    async def add_to_queue(self, guild_db: dict[str, typing.Any], message: discord.Message, **OVERFLOW) -> None:
        if str(message.channel.id) in guild_db["auto_delete"]["monitored"] and guild_db["auto_delete"]["status"]:
            self.database.update({message: guild_db["auto_delete"]["monitored"][str(message.channel.id)]})

    async def background_clock(self) -> None:
        while True:
            for msg in self.database.copy():
                self.database[msg] -= 5

                if self.database[msg] <=  0:
                    await msg.delete()
                    self.database.pop(msg)

            await asyncio.sleep(5)

async def setup(bot: commands.AutoShardedBot) -> None:
    await shared.add_plugin(AutoDeleter, tasks=[AutoDeleter.background_clock],
        config={
            ["on_message"]: AutoDeleter.add_to_queue
        }
    )
