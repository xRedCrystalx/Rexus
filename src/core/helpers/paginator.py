import sys, discord
sys.dont_write_bytecode = True

from .views import ViewHelper
from .errors import report_error

class BasicPaginator(ViewHelper):
    def __init__(self, messages: list[discord.Embed | str], timeout: float | None = None) -> None:
        super().__init__("PaginatorView", timeout)

        self.messages: list[discord.Embed | str] = messages
        self.lenList: int = len(self.messages)-1
        self.currentPage: int = -1

        if messages:
            self.create_buttons()

    def create_buttons(self) -> None:
        self.add_item(discord.ui.Button(label="◄", custom_id=f"PAGINATOR:BACK", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="►", custom_id=f"PAGINATOR:NEXT", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="✕", custom_id=f"PAGINATOR:STOP", style=discord.ButtonStyle.red))  
 
    async def paginator(self, value: int | bool, interaction: discord.Interaction) -> None:
        if value != "STOP":
            self.currentPage: int = 0 if self.currentPage + value > self.lenList else self.lenList if self.currentPage + value < 0 else self.currentPage + value
            message: str | discord.Embed = self.messages[self.currentPage]

            if isinstance(message, str):
                await interaction.response.edit_message(content=f"{message}\n\nPage {self.currentPage+1}/{self.lenList+1}")

            elif isinstance(message, discord.Embed):
                if not message.footer:
                    message.set_footer(text=f"Page {self.currentPage+1}/{self.lenList+1}")

                await interaction.response.edit_message(embed=message)
            else:
                await report_error(f"BasicPaginator.paginator<{interaction.guild.id}>", f"An error has occured. Could not find `str` or `discord.Embed` object in list. Index: {self.currentPage}")
        else:
            await interaction.response.edit_message(view=None)
            self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id: str = dict(interaction.data).get('custom_id')
        if custom_id.startswith("PAGINATOR:"):
            await self.paginator(value=1 if custom_id.endswith(":NEXT") else -1 if custom_id.endswith(":BACK") else "STOP", interaction=interaction)
        else:
            # Fail or attempted ID manipulation
            self.stop()
