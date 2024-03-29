import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class LvlCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors
        self.switch: bool = True

    @commands.hybrid_command(name="top", description="Displays top 10 members for each enabled lvl type.")
    async def top(self, ctx: commands.Context) -> None:
        member: discord.Member = ctx.author
        ServerData: dict =  self.shared.db.load_data(ctx.guild.id)
        
        if not ServerData["Plugins"]["LevelingSystem"]:
            await ctx.send("Levelling system is not enabled.")
            return
        
        ranks: dict[str, dict[str, int]] = {}
        [ranks.update(await self.CONNECTOR.callable(fun="get_members_lvl_ranks", members_db=ServerData["LevelingSystem"]["members"], type=x)) for x in ["message", "reaction", "voice", "GLOBAL"]]

        embed: discord.Embed=discord.Embed(color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
        embed.set_author(name=f"{member.display_name} | Top users", icon_url=member.display_avatar.url)
        embed.set_footer(text=f"Member ID: {member.id}")
        if ServerData["LevelingSystem"]["config"]["type"] == "multi":
            for lvlName, switch in ServerData["LevelingSystem"]["config"]["levels"].items():
                if switch:
                    embed.add_field(name=f"`` {str(lvlName).capitalize()} ``", value=f"\n".join([f"**{i+1}.**  {list(ranks[lvlName].keys())[i] if (user := ctx.guild.get_member(int(list(ranks[lvlName].keys())[i]))) is None else user.display_name if user.id != member.id else f'**{user.display_name}**'}" for i in range(len(list(ranks[lvlName].keys())) if len(list(ranks[lvlName].keys())) < 10 else 10)]) + f"\n\n**You:** `{ranks[lvlName].get(str(member.id))}`", inline=True)
        else:
            embed.add_field(name=f"`` Server Top ``", value=f"\n".join([f"**{i+1}.**  {list(ranks['GLOBAL'].keys())[i] if (user := ctx.guild.get_member(int(list(ranks['GLOBAL'].keys())[i]))) is None else user.display_name if user.id != member.id else f'**{user.display_name}**'}" for i in range(len(list(ranks['GLOBAL'].keys())) if len(list(ranks['GLOBAL'].keys())) < 10 else 10)]) + f"\n\n**You:** `{ranks['GLOBAL'].get(str(member.id))}`", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rank", description="Displays your current rank for each lvl and other info.")
    async def rank(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: 
            member: discord.Member = ctx.author
            
        ServerData: dict =  self.shared.db.load_data(ctx.guild.id)

        if not ServerData["Plugins"]["LevelingSystem"]:
            await ctx.send("Levelling system is not enabled.")
            return
        
        if not ServerData["LevelingSystem"]["members"].get(str(member.id)):
            await ctx.send("Make sure to chat! Try again in 1 minute.")
            return

        memberDB: dict[str, dict[str, int]] = ServerData["LevelingSystem"]["members"][str(member.id)]
        ranks: dict[str, dict[str, int]] = {}
        [ranks.update(await self.CONNECTOR.callable(fun="get_members_lvl_ranks", members_db=ServerData["LevelingSystem"]["members"], type=x)) for x in ["message", "reaction", "voice", "GLOBAL"]]

        embed: discord.Embed=discord.Embed(color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
        embed.set_author(name=f"{member.display_name} | Rank", icon_url=member.display_avatar.url)
        embed.set_footer(text=f"Member ID: {member.id}")

        if ServerData["LevelingSystem"]["config"]["type"] == "multi":
            for lvlName, switch in ServerData["LevelingSystem"]["config"]["levels"].items():
                if switch:
                    embed.add_field(name=f"`` {str(lvlName).capitalize()} ``", value=f"**Rank:** `{ranks[lvlName].get(str(member.id))}`\n**Level:** `{memberDB['levels'].get(lvlName)}`\n\n**XP:** `{memberDB[lvlName].get('global_xp'):,} xp`\n**Next level:**\n`{await self.CONNECTOR.callable(fun='completion_bar', completed=memberDB[lvlName].get('xp'), total=await self.CONNECTOR.callable(fun='calc_xp', level=memberDB['levels'].get(lvlName)+1))}`", inline=True)        
        else:
            embed.add_field(name=f"`` Server Rank ``", value=f"**Rank:** `{ranks['GLOBAL'].get(str(member.id))}`\n**Level:** `{memberDB['levels'].get('GLOBAL')}`\n\n**XP:** `{memberDB['GLOBAL'].get('global_xp'):,} xp`\n**Next level:**\n`{await self.CONNECTOR.callable(fun='completion_bar', completed=memberDB['GLOBAL'].get('xp'), total=await self.CONNECTOR.callable(fun='calc_xp', level=memberDB['levels'].get('GLOBAL')+1))}`", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="lvlrewards", description="Shows rewards for lvl ups.")
    async def lvlrewards(self, ctx: commands.Context) -> None:
        ServerData: dict =  self.shared.db.load_data(ctx.guild.id)
        member: discord.User | discord.Member = ctx.author
        
        if not ServerData["Plugins"]["LevelingSystem"]:
            await ctx.send("Levelling system is not enabled.")
            return

        embed: discord.Embed=discord.Embed(color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
        embed.set_author(name=f"{member.display_name} | Level Rewards", icon_url=member.display_avatar.url)
        embed.set_footer(text=f"Guild ID: {member.guild.id}")

        for lvlName, switch in ServerData["LevelingSystem"]["config"]["levels"].items():
            if switch:
                embed.add_field(name=f"`` {str(lvlName).capitalize()} ``", value=f"\n".join([f"{level}.  <@&{role}>" for level, role in ServerData["LevelingSystem"]["config"]["rewards"][lvlName].items()] if ServerData["LevelingSystem"]["config"]["rewards"][lvlName] != {} else ["No rewards found for this level type."]), inline=True)        
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LvlCommands(bot))
