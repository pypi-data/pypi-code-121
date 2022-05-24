from enum import (
    Enum,
)


class DBImageTypeEnum(Enum):
    BASE = 'base'
    ETALON = 'etalon'


class DBStatusEnum(Enum):
    REACHABLE = 'reachable'
    UNREACHABLE = 'unreachable'

