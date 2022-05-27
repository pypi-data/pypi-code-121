from enum import Enum


class BorderRadiusEnum(str, Enum):
    NONE = "none"
    LG = "lg"
    MD = "md"
    SM = "sm"
    FULL = "full"

    def __str__(self) -> str:
        return str(self.value)
