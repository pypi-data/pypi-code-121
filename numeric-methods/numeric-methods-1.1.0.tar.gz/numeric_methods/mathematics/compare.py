from decimal import Decimal
from fractions import Fraction
from math import isclose

from numeric_methods.language import TRANSLATE
from numeric_methods.language.docs.mathematics import COMPARE_DOCS
from numeric_methods.mathematics import EPSILON


NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(COMPARE_DOCS)
def compare(lhs: NUMBER, kind: str, rhs: NUMBER) -> bool:
    epsilon = EPSILON.with_context(lhs)
    return {
        "==": lambda: isclose(lhs, rhs, abs_tol=epsilon),
        "<=": lambda: (lhs < rhs) or isclose(lhs, rhs, abs_tol=epsilon),
        ">=": lambda: (lhs > rhs) or isclose(lhs, rhs, abs_tol=epsilon),
        "<": lambda: lhs < rhs,
        ">": lambda: lhs > rhs
    }[kind]()
