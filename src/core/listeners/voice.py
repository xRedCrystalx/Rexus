import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class VoiceListeners(commands.Cog):

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_voice_state_update", guild_id=member.guild.id, member=member, before=before, after=after))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(VoiceListeners())
