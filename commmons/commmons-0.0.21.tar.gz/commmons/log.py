import logging
import multiprocessing

__all__ = [
    "with_prefix",
    "with_timer",
    "get_formatter",
    "init_logger_with_handlers"
]

import os
from pathlib import Path

from typing import Union

from pydash import head

FORMAT = "%(asctime)s %(levelname)-5s %(funcName)-26s %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_formatter():
    fmtr = logging.Formatter(FORMAT)
    fmtr.datefmt = DATEFMT
    return fmtr


class LockingFileHandler(logging.FileHandler):
    def __init__(self, filename):
        super().__init__(filename)

    def emit(self, record: logging.LogRecord) -> None:
        with multiprocessing.Lock():
            super().emit(record)


def init_logger_with_handlers(name: str, level: int, path: str,
                              file_handler_class=logging.FileHandler) -> logging.Logger:
    from commmons import touch

    STREAM_HANDLER_NAME = "commmons_stream_handler"
    FILE_HANDLER_NAME = "commmons_file_handler"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    os.makedirs(Path(path).parent, exist_ok=True)
    touch(path)

    shdlr = head([h for h in logger.handlers if h.name == STREAM_HANDLER_NAME])
    if not shdlr:
        shdlr = logging.StreamHandler()
        shdlr.name = STREAM_HANDLER_NAME
        logger.addHandler(shdlr)
    shdlr.setFormatter(get_formatter())

    fhdlr = head([h for h in logger.handlers if h.name == FILE_HANDLER_NAME])
    if not fhdlr:
        fhdlr = file_handler_class(path)
        fhdlr.name = FILE_HANDLER_NAME
        logger.addHandler(fhdlr)
    fhdlr.setFormatter(get_formatter())

    return logger


def with_prefix(parent_logger: Union[logging.Logger, logging.LoggerAdapter], prefix: str) -> logging.LoggerAdapter:
    class PrefixAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return '%s %s' % (self.extra['prefix'], msg), kwargs

    return PrefixAdapter(parent_logger, {'prefix': prefix})


def with_timer(parent_logger) -> logging.LoggerAdapter:
    from commmons import now_seconds

    class TimerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return 'elapsed=%s %s' % (now_seconds() - self.extra['start_time'], msg), kwargs

    return TimerAdapter(parent_logger, {'start_time': now_seconds()})
