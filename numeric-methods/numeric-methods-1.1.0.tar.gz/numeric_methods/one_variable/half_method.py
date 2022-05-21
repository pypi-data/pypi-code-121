from decimal import Decimal
from fractions import Fraction
from math import log2
from typing import Generator

from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.one_variable import HALF_METHOD_DOCS
from numeric_methods.mathematics import compare, convert, widest_type


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(HALF_METHOD_DOCS)
def half_method(function, a: NUMBER, b: NUMBER, epsilon: NUMBER) -> Generator[tuple[NUMBER] | NUMBER, None, None]:
    # Type normalization
    Number = widest_type(a, b, epsilon)
    a = convert(a, Number)
    b = convert(b, Number)
    epsilon = convert(epsilon, Number)

    if not compare(function(a) * function(b), "<", Number(0)):
        raise ArithmeticError(f"Value of function({a}) * function({b}) must be less then zero")

    x = 0
    for step in range(1, int(log2((b - a) / epsilon)) + 1):
        x = (a + b) / Number(2)
        y = function(x)

        yield step, a, b, x, y
        if compare(y, "==", Number(0)):
            yield x
            return
        elif compare(function(a) * y, "<", Number(0)):
            b = x
        elif compare(y * function(b), "<", Number(0)):
            a = x
        else:
            raise ArithmeticError(f"Unable to find ends with different signs: {function(a)}, {y}, {function(b)}")
    yield x
