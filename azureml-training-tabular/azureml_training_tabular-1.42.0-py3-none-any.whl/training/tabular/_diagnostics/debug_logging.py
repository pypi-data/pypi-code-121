# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility module for logging."""
import functools
import logging
from typing import Any, Callable


def function_debug_log_wrapped(log_level: int = logging.DEBUG) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Add logs wrapper around transformer class function."""

    def wrapper(f: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(f)
        def debug_log_wrapped(obj: Any, *args: Any, **kwargs: Any) -> Any:
            my_logger = logging.getLogger(getattr(f, "__module__", obj.__class__.__module__))
            my_logger.log(log_level, f"Calling {obj.__class__.__name__}.{f.__name__}()")
            try:
                r = f(obj, *args, **kwargs)
                my_logger.log(log_level, f"Exiting {obj.__class__.__name__}.{f.__name__}()")
                return r
            except Exception:
                my_logger.log(log_level, f"Failure in {obj.__class__.__name__}.{f.__name__}()")
                raise

        return debug_log_wrapped

    return wrapper
