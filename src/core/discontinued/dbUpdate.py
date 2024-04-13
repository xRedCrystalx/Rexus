import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class DBCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.choices(
        value=[
        app_commands.Choice(name="String", value="str"),
        app_commands.Choice(name="Intiger", value="int"),
        app_commands.Choice(name="Boolean", value="bool"),
        app_commands.Choice(name="List", value="list"),
        app_commands.Choice(name="Dictionary", value="dict"),
        app_commands.Choice(name="None", value="none")
        ])
    @app_commands.command(name = "database", description = "Owner only command. No touchy!")
    async def db(self, interaction: discord.Interaction, key: str, value: app_commands.Choice[str], path: str = "", db_id: str | None = None) -> None:
        BotData: dict = self.shared.db.load_data()
        if interaction.user.id in [x for x in BotData["owners"]]:
            if db_id:
                self.shared.db.add_value(key=key, value_type=value.value, path=path, db_id=int(db_id))
                await interaction.response.send_message(content=f"Successfully updated {db_id} database.")
            else:
                self.shared.db.add_value(key=key, value_type=value.value, path=path)
                await interaction.response.send_message(content=f"Successfully updated all databases.")
                
            self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} executed {self.c.Yellow}/database{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: key: {key} value: {value.value} path: {path} db_id: {db_id} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
        else: 
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/database{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: key: {key} value: {value.value} path: {path} db_id: {db_id} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DBCommand(bot))
