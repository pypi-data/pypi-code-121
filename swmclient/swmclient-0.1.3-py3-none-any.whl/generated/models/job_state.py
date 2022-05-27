from enum import Enum


class JobState(str, Enum):
    R = "R"
    Q = "Q"
    W = "W"
    F = "F"
    E = "E"
    T = "T"
    C = "C"

    def __str__(self) -> str:
        return str(self.value)
