from threading import current_thread
from time import sleep, thread_time

import numpy as np


YIELD_TIMEOUT = np.nextafter(0, 1)


def yield_thread():
    sleep(YIELD_TIMEOUT)


def prefer_thread_yield(time: float = 0.01):
    """
    Requests to yield from current thread if runtime exceeds a certain amount of time.

    :param time:
        Time in seconds.
    """
    thread = current_thread()
    tm = thread_time()
    if hasattr(thread, '_last_threadtime_stamp'):
        if time < tm - thread._last_threadtime_stamp:
            thread._last_threadtime_stamp = tm
            yield_thread()
    else:
        thread._last_threadtime_stamp = tm
