from decimal import Decimal
from fractions import Fraction
from typing import Generator

from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.one_variable import FALSE_METHOD_DOCS
from numeric_methods.mathematics import compare, convert, widest_type


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(FALSE_METHOD_DOCS)
def false_method(function, double_differential, a: NUMBER, b: NUMBER, epsilon: NUMBER) -> Generator[tuple[NUMBER] | NUMBER, None, None]:
    # Type normalization
    Number = widest_type(a, b, epsilon)
    a = convert(a, Number)
    b = convert(b, Number)
    epsilon = convert(epsilon, Number)

    if compare(function(a) * double_differential(a), ">=", Number(0)):
        end, x = a, b
    elif compare(function(b) * double_differential(b), ">=", Number(0)):
        end, x = b, a
    else:
        raise ArithmeticError(f"Unable to choose x value from {a} and {b}: try to set another a and b")

    step = 1
    next_x = x - (end - x) * function(x) / (function(end) - function(x))
    yield step, next_x
    while not compare(abs(next_x - x), "<", epsilon):
        step += 1
        x = next_x
        next_x = x - (end - x) * function(x) / (function(end) - function(x))
        yield step, next_x
    yield next_x
