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
            for saved_msg in self.database.copy():
                self.database[saved_msg] -= 5

                if self.database[saved_msg] <= 0:
                    try:
                        msg: discord.Message = await saved_msg.channel.fetch_message(saved_msg.id)
                    
                        if not msg.pinned: 
                            await msg.delete()
                    except: pass

                    self.database.pop(msg)

            await asyncio.sleep(5)

SAVE: list[str] = ["database"]
async def setup(bot: commands.AutoShardedBot) -> None:
    """await shared.module_manager.load(autodelete := AutoDeleter(), tasks=[autodelete.background_clock],
        config={
            autodelete.add_to_queue: ["on_message"]
        }
    )"""
