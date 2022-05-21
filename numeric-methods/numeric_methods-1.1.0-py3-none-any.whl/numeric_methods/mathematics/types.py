from decimal import Decimal
from fractions import Fraction
from typing import Type


from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.mathematics import CONVERT_DOCS, WIDEST_TYPE_DOCS


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(CONVERT_DOCS)
def convert(value: NUMBER, into: Type[NUMBER]) -> NUMBER:
    if isinstance(value, Fraction) and into == Decimal:
        return Decimal(value.numerator) / Decimal(value.denominator)
    return into(value)


@TRANSLATE.documentation(WIDEST_TYPE_DOCS)
def widest_type(*instances: NUMBER) -> NUMBER:
    return max(
        (type(instance) for instance in instances),
        key=lambda t: {float: 0, Decimal: 1, Fraction: 2}.get(t, -1)
    )

