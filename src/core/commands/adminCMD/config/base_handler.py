import sys, typing, discord
sys.dont_write_bytecode = True
from src.connector import shared

from src.core.helpers.views import ViewHelper
from src.core.helpers.modals import ModalHelper
from src.core.helpers.errors import report_error

class BaseConfigCMDView(ViewHelper):
    def __init__(self, current_position: str, guild_id: int, timeout: float | None = 60 * 60) -> None:
        super().__init__(timeout=timeout)
        self._handle_imports(guild_id)

        self.global_config: dict[str, str] = {
            "general": "General settings",
            "cmd": "Commands",
            "alt": "Alt Detection",
            "imper": "Impersonator Detection",
            "ai": "Artificial Intelligence",
            "automod": "Automod Response",
            "link":"Link Protection",
            "ping": "Ping Protection",
            "auto_delete": "Auto Delete",
            "auto_slowmode": "Auto Slowmode",
            "reaction": "Reaction Filter",
            "QOFTD": "Question of the Day"
        }
        
        self.page_names: list[str] = list(self.global_config.keys())
        self.page_len: int = len(self.page_names)-1
        self.current_position: str = current_position if current_position else self.page_names[-1]

    def _handle_imports(self, guild_id: int) -> None:
        shared.logger.log("NP_DEBUG", f"@AdvancedPaginator._handle_imports > Importing handlers.")
        from .pages import HelpPages, ConfigPages
        from .configurator import Configurator
        
        self.help_obj: HelpPages = HelpPages(guild_id)
        self.config_obj: ConfigPages = ConfigPages(guild_id)
        self.configurator: Configurator = Configurator(guild_id)
        shared.logger.log("NP_DEBUG", f"@AdvancedPaginator._handle_imports > Imported and executed handlers..")

    def create_back_button(self, item: bool = False) -> typing.Self | discord.Button:
        button = discord.ui.Button(label="↩", custom_id="PAGINATOR:RETURN", style=discord.ButtonStyle.red)
        if item:
            return button
        return self.add_item(button)
    
    def create_paginator_buttons(self) -> typing.Self:
        self.add_item(discord.ui.Button(label="◄", custom_id="PAGINATOR:BACK", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(emoji="❔", custom_id="PAGINATOR:INFO", style=discord.ButtonStyle.green))
        self.add_item(discord.ui.Button(emoji="⚙️", custom_id="CONFIG:START", style=discord.ButtonStyle.gray))
        self.add_item(discord.ui.Button(label="►", custom_id="PAGINATOR:NEXT", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="✕", custom_id="PAGINATOR:STOP", style=discord.ButtonStyle.red))
        shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.create_paginator_buttons > Created and appended PAGINATOR buttons to view.")
        return self

    async def update_message(self, interaction: discord.Interaction, data: dict[str, typing.Any]) -> None:
        shared.logger.log("NP_DEBUG", f"@BaseConfigCMDView.update_message > Updating message...")
        if interaction.response.is_done():
            return await interaction.edit_original_response(**data)

        await interaction.response.edit_message(**data)

    async def create_modal(self, title: str, custom_id: str, text_inputs: list[discord.TextInput]) -> dict[str, str | list[dict]] | None:
        modal: ModalHelper = ModalHelper(title=title, custom_id=custom_id)
        for item in text_inputs:
            modal.add_item(item)

        await self.interaction.response.send_modal(modal)
        data: dict = await modal.clean_data()
        
        if data.get("error") or not data:
            raise ValueError("Empty modal response or error.")
        
        self.interaction = data.get("interaction")
        return data

    async def change_page(self, custom_id: str) -> None:
        guild_db: dict = shared.db.load_data(self.interaction.guild.id)
        
        if custom_id.endswith(":BACK") or custom_id.endswith(":NEXT"):
            value: int = 1 if custom_id.endswith(":NEXT") else -1
            currentPage: int = self.page_names.index(self.current_position)

            index: int = 0 if currentPage + value > self.page_len else self.page_len if currentPage + value < 0 else currentPage + value
            self.current_position = self.page_names[index]

            if config := guild_db.get(self.current_position):
                shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.change_page > Changing page to {self.current_position}.")
                await self.update_message(self.interaction, {"embed": self.config_obj.create_embed(config, name=self.global_config.get(self.current_position), interaction=self.interaction, blueprint_embed=getattr(self.config_obj, self.current_position, None))})
            else:
                raise ValueError(f"Could not find data for {self.current_position} in {self.interaction.guild.name} ({self.interaction.guild.id}) >> Triggered by PAGINATOR interaction.")

        elif custom_id.endswith(":INFO"):
            shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.change_page > Changing page to INFO.")
            await self.update_message(self.interaction, {"embed": getattr(self.help_obj, self.current_position, None), "view": self.clear_items().create_back_button()})

        elif custom_id.endswith(":STOP"):
            shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.change_page > Changing page to STOP.")
            await self.update_message(self.interaction, {"view": self.clear_items()})
            self.stop()

        elif custom_id.endswith(":RETURN"):
            shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.change_page > Resetting configurator.", "NP_DEBUG")
            self.configurator.reset_configurator()
            if config := guild_db.get(self.current_position):
                shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.change_page > Changing page to RETURN.")
                await self.update_message(self.interaction, {"embed": self.config_obj.create_embed(config, name=self.global_config.get(self.current_position), interaction=self.interaction, blueprint_embed=getattr(self.config_obj, self.current_position, None)), "view": self.clear_items().create_paginator_buttons()})
            else:
                raise ValueError(f"Could not find data for {self.current_position} in {self.interaction.guild.name} ({self.interaction.guild.id}) >> Triggered by RETURN interaction.")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.data:
            raise ValueError("Discord did not provide interaction data. >> Triggered by INTERACTION_CHECK")

        custom_id: str = dict(interaction.data ).get('custom_id')
        self.interaction: discord.Interaction = interaction
        shared.logger.log("NP_DEBUG", f"@AdvancedPaginator.interaction_check > Recieved interaction with ID: {custom_id}.")

        if interaction.type == discord.InteractionType.component:
            if custom_id.startswith("PAGINATOR:"):
                await self.change_page(custom_id)
            elif custom_id.startswith("CONFIG:"):
                await self.configurator.handle_interaction(custom_id, self)
            else:
                raise NameError("Could not resolve custom_id of the interaction. >> Triggered by INTERACTION_CHECK")
        return
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.item.Item) -> None:
        error_id: str = await report_error(self.on_error, error)

        error_embed: discord.Embed = self.help_obj.ERROR
        error_embed.description = error_embed.description.format(error=error_id)

        await self.update_message(interaction, {"embed": error_embed, "view": self.clear_items()})
