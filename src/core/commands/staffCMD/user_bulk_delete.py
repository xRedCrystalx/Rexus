import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

from src.core.helpers.permissions import check_ids, check_bot_owner
from src.core.helpers.errors import report_error

class BulkDelete(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.AutoShardedBot = bot

    @discord.app_commands.command(name="purge", description="Purges user's messages.")
    async def purge(self, interaction: discord.Interaction, member: discord.Member, number: int | None = None) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)

        def target(m: discord.Message) -> bool:
            return m.author.id == member.id

        if check_ids(interaction.user.roles, guild_db["general"]["staffRole"]) or check_bot_owner(interaction.user.id):
            try:
                await interaction.response.send_message(f"Purging {member.display_name}'s messages. Checking last {number if number else "100"} messages per channel.", ephemeral=True)
                
                for channel in interaction.guild.text_channels:
                    await channel.purge(limit=number, check=target)
             
                await interaction.followup.send(f"Successfully purged {member.display_name}'s messages from all channels.", ephemeral=True)
                    
            except Exception as error:
                error_id: str = report_error(error, self.purge, "full")
                await interaction.response.send_message(f"Failed to purge {member.display_name}'s messages. Error ID: `{error_id}`", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(BulkDelete(bot))