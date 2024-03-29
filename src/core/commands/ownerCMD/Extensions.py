import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class ExtensionsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.choices(option=[
        app_commands.Choice(name="Load", value="load"),
        app_commands.Choice(name="Reload", value="reload"),
        app_commands.Choice(name="Unload", value="unload"),
        ],
        path=[
        app_commands.Choice(name="Listeners", value="src.core.listeners."),
        app_commands.Choice(name="OwnerCMD", value="src.core.commands.ownerCMD."),
        app_commands.Choice(name="AdminCMD", value="src.core.commands.adminCMD."),
        app_commands.Choice(name="StaffCMD", value="src.core.commands.staffCMD."),
        app_commands.Choice(name="MemberCMD", value="src.core.commands.memberCMD.")
        ])
    @app_commands.command(name = "extensions", description = "Owner only command. No touchy!")
    async def extensions(self, interaction: discord.Interaction, option: app_commands.Choice[str], path: str, name: str) -> None:
        BotData: dict = self.shared.db.load_data()
        async def extensions_handler(execution) -> None:
            try:
                await execution(path+name)
                embed = discord.Embed(title=f'{option.name}', description=f'{path+name} successfully {option.value}ed.', color=0xff0000)
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                embed = discord.Embed(title=f'{option.name}', description=f'{path+name} failed to {option.value}\n{str(e)}.', color=0xff0000)
                await interaction.response.send_message(embed=embed)
            self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} executed {self.c.Yellow}/extensions{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} fullpath: {path+name} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

        if interaction.user.id in [x for x in BotData["owners"]]:
            if option.value == "reload":
                await extensions_handler(self.bot.reload_extension)
            elif option.value == "load":
                await extensions_handler(self.bot.load_extension)
            elif option.value == "unload":
                await extensions_handler(self.bot.unload_extension)
        else: 
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/extensions{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: option: {option.name} path: {path} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExtensionsCommand(bot))
