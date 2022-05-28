"""
    Geometry related functions and classes.

    Includes functions for making pretty axis labels.

    Includes IntPoint, IntSize, and IntRect classes.
"""

from __future__ import annotations

# standard libraries
import dataclasses
import math
import typing

# third party libraries
# None


RectIntTuple = typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
PointIntTuple = typing.Tuple[int, int]
SizeIntTuple = typing.Tuple[int, int]
IntRectTuple = typing.Union["IntRect", RectIntTuple]
IntPointTuple = typing.Union["IntPoint", PointIntTuple]
IntSizeTuple = typing.Union["IntSize", SizeIntTuple]

RectFloatTuple = typing.Tuple[typing.Tuple[float, float], typing.Tuple[float, float]]
PointFloatTuple = typing.Tuple[float, float]
SizeFloatTuple = typing.Tuple[float, float]
FloatRectTuple = typing.Union["FloatRect", RectFloatTuple]
FloatPointTuple = typing.Union["FloatPoint", PointFloatTuple]
FloatSizeTuple = typing.Union["FloatSize", SizeFloatTuple]


def make_pretty(val: float, rounding: bool) -> typing.Tuple[float, float]:
    """Make a pretty number, using algorithm from Paul Heckbert, extended to handle negative numbers."""
    val = float(val)
    if not val > 0.0 and not val < 0.0:
        return 0.0, 0  # make sense of values that are neither greater or less than 0.0
    if math.isfinite(val):
        factor10 = math.pow(10.0, math.floor(math.log10(abs(val))))
    else:
        return 0.0, 0
    val_norm = abs(val) / factor10  # between 1 and 10
    if val_norm < 1.0:
        val_norm = val_norm * 10
        factor10 = factor10 // 10
    if rounding:
        if val_norm < 1.5:
            val_norm = 1.0
        elif val_norm < 3.0:
            val_norm = 2.0
        elif val_norm < 7.0:
            val_norm = 5.0
        else:
            val_norm = 10.0
    else:
        if val_norm <= 1.0:
            val_norm = 1.0
        elif val_norm <= 2.0:
            val_norm = 2.0
        elif val_norm <= 5.0:
            val_norm = 5.0
        else:
            val_norm = 10.0
    return math.copysign(val_norm * factor10, val), factor10


def make_pretty2(val: float, rounding: bool) -> float:
    """Make a pretty number, using algorithm from Paul Heckbert, extended to handle negative numbers."""
    return make_pretty(val, rounding)[0]


def arange(start: float, stop: float, step: float) -> typing.Sequence[float]:
    return [start + x * step for x in range(math.ceil((stop - start) / step))]


def make_pretty_range2(value_low: float, value_high: float, ticks: int = 5, logarithmic: bool = False) -> typing.Tuple[float, float, typing.Sequence[float], float, int, float]:
    """Returns minimum, maximum, list of tick values, division, and precision.

    Value high and value low specify the data range.

    Tight indicates whether the pretty range should extend to the data (tight)
        or beyond the data (loose).

    Ticks is the approximate number of ticks desired, including the ends (if loose).

    Useful links:
        http://tog.acm.org/resources/GraphicsGems/gems/Label.c
        https://svn.r-project.org/R/trunk/src/appl/pretty.c
        http://www.mathworks.com/help/matlab/ref/axes_props.html
    """

    # adjust value_low, value_high to be floats in increasing order
    value_low = float(value_low)
    value_high = float(value_high)
    value_low, value_high = min(value_low, value_high), max(value_low, value_high)

    # check for small range
    if value_high == value_low:
        return value_low, value_low, [value_low], 0, 0, 0

    # make the value range a pretty range
    value_range = make_pretty2(value_high - value_low, False)

    # make the tick range a pretty range
    division, factor10 = make_pretty(value_range/(ticks-1), True)

    # calculate the graph minimum and maximum
    if division == 0:
        return 0, 0, [0], 0, 0, 0

    graph_minimum = math.floor(value_low / division) * division
    graph_maximum = math.ceil(value_high / division) * division

    # In logarithmic scale we calculate the ticks from the exponents of the values, so factor10 needs to
    # be adjusted accordingly.
    if logarithmic:
        factor10 = math.pow(10, graph_maximum if abs(graph_maximum) > abs(graph_minimum) else graph_minimum)

    # calculate the precision
    precision = int(max(-math.floor(math.log10(division)), 0))

    # make the tick marks
    tick_values = []

    for x in arange(graph_minimum, graph_maximum + 0.5 * division, division):
        tick_values.append(x)

    return graph_minimum, graph_maximum, tick_values, division, precision, factor10


def make_pretty_range(value_low: float, value_high: float, tight: bool = False, ticks: int = 5) -> typing.Tuple[float, float, typing.Sequence[float], float, int]:
    return make_pretty_range2(value_low, value_high, ticks)[:-1]


