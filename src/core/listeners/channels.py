import discord, sys, datetime
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class ChannelListeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_guild_channel_create", guild_id=channel.guild.id, channel=channel))

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_guild_channel_delete", guild_id=channel.guild.id, channel=channel))

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_guild_channel_update", guild_id=after.guild.id, before=before, after=after))

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel: discord.abc.GuildChannel, last_pin: datetime.datetime | None) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_guild_channel_pins_update", guild_id=channel.guild.id, channel=channel, last_pin=last_pin))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ChannelListeners(bot))
