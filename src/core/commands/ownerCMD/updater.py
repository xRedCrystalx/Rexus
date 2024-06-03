import discord, sys, typing, subprocess
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con

from xRedUtils.strings import string_split

class Updater(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.choices(cmd=[
        app_commands.Choice(name="fetch_from_github", value="fetch"),
        app_commands.Choice(name="reload", value="reload"),
        app_commands.Choice(name="full_reload", value="full")
        ]
    )
    @app_commands.command(name="updater", description="Owner commands, no touchy!")
    async def owner(self, interaction: discord.Interaction, cmd: app_commands.Choice[str], args: str = None) -> None:
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

        await interaction.response.defer(thinking=True, ephemeral=True)

        if interaction.user.id in bot_config.get("owners", []):
            if cmd.value == "fetch":
                result: subprocess.CompletedProcess[str] = subprocess.run(["git", "pull", "noping", "v3"], capture_output=True, text=True)
                await interaction.followup.send(content="Fetched latest version from github.")
                
                for chunk in string_split(result.stdout, chunk_size=1994, option="smart"):
                    await interaction.followup.send(content=f"```{chunk}```")

            elif cmd.value == "reload":
                if bot_config["reloader"].get(args):
                    self.shared.reloader.reload_module(args)
                    await interaction.followup.send(content=f"Reloaded {args}.")
                else:
                    self.shared.reloader.reload_discord_module(args)
                    await interaction.followup.send(content=f"Reloaded discord module on path: {args}")
            
            elif cmd.value == "full":
                for module in bot_config["reloader"]:
                    self.shared.reloader.reload_module(module)

                for dc_module in self.bot.cogs:
                    await self.shared.reloader.reload_discord_module(dc_module)

            elif cmd.value == "requirements":
                result: subprocess.CompletedProcess[str] = subprocess.run(["pip", "install", "-r", "./requirements.txt"], capture_output=True, text=True)
                await interaction.followup.send(content="Updating requirements..")
                
                for chunk in string_split(result.stdout, chunk_size=1994, option="smart"):
                    await interaction.followup.send(content=f"```{chunk}```")

                #TODO: reload all modules from requirements.txt
            
        else:
            await interaction.followup.send("You do not have permissions to execute this command.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:

    await bot.add_cog(Updater(bot), guild=discord.Object(id=1230040815116484678))
