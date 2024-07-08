import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared, Event

from src.core.helpers.embeds import new_embed

class BotListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.events_channel_id: int = 1234545937435725864

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.bot.tree.sync(guild = discord.Object(id=guild.id))
        channel: discord.TextChannel = guild.system_channel

        # read attempt, db handler will create or read database, if nothing returned, error happened.
        database: dict[str, typing.Any] = shared.db.load_data(guild.id)
        
        embed: discord.Embed = await new_embed("Hey there!", 
                description="Firstly, thank you for inviting me to your guild!\n\nI'm **NoPing**, friendly little robot that will help you protect your community.\nTo start with my configuration, use </config:1235708858580860929> command or </noping:1235708858136002623> for quick start pointers.",
                thumbnail="https://i.ibb.co/R6WZm04/member.png",
                footer="Developed by xRedCrystalx"                 
            )

        shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"embed": embed}}))

        if events_channel := self.bot.get_channel(self.events_channel_id):
            embed = await new_embed(f"Joined {guild.name}", description=f"**Guild:** {guild.name} (`{guild.id}`)\n**Creation date:** {guild.created_at:%d.%m.%Y %H:%M:%S}\n**Owner:** {guild.owner.display_name}, {guild.owner.global_name} (`{guild.owner_id}`)", color=discord.Colour.green())
            embed.add_field(name="`` Counts ``", value=f"**Members:** `{guild.member_count}`\n**Roles:** `{len(guild.roles)}`\n**Channels:** `{len(guild.channels)}`\n**Emojis:** `{len(guild.emojis)}`")
            shared.sender.resolver(Event(events_channel, "send", event_data={"kwargs": {"embed": embed}}))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        if events_channel := self.bot.get_channel(self.events_channel_id):
            embed: discord.Embed = await new_embed(f"Left {guild.name}", description=f"**Guild:** {guild.name} (`{guild.id}`)\n**Creation date:** {guild.created_at:%d.%m.%Y %H:%M:%S}\n**Owner:** {guild.owner.display_name}, {guild.owner.global_name} (`{guild.owner_id}`)", color=discord.Colour.red())
            shared.sender.resolver(Event(events_channel, "send", event_data={"kwargs": {"embed": embed}}))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotListeners(bot))
