import sys, re
sys.dont_write_bytecode = True

class C:
    Black: str = "\u001b[30;1m"
    Red: str = "\u001b[31;1m"
    Green: str = "\u001b[32;1m"
    Yellow: str = "\u001b[33;1m"
    Blue: str = "\u001b[34;1m"
    Magenta: str = "\u001b[35;1m"
    Cyan: str = "\u001b[36;1m"
    White: str = "\u001b[37;1m"
    R: str = "\u001b[0m"
    Gray: str = "\u001b[90m"
    Bold: str = "\u001b[1m"
    Underline: str = "\u001b[4m"
    DRed: str = "\u001b[31m"
    DGreen: str = "\u001b[32m"
    DYellow: str = "\u001b[33m"
    DMagenta: str = "\u001b[35m"
    DCyan: str = "\u001b[36m"
    DBlue: str = "\u001b[34m"

class CNone:
    Black: str = ""
    Red: str = ""
    Green: str = ""
    Yellow: str = ""
    Blue: str = ""
    DBlue: str = ""
    Magenta: str = ""
    Cyan: str = ""
    White: str = ""
    R: str = ""
    Gray: str = ""
    Bold: str = ""
    Underline: str = ""
    DRed: str = ""
    DGreen: str = ""
    DYellow: str = ""
    DMagenta: str = ""
    DCyan: str = ""
    DBlue: str = ""

def color_handler() -> C | CNone:
    ask = str(input("Display colours (y/Y or n/N)? (Your console/terminal needs to support ANSI colours): "))
    while True:   
        if ask.lower() == "y":
            return C
        elif ask.lower() == "n":
            return CNone
        else:
            ask = str(input(f"Error: {ask} is not a valid argument. Write only 'y/Y' or 'n/N'. Display colours?: "))

def rem_colors(data: str) -> str:
    return re.sub(r"\x1b[^m]*m", "", data)

def auto_color_handler() -> C | CNone:
    if sys.stdout.isatty():
        return C
    return CNone