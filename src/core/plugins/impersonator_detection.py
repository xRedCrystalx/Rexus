import discord, sys
sys.dont_write_bytecode = True
from src.connector import shared

from src.core.helpers.permissions import check_ids, compare_iterables
from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtils.type_hints import SIMPLE_ANY

class ImpersonatorDetection:
    async def check_name(self, member: discord.Member, bot_db: dict[str, SIMPLE_ANY]) -> bool:
        names: list[str] = bot_db["filters"]["impersonator"]["names"]
        whitelisted: list[int] = bot_db["filters"]["impersonator"]["whitelist"]

        return True if await compare_iterables([member.display_name.lower(), str(member.name).lower()], names) and not await check_ids(member, whitelisted) else False

    async def detect(self, guild_db: dict[str, SIMPLE_ANY], bot_db: dict[str, SIMPLE_ANY], member: discord.Member = None, after: discord.Member = None, **OVERFLOW) -> None:
        member = member or after

        if member and guild_db["imper"]["status"] and (channel_id := guild_db["imper"]["log_channel"]):
            if self.check_name(member, bot_db):
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed("Impersonator Detection"),
                    thumbnail=member.display_avatar.url)
                embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{member.display_name}\n{CEmoji.GLOBAL}┇{member.name}\n{CEmoji.ID}┇{member.id}", inline=True)
                embed.add_field(name="`` Rule ``", value=f"**Member has Celebrity/YouTuber/Bot/Staff name.**", inline=True)
                embed.add_field(name="`` Kick Message ``", value=f"```Impersonating a youtuber/celebrity/bot/staff. Come back when you've changed your name or you can request a nickname from staff.```", inline=False)

                if channel := member.guild.get_channel(channel_id):
                    await channel.send(embed=embed)

async def setup(bot) -> None:
    pass
    #await con.shared.plugin_load(impersonator := ImpersonatorDetection(), callable=(["on_member_update", "on_member_join"], impersonator.detect))