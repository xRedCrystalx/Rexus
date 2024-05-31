import sys, discord, typing, datetime
sys.dont_write_bytecode = True
import src.connector as con
from xRedUtils.dates import get_datetime

if typing.TYPE_CHECKING:
    from discord.ext import commands

class MiscellaneousHandlers:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot

    async def alt_detection(self, member: discord.Member, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if guild_db["alt"]["status"] and (channel_id := guild_db["alt"]["log_channel"]):
            joinedAt: int = int(datetime.datetime.timestamp(member.joined_at))
            createdAt: int = int(datetime.datetime.timestamp(member.created_at))

            if joinedAt-createdAt <= 259200:
                embed: discord.Embed=discord.Embed(title="Alt Detection", color=discord.Colour.dark_embed(), timestamp=get_datetime())
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{member.display_name}\n<:global:1203410626492240023>┇{member.global_name}\n<:ID:1203410054016139335>┇{member.id}", inline=True)
                embed.add_field(name="`` Rule ``", value=f"**Account was created <t:{createdAt}:R>.**\n`AccountAge < 3 days`", inline=True)
                embed.set_footer(text=f"Have an eye on this member.")

                if channel := member.guild.get_channel(channel_id):
                    self.shared.sender.resolver(con.Event(channel, "send", event_data={"kwargs": {"embed": embed}}))
        return None

    async def automod_response(self, action: discord.AutoModAction, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if action.action.channel_id and guild_db["automod"]["status"]:
            system_channel: discord.TextChannel = action.guild.get_channel(action.action.channel_id)
            db_rule_data: dict | str | None = guild_db["automod"]["rules"].get(str(action.rule_id))

            if db_rule_data and system_channel:
                if isinstance(db_rule_data, dict):
                    data: str | None = db_rule_data.get(action.matched_keyword) or db_rule_data.get("GLOBAL_VALUE")
                    if data:
                        self.shared.sender.resolver(con.Event(system_channel, "send", event_data={"kwargs": {"content": str(data).format(user=action.member, channel=action.channel)}}))

                elif isinstance(db_rule_data, str):
                    self.shared.sender.resolver(con.Event(system_channel, "send", event_data={"kwargs": {"content": db_rule_data.format(user=action.member, channel=action.channel)}}))
        return None
