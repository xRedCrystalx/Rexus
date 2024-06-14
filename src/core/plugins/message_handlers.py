import sys, discord, typing, re
sys.dont_write_bytecode = True
import src.connector as con

from src.core.helpers.permissions import check_ids
from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.other import fetch_invite_links
from src.core.helpers.event import Event

from xRedUtils.regexes import URL_PATTERN

class MessageHandlers:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

        self.social_media_domains: list[str] = ["youtube.com", "youtu.be", "facebook.com", "instagram.com", "twitter.com", "linkedin.com", "snapchat.com", "pinterest.com",
                                                "reddit.com", "tiktok.com", "whatsapp.com", "skype.com", "telegram.org", "quora.com", "twitch.tv","soundcloud.com", "imgur.com", 
                                                "netflix.com", "disneyplus.com", "spotify.com", "myspace.com", "flickr.com", "roblox.com", "garticphone.com"]

        self.links: dict[str, re.Pattern[str]] = {
            "allowDiscordInvites": self.shared.global_db["invite_links"]["regex"],
            "allowNitroGifts": re.compile(r"https?://(?:www\.)?discord\.gift/[a-zA-Z0-9]+"),
            "allowSocialLinks": re.compile(rf"https?://(?:www\.)?(?:{'|'.join(re.escape(domain) for domain in self.social_media_domains)})/[a-zA-Z0-9]+")
        }

    async def responder(self, message: discord.Message, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if guild_db["responder"]["status"]:
            # check every phrase in the db
            for phrase, data in guild_db["responder"]["responses"].items():
                if data["startsWith"]:
                    if message.content.startswith(phrase):
                        self.shared.sender.resolver(Event(message.channel, "send", event_data={"kwargs": {"content": data["content"]}}))
                else:
                    if phrase in message.content:
                        self.shared.sender.resolver(Event(message.channel, "send", event_data={"kwargs": {"content": data["content"]}}))
        return None

    async def simon_invite_link_detection(self, message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> None:
        message: discord.Message = message or after

        if (guilds := await fetch_invite_links(message.content)) and message.guild.id == 1175874833146450042:
            for guild_id in guilds:
                # id of simons's main discord server
                if guild_id == 1067152607459688549:
                    embed: discord.Embed = apply_embed_items(
                        embed=create_base_embed(title="XNDUIW | CBE_Simon Protection"),
                        thumbnail=message.author.display_avatar.url,
                        footer="Member has been banned from the guild.")
                    embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"Detected invite link redirecting to Simon's server.", inline=True)
                    embed.add_field(name="`` Message Content ``", value=message.content if len(message.content) < 1000 else message.content[:1000], inline=False)

                    self.shared.sender.resolver([
                        Event(message.author, "ban", event_data={"kwargs": {"delete_message_days": 7, "reason": "Autoban - XNDUIW"}}),
                        Event(message.guild.get_channel(1175874833146450042), "send", event_data={"kwargs": {"embed" : embed}})
                    ])
        return None

    async def antilink(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> None:
        message: discord.Message = message or after

        if guild_db["link"]["status"] and not (isinstance(message.author, discord.User) or message.author.guild_permissions.administrator):

            if check_ids([guild_db["general"]["staffRole"], guild_db["general"]["adminRole"]],  message.author.roles):
                return
                
            if (links := URL_PATTERN.findall(message.clean_content)):

                pattern_list: list[re.Pattern] = [pattern for setting, pattern in self.links.items() if guild_db["link"]["options"][setting]]
                if all([any([re.match(pattern, link) for pattern in pattern_list]) for link in links]):
                    return
                
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed("Link Protection"),
                    thumbnail=message.author.display_avatar.url)
                embed.add_field(name="`` Author ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                embed.add_field(name="`` Location ``", value=f"<:msg_id:1203422168046768129>┇{message.author.id}\n<:text_c:1203423388320669716>┇{message.channel.name}\n<:ID:1203410054016139335>┇{message.channel.id}", inline=True)
                embed.add_field(name="`` Message ``", value="Could not find the message content." if len(message.content) == 0 else message.content if len(message.content) < 1000 else f"{message.content[:1000]}...", inline=False)

                self.shared.sender.resolver([Event(message.channel, "send", event_data={"kwargs": {"content" : f"{message.author.mention} do NOT send links!", "delete_after": 5}}),
                                            Event(message, "delete", {})])

                if channel := message.guild.get_channel(guild_db["link"]["log_channel"]):
                    self.shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"embed": embed}}))
        return None