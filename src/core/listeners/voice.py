import discord, sys, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class VoiceListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        self.loop.create_task(self.shared.queue.add_to_queue(event="on_voice_state_update", guild_id=member.guild.id, member=member, before=before, after=after))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(VoiceListeners(bot))
