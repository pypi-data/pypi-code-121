import sys
import time


def seconds_to_int_nano_seconds(seconds):
    '''
    Used to convert time.time() from seconds to nanoseconds.
    Note that Python>=3.7 has time.time_ns() that returns exactly the time in nanoseconds. We use this function for
    backwards compatibility.
    '''
    return int((10 ** 9) * seconds)


def milliseconds_to_int_nano_seconds(milliseconds):
    return int((10 ** 6) * milliseconds)


'''
This trick here allows to check the python version only once when the module is loaded,
and call get_most_accurate_time_stamp_nano_seconds() to find what is the time stamp.
'''
if sys.version_info >= (3, 7):
    get_most_accurate_time_stamp_nano_seconds = lambda: time.perf_counter_ns()
elif sys.version_info >= (3, 3):
    get_most_accurate_time_stamp_nano_seconds = lambda: seconds_to_int_nano_seconds(time.perf_counter())
else:
    get_most_accurate_time_stamp_nano_seconds = lambda: seconds_to_int_nano_seconds(time.time())
