import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class ConnectionListeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_connect(self) -> None:
        ...

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        ...

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id: int) -> None:
        ...

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id: int) -> None:
        ...

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        ...

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        ...

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id: int) -> None:
        ...

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id: int) -> None:
        ...

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ConnectionListeners(bot))
