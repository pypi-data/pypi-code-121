import logging
from datetime import datetime

from rich.highlighter import ReprHighlighter
from rich.table import Table
from rich.text import Text

import cvee.utils

named_levels = {
    "info": logging.INFO,
    "warning": logging.WARNING,
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
logger_initialized = {}

_glb_log_level = None
_glb_log_file = None


def set_log_level(log_level):
    if isinstance(log_level, str):
        log_level = named_levels[log_level]

    global _glb_log_level
    _glb_log_level = log_level


def get_log_level():
    global _glb_log_level
    return _glb_log_level


def set_log_file(log_file):
    global _glb_log_file
    _glb_log_file = log_file


def get_log_file():
    global _glb_log_file
    return _glb_log_file


# https://github.com/open-mmlab/mmcv/blob/master/mmcv/utils/logging.py
# https://github.com/facebookresearch/detectron2/blob/main/detectron2/utils/logger.py
def get_logger(name, log_file=None, log_level="info", file_mode="w"):
    if isinstance(log_level, str):
        log_level = named_levels[log_level]

    # glb_log_level will override log_level
    glb_log_level = get_log_level()
    if glb_log_level is not None:
        log_level = glb_log_level

    # glb_log_file will override log_file
    glb_log_file = get_log_file()
    if glb_log_file is not None:
        log_file = glb_log_file

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    if name in logger_initialized:
        return logger

    console = cvee.utils.get_console()
    formatter = logging.Formatter("%(message)s")
    rich_handler = RichHandler(name, log_level, console)
    rich_handler.setFormatter(formatter)
    logger.addHandler(rich_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, file_mode)
        formatter = logging.Formatter(f"[%(asctime)s {name}] %(levelname)s %(message)s", datefmt="%H:%M:%S")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    logger_initialized[name] = True
    return logger


class RichHandler(logging.Handler):
    def __init__(self, name, level, console, datefmt="%H:%M:%S"):
        super().__init__(level=level)
        self.name = name
        self.console = console
        self.datefmt = datefmt
        self.highlighter = ReprHighlighter()

    def emit(self, record):
        message = self.format(record)
        message_text = Text(message)
        message_text = self.highlighter(message_text)
        log_renderable = self.render(record, message_text)

        try:
            self.console.print(log_renderable)
        except Exception:
            self.handleError(record)

    def render(self, record, message_text):
        level_no = record.levelno
        level_name = record.levelname

        output = Table.grid(padding=(0, 1))
        output.expand = True

        output.add_column()
        output.add_column(justify="left", overflow="fold", ratio=1)

        row = []
        log_time = datetime.fromtimestamp(record.created)
        text = Text()
        text.append("[", style="log.time")
        text.append(log_time.strftime(self.datefmt), style="log.time")
        text.append(" ")
        text.append(self.name, style="blue")
        text.append("]", style="log.time")

        if (level_no == logging.WARNING) or (level_no == logging.ERROR):
            text.append(" ")
            level_text = Text.styled(level_name, f"logging.level.{level_name.lower()}")
            text.append(level_text)

        row.append(text)
        row.append(message_text)

        output.add_row(*row)

        return output


if __name__ == "__main__":
    set_log_level("debug")

    log = get_logger("cvee")
    log.info("here is a info")
    log.debug("here is a debug")
    log.info("highlight number: 0.123")
    log.warning("here is a warning")
    log.error("here is a error")
    log.info("here is a very looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong log")
