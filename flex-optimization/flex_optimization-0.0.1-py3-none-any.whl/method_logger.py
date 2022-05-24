"""
Logger

The logger can be used to track how a string is transformed through the parsing.
Default level is warning.

warning: will only let you know if text any text is ignored in the parsing.
info: will show the major parsing steps.
debug: will show fine grain parsing steps.

"""

import logging
from functools import wraps
from typing import Union

color_codes = {
    "reset": "\033[0m",  # add at the end to stop coloring
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

BOLD_SEQ = "\033[1m"


def add_logging_level(level_name: str, level_num: int):
    """
    Adds a new logging level to the `logging` module and the
    currently configured logging class.

    """
    method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError('{} already defined in logging module'.format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError('{} already defined in logging module'.format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError('{} already defined in logger class'.format(method_name))

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


class LogFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')

    def format(self, record):
        # Save the original format configured by the user when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = f"\t{color_codes['cyan']}%(msg)s{color_codes['reset']}"
        elif record.levelno == logging.MONITOR:
            self._style._fmt = f"\t{color_codes['white']}%(msg)s{color_codes['reset']}"
        elif record.levelno == logging.INFO:
            self._style._fmt = f"{color_codes['green']}%(msg)s{color_codes['reset']}"
        elif record.levelno == logging.WARNING:
            self._style._fmt = f"{color_codes['yellow']}%(msg)s {color_codes['reset']}"
        elif record.levelno == logging.ERROR:
            self._style._fmt = f"{color_codes['magenta']}ERROR: %(msg)s {color_codes['reset']}"
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = f"{color_codes['red']}ERROR: %(msg)s {color_codes['reset']}"

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


add_logging_level('MONITOR', logging.INFO - 5)

logger = logging.getLogger("method")

logging_levels = dict(
    CRITICAL=50,
    FATAL="CRITICAL",
    ERROR=40,
    WARNING=30,
    WARN="WARNING",
    INFO=20,
    MONITOR=15,
    DEBUG=10,
    NOTSET=0)

for name, value in logging_levels.items():
    setattr(logger, name, value)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(LogFormatter())
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)


# Logger decorators
def log_debug(func):
    """ Add 'input --> output' logging to a function. At DEBUG level. """

    @wraps(func)
    def _log_debug(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__}: {args} --> {result}")
        return result

    return _log_debug


def log_info(func):
    """ Add 'input --> output' logging to a function. At INFO level. """

    @wraps(func)
    def _log_info(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__}: {args} --> {result}")
        return result

    return _log_info


def sig_figs(number: Union[float, int], sig_digit: int = 3) -> Union[int, float]:
    """ significant figures
    Given a number return a string rounded to the desired significant digits.
    Parameters
    ----------
    number: float, int
        number you want to reduce significant figures on
    sig_digit: int
        significant digits
    Returns
    -------
    number: int, float
    """
    if isinstance(number, float):
        return float('{:.{p}g}'.format(number, p=sig_digit))
    elif isinstance(number, int):
        return float('{:.{p}g}'.format(number, p=sig_digit))
    else:
        raise TypeError(f"'sig_figs' only accepts int or float. Given: {number} (type: {type(number)}")