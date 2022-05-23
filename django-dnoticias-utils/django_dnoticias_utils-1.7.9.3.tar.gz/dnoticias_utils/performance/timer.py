from functools import wraps
from time import perf_counter
from typing import Any, Callable, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])

def timer(prefix: Optional[str] = None, precision: int = 6) -> Callable[[F], F]:

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal prefix
            prefix = prefix if prefix is not None else f"{func.__name__}: "
            start = perf_counter()
            result = func(*args, **kwargs)
            end = perf_counter()
            print(f"{prefix}{end - start:.{precision}f}s - args: {args} - kwargs: {kwargs}")
            return result
        return cast(F, wrapper)

    return decorator
