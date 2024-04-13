import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon


class Input(discord.ui.Modal, title="Responder"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        super().__init__(timeout=None) 

    trigger = discord.ui.TextInput(label="Trigger:", placeholder="Input trigger message here!", style=discord.TextStyle.short, required=True)
    select = discord.ui.TextInput(label="Option:", placeholder="Choose between: 'inContent' or 'startsWith'", style=discord.TextStyle.short, required=True)
    response = discord.ui.TextInput(label="Response:", placeholder="Input response message here! (Word 'None' only will result to trigger deletion from database)", style=discord.TextStyle.long, min_length=1, max_length=1500, required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        ServerData: dict = self.CONNECTOR.database.load_data(server_id=interaction.guild.id, serverData=True)
        if 'inContent' == self.select.value:
            option = False
        elif 'startsWith' == self.select.value:
            option = True
        else:
            return await interaction.response.send_message('Wrong option selected. Request terminated.', ephemeral=True)
        if self.response.value == "None":
            try:
                ServerData["AutoResponder"].pop(self.trigger.value)
                self.CONNECTOR.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                return await interaction.response.send_message(f'Successfully removed `{self.trigger.value}` from database.', ephemeral=True)
            except Exception as error:
                return await interaction.response.send_message(f'Failed to remove `{self.trigger.value}` from database. Does trigger exist?', ephemeral=True)
        try:
            stripped: str = self.response.value.strip()
            if ServerData["AutoResponder"].get(self.trigger.value) is None:
                ServerData["AutoResponder"][self.trigger.value] = {"startsWith": option, "content": stripped}
            else:
                ServerData["AutoResponder"][self.trigger.value]["startsWith"] = option
                ServerData["AutoResponder"][self.trigger.value]["content"] = stripped

            self.CONNECTOR.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
            await interaction.response.send_message(f'Saved to database.\n**Trigger:** {self.trigger.value}\n**Option:** {"`startsWith`" if option else "`inContent`"}\n**Response:**\n{stripped}', ephemeral=True)
        except:
            await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class ResponderCommand(commands.Cog):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database

    @app_commands.command(name = "responder", description = "Responds on messages/commands")
    async def responder(self, interaction: discord.Interaction) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        
        if interaction.user.guild_permissions.administrator is True or interaction.user.id in [x for x in BotData["owners"]]:
            await interaction.response.send_modal(Input())
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ResponderCommand())
