import logging, sys, logging.handlers, typing
sys.dont_write_bytecode = True
import src.connector as con

class Logger:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.c = self.shared.colors
        self._levels: dict[str, int] = {
            "UPDATE": 25, 
            "SYSTEM": 17,
            "NP_DEBUG": 15,
        }

        self.FILE_LEVEL = 15
        self.CONSOLE_LEVEL = 17

        self.handlers: list[logging.Handler] = []
        self.logger: logging.Logger = logging.getLogger("discord")
        self.logger.setLevel(10)

    def _level_handler(self) -> None:
        for name, level in self._levels.items():
            setattr(logging, name, level)
            logging.addLevelName(level, name)

        self.log(f"@Logger._level_handler > Injected custom levels to logging library.", "NP_DEBUG")

    def _handler_reloader(self) -> None:
        for handler in self.handlers.copy():
            self.log(f"@Logger._handler_reloader > Removing {handler.get_name()}", "NP_DEBUG")
            self.logger.removeHandler(handler)
            self.handlers.remove(handler)

    def _formatter(self, option: str = None):
        class ColorFormatter(logging.Formatter):
            LEVEL_COLOURS: list[int, str] = [
                (logging.DEBUG, self.c.White),
                (logging.INFO, self.c.Blue),
                (logging.WARNING, self.c.Bold+self.c.Yellow),
                (logging.ERROR, self.c.Bold+self.c.Red),
                (logging.CRITICAL, self.c.Red),
                (17, self.c.Bold+self.c.White)
            ]

            FORMATS: dict[int, logging.Formatter] = {level: logging.Formatter(
                f'\x1b[30;1m%(asctime)s{self.c.R} {colour}%(levelname)-8s{self.c.R} \x1b[35m%(name)s{self.c.R} %(message)s', '%Y-%m-%d %H:%M:%S') for level, colour in LEVEL_COLOURS}

            def format(self, record) -> str:
                formatter: logging.Formatter | None = self.FORMATS.get(record.levelno)
                if formatter is None:
                    formatter = self.FORMATS[logging.DEBUG]

                # Override the traceback to always print in red
                if record.exc_info:
                    text = formatter.formatException(record.exc_info)
                    record.exc_text = f'\x1b[31m{text}\x1b[0m'

                output = formatter.format(record)

                # Remove the cache layer
                record.exc_text = None
                return output

        if option:
            return ColorFormatter()
        else:
            return logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")

    def StreamHandler(self) -> None:
        self.log(f"@Logger.StreamHandler > Creating stream handler (console)", "NP_DEBUG")
        stream_handler = logging.StreamHandler()
        
        if sys.stdout.isatty():
            formmatter = self._formatter("COLOR")
        else:
            formmatter = self._formatter()
        
        self.log(f"@Logger.StreamHandler > Setting handler's data.", "NP_DEBUG")
        stream_handler.setFormatter(formmatter)
        stream_handler.setLevel(self.CONSOLE_LEVEL)
        stream_handler.set_name("Stream Handler")

        self.handlers.append(stream_handler)
        self.logger.addHandler(stream_handler)
        self.log(f"@Logger.StreamHandler > Added handler to logger.", "NP_DEBUG")

    def FileHandler(self) -> None:
        self.log(f"@Logger.FileHandler > Creating new handler and formatter for file handler.", "NP_DEBUG")
        formatter: logging.Formatter = self._formatter()
        file_handler: logging.handlers.RotatingFileHandler = logging.handlers.RotatingFileHandler(filename=f"{self.shared.path}/logs/logger@discord-system.log", encoding="utf-8")
        
        self.log(f"@Logger.FileHandler > Setting handler's data.", "NP_DEBUG")
        file_handler.setLevel(self.FILE_LEVEL) # NoPing Debug +
        file_handler.setFormatter(formatter)
        file_handler.set_name("MainFile Handler")

        self.handlers.append(file_handler)
        self.logger.addHandler(file_handler)
        self.log(f"@Logger.FileHandler > Added file handler to logger.", "NP_DEBUG")

    def main(self) -> typing.Self:
        self._level_handler()
        self._handler_reloader()

        self.StreamHandler()
        self.FileHandler()
        return self

    def log(self, msg: str, level: str = "INFO") -> None:
        try:
            lvl: int = getattr(logging, level)
            self.logger.log(lvl, msg=msg)
        except:
            pass
            

"""
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""