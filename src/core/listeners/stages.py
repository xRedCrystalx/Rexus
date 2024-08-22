import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class StageListener(commands.Cog):

    @commands.Cog.listener()
    async def on_stage_instance_create(self, stage: discord.StageInstance) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_stage_instance_create", guild_id=stage.guild.id, stage=stage))

    @commands.Cog.listener()
    async def on_stage_instance_delete(self, stage: discord.StageInstance) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_stage_instance_delete", guild_id=stage.guild.id, stage=stage))

    @commands.Cog.listener()
    async def on_stage_instance_update(self, before: discord.StageInstance, after: discord.StageInstance) -> None:
        """
        The following, but not limited to, examples illustrate when this event is called:
        - The topic is changed.
        - The privacy level is changed.
        """
        shared.loop.create_task(shared.queue.add_to_queue(e="on_stage_instance_update", guild_id=after.guild.id, before=before, after=after))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(StageListener())
