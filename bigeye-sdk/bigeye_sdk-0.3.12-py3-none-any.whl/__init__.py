import dataclasses
from base64 import b64encode
from datetime import datetime, timedelta
from typing import Dict, Any
from .exceptions import exceptions

from betterproto import Casing, Message, FieldMetadata, DATETIME_ZERO, _Timestamp, _Duration, INT_64_TYPES, TYPE_BYTES, \
    TYPE_ENUM, TYPE_INT32, TYPE_INT64


def to_dict(
        message: Message, casing: Casing = Casing.CAMEL, include_default_values: bool = False
) -> dict:
    """
    TODO: Ripped off from betterproto Message class.  May or may not be able to roll it in.  Could also add an includE_default_list: List[str]
    Returns a dict representation of this message instance which can be
    used to serialize to e.g. JSON. Defaults to camel casing for
    compatibility but can be set to other modes.

    `include_default_values` can be set to `True` to include default
    values of fields. E.g. an `int32` type field with `0` value will
    not be in returned dict if `include_default_values` is set to
    `False`.
    """
    output: Dict[str, Any] = {}
    for field in dataclasses.fields(message):
        meta = FieldMetadata.get(field)
        v = getattr(message, field.name)
        cased_name = casing(field.name).rstrip("_")  # type: ignore
        if meta.proto_type == "message":
            if isinstance(v, datetime):
                if v != DATETIME_ZERO or include_default_values:
                    output[cased_name] = _Timestamp.timestamp_to_json(v)
            elif isinstance(v, timedelta):
                if v != timedelta(0) or include_default_values:
                    output[cased_name] = _Duration.delta_to_json(v)
            elif meta.wraps:
                if v is not None or include_default_values:
                    output[cased_name] = v
            elif isinstance(v, list):
                # Convert each item.
                v = [to_dict(i, casing, include_default_values) for i in v]
                if v or include_default_values:
                    output[cased_name] = v
            else:
                if v._serialized_on_wire or include_default_values:
                    output[cased_name] = to_dict(v, casing, include_default_values)
        elif meta.proto_type == "map":
            for k in v:
                if hasattr(v[k], "to_dict"):
                    v[k] = to_dict(v[k], casing, include_default_values)

            if v or include_default_values:
                output[cased_name] = v
        elif v != message._get_field_default(field, meta) or include_default_values:
            if meta.proto_type in INT_64_TYPES:
                if isinstance(v, list):
                    output[cased_name] = [str(n) for n in v]
                else:
                    output[cased_name] = str(v)
            elif meta.proto_type == TYPE_BYTES:
                if isinstance(v, list):
                    output[cased_name] = [b64encode(b).decode("utf8") for b in v]
                else:
                    output[cased_name] = b64encode(v).decode("utf8")
            elif meta.proto_type == TYPE_ENUM:
                enum_values = list(
                    message._betterproto.cls_by_field[field.name]
                )  # type: ignore
                if isinstance(v, list):
                    output[cased_name] = [enum_values[e].name for e in v]
                else:
                    output[cased_name] = enum_values[v].name
            else:
                output[cased_name] = v
        elif meta.proto_type in [TYPE_INT32, TYPE_INT64]:
            output[cased_name] = v

    return output
