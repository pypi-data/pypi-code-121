from typing import Type, List, Optional, Tuple


class ExceptionChainer:
    """
    Context-manager class which captures exceptions for later use. Designed for
    use in loops where an exception may occur on each iteration, so they can be
    processed at the end.
    """
    def __init__(self, *exc_types: Type[Exception]):
        self.__types: Tuple[Type[Exception]] = tuple()
        self.__exceptions: List[Optional[Exception]] = []

        self.set_types(*exc_types)

    def exception_count(self) -> int:
        """
        Gets the number of exceptions captured.
        """
        return sum(1 for e in self.__exceptions if e is not None)

    def no_exception_count(self) -> int:
        """
        Gets the number of iterations that occurred with no exception.
        """
        return len(self) - self.exception_count()

    def reset(self):
        """
        Clears the list of captured exceptions.
        """
        self.__exceptions.clear()

    def set_types(self, *exc_types: Type[Exception]):
        """
        Sets the types of exceptions this chainer will capture.
        If no types are given, captures all exceptions.

        :param exc_types:   The types of exception.
        """
        self.__types = exc_types if len(exc_types) > 0 else (Exception,)

    def exceptions(self, remove_missing: bool = False) -> List[Optional[Exception]]:
        """
        Gets the list of exceptions in captured order.

        :param remove_missing:  Whether to remove None values (iterations
                                that didn't throw).
        :return:                The list of exceptions.
        """
        return [e for e in self.__exceptions if e is not None or not remove_missing]

    def raise_last(self):
        """
        Raises the last exception captured. If there isn't one,
        simply returns.
        """
        # Get the exceptions
        exceptions = self.exceptions(True)

        # If there are any, raise the last one
        if len(exceptions) > 0:
            raise exceptions[-1]

    def raise_chained(self, reversed: bool = False):
        """
        Raises the captured exceptions. Each exception is treated as
        the cause of the following exception (or vice versa if reversed
        is set). If not exceptions have been captured, simply returns.

        :param reversed:    Whether to chain in reverse order.
        """
        # Get the exceptions
        exceptions = self.exceptions(True)

        # Just return if there are no exceptions
        if len(exceptions) == 0:
            return

        # Reverse if requested
        if reversed:
            exceptions.reverse()

        # Chain the exceptions
        exception = exceptions[0]
        for i in range(1, len(exceptions)):
            try:
                raise exceptions[i] from exception
            except Exception as e:
                exception = e

        # Raise the chained exception
        raise exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception occurred
            self.__exceptions.append(None)
            return True
        elif issubclass(exc_type, self.__types):
            # An exception we are looking for occurred
            self.__exceptions.append(exc_val)
            return True
        else:
            # An unexpected exception occurred, so don't suppress it
            return False

    def __len__(self) -> int:
        return len(self.__exceptions)
