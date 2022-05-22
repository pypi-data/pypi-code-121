from functools import wraps
from typing import Callable, List

__all__ = [
    "with_retry"
]


def with_retry(func: Callable, retry_count: int, acceptable_exceptions: List[type]) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_exception_msg = None
        for i in range(retry_count):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if type(e) in acceptable_exceptions:
                    if i + 1 < retry_count:
                        last_exception_msg = str(e)
                        continue
                raise

        raise RuntimeError(last_exception_msg)

    return wrapper
