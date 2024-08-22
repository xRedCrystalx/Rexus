import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class RoleListener(commands.Cog):

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_role_create", guild_id=role.guild.id, role=role))

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_role_delete", guild_id=role.guild.id, role=role))

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_role_update", guild_id=after.guild.id, before=before, after=after))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(RoleListener())
