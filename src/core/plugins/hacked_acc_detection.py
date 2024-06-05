import sys, discord, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

from xRedUtils.dates import get_datetime

class HackedAccounts:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot =  self.shared.bot
        self.hacked_types: dict[str, list[str]] = {
            "porn": ["18+", "teen", "girls", "free", "leaks", "onlyfans", "nude", "hot", "pussy", "porn", "nsfw", "sex", "video", "photo", "content", ":underage:", ":peach:", ":heart:", ":sweat_drops:", ":egg_plant:", ":hot_face:", ":lips:"],
            #"acc": ["gift card", "money", "[steamcommunity.com/gift"]
        }
        self.bad_guilds: dict[int, int] = {}

    async def kick(self, member: discord.Member, kick: bool) -> None:
        if not member: return

        if kick:
            self.shared.sender.resolver(con.Event(member, "kick", event_data={"reason": "Hacked account"}))

        embed: discord.Embed = discord.Embed(title="Hacked Accounts Detection", timestamp=get_datetime(), color=discord.Colour.dark_embed())
        embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{member.display_name}\n<:global:1203410626492240023>┇{member.global_name}\n<:ID:1203410054016139335>┇{member.id}", inline=True)
        embed.add_field(name="``` Rule ``", value=f"Detected patterns of hacked account behaviour.")
        embed.set_footer(text="Member has been kicked from the server." if member else "Suspicious member. Please check their messages.")

        self.shared.sender.resolver(con.Event(self.bot.get_channel(711311257570902109), "send", event_data={"embed": embed}))

    async def check_hacked(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], action: discord.Message = None, message: discord.Message = None, **OVERFLOW) -> None:
        action = action or message
        # temp. replacing with permissions when making it public
        if action.guild.id == 626159471386689546:
            if (invites := self.shared.fetch_invite_links(action.content, option="scam_guilds")):
                member: discord.Member | None = getattr(action, "member", None) or getattr(action, "author", None)

                for guild_id in invites:
                    if guild_id in bot_db["filters"]["hacked_accs_detection"]["bad_guilds"]:
                        return await self.kick(member, kick=True)
                    else:
                        if not self.bad_guilds.get(guild_id):
                            self.bad_guilds[guild_id] = 0

                        self.bad_guilds[guild_id] += 1

                        if self.bad_guilds[guild_id] >= 5:
                            self.bad_guilds.pop(guild_id)
                            bot_db["filters"]["hacked_accs_detection"]["bad_guilds"].append(guild_id)
                            self.shared.db.save_data(None, bot_db)

                for check in self.hacked_types:
                    matches: list[str] = [item for item in self.hacked_types[check] if item in action.content]
                    
                    if len(matches) > 2 and len(matches) <= 4:
                        await self.kick(member, kick=False) 
                    else:
                        return await self.kick(member, kick=True)

# NOTE: Possible memory leak for self.bad_guilds
