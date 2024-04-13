import sys, discord, typing
sys.dont_write_bytecode = True
import src.connector as con

from discord.ext import commands
from discord import app_commands

class TestView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        
    def create_selector(self) -> typing.Self:
        self.add_item(discord.ui.Select(options=[discord.SelectOption(label="Test 1", value=True), discord.SelectOption(label="Test 2", value="test2"), discord.SelectOption(label="Test 3", value="test3")], custom_id="THIS IS CUSTOM ID", min_values=2, max_values=2))
        return self
    
    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        await interaction.response.send_message(f"{dict(interaction.data)}")

class TestCMD(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.command(name="test_cmd", description="Bot's configuration command!")
    async def test(self, interaction: discord.Interaction) -> None:
        bot_db: dict[str, dict] = self.shared.db.load_data()
        guild_db: dict[str, dict] = self.shared.db.load_data(interaction.guild.id)

        await interaction.response.send_message(content="Test message", view=TestView().create_selector())

    @app_commands.choices(option=[
        app_commands.Choice(name="Ping", value="ping"),
        app_commands.Choice(name="Test", value="test")
    ])
    @app_commands.command(name="option_test")
    async def option_test(self, interaction: discord.Interaction, option: app_commands.Choice[str], args: str = None) -> None:
        await interaction.response.send_message(f"{option}\n{args}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TestCMD(bot))
