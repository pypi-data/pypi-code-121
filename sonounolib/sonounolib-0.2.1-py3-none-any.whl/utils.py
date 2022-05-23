"""Miscelaneous sonoUno library helpers."""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = ['asmax_amplitude', 'pad_along_axis']


def asmax_amplitude(value: str | float) -> float:
    """Returns the maximum amplitude from a data type.

    The maximum amplitude are the following:
        * `int16`: 32767.
        * `int32`: 2147483647.
        * `float`, `float32` or `float64`: 1.

    Arguments:
        value: The maximum amplitude or the data type for which the maximum amplitude is
            returned.

    Returns:
        The maximum amplitude associated with the input data type.

    Example:
        >>> from sonounolib.utils import asmax_amplitude
        >>> assert asmax_amplitude('int16') == 32767
        >>> assert asmax_amplitude(42) == 42
    """
    VALID_DTYPES = 'int16', 'int32', 'float', 'float32', 'float64'

    if isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
        return float(value)

    if not isinstance(value, str):
        raise TypeError(
            f'Invalid maximum amplitude of type {type(value).__name__!r}: {value}'
        )

    if value not in VALID_DTYPES:
        raise ValueError(
            f'The maximum amplitude cannot be inferred from the data type: '
            f'{value!r}.'
        )

    if value.startswith('float'):
        return 1.0

    return float(np.iinfo(value).max)


def pad_along_axis(array: ArrayLike, pad_width: int, axis: int = -1) -> NDArray[Any]:
    """Zero pads a multi-dimensional array along a specified axis.

    Arguments:
        array: The array to be padded.
        pad_width: The number of zeroes to be appended.
        axis: The axis along which the padding is performed.

    Returns:
        The padded ndarray.
    """
    array = np.asanyarray(array)
    npad = [(0, 0)] * array.ndim
    npad[axis] = (0, pad_width)
    return np.pad(array, pad_width=npad, mode='constant', constant_values=0)
