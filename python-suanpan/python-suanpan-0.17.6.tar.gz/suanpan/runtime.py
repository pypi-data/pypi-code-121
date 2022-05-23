# coding=utf-8
from __future__ import absolute_import, print_function

import os
import functools
import time
import traceback

import gevent
import retrying
import timeout_decorator

from suanpan.log import logger


def needRetryException(exception):
    return not isinstance(exception, (KeyboardInterrupt, SystemExit))


def retryRunner(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Run failed and retrying: {func.__name__}")
            logger.warning(traceback.format_exc())
            raise e

    return _dec


def retry(*args, **kwargs):
    def _wrap(func):
        kwargs.update(wrap_exception=True, retry_on_exception=needRetryException)
        _retry = retrying.retry(*args, **kwargs)
        _func = _retry(retryRunner(func))

        @functools.wraps(func)
        def _dec(*fargs, **fkwargs):
            try:
                return _func(*fargs, **fkwargs)
            except retrying.RetryError as e:
                _, error, _ = e.last_attempt.value
                if needRetryException(error):
                    rfunc = func.func if isinstance(func, functools.partial) else func
                    rfuncname = getattr(rfunc, "__name__", "unknown_func")
                    logger.error(
                        f"Retry failed after {e.last_attempt.attempt_number} attempts: {rfuncname}"
                    )
                    raise e
                raise error from e

        return _dec

    return _wrap


def globalrun(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.debug("User canceled and exit 0.")
            os._exit(0)  # pylint: disable=protected-access
        except gevent.GreenletExit:
            logger.debug("Gevent Runner Killed.")
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error(traceback.format_exc())
            raise e

    return _dec


def processrun(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        try:
            func(*args, **kwargs)
            os._exit(0)  # pylint: disable=protected-access
        except KeyboardInterrupt:
            logger.debug("User canceled and exit 0.")
            os._exit(0)  # pylint: disable=protected-access
        except gevent.GreenletExit:
            logger.debug("Gevent Runner Killed.")
            os._exit(1)  # pylint: disable=protected-access
        except Exception:  # pylint: disable=broad-except
            logger.error(traceback.format_exc())
            os._exit(1)  # pylint: disable=protected-access

    return _dec


def saferun(func, default=None):
    @functools.wraps(func)
    def _dec(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.debug("User canceled and exit 0.")
            os._exit(0)  # pylint: disable=protected-access
        except Exception:  # pylint: disable=broad-except
            logger.warning(f"Ignore Error: \n{traceback.format_exc()}")
            return default

    return _dec


def costrun(title):
    def _dec(func):
        @functools.wraps(func)
        def _wrap(*args, **kwargs):
            logger.debug(f"{title} - Start")
            startTime = time.time()
            try:
                result = func(*args, **kwargs)
                endTime = time.time()
                costTime = (endTime - startTime) * 1000
                logger.debug(f"{title} - Done - {costTime:.3f}ms")
                return result
            except Exception:  # pylint: disable=broad-except
                endTime = time.time()
                costTime = round(endTime - startTime, 6) * 1000
                logger.error(f"{title} - Error - {costTime:.3f}ms")
                raise

        return _wrap

    return _dec


timeout = timeout_decorator.timeout
