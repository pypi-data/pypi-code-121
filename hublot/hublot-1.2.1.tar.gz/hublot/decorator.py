#!/usr/bin/env python3

# standards
from collections.abc import Generator, Iterator, Sized
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
import threading
from time import sleep
from typing import Callable, Optional, Sequence

# hublot
from .exceptions import ScraperError
from .logs import LOGGER


@dataclass
class ThreadLocalStackFrame:
    is_retry: bool = False


class ThreadLocalStack(threading.local):

    def __init__(self):
        super().__init__()
        # each thread will magically get a different stack
        self.stack = [ThreadLocalStackFrame()]


SCRAPER_LOCAL = ThreadLocalStack()


def retry_on_scraper_error(
    no_parens_function: Optional[Callable] = None,
    *,
    error_types: Sequence[type] = (),
    num_attempts: int = 5,
):
    if no_parens_function:
        # decorator is without parentheses
        return retry_on_scraper_error()(no_parens_function)

    @contextmanager
    def scraper_stack_frame():
        frame = ThreadLocalStackFrame()
        SCRAPER_LOCAL.stack.append(frame)
        try:
            yield frame
        finally:
            SCRAPER_LOCAL.stack.pop()

    error_types = (ScraperError, *error_types)

    def make_wrapper(function: Callable):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with scraper_stack_frame() as frame:
                for attempt in range(num_attempts):
                    try:
                        if attempt > 0:
                            frame.is_retry = True
                        payload = function(*args, **kwargs)
                        if isinstance(payload, (Iterator, Generator)) and not isinstance(payload, Sized):
                            payload = list(payload)
                        return payload
                    except Exception as error:  # pylint: disable=broad-except
                        if isinstance(error, error_types) and attempt < num_attempts - 1:
                            delay = 5 ** attempt
                            LOGGER.error('%s: %s - sleeping %ds', type(error).__name__, error, delay)
                            sleep(delay)
                        else:
                            raise
            raise Exception("can't reach here")
        return wrapper
    return make_wrapper
