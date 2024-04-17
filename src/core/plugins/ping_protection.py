import discord, sys, typing
sys.dont_write_bytecode = True
import src.connector as con


class PingProtection:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    def handle_options(self, guild_db: dict[str, typing.Any], embed: discord.Embed, module: str, message: discord.Message) -> None:
        self.shared.sender.resolver([{message.channel : {"action" : "send", "kwargs" : {"embed" : embed, "delete_after" : 15 if module in ["StaffProtection", "Bot", "MemberProtection"] else None}}}]) 

        if guild_db["ping"][module]["ping"] and (role_id := guild_db["ServerInfo"]["StaffRole"]):
            self.shared.sender.resolver({message.channel : {"action" : "send", "kwargs" : {"content" : f"Calling staff: <@&{role_id}>"}}})

        if guild_db["ping"][module]["log"] and (channel_id := guild_db["PingProtection"][module]["LogChannel"]):
            channel: discord.TextChannel = message.guild.get_channel(channel_id)

            embed: discord.Embed = discord.Embed(title="Ping Protection", timestamp=self.shared.time.datetime())
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.add_field(name="`` Author ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
            embed.add_field(name="`` Location ``", value=f"<:msg_id:1203422168046768129>┇{message.id}\n<:text_c:1203423388320669716>┇{message.channel.name}\n<:ID:1203410054016139335>┇{message.channel.id}", inline=True)
            if (msglen := len(message.content)) > 1000:
                embed.add_field(name="`` Message ``", value=f"{message.content[:msglen-1000]}...", inline=False)
            else:
                embed.add_field(name="`` Message ``", value=message.content if msglen != 0 else "Could not find the message content.", inline=False)

            if channel:
                self.shared.sender.resolver({channel : {"action" : "send", "kwargs" : {"embed" : embed}}})

        if guild_db["ping"][module]["delete"]:
            self.shared.sender.resolver({message : {"action" : "delete"}})


    async def find_pings(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None,  **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        message: discord.Message = message or after
        
        if guild_db["ping"]["status"] and message.channel.id not in guild_db["ping"]["ignoreChannels"]:
            if not message.author.bot and guild_db["ping"]["bypassRole"] not in [role.id for role in message.author.roles]:
                
                #creates list of mentions
                pingedMembers: list[discord.Member | discord.User] = message.mentions if guild_db["ping"]["detectReplyPings"] else [message.guild.get_member(user_id) for user_id in message.raw_mentions]
                role: int = guild_db["general"]["staffRole"]

                if message.mention_everyone:
                    embed: discord.Embed = discord.Embed(title="**Hold up!**", description=f"{message.author.mention} Do NOT ping @everyone or @here. If you need help or have questions, please ping <@&{role}> instead!\n\n**As always, read the server rules!**")
                    return self.handle_options(guild_db=guild_db, embed=embed, module="Everyone/Here", message=message)

                #checks if pinged user has any of protection roles and saves in database
                if pingedMembers:
                    for user in pingedMembers:
                        IDs: list = [role.id for role in user.roles]
                        
                        if guild_db["ping"]["YouTuberProtection"]["role"] in IDs:
                            embed: discord.Embed = discord.Embed(title="**Hold up!**", description=f"{message.author.mention} do not ping Youtuber/s! They are busy with their work and likely will not have time to respond. If you need help you can ping <@&{role}>!\n\n**As always, read the server rules!**")
                            self.handle_options(guild_db=guild_db, embed=embed, module="YouTuberProtection", message=message)                  

                        elif guild_db["ping"]["StaffProtection"]["role"] in IDs:
                            embed=discord.Embed(title="**Hold up!**", description=f"{message.author.mention} pinging one specific staff member will only result in a slow reply. Please use <@&{role}> instead to ping all staff members for a faster reply!\n\n**As always, read the server rules!**")
                            self.handle_options(guild_db=guild_db, embed=embed, module="StaffProtection", message=message)

                        elif guild_db["ping"]["MemberProtection"]["role"] in IDs:
                            embed=discord.Embed(title="**Hold up!**", description=f"{message.author.mention} Please do not ping this user. If you need help or have questions, please ping <@&{role}> instead!\n\n**As always, read the server rules!**")
                            self.handle_options(guild_db=guild_db, embed=embed, module="MemberProtection", message=message)
                        
                        elif user.bot:
                            embed=discord.Embed(title="**Hold up!**", description=f"{message.author.mention} Bots can only reply to specific commands so there's no point in pinging them. If you need help or have questions, please ping <@&{role}> instead!\n\n**As always, read the server rules!**")
                            self.handle_options(guild_db=guild_db, embed=embed, module="Bot", message=message)
        return None
