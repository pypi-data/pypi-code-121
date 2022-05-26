from __future__ import annotations

import math
import operator
from typing import TYPE_CHECKING, Any, List, Union

from sila2.framework.abc.constraint import Constraint
from sila2.framework.constraints.comparison_constraint import ComparisonConstraint
from sila2.framework.data_types.date import Date
from sila2.framework.data_types.integer import Integer
from sila2.framework.data_types.real import Real
from sila2.framework.data_types.string import String
from sila2.framework.data_types.time import Time
from sila2.framework.data_types.timestamp import Timestamp
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class Set(Constraint):
    set_values: List[SetValue]

    def __init__(
        self, fdl_node, parent_feature: Feature, base_type: Union[String, Integer, Real, Date, Time, Timestamp]
    ):
        self.set_values = []
        for value_node in xpath_sila(fdl_node, "sila:Value"):
            self.set_values.append(SetValue.from_fdl_node(value_node, parent_feature, base_type))

    def validate(self, value: Any) -> bool:
        return any(set_value.validate(value) for set_value in self.set_values)

    @classmethod
    def from_fdl_node(
        cls, fdl_node, parent_feature: Feature, base_type: Union[String, Integer, Real, Date, Time, Timestamp]
    ) -> Set:
        return cls(fdl_node, parent_feature, base_type)

    def __repr__(self) -> str:
        if isinstance(self.set_values[0].base_type, Real):
            values = [v.reference_value for v in self.set_values]
        elif isinstance(self.set_values[0].base_type, Integer):
            values = [int(v.reference_value) for v in self.set_values]  # integer values are parsed as floats
        else:
            values = [v.value_from_xml for v in self.set_values]
        return f"{self.__class__.__name__}({values})"


class SetValue(ComparisonConstraint):
    def __init__(self, value: str, base_type: Union[String, Integer, Real, Date, Time, Timestamp]):
        super().__init__(base_type, float_equals if isinstance(base_type, Real) else operator.eq, value)

    @classmethod
    def from_fdl_node(
        cls, fdl_node, parent_feature: Feature, base_type: Union[String, Integer, Real, Date, Time, Timestamp]
    ):
        text = fdl_node.text
        if text is None and isinstance(base_type, String):
            text = ""
        return cls(text, base_type)


def float_equals(x: float, y: float) -> bool:
    return math.isclose(x, y, rel_tol=1e-3)
