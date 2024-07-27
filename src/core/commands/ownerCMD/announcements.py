import discord, sys, random, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from src.core.helpers.embeds import create_base_embed

from xRedUtils.type_hints import SIMPLE_ANY

class Announcements(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @discord.app_commands.choices(cmd=[
        discord.app_commands.Choice(name="reminder", value="reminder"),
        discord.app_commands.Choice(name="custom", value="custom")
    ])
    @discord.app_commands.command(name="announcements", description="Owner command")
    async def cmd(self, interaction: discord.Interaction, cmd: discord.app_commands.Choice[str], args: str = None) -> None:
        if True:#check_bot_owner(interaction.user.id):
            if cmd.value == "reminder":                
                embed: discord.Embed = create_base_embed(
                    title="🔔 Friendly reminder", 
                    description="Hello!\n\nJust a quick reminder for you to set up the bot, so you can start enjoying its features. Make sure you've configured all necessary settings using **</config:1235708858580860929>** command.\nIf you need any help, use **</noping:1235708858136002623>** command or reach out for [support](https://discord.gg/gzx3kxu68x).\n\nStay safe!"
                )
                for guild in self.bot.guilds:
                    guild_db: dict[str, SIMPLE_ANY] = shared.db.load_data(guild.id)
                    if not (guild_db["general"].get("staffChannel") and guild_db["general"].get("staffRole") and guild_db["general"].get("adminChannel") and guild_db["general"].get("adminRole")):
                        channel: discord.TextChannel = guild.system_channel or (channels[0] if (channels := [c for c in guild.text_channels if "general" in c.name]) else None)  or random.choice(guild.text_channels)
                        try:
                            await channel.send(content=guild.owner.mention, embed=embed)
                            await asyncio.sleep(2.5)
                        except Exception as error:
                            print(f"Failed to send reminder message to the guild {guild.name} ({guild.id}). {type(error).__name__}: {error}")

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Announcements(bot), guild=discord.Object(id=1230040815116484678))
