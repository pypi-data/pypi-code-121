from collections import namedtuple
from enum import Enum
from typing import List
from typing import Union

from pyspark.sql import types as spark_types
from typeguard import typechecked

from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper


class DataType(namedtuple("DataType", ["name", "spark_type"]), Enum):
    Int64 = "int64", spark_types.LongType()
    Float32 = "float32", spark_types.FloatType()
    Float64 = "float64", spark_types.DoubleType()
    String = "string", spark_types.StringType()
    Bool = "bool", spark_types.BooleanType()
    Timestamp = "timestamp", spark_types.TimestampType()


class Array:
    def __init__(self, dtype: DataType):
        self.dtype = dtype

    @property
    def spark_type(self) -> spark_types.ArrayType:
        return spark_types.ArrayType(self.dtype.spark_type)


Int64 = DataType.Int64
Float32 = DataType.Float32
Float64 = DataType.Float64
String = DataType.String
Bool = DataType.Bool
Timestamp = DataType.Timestamp


@typechecked
class Field:
    def __init__(
        self,
        name: str,
        dtype: Union[DataType, Array],
    ):
        self.name = name
        self.dtype = dtype

    def to_spark_struct_field(self) -> spark_types.StructField:
        return spark_types.StructField(self.name, self.dtype.spark_type)


def to_spark_schema_wrapper(field_list: List[Field]) -> SparkSchemaWrapper:
    s = spark_types.StructType([field.to_spark_struct_field() for field in field_list])
    return SparkSchemaWrapper(s)
