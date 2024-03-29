import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon


class AntiPingCommand(commands.GroupCog, name="ping_protection"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database
    
    @app_commands.command(name="set_role", description="Set roles. Needed for Bot to work properly.")
    @app_commands.choices(option=[
        app_commands.Choice(name="BypassRole", value="BypassRole"),
        app_commands.Choice(name="MemberProtectionRole", value="MemberProtection"),
        app_commands.Choice(name="StaffProtectionRole", value="StaffProtection"),
        app_commands.Choice(name="YouTuberProtectionRole", value="YouTuberProtection"),
        ])
    async def set_role(self, interaction: discord.Interaction, option: app_commands.Choice[str], role: discord.Role) -> None:
        BotData, ServerData =  self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                if option.value == "BypassRole":
                    ServerData["PingProtection"][option.value] = role.id
                else:    
                    ServerData["PingProtection"][option.value]["Role"] = role.id
                    
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/ping_protection set_role{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} role: {role.name} ({role.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
                await interaction.response.send_message(f"Successfully saved `{role.name}` as **{option.name}**")
                
            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to saved `{role.name}` as **{option.name}**.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/ping_protection set_role{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} role: {role.name} ({role.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/ping_protection set_role{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} role: {role.name} ({role.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
    
    @app_commands.command(name="detect_reply_pings", description="Enable/Disable reply pings detection.")
    async def switch(self, interaction: discord.Interaction, switch: bool) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["PingProtection"]["DetectReplyPings"] = switch
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Successfully set **DetectReplyPings** to `{switch}`.")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/detect_reply_pings set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: switch: {switch} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set **DetectReplyPings** to `{switch}`.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/detect_reply_pings set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: switch: {switch} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/detect_reply_pings set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: switch: {switch} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.command(name="rules", description="Sets rules of specific Detection.")
    @app_commands.choices(role=[
        app_commands.Choice(name="MemberProtectionRole", value="MemberProtection"),
        app_commands.Choice(name="StaffProtectionRole", value="StaffProtection"),
        app_commands.Choice(name="YouTuberProtectionRole", value="YouTuberProtection"),
        app_commands.Choice(name="Everyone/HereProtection", value="Everyone/Here"),
        app_commands.Choice(name="Bots", value="Bot"),
        ])
    async def rules(self, interaction: discord.Interaction, role: app_commands.Choice[str], ping_staff: bool, delete_message: bool, log_message: bool, log_channel: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["PingProtection"][role.value]["Ping"] = ping_staff
                ServerData["PingProtection"][role.value]["Log"] = log_message
                ServerData["PingProtection"][role.value]["Delete"] = delete_message
                ServerData["PingProtection"][role.value]["LogChannel"] = log_channel.id
                
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                try:
                    ObjRole: discord.Role = interaction.guild.get_role(ServerData["PingProtection"][role.value]["Role"])
                    data: str = f"({ObjRole.name} > {ObjRole.id})"
                except:
                    data: str = ""
                await interaction.response.send_message(f"__**Successfully set rules.**__\n> **Role**: {role.name} {data}\n> StaffPing: `{ping_staff}`\n> DeleteMessage: `{delete_message}`\n> LogMessage: `{log_message}`\n> LogChannel: {log_channel.mention}")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/ping_protection rules{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: role: {role.name} ping_staff: {ping_staff} delete_message: {delete_message} log_message: {log_message} log_channel: {log_channel.name} ({log_channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
            
            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set rules.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/ping_protection rules{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: role: {role.name} ping_staff: {ping_staff} delete_message: {delete_message} log_message: {log_message} log_channel: {log_channel.name} ({log_channel.id}) {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/ping_protection rules{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: role: {role.name} ping_staff: {ping_staff} delete_message: {delete_message} log_message: {log_message} log_channel: {log_channel.name} ({log_channel.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")


    @app_commands.command(name="ignore_channel", description="Adds specified channel into ignored channels list")
    @app_commands.choices(option=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove")
        ])
    async def ignore_channels(self, interaction: discord.Interaction, option: app_commands.Choice[str], channel: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            channel_match: bool = channel.id in [x for x in ServerData["PingProtection"]["IgnoreChannels"]]
            if channel_match and option.value == "add":
                await interaction.response.send_message(content=f"Provided channel ({channel.mention}) is already in **Ignored Channels** list!")
                
            elif channel_match is False and option.value == "remove":
                await interaction.response.send_message(content=f"Provided channel ({channel.mention}) is not in **Ignored Channels** list!")
                
            elif channel_match is False and option.value == "add":
                ServerData["PingProtection"]["IgnoreChannels"].append(channel.id)
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(content=f"Added {channel.mention} in **Ignored Channels** list!")
            
            elif channel_match and option.value == "remove":
                ServerData["PingProtection"]["IgnoreChannels"].remove(channel.id)
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(content=f"Removed {channel.mention} from **Ignored Channels** list!")
            
            await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} executed {self.c.Yellow}/ping_protection ignore_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} channel: {channel.name} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/ping_protection ignore_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} channel: {channel.name} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AntiPingCommand())
