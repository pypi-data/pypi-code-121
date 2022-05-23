import datetime as dt
from json import dumps
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union


def _default(x: Any, /) -> str:
    """Extension for the JSON serializer."""

    if isinstance(x, dt.date):
        return x.isoformat()
    elif isinstance(x, Path):
        return x.as_posix()
    elif isinstance(x, set):
        inner = serialize(sorted(x))
        return f"set({inner})"
    elif isinstance(x, frozenset):
        inner = serialize(sorted(x))
        return f"frozenset({inner})"
    else:
        raise TypeError(f"Invalid type: {x}")


def serialize(
    x: Any,
    /,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    indent: Optional[Union[int, str]] = None,
    separators: Optional[tuple[str, str]] = None,
    sort_keys: bool = False,
    **kwargs: Any,
) -> str:
    """Serialize an object."""

    return dumps(
        x,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        indent=indent,
        separators=separators,
        default=_default,
        sort_keys=sort_keys,
        **kwargs,
    )
