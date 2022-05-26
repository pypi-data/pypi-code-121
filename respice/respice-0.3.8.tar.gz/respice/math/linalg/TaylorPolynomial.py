from functools import reduce
from math import factorial

import numpy.polynomial.polynomial as poly


def _extend_add(l, r):
    r[:len(l)] += l
    return r


class TaylorPolynomial:
    def __init__(self, fs, a):
        r"""
        Creates a new taylor polynomial from given function and derivative values.

        :param fs:
            Function and derivative values: :math:`f(x), f'(x), f''(x), \cdots`
        :param a:
            Expansion point.
        """
        self._c = reduce(_extend_add, (f / factorial(i) * poly.polyfromroots([a] * i)
                                       for i, f in enumerate(fs)))

    def __call__(self, x):
        return poly.polyval(x, self._c)

    def derivate(self, m=1):
        return poly.Polynomial(poly.polyder(self._c, m))
