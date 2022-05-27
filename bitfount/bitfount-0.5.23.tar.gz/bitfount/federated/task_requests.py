"""Dataclasses and functionality for task request details/messages."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import typing
from typing import List, Type, TypeVar

import msgpack

from bitfount.federated.types import SerializedProtocol
from bitfount.types import _JSONDict

T = TypeVar("T", bound="_DataclassSerializerMixin")


@dataclass
class _DataclassSerializerMixin:
    """MixIn class for dataclasses that enable easy `msgpack` (de)serialization."""

    def to_dict(self) -> _JSONDict:
        """Returns dataclass as a dictionary."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls: Type[T], d: _JSONDict) -> T:
        """Creates dataclass from dictionary."""
        # Extract the types of instance fields for this dataclass
        field_types = typing.get_type_hints(cls)
        field_types = {
            k: v
            for k, v in field_types.items()
            if k in {f.name for f in dataclasses.fields(cls)}
        }

        # Create sub-dataclasses if needed
        for name, klass in field_types.items():
            if hasattr(klass, "from_dict"):
                d[name] = klass.from_dict(d[name])

        return cls(**d)

    def serialize(self) -> bytes:
        """Serializes dataclass to bytes."""
        return msgpack.dumps(self.to_dict())

    @classmethod
    def deserialize(cls: Type[T], data: bytes) -> T:
        """Deserializes dataclass from bytes."""
        return cls.from_dict(msgpack.loads(data))


@dataclass
class _TaskRequest(_DataclassSerializerMixin):
    """The full task request to be sent to the pod."""

    serialized_protocol: SerializedProtocol
    pod_identifiers: List[str]
    aes_key: bytes


@dataclass
class _EncryptedTaskRequest(_DataclassSerializerMixin):
    """Encrypted task request."""

    encrypted_request: bytes


@dataclass
class _SignedEncryptedTaskRequest(_DataclassSerializerMixin):
    """Encrypted and signed task request."""

    encrypted_request: bytes
    signature: bytes


@dataclass
class _TaskRequestMessage(_DataclassSerializerMixin):
    """Task request message to be sent to pod."""

    serialized_protocol: SerializedProtocol
    auth_type: str
    request: bytes
