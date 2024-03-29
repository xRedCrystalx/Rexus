import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon


class AICommand(commands.GroupCog, name="ai"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database


    @app_commands.command(name = "teach_me", description = "Help me teach an AI!")
    async def teach(self, interaction: discord.Interaction, question: str, answer: str) -> None:
        with open(f"{self.CONNECTOR.path}/src/system/AIData.txt", mode="a+", encoding="utf-8") as db:
            db.write(f"[\"{question}\", \"{answer}\"]\n")
        
        await interaction.response.send_message(f"""**Saved Data**
> **Question:** `{question}`
> **Answer:** `{answer}`
        
Thank you for helping me train an AI!""", ephemeral=True)
        await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/ai teach_me{self.c.R} slash command. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

    @app_commands.command(name = "channel", description = "Sets the channel where bot will talk in.")
    async def channel(self, interaction: discord.Interaction, set: discord.TextChannel) -> None:
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        
        if interaction.user.guild_permissions.administrator or interaction.user.id in [x for x in BotData["owners"]]:
            try:
                ServerData["AI"] = set.id
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(f"Set **AI Channel** to {set.mention}")
                await self.CONNECTOR.logging(logType="CHANGE", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/ai channel set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: set: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
            except Exception as Error:
                id: str = await self.CONNECTOR.callable(fun="error_id")
                await interaction.response.send_message(f"Failed to set **AI Channel** to {set.mention}.\nError ID: {id}")
                await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/ai channel set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: set: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(Error).__name__}: {Error}")
        else:   
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/ai channel set{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: set: {set.name} ({set.id}) {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AICommand())
