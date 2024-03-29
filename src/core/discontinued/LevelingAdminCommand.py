import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon

class buttonHandler(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=15)
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.original_message: discord.InteractionMessage = None
        self.isClicked = False
        self.server_data: dict = None
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        
    @discord.ui.button(label = "Yes, wipe it.", style = discord.ButtonStyle.green)
    async def buttonYes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed: discord.Embed  = self.original_message.embeds[0]
        try:
            self.CONNECTOR.database.save_data(server_id=interaction.guild.id, update_data=self.server_data)
            embed.title = "Task completed."
            embed.description = "Requsted action has been executed."
            await self.CONNECTOR.logging(logType="IMPORTANT", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_admin reset all{self.c.R} slash command. REQUEST WAS SUCCESSFULLY EXECUTED. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

        except Exception as error:
            id: str = await self.CONNECTOR.callable(fun="error_id")
            embed.title = "Error"
            embed.description = f"An error has occuered. Error ID: {id}"
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_admin reset all{self.c.R} slash command. REQUEST FAILED TO EXECUTE. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}Error ID{self.c.R}: {id} {self.c.Red}Error: {type(error).__name__}: {error}{self.c.R}")

        await interaction.response.edit_message(view=None, embed=embed)
        self.isClicked = True
    
    @discord.ui.button(label = "No, stop!!1!", style = discord.ButtonStyle.red)
    async def buttonNo(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed: discord.Embed  = self.original_message.embeds[0]
        embed.title = "Stopped."
        embed.description = "Request canceled. No changes were made."
        await interaction.response.edit_message(view=None, embed=embed)
        self.isClicked = True
        await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_admin reset all{self.c.R} slash command. REQUEST WAS CANCELED. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
    
    async def on_timeout(self) -> None:
        if self.original_message is not None and self.isClicked is False:
            await self.original_message.edit(view=None)

class LevelingAdminCommand(commands.GroupCog, name="lvl_admin"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database
        self.lvlSystem: syscon.LevelingSystem = self.CONNECTOR.lvlSys
        self.trigger: bool = False

    @app_commands.choices(action=[app_commands.Choice(name="Add", value="add"), app_commands.Choice(name="Remove", value="remove")],
                          level=[app_commands.Choice(name="Message", value="message"), app_commands.Choice(name="Voice", value="voice"), app_commands.Choice(name="Reaction", value="reaction")],
                          option=[app_commands.Choice(name="XP", value="xp"), app_commands.Choice(name="Level", value="level")]) 
    @app_commands.command(name = "set", description = "Gives/removes XP/levels of a user")
    async def set(self, interaction: discord.Interaction, member: discord.Member, action: app_commands.Choice[str], level: app_commands.Choice[str], option: app_commands.Choice[str], value: int) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        
        async def lvl_to_xp(levels: int) -> int:
            current_lvl: int = ServerData["LevelingSystem"][str(member.id)]["levels"][option.value]
            return sum([await self.CONNECTOR.callable(fun="calc_xp", level=current_lvl + 1 + i)] for i in range(levels))
        
        if ServerData["Plugin"]["LevelingSystem"] is False or ServerData["LevelingSystem"]["config"]["levels"][level.value] is False:
            return await interaction.response.send_message(content="Please enable leveling system/level in the configuration.")

        if str(member.id) not in ServerData["LevelingSystem"]["members"]:
            return await interaction.response.send_message(content="The data you provided could not be saved due to the absence of a corresponding member in the database. Kindly request the member to send at least one message within the server. If the issue persists, please notify @xRedCrystalx for further investigation.")

        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                if option.value == "xp":
                    if action.value == "add":
                        ServerData["LevelingSystem"][str(member.id)][option.value]["xp"] + value
                        ServerData["LevelingSystem"][str(member.id)][option.value]["global_xp"] + value
                        self.trigger = True
                    else:
                        await interaction.response.send_message(content="Removing XP is currently under development.", ephemeral=True)
                else:
                    if action.value == "add":
                        xp = await lvl_to_xp(value)
                        ServerData["LevelingSystem"][str(member.id)][option.value]["xp"] + xp
                        ServerData["LevelingSystem"][str(member.id)][option.value]["global_xp"] + xp
                        self.trigger = True
                    else:
                        #ServerData["LevelingSystem"]["config"]["levels"][level.value] - value
                        #if ServerData["LevelingSystem"]["config"]["levels"][level.value] < 0:
                        #    ServerData["LevelingSystem"]["config"]["levels"][level.value] = 0
                        await interaction.response.send_message(content="Removing levels is currently under development.", ephemeral=True)

                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                
                if self.trigger:
                    db: dict = {interaction.guild.id: {member.id : 0}} if level == "voice" else {interaction.guild.id: {1234567 : [member.id]}} if level == "reaction" else {interaction.guild.id: {member.id : {"counter" : 0, "xp" : 0}}}
                    await self.lvlSystem.caller(option=level, db=db)
                    self.trigger = False
                
                await interaction.response.send_message(f"Sucessfully {action.value}ed {level.value} {option.value} {'to' if action.value == 'add' else 'of'} {member.display_name} ({member.id}).")
                await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_admin set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) action: {action.name} level: {level.name} option: {option.name} value: {value} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set leveling system's configuration.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/lvl_admin set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) action: {action.name} level: {level.name} option: {option.name} value: {value} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:
            await interaction.response.send_message(content="You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_admin set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) action: {action.name} level: {level.name} option: {option.name} value: {value}")

    @app_commands.choices(level=[app_commands.Choice(name="Message", value="message"), app_commands.Choice(name="Voice", value="voice"), app_commands.Choice(name="Reaction", value="reaction"), app_commands.Choice(name="All", value="all"), app_commands.Choice(name="Merged", value="GLOBAL")]) 
    @app_commands.command(name = "reset-all", description = "Resets all members lvl data.")
    async def reset_all(self, interaction: discord.Interaction, level: app_commands.Choice[str]) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            buttons = buttonHandler()
            if level.value == "all":
                ServerData["LevelingSystem"]["members"] = {}
                embed: discord.Embed = discord.Embed(title="Confirm!", description=f"**Are you 100% sure?**\nClicking on green button will result to complete level wipe from EVERYONE.", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
                await interaction.response.send_message(embed=embed, view=buttons, ephemeral=True)
                buttons.original_message = await interaction.original_response()
                buttons.server_data = ServerData
            
            elif level.value == "GLOBAL":
                for member, data in ServerData["LevelingSystem"]["members"].items():
                    data["GLOBAL"]["level"] = 0
                    data[level.value]["xp"] = 0
                    data[level.value]["global_xp"] = 0
                    data[level.value]["rewards"] = []
                    
                    data[level.value]["contribution"]["message"] = 0
                    data[level.value]["contribution"]["reaction"] = 0
                    data[level.value]["contribution"]["voice"] = 0
                    data[level.value]["contribution"]["giveaway"] = 0

            else:
                for member, data in ServerData["LevelingSystem"]["members"].items():
                    data[level.value]["counter" if level.value != "voice" else "time"] = 0
                    data[level.value]["xp"] = 0
                    data[level.value]["global_xp"] = 0
                    data[level.value]["rewards"] = []
                    data["levels"][level.value] = 0
                    
                embed: discord.Embed = discord.Embed(title="Confirm!", description=f"**Are you 100% sure?**\nClicking on green button will result to complete level wipe of {level.value} from EVERYONE.", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
                await interaction.response.send_message(embed=embed, view=buttons, ephemeral=True)
                buttons.original_message = await interaction.original_response()
                buttons.server_data = ServerData
        else:
            await interaction.response.send_message(content="You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_admin reset all{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: level: {level.value} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.choices(level=[app_commands.Choice(name="Message", value="message"), app_commands.Choice(name="Voice", value="voice"), app_commands.Choice(name="Reaction", value="reaction"), app_commands.Choice(name="All", value="all")]) 
    @app_commands.command(name = "reset", description = "Resets user's lvl data.")
    async def reset(self, interaction: discord.Interaction, member: discord.Member, level: app_commands.Choice[str]) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            if not ServerData["LevelingSystem"]["members"].get(str(member.id)):
                await interaction.response.send_message(content="Could not find the specified member in the database.")
                return
            
            if level.value == "all":
                try:
                    ServerData["LevelingSystem"]["members"].pop(str(member.id))
                    self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                    await interaction.response.send_message(f"Successfully reset {member.display_name}'s level data.")
                    await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_admin reset{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) level: {level.value} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
                
                except Exception as error:
                    id: str = await self.CONNECTOR.callable(fun="error_id")
                    await interaction.response.send_message(f"Failed to reset {member.display_name}'s level data. Error ID: {id}")
                    await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed used {self.c.Yellow}/lvl_admin reset{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) level: {level.value} {self.c.DBlue}Error ID{self.c.R}: {id} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.Red}Error: {type(error).__name__}: {error}{self.c.R}")

            elif level.value == "GLOBAL":
                data[level.value]["level"] = 0
                data[level.value]["xp"] = 0
                data[level.value]["global_xp"] = 0
                data[level.value]["rewards"] = []
                    
                data[level.value]["contribution"]["message"] = 0
                data[level.value]["contribution"]["reaction"] = 0
                data[level.value]["contribution"]["voice"] = 0
                data[level.value]["contribution"]["giveaway"] = 0
            else:
                try:
                    data= ServerData["LevelingSystem"]["members"][str(member.id)]
                    data[level.value]["counter" if level.value != "voice" else "time"] = 0
                    data[level.value]["xp"] = 0
                    data[level.value]["global_xp"] = 0
                    data[level.value]["rewards"] = []
                    data["levels"][level.value] = 0

                    self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                    await interaction.response.send_message(f"Successfully reset {member.display_name}'s {level.value} level data.")
                    await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/lvl_admin reset{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) level: {level.value} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
                
                except Exception as error:
                    id: str = await self.CONNECTOR.callable(fun="error_id")
                    await interaction.response.send_message(f"Failed to reset {member.display_name}'s {level.value} level data. Error ID: {id}")
                    await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed used {self.c.Yellow}/lvl_admin reset{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) level: {level.value} {self.c.DBlue}Error ID{self.c.R}: {id} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.Red}Error: {type(error).__name__}: {error}{self.c.R}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/lvl_admin reset{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) level: {level.value} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LevelingAdminCommand())

#remove from global, reset lvl and xp, call loop, get lvl, xp and 2xglobal, global/2