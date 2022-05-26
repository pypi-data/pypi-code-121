from __future__ import annotations

import uuid
from typing import Any as TypingAny
from typing import NamedTuple, Optional

from lxml import etree

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.data_types.list import List
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Any as SilaAny
from sila2.framework.utils import xml_node_to_normalized_string

VOID_TYPE_XML = """
<DataType>
  <Constrained>
    <DataType>
      <Basic>String</Basic>
    </DataType>
    <Constraints>
      <Length>0</Length>
    </Constraints>
  </Constrained>
</DataType>
"""


class SilaAnyType(NamedTuple):
    type_xml: str
    """
    DataType element, must adhere to
    `AnyTypeDataType.xsd <https://gitlab.com/SiLA2/sila_base/-/blob/master/schema/AnyTypeDataType.xsd>`_
    """
    value: TypingAny
    """Value of the given type"""


class Any(DataType[SilaAny, SilaAnyType]):
    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Any

    def to_native_type(self, message: SilaAny, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaAnyType:
        type_str = message.type
        data_type = self.__getdata_type(type_str)
        msg = data_type.message_type.FromString(message.payload)
        if self.__is_void(type_str):
            return SilaAnyType(type_str, None)
        return SilaAnyType(type_str, data_type.to_native_type(msg, toplevel_named_data_node=toplevel_named_data_node))

    def to_message(self, value: SilaAnyType, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaAny:
        type_str, native_payload = value
        if self.__is_void(type_str):
            native_payload = ""
        data_type = self.__getdata_type(type_str)
        binary_payload = data_type.to_message(
            native_payload, toplevel_named_data_node=toplevel_named_data_node
        ).SerializeToString()

        return self.message_type(type=xml_node_to_normalized_string(type_str), payload=binary_payload)

    @staticmethod
    def __is_void(type_xml_str: str) -> bool:
        type_node = etree.fromstring(type_xml_str)
        return xml_node_to_normalized_string(type_node) == xml_node_to_normalized_string(VOID_TYPE_XML)

    @staticmethod
    def __getdata_type(type_xml_str: str) -> DataType:
        from sila2.framework.feature import Feature

        fdl_str = Any.__build_feature_xml(type_xml_str)
        data_type = Feature(fdl_str)._data_type_definitions["Any"]

        if isinstance(data_type, List):
            raise NotImplementedError("Any with List is not yet implemented")

        return data_type

    @staticmethod
    def __build_feature_xml(type_xml_str: str) -> str:
        return f"""<?xml version="1.0" encoding="utf-8" ?>
        <Feature SiLA2Version="1.0" FeatureVersion="1.0" Originator="org.silastandard"
                 Category="tests"
                 xmlns="http://www.sila-standard.org"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://www.sila-standard.org https://gitlab.com/SiLA2/sila_base/raw/master/schema/FeatureDefinition.xsd">
            <Identifier>AnyFeature{str(uuid.uuid4()).replace("-", "")}</Identifier>
            <DisplayName>Any</DisplayName>
            <Description>Dummy feature for the SiLA2 Any type</Description>
            <DataTypeDefinition>
                <Identifier>Any</Identifier>
                <DisplayName>Any</DisplayName>
                <Description>Any</Description>
                {type_xml_str}
            </DataTypeDefinition>
        </Feature>"""
