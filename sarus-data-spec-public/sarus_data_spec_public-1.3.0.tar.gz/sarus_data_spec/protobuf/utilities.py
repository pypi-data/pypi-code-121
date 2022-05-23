from __future__ import annotations

from typing import Any, Dict, Type, TypeVar, Union, cast
import base64

from google.protobuf.any_pb2 import Any as AnyProto
from google.protobuf.descriptor_pool import Default
from google.protobuf.json_format import (
    MessageToDict,
    MessageToJson,
    Parse,
    ParseDict,
)
from google.protobuf.message_factory import MessageFactory

from sarus_data_spec.protobuf.typing import Protobuf
import sarus_data_spec as s


def message(type_name: str) -> Protobuf:
    """Return a message instance from a type_name."""
    return MessageFactory().GetPrototype(
        Default().FindMessageTypeByName(type_name)  # type: ignore
    )()


def message_type(type_name: str) -> Type[Protobuf]:
    """Return a message type from a type_name."""
    return MessageFactory().GetPrototype(
        Default().FindMessageTypeByName(type_name)  # type: ignore
    )


def type_name(message: Union[Type[Protobuf], Protobuf]) -> str:
    """Return a type_name from a message."""
    return cast(str, message.DESCRIPTOR.full_name)


def wrap(message: Protobuf) -> AnyProto:
    """Wrap a Message into an Any"""
    wrapped_message: AnyProto = AnyProto()
    wrapped_message.Pack(
        message,
        type_url_prefix=cast(bytes, s.PACKAGE_NAME),
        deterministic=True,
    )
    return wrapped_message


def unwrap(wrapped_message: AnyProto) -> Protobuf:
    """Unwrap an Any to a Message"""
    result = message(wrapped_message.TypeName())  # type: ignore
    wrapped_message.Unpack(result)
    return result


M = TypeVar('M', bound=Protobuf)


def copy(value: M) -> M:
    result = message(value.DESCRIPTOR.full_name)
    result.CopyFrom(value)
    return cast(M, result)


def serialize(message: M) -> bytes:
    return wrap(message).SerializeToString(deterministic=True)


def deserialize(bytes: bytes) -> Protobuf:
    wrapped_message: AnyProto = AnyProto()
    wrapped_message.MergeFromString(bytes)
    return unwrap(wrapped_message)


def json_serialize(message: Protobuf) -> bytes:
    return MessageToJson(
        wrap(message),
        including_default_value_fields=True,
        preserving_proto_field_name=True,
        sort_keys=True,
    ).encode('utf8')


def json_deserialize(bytes: bytes) -> Protobuf:
    wrapped_message: AnyProto = AnyProto()
    Parse(bytes.decode('utf8'), wrapped_message)
    return unwrap(wrapped_message)


def dict_serialize(message: Protobuf) -> Dict[str, Any]:
    return MessageToDict(
        wrap(message),
        including_default_value_fields=True,
        preserving_proto_field_name=True,
    )


def dict_deserialize(dct: Dict[str, Any]) -> Protobuf:
    wrapped_message: AnyProto = AnyProto()
    ParseDict(dct, wrapped_message)
    return unwrap(wrapped_message)


def json(message: Protobuf) -> str:
    return MessageToJson(
        wrap(message),
        including_default_value_fields=True,
        preserving_proto_field_name=True,
        sort_keys=True,
    )


def dejson(string: str) -> Protobuf:
    wrapped_message: AnyProto = AnyProto()
    Parse(string, wrapped_message)
    return unwrap(wrapped_message)


def to_base64(message: Protobuf) -> str:
    return base64.b64encode(
        message.SerializeToString(deterministic=True)
    ).decode('ASCII')


def from_base64(string: str, message: M) -> M:
    return cast(M, message.FromString(base64.b64decode(string)))
