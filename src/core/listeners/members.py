import discord, sys, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class MemberListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        self.shared.loop.create_task(self.shared.queue.add_to_queue(event="on_member_update", guild_id=after.guild.id, before=before, after=after))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        self.shared.loop.create_task(self.shared.queue.add_to_queue(event="on_member_join", guild_id=member.guild.id, member=member))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemberListeners(bot))
