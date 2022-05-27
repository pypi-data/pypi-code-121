from ctypes import *
from ctypes.wintypes import DWORD
from ctypes.wintypes import UINT
import contextlib
import ctypes
from ctypes import wintypes
import sys
from time import perf_counter_ns, sleep
from kamzik3.snippets.snippetsInterfaces import CallbackTimerInterface

assert sys.platform == "win32", "OS not supported"

timeproc = WINFUNCTYPE(None, c_uint, c_uint, DWORD, DWORD, DWORD)
timeSetEvent = windll.winmm.timeSetEvent
timeKillEvent = windll.winmm.timeKillEvent


class CallbackTimerWMT(CallbackTimerInterface):
    def __init__(self, timeout, callback, with_correction=True):
        self.resolution = UINT(0)
        self.tick_function = callback
        self.periodic = True
        self.id = None
        self.calbckfn = timeproc(self.callback)
        CallbackTimerInterface.__init__(self, callback, timeout, with_correction)

    def set_timeout(self, timeout):
        self.interval = UINT(int(timeout))

    def start(self, instant=False):
        if instant:
            self.tick_function()

        self.id = timeSetEvent(
            self.interval,
            self.resolution,
            self.calbckfn,
            c_ulong(0),
            c_uint(self.periodic),
        )
        CallbackTimerInterface.start(self)

    def run(self):
        while not self.stopped.wait(0.1):
            pass
        timeKillEvent(self.id)

    def callback(self, uID, uMsg, dwUser, dw1, dw2):
        self.tick_function()

    def stop(self):
        self.stopped.set()


winmm = ctypes.WinDLL("winmm")


class TIMECAPS(ctypes.Structure):
    _fields_ = (("wPeriodMin", wintypes.UINT), ("wPeriodMax", wintypes.UINT))


def _check_time_err(err, func, args):
    if err:
        raise WindowsError("%s error %d" % (func.__name__, err))
    return args


winmm.timeGetDevCaps.errcheck = _check_time_err  # type: ignore
winmm.timeBeginPeriod.errcheck = _check_time_err  # type: ignore
winmm.timeEndPeriod.errcheck = _check_time_err  # type: ignore


@contextlib.contextmanager
def timer_resolution(msecs=0):
    caps = TIMECAPS()
    winmm.timeGetDevCaps(ctypes.byref(caps), ctypes.sizeof(caps))
    msecs = min(max(msecs, caps.wPeriodMin), caps.wPeriodMax)
    winmm.timeBeginPeriod(msecs)
    yield
    winmm.timeEndPeriod(msecs)


def set_timer_resolution(msecs=0):
    caps = TIMECAPS()
    winmm.timeGetDevCaps(ctypes.byref(caps), ctypes.sizeof(caps))
    msecs = min(max(msecs, caps.wPeriodMin), caps.wPeriodMax)
    winmm.timeBeginPeriod(msecs)


class CallbackTimerWOC(CallbackTimerInterface):
    def run(self):
        if self.with_correction:
            time_reference = perf_counter_ns()
            with timer_resolution(0):
                while not self.stopped.is_set():
                    try:
                        sleep(
                            self.timeout - (perf_counter_ns() - time_reference) * 1e-9
                        )
                    except ValueError:
                        pass
                    self.callback()
                    time_reference += self.timeout * 1e9
        else:
            with timer_resolution(0):
                while not self.stopped.is_set():
                    sleep(self.timeout)
                    self.callback()
