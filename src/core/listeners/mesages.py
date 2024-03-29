import discord, sys, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class MessageListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild and message.author.id != self.bot.user.id:
            self.loop.create_task(self.shared.queue.add_to_queue(event="on_message", message=message, guild_id=message.guild.id))

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content != after.content and after.author.id != self.bot.user.id and after.guild:
            self.loop.create_task(self.shared.queue.add_to_queue(event="on_message_edit", guild_id=after.guild.id, before=before, after=after))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MessageListeners(bot))
