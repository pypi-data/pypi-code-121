# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Callable, Optional


def _log_traceback(
    exception: BaseException,
    logger: logging.Logger,
    override_error_msg: Optional[str] = None,
    is_critical: Optional[bool] = True,
    tb: Optional[Any] = None,
) -> None:
    """
    Log exception traces.

    :param exception: The exception to log.
    :param logger: The logger to use.
    :param override_error_msg: The message to display that will override the current error_msg.
    :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
    :param tb: The traceback to use for logging; if not provided, the one attached to the exception is used.
    """
    if logger is None:
        logger = logging.getLogger()

    if override_error_msg is not None:
        error_msg = override_error_msg
    else:
        error_msg = str(exception)

    if is_critical:
        logger.critical(error_msg, exc_info=exception)
    else:
        logger.error(error_msg, exc_info=exception)


def install_custom_log_traceback(
    func: Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
) -> None:
    global current_log_traceback
    current_log_traceback = func


def log_traceback(
    exception: BaseException,
    logger: logging.Logger,
    override_error_msg: Optional[str] = None,
    is_critical: Optional[bool] = True,
    tb: Optional[Any] = None,
) -> None:
    """
    Log exception traces.

    :param exception: The exception to log.
    :param logger: The logger to use.
    :param override_error_msg: The message to display that will override the current error_msg.
    :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
    :param tb: The traceback to use for logging; if not provided, the one attached to the exception is used.
    """
    current_log_traceback(exception, logger, override_error_msg, is_critical, tb)


current_log_traceback = _log_traceback