class Ticker:

    def __init__(self, value_low: float, value_high: float, *, ticks: int = 5) -> None:
        self._value_low = value_low
        self._value_high = value_high
        self._ticks = ticks

        self._tick_values: typing.Sequence[float] = []
        self._tick_labels: typing.Sequence[str] = []
        self._minor_tick_indices: typing.List[int] = []
        self._minimum = 0.0
        self._maximum = 0.0
        self._division = 1.0
        self._precision = 0

    def value_label(self, value: float) -> str:
        raise NotImplementedError

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def values(self) -> typing.Sequence[float]:
        return self._tick_values

    @property
    def labels(self) -> typing.Sequence[str]:
        return self._tick_labels

    @property
    def minimum(self) -> float:
        return self._minimum

    @property
    def maximum(self) -> float:
        return self._maximum

    @property
    def division(self) -> float:
        return self._division

    @property
    def precision(self) -> int:
        return self._precision

    @property
    def minor_tick_indices(self) -> typing.Sequence[int]:
        return self._minor_tick_indices


class LinearTicker(Ticker):

    def __init__(self, value_low: float, value_high: float, *, ticks: int=5):
        super().__init__(value_low, value_high, ticks=ticks)
        self._minimum, self._maximum, self._tick_values, self._division, self._precision, self._factor10 = make_pretty_range2(value_low, value_high, ticks=ticks)
        self._tick_labels = list(self.value_label(tick_value) for tick_value in self._tick_values)

    def __nice_label(self, value: float, precision: int, factor10: float) -> str:
        f10 = int(math.log10(factor10)) if factor10 > 0 else 0
        if abs(f10) > 5:
            f10x = int(math.log10(value)) if value > 0 else f10
            precision = max(0, f10x - f10)
            return (u"{0:0." + u"{0:d}".format(precision) + "e}").format(value)
        else:
            return (u"{0:0." + u"{0:d}".format(precision) + "f}").format(value)

    def value_label(self, value: float) -> str:
        return self.__nice_label(value, self.precision, self._factor10)


