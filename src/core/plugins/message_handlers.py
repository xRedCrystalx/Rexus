import sys, discord, typing, re
sys.dont_write_bytecode = True
import src.connector as con

if typing.TYPE_CHECKING:
    from discord.ext import commands

class MessageHandlers:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot

        self.invite_link_pattern: re.Pattern[str] = re.compile(pattern=r"https://discord\.gg/[a-zA-Z0-9]+")
        self.link_db: dict[str, discord.Invite] = {}
        self.names: list[str] = ["xnduiw", "clone", "alt", "criminalcode", "simon"]

    async def fan_art(self, message: discord.Message, guild_db: dict[str, typing.Any], **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        try:
            if guild_db["fan_art"]["status"]:
                if not isinstance(message.author, discord.User) and message.channel.id in guild_db["fan_art"]["monitored"]:
                    images: list[discord.Attachment] = [attachment for attachment in message.attachments if attachment.content_type.startswith("image/") or attachment.content_type.startswith("video/")]
                    if images:
                        return [{message : {"action" : "create_thread", "kwargs" : {"name" : f"Fan art by {message.author.display_name} ({message.author.global_name})"}}}, 
                                {message : {"action" : "add_reaction", "args" : ["❤️"]}}]
                    else:
                        return [{message : {"action" : "delete"}}]
                    

        except Exception as error:
            self.shared.logger.log(f"@MessageHandlers.fan_art: {type(error).__name__}: {error}", "ERROR")
        return None

    async def responder(self, message: discord.Message, guild_db: dict[str, typing.Any], **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        try:
            if guild_db["responder"]["status"]:
                for phrase, data in guild_db["responder"]["options"].items():
                    if data["startsWith"]:
                        if message.content.startswith(phrase):
                            return [{message.channel : {"action" : "send", "kwargs" : {"content" : data["content"]}}}]
                    else:
                        if phrase in message.content:
                            return [{message.channel : {"action" : "send", "kwargs" : {"content" : data["content"]}}}]

        except Exception as error:
            self.shared.logger.log(f"@MessageHandlers.responder: {type(error).__name__}: {error}", "ERROR")
        return None

    async def simon_invite_link_detection(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        try:
            message: discord.Message = message or after

            if links := self.invite_link_pattern.findall(string=message.content) and message.guild.id == 1175874833146450042:
                for link in links:
                    if link not in self.link_db.keys():
                        link_data: discord.Invite = await self.bot.fetch_invite(link)
                        self.link_db[link] = link_data

                    invite_object: discord.Invite = self.link_db[link]

                    if invite_object.guild.id == 1067152607459688549:
                        await message.author.ban(delete_message_days=7, reason="Autoban - XNDUIW")

                        embed: discord.Embed = discord.Embed(title="XNDUIW | CBE_Simon Protection", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
                        embed.set_thumbnail(url=message.author.display_avatar.url)
                        embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                        embed.add_field(name="`` Rule ``", value=f"Detected invite link redirecting to Simon's server.", inline=True)
                        embed.add_field(name="`` Message Content ``", value=message.content if len(message.content) < 1000 else message.content[:1000], inline=False)
                        embed.set_footer(text="Member has been banned from the guild.")

                        return [{message.guild.get_channel(1175874833146450042) : {"action" : "send", "kwargs" : {"embed" : embed}}}]

        except Exception as error:
            self.shared.logger.log(f"@MessageHandlers.simon_invite_link_detection: {type(error).__name__}: {error}", "ERROR")
        return None

    async def antilink(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        try:
            message: discord.Message = message or after
            if guild_db["link"]["status"] and (message.author.guild_permissions.administrator or guild_db["ServerInfo"]["StaffRole"] in [role.id for role in message.author.roles]): # not
                if "http://" in message.content or "https://" in message.content and (channel_id := guild_db["Logging"]["Link"]):

                    embed: discord.Embed=discord.Embed(title="Link Protection", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.add_field(name="`` Author ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                    embed.add_field(name="`` Message ``", value=f"<:msg_id:1203422168046768129>┇{message.author.id}\n<:text_c:1203423388320669716>┇{message.channel.name}\n<:ID:1203410054016139335>┇{message.channel.id}", inline=True)

                    if (msglen := len(message.content)) > 1000:
                        embed.add_field(name="`` Message ``", value=f"{message.content[:msglen-1000]}...", inline=False)
                    else:
                        embed.add_field(name="`` Message ``", value=f"{message.content if msglen != 0 else 'Could not find the message content.'}", inline=False)

                    if channel := message.guild.get_channel(channel_id):
                        return [{message.channel : {"action" : "send", "kwargs" : {"content" : f"{message.author.mention} do NOT send links!", "delete_after" : 5}}},
                                {message : {"action" : "delete"}},
                                {channel : {"action" : "send", "kwargs" : {"embed" : embed}}}]

        except Exception as error:
            self.shared.logger.log(f"@MessageHandlers.antilink: {type(error).__name__}: {error}", "ERROR")
        return None
