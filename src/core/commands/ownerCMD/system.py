import discord, sys, typing, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from xRedUtils.iterables import get_attr_data
from src.core.helpers.embeds import new_embed, create_base_embed

class TempCMD(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @discord.app_commands.choices(cmd=[
        discord.app_commands.Choice(name="plugins", value="p"),
        discord.app_commands.Choice(name="filter", value="f"),
        discord.app_commands.Choice(name="tasks", value="t"),
        discord.app_commands.Choice(name="system", value="s"),
    ])
    @discord.app_commands.command(name="plugins", description="Displays currently running plugins information.")
    async def plugins(self, interaction: discord.Interaction, cmd: discord.app_commands.Choice[str]) -> None:
        if cmd.value == "p":
            await interaction.response.send_message(
                "\n".join([f"**{plugin.__class__.__name__}**: `Location - {location}`" for location, plugin in shared.plugins.items()]),
                ephemeral=True
            )
        elif cmd.value == "f":
            await interaction.response.send_message(
                "\n".join([f"**{event}**: `{get_attr_data(funcs, "__qualname__")}`" for event, funcs in shared.plugin_filter.items()]),
                ephemeral=True
            )
        elif cmd.value == "t":
            await interaction.response.send_message(
                "\n".join([f"**Task {i}:** `{asyncio.coroutines._format_coroutine(task.get_coro())}`" for i, task in enumerate(shared.plugin_tasks, 1)]),
                ephemeral=True
            )
        elif cmd.value == "s":
            await interaction.response.send_message(
                "\n".join([f"**{sys_module.__class__.__qualname__ if sys_module else ""}**: `{sys_module}`" for sys_module in [shared.db, shared.logger, shared.reloader, shared.queue, shared.session, shared.bot, shared.loop]]),
                ephemeral=True
            )
    
    @discord.app_commands.command(name="check_guilds", description="Checks and displays which guilds haven't set up the bot.")
    async def configurated(self, interaction: discord.Interaction) -> None:
        required_settings: list[str] = ["staffRole", "staffChannel", "adminRole", "adminChannel"]
        yes, no = (0, 0)

        for guild in self.bot.guilds:
            database: dict[str, dict[str, bool | int]] = shared.db.load_data(guild.id)
            if all([database["general"][conf] for conf in required_settings]):
                yes += 1
            else:
                no += 1

        embed: discord.Embed = create_base_embed("Server configuration statistics", description=f"**Configured:** `{yes}` • **Not configured:** `{no}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(TempCMD(bot), guild=discord.Object(id=1230040815116484678))
