import sys
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class CommandListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            # ignore Unknown commands errors - i dont need console spam
            pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommandListeners(bot))