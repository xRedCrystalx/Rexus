import sys
sys.dont_write_bytecode = True
from discord.utils import (format_dt, 
                           escape_markdown, 
                           remove_markdown, 
                           parse_time, 
                           escape_mentions)

def italics(s: str) -> str:
    return f"*{s}*"

def bold(s: str) -> str:
    return f"**{s}**"

def bolitalic(s: str) -> str:
    """Bold and italic"""
    return f"***{s}***"

def underline(s: str) -> str:
    return f"__{s}__"

def strike_through(s: str) -> str:
    return f"~~{s}~~"

def one_line_code(s: str) -> str:
    return f"`{s}`"

def code_block(s: str, lang: str = "") -> str:
    return f"```{lang}\n{s}```"

def masked_link(name: str, link: str) -> str:
    return f"[{name}]({link})"

def header(s: str, level: int) -> str:
    return "#"*level + s

def quote(s: str) -> str:
    return f"> {s}"

def spoiler(s: str) -> str:
    return f"||{s}||"

def subtext(s: str) -> str:
    return f"-#{s}"

def listing(s: list[str]) -> str:
    return "\n".join([f"- {part}" for part in s])

# TODO: organizational text formatting - experimental