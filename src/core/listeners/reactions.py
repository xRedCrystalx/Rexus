import discord, sys, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class ReactionListener(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.guild_id:
            self.shared.loop.create_task(self.shared.queue.add_to_queue(event="on_raw_reaction_add", guild_id=payload.guild_id, payload=payload))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReactionListener(bot))
