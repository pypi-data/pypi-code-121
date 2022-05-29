from enum import Enum


class DjangoReadyEnum(Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


__all__ = ["DjangoReadyEnum"]
