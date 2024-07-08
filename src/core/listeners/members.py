import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class MemberListeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_member_join", guild_id=member.guild.id, member=member))

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_member_remove", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """
        This is called when one or more of the following things change:
        - nickname
        - roles
        - pending
        - timeout
        - guild avatar
        - flags
        Due to a Discord limitation, this event is not dispatched when a member's timeout expires.
        """
        shared.loop.create_task(shared.queue.add_to_queue(event="on_member_update", guild_id=after.guild.id, before=before, after=after))

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        """        
        This is called when one or more of the following things change:
        - avatar
        - username
        - discriminator
        """
        shared.loop.create_task(shared.queue.add_to_queue(event="on_user_update", before=before, after=after))

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User | discord.Member) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_member_ban", guild_id=guild.id, guild=guild, user=user))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User | discord.Member) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_member_unban", guild_id=guild.id, guild=guild, user=user))

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_presence_update", guild_id=after.guild.id, before=before, after=after))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(MemberListeners(bot))
