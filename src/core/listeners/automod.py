import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class AutomodListeners(commands.Cog):

    @commands.Cog.listener()
    async def on_automod_rule_create(self, rule: discord.AutoModRule) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_automod_rule_create", guild_id=rule.guild.id, rule=rule))

    @commands.Cog.listener()
    async def on_automod_rule_update(self, rule: discord.AutoModRule) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_automod_rule_update", guild_id=rule.guild.id, rule=rule))

    @commands.Cog.listener()
    async def on_automod_rule_delete(self, rule: discord.AutoModRule) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_automod_rule_delete", guild_id=rule.guild.id, rule=rule))

    @commands.Cog.listener()
    async def on_automod_action(self, action: discord.AutoModAction) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_automod_action", guild_id=action.guild_id, action=action))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(AutomodListeners())
