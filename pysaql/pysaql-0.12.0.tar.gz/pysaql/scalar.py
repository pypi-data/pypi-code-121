"""Contains definition of a scalar"""

from __future__ import annotations

from abc import ABC
import operator
from typing import Any, Callable, Optional, Protocol, Sequence, Union

from .expression import Expression
from .util import escape_identifier, stringify

# Mapping from operator function to its string representation in SAQL
OPERATOR_STRINGS = {
    operator.add: "+",
    operator.and_: "&&",
    operator.contains: "in",
    operator.eq: "==",
    operator.ge: ">=",
    operator.gt: ">",
    operator.inv: "!",
    operator.is_: "is",
    operator.is_not: "is not",
    operator.le: "<=",
    operator.lt: "<",
    operator.mod: "%",
    operator.mul: "*",
    operator.ne: "!=",
    operator.neg: "-",
    operator.or_: "||",
    operator.sub: "-",
    operator.truediv: "/",
}


class BooleanOperation(Expression):
    """Mixin that defines boolean comparison methods"""

    def __and__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `and` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.and_, self, obj)

    def __or__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `or` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.or_, self, obj)

    def __invert__(self) -> UnaryOperation:
        """Creates a unary operation using the `inv` operator

        Returns:
            unary operation

        """
        return UnaryOperation(operator.inv, self)


class Scalar(BooleanOperation, ABC):
    """Represents a scalar expression"""

    def __eq__(self, obj: Any) -> BinaryOperation:  # type: ignore[override]
        """Creates a binary operation using the `eq` or `is` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        op = operator.is_ if obj is None else operator.eq
        return BinaryOperation(op, self, obj)

    def __ne__(self, obj: Any) -> BinaryOperation:  # type: ignore[override]
        """Creates a binary operation using the `ne` or `is_not` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        op = operator.is_not if obj is None else operator.ne
        return BinaryOperation(op, self, obj)

    def __lt__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `lt` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.lt, self, obj)

    def __le__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `le` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.le, self, obj)

    def __gt__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `gt` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.gt, self, obj)

    def __ge__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `ge` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.ge, self, obj)

    def __add__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `add` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.add, self, obj)

    def __sub__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `sub` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.sub, self, obj)

    def __mul__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `mul` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.mul, self, obj)

    def __truediv__(self, obj: Any) -> BinaryOperation:
        """Creates a binary operation using the `truediv` operator

        Args:
            obj: Object to use for the right operand

        Returns:
            binary operation

        """
        return BinaryOperation(operator.truediv, self, obj)

    def __neg__(self) -> UnaryOperation:
        """Creates a unary operation using the `neg` operator

        Returns:
            unary operation

        """
        return UnaryOperation(operator.neg, self)

    def in_(self, iterable: Union[Sequence, Expression]) -> BinaryOperation:
        """Creates a binary operation using the `contains` operator

        Args:
            iterable: Iterable that may contain the current scalar

        Returns:
            binary operation

        """
        return BinaryOperation(operator.contains, self, iterable)


class BinaryOperation(Scalar):
    """Represents a binary operation"""

    def __init__(self, op: Callable, left: Any, right: Any, wrap: bool = False) -> None:
        """Initializer

        Args:
            op: Operator function that accepts two operands
            left: Left operand
            right: Right operand
            wrap: Flag that indicates whether the stringified operation should be
                wrapped in parentheses to denote precedence. Defaults to False.

        """
        super().__init__()
        if op not in OPERATOR_STRINGS:
            operators = ", ".join(f"operator.{fn.__name__}" for fn in OPERATOR_STRINGS)
            raise ValueError(f"Operator must be one of: {operators}. Provided: {op}")
        self.op = op
        self.left = left
        self.right = right
        self.wrap = wrap
        for operand in (self.left, self.right):
            if isinstance(operand, BinaryOperation):
                operand.wrap = True

    def to_string(self) -> str:
        """Cast the binary operation to a string"""
        s = f"{stringify(self.left)} {OPERATOR_STRINGS[self.op]} {stringify(self.right)}"
        if self.wrap:
            s = f"({s})"

        return s


class UnaryOperation(Scalar):
    """Represents a unary operation"""

    def __init__(self, op: Callable, value: Any) -> None:
        """Initializer

        Args:
            op: Operator function that accepts one argument
            value: Value to pass to the operator

        """
        super().__init__()
        self.op = op
        self.value = value

    def to_string(self) -> str:
        """Cast the unary operation to a string"""
        return f"{OPERATOR_STRINGS[self.op]} {stringify(self.value)}"


class StreamProtocol(Protocol):
    """Protocol definition for a stream interface

    This is defined to prevent recursive dependencies
    """

    @property
    def ref(self) -> str:
        """Stream reference in the SAQL query"""
        pass


class field(Scalar):
    """Represents a field (column) in the data stream"""

    def __init__(self, name: str, stream: Optional[StreamProtocol] = None) -> None:
        """Represents a field (column) in the data stream

        Args:
            name: Name of the field
            stream: Optional stream. Providing a stream indicates the field
                reference string should include a stream prefix to distinguish them from
                fields in other streams.

        """
        super().__init__()
        self.name = name
        self.stream = stream

    def to_string(self) -> str:
        """Cast the field to a string"""
        prefix = f"{self.stream.ref}." if self.stream else ""
        return prefix + escape_identifier(self.name)


class literal(Scalar):
    """Represents a literal value"""

    def __init__(self, value: Any) -> None:
        """Represents a literal value

        Args:
            value: Literal value

        """
        super().__init__()
        self.value = value

    def to_string(self) -> str:
        """Cast the literal to a string"""
        return stringify(self.value)
