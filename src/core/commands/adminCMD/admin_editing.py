import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con

class AdminEditing(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.command(name="admin_editing", description="Allow/Disallow admin editing - Owner CMD")
    async def admin_cmd(self, interaction: discord.Interaction) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_db: dict[str, typing.Any] = self.shared.db.load_data()
        if interaction.user == interaction.guild.owner or interaction.user.id in bot_db["owners"]:
            value: bool = not guild_db["general"]["allowAdminEditing"] # switch value
            guild_db["general"]["allowAdminEditing"] = value

            self.shared.db.save_data(interaction.guild_id, guild_db)
            await interaction.response.send_message(f"**{"Enabled" if value else "Disabled"}** admin editing. Use same command to {"disable" if value else "enable"} it.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You are not the guild owner. Bye bye.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminEditing(bot))
