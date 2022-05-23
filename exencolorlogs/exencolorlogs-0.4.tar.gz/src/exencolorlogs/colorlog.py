import logging

from termcolor import colored

logging.addLevelName(25, "OK")
OK = 25

COLORS: dict[str, str] = {
    "OK": "green",
    "CRITICAL": "red",
    "ERROR": "red",
    "WARNING": "yellow",
    "INFO": "cyan",
    "DEBUG": "white",
}


class Logger(logging.Logger):
    def __init__(self, tag: str = "BOT", level: int = logging.DEBUG):
        super().__init__(tag, level)
        handler = logging.StreamHandler()
        formatter = Formatter()
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def ok(self, message, *args, **kwargs):
        self.log(OK, message, *args, **kwargs)


class Formatter(logging.Formatter):
    def __init__(self):
        super().__init__("{asctime} [ {levelname} ] {name}: {message}", style="{")

    def format(self, record: logging.LogRecord):
        color = COLORS[record.levelname]
        record.levelname = colored(record.levelname, color)
        return super().format(record)
