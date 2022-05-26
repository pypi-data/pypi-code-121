from collections import namedtuple
from typing import Any, Dict, Generic, Iterable, List, Optional, Tuple, Type, TypeVar

from google.protobuf.message import Message

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.command.intermediate_response import IntermediateResponse
from sila2.framework.command.parameter import Parameter
from sila2.framework.command.response import Response
from sila2.framework.data_types.list import List as SilaList
from sila2.framework.errors.validation_error import ValidationError
from sila2.framework.property.property import Property

T = TypeVar("T", bound=NamedDataNode)


class CompositeMessageMappable(MessageMappable, Generic[T]):
    name: str
    fields: List[T]

    def __init__(self, fields: Iterable[T], message_type: Type[Message]):
        self.fields = list(fields)
        self.message_type = message_type
        self.name = message_type.__name__
        self.namedtuple_type = namedtuple(self.name, [field._identifier for field in fields])

    def __bool__(self):
        return bool(self.fields)

    def __iter__(self):
        return iter(self.fields)

    def to_message(self, *args, **kwargs) -> Message:
        # TODO: error messages
        #   - if multiple args are expected and only one integer is given: "int object has no length"
        #   - include fields names
        toplevel_named_data_node = (
            kwargs.pop("toplevel_named_data_node") if "toplevel_named_data_node" in kwargs else None
        )

        n_args = len(args) + len(kwargs)
        if len(self) == 0:
            if n_args == 0:
                return self.message_type()
            elif (
                len(args) == 1
                and not kwargs
                and (args[0] is None or (isinstance(args[0], tuple) and len(args[0]) == 0))
            ):
                return self.message_type()
            else:
                raise TypeError(f"Expected no arguments, got {args}")

        # args[0] is NamedTuple representation of the message type
        if (
            len(args) == 1
            and not kwargs
            and isinstance(args[0], tuple)
            and hasattr(args[0], "_fields")
            and set(args[0]._fields) == set(f._identifier for f in self.fields)
        ):
            kwargs = {f._identifier: getattr(args[0], f._identifier) for f in self.fields}
            args = ()

        if len(args) == 1 and not kwargs and len(self) != 1:
            if isinstance(args[0], dict):
                kwargs = args[0]
                args = ()
            else:
                args = args[0]

        n_args = len(args) + len(kwargs)
        if n_args != len(self):
            raise TypeError(f"Message {self.message_type.__name__} has {len(self)} field(s), got {n_args} argument(s)")

        expected_kwargs_keys = {f._identifier for f in self.fields[len(args) :]}
        provided_kwargs_keys = set(kwargs.keys())
        if not expected_kwargs_keys.issubset(provided_kwargs_keys):
            raise TypeError(
                f"Message {self.message_type.__name__}: "
                f"Missing arguments for fields {expected_kwargs_keys - provided_kwargs_keys}"
            )

        field_values: Dict[str, Tuple[NamedDataNode, Any]] = {
            f._identifier: (f, arg) for f, arg in zip(self.fields[: len(args)], args)
        }
        for field in self.fields[len(args) :]:
            field_values[field._identifier] = field, kwargs[field._identifier]

        return self.message_type(
            **{
                field_id: field.data_type.to_message(
                    arg,
                    toplevel_named_data_node=field
                    if isinstance(field, (Parameter, Property, Response, IntermediateResponse))
                    else toplevel_named_data_node,
                )
                for field_id, (field, arg) in field_values.items()
            }
        )

    def to_native_type(self, message: Message, toplevel_named_data_node: Optional[NamedDataNode] = None) -> Any:
        field_values = []
        for field in self.fields:
            try:
                value_msg = getattr(message, field._identifier)

                # HasFields only works with message fields, not with repeated fields (list) or primitive types (int64)
                if not isinstance(field.data_type, SilaList) and not message.HasField(field._identifier):
                    raise ValidationError(
                        f"Missing required field {field._identifier} in message {message.__class__.__name__}"
                    )

                if isinstance(field, (Parameter, Property, Response, IntermediateResponse)):
                    field_toplevel_named_data_node = field
                else:
                    field_toplevel_named_data_node = toplevel_named_data_node

                field_values.append(field.data_type.to_native_type(value_msg, field_toplevel_named_data_node))
            except Exception as exc:
                if isinstance(exc, ValidationError):
                    val_err = exc
                else:
                    val_err = ValidationError(
                        f"Field {field._identifier}: Failed to parse field {field._identifier} of message "
                        f"{message.__class__.__name__} ({exc!r})"
                    )
                if isinstance(field, Parameter):
                    val_err.parameter_fully_qualified_identifier = field.fully_qualified_identifier
                raise val_err

        return self.namedtuple_type(*field_values)

    def __len__(self):
        return len(self.fields)