class LogTicker(Ticker):

    def __init__(self, value_low: float, value_high:float, *, ticks: int = 5, base: int = 10):
        super().__init__(value_low, value_high, ticks=ticks)
        self._base = base

        if not all([math.isfinite(val) for val in [value_low, value_high, base]]):
            self._tick_values = [1]
            self._tick_labels = ["0e+00"]
            return

        val_range = abs(self._value_high - self._value_low)
        self._factor_b = math.pow(self.base, math.floor(math.log(val_range, self.base))) if (self._ticks-2)/self._base > val_range > 0 else 1.0
        self._minimum = math.floor(self._value_low / self._factor_b)
        self._maximum = max(math.ceil(self._value_high / self._factor_b), self._minimum + 1)
        self._precision = round(abs(math.log(self._factor_b, self.base)))

        numdec = self._maximum - self._minimum

        while abs(numdec) > 1.5 * val_range and self._factor_b == 1.0 and numdec > 0:
            numdec -= 1

        self._division = max((numdec + 1) // self._ticks, 1)
        decades = arange(self._minimum, self._maximum + self.division, self.division)
        if self._factor_b == 1.0:
            self._maximum = self._minimum + numdec
        # We will get len(decades) * subs ticks, so calculate the number of subs we need
        num_subs = self._ticks / (val_range / self._division) if val_range > 0 else 0.0

        subs: typing.List[float]
        if self._factor_b != 1.0:
           subs = []
        elif num_subs >= (self.base - 2):
            subs = list(arange(2, self.base, 1))
        elif num_subs >= (self.base - 2) * 0.5:
            subs = list(arange(2, self.base, 2))
        elif num_subs >= (self.base - 2) * 0.25:
            subs = [round(self.base * 0.5)]
        else:
            subs = []

        if subs and self._value_high >= self._maximum:
            high_floor = math.floor(self._value_high)
            self._maximum = high_floor + math.log(math.floor(math.pow(self.base, self._value_high - high_floor)) + 1, self.base)

        tick_values = list()
        for decade_start in decades:
            decade = math.pow(self.base, decade_start * self._factor_b)
            tick_values.append(decade)
            for sub in subs:
                tick_values.append(sub * decade)
                self._minor_tick_indices.append(len(tick_values) - 1)

        self._tick_labels = [self.value_label(value) for value in tick_values]
        self._tick_values = [math.log(value, self.base) for value in tick_values]

         # Revert maximum to its original value because it is used for auto display limits
        self._maximum *= self._factor_b
        # Set minimum slightly lower than the data minimum because it is used for auto display limits
        self._minimum = self._value_low - (self._maximum - self._value_low) * 0.01

    def value_label(self, value: float) -> str:
        return (u"{0:." + u"{0:d}".format(self.precision) + "e}").format(value)

    @property
    def base(self) -> int:
        return self._base


def fit_to_aspect_ratio(rect_: typing.Union[FloatRectTuple, IntRectTuple], aspect_ratio: float) -> FloatRect:
    """ Return rectangle fit to aspect ratio. Returned rectangle will have float coordinates. """
    rect = FloatRect.make(((rect_[0][0], rect_[0][1]), (rect_[1][0], rect_[1][1])))
    aspect_ratio = float(aspect_ratio)
    if rect.aspect_ratio > aspect_ratio:
        # height will fill entire frame
        new_size = FloatSize(height=rect.height, width=rect.height * aspect_ratio)
        new_origin = FloatPoint(y=rect.top, x=rect.left + 0.5 * (rect.width - new_size.width))
        return FloatRect(origin=new_origin, size=new_size)
    else:
        new_size = FloatSize(height=rect.width / aspect_ratio, width=rect.width)
        new_origin = FloatPoint(y=rect.top + 0.5*(rect.height - new_size.height), x=rect.left)
        return FloatRect(origin=new_origin, size=new_size)


def fit_to_size(rect: typing.Union[FloatRectTuple, IntRectTuple], fit_size: typing.Union[FloatSizeTuple, IntSizeTuple]) -> FloatRect:
    """ Return rectangle fit to size (aspect ratio). """
    return fit_to_aspect_ratio(rect, float(fit_size[1]) / float(fit_size[0]))


def inset_rect(rect: FloatRectTuple, amount: float) -> RectFloatTuple:
    """ Return rectangle inset by given amount. """
    return ((rect[0][0] + amount, rect[0][1] + amount), (rect[1][0] - 2 * amount, rect[1][1] - 2 * amount))


def distance(pt1: FloatPointTuple, pt2: FloatPointTuple) -> float:
    """ Return distance between points as float. """
    return math.sqrt(pow(pt2[0] - pt1[0], 2) + pow(pt2[1] - pt1[1], 2))


def midpoint(pt1: FloatPointTuple, pt2: FloatPointTuple) -> FloatPoint:
    """ Return midpoint between points. """
    return FloatPoint(0.5 * (pt1[0] + pt2[0]), 0.5 * (pt1[1] + pt2[1]))


@dataclasses.dataclass
class Margins:
    """Margins for a canvas item, specified by top, left, bottom, and right."""
    top: int
    left: int
    bottom: int
    right: int


class IntPoint:
    """A class representing an integer point (x, y)."""

    def __init__(self, y: int = 0, x: int = 0) -> None:
        self.__y = int(y)
        self.__x = int(x)

    @classmethod
    def make(cls, value: IntPointTuple) -> IntPoint:
        """ Make an IntPoint from a y, x tuple. """
        value_tuple = tuple(value)
        return IntPoint(y=value_tuple[0], x=value_tuple[1])

    def __str__(self) -> str:
        return "(x={}, y={})".format(self.__x, self.__y)

    def __repr__(self) -> str:
        return "{2} (x={0}, y={1})".format(self.__x, self.__y, super(IntPoint, self).__repr__())

    def to_float_point(self) -> FloatPoint:
        return FloatPoint(y=self.y, x=self.x)

    def as_tuple(self) -> PointIntTuple:
        return self.y, self.x

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def __eq__(self, other: typing.Any) -> bool:
        if other is not None:
            other = IntPoint.make(other)
            return bool((self.__x == other.x) and (self.__y == other.y))
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if other is not None:
            other = IntPoint.make(other)
            return bool((self.__x != other.x) or (self.__y != other.y))
        return True

    def __neg__(self) -> IntPoint:
        return IntPoint(y=-self.__y, x=-self.__x)

    def __abs__(self) -> float:
        return math.sqrt(pow(self.__x, 2) + pow(self.__y, 2))

    @typing.overload
    def __add__(self, other: typing.Union[IntPoint, IntSize]) -> IntPoint:
        ...

    @typing.overload
    def __add__(self, other: IntRect) -> IntRect:
        ...

    def __add__(self, other: typing.Union[IntPoint, IntSize, IntRect]) -> typing.Union[IntPoint, IntRect]:
        if isinstance(other, IntPoint):
            return IntPoint(y=self.__y + other.y, x=self.__x + other.x)
        elif isinstance(other, IntSize):
            return IntPoint(y=self.__y + other.height, x=self.__x + other.width)
        elif isinstance(other, IntRect):
            return other + self
        else:
            raise NotImplementedError()

    @typing.overload
    def __sub__(self, other: typing.Union[IntPoint, IntSize]) -> IntPoint:
        ...

    @typing.overload
    def __sub__(self, other: IntRect) -> IntRect:
        ...

    def __sub__(self, other: typing.Union[IntPoint, IntSize, IntRect]) -> typing.Union[IntPoint, IntRect]:
        if isinstance(other, IntPoint):
            return IntPoint(y=self.__y - other.y, x=self.__x - other.x)
        elif isinstance(other, IntSize):
            return IntPoint(y=self.__y - other.height, x=self.__x - other.width)
        elif isinstance(other, IntRect):
            return IntRect.from_center_and_size(self - other.center, other.size)
        else:
            raise NotImplementedError()

    def __getitem__(self, index: int) -> int:
        return (self.__y, self.__x)[index]

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> typing.Iterator[int]:
        yield self.__y
        yield self.__x

    def as_size(self) -> IntSize:
        return IntSize(w=self.x, h=self.y)


class IntSize:

    """ A class representing an integer size (width, height). """

    def __init__(self, height: typing.Optional[int] = None, width: typing.Optional[int] = None,
                 h: typing.Optional[int] = None, w: typing.Optional[int] = None) -> None:
        if height is not None:
            self.__height = int(height)
        elif h is not None:
            self.__height = int(h)
        else:
            self.__height = 0
        if width is not None:
            self.__width = int(width)
        elif w is not None:
            self.__width = int(w)
        else:
            self.__width = 0

    @classmethod
    def make(cls, value: IntSizeTuple) -> IntSize:
        """ Make an IntSize from a height, width tuple. """
        value_tuple = tuple(value)
        return IntSize(value_tuple[0], value_tuple[1])

    def __str__(self) -> str:
        return "(w={}, h={})".format(self.__width, self.__height)

    def __repr__(self) -> str:
        return "{2} (w={0}, h={1})".format(self.__width, self.__height, super(IntSize, self).__repr__())

    def to_float_size(self) -> FloatSize:
        return FloatSize(h=self.height, w=self.width)

    def as_tuple(self) -> PointIntTuple:
        return self.height, self.width

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def __eq__(self, other: typing.Any) -> bool:
        if other is not None:
            other = IntSize.make(other)
            return bool((self.__width == other.width) and (self.__height == other.height))
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if other is not None:
            other = IntSize.make(other)
            return bool((self.__width != other.width) or (self.__height != other.height))
        return True

    def __neg__(self) -> IntSize:
        return IntSize(-self.__height, -self.__width)

    def __abs__(self) -> float:
        return math.sqrt(pow(self.__width, 2) + pow(self.__height, 2))

    def __add__(self, other: typing.Union[IntSizeTuple, IntPointTuple]) -> IntSize:
        other = IntSize.make((other[0], other[1]))
        return IntSize(self.__height + other.height, self.__width + other.width)

    def __sub__(self, other: typing.Union[IntSizeTuple, IntPointTuple]) -> IntSize:
        other = IntSize.make((other[0], other[1]))
        return IntSize(self.__height - other.height, self.__width - other.width)

    def __mul__(self, multiplicand: float) -> IntSize:
        multiplicand = float(multiplicand)
        return IntSize(int(self.__height * multiplicand), int(self.__width * multiplicand))

    def __rmul__(self, multiplicand: float) -> IntSize:
        multiplicand = float(multiplicand)
        return IntSize(int(self.__height * multiplicand), int(self.__width * multiplicand))

    def __floordiv__(self, other: float) -> IntSize:
        return IntSize(int(self.__height / other), int(self.__width / other))

    def __getitem__(self, index: int) -> int:
        return (self.__height, self.__width)[index]

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> typing.Iterator[int]:
        yield self.__height
        yield self.__width

    def as_point(self) -> IntPoint:
        return IntPoint(x=self.width, y=self.height)

    @property
    def aspect_ratio(self) -> float:
        return float(self.__width) / float(self.__height) if self.__height != 0 else 1.0


class IntRect:

    """
        A class representing an integer rect (origin, size).

        Increasing size goes down and to the right from origin.
    """

    def __init__(self, origin: IntPointTuple, size: IntSizeTuple) -> None:
        self.__origin = IntPoint.make(origin)
        self.__size = IntSize.make(size)

    @classmethod
    def make(cls, value: IntRectTuple) -> IntRect:
        """ Make an IntRect from a origin, size tuple. """
        value_tuple = tuple(value)
        return IntRect(typing.cast(IntPoint, value_tuple[0]), typing.cast(IntSize, value_tuple[1]))

    @classmethod
    def from_center_and_size(cls, center: IntPointTuple, size: IntSizeTuple) -> IntRect:
        """ Make an IntRect from a center, size. """
        center = IntPoint.make(center)
        size = IntSize.make(size)
        origin = center - IntSize(height=size.height // 2, width=size.width // 2)
        return IntRect(origin, size)

    @classmethod
    def from_tlbr(cls, top: int, left: int, bottom: int, right: int) -> IntRect:
        """ Make an IntRect from a center, size. """
        origin = IntPoint(y=top, x=left)
        size = IntSize(height=bottom - top, width=right - left)
        return IntRect(origin, size)

    @classmethod
    def from_tlhw(cls, top: int, left: int, height: int, width: int) -> IntRect:
        """ Make an IntRect from a center, size. """
        origin = IntPoint(y=top, x=left)
        size = IntSize(height=height, width=width)
        return IntRect(origin, size)

    @classmethod
    def unit_rect(cls) -> IntRect:
        return cls.from_tlhw(0, 0, 1, 1)

    @classmethod
    def empty_rect(cls) -> IntRect:
        return cls.from_tlhw(0, 0, 0, 0)

    def __str__(self) -> str:
        return "(o={}, s={})".format(self.__origin, self.__size)

    def __repr__(self) -> str:
        return "{2} (o={0}, s={1})".format(self.__origin, self.__size, super(IntRect, self).__repr__())

    def to_float_rect(self) -> FloatRect:
        return FloatRect.from_tlbr(self.top, self.left, self.bottom, self.right)

    def as_tuple(self) -> RectIntTuple:
        return self.origin.as_tuple(), self.size.as_tuple()

    @property
    def origin(self) -> IntPoint:
        return self.__origin

    @property
    def size(self) -> IntSize:
        return self.__size

    @property
    def width(self) -> int:
        return self.size.width

    @property
    def height(self) -> int:
        return self.size.height

    @property
    def left(self) -> int:
        return self.origin.x

    @property
    def top(self) -> int:
        return self.origin.y

    @property
    def right(self) -> int:
        return self.origin.x + self.size.width

    @property
    def bottom(self) -> int:
        return self.origin.y + self.size.height

    @property
    def top_left(self) -> IntPoint:
        return IntPoint(y=self.top, x=self.left)

    @property
    def top_right(self) -> IntPoint:
        return IntPoint(y=self.top, x=self.right)

    @property
    def bottom_left(self) -> IntPoint:
        return IntPoint(y=self.bottom, x=self.left)

    @property
    def bottom_right(self) -> IntPoint:
        return IntPoint(y=self.bottom, x=self.right)

    @property
    def center(self) -> IntPoint:
        return IntPoint(y=(self.top + self.bottom) // 2, x=(self.left + self.right) // 2)

    @property
    def slice(self) -> typing.Tuple[slice, slice]:
        return slice(self.top, self.bottom), slice(self.left, self.right)

    def __eq__(self, other: typing.Any) -> bool:
        if other is not None:
            other = IntRect.make(other)
            return bool((self.__origin == other.origin) and (self.__size == other.size))
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if other is not None:
            other = IntRect.make(other)
            return bool((self.__origin != other.origin) or (self.__size != other.size))
        return True

    @typing.overload
    def __getitem__(self, index: typing.Literal[0]) -> PointIntTuple: ...

    @typing.overload
    def __getitem__(self, index: typing.Literal[1]) -> SizeIntTuple: ...

    def __getitem__(self, index: int) -> typing.Union[PointIntTuple, SizeIntTuple]:
        origin_tuple = typing.cast(PointIntTuple, tuple(self.__origin))
        size_tuple = typing.cast(SizeIntTuple, tuple(self.__size))
        return (origin_tuple, size_tuple)[index]

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> typing.Iterator[typing.Union[PointIntTuple, SizeIntTuple]]:
        yield self.__getitem__(0)
        yield self.__getitem__(1)

    @property
    def aspect_ratio(self) -> float:
        return float(self.width) / float(self.height) if self.height != 0 else 1.0

    def contains_point(self, point: IntPointTuple) -> bool:
        """Return whether the point is contained in this rectangle.

        Left/top sides are inclusive, right/bottom sides are not.
        """
        point = IntPoint.make(point)
        return point.x >= self.left and point.x < self.right and point.y >= self.top and point.y < self.bottom

    def intersects_rect(self, rect: IntRect) -> bool:
        """Return whether the rectangle intersects this rectangle."""
        # if one rectangle is on left side of the other
        if self.left > rect.right or rect.left > self.right:
            return False
        # if one rectangle is above the other
        if self.bottom < rect.top or rect.bottom < self.top:
            return False
        return True

    def translated(self, point: IntPointTuple) -> IntRect:
        """ Return the rectangle translated by the point or size. """
        return IntRect(self.origin + IntPoint.make(point), self.size)

    def inset(self, dx: int, dy: typing.Optional[int] = None) -> IntRect:
        """ Returns the rectangle inset by the specified amount. """
        dy = dy if dy is not None else dx
        origin = IntPoint(y=self.top + dy, x=self.left + dx)
        size = IntSize(height=self.height - dy * 2, width=self.width - dx * 2)
        return IntRect(origin, size)

    def intersect(self, rect: IntRect) -> IntRect:
        top = max(self.top, rect.top)
        left = max(self.left, rect.left)
        bottom = min(self.bottom, rect.bottom)
        right = min(self.right, rect.right)
        return IntRect.from_tlbr(top, left, bottom, right)

    def union(self, rect: IntRect) -> IntRect:
        top = min(self.top, rect.top)
        left = min(self.left, rect.left)
        bottom = max(self.bottom, rect.bottom)
        right = max(self.right, rect.right)
        return IntRect.from_tlbr(top, left, bottom, right)

    def __add__(self, other: IntPoint) -> IntRect:
        if isinstance(other, IntPoint):
            return IntRect.from_center_and_size(self.center + other, self.size)
        else:
            raise NotImplementedError()

    def __sub__(self, other: IntPoint) -> IntRect:
        if isinstance(other, IntPoint):
            return IntRect.from_center_and_size(self.center - other, self.size)
        else:
            raise NotImplementedError()


class FloatPoint:

    """ A class representing an float point (x, y). """

    def __init__(self, y: float = 0.0, x: float = 0.0) -> None:
        self.__y = float(y)
        self.__x = float(x)

    @classmethod
    def make(cls, value: FloatPointTuple) -> FloatPoint:
        """ Make an FloatPoint from a y, x tuple. """
        value_tuple = tuple(value)
        return FloatPoint(y=value_tuple[0], x=value_tuple[1])

    def __str__(self) -> str:
        return "(x={}, y={})".format(self.__x, self.__y)

    def __repr__(self) -> str:
        return "{2} (x={0}, y={1})".format(self.__x, self.__y, super(FloatPoint, self).__repr__())

    def to_int_point(self) -> IntPoint:
        return IntPoint(y=round(self.y), x=round(self.x))

    def as_tuple(self) -> PointFloatTuple:
        return self.y, self.x

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    def __eq__(self, other: typing.Any) -> bool:
        if other is not None:
            other = FloatPoint.make(other)
            return bool((self.__x == other.x) and (self.__y == other.y))
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if other is not None:
            other = FloatPoint.make(other)
            return bool((self.__x != other.x) or (self.__y != other.y))
        return True

    def __neg__(self) -> FloatPoint:
        return FloatPoint(y=-self.__y, x=-self.__x)

    def __abs__(self) -> float:
        return math.sqrt(pow(self.__x, 2) + pow(self.__y, 2))

    @typing.overload
    def __add__(self, other: typing.Union[FloatPoint, FloatSize]) -> FloatPoint:
        ...

    @typing.overload
    def __add__(self, other: FloatRect) -> FloatRect:
        ...

    def __add__(self, other: typing.Union[FloatPoint, FloatSize, FloatRect]) -> typing.Union[FloatPoint, FloatRect]:
        if isinstance(other, FloatPoint):
            return FloatPoint(y=self.__y + other.y, x=self.__x + other.x)
        elif isinstance(other, FloatSize):
            return FloatPoint(y=self.__y + other.height, x=self.__x + other.width)
        elif isinstance(other, FloatRect):
            return other + self
        else:
            raise NotImplementedError()

    @typing.overload
    def __sub__(self, other: FloatPoint) -> FloatPoint:
        ...

    @typing.overload
    def __sub__(self, other: FloatSize) -> FloatPoint:
        ...

    @typing.overload
    def __sub__(self, other: FloatRect) -> FloatRect:
        ...

    def __sub__(self, other: typing.Union[FloatPoint, FloatSize, FloatRect]) -> typing.Union[FloatPoint, FloatRect]:
        if isinstance(other, FloatPoint):
            return FloatPoint(y=self.__y - other.y, x=self.__x - other.x)
        elif isinstance(other, FloatSize):
            return FloatPoint(y=self.__y - other.height, x=self.__x - other.width)
        elif isinstance(other, FloatRect):
            return FloatRect.from_center_and_size(self - other.center, other.size)
        else:
            raise NotImplementedError()

    def __mul__(self, multiplicand: float) -> FloatPoint:
        multiplicand = float(multiplicand)
        return FloatPoint(y=self.__y * multiplicand, x=self.__x * multiplicand)

    def __rmul__(self, multiplicand: float) -> FloatPoint:
        multiplicand = float(multiplicand)
        return FloatPoint(y=self.__y * multiplicand, x=self.__x * multiplicand)

    def __truediv__(self, dividend: float) -> FloatPoint:
        dividend = float(dividend)
        return FloatPoint(y=self.__y / dividend, x=self.__x / dividend)

    def __getitem__(self, index: int) -> float:
        return (self.__y, self.__x)[index]

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> typing.Iterator[float]:
        yield self.__y
        yield self.__x

    def as_size(self) -> FloatSize:
        return FloatSize(w=self.x, h=self.y)

    def rotate(self, radians: float, origin: typing.Optional[FloatPoint] = None) -> FloatPoint:
        origin = origin or FloatPoint()
        dx = self.x - origin.x
        dy = self.y - origin.y
        cos_rad = math.cos(radians)
        sin_rad = math.sin(radians)
        x = origin.x + cos_rad * dx - sin_rad * dy
        y = origin.y + sin_rad * dx + cos_rad * dy
        return FloatPoint(x=x, y=y)


class FloatSize:

    """ A class representing an float size (width, height). """

    def __init__(self, height: typing.Optional[float] = None, width: typing.Optional[float] = None,
                 h: typing.Optional[float] = None, w: typing.Optional[float] = None) -> None:
        if height is not None:
            self.__height = float(height)
        elif h is not None:
            self.__height = float(h)
        else:
            self.__height = 0.0
        if width is not None:
            self.__width = float(width)
        elif w is not None:
            self.__width = float(w)
        else:
            self.__width = 0.0

    @classmethod
    def make(cls, value: FloatSizeTuple) -> FloatSize:
        """ Make an FloatSize from a height, width tuple. """
        value_tuple = tuple(value)
        return FloatSize(value_tuple[0], value_tuple[1])

    def __str__(self) -> str:
        return "(w={}, h={})".format(self.__width, self.__height)

    def __repr__(self) -> str:
        return "{2} (w={0}, h={1})".format(self.__width, self.__height, super(FloatSize, self).__repr__())

    def to_int_size(self) -> IntSize:
        return IntSize(height=round(self.height), width=round(self.width))

    def as_tuple(self) -> PointFloatTuple:
        return self.height, self.width

    @property
    def width(self) -> float:
        return self.__width

    @property
    def height(self) -> float:
        return self.__height

    def __eq__(self, other: typing.Any) -> bool:
        if other is not None:
            other = FloatSize.make(other)
            return bool((self.__width == other.width) and (self.__height == other.height))
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if other is not None:
            other = FloatSize.make(other)
            return bool((self.__width != other.width) or (self.__height != other.height))
        return True

    def __neg__(self) -> FloatSize:
        return FloatSize(-self.__height, -self.__width)

    def __abs__(self) -> float:
        return math.sqrt(pow(self.__width, 2) + pow(self.__height, 2))

    def __add__(self, other: typing.Union[FloatSizeTuple, FloatPointTuple]) -> FloatSize:
        other = FloatSize.make((other[0], other[1]))
        return FloatSize(self.__height + other.height, self.__width + other.width)

    def __sub__(self, other: typing.Union[FloatSizeTuple, FloatPointTuple]) -> FloatSize:
        other = FloatSize.make((other[0], other[1]))
        return FloatSize(self.__height - other.height, self.__width - other.width)

    def __mul__(self, multiplicand: float) -> FloatSize:
        multiplicand = float(multiplicand)
        return FloatSize(self.__height * multiplicand, self.__width * multiplicand)

    def __rmul__(self, multiplicand: float) -> FloatSize:
        multiplicand = float(multiplicand)
        return FloatSize(self.__height * multiplicand, self.__width * multiplicand)

    def __truediv__(self, dividend: float) -> FloatSize:
        dividend = float(dividend)
        return FloatSize(self.__height / dividend, self.__width / dividend)

    def __getitem__(self, index: int) -> float:
        return (self.__height, self.__width)[index]

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> typing.Iterator[float]:
        yield self.__height
        yield self.__width

    def as_point(self) -> FloatPoint:
        return FloatPoint(x=self.width, y=self.height)

    @property
    def aspect_ratio(self) -> float:
        return float(self.__width) / float(self.__height) if self.__height != 0 else 1.0

    def rotate(self, radians: float) -> FloatSize:
        dx = self.width
        dy = self.height
        cos_rad = math.cos(radians)
        sin_rad = math.sin(radians)
        x = cos_rad * dx - sin_rad * dy
        y = sin_rad * dx + cos_rad * dy
        return FloatSize(w=x, h=y)


class FloatRect:

    """
        A class representing an float rect (origin, size).

        Increasing size goes down and to the right from origin.
    """

    def __init__(self, origin: FloatPointTuple, size: FloatSizeTuple) -> None:
        self.__origin = FloatPoint.make(origin)
        self.__size = FloatSize.make(size)

    @classmethod
    def make(cls, value: FloatRectTuple) -> FloatRect:
        """ Make a FloatRect from a origin, size tuple. """
        value_tuple = tuple(value)
        return FloatRect(typing.cast(FloatPoint, value_tuple[0]), typing.cast(FloatSize, value_tuple[1]))

    @classmethod
    def from_center_and_size(cls, center: FloatPointTuple, size: FloatSizeTuple) -> FloatRect:
        """ Make a FloatRect from a center, size. """
        center = FloatPoint.make(center)
        size = FloatSize.make(size)
        origin = center - FloatSize(height=size.height * 0.5, width=size.width * 0.5)
        return FloatRect(origin, size)

    @classmethod
    def from_tlbr(cls, top: float, left: float, bottom: float, right: float) -> FloatRect:
        """ Make an FloatRect from a center, size. """
        origin = FloatPoint(y=top, x=left)
        size = FloatSize(height=bottom - top, width=right - left)
        return FloatRect(origin, size)

    @classmethod
    def from_tlhw(cls, top: float, left: float, height: float, width: float) -> FloatRect:
        """ Make an FloatRect from a center, size. """
        origin = FloatPoint(y=top, x=left)
        size = FloatSize(height=height, width=width)
        return FloatRect(origin, size)

    @classmethod
    def unit_rect(cls) -> FloatRect:
        return cls.from_tlhw(0, 0, 1, 1)

    @classmethod
    def empty_rect(cls) -> FloatRect:
        return cls.from_tlhw(0, 0, 0, 0)

    def __str__(self) -> str:
        return "(o={}, s={})".format(self.__origin, self.__size)

    def __repr__(self) -> str:
        return "{2} (o={0}, s={1})".format(self.__origin, self.__size, super(FloatRect, self).__repr__())

    def to_int_rect(self) -> IntRect:
        return IntRect(origin=self.origin.to_int_point(), size=self.size.to_int_size())

    def as_tuple(self) -> RectFloatTuple:
        return self.origin.as_tuple(), self.size.as_tuple()

    @property
    def origin(self) -> FloatPoint:
        return self.__origin

    @property
    def size(self) -> FloatSize:
        return self.__size

    @property
    def width(self) -> float:
        return self.size.width

    @property
    def height(self) -> float:
        return self.size.height

    @property
    def left(self) -> float:
        return self.origin.x

    @property
    def top(self) -> float:
        return self.origin.y

    @property
    def right(self) -> float:
        return self.origin.x + self.size.width

    @property
    def bottom(self) -> float:
        return self.origin.y + self.size.height

    @property
    def top_left(self) -> FloatPoint:
        return FloatPoint(y=self.top, x=self.left)

    @property
    def top_right(self) -> FloatPoint:
        return FloatPoint(y=self.top, x=self.right)

    @property
    def bottom_left(self) -> FloatPoint:
        return FloatPoint(y=self.bottom, x=self.left)

    @property
    def bottom_right(self) -> FloatPoint:
        return FloatPoint(y=self.bottom, x=self.right)

    @property
    def center(self) -> FloatPoint:
        return FloatPoint(y=(self.top + self.bottom) / 2, x=(self.left + self.right) / 2)

    def __eq__(self, other: typing.Any) -> bool:
        if other is not None:
            other = FloatRect.make(other)
            return bool((self.__origin == other.origin) and (self.__size == other.size))
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if other is not None:
            other = FloatRect.make(other)
            return bool((self.__origin != other.origin) or (self.__size != other.size))
        return True

    @typing.overload
    def __getitem__(self, index: typing.Literal[0]) -> PointFloatTuple: ...

    @typing.overload
    def __getitem__(self, index: typing.Literal[1]) -> SizeFloatTuple: ...

    def __getitem__(self, index: int) -> typing.Union[PointFloatTuple, SizeFloatTuple]:
        origin_tuple = typing.cast(PointFloatTuple, tuple(self.__origin))
        size_tuple = typing.cast(SizeFloatTuple, tuple(self.__size))
        return (origin_tuple, size_tuple)[index]

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> typing.Iterator[typing.Union[PointFloatTuple, SizeFloatTuple]]:
        yield self.__getitem__(0)
        yield self.__getitem__(1)

    @property
    def aspect_ratio(self) -> float:
        return float(self.width) / float(self.height) if self.height != 0 else 1.0

    def contains_point(self, point: FloatPointTuple) -> bool:
        """Return whether the point is contained in this rectangle.

        Left/top sides are inclusive, right/bottom sides are not.
        """
        point = FloatPoint.make(point)
        return point.x >= self.left and point.x < self.right and point.y >= self.top and point.y < self.bottom

    def intersects_rect(self, rect: FloatRect) -> bool:
        """Return whether the rectangle intersects this rectangle."""
        # if one rectangle is on left side of the other
        if self.left > rect.right or rect.left > self.right:
            return False
        # if one rectangle is above the other
        if self.bottom < rect.top or rect.bottom < self.top:
            return False
        return True

    def translated(self, point: FloatPointTuple) -> FloatRect:
        """ Return the rectangle translated by the point or size. """
        return FloatRect(self.origin + FloatPoint.make(point), self.size)

    def inset(self, dx: float, dy: typing.Optional[float] = None) -> FloatRect:
        """ Returns the rectangle inset by the specified amount. """
        dy = dy if dy is not None else dx
        origin = FloatPoint(y=self.top + dy, x=self.left + dx)
        size = FloatSize(height=self.height - dy * 2, width=self.width - dx * 2)
        return FloatRect(origin, size)

    def intersect(self, rect: FloatRect) -> FloatRect:
        top = max(self.top, rect.top)
        left = max(self.left, rect.left)
        bottom = min(self.bottom, rect.bottom)
        right = min(self.right, rect.right)
        return FloatRect.from_tlbr(top, left, bottom, right)

    def union(self, rect: FloatRect) -> FloatRect:
        top = min(self.top, rect.top)
        left = min(self.left, rect.left)
        bottom = max(self.bottom, rect.bottom)
        right = max(self.right, rect.right)
        return FloatRect.from_tlbr(top, left, bottom, right)

    def __add__(self, other: FloatPoint) -> FloatRect:
        if isinstance(other, FloatPoint):
            return FloatRect.from_center_and_size(self.center + other, self.size)
        else:
            raise NotImplementedError()

    def __sub__(self, other: FloatPoint) -> FloatRect:
        if isinstance(other, FloatPoint):
            return FloatRect.from_center_and_size(self.center - other, self.size)
        else:
            raise NotImplementedError()


def map_point(p: FloatPoint, f: FloatRect, t: FloatRect) -> FloatPoint:
    return FloatPoint(y=((p.y - f.top) / f.height) * t.height + t.top,
                      x=((p.x - f.left) / f.width) * t.width + t.left)


def map_size(s: FloatSize, f: FloatRect, t: FloatRect) -> FloatSize:
    return FloatSize(height=(s.height / f.height) * t.height,
                     width=(s.width / f.width) * t.width)


def map_rect(r: FloatRect, f: FloatRect, t: FloatRect) -> FloatRect:
    return FloatRect.from_center_and_size(map_point(r.center, f, t),
                                          map_size(r.size, f, t))
