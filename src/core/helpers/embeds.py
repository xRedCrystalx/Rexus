import sys, discord
sys.dont_write_bytecode = True
from discord import Embed

from xRedUtils.dates import get_datetime
from xRedUtils.type_hints import SIMPLE_ANY

def new_embed(title: str = "", thumbnail: str = None, footer: str | dict = None, **kwargs) -> Embed:
    """
    |sync|

    Simple mostly used function. Use `create_base_embed` and `apply_embed_items` for more customization.

    Base embed:
    - `title` - `str`
    - `description` - `str`
    - `color` - `str` | `discord.Colour`
    - `url` - `str`
    - `timestamp` - `datetime` | `None`

    Embed items:
    - `author` - `dict[name: str, url: str, icon_url: str]` > Author field (Small thing on top, `url` parameter is for link)
    - `image` - `str` > URL of image (under the text image)
    - `thumbnail` - `str` > URL of thumbnail (on the side image)
    - `footer` - `dict[text: str = None, icon_url: str = None]` | `str` > Everything for footer
    """
    return apply_embed_items(
        embed= create_base_embed(title=title, **kwargs),
        author=kwargs.get("author"),
        thumbnail=thumbnail,
        image=kwargs.get("image"),
        footer=footer
    )

def create_base_embed(title: str = "", description: str = None, **kwargs) -> Embed:
    """|sync|"""
    return discord.Embed(title=title, description=description, 
                        color=kwargs.get("color") or discord.Colour.dark_embed(),
                        url=kwargs.get("url"),
                        timestamp=kwargs.get("timestamp") or get_datetime())

def apply_embed_items(embed: discord.Embed, author: dict[str, str] = None, thumbnail: str = None, image: str = None, footer: str | dict[str, str] = None) -> Embed:
    """
    |sync|

    Adds data to the embed.
    - author: `dict[name: str, url: str = None, icon_url: str = None]` > Author field (Small thing on top, `url` parameter is for link)
    - image: `str` > URL of image (under the text image)
    - thumbnail: `str` > URL of thumbnail (on the side image)
    - footer: `dict[text: str = None, icon_url: str = None]` | `str` > Everything for footer
    """
    if author:
        embed.set_author(**author)

    embed.set_thumbnail(url=thumbnail)
    embed.set_image(url=image)

    if isinstance(footer, dict):
        embed.set_footer(**footer)
    else:
        embed.set_footer(text=footer)

    return embed

def to_embed(embed: dict[str, SIMPLE_ANY]) -> Embed:
    """|sync|"""
    return discord.Embed.from_dict(embed)

def to_dict(embed: Embed) -> dict[str, SIMPLE_ANY]:
    """|sync|"""
    return discord.Embed.to_dict(embed)

NO_PERMISSIONS: Embed = new_embed(title="No permissions", description="You are not allowed to do that!", color=discord.Colour.red())
