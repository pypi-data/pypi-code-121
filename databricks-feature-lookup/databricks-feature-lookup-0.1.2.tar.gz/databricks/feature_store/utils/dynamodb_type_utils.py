""" Defines the type conversion classes from pandas to dynamodb and vice versa.
"""
import calendar
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal, Context

import numpy as np
import pandas as pd

from databricks.feature_store.utils.dynamodb_utils import return_if_none, return_if_nan


class DynamoDbPandasTypeConverter(ABC):
    @staticmethod
    @abstractmethod
    def to_dynamodb(value):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def to_pandas(value):
        raise NotImplementedError


class DynamoDbPandasBooleanTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.bool) -> int:
        if value:
            return 1
        else:
            return 0

    @staticmethod
    @return_if_none
    def to_pandas(value: Decimal) -> np.bool:
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            raise ValueError("Unsupported value for bool: " + str(value))


class DynamoDbPandasShortTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.int16) -> int:
        return int(value)

    @staticmethod
    @return_if_none
    @return_if_nan
    def to_pandas(value: Decimal) -> np.int16:
        # TODO (ML-20967): We currently return an np.int16 with best effort if there are no undefined values.
        #  However, if a np.nan is provided, we will return np.nan which is a np.float instead.
        return np.int16(value)


class DynamoDbPandasIntTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.int32) -> int:
        return int(value)

    @staticmethod
    @return_if_none
    @return_if_nan
    def to_pandas(value: Decimal) -> np.int32:
        # TODO (ML-20967): We currently return an np.int32 with best effort if there are no undefined values.
        #  However, if a np.nan is provided, we will return np.nan which is a np.float instead.
        return np.int32(value)


class DynamoDbPandasLongTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.int64) -> int:
        return int(value)

    @staticmethod
    @return_if_none
    @return_if_nan
    def to_pandas(value: Decimal) -> np.int64:
        # TODO (ML-20967): We currently return an np.int64 with best effort if there are no undefined values.
        #  However, if a np.nan is provided, we will return np.nan which is a np.float instead.
        return np.int64(value)


class DynamoDbPandasStringTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.object) -> str:
        return str(value)

    @staticmethod
    @return_if_none
    def to_pandas(value: str) -> np.object:
        return value


class DynamoDbPandasFloatTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.float32) -> float:
        return float(value)

    @staticmethod
    @return_if_none
    def to_pandas(value: Decimal) -> np.float32:
        return np.float32(value)


class DynamoDbPandasDoubleTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.float64) -> float:
        return float(value)

    @staticmethod
    @return_if_none
    def to_pandas(value: Decimal) -> np.float64:
        return np.float64(value)


class DynamoDbPandasTimestampTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: str) -> int:
        dt = pd.Timestamp(value).floor("us")
        return int(dt.timestamp() * 1e6)

    @staticmethod
    @return_if_none
    def to_pandas(value: int) -> pd.Timestamp:
        return pd.Timestamp(int(value), unit="us")


class DynamoDbPandasDateTypeConverter(DynamoDbPandasTypeConverter):
    """
    This converter will allow but truncate all inexact dates to the most recent date.
    """

    @staticmethod
    def to_dynamodb(value: str) -> int:
        dt = pd.Timestamp(value).date()
        return calendar.timegm(dt.timetuple())

    @staticmethod
    @return_if_none
    def to_pandas(value: int) -> date:
        return pd.Timestamp(int(value), unit="s").date()


class DynamoDbPandasBinaryTypeConverter(DynamoDbPandasTypeConverter):
    @staticmethod
    def to_dynamodb(value: np.object) -> bytearray:
        return bytearray(value)

    @staticmethod
    @return_if_none
    # TODO value is boto3 object
    def to_pandas(value) -> np.object:
        return bytearray(value.value)


class DynamoDbPandasDecimalTypeConverter(DynamoDbPandasTypeConverter):
    def __init__(self, precision) -> None:
        self._precision = precision

    @staticmethod
    def to_dynamodb(value):
        raise NotImplementedError

    @return_if_none
    def to_pandas(self, value: Decimal) -> Decimal:
        # Set the Decimal context with the appropriate precision
        context = Context(prec=self._precision)
        return context.create_decimal(value)


class DynamoDbPandasArrayTypeConverter(DynamoDbPandasTypeConverter):
    def __init__(self, element_converter) -> None:
        self._element_converter = element_converter

    @staticmethod
    def to_dynamodb(value):
        raise NotImplementedError

    @return_if_none
    def to_pandas(self, value: list) -> np.ndarray:
        if value is not None:
            return np.array(
                [
                    self._element_converter.to_pandas(x) if x is not None else x
                    for x in value
                ]
            )


class DynamoDbPandasMapTypeConverter(DynamoDbPandasTypeConverter):
    def __init__(self, key_converter, value_converter) -> None:
        self._key_converter = key_converter
        self._value_converter = value_converter

    @staticmethod
    def to_dynamodb(value):
        raise NotImplementedError

    @return_if_none
    def to_pandas(self, value: dict) -> np.object:
        if value is not None:
            return {
                self._key_converter.to_pandas(k): (
                    self._value_converter.to_pandas(v) if v is not None else v
                )
                for k, v in value.items()
            }
