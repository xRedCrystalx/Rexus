import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class GuildListeners(commands.Cog):

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_available", guild_id=guild.id, guild=guild))

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild: discord.Guild) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_unavailable", guild_id=guild.id, guild=guild))
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_join", guild_id=guild.id, guild=guild))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_remove", guild_id=guild.id, guild=guild))

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_update", guild_id=after.id, before=before, after=after))
    
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: list[discord.Emoji], after: list[discord.Emoji]) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_emojis_update", guild_id=guild.id, guild=guild, after=after, before=before))

    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild: discord.Guild, before: list[discord.GuildSticker], after: list[discord.GuildSticker]) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_guild_stickers_update", guild_id=guild.id, guild=guild, before=before, after=after))

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_audit_log_entry_create", guild_id=entry.guild.id, entry=entry))

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_invite_create", guild_id=invite.guild.id, invite=invite))

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        shared.loop.create_task(shared.queue.add_to_queue(e="on_invite_delete", guild_id=invite.guild.id, invite=invite))

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(GuildListeners())
