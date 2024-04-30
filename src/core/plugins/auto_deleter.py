import discord, asyncio, sys, typing
sys.dont_write_bytecode = True
import src.connector as con

class AutoDeleter:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.database: dict[discord.Message, int] = {}

    async def add_to_queue(self, guild_db: dict[str, typing.Any], message: discord.Message, **OVERFLOW) -> None:
        if str(message.channel.id) in guild_db["auto_delete"]["monitored"] and guild_db["auto_delete"]["status"]:
            self.database.update({message: guild_db["auto_delete"]["monitored"][str(message.channel.id)]})

    async def start(self) -> None:
        while True:
            for msg in self.database.copy():
                self.database[msg] -= 5

                if self.database[msg] <=  0:
                    self.shared.sender.resolver(con.Event(msg, "delete", event_data={}))
                    self.database.pop(msg)

            await asyncio.sleep(5)
