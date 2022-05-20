# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Implement functions that help with adding timing information to different methods and functions."""

import time
import functools
import logging


def timeit(message=None):
    def timeit_decorator(method):
        """A decorator function that takes a method/function and computes the the elapsed time

        :param method: a method/function
        :return: the elapsed_time
        """
        @functools.wraps(wrapped=method)
        def elapsed_time(*args, **kwargs):
            nonlocal message
            start_time = time.time()
            result = method(*args, **kwargs)
            end_time = time.time()
            time_diff = end_time - start_time
            # because we only show 2 digits after the floating point, we skip the message if the time taken is less
            # than 0.01 seconds
            if time_diff > 0.01:
                if not message:  # pragma: no cover
                    message = "run " + method.__name__
                logging.info('Timer: it took {0:.2f} seconds to {1}'.format(time_diff, message))
            return result
        return elapsed_time
    return timeit_decorator
