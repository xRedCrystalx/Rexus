import sys, discord, typing, re
sys.dont_write_bytecode = True
import src.connector as con
from xRedUtils.dates import get_datetime

if typing.TYPE_CHECKING:
    from discord.ext import commands

class MessageHandlers:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot

        self.URL_pattern: re.Pattern[str] =  re.compile(r"\bhttps?://\S+\b")
        self.social_media_domains: list[str] = ["youtube.com", "youtu.be", "facebook.com", "instagram.com", "twitter.com", "linkedin.com", "snapchat.com", "pinterest.com",
                                                "reddit.com", "tiktok.com", "whatsapp.com", "skype.com", "telegram.org", "quora.com", "twitch.tv","soundcloud.com", "imgur.com", 
                                                "netflix.com", "disneyplus.com", "spotify.com", "myspace.com", "flickr.com", "roblox.com", "garticphone.com"]

        self.social_medias_pattern: re.Pattern[str] = re.compile(rf"https?://(?:www\.)?(?:{'|'.join(re.escape(domain) for domain in self.social_media_domains)})/[a-zA-Z0-9]+")
        self.invite_link_pattern: re.Pattern[str] = re.compile(r"\b(?:https?://)?(?:www\.)?(?:discord\.(?:gg|com/invite)|discordapp\.com/invite)/[a-zA-Z0-9]+(?:\?[^\s&]+)?\b")
        self.nitro_gift_pattern: re.Pattern[str] = re.compile(r"https?://(?:www\.)?discord\.gift/[a-zA-Z0-9]+")
        
        self.link_db: dict[str, discord.Invite] = {}

    async def responder(self, message: discord.Message, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if guild_db["responder"]["status"]:
            events: list[con.Event] = []
            for phrase, data in guild_db["responder"]["responses"].items():
                if data["startsWith"]:
                    if message.content.startswith(phrase):
                        events.append(con.Event(message.channel, "send", event_data={"kwargs": {"content": data["content"]}}))
                else:
                    if phrase in message.content:
                        events.append(con.Event(message.channel, "send", event_data={"kwargs": {"content": data["content"]}}))

            self.shared.sender.resolver(events)
        return None

    async def simon_invite_link_detection(self, message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> None:
        message: discord.Message = message or after

        if (guilds := await self.shared.fetch_invite_links(message.content, option="simon")) and message.guild.id == 1175874833146450042:
            for guild_id in guilds:
                if guild_id == 1067152607459688549:
                    embed: discord.Embed = discord.Embed(title="XNDUIW | CBE_Simon Protection", color=discord.Colour.dark_embed(), timestamp=get_datetime())
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"Detected invite link redirecting to Simon's server.", inline=True)
                    embed.add_field(name="`` Message Content ``", value=message.content if len(message.content) < 1000 else message.content[:1000], inline=False)
                    embed.set_footer(text="Member has been banned from the guild.")

                    self.shared.sender.resolver([
                        con.Event(message.author, "ban", event_data={"kwargs": {"delete_message_days": 7, "reason": "Autoban - XNDUIW"}}),
                        con.Event(message.guild.get_channel(1175874833146450042), "send", event_data={"kwargs": {"embed" : embed}})
                    ])

    async def antilink(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> None:
        message: discord.Message = message or after

        if guild_db["link"]["status"] and not (isinstance(message.author, discord.User) or message.author.guild_permissions.administrator ):
            roles: list[int] = [role.id for role in message.author.roles]
            if not (guild_db["general"]["staffRole"] in roles or guild_db["general"]["adminRole"] in roles):
                if (links := self.URL_pattern.findall(message.clean_content)) and (channel_id := guild_db["link"]["log_channel"]):
                    options: dict[str, bool] = guild_db["link"]["options"]
                    pattern_list: list[re.Pattern] = [pattern 
                                                    for setting, pattern in 
                                                    zip(["allowDiscordInvites", "allowNitroGifts", "allowSocialLinks"], [self.invite_link_pattern, self.nitro_gift_pattern, self.social_medias_pattern]) 
                                                    if options[setting]]

                    if all([any([re.match(pattern, link) for pattern in pattern_list]) for link in links]):
                        return

                    embed: discord.Embed=discord.Embed(title="Link Protection", color=discord.Colour.dark_embed(), timestamp=get_datetime())
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.add_field(name="`` Author ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                    embed.add_field(name="`` Message ``", value=f"<:msg_id:1203422168046768129>┇{message.author.id}\n<:text_c:1203423388320669716>┇{message.channel.name}\n<:ID:1203410054016139335>┇{message.channel.id}", inline=True)

                    if (msglen := len(message.content)) > 1000:
                        embed.add_field(name="`` Message ``", value=f"{message.content[:msglen-1000]}...", inline=False)
                    else:
                        embed.add_field(name="`` Message ``", value=f"{message.content if msglen != 0 else 'Could not find the message content.'}", inline=False)

                    self.shared.sender.resolver([con.Event(message.channel, "send", event_data={"kwargs": {"content" : f"{message.author.mention} do NOT send links!", "delete_after": 5}}),
                                                con.Event(message, "delete", {})])

                    if channel := message.guild.get_channel(channel_id):
                        self.shared.sender.resolver(con.Event(channel, "send", event_data={"kwargs": {"embed": embed}}))
