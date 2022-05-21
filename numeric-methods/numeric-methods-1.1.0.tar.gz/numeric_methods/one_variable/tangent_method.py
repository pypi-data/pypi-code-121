from decimal import Decimal
from fractions import Fraction
from typing import Generator

from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.one_variable import TANGENT_METHOD_DOCS
from numeric_methods.mathematics import compare, convert, widest_type


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(TANGENT_METHOD_DOCS)
def tangent_method(function, differential, a: NUMBER, b: NUMBER, epsilon: NUMBER, x: NUMBER = None, double_differential=None) -> Generator[tuple[NUMBER] | NUMBER, None, None]:
    # Type normalization
    Number = widest_type(a, b, epsilon)
    if x is not None:
        Number = widest_type(Number, x)
    elif double_differential is not None:
        if compare(function(a) * double_differential(a), ">=", Number(0)):
            x = a
        elif compare(function(b) * double_differential(b), ">=", Number(0)):
            x = b
        else:
            raise ArithmeticError(f"Unable to choose x value from {a} and {b}: try to set another a and b or choose x manually")
    else:
        raise ValueError("Neither x nor double_differential were set: one of these parameters must be specified")

    a = convert(a, Number)
    b = convert(b, Number)
    epsilon = convert(epsilon, Number)
    x = convert(x, Number)

    if not compare(function(a) * function(b), "<", Number(0)):
        raise ArithmeticError(f"Value of function({a}) * function({b}) must be less then zero")

    step = 1
    x = b
    next_x = x - function(x) / differential(x)
    yield step, next_x
    while not compare(abs(next_x - x), "<", epsilon):
        step += 1
        x = next_x
        next_x = x - function(x) / differential(x)
        yield step, next_x
    yield next_x
