from pydash import now

__all__ = [
    "now_seconds"
]


def now_seconds() -> int:
    return int(now() / 1000)
