import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

from psutil import Process


def get_logger(
    name: Optional[str] = None,
    log_level: Optional[Union[str, int]] = None,
    show_file_path: Optional[bool] = None,
    file_dir: Optional[str] = None,
    max_bytes: int = 20_000_000,
    backup_count: int = 2,
) -> Logger:
    """Configure a logger.

    Args:
        name (Optional[str], optional): Name for the logger. Included in log string prefix. Defaults to None.
        level (Optional[Union[str, int]], optional): Logging level -- CRITICAL: 50, ERROR: 40, WARNING: 30, INFO: 20, DEBUG: 10. Defaults to f"{name.upper()}_LOG_LEVEL" environment variable or INFO.
        file (Optional[Union[bool, str]], optional): File to write logs to. If True, logs will be written to a file in user's home directory. Defaults to f"{name.upper()}_FILE" environment variable or None.
        show_file_path (Optional[bool], optional): Show complete file path in log string prefix, rather than just filename. Defaults to level == DEBUG.

    Returns:
        Logger: The configured logger.
    """
    # create a new logger or return a reference to an already configured logger.
    logger = logging.getLogger(name)
    # if this is not the first call, the logger will already have handlers.
    if logger.handlers:
        return logger

    # determine variable values.
    if log_level is None:
        if name:
            log_level = os.getenv(f"{name.upper()}_LOG_LEVEL")
        log_level = log_level or os.getenv("READY_LOGGER_LOG_LEVEL", logging.INFO)
    if show_file_path is None:
        if name:
            show_file_path = os.getenv(f"{name}_SHOW_FILE_PATH")
        show_file_path = show_file_path or os.getenv("READY_LOGGER_SHOW_FILE_PATH")
    if file_dir is None:
        if name:
            file_dir = os.getenv(f"{name}_FILE_DIR")
        file_dir = file_dir or os.getenv("READY_LOGGER_FILE_DIR")
    if max_bytes is None:
        if name:
            max_bytes = os.getenv(f"{name}_MAX_BYTES")
        max_bytes = max_bytes or os.getenv("READY_LOGGER_MAX_BYTES")
    if backup_count is None:
        if name:
            backup_count = os.getenv(f"{name}_BACKUP_COUNT")
        backup_count = backup_count or os.getenv("READY_LOGGER_BACKUP_COUNT")

    # set log level.
    if isinstance(log_level, str):
        log_level = logging.getLevelName(log_level.upper())
    logger.setLevel(log_level)

    # set formatting and handling.
    file_name_fmt = "pathname" if show_file_path else "filename"
    formatter = logging.Formatter(
        f"[%(asctime)s][%(levelname)s]{'[%(name)s]' if name else ''}[%({file_name_fmt})s:%(lineno)d] %(message)s"
    )
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if file_dir:
        stem = name or f"{(p := Process(os.getpid())).name()}_{p.pid}"
        file = Path(file_dir) / f"{stem}.log"
        # create log directory if it doesn't currently exist.
        file.parent.mkdir(exist_ok=True, parents=True)
        # add file handler.
        file_handler = RotatingFileHandler(
            file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # don't duplicate log messages.
    logger.propagate = False

    return logger
