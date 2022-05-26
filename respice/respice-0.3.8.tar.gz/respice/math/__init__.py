from fractions import Fraction
from functools import reduce

import numpy as np


def lcm(*numbers: int):
    """
    Returns the least common multiple of all given numbers.
    """
    return reduce(lambda x, y: np.lcm(x, y), numbers)


def flcm(*numbers: float, tol=2**-26, ignore_zeros=False):
    r"""
    Returns the least common multiple for floating point numbers.

    The least common multiple for floating point numbers is not exactly analogous to the
    normal case. Mainly, if rational numbers are considered, pure rational numbers would
    always produce :math:`\infty`. A viable solution only exists for rational numbers.

    In fact, computer floating point precision is always a rational numbers. However, due to
    rounding and other effects, it is usually desired to obtain an approximate value for the
    least common multiple. This can be controlled by the parameter `tol`.

    :param numbers:
        The floating point numbers to get the least common multiple from.
    :param tol:
        The tolerance. The floating point numbers are converted to `Fraction`s and rounded
        to the closes fraction fulfilling this tolerance.
    :param ignore_zeros:
        Whether to ignore zero values encountered in `numbers`.
    """
    fractional_limit = int(1 / tol)
    fractions = [Fraction(number).limit_denominator(fractional_limit)
                 for number in numbers]

    if ignore_zeros:
        fractions = [fraction for fraction in fractions if fraction.numerator != 0]

    numerators = np.fromiter((f.numerator for f in fractions), dtype=int)
    denominators = np.fromiter((f.denominator for f in fractions), dtype=int)

    common_denominator = lcm(*denominators)

    normalized_numerators = numerators * (common_denominator // denominators)

    return lcm(*normalized_numerators) / common_denominator
