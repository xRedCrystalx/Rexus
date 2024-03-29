import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con


class SayCommandOwner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @commands.command(name="say")
    async def SayCommand(self, ctx: commands.Context, *args) -> None:
        BotData: dict = self.shared.db.load_data()
        if ctx.author.id in [x for x in BotData["owners"]]:
            await ctx.message.delete()
            channel = args[0]
            if isinstance(int(channel), int) == True:
                data: str = " ".join(args[1:])
                try:
                    send_channel: discord.TextChannel = discord.utils.get(ctx.guild.channels, id = int(channel))
                    await send_channel.send(content = data)
                except:
                    await ctx.send(content = f"Invalid channel ID or no permissions.")
            else:
                await ctx.send(content = f"Please input channel ID. `r!say [channelID] [text]`")              
                    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SayCommandOwner(bot))
