from contextlib import ContextDecorator
from time import perf_counter


class Timer(ContextDecorator):
    def __init__(self, start=True, print_tmpl=None, logger=None):
        self.print_tmpl = print_tmpl if print_tmpl is not None else "{:.4f}"
        self.logger = logger

        self._is_paused = False
        self._total_paused = 0

        if start:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        print(self.print_tmpl.format(self.check()))

    def start(self):
        if not self._is_paused:
            self._start = perf_counter()
        else:
            self._total_paused += perf_counter() - self._last
        self._last = perf_counter()
        self._is_paused = False

    def check(self):
        dur = perf_counter() - self._last
        self._last = perf_counter()
        return dur

    def pause(self):
        self._last = perf_counter()
        dur = perf_counter() - self._last
        self._is_paused = True
        return dur

    def seconds(self):
        if self._is_paused:
            end_time = self._last
        else:
            end_time = perf_counter()
        return end_time - self._start - self._total_paused


if __name__ == "__main__":
    import time

    timer = Timer()
    time.sleep(0.5)
    print(timer.check())

    with Timer():
        time.sleep(0.5)

    with Timer(print_tmpl="it takes {:.2f} seconds"):
        time.sleep(0.5)

    timer = Timer(start=False)
    for i in range(5):
        timer.start()
        time.sleep(0.2)
        timer.pause()
        time.sleep(0.2)
    print(timer.seconds())

    timer = Timer(start=False)
    for i in range(5):
        timer.start()
        time.sleep(0.2)
        timer.pause()
        time.sleep(0.2)
    timer.start()
    time.sleep(0.2)
    print(timer.seconds())

    @Timer(print_tmpl="it takes {:.2f} seconds")
    def foo():
        time.sleep(0.5)

    foo()
