import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

from src.core.helpers.permissions import check_ids, check_bot_owner
from src.core.helpers.errors import report_error

from xRedUtils.times import seconds_to_str

class SlowmodeCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.AutoShardedBot = bot

    @discord.app_commands.command(name="slowmode", description="Set slowmode. (in seconds, 0 = No slowmode)")
    async def slowmode(self, interaction: discord.Interaction, set: int, channel: discord.TextChannel | None = None) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)

        if check_ids(interaction.user.roles, [guild_db["general"]["staffRole"], guild_db["general"]["adminRole"]]) or check_bot_owner(interaction.user.id):
            if not channel:
                channel = interaction.channel

            if set > 21600:
                await interaction.response.send_message(f"Slow mode can be only set up to 6h (21600s). Please try again with lower value.", ephemeral=True)
                return

            try:
                await channel.edit(slowmode_delay=set)
                await interaction.response.send_message(f"Successfully set **{channel.name}'s** slowmode to `{seconds_to_str(set)}`.", ephemeral=True)
                    
            except Exception as error:
                error_id: str = report_error(error, self.slowmode, "full")
                await interaction.response.send_message(f"Failed to set slowmode. Error ID: `{error_id}`", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            
async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(SlowmodeCommand(bot))
