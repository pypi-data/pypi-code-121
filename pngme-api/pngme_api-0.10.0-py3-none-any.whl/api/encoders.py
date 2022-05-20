from datetime import datetime
from typing import Any, Dict


def _to_isoformat(value: datetime) -> str:
    """Cast datetime to string removing microseconds."""
    return value.replace(microsecond=0).isoformat()


def _filter_truthy_values(**kwargs: Any) -> Dict[str, Any]:
    """Return a copy containing only keys containing truthy values."""
    return {k: v for k, v in kwargs.items() if v}


def encode_query_params(**kwargs: Any) -> Dict[str, Any]:
    """Serialize incompatible types and remove falsy values."""
    query_params = {}
    for key, value in _filter_truthy_values(**kwargs).items():
        if isinstance(value, datetime):
            query_params[key] = _to_isoformat(value)
        else:
            query_params[key] = value
    return query_params
