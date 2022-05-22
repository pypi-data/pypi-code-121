#!/usr/bin/env python3

"""
pgt.mathf

Type: module

Description: A module that contains some useful math and ea_sing
    functions, and custom Pos and Size classes

Ea_sing functions (taken and adapted from https://ea_sings.net/):
    e_in__sin,     e_out__sin,     e_in_out__sin
    e_in_quad,    e_out_quad,    e_in_out_quad
    e_in_cubic,   e_out_cubic,   e_in_out_cubic
    e_in_quart,   e_out_quart,   e_in_out_quart
    e_in_quint,   e_out_quint,   e_in_out_quint
    e_in_exp,     e_out_exp,     e_in_out_exp
    e_in_circ,    e_out_circ,    e_in_out_circ
    e_in_back,    e_out_back,    e_in_out_back
    e_in_elastic, e_out_elastic, e_in_out_elastic
    e_in_bounce,  e_out_bounce,  e_in_out_bounce

    Every ea_sing function takes one argument (x) that is a floating
    point value between 0 (the start) and 1 (the end) and returns a
    value between 0 and 1 (elastic and back functions can return a
    value bigger than 1 or smaller than 0)

Additional functions:
    'clamp(value, min_, max_)': keeps value between min_ and max_
    'get_i(c1, c2)': returns the hypotenuse given the two catheti
    'get_c(i, c)': returns a cathetus given the hypotenuse and the other
        cathetus
    'sign(x)': returns -1 if x is negative, 1 if it's positive
    'quad_bezier(x, p0, p1, p2, p3)': a quadratic Bézier curve with p0
        being the start, p3 the end and p1 and p2 the two control points
    'safe_div(x, y)': a division that instead of raising a ZeroDivisionError,
        returns 0

Classes:
    - Pos
    - Size
"""
from __future__ import annotations

from math import (sqrt as _sqrt,
                  pi as _pi,
                  sin as _sin,
                  cos as _cos,
                  atan2 as _atan2,
                  tau as _tau)
try:
    from math import dist as _dist
except ImportError:
    # Taken from https://docs.python.org/3/library/math.html#math.dist
    _dist = lambda p, q: _sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))

clamp = lambda value, min_, max_: min(max(value, min_), max_)

get_i = lambda c1, c2: _sqrt(c1*c1 + c2*c2)
get_c = lambda i, c: _sqrt(i*i - c*c)

sign = lambda x: -1 if x < 0 else 1

quad_bezier = lambda x, p0, p1, p2, p3: p0 * (1 - x)**3 + \
                                        p1 * 3 * x * (1 - x)**2 + \
                                        p2 * 3 * x**2 * (1 - x) + \
                                        p3 * x**3


def safe_div(x, y):
    try:
        return x / y
    except ZeroDivisionError:
        return 0


# Sin
e_in_sin = lambda x: 1 - _cos((x * _pi) / 2)
e_out_sin = lambda x: _sin((x * _pi) / 2)
e_in_out_sin = lambda x: -(_cos(_pi * x) - 1) / 2

# Quadratic
e_in_quad = lambda x: x * x
e_out_quad = lambda x: 1 - (1 - x) * (1 - x)
e_in_out_quad = lambda x: 2 * x**2 if x < .5 else 1 - (-2 * x + 2)**2 / 2

# Cubic
e_in_cubic = lambda x: x ** 3
e_out_cubic = lambda x: 1 - (1 - x)**3
e_in_out_cubic = lambda x: 4 * x**3 if x < .5 else 1 - (-2 * x + 2)**3 / 2

# Quart
e_in_quart = lambda x: x ** 4
e_out_quart = lambda x: 1 - (1 - x)**4
e_in_out_quart = lambda x: 8 * x**4 if x < .5 else 1 - (-2 * x + 2)**4 / 2

# Quint
e_in_quint = lambda x: x ** 5
e_out_quint = lambda x: 1 - (1 - x)**5
e_in_out_quint = lambda x: 16 * x**5 if x < .5 else 1 - (-2 * x + 2)**5 / 2

