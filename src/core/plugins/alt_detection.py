import sys, discord
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtilsAsync.dates import timestamp
from xRedUtilsAsync.type_hints import SIMPLE_ANY

class AltDetection:
    async def detect(self, member: discord.Member, guild_db: dict[str, SIMPLE_ANY], **OVERFLOW) -> None:
        if guild_db["alt"]["status"] and (channel_id := guild_db["alt"]["log_channel"]):
            joinedAt: int = int(timestamp(member.joined_at))
            createdAt: int = int(timestamp(member.created_at))

            if joinedAt-createdAt <= 259200:
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed(title="Alt Detection"),
                    thumbnail=member.display_avatar.url,
                    footer="Have an eye on this member.")
                embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{member.display_name}\n{CEmoji.GLOBAL}┇{member.name}\n{CEmoji.ID}┇{member.id}", inline=True)
                embed.add_field(name="`` Rule ``", value=f"**Account was created <t:{createdAt}:R>.**\n`AccountAge < 3 days`", inline=True)

                if channel := member.guild.get_channel(channel_id):
                    await channel.send(embed=embed)
        return None

async def setup(bot: commands.AutoShardedBot) -> None:
    await shared.module_manager.load(alt := AltDetection(), 
        config={
            alt.detect: ["on_member_join"]
        }
    )
