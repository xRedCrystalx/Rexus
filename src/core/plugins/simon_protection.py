import sys, discord
sys.dont_write_bytecode = True
from src.connector import shared

from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.other import fetch_invite_links
from src.core.helpers.emojis import CustomEmoji as CEmoji

class SimonProtection:
    async def simon_invite_link_detection(self, message: discord.Message = None, after: discord.Message = None, **OVERFLOW) -> None:
        message: discord.Message = message or after

        if (guilds := await fetch_invite_links(message.content)) and message.guild.id == 1175874833146450042:
            for guild_id in guilds:
                # id of simons's main discord server
                if guild_id == 1067152607459688549:
                    embed: discord.Embed = apply_embed_items(
                        embed=create_base_embed(title="XNDUIW | CBE_Simon Protection"),
                        thumbnail=message.author.display_avatar.url,
                        footer="Member has been banned from the guild.")
                    embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{message.author.display_name}\n{CEmoji.GLOBAL}┇{message.author.name}\n{CEmoji.ID}┇{message.author.id}", inline=True)
                    embed.add_field(name="`` Rule ``", value=f"Detected invite link redirecting to Simon's server.", inline=True)
                    embed.add_field(name="`` Message Content ``", value=message.content if len(message.content) < 1000 else message.content[:1000], inline=False)

                    await message.author.ban(delete_message_days=7, reason="Autoban - XNDUIW")
                    
                    await message.guild.get_channel(1175874833146450042).send(embed=embed)

        return None

async def setup(bot) -> None:
    """await shared.module_manager.load(simon := SimonProtection(), 
        config={
            simon.simon_invite_link_detection: ["on_message", "on_raw_message_edit"]
        }
    )"""