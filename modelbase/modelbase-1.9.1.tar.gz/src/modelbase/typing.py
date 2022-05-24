from __future__ import annotations

from typing import List, Union

import numpy as np
from matplotlib.axes import Axes as plt_axes
from matplotlib.figure import Figure as plt_figure
from numpy.typing import NDArray
from typing_extensions import TypeAlias

Array: TypeAlias = NDArray[np.float64]
Number = Union[
    float,
    List[float],
    Array,
]

Axis = plt_axes
Axes = NDArray[plt_axes]  # type: ignore
Figure = plt_figure
ArrayLike = Union[NDArray[np.float64], List[float]]
