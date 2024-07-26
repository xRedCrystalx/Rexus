import sys, discord
sys.dont_write_bytecode = True
from src.connector import shared

from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtils.type_hints import SIMPLE_ANY

class HackedAccounts:
    def __init__(self) -> None:
        self.hacked_types: dict[str, list[str]] = {
            "porn": ["18+", "teen", "girls", "free", "leaks", "onlyfans", "nude", "hot", "pussy", "porn", "nsfw", "sex", "video", "photo", "content", ":underage:", ":peach:", ":heart:", ":sweat_drops:", ":egg_plant:", ":hot_face:", ":lips:"],
            #"acc": ["gift card", "money", "[steamcommunity.com/gift"]
        }

    async def check_hacked(self, guild_db: dict[str, SIMPLE_ANY], bot_db: dict[str, SIMPLE_ANY], action: discord.AutoModAction = None, message: discord.Message = None, **OVERFLOW) -> None:
        action: discord.Message | discord.AutoModAction = action or message

        action_guild: discord.Guild = getattr(action, "guild", None)
        action_member: discord.Member = getattr(action, "member", None) or getattr(action, "author", None)
        action_content: str = getattr(action, "content", None)

        if not (action_guild and action_member and action_content) or action_member.bot:
            return

        # temp. replacing with permissions when making it public
        if action_guild.id == 626159471386689546:
            action_content = action_content.lower()

            for check in self.hacked_types.keys():
                matches: list[str] = [item for item in self.hacked_types[check] if item in action_content]
                
                if len(matches) > 4:
                    await shared.logger.log( "TESTING", f"Match found! {matches} - {action_member.display_name} ({action_member.id})")
                    
                    embed: discord.Embed = apply_embed_items(
                        embed=create_base_embed("Hacked Accounts Protection"),
                        thumbnail=action_member.display_avatar.url,
                        footer="Member has been kicked from the server.")
                    embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{action_member.display_name}\n{CEmoji.GLOBAL}┇{action_member.name}\n{CEmoji.ID}┇{action_member.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"Detected patterns of hacked account behaviour.")

                    await action_guild.get_channel(711311257570902109).send(embed=embed)
                    await action_member.kick(reason="Hacked account")

async def setup(bot) -> None:
    await shared.reloader.load(hacked := HackedAccounts(), 
        config={
            hacked.check_hacked: ["on_message", "on_automod_action"]
        }
    )
