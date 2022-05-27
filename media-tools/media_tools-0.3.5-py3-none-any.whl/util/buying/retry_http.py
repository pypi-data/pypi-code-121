__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

from functools import wraps
import time
from urllib.error import HTTPError

MAX_TIMES_TRY = 2
WAIT_RETRY_SECS = 0.1


def retry_http(
        max_times_try: int = MAX_TIMES_TRY, silent: bool = True,
        wait_retry_secs: float = WAIT_RETRY_SECS, wait_retry_progressive: bool = False
):

    def actual_decorator(method):
        @wraps(method)
        def allow_fail(self, *args, **kwargs):
            wait_retry = wait_retry_secs
            for i in range(1, max_times_try + 1):
                try:
                    return method(self, *args, **kwargs)
                except HTTPError as error:
                    if not silent:
                        print(
                            f'{type(self).__name__}.{method.__name__}() {error.code}: {error.msg} '
                            f'failed {i} / {max_times_try} times'
                        )
                    if i < max_times_try:
                        time.sleep(wait_retry)
                        if wait_retry_progressive:
                            wait_retry *= 2
            return False

        return allow_fail

    return actual_decorator
