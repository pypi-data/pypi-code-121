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
Function for plotting the populations.
"""
from collections import namedtuple
from typing import (
    Dict,
    List,
)

import numpy as np
from matplotlib.figure import Figure

from .style import (
    FIG_HEIGHT,
    FIG_WIDTH,
    qctrl_style,
)
from .utils import get_units


@qctrl_style()
def plot_populations(figure: Figure, sample_times: np.ndarray, populations: Dict):
    """
    Creates a plot of the specified populations.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed.
        The dimensions of the Figure will be overridden by this method.
    sample_times : np.ndarray
        The 1D array of times in seconds at which the populations have been sampled.
    populations : dict
        The dictionary of populations to plot, of the form
        {
            "label_1": population_values_1,
            "label_2": population_values_2,
            ...
        }.
        Each `population_values_n` is a 1D array of population values with the same
        length as `sample_times` and `label_n` is its label.
        Population values must lie between 0 and 1.

    Raises
    ------
    TypeError
        If `populations` is not a dictionary.
    ValueError
        If values are out of range.
    """

    population_data = _create_population_data_from_population(populations)
    if not isinstance(sample_times, np.ndarray):
        raise TypeError("The `sample_times` must be an array.")

    figure.set_figwidth(FIG_WIDTH)
    figure.set_figheight(FIG_HEIGHT)

    axes = figure.subplots(nrows=1, ncols=1)

    scale, prefix = get_units(sample_times)
    sample_count = len(sample_times)
    for data in population_data:
        if len(data.values) != sample_count:
            ValueError(
                "The number of population values must match the number of sample times."
            )
        axes.plot(sample_times / scale, data.values, label=data.label)

    axes.set_xlabel(f"Time ({prefix}s)")
    axes.set_ylabel("Probability")

    axes.legend()


_PopulationData = namedtuple("_PopulationData", ["values", "label"])


def _create_population_data_from_population(populations: Dict) -> List:
    """
    Creates a list of _PopulationData objects for the given control data.

    Parameters
    ----------
    populations : dict
        The populations to plot.

    Returns
    -------
    list
        A list of _PopulationData.

    Raises
    ------
    TypeError
        If `populations` is not a dictionary.
    ValueError
        If values are out of range.
    """
    if not isinstance(populations, dict):
        raise TypeError("The `populations` parameter must be a dictionary.")
    plot_data = []
    for label, pop in populations.items():
        if not isinstance(pop, (list, np.ndarray)):
            raise TypeError(
                "Each element in the `populations` parameter must be an array or a list."
            )
        if np.any(np.asarray(pop) < 0) or np.any(np.asarray(pop) > 1):
            raise ValueError("Population values must lie between 0 and 1.")
        plot_data.append(_PopulationData(np.asarray(pop), label))

    return plot_data
