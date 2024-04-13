import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import connector as syscon

class AutoDeleteCommand(commands.GroupCog, name="autodelete"):
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.c: syscon.Colors.C | syscon.Colors.CNone = self.CONNECTOR.colors
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.database: syscon.databaseHandler = self.CONNECTOR.database
        self.seconds_per_unit: dict[str, int] = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

    @app_commands.command(name="watch", description="Adds specified channel into watchlist")
    @app_commands.choices(option=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove")
        ])
    async def watch(self, interaction: discord.Interaction, option: app_commands.Choice[str], channel: discord.TextChannel, time: str) -> None:
        def convert_to_seconds(VALUE: int) -> int:
            return int(VALUE[:-1]) * self.seconds_per_unit[VALUE[-1]]
        BotData, ServerData = self.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)

        if interaction.user.guild_permissions.administrator is True or interaction.user.id in [x for x in BotData["owners"]]:
            channel_match: bool = str(channel.id) in [x for x in ServerData["AutoDelete"]]
            if channel_match is True and option.value == "add":
                await interaction.response.send_message(content=f"Provided channel ({channel.mention}) is already in **Watchlist**!")

            elif channel_match is False and option.value == "remove":
                await interaction.response.send_message(content=f"Provided channel ({channel.mention}) is not in **Watchlist**!")

            elif channel_match is False and option.value == "add":
                ServerData["AutoDelete"].update({str(channel.id) : convert_to_seconds(VALUE=time)})
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(content=f"Added {channel.mention} in **Watchlist**!")

            elif channel_match is True and option.value == "remove":
                ServerData["AutoDelete"].pop(str(channel.id))
                self.database.save_data(server_id=interaction.guild.id, update_data=ServerData)
                await interaction.response.send_message(content=f"Removed {channel.mention} from **Watchlist**!")
            await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} executed {self.c.Yellow}/autodelete watchignore_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} channel: {channel.name} time: {time} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/autodelete watch ignore_channel{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} channel: {channel.name} time: {time} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoDeleteCommand())
