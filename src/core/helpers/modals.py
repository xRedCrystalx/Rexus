import discord, sys
sys.dont_write_bytecode = True
from discord.ui import Modal
import src.connector as con


class ModalHandler(Modal):
    def __init__(self, title: str, custom_id: str, timeout: float | None = None) -> None:
        """Handler for `discord.Modal`
        
        - my_modal.wait()      [`None`]          -> wait for modal to finish
        - my_modal.get_data()  [`dict` | `None`] -> get dict of returned data or error"""
        
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        
        self.shared: con.Shared = con.shared
        self.data: None | dict = None
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.data = dict(interaction.data)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        self.shared.logger.log(f"@ModalHandler.on_error[{interaction.data['custom_id']}] > {type(error).__name__}: {error}", "ERROR")
        self.data = {"error": error}
    
    async def on_timeout(self) -> None:
        self.stop()

    def get_data(self) -> dict[str, str | list[dict] | Exception] | None:
        return self.data

    

