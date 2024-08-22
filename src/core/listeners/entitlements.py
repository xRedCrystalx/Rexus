import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class EntitlementListeners(commands.Cog):
    """Actual bot subscription"""

    @commands.Cog.listener()
    async def on_entitlement_create(self, entitlement: discord.Entitlement) -> None:
        ...

    @commands.Cog.listener()
    async def on_entitlement_update(self, entitlement: discord.Entitlement) -> None:
        ...

    @commands.Cog.listener()
    async def on_entitlement_delete(self, entitlement: discord.Entitlement) -> None:
        ...

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(EntitlementListeners())
