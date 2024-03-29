import discord, sys, os
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con


class Shutdown(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @commands.command(name="restart")
    async def shutdown(self, ctx: commands.Context) -> None:
        BotData: dict =  self.shared.db.load_data()
        if ctx.author.id in [x for x in BotData["owners"]]:
            await ctx.send(content="Closing connection with discord...")
            await self.bot.close()
            #os.system("shutdown /s /t 1")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shutdown(bot))
