"""Utility functions for the runner modules."""
from datetime import datetime
import logging
import os
from pathlib import Path
import sys
from typing import List, Optional

from bitfount.config import BITFOUNT_LOGS_DIR

logger = logging.getLogger(__name__)


def setup_loggers(
    loggers: List[logging.Logger], name: Optional[str] = None
) -> List[logging.Logger]:
    """Set up loggers with console and file handlers.

    Creates a logfile in 'logs' directory with the current date and time and outputs all
    logs at the "DEBUG" level. Also outputs logs to stdout at the "INFO" level. A common
    scenario is to attach handlers only to the root logger, and to let propagation take
    care of the rest.

    Args:
        loggers (List[logging.Logger]): logger(s) to setup
        name (Optional[str], optional): creates a subdirectory inside BITFOUNT_LOGS_DIR
            if provided. Defaults to None.

    Returns:
        List[logging.Logger]: updated logger(s)
    """
    handlers: List[logging.Handler] = []

    # Check if logging to file is not disabled
    if os.environ.get("BITFOUNT_LOG_TO_FILE", "true") == "true":
        # Create directory if it doesn't exist
        parent_logfile_dir = (
            Path(os.environ.get("BITFOUNT_LOGS_DIR", ".")) / BITFOUNT_LOGS_DIR
        )
        logfile_dir = parent_logfile_dir if not name else parent_logfile_dir / name
        logfile_dir.mkdir(parents=True, exist_ok=True)

        # Set file logging configuration
        file_handler = logging.FileHandler(
            f"{logfile_dir}/{datetime.now():%Y-%m-%d-%H%M%S}.log"
        )
        file_log_formatter = logging.Formatter(
            "%(asctime)s %(thread)-12d [%(levelname)-8s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_log_formatter)
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)

    # Set console logging configuration
    console_handler = logging.StreamHandler(sys.stdout)
    console_log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_log_formatter)
    console_handler.setLevel(logging.INFO)
    handlers.append(console_handler)

    # Cannot use `logger` as iter-variable as shadows outer name.
    for i_logger in loggers:
        # Clear any existing configuration
        list(map(i_logger.removeHandler, i_logger.handlers))
        list(map(i_logger.removeFilter, i_logger.filters))

        # Set base level to DEBUG and ensure messages are not duplicated
        i_logger.setLevel(logging.DEBUG)
        i_logger.propagate = False

        # Add handlers to loggers
        list(map(i_logger.addHandler, handlers))

    return loggers
