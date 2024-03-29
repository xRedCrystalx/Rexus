import discord, sys, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class AutomodListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    @commands.Cog.listener()
    async def on_automod_action(self, action: discord.AutoModAction) -> None:
        self.loop.create_task(self.shared.queue.add_to_queue(event="on_automod_action", guild_id=action.guild_id, action=action))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutomodListeners(bot))
