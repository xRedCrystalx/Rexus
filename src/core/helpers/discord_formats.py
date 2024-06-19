import sys
sys.dont_write_bytecode = True

def code_block(string: str, lang: str = "") -> str:
    return f"```{lang}\n{string}```"

def one_line_code(string: str) -> str:
    return f"`{string}`"

def bold(string: str) -> str:
    return f"**{string}**"

def italics(string: str) -> str:
    return f"*{string}*"

def underline(string: str) -> str:
    return f"__{string}__"

def strike_through(string: str) -> str:
    return f"~~{string}~~"

def masked(name: str, link: str) -> str:
    return f"[{name}]({link})"

# ignoring headers, quotes and lists due to levels