import sys, discord
sys.dont_write_bytecode = True
from discord.ui import View

from .errors import report_error, new_error_embed

class ViewHelper(View):
    def __init__(self, custom_id: str, timeout: float | None = 60) -> None:
        super().__init__(timeout=timeout)
        self.interaction: discord.Interaction = None
        self.custom_id: str = custom_id
    
    async def on_timeout(self) -> None:
        self.stop()
        try:
            await self.interaction.edit_original_response(view=None)
        # original response does not exist
        except: pass
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, item) -> None:
        error_id: str = await report_error(f"ViewHelper.on_error[{self.custom_id}]<{interaction.guild.id}>", "full")
        embed: discord.Embed = await new_error_embed(error_id)
        await interaction.response.send_message(embed=embed, ephemeral=True)
