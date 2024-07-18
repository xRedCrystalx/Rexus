import sys, discord, re
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from src.core.helpers.permissions import check_ids
from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtilsAsync.regexes import URL_PATTERN
from xRedUtilsAsync.type_hints import SIMPLE_ANY

class AntiLink:
    def __init__(self) -> None:
        self.social_media_domains: list[str] = [
            "youtube.com", "youtu.be", "facebook.com", "instagram.com", "twitter.com", "linkedin.com", "snapchat.com", "pinterest.com",
            "reddit.com", "tiktok.com", "whatsapp.com", "skype.com", "telegram.org", "quora.com", "twitch.tv","soundcloud.com", "imgur.com", 
            "netflix.com", "disneyplus.com", "spotify.com", "myspace.com", "flickr.com", "roblox.com", "garticphone.com"
        ]
        self.links: dict[str, re.Pattern[str]] = {
            "allowDiscordInvites": shared.global_db["invite_links"]["regex"],
            "allowNitroGifts": re.compile(r"https?://(?:www\.)?discord\.gift/[a-zA-Z0-9]+"),
            "allowSocialLinks": re.compile(rf"https?://(?:www\.)?(?:{'|'.join(re.escape(domain) for domain in self.social_media_domains)})/[a-zA-Z0-9]+")
        }

    async def antilink(self, guild_db: dict[str, SIMPLE_ANY], message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> None:
        message: discord.Message = message or after
        #                                      fix this with the right permissions (ignored roles)
        if guild_db["link"]["status"] and not (message.author.bot or message.author.guild_permissions.administrator):

            if await check_ids([guild_db["general"]["staffRole"], guild_db["general"]["adminRole"]],  message.author.roles):
                return
                
            if (links := URL_PATTERN.findall(message.clean_content)):
                pattern_list: list[re.Pattern] = [pattern for setting, pattern in self.links.items() if guild_db["link"]["options"][setting]]
                if all([any([re.match(pattern, link) for pattern in pattern_list]) for link in links]):
                    return
                
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed("Link Protection"),
                    thumbnail=message.author.display_avatar.url)
                embed.add_field(name="`` Author ``", value=f"{CEmoji.PROFILE}┇{message.author.display_name}\n{CEmoji.PROFILE}┇{message.author.name}\n{CEmoji.ID}┇{message.author.id}", inline=True)
                embed.add_field(name="`` Location ``", value=f"{CEmoji.MSG_ID}┇{message.id}\n{CEmoji.TEXT_C}┇{message.channel.mention}\n{CEmoji.ID}┇{message.channel.id}", inline=True)
                embed.add_field(name="`` Message ``", value=message.content if len(message.content) < 1000 else f"{message.content[:1000]}...", inline=False)

                await message.channel.send(f"{message.author.mention} do NOT send links!", delete_after=5)
                await message.delete()

                if channel := message.guild.get_channel(guild_db["link"]["log_channel"]):
                    await channel.send(embed=embed)

        return None
    
async def setup(bot: commands.AutoShardedBot) -> None:
    await shared.add_plugin(AntiLink, 
        config={
            ["on_message"]: AntiLink.antilink # support for on_raw_message_update
        }
    )
