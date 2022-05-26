from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable, List

if TYPE_CHECKING:
    from sila2.server import SilaServer


_STOP_THREAD_CHECK_PERIOD: float = 0.1


class FeatureImplementationBase:
    parent_server: SilaServer
    """SiLA Server serving this feature implementation"""

    def __init__(self, parent_server: SilaServer) -> None:
        """
        Base class for all SiLA feature implementations

        Parameters
        ----------
        parent_server
            SiLA Server that serves this feature implementation
        """
        self.parent_server = parent_server
        self.__started: bool = False
        self.__is_running: bool = False
        self.__periodic_funcs: List[Callable[[], None]] = []

    def start(self) -> None:
        """
        Called automatically when the SiLA Server is started

        Raises
        ------
        RuntimeError
            When called twice

        Notes
        -----
        When overriding this method, don't forget to call ``super().start()``.
        """
        if self.__started:
            raise RuntimeError("Cannot start feature implementation twice")
        self.__is_running = True
        self.__started = True

        for func in self.__periodic_funcs:
            self.parent_server.child_task_executor.submit(func)

    def stop(self) -> None:
        """
        Called automatically when the SiLA Server is stopped

        Raises
        ------
        RuntimeError
            When called while the server is not running

        Notes
        -----
        When overriding this method, don't forget to call ``super().stop()``.
        """
        if not self.__is_running:
            raise RuntimeError("Can only stop running servers")
        self.__is_running = False

    def run_periodically(self, func: Callable[[], Any], delay_seconds: float = _STOP_THREAD_CHECK_PERIOD) -> None:
        """
        Register a function to be called periodically while the SiLA Server is running

        Parameters
        ----------
        func
            Function to call periodically. Will be called without arguments. Returned values are ignored.
        delay_seconds
            Time to wait between calling ``func()``
        """
        n_checks_per_loop = max(1, int(delay_seconds / _STOP_THREAD_CHECK_PERIOD))
        delay_seconds /= n_checks_per_loop

        def looped_func():
            while self.__is_running:
                func()
                for _ in range(n_checks_per_loop):
                    if not self.__is_running:
                        break
                    time.sleep(delay_seconds)

        self.__periodic_funcs.append(looped_func)

        if self.__is_running:
            self.parent_server.child_task_executor.submit(looped_func)
