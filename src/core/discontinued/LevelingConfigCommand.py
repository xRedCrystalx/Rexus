import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon

class LevelingConfigCommand(commands.GroupCog, name="lvl_config"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database
        
    #@syscon.permission_check(_type="lvl_config set")
    @app_commands.choices(level=[app_commands.Choice(name="Message", value="message"), app_commands.Choice(name="Voice", value="voice"), app_commands.Choice(name="Reaction", value="reaction")]) 
    @app_commands.command(name = "set", description = "Enables/Disables specific leveling.")
    async def set(self, interaction: discord.Interaction, level: app_commands.Choice[str], switch: bool) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["LevelingSystem"]["config"]["levels"][level.value] = switch
                await interaction.response.send_message(f"Sucessfully set **{level.name}** to `{switch}`!")

                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_config set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: level: {level.name} switch: {switch} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set **{level.name}** to `{switch}`.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/lvl_config set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: level: {level.name} switch: {switch} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_config set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: level: {level.name} switch: {switch} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.choices(option=[app_commands.Choice(name="Server", value="guild"), app_commands.Choice(name="Direct Message", value="dm")]) 
    @app_commands.command(name = "notification", description = "Creates rules for level up notifications.")
    async def notification(self, interaction: discord.Interaction, option: app_commands.Choice[str], send_message: bool, ping_member: bool = False, message: str = "Congrats {member}, you just advanced to {type} level {num}!") -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["LevelingSystem"]["config"]["notifications"][option.value]["send"] = send_message
                ServerData["LevelingSystem"]["config"]["notifications"][option.value]["ping"] = ping_member
                ServerData["LevelingSystem"]["config"]["notifications"][option.value]["message"] = message
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Sucessfully set configuration for {option.name}!\n> **Send message:** `{send_message}`\n> **Ping Member:** `{ping_member}`\n> **Message:** {message}")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_config notification{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} send_message: {send_message} ping_member: {ping_member} message: {message} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set leveling system's configuration.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/lvl_config notification{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} send_message: {send_message} ping_member: {ping_member} message: {message} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_config notification{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} send_message: {send_message} ping_member: {ping_member} message: {message} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.choices(option=[app_commands.Choice(name="Add", value="add"), app_commands.Choice(name="Remove", value="remove")], level_type=[app_commands.Choice(name="Message", value="message"), app_commands.Choice(name="Voice", value="voice"), app_commands.Choice(name="Reaction", value="reaction"), app_commands.Choice(name="Global", value="GLOBAL")]) 
    @app_commands.command(name = "reward", description = "Set reward for level-ups!")
    async def reward(self, interaction: discord.Interaction, option: app_commands.Choice[str], level_type: app_commands.Choice[str], level: int, role: discord.Role) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            if option.value == "add":
                try:
                    ServerData["LevelingSystem"]["config"]["rewards"][level_type.value][str(level)] = role.id
                    self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                    await interaction.response.send_message(f"Sucessfully set `{role}` as role reward for {level_type.value} level {level}!")
                    await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_config reward{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} level_type: {level_type.name} level: {level} role: {role} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

                except Exception as Error:
                    id: str = await self.CONNECTOR.callable(fun="error_id")
                    await interaction.response.send_message(f"Failed to set leveling system's configuration.\nError ID: {id}")
                    await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/lvl_config reward{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} level_type: {level_type.name} level: {level} role: {role} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
            else:
                try:
                    if ServerData["LevelingSystem"]["config"]["rewards"][level_type.value].get(str(level)):
                        ServerData["LevelingSystem"]["config"]["rewards"][level_type.value].pop(str(level))
                        self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                        await interaction.response.send_message(f"Sucessfully removed {level_type.value} level {level} reward!")
                        await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_config reward{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} level_type: {level_type.name} level: {level} role: {role} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
                    else:
                        await interaction.response.send_message(f"Could not find {level_type.value} level {level} reward in database. No change applied.")
                        await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_config reward{self.c.R} slash command, but no change was applied. {self.c.DBlue}Input{self.c.R}: option: {option.name} level_type: {level_type.name} level: {level} role: {role} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

                except Exception as error:
                    id: str = await self.CONNECTOR.callable(fun="error_id")
                    await interaction.response.send_message(f"Failed to set leveling system's configuration.\nError ID: {id}")
                    await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/lvl_config reward{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} level_type: {level_type.name} level: {level} role: {role} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(error).__name__}: {error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_config reward{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} level_type: {level_type.name} level: {level} role: {role} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.choices(option=[app_commands.Choice(name="Single-level", value="singlelevel"), app_commands.Choice(name="Multi-level", value="multilevel")]) 
    @app_commands.command(name = "switch", description = "Switches between single-level system and multi-level system")
    async def switch(self, interaction: discord.Interaction, option: app_commands.Choice[str], send_message: bool, ping_member: bool = False, message: str = "Congrats {member}, you just advanced to {type} level {num}!") -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["LevelingSystem"]["config"]["switch"] = option.value
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                
                await interaction.response.send_message(f"Sucessfully set leveling type to `{option.name}`!")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_config switch{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set leveling system's configuration.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/lvl_config switch{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_config switch{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LevelingConfigCommand())