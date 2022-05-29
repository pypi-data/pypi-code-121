#!/usr/bin/env python
import time
from abc import abstractclassmethod
from functools import wraps

from codefast.logger import Logger

logger = Logger()


class Cleaner(object):
    def __init__(self, e, f) -> None:
        self.error = e
        self.func = f

    @abstractclassmethod
    def handle(self):
        pass


class ErrorMessagerPoster(Cleaner):
    """ keep error message to log and sent a copy.
    """

    def __init__(self, e, f) -> None:
        super().__init__(e, f)

    def handle(self):
        """ Need a poster to send error message.
        """
        fi = FunctionInspector(self.func)
        logger.error(str(fi))
        self.poster.post(str(fi))


class FunctionInspector(object):
    def __init__(self, e, f):
        self.e = e
        self.f = f

    def __str__(self) -> str:
        return 'Error message : {}, function_name : {}'.format(
            str(self.e), self.f.__name__)


class RaiseException(Cleaner):
    def __init__(self, e, f) -> None:
        super().__init__(e, f)

    def handle(self):
        fi = FunctionInspector(self.error, self.func)
        logger.error(str(fi))
        raise self.error


def retry(total_tries=3,
          initial_wait=0.5,
          backoff_factor=2,
          CleanerType: Cleaner = RaiseException, messger_poster=None):
    """calling the decorated function applying an exponential backoff.
    Args:
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
        cleaner: Cleaner function to call after all try failed
    """
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries, initial_wait
            while _tries > 0:
                try:
                    msg = f'{f.__name__} {total_tries - _tries} try.'
                    logger.info(msg)
                    return f(*args, **kwargs)
                except Exception as e:
                    _tries -= 1
                    if _tries == 0:
                        msg = "Fuction [{}] failed after {} tries".format(
                            f.__name__, total_tries)
                        logger.error(msg)
                        cleaner = CleanerType(e, f)
                        if messger_poster:
                            cleaner.poster = messger_poster
                        cleaner.handle()
                        return
                    else:
                        fi = FunctionInspector(e, f)
                        msg = str(fi) + \
                            ' retrying in {} seconds...'.format(_delay)
                        logger.warning(msg)
                        time.sleep(_delay)
                        _delay *= backoff_factor

        return func_with_retries

    return retry_decorator

