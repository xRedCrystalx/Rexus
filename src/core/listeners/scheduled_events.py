import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class ScheduleEventListener(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_scheduled_event_create", guild_id=event.guild.id, event=event))

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event: discord.ScheduledEvent) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_scheduled_event_delete", guild_id=event.guild.id, event=event))

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent) -> None:
        """
        The following, but not limited to, examples illustrate when this event is called:
        - The scheduled start/end times are changed.
        - The channel is changed.
        - The description is changed.
        - The status is changed.
        - The image is changed.
        """
        shared.loop.create_task(shared.queue.add_to_queue(event="on_scheduled_event_update", guild_id=after.guild.id, before=before, after=after))

    @commands.Cog.listener()
    async def on_scheduled_event_user_add(self, event: discord.ScheduledEvent, user: discord.User) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_scheduled_event_user_add", guild_id=event.guild.id, event=event, user=user))

    @commands.Cog.listener()
    async def on_scheduled_event_user_remove(self, event: discord.ScheduledEvent, user: discord.User) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(event="on_scheduled_event_user_remove", guild_id=event.guild.id, event=event, user=user))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ScheduleEventListener(bot))
