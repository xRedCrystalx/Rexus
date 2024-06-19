import discord, sys, typing
sys.dont_write_bytecode = True
import src.connector as con

from src.core.helpers.permissions import check_ids
from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.event import Event
from src.core.helpers.emojis import CustomEmoji as CEmoji

class PingProtection:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    async def find_pings(self, guild_db: dict[str, typing.Any], message: discord.Message = None, after: discord.Message = None,  **OVERFLOW) -> None:
        # check for on_message or on_message_edit events - one is always `None`
        message: discord.Message = message or after
        
        # plugin disabled, bot, ignored channel
        if not guild_db["ping"]["status"] and check_ids([message.channel], guild_db["ping"]["ignoredChannels"]) and message.author.bot:
            return
            
        pingedMembers: list[discord.Member | discord.User] = message.mentions if guild_db["ping"]["detectReplyPings"] else [message.guild.get_member(user_id) for user_id in message.raw_mentions]
        staff_role: int = guild_db["general"]["staffRole"]

        #checks if pinged users have any of protection roles
        for member in pingedMembers:
            
            #checks every custom rule:
            for rule_name, rule_data in guild_db["ping"]["rules"].items():
                # has bypass or not protected, skipping
                if not check_ids(rule_data.get("role"), member.roles) or check_ids([rule_data.get("bypass")], member.roles):
                    continue
                
                # whole notification logic - once executed, check will stop
                embed = create_base_embed("**Hold up!**", description=f"{message.author.mention} Please do not ping this user. If you need help or have questions, please ping <@&{staff_role}> instead!\n\n**As always, read the server rules!**")
                self.shared.sender.resolver(Event(message.channel, "send", event_data={"kwargs": {"embed": embed, "delete_after": 30}})) 

                if rule_data.get("ping"):
                    self.shared.sender.resolver(Event(message.channel, "send", event_data={"kwargs": {"content": f"Calling staff team: <@&{staff_role}>"}}))

                if rule_data.get("delete"):
                    self.shared.sender.resolver(Event(message, "delete", event_data={}))

                # log message
                if rule_data.get("log") and (log_channel_id := rule_data.get("logChannel")):
                    embed: discord.Embed =  apply_embed_items(
                        embed=create_base_embed(f"Ping Protection - {rule_name}"),
                        thumbnail=message.author.display_avatar.url)
                    embed.add_field(name="`` Author ``", value=f"{CEmoji.PROFILE}┇{message.author.display_name}\n{CEmoji.GLOBAL}┇{message.author.global_name}\n{CEmoji.ID}┇{message.author.id}", inline=True)
                    embed.add_field(name="`` Location ``", value=f"{CEmoji.MSG_ID}┇{message.id}\n{CEmoji.TEXT_C}┇{message.channel.mention}\n{CEmoji.ID}┇{message.channel.id}", inline=True)
                    embed.add_field(name="`` Message ``", value="Could not find the message content." if len(message.content) == 0 else message.content if len(message.content) < 1000 else f"{message.content[:1000]}...", inline=False)

                    if log_channel := message.guild.get_channel(log_channel_id):
                        self.shared.sender.resolver(Event(log_channel, "send", event_data={"kwargs": {"embed": embed}}))
                return None
