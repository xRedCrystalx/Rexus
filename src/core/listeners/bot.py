import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

from xRedUtils.dates import get_datetime

class BotListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.events_channel_id: int = 1234545937435725864

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.bot.tree.sync(guild = discord.Object(id=guild.id))
        channel: discord.TextChannel = guild.system_channel

        # read attempt, db handler will create or read database, if nothing returned, error happened. -- TODO: creation of db here
        database: dict[str, typing.Any] = self.shared.db.load_data(guild.id)

        if not database:
            id: str = self.shared._create_id()
            await channel.send(f"An error has occured. Please report this to the developer. Error ID: `{id}`")
            self.shared.logger.log(f"Failed to create database file for guild {guild.name} ({guild.id}). Error ID: {id}\n{self.shared.errors.full_traceback()}", "ERROR")

        embed: discord.Embed = discord.Embed(title="Hey there!", timestamp=get_datetime(), color=discord.Colour.dark_embed(),
                                             description=f"Firstly, thank you for inviting me to your guild!\n\nI'm **NoPing**, friendly little robot that will help you protect your community.\nTo start with my configuration, use </config:1235708858580860929> command or </noping:1235708858136002623> for quick start pointers.")
        embed.set_thumbnail(url="https://i.ibb.co/R6WZm04/member.png")
        embed.set_footer(text="Developed by xRedCrystalx")
        await channel.send(embed=embed)

        if events_channel := self.bot.get_channel(self.events_channel_id):
            embed = discord.Embed(title=f"Joined {guild.name}", description=f"**Guild:** {guild.name} (`{guild.id}`)\n**Creation date:** {guild.created_at:%d.%m.%Y %H:%M:%S}\n**Owner:** {guild.owner.display_name}, {guild.owner.global_name} (`{guild.owner_id}`)",
                                   timestamp=get_datetime(), color=discord.Colour.green())
            embed.add_field(name="`` Counts ``", value=f"**Members:** `{guild.member_count}`\n**Roles:** `{len(guild.roles)}`\n**Channels:** `{len(guild.channels)}`\n**Emojis:** `{len(guild.emojis)}`")
            await events_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        if events_channel := self.bot.get_channel(self.events_channel_id):
            embed = discord.Embed(title=f"Left {guild.name}", description=f"**Guild:** {guild.name} (`{guild.id}`)\n**Creation date:** {guild.created_at:%d.%m.%Y %H:%M:%S}\n**Owner:** {guild.owner.display_name}, {guild.owner.global_name} (`{guild.owner_id}`)",
                                   timestamp=get_datetime(), color=discord.Colour.red())
            await events_channel.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotListeners(bot))
