import sys
from threading import Timer
from time import perf_counter_ns

from kamzik3.snippets.snippetsInterfaces import CallbackTimerInterface


class CallbackTimer(CallbackTimerInterface):
    def run(self):
        if self.with_correction:
            time_reference = perf_counter_ns()
            while not self.stopped.wait(
                self.timeout - (perf_counter_ns() - time_reference) * 1e-9
            ):
                self.callback()
                time_reference += self.timeout * 1e9
        else:
            while not self.stopped.wait(self.timeout):
                self.callback()


if sys.platform == "win32":
    # If more precise timer is requested for windows.
    # Problem of windows is that it's running on lower clock compared to Linux platform.
    # We can get only to resolution of 10ms.
    # We have to increase clock of CPU.
    # THIS CHANGES CLOCK GLOBALLY !!!!!!!!
    from kamzik3.snippets.snippetsWin32 import CallbackTimerWOC

    class PreciseCallbackTimer(CallbackTimerWOC):
        pass

else:
    # For Linux we use same timer since there is no problem with clock precision.
    # We can get up to 1us resolution.
    class PreciseCallbackTimer(CallbackTimer):
        pass


class RecallableTimer:
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        self.f(*self.args, **self.kwargs)

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()
