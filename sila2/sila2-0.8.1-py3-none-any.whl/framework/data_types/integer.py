from __future__ import annotations

import re
from typing import Optional, Type

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Integer as SilaInteger


class Integer(DataType[SilaInteger, int]):
    native_type = int
    message_type: Type[SilaInteger]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Integer

    def to_native_type(self, message: SilaInteger, toplevel_named_data_node: Optional[NamedDataNode] = None) -> int:
        return message.value

    def to_message(self, value: int, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaInteger:
        return self.message_type(value=value)

    @staticmethod
    def from_string(value: str) -> int:
        if not re.match("^[-+]?[0-9]+$", value):
            raise ValueError(f"Cannot parse as integer: '{value}'")
        return int(value)
