from __future__ import annotations

from enum import Enum
from math import isclose
from typing import TYPE_CHECKING, Iterable, NamedTuple, Optional, Tuple, TypeVar, Union

from sila2.framework.abc.constraint import Constraint
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


T = TypeVar("T", bound=Union[int, float])


class Unit(Constraint[T]):
    label: str
    factor: float
    offset: float
    unit_components: Tuple[UnitComponent, ...]

    def __init__(
        self,
        label: str,
        factor: float,
        offset: float,
        unit_components: Optional[Iterable[UnitComponent]] = None,
    ):
        self.label = label
        self.factor = factor
        self.offset = offset
        self.unit_components = () if unit_components is None else tuple(unit_components)

    def validate(self, value: T) -> bool:
        return True

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> Unit:
        label = xpath_sila(fdl_node, "sila:Label/text()")[0]
        factor = float(xpath_sila(fdl_node, "sila:Factor/text()")[0])
        offset = float(xpath_sila(fdl_node, "sila:Offset/text()")[0])

        unit_components = []
        for comp_node in xpath_sila(fdl_node, "sila:UnitComponent"):
            unit_str = xpath_sila(comp_node, "sila:SIUnit/text()")[0]
            exponent = getattr(SIUnit, xpath_sila(comp_node, "sila:SIUnit/text()")[0])
            unit_components.append(UnitComponent(getattr(SIUnit, unit_str), exponent))

        return cls(label, factor, offset, unit_components)

    def __repr__(self) -> str:
        factor_str = "" if isclose(self.factor, 1) else f" * {self.factor}"
        offset_str = "" if isclose(self.offset, 0) else f" + {self.offset}"
        return f"Unit({self.label!r}: '{' * '.join(str(u) for u in self.unit_components)}{factor_str}{offset_str}')"


class UnitComponent(NamedTuple):
    si_unit: SIUnit
    exponent: int

    def __str__(self) -> str:
        if self.exponent == 1:
            return self.si_unit.value
        return f"{self.si_unit.value}^{self.exponent}"


class SIUnit(Enum):
    Ampere = "A"
    Candela = "cd"
    Dimensionless = ""
    Kelvin = "K"
    Kilogram = "kg"
    Meter = "m"
    Mole = "mol"
    Second = "s"
