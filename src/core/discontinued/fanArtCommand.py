import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon

class fanArtCommand(commands.GroupCog, name="fanart"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database

    @app_commands.command(name = "add", description = "Enables listener for that channel")
    async def set(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                if channel.id not in ServerData["FanArt"]:
                    ServerData["FanArt"].append(channel.id)
                    
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Added {channel.mention} to the watchlist")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/fanart set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {channel.name} ({channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to add {channel.mention} to the watchlist.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/fanart set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {channel.name} ({channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/fanart set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {channel.name} ({channel.id}){self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")


    @app_commands.command(name = "remove", description = "Removes channel from the watchlist.")
    async def delete(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        
        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["FanArt"].remove(channel.id)
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Removed {channel.mention} from the watchlist.")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/fanart remove{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {channel.name} ({channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to remove {channel.mention} from the watchlist.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/fanart remove{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {channel.name} ({channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:   
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/fanart remove{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {channel.name} ({channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fanArtCommand())