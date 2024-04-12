import sys, typing, discord, traceback
sys.dont_write_bytecode = True
import src.connector as con

class AdvancedPaginator(discord.ui.View):
    def __init__(self, current_position: str, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)
        self.shared: con.Shared = con.shared
        self._handle_imports()

        self.global_config: dict[str, dict[str, str | list]] = {
            "general": {
                "name": "General settings",
                "help": self.help_obj.general,
                "config": self.config_obj.general
            },
            "cmd": {
                "name": "Commands",
                "help": self.help_obj.commands,
                "config": self.config_obj.commands
            },
            "alt": {
                "name": "Alt Detection",
                "help": self.help_obj.altDetection,
                "config": self.config_obj.altDetection
            },
            "imper": {
                "name": "Impersonator Detection",
                "help": self.help_obj.impersonatorDetection,
                "config": self.config_obj.imperDetection
            },
            "ai": {
                "name": "Artificial Intelligence",
                "help": self.help_obj.ai,
                "config": self.config_obj.ai
            },
            "automod": {
                "name": "Automod Response",
                "help": self.help_obj.automod,
                "config": self.config_obj.automod
            },
            "link": {
                "name": "Link Protection",
                "help": self.help_obj.linkProtection,
                "config": self.config_obj.linkProtection
            },
            "ping": {
                "name": "Ping Protection",
                "help": self.help_obj.pingProtection,
                "config": self.config_obj.pingProtection
            },
            "auto_delete": {
                "name": "Auto Delete",
                "help": self.help_obj.autoDelete,
                "config": self.config_obj.autoDelete
            },
            "auto_slowmode": {
                "name": "Auto Slowmode",
                "help": self.help_obj.autoSlowmode,
                "config": self.config_obj.autoSlowmode
            }
        }
        
        self.page_names: list[str] = list(self.global_config.keys())
        self.page_len: int = len(self.page_names)-1
        self.current_position: str = current_position if current_position else self.page_names[-1]

    def _handle_imports(self) -> None:
        self.shared.logger.log(f"@AdvancedPaginator._handle_imports > Importing handlers.", "NP_DEBUG")
        from .pages import HelpPages, ConfigPages
        from .configurator import Configurator

        try:
            self.help_obj: HelpPages = HelpPages()
            self.config_obj: ConfigPages = ConfigPages()
            self.configurator: Configurator = Configurator()
            self.shared.logger.log(f"@AdvancedPaginator._handle_imports > Imported and executed handlers..", "NP_DEBUG")

        except Exception as error:
            self.shared.logger.log(f"@AdvancedPaginator._handle_imports > {type(error).__name__}: {error}", "ERROR")

    def create_back_button(self, item: bool = False) -> typing.Self | discord.Button:
        button = discord.ui.Button(label="↩", custom_id="PAGINATOR:RETURN", style=discord.ButtonStyle.red)
        if item:
            self.shared.logger.log(f"@AdvancedPaginator.create_back_button > Created BACK button.", "NP_DEBUG")
            return button
        else:
            self.shared.logger.log(f"@AdvancedPaginator.create_back_button > Created and appended BACK button to view.", "NP_DEBUG")
            return self.add_item(button)
    
    def create_paginator_buttons(self) -> typing.Self:
        self.add_item(discord.ui.Button(label="◄", custom_id="PAGINATOR:BACK", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(emoji="❔", custom_id="PAGINATOR:INFO", style=discord.ButtonStyle.green))
        self.add_item(discord.ui.Button(emoji="⚙️", custom_id="CONFIG:START", style=discord.ButtonStyle.gray))
        self.add_item(discord.ui.Button(label="►", custom_id="PAGINATOR:NEXT", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="✕", custom_id="PAGINATOR:STOP", style=discord.ButtonStyle.red))
        self.shared.logger.log(f"@AdvancedPaginator.create_paginator_buttons > Created and appended PAGINATOR buttons to view.", "NP_DEBUG")
        return self

    async def update_message(self, interaction: discord.Interaction, data: dict[str, typing.Any]) -> None:
        self.shared.logger.log(f"@AdvancedPaginator.update_message > Updating message...", "NP_DEBUG")
        await interaction.response.edit_message(**data)

    async def change_page(self, custom_id: str, interaction: discord.Interaction) -> None:
        guild_db: dict = self.shared.db.load_data(interaction.guild.id)
        
        if custom_id.endswith(":BACK") or custom_id.endswith(":NEXT"):
            value: int = 1 if custom_id.endswith(":NEXT") else -1

            currentPage: int = self.page_names.index(self.current_position)
            index: int = 0 if currentPage + value > self.page_len else self.page_len if currentPage + value < 0 else currentPage + value
            self.current_position = self.page_names[index]

            if config := guild_db.get(self.current_position):
                self.shared.logger.log(f"@AdvancedPaginator.change_page > Changing page to {self.current_position}.", "NP_DEBUG")
                cnf: dict[str, str | discord.Embed] = self.global_config.get(self.current_position)
                await self.update_message(interaction, {"embed": self.config_obj.create_embed(config, name=cnf["name"], interaction=interaction, blueprint_embed=cnf["config"])})
            else:
                raise ValueError(f"Could not find data for {self.current_position} in {interaction.guild.name} ({interaction.guild.id}) >> Triggered by PAGINATOR interaction.")

        elif custom_id.endswith(":INFO"):
            self.shared.logger.log(f"@AdvancedPaginator.change_page > Changing page to INFO.", "NP_DEBUG")
            await self.update_message(interaction, {"embed": self.global_config.get(self.current_position)["help"], "view": self.clear_items().create_back_button()})

        elif custom_id.endswith(":STOP"):
            self.shared.logger.log(f"@AdvancedPaginator.change_page > Changing page to STOP.", "NP_DEBUG")
            await self.update_message(interaction, {"view": self.clear_items()})
            self.stop()

        elif custom_id.endswith(":RETURN"):
            self.shared.logger.log(f"@AdvancedPaginator.change_page > Resetting configurator.", "NP_DEBUG")
            self.configurator.reset_configurator()
            if config := guild_db.get(self.current_position):
                self.shared.logger.log(f"@AdvancedPaginator.change_page > Changing page to RETURN.", "NP_DEBUG")
                cnf: dict[str, str | discord.Embed] = self.global_config.get(self.current_position)
                await self.update_message(interaction, {"embed": self.config_obj.create_embed(config, name=cnf["name"], interaction=interaction, blueprint_embed=cnf["config"]), "view": self.clear_items().create_paginator_buttons()})
            else:
                raise ValueError(f"Could not find data for {self.current_position} in {interaction.guild.name} ({interaction.guild.id}) >> Triggered by RETURN interaction.")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.data:
            raise ValueError("Discord did not provide interaction data. >> Triggered by INTERACTION_CHECK")

        custom_id: str = dict(interaction.data ).get('custom_id')
        self.shared.logger.log(f"@AdvancedPaginator.interaction_check > Recieved interaction with ID: {custom_id}.", "NP_DEBUG")

        if interaction.type == discord.InteractionType.component:
            if custom_id.startswith("PAGINATOR:"):
                await self.change_page(custom_id, interaction)
            elif custom_id.startswith("CONFIG:"):
                await self.configurator.handle_interaction(custom_id, interaction, self)
            else:
                raise NameError("Could not resolve custom_id of the interaction. >> Triggered by INTERACTION_CHECK")
        return
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.item.Item) -> None:
        error_id: str = self.shared._create_id()
        self.shared.logger.log(f"@AdvancedPaginator.on_error > Error ID: {error_id}\n{traceback.format_exc()}", "ERROR")

        error_embed: discord.Embed = self.help_obj.ERROR
        error_embed.description = error_embed.description.format(error=error_id)

        await self.update_message(interaction, {"embed": error_embed, "view": self.clear_items()})
