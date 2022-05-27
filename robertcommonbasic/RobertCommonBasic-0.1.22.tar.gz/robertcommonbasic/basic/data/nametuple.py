from datetime import datetime
from enum import Enum


def is_named_tuple(x):
    _type = type(x)
    bases = _type.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(type(i) == str for i in fields)


def to_json(obj, timeformat=None):
    # timeformat like "%Y-%m-%d %H:%M:%S"
    if isinstance(obj, dict):
        return {key: to_json(value, timeformat) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [to_json(value, timeformat) for value in obj]
    elif is_named_tuple(obj):
        # noinspection PyProtectedMember
        return {key: to_json(value, timeformat) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(to_json(value, timeformat) for value in obj)
    elif issubclass(obj.__class__, Enum):
        return obj.value
    elif type(obj) is datetime and timeformat:
        return obj.strftime(timeformat)
    else:
        return obj