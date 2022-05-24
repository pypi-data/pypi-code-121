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
Functions for plotting cost vs iterations.
"""

from typing import (
    List,
    Optional,
)

from matplotlib.figure import Figure

from .style import (
    FIG_HEIGHT,
    FIG_WIDTH,
    qctrl_style,
)


@qctrl_style()
def plot_cost_history(
    figure: Figure,
    cost_histories: List,
    labels: Optional[List] = None,
    y_axis_log: bool = True,
    initial_iteration: int = 1,
):
    """
    Creates a plot of the cost against iterations for either a single cost history or
    a set of cost histories.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed.
        Its dimensions will be overridden by this method.
    cost_histories : list
        The values of the cost histories.
        Must be either a list of a single cost history or a list of several cost histories,
        where each individual cost history is a list.
        For example, a single cost history can be passed
            cost_histories = [0.1, 0.05, 0.02]
        or multiple cost histories
            cost_histories = [[0.1, 0.05, 0.02], [0.23, 0.2, 0.14, 0.1, 0.04, 0.015]]
    labels : list, optional
        The labels corresponding to the individual cost histories in `cost_histories`.
        If you provide this, it must be the same length as `cost_histories`.
    y_axis_log : bool, optional
        Whether the y-axis is log-scale.
        Defaults to True.
    initial_iteration : int, optional
        Where the iteration count on the x-axis starts from.
        This is useful if you want to include the initial cost—before optimization—at
        iteration 0 or if you pass cost histories that start at a later iteration.
        Defaults to 1.

    Raises
    ------
    ValueError
        If any of the input parameters are invalid.
    """

    figure.set_figwidth(FIG_WIDTH)
    figure.set_figheight(FIG_HEIGHT)

    axs = figure.subplots(nrows=1, ncols=1)

    if not isinstance(cost_histories, List):
        raise ValueError("`cost_histories` must be a List")

    if not all(isinstance(history, List) for history in cost_histories):
        cost_histories = [cost_histories]

    if labels is not None:
        if len(cost_histories) != len(labels):
            raise ValueError(
                "If passing `labels` as argument, "
                "it must be of the same length as `cost_histories`."
            )

        for cost_history, label in zip(cost_histories, labels):
            axs.plot(
                range(initial_iteration, initial_iteration + len(cost_history)),
                cost_history,
                label=label,
            )
        axs.legend(loc="upper left", bbox_to_anchor=(1, 1))
    else:
        for cost_history in cost_histories:
            axs.plot(
                range(initial_iteration, initial_iteration + len(cost_history)),
                cost_history,
            )

    axs.set_xlabel("Iteration")
    axs.set_ylabel("Cost")

    if y_axis_log:
        axs.set_yscale("log")
