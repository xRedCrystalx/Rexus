import sys, discord
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from .config.base_handler import BaseConfigCMDView

class ConfigureCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @discord.app_commands.choices(plugin=[
        discord.app_commands.Choice(name="General settings", value="general"),
        discord.app_commands.Choice(name="Commands", value="cmd"),
        discord.app_commands.Choice(name="Alt Detection", value="alt"),
        discord.app_commands.Choice(name="Impersonator detection", value="imper"),
        discord.app_commands.Choice(name="Artificial Intelligence", value="ai"),
        discord.app_commands.Choice(name="Automod Response", value="automod"),
        discord.app_commands.Choice(name="Link Protection", value="link"),
        discord.app_commands.Choice(name="Ping Protection", value="ping"),
        discord.app_commands.Choice(name="Auto Delete", value="auto_delete"),
        discord.app_commands.Choice(name="Auto Slowmode", value="auto_slowmode"),
        discord.app_commands.Choice(name="Reaction Filter", value="reaction"),
        discord.app_commands.Choice(name="Quote of the day", value="QOFTD")
    ])
    @discord.app_commands.command(name="config", description="Bot's configuration command!")
    async def config(self, interaction: discord.Interaction, plugin: discord.app_commands.Choice[str] | None) -> None:
        if not interaction.guild:
            await interaction.response.send_message("Sorry, but this command only works in guilds!", ephemeral=True)
            shared.logger.log("NP_DEBUG", f"@ConfigureCommand.config[cmd] > In DMs command execution attempt.")

        guild_db: dict[str, dict] = shared.db.load_data(interaction.guild.id)
        allowAdminEditing: bool = guild_db["general"].get("allowAdminEditing")

        if (allowAdminEditing and interaction.user.guild_permissions.administrator) or (interaction.user.id == interaction.guild.owner.id):# or check_bot_owner(interaction.user.id)
            paginator = BaseConfigCMDView(current_position=plugin.value if plugin else None, guild_id=interaction.guild.id)
            shared.logger.log("NP_DEBUG", f"@ConfigureCommand.config[cmd] > Created base paginator system.")
            
            if plugin:
                # plugin specific config
                await interaction.response.send_message(embed=paginator.config_obj.create_embed(guild_db.get(plugin.value), name=plugin.value, interaction=interaction, blueprint_embed=getattr(paginator.config_obj, plugin.value, None)), view=paginator.create_paginator_buttons(), ephemeral=True)
                shared.logger.log("NP_DEBUG", f"@ConfigureCommand.config[cmd] > Executing plugin specific config.")
            else:
                # global config
                await interaction.response.send_message(embed=paginator.help_obj.START, view=paginator.create_paginator_buttons(), ephemeral=True)
                shared.logger.log("NP_DEBUG", f"@ConfigureCommand.config[cmd] > Executing global config.")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command!", ephemeral=True)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ConfigureCommand(bot))
