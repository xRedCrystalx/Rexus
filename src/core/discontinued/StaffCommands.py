import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon


class StaffRoleCommand(commands.GroupCog, name="staff"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database

    @app_commands.command(name = "role", description = "Sets server's StaffRole for future use.")
    async def staff_role_command(self, interaction: discord.Interaction, set: discord.Role) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        
        if interaction.user.guild_permissions.administrator is True or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["ServerInfo"]["StaffRole"] = set.id
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Successfully saved `{set.name}` as **StaffRole**")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/staff role{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: role: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
            
            except Exception as Error: 
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to saved `{set.name}` as **StaffRole**.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/staff role{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: role: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/staff role{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: role: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.command(name = "channel", description = "Sets server's StaffChannel for future use.")
    async def staff_channel_command(self, interaction: discord.Interaction, set: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator is True or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["ServerInfo"]["StaffChannel"] = set.id
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Successfully saved {set.mention} as **StaffChannel**")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/staff channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to saved {set.mention} as **StaffChannel**.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/staff channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/staff channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: channel: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")


    @app_commands.command(name = "logging_channel", description = "Sets server's StaffLog Channel for future use.")
    async def staff_log_channel_command(self, interaction: discord.Interaction, set: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator is True or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["ServerInfo"]["LogChannel"] = set.id
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Successfully saved {set.mention} as **StaffLogChannel**")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/staff logging_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: logging_channel: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to saved {set.mention} as **StaffLogChannel**.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/staff logging_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: logging_channel: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")

        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/staff logging_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: logging_channel: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StaffRoleCommand())
