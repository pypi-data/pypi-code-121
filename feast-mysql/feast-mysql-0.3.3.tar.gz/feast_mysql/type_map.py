from typing import Dict

import pyarrow as pa

from feast import ValueType
from pymysql import FIELD_TYPE


def arrow_type_string_to_mysql_type(t_str: str) -> str:
    try:
        if t_str.startswith("timestamp"):
            return "timestamptz" if "tz=" in t_str else "timestamp"
        return {
            "null": "null",
            "bool": "boolean",
            "int8": "tinyint",
            "int16": "smallint",
            "int32": "int",
            "int64": "bigint",
            "list<item: int32>": "int[]",
            "list<item: int64>": "bigint[]",
            "list<item: bool>": "boolean[]",
            "list<item: double>": "double[]",
            "uint8": "tinyint unsigned",
            "uint16": "smallint unsigned",
            "uint32": "int unsigned",
            "uint64": "bigint unsigned",
            "float": "float",
            "double": "double",
            "binary": "binary",
            "string": "longtext",
        }[t_str]
    except KeyError:
        raise ValueError(f"Unsupported type: {t_str}")


def mysql_type_to_arrow_type_string(t_str: str) -> str:
    try:
        if t_str.startswith("timestamp"):
            return "timestamptz" if "tz=" in t_str else "timestamp"
        return {
            "null": "null",
            "boolean": "bool",
            "tinyint": "int8",
            "smallint": "int16",
            "int": "int32",
            "bigint": "int64",
            "bigint[]": "list<item: int64>",
            "decimal": "double",
            "float": "float",
            "double": "double",
            "binary": "binary",
            "longtext": "string",
        }[t_str]
    except KeyError:
        raise ValueError(f"Unsupported type: {t_str}")


def mysql_type_to_feast_value_type(type_str: str) -> ValueType:
    type_map: Dict[str, ValueType] = {
        "boolean": ValueType.BOOL,
        "blob": ValueType.BYTES,
        "char": ValueType.STRING,
        "bigint": ValueType.INT64,
        "smallint": ValueType.INT32,
        "int": ValueType.INT32,
        "float": ValueType.DOUBLE,
        "double": ValueType.DOUBLE,
        "boolean[]": ValueType.BOOL_LIST,
        "blob[]": ValueType.BYTES_LIST,
        "char[]": ValueType.STRING_LIST,
        "smallint[]": ValueType.INT32_LIST,
        "int[]": ValueType.INT32_LIST,
        "longtext": ValueType.STRING,
        "longtext[]": ValueType.STRING_LIST,
        "character[]": ValueType.STRING_LIST,
        "bigint[]": ValueType.INT64_LIST,
        "float[]": ValueType.DOUBLE_LIST,
        "double[]": ValueType.DOUBLE_LIST,
        "character": ValueType.STRING,
        "varchar": ValueType.STRING,
        "date": ValueType.UNIX_TIMESTAMP,
        "time without time zone": ValueType.UNIX_TIMESTAMP,
        "timestamp without time zone": ValueType.UNIX_TIMESTAMP,
        "timestamp without time zone[]": ValueType.UNIX_TIMESTAMP_LIST,
        "date[]": ValueType.UNIX_TIMESTAMP_LIST,
        "time without time zone[]": ValueType.UNIX_TIMESTAMP_LIST,
        "timestamp with time zone": ValueType.UNIX_TIMESTAMP,
        "timestamp with time zone[]": ValueType.UNIX_TIMESTAMP_LIST,
        "numeric[]": ValueType.DOUBLE_LIST,
        "numeric": ValueType.DOUBLE,
        "uuid": ValueType.STRING,
        "uuid[]": ValueType.STRING_LIST,
    }
    value = (
        type_map[type_str.lower()]
        if type_str.lower() in type_map
        else ValueType.UNKNOWN
    )
    if value == ValueType.UNKNOWN:
        print("unknown type:", type_str)
    return value


def feast_value_type_to_arrow_type(feast_type: ValueType) -> pa.DataType:
    type_map = {
        ValueType.INT32: pa.int32(),
        ValueType.INT64: pa.int64(),
        ValueType.DOUBLE: pa.float64(),
        ValueType.FLOAT: pa.float32(),
        ValueType.STRING: pa.string(),
        ValueType.BYTES: pa.binary(),
        ValueType.BOOL: pa.bool_(),
        ValueType.UNIX_TIMESTAMP: pa.timestamp("us"),
        ValueType.INT32_LIST: pa.list_(pa.int32()),
        ValueType.INT64_LIST: pa.list_(pa.int64()),
        ValueType.DOUBLE_LIST: pa.list_(pa.float64()),
        ValueType.FLOAT_LIST: pa.list_(pa.float32()),
        ValueType.STRING_LIST: pa.list_(pa.string()),
        ValueType.BYTES_LIST: pa.list_(pa.binary()),
        ValueType.BOOL_LIST: pa.list_(pa.bool_()),
        ValueType.UNIX_TIMESTAMP_LIST: pa.list_(pa.timestamp("us")),
        ValueType.NULL: pa.null(),
    }
    return type_map[feast_type]


def mysql_type_code_to_mysql_type(code: int) -> str:
    return {
        FIELD_TYPE.DECIMAL: "",
        FIELD_TYPE.TINY: "char",
        FIELD_TYPE.SHORT: "smallint",
        FIELD_TYPE.LONG: "int",
        FIELD_TYPE.FLOAT: "float",
        FIELD_TYPE.DOUBLE: "double",
        FIELD_TYPE.NULL: "",
        FIELD_TYPE.TIMESTAMP: "",
        FIELD_TYPE.LONGLONG: "",
        FIELD_TYPE.INT24: "",
        FIELD_TYPE.DATE: "date",
        FIELD_TYPE.TIME: "",
        FIELD_TYPE.DATETIME: "",
        FIELD_TYPE.YEAR: "",
        FIELD_TYPE.NEWDATE: "",
        FIELD_TYPE.VARCHAR: "varchar",
        FIELD_TYPE.BIT: "boolean",
        FIELD_TYPE.JSON: "",
        FIELD_TYPE.NEWDECIMAL: "",
        FIELD_TYPE.ENUM: "",
        FIELD_TYPE.SET: "",
        FIELD_TYPE.TINY_BLOB: "",
        FIELD_TYPE.MEDIUM_BLOB: "",
        FIELD_TYPE.LONG_BLOB: "",
        FIELD_TYPE.BLOB: "blob",
        FIELD_TYPE.VAR_STRING: "varchar",
        FIELD_TYPE.STRING: "varchar",
        FIELD_TYPE.GEOMETRY: "",
        FIELD_TYPE.CHAR: "char",
        FIELD_TYPE.INTERVAL: "",
    }[code]
