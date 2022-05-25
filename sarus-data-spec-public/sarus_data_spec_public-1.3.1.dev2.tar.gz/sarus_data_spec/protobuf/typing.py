"""Protocols describing common object behaviors
"""
from typing import (
    ByteString,
    MutableMapping,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from google.protobuf.descriptor import Descriptor

M = TypeVar('M')


@runtime_checkable
class Protobuf(Protocol):
    """A protobuf message.
    Only the used methods are defined in this protocol.
    We assume all protobuf messages have properties
    """

    DESCRIPTOR: Descriptor

    def CopyFrom(self: M, other_msg: M) -> None:
        ...

    def SerializeToString(self: M, deterministic: bool) -> bytes:
        ...

    def FromString(self: M, s: Union[ByteString, bytes]) -> M:
        ...

    @property
    def properties(self) -> MutableMapping:
        ...


@runtime_checkable
class ProtobufWithUUID(Protobuf, Protocol):
    uuid: str


@runtime_checkable
class ProtobufWithUUIDAndDatetime(ProtobufWithUUID, Protocol):
    datetime: str  # ISO 8601 datetime
