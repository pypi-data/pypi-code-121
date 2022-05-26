from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from lxml import etree

from sila2.framework.abc.message_mappable import MessageMappable, ProtobufType, PythonType
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class DataType(MessageMappable[ProtobufType, PythonType], ABC):
    @staticmethod
    def from_fdl_node(fdl_node, parent_feature: Feature, parent_namespace) -> DataType:
        sila2_framework_pb2_module = parent_feature._pb2_module.SiLAFramework__pb2
        if xpath_sila(fdl_node, "sila:Basic"):
            identifier = xpath_sila(fdl_node, "sila:Basic/text()")[0]
            if identifier == "Boolean":
                from sila2.framework.data_types.boolean import Boolean

                return Boolean(sila2_framework_pb2_module)
            if identifier == "Integer":
                from sila2.framework.data_types.integer import Integer

                return Integer(sila2_framework_pb2_module)
            if identifier == "Real":
                from sila2.framework.data_types.real import Real

                return Real(sila2_framework_pb2_module)
            if identifier == "String":
                from sila2.framework.data_types.string import String

                return String(sila2_framework_pb2_module)
            if identifier == "Binary":
                from sila2.framework.data_types.binary import Binary

                return Binary(parent_feature, sila2_framework_pb2_module)
            if identifier == "Date":
                from sila2.framework.data_types.date import Date

                return Date(sila2_framework_pb2_module)
            if identifier == "Time":
                from sila2.framework.data_types.time import Time

                return Time(sila2_framework_pb2_module)
            if identifier == "Timestamp":
                from sila2.framework.data_types.timestamp import Timestamp

                return Timestamp(sila2_framework_pb2_module)
            if identifier == "Any":
                from sila2.framework.data_types.any import Any

                return Any(sila2_framework_pb2_module)
            else:  # pragma: no cover
                raise RuntimeError(f"Unknown basic data type: {identifier}")
        if xpath_sila(fdl_node, "sila:Constrained"):
            from sila2.framework.data_types.constrained import Constrained

            return Constrained.from_fdl_node(
                xpath_sila(fdl_node, "sila:Constrained")[0],
                parent_feature,
                parent_namespace,
            )
        if xpath_sila(fdl_node, "sila:DataTypeIdentifier"):
            identifier = xpath_sila(fdl_node, "sila:DataTypeIdentifier/text()")[0]
            return parent_feature._data_type_definitions[identifier]
        if xpath_sila(fdl_node, "sila:List"):
            from sila2.framework.data_types.list import List

            return List(xpath_sila(fdl_node, "sila:List")[0], parent_feature, parent_namespace)
        if xpath_sila(fdl_node, "sila:Structure"):
            from sila2.framework.data_types.structure import Structure

            return Structure(
                xpath_sila(fdl_node, "sila:Structure")[0],
                parent_feature,
                parent_namespace,
            )
        raise RuntimeError(f"Unknown data type node: {etree.tostring(fdl_node).decode('utf-8')}")  # pragma: no cover
