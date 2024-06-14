import sys, discord
sys.dont_write_bytecode = True

from xRedUtils.dates import get_datetime
from xRedUtils.type_hints import SIMPLE_ANY

def create_base_embed(title: str = "", description: str = "", **kwargs) -> discord.Embed:
    return discord.Embed(title=title, description=description, 
                        color=kwargs.get("color") or discord.Colour.dark_embed(),
                        url=kwargs.get("url") or "",
                        timestamp=get_datetime())

def apply_embed_items(embed: discord.Embed, author: dict[str, str] = None, thumbnail: str = None, image: str = None, footer: str | dict[str, str] = None) -> discord.Embed:
    """
    Adds data to the embed.
    - author: `dict[name: str, url: str = None, icon_url: str = None]` > Author field (Small thing on top, `url` parameter is for link)
    - image: `str` > URL of image (under the text image)
    - thumbnail: `str` > URL of thumbnail (on the side image)
    - footer: `dict[text: str = Non, icon_url: str = None]` | `str` > Everything for footer
    """
    if author:
        embed.set_author(**author)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)
    
    if footer:
        if isinstance(footer, dict):
            embed.set_footer(**footer)
        else:
            embed.set_footer(text=footer)

    return embed

def to_embed(embed) -> discord.Embed:
    return discord.Embed.from_dict(embed)

def to_dict(embed) -> dict[str, SIMPLE_ANY]:
    return discord.Embed.to_dict(embed)
