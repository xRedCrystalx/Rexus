import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class ReactionListener(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.guild_id:
            shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_reaction_add", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.guild_id:
            shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_reaction_remove", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload: discord.RawReactionClearEvent) -> None:
        if payload.guild_id:
            shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_reaction_clear", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload: discord.RawReactionClearEmojiEvent) -> None:
        if payload.guild_id:
            shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_reaction_clear_emoji", guild_id=payload.guild_id, payload=payload))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ReactionListener(bot))
