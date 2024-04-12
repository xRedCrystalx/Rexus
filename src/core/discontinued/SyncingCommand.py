import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class SyncCommandOwner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @commands.command(name="sync")
    async def sync_Command(self, ctx: commands.Context) -> None:
        BotData: dict = self.shared.db.load_data()
        if ctx.author.id in [x for x in BotData["owners"]]:
            try:
                await self.bot.tree.sync(guild=discord.Object(id=int(ctx.message.content[6:])))
                await ctx.send(content = f"Synced this group.") 
            except:
                await self.bot.tree.sync()
                await ctx.send(content = f"Synced Globally")          

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCommandOwner(bot))
