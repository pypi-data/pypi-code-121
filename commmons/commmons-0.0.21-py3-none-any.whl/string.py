import re

__all__ = [
    "strip_non_numeric"
]

_non_numeric = re.compile(r'[^\d]+')


def strip_non_numeric(s: str) -> str:
    return _non_numeric.sub('', s)
