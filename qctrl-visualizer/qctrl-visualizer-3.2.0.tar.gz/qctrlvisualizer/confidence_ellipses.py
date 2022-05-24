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
Functions for plotting confidence ellipses.
"""
from typing import (
    List,
    Optional,
    Union,
)

import numpy as np
from matplotlib.figure import Figure

from .style import (
    FIG_HEIGHT,
    QCTRL_STYLE_COLORS,
    qctrl_style,
)
from .utils import (
    create_axes,
    get_units,
)


@qctrl_style()
def plot_confidence_ellipses(
    figure: Figure,
    ellipse_matrix: np.ndarray,
    estimated_parameters: np.ndarray,
    actual_parameters: Optional[np.ndarray] = None,
    parameter_names: Optional[List[str]] = None,
    parameter_units: Union[str, List[str]] = "Hz",
):
    """
    Creates an array of confidence ellipse plots.

    From an (N,N) matrix transformation and N estimated parameters,
    plots the confidence ellipse for each pair of parameters.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed.
        Its dimensions will be overridden by this method.
    ellipse_matrix : np.ndarray
        The square matrix which transforms a unit hypersphere in an
        N-dimensional space into a hyperellipse representing the confidence
        region. Must be of shape (N, N), with N > 1.
    estimated_parameters : np.ndarray
        The values of the estimated parameters. Must be of shape (N,).
    actual_parameters : np.ndarray, optional
        The actual values of the estimated parameters.
        If you provide these, they're plotted alongside the ellipses and
        estimated parameters. Must be of shape (N,).
    parameter_names : list[str], optional
        The name of each parameter, to be used as axes labels.
        If provided, it must be of length N. If not provided,
        the axes are labelled "Parameter 0", "Parameter 1", ...
    parameter_units : str or list[str], optional
        The units of each parameter. You can provide a list of strings with
        the units of each parameter, or a single string if all parameters have
        the same units. Defaults to "Hz".

    Raises
    ------
    ValueError
        If any of the input parameters are invalid.
    """

    ellipse_matrix = np.asarray(ellipse_matrix)
    estimated_parameters = np.asarray(estimated_parameters)
    if actual_parameters is not None:
        actual_parameters = np.asarray(actual_parameters)

    if len(estimated_parameters.shape) > 1:
        raise ValueError("`estimated_parameters` must be 1D array.")

    if len(estimated_parameters) < 2:
        raise ValueError("`estimated_parameters` must contain at least two parameters.")

    parameter_count = len(estimated_parameters)

    if ellipse_matrix.shape != (parameter_count, parameter_count):
        raise ValueError(
            "`ellipse_matrix` must be a square 2D array, "
            "with the same length as `estimated_parameters`."
        )

    if (actual_parameters is not None) and (
        actual_parameters.shape != (parameter_count,)
    ):
        raise ValueError(
            "`actual_parameters` must be 1D array "
            "with the same shape as `estimated_parameters`."
        )

    if parameter_names is not None:
        if len(parameter_names) != parameter_count:
            raise ValueError(
                "`parameter_names` must be list "
                "with the same length as `estimated_parameters`."
            )
    else:
        parameter_names = [f"Parameter {k}" for k in range(parameter_count)]

    if isinstance(parameter_units, str):
        parameter_units = [parameter_units] * parameter_count

    if len(parameter_units) != parameter_count:
        raise ValueError(
            "`parameter_units` must be list "
            "with the same length as `estimated_parameters`."
        )

    # Set the N (N-1) / 2 plots in a 2D grid of axes.
    if parameter_count % 2 == 0:
        plot_count_x = parameter_count - 1
        plot_count_y = parameter_count // 2
    else:
        plot_count_x = parameter_count
        plot_count_y = (parameter_count - 1) // 2

    axes_array = create_axes(
        figure, plot_count_x, plot_count_y, FIG_HEIGHT, FIG_HEIGHT
    ).flatten()

    # Create pairs of indices with all possible parameter pairings.
    index_1_list, index_2_list = np.triu_indices(parameter_count, k=1)

    for axes, index_1, index_2 in zip(axes_array, index_1_list, index_2_list):

        # Obtain points representing the correct parameters and their estimates.
        estimated_dot = estimated_parameters[[index_1, index_2]]

        # Obtain coordinates for a circle.
        theta = np.linspace(0, 2 * np.pi, 101)
        circle_coordinates = np.array([np.cos(theta), np.sin(theta)])

        # Define matrix that transforms circle coordinates into ellipse coordinates.
        coordinate_change = ellipse_matrix[
            np.ix_([index_1, index_2], [index_1, index_2])
        ]
        ellipse = coordinate_change @ circle_coordinates + estimated_dot[:, None]
        scale_x, units_x = get_units(ellipse[0])
        scale_y, units_y = get_units(ellipse[1])
        scale = np.array([scale_x, scale_y])

        # Define labels of the axes.
        axes.set_xlabel(
            f"{parameter_names[index_1]} ({units_x}{parameter_units[index_1]})",
            labelpad=0,
        )
        axes.set_ylabel(
            f"{parameter_names[index_2]} ({units_y}{parameter_units[index_2]})",
            labelpad=0,
        )

        # Plot estimated parameters.
        estimated_dot = estimated_dot / scale
        axes.plot(
            *estimated_dot, "o", label="Estimated parameters", c=QCTRL_STYLE_COLORS[0]
        )

        # Plot confidence ellipse.
        ellipse = ellipse / scale[:, None]
        axes.plot(*ellipse, "--", label="Confidence region", c=QCTRL_STYLE_COLORS[0])

        # Plot actual parameters (if available).
        if actual_parameters is not None:
            actual_dot = actual_parameters[[index_1, index_2]] / scale
            axes.plot(
                *actual_dot, "o", label="Actual parameters", c=QCTRL_STYLE_COLORS[1]
            )

    # Create legends.
    handles, labels = axes_array[0].get_legend_handles_labels()
    figure.legend(
        handles=handles, labels=labels, loc="center", bbox_to_anchor=(0.5, 0.95), ncol=3
    )
