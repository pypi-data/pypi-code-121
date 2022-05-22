from enum import (
    Enum,
)


class IPAddressStateEnum(Enum):
    NOT_CHECKED = 'not checked'
    INVALID = 'invalid'
    VALID = 'valid'
    REACHABLE = 'reachable'
    UNREACHABLE = 'unreachable'
