"""
function-level manipulation
"""

import sys
import time
from typing import Callable, Union


__all__ = ['profile_runtime', 'RecurseLimit']


def profile_runtime(callback: Callable, sleep: Union[float, int] = None):
    import cProfile
    import pstats
    profiler = cProfile.Profile()
    profiler.enable()
    callback()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    if sleep:    # Sometimes, the top rows in `print_states` are now shown properly
        time.sleep(sleep)
    stats.print_stats()


class RecurseLimit:
    # credit: https://stackoverflow.com/a/50120316/10732321
    def __init__(self, limit):
        self.limit = limit

    def __enter__(self):
        self.old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.limit)

    def __exit__(self, kind, value, tb):
        sys.setrecursionlimit(self.old_limit)
