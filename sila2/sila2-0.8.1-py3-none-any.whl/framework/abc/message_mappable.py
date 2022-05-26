from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from sila2.framework.abc.named_data_node import NamedDataNode


ProtobufType = TypeVar("ProtobufType")
PythonType = TypeVar("PythonType")


class MessageMappable(Generic[ProtobufType, PythonType], ABC):
    """Abstract class all classes representing Python-mappings for protobuf messages"""

    @abstractmethod
    def to_native_type(
        self, message: ProtobufType, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> PythonType:
        """Convert a protobuf message to the associated native type"""
        pass

    @abstractmethod
    def to_message(self, value: PythonType, toplevel_named_data_node: Optional[NamedDataNode]) -> ProtobufType:
        """
        Construct a protobuf message from a Python object

        Special kwargs:
        - toplevel_named_data_node: Optional[NamedDataNode]: The NamedDataNode object that the generated message is
            a part of (e.g. a Parameter instance)
        """
        pass
