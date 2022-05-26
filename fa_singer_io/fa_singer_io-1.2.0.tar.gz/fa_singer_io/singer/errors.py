from typing import (
    FrozenSet,
)


class MissingKeys(Exception):
    def __init__(self, keys: FrozenSet[str], at: str) -> None:
        super().__init__(f"{keys} at {at}")
