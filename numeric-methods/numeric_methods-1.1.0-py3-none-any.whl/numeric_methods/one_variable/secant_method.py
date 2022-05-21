from decimal import Decimal
from fractions import Fraction
from typing import Generator

from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.one_variable import SECANT_METHOD_DOCS
from numeric_methods.mathematics import compare, convert, widest_type


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(SECANT_METHOD_DOCS)
def secant_method(function, x_prev: NUMBER, x: NUMBER, epsilon: NUMBER) -> Generator[tuple[NUMBER] | NUMBER, None, None]:
    # Type normalization
    Number = widest_type(x_prev, x, epsilon)
    x_prev = convert(x_prev, Number)
    x = convert(x, Number)
    epsilon = convert(epsilon, Number)

    step = 1
    next_x = x - (x - x_prev) * function(x) / (function(x) - function(x_prev))
    yield step, next_x
    while not compare(abs(next_x - x), "<", epsilon):
        step += 1
        x_prev = x
        x = next_x
        next_x = x - (x - x_prev) * function(x) / (function(x) - function(x_prev))
        yield step, next_x
    yield next_x
