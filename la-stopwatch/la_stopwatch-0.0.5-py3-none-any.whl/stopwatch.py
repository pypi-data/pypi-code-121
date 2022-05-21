from datetime import timedelta
from time import time_ns

from la_stopwatch.stopwatch_ns import StopwatchNS


class Stopwatch(StopwatchNS):
    def duration(self) -> timedelta:
        return timedelta(microseconds=(time_ns() - self._start) / 1000)
