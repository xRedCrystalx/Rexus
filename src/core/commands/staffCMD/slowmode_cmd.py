import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class SlowmodeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.command(name="slowmode", description="Set slowmode. (in seconds, 0 = No slowmode)")
    async def slowmode(self, interaction: discord.Interaction, set: int, channel: discord.TextChannel | None = None) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

        if (guild_db["general"]["staffRole"] in [x.id for x in interaction.user.roles]) or (interaction.user.id in [x for x in bot_config["owners"]]):
            if not channel:
                channel = interaction.channel

            if set > 21600:
                return await interaction.response.send_message(f"Slow mode can be only set up to 6h (21600s). Please try again with lower value.", ephemeral=True)
            try:
                await channel.edit(slowmode_delay=set)
                await interaction.response.send_message(f"Successfully set **{channel.name}'s** slowmode to `{set} seconds`.", ephemeral=True)
                    
            except Exception:
                id: str = self.shared._create_id()
                await interaction.response.send_message(f"Failed to set slowmode. Error ID: `{id}`", ephemeral=True)
                self.shared.logger.log(f"@SlowmodeCommand.slowmode >\n{self.shared.errors.full_traceback()}", "ERROR")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SlowmodeCommand(bot))
