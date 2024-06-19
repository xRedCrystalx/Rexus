import sys, discord, typing
sys.dont_write_bytecode = True
import src.connector as con

from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.event import Event
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtils.dates import timestamp

class MiscellaneousHandlers:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    async def alt_detection(self, member: discord.Member, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if guild_db["alt"]["status"] and (channel_id := guild_db["alt"]["log_channel"]):
            joinedAt: int = int(timestamp(member.joined_at))
            createdAt: int = int(timestamp(member.created_at))

            if joinedAt-createdAt <= 259200:
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed(title="Alt Detection"),
                    thumbnail=member.display_avatar.url,
                    footer="Have an eye on this member."
                )
                embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{member.display_name}\n{CEmoji.GLOBAL}┇{member.name}\n{CEmoji.ID}┇{member.id}", inline=True)
                embed.add_field(name="`` Rule ``", value=f"**Account was created <t:{createdAt}:R>.**\n`AccountAge < 3 days`", inline=True)

                if channel := member.guild.get_channel(channel_id):
                    self.shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"embed": embed}}))
        return None

    async def automod_response(self, action: discord.AutoModAction, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if action.action.channel_id and guild_db["automod"]["status"]:
            system_channel: discord.TextChannel = action.guild.get_channel(action.action.channel_id)
            db_rule_data: dict | str | None = guild_db["automod"]["rules"].get(str(action.rule_id))

            if db_rule_data and system_channel:
                frmt: dict[str, object] = {"user": action.member, "channel": action.channel}

                if isinstance(db_rule_data, dict):
                    if (data := db_rule_data.get(action.matched_keyword) or db_rule_data.get("GLOBAL_VALUE")):
                        self.shared.sender.resolver(Event(system_channel, "send", event_data={"kwargs": {"content": str(data).format(**frmt)}}))

                elif isinstance(db_rule_data, str):
                    self.shared.sender.resolver(Event(system_channel, "send", event_data={"kwargs": {"content": db_rule_data.format(**frmt)}}))
        return None