# Exponential
e_in_exp = lambda x: 0 if x == 0 else 2 ** (10 * (x - 1))
e_out_exp = lambda x: 1 if x == 1 else 1 - 2 ** (-10 * x)
e_in_out_exp = lambda x: e_in_exp(x * 2) / 2 if x < .5 else \
                         e_out_exp(x * 2 - 1) / 2 + .5
# Circular
e_in_circ = lambda x: 1 - _sqrt(1 - x ** 2)
e_out_circ = lambda x: _sqrt(1 - (x - 1)**2)
e_in_out_circ = lambda x: e_in_circ(x * 2) / 2 if x < .5 else\
                          e_out_circ(x * 2 - 1) / 2 + .5
# Back
e_in_back = lambda x: 2.70158 * x**3 - 1.70158 * x**2
e_out_back = lambda x: 1 + 2.70158 * (x - 1)**3 + 1.70158 * (x - 1)**2
e_in_out_back = lambda x: e_in_back(x * 2) / 2 if x < .5 else\
                          e_out_back(x * 2 - 1) / 2 + .5


# Elastic
def e_in_elastic(x: float) -> float:
    if x in (0, 1): return x
    return -2 ** (10 * x - 10) * _sin((x * 10 - 10.75) * 2.09439)


def e_out_elastic(x: float) -> float:
    if x in (0, 1): return x
    return 2**(-10 * x) * _sin((x * 10 - 0.75) * 2.09439) + 1


e_in_out_elastic = lambda x: e_in_elastic(x * 2) / 2 if x < .5 else\
                             e_out_elastic(x * 2 - 1) / 2 + .5


# Bounce
def e_out_bounce(x: float) -> float:
    if x < 4 / 11:
        return 121 * x * x / 16
    elif x < 8 / 11:
        return (363 / 40 * x * x) - (99 / 10 * x) + 17 / 5
    elif x < 9 / 10:
        return (4356 / 361 * x * x) - (35442 / 1805 * x) + 16061 / 1805
    return (54 / 5 * x * x) - (513 / 25 * x) + 268 / 25


e_in_bounce = lambda x: 1 - e_out_bounce(1 - x)
e_in_out_bounce = lambda x: (1 - e_out_bounce(1 - 2 * x)) / 2 if x < .5 else \
                            (1 + e_out_bounce(2 * x - 1)) / 2


