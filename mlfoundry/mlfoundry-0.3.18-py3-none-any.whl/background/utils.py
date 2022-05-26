from __future__ import print_function

import abc
import logging
import os
import threading
from timeit import default_timer
from types import TracebackType
from typing import Optional, Tuple, Type, Union

ExceptionType = Union[
    Tuple[Type[BaseException], BaseException, TracebackType],
    Tuple[None, None, None],
]

logger = logging.getLogger(__name__)


class BackgroundJob(threading.Thread):
    """
    Base class for background jobs in a MlFoundryRun

    Attributes:
        name: name of the thread
        interval: time in seconds to sleep between calls to `self._loop` i.e. between iterations
        _wake_up_event: threading.Event that can be set to wake the thread up from sleep between iterations
        _interrupted: loop until this flag is set to True. initialised to False
    """

    name_prefix = "MLFUnnamedThread"

    def __init__(self, name: str, interval: float) -> None:
        """
        Args:
            name: name of the thread
            interval: time in seconds to sleep between calls to `self._loop` i.e. between iterations
        """
        super().__init__(name=name, daemon=True)
        self.interval = interval
        self._wake_up_event = threading.Event()
        self._interrupted = False

    def run(self) -> None:
        """
        Call `self._loop` every `interval` seconds till `self._interrupted` is set to True and call `self._finish`
        before returning
        """
        execution_time = self.interval  # to run immediately at start
        while not self._interrupted:
            if self.interval > 0 and not self._interrupted:
                timeout = max(0.0, self.interval - execution_time)
                self._wake_up_event.wait(timeout=timeout)
                self._wake_up_event.clear()
            start = default_timer()
            try:
                self._loop()
            except Exception as e:
                logger.warning(
                    f"Thread {self.name} encountered an internal error: {str(e)}"
                )
                # TODO (chiragjn): We should have a tolerance counter after which we should break out of the loop
            execution_time = default_timer() - start
        self._finish()

    @abc.abstractmethod
    def _loop(self):
        """
        Method body to call every `self.interval` seconds
        """
        raise NotImplementedError

    def _finish(self):
        """
        Method body to call before returning from Thread's run. Useful for cleaning up state.
        """
        pass

    def disable_sleep(self) -> None:
        """
        Disable sleeping between consecutive calls to `self._loop`
        """
        self.interval = 0

    def interrupt(self) -> None:
        """
        Set `self._interrupted` to True causing the run loop to break and trigger `self._finish`
        """
        self._interrupted = True
        self.wake_up()

    def wake_up(self) -> None:
        """
        Wake up the thread from its sleep between consecutive calls to `self._loop`
        """
        self._wake_up_event.set()

    def stop(self, disable_sleep: bool = False, timeout: Optional[int] = None) -> None:
        """
        Interrupt, wake up and wait for thread to finish by joining for `timeout` seconds

        Args:
            disable_sleep: if to disable sleep between consecutive calls to `self._loop`
            timeout: time in seconds to wait while joining the thread
        """
        if self.is_alive():
            if disable_sleep:
                self.disable_sleep()
            self.wake_up()
            self.interrupt()
            self.join(timeout)


def make_log(message: str) -> str:
    """
    Add process pid and thread name as prefix to `message`
    Args:
        message: message to prepend to

    Returns:
        str: message with process pid and thread name as prepended
    """
    # TODO (chiragjn): Maybe just configure a logging.Handler with a logging.Formatter?
    return f"pid={os.getpid()} thread={threading.currentThread().getName()} {message}"
