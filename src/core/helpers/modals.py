import discord, sys
sys.dont_write_bytecode = True
from discord.ui import Modal
import src.connector as con


class ModalHandler(Modal):
    def __init__(self, title: str, custom_id: str, timeout: float | None = None) -> None:
        """Handler for `discord.Modal`
        
        - my_modal.get_data()     [`dict` | `None`] -> get original dict of returned data or error
        or
        - my_modal.clean_data()   [`dict` | `None`] -> get filtered/clean dict of returned data or error"""
        
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        
        self.shared: con.Shared = con.shared
        self.data: None | dict = None
        self.interaction: discord.Interaction = None
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.data = dict(interaction.data) | {"interaction": interaction}
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        self.shared.logger.log(f"@ModalHandler.on_error[{interaction.data['custom_id']}] > {type(error).__name__}: {error}", "ERROR")
        self.data = {"error": error, "interaction": interaction}
    
    async def on_timeout(self) -> None:
        self.stop()

    async def get_data(self) -> dict[str, str | list[dict] | Exception | discord.Interaction] | None:
        await self.wait()
        return self.data
    
    async def clean_data(self) -> dict[str, str | list[dict] | Exception] | None:
        raw: dict[str, str | list[dict]] = await self.get_data()
        if not raw or raw.get("error"):
            return raw
    
        return {"modal_id": raw.get("custom_id"), "interaction": raw.get("interaction"),
                "components": [{"custom_id": item["components"][0].get("custom_id"),"value": item["components"][0].get("value")} for item in raw.get("components")]}


    

