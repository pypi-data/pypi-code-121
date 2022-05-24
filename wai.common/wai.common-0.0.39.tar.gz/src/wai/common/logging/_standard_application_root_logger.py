"""
Module containing tools for creating a standard root logger, for
when you don't want to think about how to add logging to your application.
"""
import logging
import sys
from typing import Callable

# The names for the default handlers
DEBUG_HANDLER_NAME = "debug_handler"
INFO_HANDLER_NAME = "info_handler"
WARNING_HANDLER_NAME = "warning_handler"
ERROR_HANDLER_NAME = "error_handler"


def exact_level_filter(level: int) -> Callable[[logging.LogRecord], bool]:
    """
    Creates a filter function which only allows records with a
    specified level though.

    :param level:   The level to filter for.
    :return:        The filter function.
    """
    def filter_function(record: logging.LogRecord) -> bool:
        return record.levelno == level

    return filter_function


def create_standard_handler(std_out: bool,
                            name: str,
                            level: int,
                            format_string: str,
                            exact_level: bool = True) -> logging.StreamHandler:
    """
    Creates a standard handler for printing log messages to
    either std-out or std-err.

    :param std_out:         Whether std-out should be used for printing. If False,
                            std-err is used instead.
    :param name:            The handler's name.
    :param level:           The level of message the handler should handle.
    :param format_string:   The format string for the log messages, in '{' style.
    :param exact_level:     Whether the handler should only handle records of an
                            exact level.
    :return:                The handler.
    """
    # Configure the handler
    handler = logging.StreamHandler(sys.stdout if std_out else sys.stderr)
    handler.name = name
    handler.setLevel(level)
    if exact_level:
        handler.addFilter(exact_level_filter(level))

    # Add the message format
    formatter = logging.Formatter(format_string, style="{")
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)

    return handler


def create_standard_application_root_logger() -> logging.Logger:
    """
    Sets up a standard root logger and returns it. If the root
    logger has already been configured, issues a warning but leaves
    the logger unchanged.

    :return:        The root logger.
    """
    # Get the root logger
    logger = logging.getLogger()

    # If the logger already has been configured, warn and abort
    if len(logger.handlers) > 0:
        logger.warning("Attempted to reconfigure root logger")
        return logger

    # Create a debug handler to print debug info to std-out
    debug_handler = create_standard_handler(
        True,
        DEBUG_HANDLER_NAME,
        logging.DEBUG,
        "{levelname:8} {created:023} - {name} - {lineno} - {funcName} - {pathname}\n"
        "{message}"
    )

    # Create an info handler to print info messages to std-out
    info_handler = create_standard_handler(
        True,
        INFO_HANDLER_NAME,
        logging.INFO,
        "{levelname:8} {asctime:23} - {name} - {message}"
    )

    # Create a warning handler to print warning messages to std-err
    warning_handler = create_standard_handler(
        False,
        WARNING_HANDLER_NAME,
        logging.WARNING,
        "{levelname:8} {asctime:23} - {name} - {message}"
    )

    # Create a final handler to print all error/critical messages to std-err
    error_handler = create_standard_handler(
        False,
        ERROR_HANDLER_NAME,
        logging.ERROR,
        "{levelname:8} {asctime:23} - {name} - {message}",
        False
    )

    # Add the handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)

    # Set the main logger to warning level
    logger.setLevel(logging.WARNING)

    return logger
