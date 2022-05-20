"""
Utilities to implement functional retry policies.

Examples:
    @retry_policy()
    def hello_world():
        return "Hello world"
"""

import logging
import time
from functools import partial, wraps
from typing import Callable, Sequence, Type, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


logger = logging.getLogger(__name__)

class RetryLimitExceeded(Exception):
    """Function raised more exceptions than allowed."""


def execute_with_retry_policy(
    function: Callable[[], T],
    min_retry_interval_seconds: float = 1,
    max_retry_interval_seconds: float = 60,
    max_retry_count: int = 10,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
) -> T:
    """Invoke given function and manage retries for configured exceptions.

    If the function requires positional or keyword arguments, use
    functools.partial to construct a callable with predefined arguments.
    """
    retriable_exceptions_set = set(retryable_exceptions)
    retry_count = 0
    retry_interval_seconds = min_retry_interval_seconds

    while True:
        try:
            return function()
        except Exception as e:  # pylint: disable=broad-except
            if type(e) not in retriable_exceptions_set:
                raise

            if retry_count >= max_retry_count:
                # Construct dynamically created exception which subclasses from
                # RetryLimitExceeded and the exception raised from the callable
                # to preserve exception handling behavior of the caller.
                raise type("RetryFailed", (RetryLimitExceeded, type(e)), {})

            logger.warning("Retrying exception: %s", repr(e))
            time.sleep(retry_interval_seconds)

            retry_count += 1
            retry_interval_seconds = min(
                retry_interval_seconds * 2, max_retry_interval_seconds
            )


def retry_policy(
    min_retry_interval_seconds: float = 1,
    max_retry_interval_seconds: float = 60,
    max_retry_count: int = 10,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorate function to execute in managed retry environment."""

    def function_with_retry_policy(function: Callable[P, T]) -> Callable[P, T]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            result = execute_with_retry_policy(
                partial(function, *args, **kwargs),
                min_retry_interval_seconds=min_retry_interval_seconds,
                max_retry_interval_seconds=max_retry_interval_seconds,
                max_retry_count=max_retry_count,
                retryable_exceptions=retryable_exceptions,
            )
            return result

        return wrapper

    return function_with_retry_policy
