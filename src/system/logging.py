import logging, sys
sys.dont_write_bytecode = True
from types import MethodType
from src.connector import shared

from xRedUtilsAsync.colors import (
    Foreground255 as FG,
    Style as ST
)
from xRedUtils.dates import get_datetime

# fucking hate logging module - monkeypatch for custom options
class OverWriter:
    def format(self, record: logging.LogRecord) -> str:
        color: str = self.COLORS.get(record.levelno, FG.BLUE)

        # Override the traceback to always print in red
        if record.exc_info:
            text: str = self.formatException(record.exc_info)
            record.exc_text = f"{FG.RED}{text}{ST.RESET}"

        formatted: str = logging.Formatter.format(self, record).format(lvl_c=color)
    
        # Remove the cache layer
        record.exc_text = None
        return formatted
    
    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno not in self.LEVELS:
            return
        getattr(logging, self.__class__.__name__).emit(self, record) # check if it works

class Logger(logging.Logger):
    def __init__(self, config: dict[str, dict[str, tuple]]) -> None:
        self.config: dict[str, dict[str, tuple]] = config
        super().__init__("Rexus", 1)
        # remove previous handlers and update levels
        self.handlers.clear()
        self._setLevels()

        for name, (lvl, path, format) in self.config["handlers"].items():
            self.createHandler(name, lvl, path, format)

    def _setLevels(self) -> None:
        """Removes all levels from the `dicts` and adds new ones."""
        logging._nameToLevel.clear()
        logging._levelToName.clear()
    
        for name, level in self.config["levels"].items():
            logging.addLevelName(level[0], name)

    def createHandler(self, name: str, level: int | list[int], path: str | None, format: str) -> logging.Formatter:
        if path:
            handler = logging.FileHandler(path, encoding="utf-8")
        else:
            handler = logging.StreamHandler()
        
        if isinstance(level, (list, tuple)):
            handler.LEVELS = level
            handler.emit = MethodType(OverWriter.emit, handler) # monkeypatch
            level = min(level)

        handler.set_name(name)
        handler.setLevel(level)

        formatter = logging.Formatter(fmt=format, datefmt="%Y-%m-%d %H:%M:%S")
        if not path and sys.stdout.isatty():
            formatter.COLORS = {level: colour for level, colour in self.config["levels"].values()}
            formatter.format = MethodType(OverWriter.format, formatter) # monkeypatch

        handler.setFormatter(formatter)
        self.addHandler(handler)

    def log(self, level: int | str, msg: str, *args, logger_name: str = None, **kwargs) -> None:
        if isinstance(level, str):
            level = logging._nameToLevel.get(level.upper(), logging.INFO)

        logger: logging.Logger = logging.getLogger(logger_name) if logger_name else self
        logger._log(level, msg, args, **kwargs)

configuration: dict[str, dict[str, tuple]] = {
    "levels": {
        "CRITICAL": (50, FG.RED),
        "ERROR": (40, FG.RED_BERRY),
        "WARNING": (30, FG.YELLOW),
        "UPDATE": (25, FG.GREEN),
        "SYSTEM": (22, FG.PLATINUM),
        "INFO": (20, FG.CANARY),
        "TESTING": (18,  FG.CHARCOAL),
        "DEBUG": (10, FG.WHITE),
        "NOTSET": (0, None)
    },
    "handlers": {
        "Console": (18, None, "\x1b[30;1m%(asctime)s\x1b[0m {lvl_c}%(levelname)-10s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s\x1b[0m"),
        "InDev": ([10, 18], f"./logs/development.log", "[%(asctime)s] [%(levelname)-10s] %(name)s: %(message)s"),
        "Daily": (1, f"./logs/{get_datetime():%Y-%m-%d}.log", "[%(asctime)s] [%(levelname)-10s] %(name)s: %(message)s")
    }
}

async def setup(bot) -> None:
    await shared.module_manager.load(Logger(configuration),
        config={
            "module": True,
            "location": shared,
            "var": "logger"
        }
    )