from __future__ import annotations

import re
from typing import Optional, Type, Union

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Real as SilaReal


class Real(DataType[SilaReal, float]):
    native_type = float
    message_type: Type[SilaReal]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Real

    def to_native_type(self, message: SilaReal, toplevel_named_data_node: Optional[NamedDataNode] = None) -> float:
        return message.value

    def to_message(
        self, value: Union[float, int], toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> SilaReal:
        if isinstance(value, int):
            value = float(value)  # get meaningful errors for impossible conversions, e.g. on overflows
        return self.message_type(value=value)

    @staticmethod
    def from_string(value: str) -> float:
        # regex: https://www.w3.org/TR/xmlschema11-2/#nt-decimalRep
        if not re.match(r"^([+-])?([0-9]+(\.[0-9]*)?|\.[0-9]+)$", value):
            raise ValueError(f"Cannot parse as decimal: '{value}'")
        return float(value)
