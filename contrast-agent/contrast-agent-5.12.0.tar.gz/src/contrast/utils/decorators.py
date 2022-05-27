# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
from contextlib import contextmanager
import logging as stdlib_logging

import contrast
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.timer import now_ms_float
from contrast.utils.loggers import TRACE_LEVEL
from contrast.extern import structlog as logging
from contrast.agent.validator import ValidationException

logger = logging.getLogger("contrast")

DEBUG_LEVEL = stdlib_logging.DEBUG


def _log_extra_safely(
    log_message: str, error: Exception, original_func, args, kwargs, log_level="debug"
):
    if not contrast.telemetry_disabled():
        TELEMETRY = contrast.TELEMETRY
    else:
        TELEMETRY = None

    try:
        full_msg = log_message + ": " + str(error)
        getattr(logger, log_level)(full_msg, exc_info=error)
        logger.debug("wrapped function args: %s", args)
        logger.debug("wrapped function kwargs: %s", kwargs)

        if TELEMETRY is not None:
            TELEMETRY.report_error(
                error=error, original_func=original_func, message=full_msg
            )
    except ValidationException as val_ex:
        logger.debug(f"Cannot report error to Telemetry: {str(val_ex)}")
    except Exception:
        # For complete safety, we're not going to try to log the logging error
        # because sometimes the logging error is actually an error (such as a recursive
        # error) within the logging module itself!
        pass


def fail_loudly(log_message, log_level="exception", return_value=None):
    """
    Decorator that will run the decorated function/method and, if
    an exception is raised, return a safe value and log the error.

    Note that SecurityException will always be re-raised.

    :param log_message: message to log in case of failure
    :param log_level: level to log in case of failure
    :param return_value: safe value to return in case of failure
    :return: original func return or return_value
    """

    def wrap(original_func):
        def run_safely(*args, **kwargs):
            try:
                return original_func(*args, **kwargs)
            except SecurityException:
                raise
            except Exception as ex:
                _log_extra_safely(
                    log_message, ex, original_func, args, kwargs, log_level
                )
                if os.environ.get("CONTRAST_TESTING"):
                    raise

            return return_value

        return run_safely

    return wrap


def log_time(log_message):
    """
    Decorator that will TRACE log before some method/func runs,
    run the function, log after, and finally log the elapsed time.
    """

    def wrap(original_func):
        def _log_time(*args, **kwargs):
            # Don't do any work if logger is not TRACE.
            if logger.level > TRACE_LEVEL:
                return original_func(*args, **kwargs)

            # Since we can't grab the "time" value from the trace log msg,
            # we compute the time ourselves. This means there will be a tiny,
            # probably insignificant difference between the logging message and the
            # time calculation.
            logger.trace("start %s", log_message)

            start = now_ms_float()
            return_value = original_func(*args, **kwargs)
            end = now_ms_float()

            logger.trace("end %s", log_message)

            elapsed_time = end - start

            logger.trace("elapsed time ms %s", log_message, elapsed_time=elapsed_time)

            return return_value

        return _log_time

    return wrap


@contextmanager
def log_time_cm(log_message):
    """
    Context manager for DEBUG and TRACE level logging.
    If logger is using:
        DEBUG LEVEL: log start, do work, log end at debug level
        TRACE LEVEL: log start, keep time, do work, log end, log elapsed time at
            trace level
        ANY OTHER LEVEL: just do work
    """
    if logger.level > DEBUG_LEVEL:
        yield

    elif logger.level is DEBUG_LEVEL:
        logger.debug("start %s", log_message)
        try:
            yield
        finally:
            logger.debug("end %s", log_message)

    elif logger.level is TRACE_LEVEL:
        logger.trace("start %s", log_message)
        start = now_ms_float()
        try:
            yield
        finally:
            end = now_ms_float()

            logger.trace("end %s", log_message)

            elapsed_time = end - start

            logger.trace("elapsed time ms %s", log_message, elapsed_time=elapsed_time)


def fail_quietly(log_message, return_value=None):
    """
    Similar to fail_loudly (see above)

    This decorator is intended to handle cases where an exception may occur but won't
    disrupt normal operation of the agent. This decorator should be used to protect
    against external exceptions we can't prevent but still want to handle.

    In these cases, we log an error message and the exception traceback, both at DEBUG
    level.
    """

    def wrap(original_func):
        def run_safely(*args, **kwargs):
            try:
                return original_func(*args, **kwargs)
            except SecurityException:
                raise
            except Exception as ex:
                _log_extra_safely(log_message, ex, original_func, args, kwargs)
                if os.environ.get("CONTRAST_TESTING"):
                    raise
            return return_value

        return run_safely

    return wrap


class cached_property(object):
    """
    https://github.com/pydanny/cached-property
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
