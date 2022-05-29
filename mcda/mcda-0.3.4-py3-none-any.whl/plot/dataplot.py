from typing import Any, List, cast

import numpy as np

from ..core import performance_table as ptable
from ..core.aliases import NumericValue, PerformanceTable
from ..core.scales import NominalScale, QualitativeScale, Scale
from .plot import BarPlot, Figure


def plot_performance_table(
    performance_table: PerformanceTable,
    criteria_scales: List[Scale],
    alternatives: List[str] = None,
    criteria: List[str] = None,
    plot: Any = None,
) -> Figure:
    """Create figure with all criterion values plotted in their own subplot.

    :param performance_table:
    :param criteria_scales:
    :param alternatives:
    :param criteria:
    :param plot: class chosen to plot each criterion values
    :return: figure created
    """
    plot = BarPlot if plot is None else plot
    fig = Figure(ncols=2, nrows=int(np.ceil(len(performance_table[0]) / 2)))
    x = [*range(len(performance_table))]
    xticks = x
    xticklabels = alternatives
    for i in range(len(performance_table[0])):
        values = ptable.get_criterion_values(performance_table, i)
        ax = fig.create_add_axis()
        if criteria is not None:
            ax.title = criteria[i]
        yticks = None
        yticklabels = None
        y = values
        if isinstance(criteria_scales[i], QualitativeScale):
            y = [criteria_scales[i].transform_to(v) for v in values]
            yticklabels = criteria_scales[i].range()
            yticks = [
                criteria_scales[i].transform_to(yy) for yy in yticklabels
            ]
        elif isinstance(criteria_scales[i], NominalScale):
            yticklabels = criteria_scales[i].range()
            yticks = [*range(len(yticklabels))]
            y = [yticks[yticklabels.index(v)] for v in values]
        ax.add_plot(
            plot(
                x,
                cast(List[NumericValue], y),
                xticks=cast(List[NumericValue], xticks),
                yticks=cast(List[NumericValue], yticks),
                xticklabels=cast(List[str], xticklabels),
                yticklabels=cast(List[str], yticklabels),
            )
        )
    return fig
