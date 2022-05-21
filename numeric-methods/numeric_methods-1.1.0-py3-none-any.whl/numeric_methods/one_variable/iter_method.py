from decimal import Decimal
from fractions import Fraction
from typing import Generator

from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.one_variable import ITER_METHOD_DOCS
from numeric_methods.mathematics import compare, convert, widest_type


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(ITER_METHOD_DOCS)
def iter_method(function, x: NUMBER, epsilon: NUMBER, c_criterion: NUMBER = 0.5) -> Generator[tuple[NUMBER] | NUMBER, None, None]:
    # Type normalization
    Number = widest_type(x, epsilon)
    x = convert(x, Number)
    epsilon = convert(epsilon, Number)
    c_criterion = convert(c_criterion, Number)

    step = 1
    next_x = function(x)
    yield step, next_x
    while not compare(abs(next_x - x), "<", (Number(1) - c_criterion) / c_criterion * epsilon):
        step += 1
        x = next_x
        next_x = function(x)
        yield step, next_x
    yield next_x
