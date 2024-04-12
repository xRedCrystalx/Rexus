import sys, discord
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands

import src.connector as con

class ConfigureCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.reload()

    @app_commands.choices(plugin=[
        app_commands.Choice(name="General settings", value="general"),
        app_commands.Choice(name="Commands", value="cmd"),
        app_commands.Choice(name="Alt Detection", value="alt"),
        app_commands.Choice(name="Impersonator detection", value="imper"),
        app_commands.Choice(name="Artificial Intelligence", value="ai"),
        app_commands.Choice(name="Automod Response", value="automod"),
        app_commands.Choice(name="Link Protection", value="link"),
        app_commands.Choice(name="Ping Protection", value="ping"),
        app_commands.Choice(name="Auto Delete", value="autodelete"),
        app_commands.Choice(name="Auto Slowmode", value="autoslowmode"),
        app_commands.Choice(name="Reaction Filter", value="reaction"),
        app_commands.Choice(name="Quote of the day", value="QOFTD")
    ])
    @app_commands.command(name="config", description="Bot's configuration command!")
    async def config(self, interaction: discord.Interaction, plugin: app_commands.Choice[str] | None) -> None:
        self.shared.logger.log(f"@ConfigureCommand.config[cmd] > Called config command.", "NP_DEBUG")
        if not interaction.guild:
            await interaction.response.send_message("Sorry, but this command only works in guilds!", ephemeral=True)
            self.shared.logger.log(f"@ConfigureCommand.config[cmd] > In DMs command execution attempt.", "NP_DEBUG")

        bot_db: dict[str, dict] = self.shared.db.load_data()
        guild_db: dict[str, dict] = self.shared.db.load_data(interaction.guild.id)
        allowAdminEditing: bool = guild_db["general"].get("allowAdminEditing")
        self.shared.logger.log(f"@ConfigureCommand.config[cmd] > Loaded databases.", "NP_DEBUG")

        if (allowAdminEditing and interaction.user.guild_permissions.administrator) or (interaction.user.id in bot_db["owners"]) or (interaction.user == interaction.guild.owner):
            self.reload()
            paginator = self.advancedPaginator(current_position=plugin.value if plugin else None)
            self.shared.logger.log(f"@ConfigureCommand.config[cmd] > Created base paginator system.", "NP_DEBUG")
            
            if plugin:
                # plugin specific config
                await interaction.response.send_message(embed=paginator.config_obj.create_embed(guild_db.get(plugin.value), name=plugin.value, interaction=interaction, blueprint_embed=paginator.global_config.get(plugin.value)["config"]), view=paginator.create_paginator_buttons(), ephemeral=True)
                self.shared.logger.log(f"@ConfigureCommand.config[cmd] > Executing plugin specific config.", "NP_DEBUG")
            else:
                # global config
                await interaction.response.send_message(embed=paginator.help_obj.START, view=paginator.create_paginator_buttons(), ephemeral=True)
                self.shared.logger.log(f"@ConfigureCommand.config[cmd] > Executing global config.", "NP_DEBUG")
        else:
            self.shared.logger.log(f"@ConfigureCommand.config[cmd] > No permission.", "NP_DEBUG")
            await interaction.response.send_message("You do not have permissions to execute this command!", ephemeral=True)

    def reload(self) -> None:
        for imp in ["config_handler", "pages", "configurator"]:
            if f"src.core.commands.adminCMD.config.{imp}" in sys.modules:
                del sys.modules[f"src.core.commands.adminCMD.config.{imp}"]

        from .config.base_handler import AdvancedPaginator
        self.advancedPaginator = AdvancedPaginator

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ConfigureCommand(bot))
