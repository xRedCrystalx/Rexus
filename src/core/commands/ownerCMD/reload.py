import discord, sys, os, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class Reload(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    @commands.command(name="reload")
    async def reload(self, ctx: commands.Context, module: str) -> None:
        BotData: dict =  self.shared.db.load_data()
        if ctx.author.id in [x for x in BotData["owners"]]:
            msg: discord.Message = await ctx.send(content="Updating systems..")
            self.shared.reloader.reload_module(module)
            await msg.edit(content="Successfully updated system.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reload(bot))
