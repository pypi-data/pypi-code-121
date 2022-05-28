"""A promise class to delay evaluation."""
import threading
import typing

T = typing.TypeVar('T')

class Promise(typing.Generic[T]):
    """A promise to provide data and metadata on request.

    Pass a callable to produce a value. Access the value using the value or opt_value properties.
    """
    def __init__(self, fn: typing.Callable[[], T]):
        assert fn
        self.__lock = threading.RLock()
        self.__value : typing.Optional[T] = None
        self.__fn : typing.Optional[typing.Callable[[], T]] = fn

    @property
    def value(self) -> typing.Optional[T]:
        """Evaluate the value if not already evaluated and return the value."""
        with self.__lock:
            if callable(self.__fn):
                self.__value = self.__fn()
                self.__fn = None
            return self.__value

    @property
    def opt_value(self) -> typing.Optional[T]:
        """Return the value but do not evaluate it if it hasn't already been evaluated."""
        return self.__value

    @property
    def has_value(self) -> bool:
        """Return the value but do not evaluate it if it hasn't already been evaluated."""
        return self.__value is not None
