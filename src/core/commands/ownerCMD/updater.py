import discord, sys, typing, subprocess
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class Updater(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.choices(cmd=[
        app_commands.Choice(name="fetch_from_github", value="fetch"),
        app_commands.Choice(name="reload", value="reload")
        ]
    )
    @app_commands.command(name="updater", description="Owner commands, no touchy!")
    async def owner(self, interaction: discord.Interaction, cmd: app_commands.Choice[str], args: str = None) -> None:
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

        await interaction.response.defer(thinking=True, ephemeral=True)

        if interaction.user.id in bot_config.get("owners", []):
            if cmd.value == "fetch":
                process: subprocess.CompletedProcess[bytes] = subprocess.run(["git", "pull", "noping", "v3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                await interaction.followup.send(content="Fetched latest version from github.")
            elif cmd.value == "reload":
                if bot_config["reloader"].get(args):
                    self.shared.reloader.reload_module(args)
                    await interaction.followup.send(content=f"Reloaded {args}.")
                else:
                    await interaction.followup.send(content=f"Could not find the config info of {args} in configuration.")
        else:
            await interaction.followup.send("You do not have permissions to execute this command.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Updater(bot), guild=discord.Object(id=1230040815116484678))
