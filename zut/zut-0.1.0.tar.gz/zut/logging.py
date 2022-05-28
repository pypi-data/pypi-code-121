import os, logging, logging.config, atexit
from .color import FOREGROUND_RED, BACKGROUND_RED

class CountHandler(logging.Handler):
    instance = None

    def __init__(self, level=logging.WARNING):
        if CountHandler.instance:
            raise ValueError("CountHandler was already instanciated")

        CountHandler.instance = self
        atexit.register(self.atexit)

        super().__init__(level=level)
        self.level_count = {}
        
    def emit(self, record: logging.LogRecord):
        if record.levelno >= self.level:
            if not record.levelno in self.level_count:
                self.level_count[record.levelno] = 1
            else:
                self.level_count[record.levelno] += 1

    def get_max_levelno(self):
        max_levelno = 0
        for levelno in self.level_count.keys():
            if levelno >= self.level and levelno > max_levelno:
                max_levelno = levelno
        return max_levelno

    @classmethod
    def atexit(self):
        if not CountHandler.instance:
            raise ValueError("CountHandler was not instanciated")

        msg = ""

        levelnos = sorted(CountHandler.instance.level_count.keys(), reverse=True)
        for levelno in levelnos:
            msg += (", " if msg else "") + "%s: %d" % (logging.getLevelName(levelno), CountHandler.instance.level_count[levelno])

        if msg:
            print("Logged " + msg)


def configure_logging(config: dict = None):
    if config == "count":
        count = True
        config = None
    else:
        count = False

    if not config:
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": { 
                    "format": "%(levelname)s [%(name)s] %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                }
            },
            "loggers": {
                "": { # root logger
                    "handlers": ["console"],
                    "level": os.environ.get("LOGLEVEL", "INFO").upper(),
                },
            },
        }

        if count:
            config["handlers"]["count"] = {
                "level": "WARNING",
                "class": "zut.logging.CountHandler",
            }
            for logger in config["loggers"]:
                config["loggers"][logger]["handlers"].append("count")

    # Color logging levels equal or greater than WARNING
    logging.addLevelName(logging.WARNING, FOREGROUND_RED % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, BACKGROUND_RED % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.CRITICAL, BACKGROUND_RED % logging.getLevelName(logging.CRITICAL))

    # Apply configuration
    logging.config.dictConfig(config)
