from typing import Optional

from hypothesis.extra.numpy import array_shapes
from hypothesis.extra.numpy import arrays
from hypothesis.extra.numpy import from_dtype
from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import booleans
from hypothesis.strategies import floats
from hypothesis.strategies import integers
from hypothesis.strategies import nothing
from numpy import bool_
from numpy import dtype
from numpy import float64
from numpy import iinfo
from numpy import int64
from numpy.typing import NDArray

from dycw_utilities.hypothesis import draw_and_flatmap
from dycw_utilities.hypothesis.typing import MaybeSearchStrategy
from dycw_utilities.hypothesis.typing import Shape


def bool_arrays(
    *, shape: MaybeSearchStrategy[Shape] = array_shapes()
) -> SearchStrategy[NDArray[bool_]]:
    """Strategy for generating arrays of booleans."""

    return draw_and_flatmap(_draw_bool_arrays, shape)


def _draw_bool_arrays(shape: Shape, /) -> SearchStrategy[NDArray[bool_]]:
    return arrays(bool, shape, elements=booleans(), fill=nothing())


def float_arrays(
    *,
    shape: MaybeSearchStrategy[Shape] = array_shapes(),
    min_value: MaybeSearchStrategy[Optional[float]] = None,
    max_value: MaybeSearchStrategy[Optional[float]] = None,
    allow_nan: MaybeSearchStrategy[Optional[bool]] = None,
    allow_infinity: MaybeSearchStrategy[Optional[bool]] = None,
) -> SearchStrategy[NDArray[float64]]:
    """Strategy for generating arrays of floats."""

    return draw_and_flatmap(
        _draw_float_arrays,
        shape,
        min_value=min_value,
        max_value=max_value,
        allow_nan=allow_nan,
        allow_infinity=allow_infinity,
    )


def _draw_float_arrays(
    shape: Shape,
    /,
    *,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_nan: Optional[bool] = None,
    allow_infinity: Optional[bool] = None,
) -> SearchStrategy[NDArray[float64]]:
    elements = floats(
        min_value=min_value,
        max_value=max_value,
        allow_nan=allow_nan,
        allow_infinity=allow_infinity,
    )
    return arrays(float, shape, elements=elements, fill=nothing())


def int_arrays(
    *,
    shape: MaybeSearchStrategy[Shape] = array_shapes(),
    min_value: MaybeSearchStrategy[Optional[int]] = None,
    max_value: MaybeSearchStrategy[Optional[int]] = None,
) -> SearchStrategy[NDArray[int64]]:
    """Strategy for generating arrays of ints."""

    return draw_and_flatmap(
        _draw_int_arrays, shape, min_value=min_value, max_value=max_value
    )


def _draw_int_arrays(
    shape: Shape,
    /,
    *,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> SearchStrategy[NDArray[int64]]:
    info = iinfo(int64)
    min_value_use = info.min if min_value is None else min_value
    max_value_use = info.max if max_value is None else max_value
    elements = integers(min_value=min_value_use, max_value=max_value_use)
    return arrays(int, shape, elements=elements, fill=nothing())


def int64s() -> SearchStrategy[int]:
    """Strategy for generating int64s."""

    return from_dtype(dtype(int64)).map(int)
