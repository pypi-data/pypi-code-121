import sys
from datetime import datetime


def fromisoformat(s: str) -> datetime:
    if sys.version_info < (3, 7):
        return datetime.strptime(s[:-3] + s[-2:], "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return datetime.fromisoformat(s)
