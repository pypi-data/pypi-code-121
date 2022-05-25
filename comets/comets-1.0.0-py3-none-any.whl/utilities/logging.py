# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import logging
import os
from contextlib import redirect_stdout, contextmanager, ExitStack


class CustomFormatter(logging.Formatter):
    """
    Formatter used for defining the format of logging messages
    """

    debug_format = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s  - %(lineno)d - %(message)s"
    info_format = "%(asctime)s - %(message)s"
    warning_format = "%(asctime)s - %(levelname)s - %(message)s"
    error_format = "%(asctime)s - %(levelname)s - %(module)s - %(filename)s - %(lineno)d - %(message)s"

    debug_fmt = logging.Formatter(debug_format)
    info_fmt = logging.Formatter(info_format)
    warning_fmt = logging.Formatter(warning_format)
    error_fmt = logging.Formatter(error_format)

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        super(CustomFormatter, self).__init__(fmt)

    def format(self, record):  # pragma: no cover
        if record.levelno == logging.DEBUG:
            return self.debug_fmt.format(record)
        elif record.levelno == logging.INFO:
            return self.info_fmt.format(record)
        elif record.levelno == logging.WARNING:
            return self.warning_fmt.format(record)
        elif record.levelno == logging.ERROR:
            return self.error_fmt.format(record)


def has_handlers(logger):
    """
    See if this logger has any handlers already configured.
    Loop through all handlers in the logger hierarchy until a logger with the "propagate" attribute set to zero is found.

    Returns
    -------
    bool
        True if the logger or any parent logger has handlers.
    """
    current_logger = logger
    has_handler = False
    while current_logger:
        if current_logger.handlers:
            has_handler = True
            break  # pragma: no cover
        if not current_logger.propagate:
            break  # pragma: no cover
        else:
            current_logger = current_logger.parent
    return has_handler


def get_logger(name):
    """
    Get the logger with the corresponding name and set its logging level

    Args:
        name : The name of the logger.

    Returns
    -------
    logger : Logger object
        The logger object.
    """
    logger = logging.getLogger(name)

    # Set the logging level to the environment variable cometsloglevel
    if 'COMETSLOGLEVEL' in os.environ:
        logger.setLevel(int(os.environ['COMETSLOGLEVEL']))

    # Adding handlers to the logger if they are not present, which may happen in processes that run in parallel
    if not has_handlers(logger):
        sh = logging.StreamHandler()
        sh.setFormatter(CustomFormatter())
        logger.addHandler(sh)

    return logger


def set_logging_level(loglevel):
    """
    Set the global logging level of the logger

    Args:
        loglevel : {"debug", "info", "warning", "error"}
            Set the threshold for the logging level. Logging messages less severe
            than this level will be ignored. Default logger level is "warning".

    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    os.environ['COMETSLOGLEVEL'] = str(numeric_level)


@contextmanager
def suppressstdout(out=True):  # pragma: no cover
    # Context manager for supressing the standard output stream
    # Used because we usually don't want a model or an external library running many times to send output to stdout
    with ExitStack() as stack:
        with open(os.devnull, "w") as null:
            if out:
                stack.enter_context(redirect_stdout(null))
            yield


# Set default logging level to "warning"
set_logging_level("warning")
