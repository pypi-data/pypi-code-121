from enum import IntEnum, auto

__all__ = [
    'ShowResource',
]


class ShowResource(IntEnum):
    """LXD resource to show."""
    CONTAINER = auto()
    VIRTUAL_MACHINE = auto()
    BOTH = auto()
