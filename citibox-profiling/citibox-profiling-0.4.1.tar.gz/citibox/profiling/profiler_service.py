from abc import ABC, abstractmethod

from .config import Config


class ProfilerService(ABC):

    def __init__(self, config: Config):
        self._started: bool = False
        self._config = config

    @abstractmethod
    def start(self) -> None:
        self._assert_started()
        self._started = True

    def _assert_started(self) -> None:
        if self._started:
            raise AlreadyStarted()


class AlreadyStarted(Exception):
    pass
