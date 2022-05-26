"""Utility helper functions that are re-used in multiple locations."""
import asyncio
from functools import wraps


# https://github.com/pallets/click/issues/85#issuecomment-503464628
def async_command(f):
    """Wraps a function and allows it to be called asynchronously with click commands."""  # noqa: D401

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper
