import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class PollListeners(commands.Cog):

    @commands.Cog.listener()
    async def on_raw_poll_vote_add(self, payload: discord.RawPollVoteActionEvent) -> None:
        if payload.guild_id:
            shared.loop.create_task(shared.queue.add_to_queue(e="on_raw_poll_vote_add", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_raw_poll_vote_remove(self, payload: discord.RawPollVoteActionEvent) -> None:
        if payload.guild_id:
            shared.loop.create_task(shared.queue.add_to_queue(e="on_raw_poll_vote_remove", guild_id=payload.guild_id, payload=payload))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(PollListeners())
