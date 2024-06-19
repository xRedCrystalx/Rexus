import discord, sys, typing
sys.dont_write_bytecode = True
import src.connector as con

from src.core.helpers.permissions import check_ids
from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.event import Event
from src.core.helpers.emojis import CustomEmoji as CEmoji

class ImpersonatorDetection:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    async def detection_on_join(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], member: discord.Member, **OVERFLOW) -> None:
        if member and guild_db["imper"]["status"] and (channel_id := guild_db["imper"]["log_channel"]):
            names: list[str] = bot_db["filters"]["impersonator"]["names"]
            whitelisted: list[int] = bot_db["filters"]["impersonator"]["whitelist"]

            if member.display_name.lower() in names or str(member.name).lower() in names and not check_ids(member.id, whitelisted):
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed("Impersonator Detection"),
                    thumbnail=member.display_avatar.url)
                embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{member.display_name}\n{CEmoji.GLOBAL}┇{member.name}\n{CEmoji.ID}┇{member.id}", inline=True)
                embed.add_field(name="`` Rule ``", value=f"**Member joined with Celebrity/YouTuber/Bot/Staff name.**", inline=True)
                embed.add_field(name="`` Kick Message ``", value=f"```Impersonating a youtuber/celebrity/bot/staff. Come back when you've changed your name or you can request a nickname from staff.```", inline=False)

                if channel := member.guild.get_channel(channel_id):
                    self.shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"embed": embed}}))
        return None

    async def detection_on_update(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], before: discord.Member, after: discord.Member, **OVERFLOW) -> None:
        if after.name != before.name or after.display_name != before.display_name:
            if guild_db["imper"]["status"] and (channel_id := guild_db["imper"]["log_channel"]):
                names: list[str] = bot_db["filters"]["impersonator"]["names"]
                whitelisted: list[int] = bot_db["filters"]["impersonator"]["whitelist"]

                if after.display_name.lower() in names or str(after.name).lower() in names and not check_ids(after.id, whitelisted):
                    embed: discord.Embed = apply_embed_items(
                        embed=create_base_embed("Impersonator Detection"),
                        thumbnail=after.display_avatar.url)
                    embed.add_field(name="`` Before ``", value=f"{CEmoji.PROFILE}┇{before.display_name}\n{CEmoji.GLOBAL}┇{before.name}\n{CEmoji.ID}┇{before.id}", inline=True)
                    embed.add_field(name="`` After ``", value=f"{CEmoji.PROFILE}┇{after.display_name}\n{CEmoji.GLOBAL}┇{after.name}\n{CEmoji.ID}┇{after.id}", inline=True)
                    embed.add_field(name="`` Reason ``", value=f"Member changed their name to Celebrity/YouTuber/Bot/Staff name. \n\n```Impersonating a youtuber/celebrity/bot/staff. Come back when you've changed your name or you can request a nickname from staff.```", inline=False)

                    if channel := after.guild.get_channel(channel_id):
                        self.shared.sender.resolver(Event(channel, "send", event_data={"kwargs": {"embed": embed}}))
        return None
