from typing import Any


def ensure_str(x: Any, /) -> str:
    """Ensure an object is a string."""

    if isinstance(x, str):
        return x
    else:
        raise TypeError(f"{x} is not a string")
