import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class ThreadListener(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_thread_create", guild_id=thread.guild.id, thread=thread))

    @commands.Cog.listener()
    async def on_thread_join(self, thread: discord.Thread) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_thread_join", guild_id=thread.guild.id, thread=thread))

    @commands.Cog.listener()
    async def on_raw_thread_update(self, payload: discord.RawThreadUpdateEvent) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_raw_thread_update", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_thread_remove(self, thread: discord.Thread) -> None:
        """Local cache check, when bot left/was removed from thread. Can be delayed."""
        shared.loop.create_task(shared.queue.add_to_queue(e="on_thread_remove", guild_id=thread.guild.id, thread=thread))

    @commands.Cog.listener()
    async def on_raw_thread_delete(self, payload: discord.RawThreadDeleteEvent) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_raw_thread_delete", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_thread_member_join(self, member: discord.Member) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_thread_member_join", guild_id=member.guild.id, member=member))

    @commands.Cog.listener()
    async def on_raw_thread_member_remove(self, payload: discord.RawThreadMembersUpdate) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_raw_thread_member_remove", guild_id=payload.guild_id, payload=payload))


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ThreadListener(bot))
