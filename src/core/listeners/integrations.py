import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class IntegrationListeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_integration_create(self, integration: discord.Integration) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_integration_create", guild_id=integration.guild.id, integration=integration))

    @commands.Cog.listener()
    async def on_integration_update(self, integration: discord.Integration) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_integration_update", guild_id=integration.guild.id, integration=integration))
        
    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild: discord.Guild) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_guild_integrations_update", guild_id=guild.id, guild=guild))

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.abc.GuildChannel) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_webhooks_update", guild_id=channel.guild.id, channel=channel))

    @commands.Cog.listener()
    async def on_raw_integration_delete(self, payload: discord.RawIntegrationDeleteEvent) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_raw_integration_delete", guild_id=payload.guild_id, payload=payload))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(IntegrationListeners(bot))
