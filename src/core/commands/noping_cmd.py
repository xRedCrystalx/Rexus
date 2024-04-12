import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class NoPing(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.choices(cmd=[
        app_commands.Choice(name="ping", value="ping"),
        app_commands.Choice(name="report_bug", value="report_bug"),
        app_commands.Choice(name="help", value="help")
        ]
    )
    @app_commands.command(name="noping", description="General NoPing command.")
    async def noping(self, interaction: discord.Interaction, cmd: app_commands.Choice[str], args: str = None) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NoPing(bot))