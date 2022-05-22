from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, List
from . import *


def get_versions() -> List[Type]:
    from .version_0 import Version0
    from .version_1 import Version1
    return [Version0, Version1]


class MigrationVersion(ABC):
    """
    Abstracts a database migration.
    """

    @abstractmethod
    def get_version(self) -> int:
        ...

    @abstractmethod
    def do(self, engine, schema=None) -> None:
        ...

    @abstractmethod
    def undo(self, engine, schema=None) -> None:
        ...

    def __lt__(self, other: MigrationVersion):
        return self.get_version() < other.get_version()
