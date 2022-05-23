from enum import Enum


class MemberStatusEnum(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"
