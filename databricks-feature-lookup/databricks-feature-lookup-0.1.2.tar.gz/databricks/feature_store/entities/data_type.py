from databricks.feature_store.protos.feature_store_serving_pb2 import (
    DataType as ProtoDataType,
)
from databricks.feature_store.entities._proto_enum_entity import _ProtoEnumEntity

from typing import Any


class DataType(_ProtoEnumEntity):
    """Online store data types."""

    INTEGER = ProtoDataType.Value("INTEGER")
    FLOAT = ProtoDataType.Value("FLOAT")
    BOOLEAN = ProtoDataType.Value("BOOLEAN")
    STRING = ProtoDataType.Value("STRING")
    DOUBLE = ProtoDataType.Value("DOUBLE")
    LONG = ProtoDataType.Value("LONG")
    TIMESTAMP = ProtoDataType.Value("TIMESTAMP")
    DATE = ProtoDataType.Value("DATE")
    SHORT = ProtoDataType.Value("SHORT")
    ARRAY = ProtoDataType.Value("ARRAY")
    MAP = ProtoDataType.Value("MAP")
    BINARY = ProtoDataType.Value("BINARY")
    DECIMAL = ProtoDataType.Value("DECIMAL")

    @classmethod
    def _enum_type(cls) -> Any:
        return ProtoDataType
