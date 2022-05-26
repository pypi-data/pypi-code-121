from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Union

from sila2.framework.constraints.comparison_constraint import ComparisonConstraint
from sila2.framework.data_types.date import Date
from sila2.framework.data_types.integer import Integer
from sila2.framework.data_types.real import Real
from sila2.framework.data_types.string import String
from sila2.framework.data_types.time import Time
from sila2.framework.data_types.timestamp import Timestamp

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class MinimalInclusive(ComparisonConstraint):
    def __init__(self, value: str, base_type: Union[String, Integer, Real, Date, Time, Timestamp]):
        super().__init__(base_type, operator.le, value)

    @classmethod
    def from_fdl_node(
        cls, fdl_node, parent_feature: Feature, base_type: Union[String, Integer, Real, Date, Time, Timestamp]
    ) -> MinimalInclusive:
        return cls(fdl_node.text, base_type)
