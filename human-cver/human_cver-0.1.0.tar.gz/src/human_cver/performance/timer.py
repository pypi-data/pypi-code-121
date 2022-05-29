import time


class Timer(object):
    def __init__(self) -> None:

        self._total_time = 0.0
        self._count = 0
        self._start = None

    def tic(self) -> None:
        self._start = time.time()

    def toc(self) -> float:
        t = 0.0
        if self._start is not None:
            t = time.time() - self._start
            self._start = None

        self._total_time += t
        self._count += 1
        return t

    def total(self) -> float:
        """total time"""
        return self._total_time

    def count(self) -> int:
        return self._count

    def fps(self) -> float:
        if self._count == 0:
            return 0.0
        return self._count / self._total_time
