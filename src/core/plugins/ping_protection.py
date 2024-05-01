import discord, sys, typing
sys.dont_write_bytecode = True
import src.connector as con


class PingProtection:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    async def find_pings(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None,  **OVERFLOW) -> None:
        message: discord.Message = message or after
        
        if guild_db["ping"]["status"] and message.channel.id not in guild_db["ping"]["ignoredChannels"] and not message.author.bot:
            pingedMembers: list[discord.Member | discord.User] = message.mentions if guild_db["ping"]["detectReplyPings"] else [message.guild.get_member(user_id) for user_id in message.raw_mentions]
            user_role_ids: list[int] = [role.id for role in message.author.roles]
            staff_role: int = guild_db["general"]["staffRole"]

            #checks if pinged users have any of protection roles
            if pingedMembers:
                for user in pingedMembers:
                    role_IDs: list = [role.id for role in user.roles]
                    events: list[con.Event] = []
                    
                    # now we check every custom rule:
                    for rule_name, rule_data in guild_db["ping"]["rules"].items():
                        # has bypass or not protected, skipping
                        if rule_data.get("role") not in role_IDs or rule_data.get("bypass") in user_role_ids:
                            continue

                        embed = discord.Embed(title="**Hold up!**", 
                                              description=f"{message.author.mention} Please do not ping this user. If you need help or have questions, please ping <@&{staff_role}> instead!\n\n**As always, read the server rules!**", 
                                              color=discord.Colour.dark_embed(), timestamp=self.shared.time.datetime())
                        events.append(con.Event(message.channel, "send", event_data={"kwargs": {"embed": embed, "delete_after": 30}}))

                        if rule_data.get("ping"):
                            events.append(con.Event(message.channel, "send", event_data={"kwargs": {"content": f"Calling staff team: <@&{staff_role}>"}}))

                        if rule_data.get("delete"):
                            events.append(con.Event(message, "delete", event_data={}))

                        if rule_data.get("log") and (log_channel_id := rule_data.get("logChannel")):
                            if log_channel := message.guild.get_channel(log_channel_id):
                                embed: discord.Embed = discord.Embed(title=f"Ping Protection - {rule_name}", timestamp=self.shared.time.datetime(), color=discord.Colour.dark_embed())
                                embed.set_thumbnail(url=message.author.display_avatar.url)
                                embed.add_field(name="`` Author ``", value=f"<:profile:1203409921719140432>┇{message.author.display_name}\n<:global:1203410626492240023>┇{message.author.global_name}\n<:ID:1203410054016139335>┇{message.author.id}", inline=True)
                                embed.add_field(name="`` Location ``", value=f"<:msg_id:1203422168046768129>┇{message.id}\n<:text_c:1203423388320669716>┇{message.channel.name}\n<:ID:1203410054016139335>┇{message.channel.id}", inline=True)
                                if (msglen := len(message.content)) > 1000:
                                    embed.add_field(name="`` Message ``", value=f"{message.content[:msglen-1000]}...", inline=False)
                                else:
                                    embed.add_field(name="`` Message ``", value=message.content if msglen != 0 else "Could not find the message content.", inline=False)
    
                                events.append(con.Event(log_channel, "send", event_data={"kwargs": {"embed": embed}}))

                    self.shared.sender.resolver(events)
