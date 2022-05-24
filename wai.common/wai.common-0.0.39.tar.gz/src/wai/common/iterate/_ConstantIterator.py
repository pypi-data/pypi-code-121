from typing import Optional, Iterator

from .._typing import T


class ConstantIterator(Iterator[T]):
    """
    Class which implements the iterator interface, but always returns a single value.
    """
    def __init__(self, value: T, num_iterations: Optional[int] = None):
        self._value: T = value
        self._num_iterations: Optional[int] = num_iterations

    def __next__(self) -> T:
        if self._num_iterations == 0:
            raise StopIteration
        elif self._num_iterations is not None:
            self._num_iterations -= 1

        return self._value
