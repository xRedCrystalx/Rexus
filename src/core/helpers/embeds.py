import sys, discord
sys.dont_write_bytecode = True
from discord import Embed

from xRedUtilsAsync.dates import get_datetime
from xRedUtilsAsync.type_hints import SIMPLE_ANY

async def new_embed(title: str = "", thumbnail: str = "", footer: str | dict = None, **kwargs) -> Embed:
    """
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
    return await apply_embed_items(
        embed= await create_base_embed(title=title, **kwargs),
        author=kwargs.get("author"),
        thumbnail=thumbnail,
        image=kwargs.get("image"),
        footer=footer
    )

async def create_base_embed(title: str = "", description: str = None, **kwargs) -> Embed:
    return discord.Embed(title=title, description=description, 
                        color=kwargs.get("color") or discord.Colour.dark_embed(),
                        url=kwargs.get("url"),
                        timestamp=kwargs.get("timestamp") or await get_datetime())

async def apply_embed_items(embed: discord.Embed, author: dict[str, str] = None, thumbnail: str = None, image: str = None, footer: str | dict[str, str] = None) -> Embed:
    """
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

async def to_embed(embed: dict[str, SIMPLE_ANY]) -> Embed:
    return discord.Embed.from_dict(embed)

async def to_dict(embed: Embed) -> dict[str, SIMPLE_ANY]:
    return discord.Embed.to_dict(embed)
