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
Functions for plotting filter functions.
"""

import numpy as np

from .style import (
    FIG_HEIGHT,
    FIG_WIDTH,
    qctrl_style,
)


@qctrl_style()
def plot_filter_functions(figure, filter_functions):
    """
    Creates a plot of the specified filter functions.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed. The dimensions of the Figure
        will be overridden by this method, but may be subsequently modified by the caller if
        desired.
    filter_functions : dict
        The dictionary of filter functions to plot. The keys should be the names of the filter
        functions, and the values the list of samples representing that filter function. Each such
        sample must be a dictionary with 'frequency', 'inverse_power', and
        'inverse_power_uncertainty' (optional) keys, giving the frequency (in Hertz) at which the
        sample was taken, the inverse power (in seconds) of the filter function at the sample, and
        the optional uncertainty of that inverse power (in seconds).

        The key 'inverse_power_precision' can be used instead of 'inverse_power_uncertainty'. If
        both are provided then the value corresponding to 'inverse_power_uncertainty' is used.

        If the uncertainty of an inverse power is provided, it must be non-negative.

        For example, the following would be a valid ``filter_functions`` input::

            {
             'Primitive': [
                 {'frequency': 0.0, 'inverse_power': 15.},
                 {'frequency': 1.0, 'inverse_power': 12.},
                 {'frequency': 2.0,
                  'inverse_power': 3.,
                  'inverse_power_uncertainty' 0.2},
             ],
             'CORPSE': [
                 {'frequency': 0.0, 'inverse_power': 10.},
                 {'frequency': 0.5, 'inverse_power': 8.5},
                 {'frequency': 1.0,
                  'inverse_power': 5.,
                  'inverse_power_uncertainty' 0.1},
                 {'frequency': 1.5, 'inverse_power': 2.5},
             ],
            }

    Raises
    ------
    ValueError
        If any of the input parameters are invalid.
    """
    if not filter_functions:
        raise ValueError("At least one filter function must be provided")

    figure.set_figwidth(FIG_WIDTH)
    figure.set_figheight(FIG_HEIGHT)

    axes = figure.subplots(nrows=1, ncols=1)

    for name in filter_functions:
        samples = filter_functions[name]
        frequencies, inverse_powers, inverse_power_uncertainties = np.array(
            list(
                zip(
                    *[
                        (
                            sample["frequency"],
                            sample["inverse_power"],
                            sample["inverse_power_uncertainty"]
                            if "inverse_power_uncertainty" in sample
                            else sample.get("inverse_power_precision", 0.0),
                        )
                        for sample in samples
                    ]
                )
            )
        )

        if np.any(inverse_power_uncertainties < 0.0):
            raise ValueError(f"Uncertainties must all be non-negative: {samples}")

        inverse_powers_upper = inverse_powers + inverse_power_uncertainties
        inverse_powers_lower = inverse_powers - inverse_power_uncertainties

        lines = axes.plot(frequencies, inverse_powers, label=name)
        axes.fill_between(
            frequencies,
            inverse_powers_lower,
            inverse_powers_upper,
            alpha=0.35,
            hatch="||",
            facecolor="none",
            edgecolor=lines[0].get_color(),
            linewidth=0,
        )

    axes.legend()

    axes.set_xscale("log")
    axes.set_yscale("log")

    axes.autoscale(axis="x", tight=True)

    axes.set_xlabel("Frequency (Hz)")
    axes.set_ylabel("Inverse power (s)")
