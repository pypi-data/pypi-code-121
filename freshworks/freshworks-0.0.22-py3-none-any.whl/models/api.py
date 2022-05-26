from enum import auto
from enum import IntEnum


class APIVersion(IntEnum):

    V1 = auto()
    V2 = auto()

    def __init__(self, value):

        self.path = f"/v{value}"
