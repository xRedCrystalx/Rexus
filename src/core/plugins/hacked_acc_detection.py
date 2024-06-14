import sys, discord, typing
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.event import Event

class HackedAccounts:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot =  self.shared.bot
        self.hacked_types: dict[str, list[str]] = {
            "porn": ["18+", "teen", "girls", "free", "leaks", "onlyfans", "nude", "hot", "pussy", "porn", "nsfw", "sex", "video", "photo", "content", ":underage:", ":peach:", ":heart:", ":sweat_drops:", ":egg_plant:", ":hot_face:", ":lips:"],
            #"acc": ["gift card", "money", "[steamcommunity.com/gift"]
        }

    async def check_hacked(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], action: discord.Message = None, message: discord.Message = None, **OVERFLOW) -> None:
        action = action or message
        
        # temp. replacing with permissions when making it public
        if action.guild.id == 626159471386689546:
            member: discord.Member | None = getattr(action, "member", None) or getattr(action, "author", None)

            for check in self.hacked_types:
                matches: list[str] = len([item for item in self.hacked_types[check] if item in action.content])
                
                if not matches:
                    return
                
                elif matches > 4:
                    embed: discord.Embed = apply_embed_items(
                        embed=create_base_embed("Hacked Accounts Protection"),
                        thumbnail=member.display_avatar.url,
                        footer="Member has been kicked from the server.")
                    embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{member.display_name}\n<:global:1203410626492240023>┇{member.global_name}\n<:ID:1203410054016139335>┇{member.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"Detected patterns of hacked account behaviour.")

                    self.shared.sender.resolver([
                        Event(member, "kick", event_data={"kwargs": {"reason": "Hacked account"}}),
                        Event(self.bot.get_channel(711311257570902109), "send", event_data={"kwargs": {"embed": embed}})
                    ])
                    return
