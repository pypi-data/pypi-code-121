from enum import Enum
from typing import Protocol, Tuple


class VmState(Enum):
    ...


class VmInstanceProxy(Protocol):
    # pytype: disable=bad-return-type
    def start(self, wait: bool = True) -> None:
        ...

    # pytype: disable=bad-return-type
    def stop(self, wait: bool = True) -> None:
        ...

    # pytype: disable=bad-return-type
    @property
    def state(self) -> VmState:
        ...


class RemoteShellProxy(VmInstanceProxy):
    # pytype: disable=bad-return-type
    def execute(self, *commands: str) -> Tuple[str, str]:
        ...

    # pytype: disable=bad-return-type
    def start(self, wait: bool = True) -> None:
        ...

    # pytype: disable=bad-return-type
    def stop(self, wait: bool = True) -> None:
        ...

    # pytype: disable=bad-return-type

    @property
    def state(self) -> VmState:
        ...
