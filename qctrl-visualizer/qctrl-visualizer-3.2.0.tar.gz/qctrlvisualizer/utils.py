# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Utility functions for plotting.
"""

import numpy as np
from matplotlib.ticker import ScalarFormatter


def get_units(values):
    """
    For the given range of values, calculates the units to be used for plotting.  Specifically,
    returns a tuple (scaling factor, prefix), for example (1000, 'k') or (0.001, 'm'). The values
    should be divided by the first element, and the unit label prepended with the second element.
    If the values are zero the scaling factor is 1.
    """
    prefixes = {
        -24: "y",
        -21: "z",
        -18: "a",
        -15: "f",
        -12: "p",
        -9: "n",
        -6: "\N{MICRO SIGN}",
        -3: "m",
        0: "",
        3: "k",
        6: "M",
        9: "G",
        12: "T",
        15: "P",
        18: "E",
        21: "Z",
        24: "Y",
    }
    # We apply a simple algorithm: get the element with largest magnitude, then map according to
    # [0.001, 1) -> 0.001x/milli,
    # [1, 1000) -> no scaling,
    # [1000, 1e6) -> 1000x/kilo,
    # and so on.
    max_value = max(np.abs(values))
    exponent = float(
        3
        * np.floor_divide(np.log10(max_value, out=np.zeros(1), where=max_value > 0), 3)
    )
    # Clip the scaling to the allowable range.
    exponent_clipped = np.clip(exponent, -24, 24)
    return 10**exponent_clipped, prefixes[exponent_clipped]


def create_axes(figure, count_x, count_y, width, height, share_x=False, share_y=False):
    """
    Creates a set of axes with default axis labels and axis formatting.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the axes should be placed.
        Its dimensions will be overridden by this method.
    count_x : int
        The number of axes to create horizontally.
    count_y : int
        The number of axes to create vertically.
    width : float
        The width (in inches) for each axes.
    height : float
        The height (in inches) for each axes.
    share_x : bool, optional
        Whether the axes share the x-axis.
        Defaults to False.
    share_y : bool, optional
        Whether the axes share the y-axis.
        Defaults to False.

    Returns
    -------
    np.ndarray
        A 2D array of Axes objects.
    """
    figure.set_figheight(height * count_y)
    figure.set_figwidth(width * count_x)
    figure.subplots_adjust(hspace=0.2, wspace=0.25)

    axes_array = figure.subplots(
        nrows=count_y, ncols=count_x, sharex=share_x, sharey=share_y, squeeze=False
    )

    # Set axis formatting.
    for axes in axes_array.flat:
        axes.yaxis.set_major_formatter(ScalarFormatter())
        axes.xaxis.set_major_formatter(ScalarFormatter())

    return axes_array
