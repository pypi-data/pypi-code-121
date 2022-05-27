"""Binary (two reference arguments) transformations.

This module contains the base class and concrete classes for binary transformations,
those that can take two reference arguments (i.e. column or transformation names).
"""
from __future__ import annotations

from typing import Any, Union

import attr

from bitfount.transformations.base_transformation import Transformation


@attr.dataclass(kw_only=True)
class BinaryOperation(Transformation):
    """Base two-arg transformation.

    The base abstract class for all Binary Operation Transformations.

    Args:
        arg1: The first argument
        arg2: The second argument
    """

    arg1: Any
    arg2: Any


@attr.dataclass(kw_only=True)
class NumericBinaryOperation(BinaryOperation):
    """Base two-arg operation involving numbers.

    This class represents any BinaryOperation where arg2 can be numeric or a
    second column name such as addition, multiplication, etc.

    Args:
        arg1: The first argument (column name).
        arg2: The second argument (column name or numeric value).
    """

    arg1: str
    arg2: Union[float, str]


@attr.dataclass(kw_only=True)
class AdditionTransformation(NumericBinaryOperation):
    """Represents the addition of two columns or of a constant to a column."""

    _registry_name = "add"


@attr.dataclass(kw_only=True)
class SubtractionTransformation(NumericBinaryOperation):
    """Column subtracting transformation.

    Represents the subtraction of one column from another or of a constant from
    a column.
    """

    _registry_name = "subtract"


@attr.dataclass(kw_only=True)
class MultiplicationTransformation(NumericBinaryOperation):
    """Represents the multiplication of two columns or of a column and a constant."""

    _registry_name = "multiply"


@attr.dataclass(kw_only=True)
class DivisionTransformation(NumericBinaryOperation):
    """Column division transformation.

    Represents the division of one column by another or of one column by a constant.
    """

    _registry_name = "divide"


@attr.dataclass(kw_only=True)
class ComparisonTransformation(NumericBinaryOperation):
    """Represents the comparison between two columns or of one column and a constant.

    The resulting output should be:
    - -1 if arg1 < arg2
    - 0 if arg1 == arg2
    - +1 if arg1 > arg2
    """

    _registry_name = "compare"
