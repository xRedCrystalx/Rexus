import discord, sys
sys.dont_write_bytecode = True
from .errors import report_error

from xRedUtilsAsync.iterables import to_iterable
class ModalHelper(discord.ui.Modal):
    def __init__(self, title: str, custom_id: str, timeout: float | None = None) -> None:
        """
        Handler for `discord.Modal`
        - `.add_items()` - adds items to the Modal
    
        
        - `.get_data()` - get original dict (discord response) or error
        - `.clean_data()` - get filtered/clean dict or error
        """
        
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        
        self.data: None | dict = None
        self.interaction: discord.Interaction = None
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.data = dict(interaction.data) | {"interaction": interaction}

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await report_error(f"ModalHelper.on_error<{interaction.data["custom_id"]}>", "full")
        self.data = {"error": error, "interaction": interaction}

    async def on_timeout(self) -> None:
        self.data = {"error": "Timed out."}
        self.stop()

    async def add_items(self, items: list[discord.TextInput] | discord.TextInput) -> None:
        """|async|"""
        for item in await to_iterable(items):
            try:
                self.add_item(item)
            except Exception:
                await report_error(self.add_item, "simple")

    async def get_data(self) -> dict[str, str | list[dict] | Exception | discord.Interaction] | None:
        """
        |async|
        
        Returns raw data (discord response)
        """
        await self.wait()
        return self.data
    
    async def clean_data(self) -> dict[str, str | dict[str, str] | Exception] | None:
        """|async|"""
        raw: dict[str, str | list[dict]] = await self.get_data()
        if not raw or raw.get("error"):
            return raw
    
        return {
            "modal_id": raw.get("custom_id"), 
            "interaction": raw.get("interaction"),
            "components": {
                    item["components"][0].get("custom_id"): item["components"][0].get("value") for item in raw.get("components")
            }
        }
