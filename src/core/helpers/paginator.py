import sys, discord
sys.dont_write_bytecode = True
from .views import ViewHelper

class BasicPaginator(ViewHelper):
    def __init__(self, messages: list[discord.Embed | str], timeout: float | None = None) -> None:
        super().__init__(timeout)

        self.msgList: list = messages
        self.lenList: int = len(self.msgList)-1
        self.currentPage: int = -1

        self.create_buttons()

    def create_buttons(self) -> None:
        self.add_item(discord.ui.Button(label="◄", custom_id=f"PAGINATOR:BACK", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="►", custom_id=f"PAGINATOR:NEXT", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="✕", custom_id=f"PAGINATOR:STOP", style=discord.ButtonStyle.red))  
 
    async def paginator(self, value: int | bool, interaction: discord.Interaction) -> None:
        self.lenList: int = len(self.msgList)-1
        index: int = 0 if self.currentPage + value > self.lenList else self.lenList if self.currentPage + value < 0 else self.currentPage + value
        self.currentPage = index
        if value:
            if isinstance(self.msgList[index], str):
                await interaction.response.edit_message(content=f"{self.msgList[index]}\n\nPage {self.currentPage+1}/{self.lenList+1}")
            
            elif isinstance(self.msgList[index], discord.Embed):
                embed: discord.Embed = self.msgList[index]
                embed.set_footer(text=f"Page {self.currentPage+1}/{self.lenList+1}")
                embed.timestamp = self.shared.time.datetime()
                await interaction.response.edit_message(embed=embed)
            else:
                self.shared.logger(f"@BasicPaginator.paginator > An error has occured. Could not find `str` or `discord.Embed` object in list. Index: {index}")
        else:
            await interaction.response.edit_message(view=None)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id: str = dict(interaction.data).get('custom_id')
        if interaction.type == discord.InteractionType.component and custom_id.startswith("PAGINATOR:"):
            await self.paginator(value=1 if custom_id.endswith(":NEXT") else -1 if custom_id.endswith(":BACK") else False, interaction=interaction)
        return True
