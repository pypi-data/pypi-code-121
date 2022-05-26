import abc
import logging
from numbers import Number

from cosapp.patterns import Singleton, Observer, Subject

logger = logging.getLogger(__name__)


class TimeManager(Subject):
    """Observer pattern subject notifying its observers when time changes"""
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, TimeObserver)

    def __init__(self, t: Number = 0):
        super().__init__()
        self.__time = t

    @property
    def time(self) -> Number:
        """Current simulation time"""
        return self.__time

    @time.setter
    def time(self, t: Number):
        logger.info(f"Time = {t:.5g} s")
        dt = t - self.__time
        self.__time = t
        self.notify(dt)

    def reset(self, t: Number = 0):
        """Reset time to a chosen value, without notifying observers"""
        self.__time = t


class UniversalClock(TimeManager, metaclass=Singleton):
    """Unique (singleton) time manager"""
    def __repr__(self) -> str:
        return f"Universal time manager @ t = {self.time}"


class TimeObserver(Observer):
    """
    Abstract time observer.
    Concrete derived classes must implement abstract method '_update'.
    """
    def __init__(self, sign_in=True):
        super().__init__()
        if sign_in:
            self.observe()

    def observe(self):
        """Sign in as observer of the universal time manager"""
        clock = UniversalClock()
        super().observe(clock)

    def observes(self) -> bool:
        """Bool: has object signed up as an observer?"""
        clock = UniversalClock()
        return super().observes(clock)

    @property
    def t(self) -> Number:
        """Current simulation time - alias for time"""
        return self.time

    @property
    def time(self) -> Number:
        """Current simulation time"""
        return UniversalClock().time

    @abc.abstractmethod
    def _update(self, dt: Number) -> None:
        """Specifies how object must update when notified a time step of `dt`"""
        pass
