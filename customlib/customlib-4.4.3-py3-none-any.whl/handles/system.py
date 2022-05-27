# -*- coding: UTF-8 -*-

from ctypes import windll

from ..constants import ES


class OsSleepInhibitor(object):
    """
    Prevent OS from sleep/hibernate.

    Documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx
    """

    @staticmethod
    def _set_thread_execution_state(*args, **kwargs):
        windll.kernel32.SetThreadExecutionState(*args, **kwargs)

    def __init__(self, keep_screen_awake: bool = False):
        self._keep_screen_awake = keep_screen_awake

    def __enter__(self):
        self.acquire(self._keep_screen_awake)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self, keep_screen_awake: bool = False):
        """Prevents windows from entering sleep mode."""
        flags = ES.CONTINUOUS | ES.SYSTEM_REQUIRED

        if keep_screen_awake:
            flags |= ES.DISPLAY_REQUIRED

        # log.debug("Inhibit (prevent) suspend mode")
        self._set_thread_execution_state(flags)

    def release(self):
        """Resets the flags and allows windows to enter sleep mode."""
        # log.debug("Uninhibited (allow) suspend mode.")
        self._set_thread_execution_state(ES.CONTINUOUS)
