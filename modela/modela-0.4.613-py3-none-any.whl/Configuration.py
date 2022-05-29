from dataclasses import dataclass
from typing import List, get_type_hints, get_args
import typing_utils
from google.protobuf.message import Message
from enum import Enum
from modela.util import TrackedList


def isPrimitive(obj):
    return not hasattr(obj, '__dict__')


def convert_case(attr):
    return attr[0].lower() + attr[1:]


class Configuration(object):
    """
    Configuration is a base class for all dataclasses which reflect Protobuf Messages representing Modela API models.
    It serves to provide fully typed (and tracked) interactions with the Modela API. This class
    provides methods for interacting with raw Protobuf Message types and automatically reading and propagating changes
    from a Python dataclass to a Protobuf Message, and vice-versa.
    """

    def __post_init__(self):  # Apply tracking to all list attributes post-initialization
        for attribute, value in self.__dict__.items():
            annotation_type = get_type_hints(self)[attribute]
            if typing_utils.issubtype(annotation_type, List):
                setattr(self, attribute, TrackedList(value, self, attribute))

    def to_message(self):
        if hasattr(self, "proto_type"):
            return self.set_parent(self.proto_type()).parent
        else:
            raise TypeError("Configuration does not have any protobuf information.")

    def apply_field(self, attribute, value, message: Message):
        """ Apply a single attribute to a Protobuf Message."""
        if value is None:
            return
        real_field = convert_case(attribute)
        annotation_type = get_type_hints(self)[attribute]
        if typing_utils.issubtype(annotation_type, List):
            del getattr(message, real_field)[:]
            if issubclass(get_args(annotation_type)[0], Enum): 
                getattr(message, real_field).extend([model.value for model in value])
            elif isPrimitive(get_args(annotation_type)[0]()):
                getattr(message, real_field).extend(value)
            else:
                getattr(message, real_field).extend([model.to_message() for model in value])
                for ind, model in enumerate(
                        value):  # Fix _parent references, protobuf containers like to make copies of objects
                    model._parent = getattr(message, real_field)[ind]

        elif isinstance(getattr(message, real_field), Message):
            value.set_parent(getattr(message, real_field))
        else:
            setattr(message, real_field, value.value if isinstance(value, Enum) else (value or annotation_type()))

    def apply_config(self, message: Message):
        """
        Apply all attributes of a Configuration to a Protobuf Message. If the message does not match the fields of the
        Configuration, an error will be thrown.
        """
        for attribute, value in self.__dict__.items():
            if attribute == "_parent":
                continue
            self.apply_field(attribute, value, message)

        return message

    def copy_from(self, message: Message):
        """
        Copy the attributes of a Protobuf Message to the attributes of the Configuration dataclass.

        :param message: The Protobuf Message to copy data from.
        :rtype: Configuration
        """
        for attribute, value in self.__dict__.items():
            if attribute == "_parent":
                continue
            annotation_type = get_type_hints(self)[attribute]
            message_attr = getattr(message, convert_case(attribute))
            if typing_utils.issubtype(annotation_type, List):
                annotation_type = get_args(annotation_type)[0]
                if issubclass(annotation_type, Enum) or isPrimitive(annotation_type()):
                    setattr(self, attribute, TrackedList([annotation_type(message) for message in message_attr],
                                                         self, attribute))
                else:
                    setattr(self, attribute, TrackedList(
                        [annotation_type().copy_from(message).set_parent(message) for message in message_attr],
                        self, attribute))
            elif isinstance(message_attr, Message):
                if message_attr.ByteSize() <= 0:
                    continue
                setattr(self, attribute, annotation_type().copy_from(message_attr))
            else:
                try:
                    setattr(self, attribute,
                            (type(annotation_type) if not callable(annotation_type) else annotation_type)(
                                message_attr))
                except ValueError:
                    pass

        self._parent = message
        return self

    def from_dict(self, data: dict):
        for attribute, value in self.__dict__.items():
            if attribute == "_parent" or not convert_case(attribute) in data:
                continue

            annotation_type = get_type_hints(self)[attribute]
            dict_attr = data[convert_case(attribute)]
            if typing_utils.issubtype(annotation_type, List):
                annotation_type = get_args(annotation_type)[0]
                if issubclass(annotation_type, Enum) or isPrimitive(annotation_type()):
                    setattr(self, attribute, TrackedList([annotation_type(message) for message in dict_attr],
                                                         self, attribute))
                else:
                    setattr(self, attribute, TrackedList(
                        [annotation_type().from_dict(message) for message in dict_attr],
                        self, attribute))
            elif isinstance(dict_attr, dict):
                setattr(self, attribute, annotation_type().from_dict(data))
            else:
                try:
                    setattr(self, attribute,
                            (type(annotation_type) if not callable(annotation_type) else annotation_type)(
                                dict_attr))
                except ValueError:
                    pass

        return self

    def set_parent(self, message: Message):
        """
        Set the Configuration's related Protobuf Message. Each attribute of the configuration will be applied to the message.
        If `message` does not contain the exact attributes of the configuration the function will fail. All future changes
        to the Configuration will be propagated to the message.

        :rtype: Configuration
        :param message: Protobuf Message which represents this Configuration.
        """
        self._parent = message
        self.apply_config(message)
        return self

    def propagate_to_parent(self, attribute, value):
        if hasattr(self, "_parent"):
            self.apply_field(attribute, value, self._parent)

    @property
    def parent(self):
        return self._parent

    def __setattr__(self, attribute, value):
        if hasattr(self, "_parent") and attribute != "_parent":
            self.apply_field(attribute, value, self._parent)

        if type(value) == list:
            value = TrackedList(value, self, attribute)

        super().__setattr__(attribute, value)

class ImmutableConfiguration(Configuration):
    """
    ImmutableConfiguration represents Modela API objects which should not be changed by end-users.
    """

    def __setattr__(self, attribute, value):
        object.__setattr__(self, attribute, value)

def datamodel(proto):
    """
    Decorator for Configurations to wrap them in a dataclass and store additional information about their related Protobuf message
    """
    def wrap(cls):
        setattr(cls, "proto_type", proto)
        return dataclass(cls)

    return wrap