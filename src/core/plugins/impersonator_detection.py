import discord, sys, typing
sys.dont_write_bytecode = True
import src.connector as con

class ImpersonatorDetection:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    def _create_embed(self, member: discord.Member) -> discord.Embed:
        embed: discord.Embed = discord.Embed(title="Impersonator Detection", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    async def detection_on_join(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], member: discord.Member, **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        if member and guild_db["imper"]["status"] and (channel_id := guild_db["imper"]["log_channel"]):
            names: list[str] = bot_db["filters"]["impersonator"]["names"]
            if member.display_name.lower() in names or str(member.global_name).lower() in names and member.id not in names:
                try:
                    embed: discord.Embed = self._create_embed(member)
                    embed.add_field(name="`` Member ``", value=f"<:profile:1203409921719140432>┇{member.display_name}\n<:global:1203410626492240023>┇{member.global_name}\n<:ID:1203410054016139335>┇{member.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"**Member joined with Celebrity/YouTuber/Bot/Staff name.**", inline=True)
                    embed.add_field(name="`` Kick Message ``", value=f"```Impersonating a youtuber/celebrity/bot/staff. Come back when you've changed your name or you can request a nickname from staff.```", inline=False)

                    if channel := member.guild.get_channel(channel_id):
                        return [{channel: {"action": "send", "kwargs": {"embed": embed}}}]

                except Exception as error:
                    self.shared.logger.log(f"@ImpersonatorDetection.detection_on_join: {type(error).__name__}: {error}", "ERROR")
        return None

    async def detection_on_update(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], before: discord.Member, after: discord.Member, **OVERFLOW) -> dict[typing.Any, dict[str, typing.Any]] | None:
        if after.global_name != before.global_name or before.display_name != after.display_name:
            if guild_db["imper"]["status"] and (channel_id := guild_db["imper"]["log_channel"]):
                names: list[str] = bot_db["filters"]["impersonator"]["names"]
                if after.display_name.lower() in names or str(after.global_name).lower() in names and after.id not in names:
                    try:
                        embed: discord.Embed = self._create_embed(after)
                        embed.add_field(name="`` Before ``", value=f"<:profile:1203409921719140432>┇{before.display_name}\n<:global:1203410626492240023>┇{before.global_name}\n<:ID:1203410054016139335>┇{before.id}", inline=True)
                        embed.add_field(name="`` After ``", value=f"<:profile:1203409921719140432>┇{after.display_name}\n<:global:1203410626492240023>┇{after.global_name}\n<:ID:1203410054016139335>┇{after.id}", inline=True)
                        embed.add_field(name="`` Reason ``", value=f"Member changed name to Celebrity/YouTuber/Bot/Staff name. name.\n\n```Impersonating a youtuber/celebrity/bot/staff. Come back when you've changed your name or you can request a nickname from staff.```", inline=False)

                        if channel := after.guild.get_channel(channel_id):
                            return [{channel: {"action": "send", "kwargs": {"embed": embed}}}]

                    except Exception as error:
                        self.shared.logger.log(f"@ImpersonatorDetection.detection_on_update: {type(error).__name__}: {error}", "ERROR")
        return None
