from __future__ import annotations

from enum import auto, Enum, unique
from typing import Optional, TypedDict


@unique
class StrEnum(str, Enum):
    """An str-comparable enumeration"""
    def _generate_next_value_(name, start, count, last_values):
        return name


class PoolMode(StrEnum):
    """
    PoolMode is an enum type which defines the mode of the pool.
    """
    STANDARD = auto()
    OPENING = auto()
    WINTER = auto()
    INITIALIZATION = auto()


class MeasureMode(StrEnum):
    """
    MeasureMode is an enum type which defines the mode of a measure.
    """
    standard = auto()
    live = auto()
    maintenance = auto()
    manual = auto()
    backup = auto()
    gateway = auto()


IsoDatetime = str

class Measure(TypedDict):
    """
    Measure is a typed dictionary which contains the data of a measure.
    """
    temperature: float
    ph: float
    orp: float
    mode: MeasureMode
    isValid: bool
    measuredAt: IsoDatetime


class Advice(TypedDict):
    filtrationDuration: Optional[float]


class Pool(TypedDict):
    id: str
    title: str
    mode: PoolMode
    hasAnActionRequired: bool
    latestMeasure: Optional[Measure]
    advice: Advice
