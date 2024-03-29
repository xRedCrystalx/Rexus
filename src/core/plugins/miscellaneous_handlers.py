import sys, discord, typing, datetime
sys.dont_write_bytecode = True
import src.connector as con

if typing.TYPE_CHECKING:
    from discord.ext import commands

class MiscellaneousHandlers:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot

    async def alt_detection(self, member: discord.Member, guild_db: dict[str, typing.Any], **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        try:
            if guild_db["alt"]["status"] and (channel_id := guild_db["alt"]["log_channel"]):
                joinedAt: int = int(datetime.datetime.timestamp(member.joined_at))
                createdAt: int = int(datetime.datetime.timestamp(member.created_at))

                if joinedAt-createdAt <= 259200:
                    embed: discord.Embed=discord.Embed(title="Alt Detection", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.add_field(name="`` Member ``", value=f"**Display Name:** {member.display_name}\n**Global Name:** {member.global_name}\n**ID:** {member.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"**Account was created <t:{createdAt}:R>.**\n`AccountAge < 3 days`", inline=True)
                    embed.set_footer(text=f"User ID: {member.id} | Have an eye on this member.")

                    if channel := member.guild.get_channel(channel_id):
                        return [{channel : {"action" : "send", "kwargs" : {"embed" : embed}}}]

        except Exception as error:
            self.shared.logger.log(f"@MiscellaneousHandlers.alt_detection: {type(error).__name__}: {error}", "ERROR")
        return None

    async def automod_response(self, action: discord.AutoModAction, guild_db: dict[str, typing.Any], **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        try:
            if action.action.channel_id and guild_db["automod"]["status"]:
                system_channel: discord.TextChannel = action.guild.get_channel(action.action.channel_id)
                db_rule_data: dict | str | None = guild_db["automod"]["rules"].get(str(action.rule_id))

                if db_rule_data and system_channel:
                    if isinstance(db_rule_data, dict):
                        data: str | None = db_rule_data.get(action.matched_keyword) or db_rule_data.get("GLOBAL_VALUE")
                        if data:
                            return [{system_channel: {"action": "send", "kwargs": {"content": str(data).format(user=action.member, channel=action.channel)}}}]

                    elif isinstance(db_rule_data, str):
                        return [{system_channel: {"action": "send", "kwargs": {"content": db_rule_data.format(user=action.member, channel=action.channel)}}}]

        except Exception as error:
            self.shared.logger.log(f"@MiscellaneousHandlers.automod_response: {type(error).__name__}: {error}", "ERROR")
        return None