class Pos:
    """
    Pos

    Type: class

    Description: a class that simplifies working with coordinates

    Initialization: you can give two separate arguments or an iterable
        containing them, and they will be automatically be set

    Args:
        When the given two arguments, `x` is assigned to the first and
        `y` to the second.
        When given an iterable of length two, `x` is assigned to the
        first value and `y` to the second.
        In any other case both `x` and `y` get the value of the first
        argument
        >>> Pos(1, 2)
        Pos(1, 2)
        >>> Pos([1, 2])
        Pos(1, 2)
        >>> Pos(1)
        Pos(1, 1)
        >>> Pos(1, 2, 3)  # Here too many arguments are passed so the
        ...               # so the first value is taken
        Pos(1, 1)
        >>> Pos([1, 2, 3])  # Here happens the same thing, the iterable
        ...                 # is too long
        Pos([1, 2, 3], [1, 2, 3])

        No keyword arguments are accepted

    Attrs:
        'x' (Any): position on the x-axis
        'y' (Any): position on the y-axis

    Methods:
        'list()' (list): converts the position into a list
        'tuple()' (tuple): converts the position into a tuple
        'int()' (Pos): makes integers x and y
        'copy()' (Pos): returns a copy of itself
        'dot(other)' (int): returns the dot product between two positions
        'lerp(other, t)' (Pos): linear interpolation to 'other'
        'slerp(other, t, c=0)' (Pos): spherical interpolation to 'other'
            with 'c' being the center of the plane, defaults to (0, 0)
        'quad_bezier(other, p1, p2, t)' (Pos): quadratic Bézier curve to
            other with p1 and p2 being the two control points

    How operations work: if given an iterable with size 2 (Pos is an
        iterable) it will make the operation between x and the first
        object, and between y and the second object, else just adds
        the object to both x and y.
        >>> Pos(2, 3) + [10, 5]
        Pos(12, 8)
        >>> Pos(4, 4) - 3
        Pos(1, 1)
        # Pos can contain any type of object
        >>> Pos((1,), (2,)) + (1, 2)
        Pos((1, 1, 2), (2, 1, 2))

    """
    __slots__ = "x", "y"  # Saves quite a bit of memory

    def __init__(self, *args):
        try:
            x, y = args
        except (TypeError, ValueError):
            try:
                x, y = args[0]
            except (TypeError, ValueError):
                y = x = args[0]

        self.x = x
        self.y = y

    def __repr__(self):
        return f"Pos({self.x}, {self.y})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        try:
            x = self.x + other[0]
            y = self.y + other[1]
        except (TypeError, ValueError):
            try:
                x = self.x + other
                y = self.y + other
            except Exception:
                raise TypeError("unsupported operand type(s) for +: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __sub__(self, other):
        try:
            x = self.x - other[0]
            y = self.y - other[1]
        except (TypeError, ValueError):
            try:
                x = self.x - other
                y = self.y - other
            except Exception:
                raise TypeError("unsupported operand type(s) for -: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __mul__(self, other):
        try:
            x = self.x * other[0]
            y = self.y * other[1]
        except (TypeError, ValueError):
            try:
                x = self.x * other
                y = self.y * other
            except Exception:
                raise TypeError("unsupported operand type(s) for *: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __truediv__(self, other):
        try:
            x = self.x / other[0]
            y = self.y / other[1]
        except (TypeError, ValueError):
            try:
                x = self.x / other
                y = self.y / other
            except Exception:
                raise TypeError("unsupported operand type(s) for /: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __floordiv__(self, other):
        try:
            x = self.x // other[0]
            y = self.y // other[1]
        except (TypeError, ValueError):
            try:
                x = self.x // other
                y = self.y // other
            except Exception:
                raise TypeError("unsupported operand type(s) for //: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __mod__(self, other):
        try:
            x = self.x % other[0]
            y = self.y % other[1]
        except (TypeError, ValueError):
            try:
                x = self.x % other
                y = self.y % other
            except Exception:
                raise TypeError("unsupported operand type(s) for %: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __pow__(self, other):
        try:
            x = self.x ** other[0]
            y = self.y ** other[1]
        except (TypeError, ValueError):
            try:
                x = self.x ** other
                y = self.y ** other
            except Exception:
                raise TypeError("unsupported operand type(s) for **: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __lshift__(self, other):
        try:
            x = self.x << other[0]
            y = self.y << other[1]
        except (TypeError, ValueError):
            try:
                x = self.x << other
                y = self.y << other
            except Exception:
                raise TypeError("unsupported operand type(s) for <<: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __rshift__(self, other):
        try:
            x = self.x >> other[0]
            y = self.y >> other[1]
        except (TypeError, ValueError):
            try:
                x = self.x >> other
                y = self.y >> other
            except Exception:
                raise TypeError("unsupported operand type(s) for >>: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __and__(self, other):
        try:
            x = self.x & other[0]
            y = self.y & other[1]
        except (TypeError, ValueError):
            try:
                x = self.x & other
                y = self.y & other
            except Exception:
                raise TypeError("unsupported operand type(s) for &: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __or__(self, other):
        try:
            x = self.x | other[0]
            y = self.y | other[1]
        except (TypeError, ValueError):
            try:
                x = self.x | other
                y = self.y | other
            except Exception:
                raise TypeError("unsupported operand type(s) for |: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __xor__(self, other):
        try:
            x = self.x ^ other[0]
            y = self.y ^ other[1]
        except (TypeError, ValueError):
            try:
                x = self.x ^ other
                y = self.y ^ other
            except Exception:
                raise TypeError("unsupported operand type(s) for ^: "
                                f"'{self.__class__.__name__}' "
                                f"and '{other.__class__.__name__}'")
        return self.c(x, y)

    def __invert__(self):
        return self.c(~self.x, ~self.y)

    def __round__(self, ndigits=None):
        return self.c(round(self.x, ndigits), round(self.y, ndigits))

    def __abs__(self):
        return self.c(abs(self.x), abs(self.y))

    def __neg__(self): return self.c(-self.x, -self.y)

    def __floor__(self): return self.c(self.x.__floor__(), self.y.__floor__())

    def __ceil__(self): return self.c(self.x.__ceil__(), self.y.__ceil__())

    def __trunc__(self, ndigits):
        return self.c(self.x.__trunc__(ndigits), self.y.__trunc__(ndigits))

    def __radd__(self, other): return self.__add__(other)

    def __rsub__(self, other): return -self.__sub__(-other)

    def __rmul__(self, other): return self.__mul__(other)

    def __rand__(self, other): return self.__and__(other)

    def __ror__(self, other): return self.__or__(other)

    def __rxor__(self, other): return self.__xor__(other)

    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
        else: raise IndexError(f"index {i} out of range for size 2")

    def __setitem__(self, i, value):
        if i == 0: self.x = value
        elif i == 1: self.y = value
        else: raise IndexError(f"index {i} out of range for size 2")

    def __len__(self): return 2

    def __hash__(self):
        return self.tuple().__hash__()

    def __eq__(self, other):
        try:
            return self.x == other[0] and self.y == other[1]
        except (TypeError, ValueError):
            return self.x == other and self.y == other

    def __ne__(self, other):
        try:
            return self.x != other[0] or self.y != other[1]
        except (TypeError, ValueError):
            return self.x != other or self.y != other

    def __gt__(self, other):
        try:
            return self.x > other[0] and self.y > other[1]
        except (TypeError, ValueError):
            return self.x > other and self.y > other

    def __lt__(self, other):
        try:
            return self.x < other[0] and self.y < other[1]
        except (TypeError, ValueError):
            return self.x < other and self.y < other

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    def list(self) -> list:
        return [self.x, self.y]

    def tuple(self) -> tuple:
        return self.x, self.y

    def int(self) -> Pos:
        return self.c(int(self.x), int(self.y))

    def copy(self) -> Pos:
        return self.c(self.x, self.y)

    def dot(self, other) -> float:
        product = self * other
        return product.x + product.y

    def lerp(self, other, t) -> Pos:
        return self * (1 - t) + Pos(other) * t

    def slerp(self, other, t, c=0) -> Pos:
        c = Pos(c)
        pos1 = self.copy() - c
        pos2 = Pos(other) - c

        mid = (pos1 + pos2) / 2
        diff = pos2 - pos1
        try:
            m = diff.x / diff.y
        except ZeroDivisionError:
            center = Pos(mid.x, 0)
        else:
            try:
                q = mid.y + m * mid.x
                if q / m > q:
                    center = Pos(q / m, 0)
                else:
                    center = Pos(0, q)
            except ZeroDivisionError:
                center = Pos(0, (pos1.y + pos2.y) * 0.5)

        radius = _dist(pos1, center)

        try:
            pos1 = (pos1 - center) / radius
            pos2 = (pos2 - center) / radius
        except ZeroDivisionError:
            pos1 = pos2 = Pos(0)

        angle1 = _atan2(pos1.y, pos1.x)
        angle2 = _atan2(pos2.y, pos2.x)
        ang_diff = abs(angle1 - angle2)

        # if ang_diff > 180°, use the other arc
        if ang_diff > _pi:
            t *= -(_tau - ang_diff) / ang_diff
        angle = angle1 * (1 - t) + angle2 * t
        return self.c(_cos(angle), _sin(angle)) * radius + center + c

    def quad_bezier(self, other, p1, p2, t) -> Pos:
        return quad_bezier(t, self, p1, p2, other)

    @classmethod
    def c(cls, *args):
        return cls(*args)


class Size(Pos):
    """
    Size

    Type: class

    Description: it's the same as Pos and adds two attributes

    Attrs:
        'w' (Any): width, the same as 'x'
        'h' (Any): width, the same as 'y'
    """
    @property
    def w(self): return self.x
    @w.setter
    def w(self, value): self.x = value

    @property
    def h(self): return self.y
    @h.setter
    def h(self, value): self.y = value

    def __repr__(self):
        return f"Size({self.w}, {self.h})"
