"""
Utility classes for executing CoSApp simulation following file events.

Those classes use third-party `watchdog` package to observe file events.
"""
import logging
from threading import Timer
from typing import AnyStr, List, Union

from cosapp.systems import System

logger = logging.getLogger(__name__)


try:  # watchdog will be a conditional dependency
    from watchdog.events import (
        PatternMatchingEventHandler,
        FileCreatedEvent,
        FileModifiedEvent,
    )
    from watchdog.observers import Observer

    class WatchdogHandler(PatternMatchingEventHandler):
        """Define a watchdog class that allows to trigger actions on file events (creation,
        modification, etc.).
            
        Parameters
        ----------
        owner: System
            Owner of the watchdog. Actions will be triggered on him on events  
        folder: str
            Folder to supervise with the watchdog
        timeout: float, optional
            Define the max inactivity duration of the watchdog
        patterns: Union[List, AnyStr], optional
            Define the file patterns to monitor in the chosen path
        """

        def __init__(
            self,
            owner: System,
            folder: str,
            timeout: float = 30.0,
            patterns: Union[List, AnyStr] = "*.*",
        ):
            """`WatchdogHandler` class constructor
            
            Parameters
            ----------
            owner: System
                Owner of the watchdog. Actions will be triggered on him on events  
            folder: str
                Folder to supervise with the watchdog
            timeout: float, optional
                Define the max inactivity duration of the watchdog
            patterns: Union[List, AnyStr], optional
                Define the file patterns to monitor in the chosen path
            """
            super(WatchdogHandler, self).__init__(patterns=patterns)
            self._owner = owner
            self.timeout = timeout
            self.exit = False
            self.folder = folder

            self.__observer: Observer = None
            self.__timer: Timer = None
            self.__is_alive = False

        def compute(self, file_full_path: str) -> None:
            """Actions to do while an event is detected
            
            Parameters
            ----------
            file_full_path: str
                Gives access to the file that triggered an event
            """
            self._owner.run_drivers()

        def is_alive(self) -> bool:
            """Is the watcher alive?"""
            return self.__is_alive

        def reset(self) -> None:
            """Reset the watchdog by stopping the timer countdown and starting a new one"""
            if self.__observer is None:
                raise RuntimeError("Watcher has never been started.")
            self.__timer.cancel()
            self.__timer = Timer(self.timeout, self.stop)
            self.__timer.start()

        def stop(self) -> None:
            """Exits the watchdog monitoring"""
            if not self.__is_alive:
                logger.debug("Watcher not alive.")
                return

            self.__is_alive = False
            self.__timer.cancel()
            self.__observer.stop()
            self.__observer.join()

            logger.info(f"..trigger on {self._owner.name!r} is timeout")

        def start(self, time_step: float = 1.0) -> None:
            """Starts the watchdog monitoring

            Parameters
            ----------
            time_step: float, optional
                Gives the time step at which the watchdog will check events in the supervised folder
            """
            self.__observer = Observer()
            self.__observer.schedule(self, path=self.folder)

            if time_step > self.timeout:
                time_step = self.timeout

            logger.debug(
                f"> trigger created on {self._owner.name!r} with {self.timeout} seconds timeout.."
            )
            self.__observer.start()

            self.__timer = Timer(self.timeout, self.stop)
            self.__timer.start()
            self.__is_alive = True

    class FileCreationHandler(WatchdogHandler):
        """Specific watchdog class to monitor file creation events
            
        Parameters
        ----------
        owner: System
            Owner of the watchdog. Actions will be triggered on him on events  
        folder: str
            Folder to supervise with the watchdog
        timeout: float, optional
            Define the max inactivity duration of the watchdog
        patterns: Union[List, AnyStr], optional
            Define the file patterns to monitor in the chosen path
        """

        def on_created(self, event: FileCreatedEvent) -> None:  # when file is created
            """Actions to complete when a creation event is triggered
            
            Parameters
            ----------
            event
                Event that triggered the watchdog
            """
            logger.info(f" #creation of file {event.src_path!r} detected")
            self.compute(event.src_path)
            self.reset()
            logger.debug(
                f"> trigger restart on {self._owner.name!r} for another {self.timeout} seconds.."
            )

    class FileModificationHandler(WatchdogHandler):
        """Specific watchdog class to monitor file modification events.
            
        Parameters
        ----------
        owner: System
            Owner of the watchdog. Actions will be triggered on him on events  
        folder: str
            Folder to supervise with the watchdog
        timeout: float, optional
            Define the max inactivity duration of the watchdog
        patterns: Union[List, AnyStr], optional
            Define the file patterns to monitor in the chosen path
        """

        def on_modified(
            self, event: FileModifiedEvent
        ) -> None:  # when file is modified
            """Actions to complete when a modification event is triggered

            Parameters
            ----------
            event
                Event that triggered the watchdog
            """
            logger.info(f" #modification of file {event.src_path!r} detected")
            self.compute(event.src_path)
            self.reset()
            logger.debug(
                f"> trigger restart on {self._owner.name!r} for another {self.timeout} seconds.."
            )


except ImportError:
    logger.warning(
        "'watchdog' package is not installed. Files modification and creation trackers are not available."
    )
