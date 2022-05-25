from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Dict, Generic, Optional, TypeVar, Union

from benchling_api_client.v2.beta.models.scalar_config_types import ScalarConfigTypes

ScalarType = TypeVar("ScalarType", bool, date, datetime, float, int, str)
ScalarModelType = Union[bool, date, datetime, float, int, str]


class ScalarDefinition(ABC, Generic[ScalarType]):
    """
    Scalar definition.

    Maps how ScalarConfigTypes values can be mapped into corresponding Python types.
    """

    @classmethod
    def init(cls):
        return cls()

    @abstractmethod
    def from_str(self, value: Optional[str]) -> Optional[ScalarType]:
        """
        From string.

        Given an optional string value of scalar configuration, produce an Optional instance of the
        specific ScalarType. For instance, converting str to int.
        """
        pass


class BoolScalar(ScalarDefinition[bool]):
    def from_str(self, value: Optional[str]) -> Optional[bool]:
        # Though the spec declares str, this is actually being sent in JSON as a real Boolean
        # So runtime check defensively
        if value is not None:
            if isinstance(value, bool):
                return value
            if value.lower() == "true":
                return True
            return False
        return None


class DateScalar(ScalarDefinition[date]):
    def from_str(self, value: Optional[str]) -> Optional[date]:
        return date.fromisoformat(value) if value is not None else None


class DateTimeScalar(ScalarDefinition[datetime]):
    def from_str(self, value: Optional[str]) -> Optional[datetime]:
        return datetime.strptime(value, self.expected_format()) if value is not None else None

    @staticmethod
    def expected_format() -> str:
        return "%Y-%m-%d %H:%M:%S %p"


class FloatScalar(ScalarDefinition[float]):
    def from_str(self, value: Optional[str]) -> Optional[float]:
        return float(value) if value is not None else None


class IntScalar(ScalarDefinition[int]):
    def from_str(self, value: Optional[str]) -> Optional[int]:
        return int(value) if value is not None else None


class TextScalar(ScalarDefinition[str]):
    def from_str(self, value: Optional[str]) -> Optional[str]:
        return value


DEFAULT_SCALAR_DEFINITIONS: Dict[ScalarConfigTypes, ScalarDefinition] = {
    ScalarConfigTypes.BOOLEAN: BoolScalar.init(),
    ScalarConfigTypes.DATE: DateScalar.init(),
    ScalarConfigTypes.DATETIME: DateTimeScalar.init(),
    ScalarConfigTypes.FLOAT: FloatScalar.init(),
    ScalarConfigTypes.INTEGER: IntScalar.init(),
    ScalarConfigTypes.TEXT: TextScalar.init(),
}
