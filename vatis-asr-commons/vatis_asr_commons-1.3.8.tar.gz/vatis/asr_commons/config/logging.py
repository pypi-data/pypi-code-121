import functools
import logging
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from inspect import signature

# configuration
from threading import RLock
from typing import Optional

FORMATTER = logging.Formatter("%(asctime)s — %(threadName)s — %(process)d — %(name)s — %(levelname)s — %(message)s")
LOGS_FILE = 'logs/app.logs'
CONSOLE_LOGGING: bool = True
FILE_LOGGING: bool = False

_execution_time_logger: logging.Logger


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOGS_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, console_logging: bool = CONSOLE_LOGGING,
               file_logging: bool = FILE_LOGGING) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough

    if console_logging:
        logger.addHandler(get_console_handler())

    if file_logging:
        logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


def execution_time(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)

            _execution_time_logger.info(
                f'Successfully executed {func.__name__} in {str(time.time() - start_time)} seconds')

            return result
        except Exception as e:
            _execution_time_logger.info(
                f'Exception raised in {func.__name__} after {str(time.time() - start_time)} seconds')
            raise e

    return _wrapper


_execution_time_logger = get_logger('execution_time_profiler')
