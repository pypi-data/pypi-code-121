from typing_extensions import Protocol


class HasStr(Protocol):
    def __str__(self) -> str:
        ...
