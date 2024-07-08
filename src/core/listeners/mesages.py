import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class MessageListeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild and message.author.id != self.bot.user.id: # remove this in future
            shared.loop.create_task(shared.queue.add_to_queue(event="on_message", message=message, guild_id=message.guild.id))

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        """If the message is found in the message cache, it can be accessed via `RawMessageUpdateEvent.cached_message`."""
        if payload.guild_id: # remove this in future
            shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_message_edit", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """If the message is found in the message cache, it can be accessed via `RawMessageDeleteEvent.cached_message`."""
        if payload.guild_id: # remove this in future
            shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_message_delete", guild_id=payload.guild_id, payload=payload))

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent) -> None:
        """If the messages are found in the message cache, they can be accessed via `RawBulkMessageDeleteEvent.cached_messages`."""
        shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_message_delete", guild_id=payload.guild_id, payload=payload))


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(MessageListeners(bot))
