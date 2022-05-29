"""This module gathers all plotting functions.

All those functions use `matplotlib <https://matplotlib.org/>`
and `graphviz <https://graphviz.org/>`.
"""
from typing import Any, Dict, List, Tuple

import graphviz
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from graphviz import Digraph
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path as MPath
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

from ..core.aliases import NumericValue
from ..core.sorting import RelationType
from ..outranking.utils import transitive_reduction_matrix


def piecewise_linear_colormap(
    colors: Any, name: str = "cmap"
) -> mcolors.LinearSegmentedColormap:
    """Create piecewise linear colormap.

    :param colors: list of any type of color accepted by :mod:`matplotlib`
    :param name: name of the created colormap
    :return: piecewise linear colormap
    """
    return mcolors.LinearSegmentedColormap.from_list(name, colors)


def radar_projection_name(num_vars: int) -> str:
    """Give projection corresponding to radar with `num_vars` axes.

    :param num_vars: number of axes of the radar plot
    :return:
    """
    return f"radar{num_vars}"


def create_radar_projection(num_vars: int, frame: str = "circle"):
    """Create a radar projection with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    :param num_vars: number of variables for radar chart
    :param frame: shape of frame surrounding axes ('circle' or 'polygon')

    Example:
        If you want to create radar projections up to a reasonable amount of
        variables. You can use the code below:

        .. code:: python

            from mcda.plot.new_plot import create_radar_projection

            for i in range(1, 12):
                create_radar_projection(i, frame="polygon")
    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = radar_projection_name(num_vars)
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location("N")

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == "circle":
                return Circle((0.5, 0.5), 0.5)
            elif frame == "polygon":
                return RegularPolygon(
                    (0.5, 0.5), num_vars, radius=0.5, edgecolor="k"
                )
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == "circle":
                return super()._gen_axes_spines()
            elif frame == "polygon":
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(
                    axes=self,
                    spine_type="circle",
                    path=MPath.unit_regular_polygon(num_vars),
                )
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(
                    Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes
                )
                return {"polar": spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)


class Figure:
    """This class is a wrapper around :class:`matplotlib.figure.Figure`

    It plots and organizes any number of :class:`mcda.plot.new_plot.Axis`.

    If `ncols` (resp. `nrows`) is ``0``, then columns will be added (resp.
    rows) when a row is full (resp. column). If both are ``0``, the grid layout
    will be as balanced as possible.

    :param fig: matplotlib figure to use (if not provided, one will be created)
    :param figsize: figure size in inches as a tuple (`width`, `height`)
    :param ncols: number of columns for the subplot layout
    :param nrows: number of rows for the subplot layout
    :param tight_layout:
        if ``True``, matplotlib `tight_layout` function is used to organize
        axes

    .. note::
        if `ncols` or `nrows` is ``0``, an unlimited number of axes can be
        added to the figure

    .. seealso::
        `Matplotlib tight layout guide <https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html>`_
            Guide on tight-layout usage to fit plots within figures more cleanly
    """  # noqa E501

    def __init__(
        self,
        fig: Any = None,
        figsize: Tuple[float, float] = None,
        ncols: int = 0,
        nrows: int = 0,
        tight_layout: bool = True,
    ):
        self.fig = fig
        self.axes: List[Axis] = []
        self.figsize = figsize
        self.layout = (nrows, ncols)
        self.tight_layout = tight_layout

    def reset(self):
        """Reset `fig` attribute"""
        self.fig = (
            plt.figure()
            if self.figsize is None
            else plt.figure(figsize=self.figsize)
        )

    @property
    def max_axes(self) -> NumericValue:
        """Return maximum number of axes the figure can handle.

        :return:
        """
        if self.layout[0] == 0 or self.layout[1] == 0:
            return float("inf")
        return self.layout[0] * self.layout[1]

    def create_add_axis(self, projection: str = None) -> "Axis":
        """Create an axis and add it to figure.

        :param projection: projection ot use in created axis
        :return: created axis
        """
        axis = Axis(projection=projection)
        self.add_axis(axis)
        return axis

    def add_axis(self, axis: "Axis"):
        """Add axis to the figure.

        :param axis:
        """
        if len(self.axes) > self.max_axes:
            raise IndexError("already max number of axes")
        self.axes.append(axis)
        axis.figure = self

    def _pre_draw(self):
        """Prepare figure before drawing."""
        self.fig.clear()
        nb = len(self.axes)
        nrows, ncols = self.layout
        if self.layout[0] == 0 and self.layout[1] == 0:
            nrows = int(np.ceil(np.sqrt(nb)))
            ncols = int(np.ceil(nb / nrows))
        elif self.layout[0] == 0:
            nrows = int(np.ceil(nb / ncols))
        elif self.layout[1] == 0:
            ncols = int(np.ceil(nb / nrows))
        for i, axis in enumerate(self.axes):
            if axis.projection is None:
                ax = self.fig.add_subplot(nrows, ncols, i + 1)
            else:
                ax = self.fig.add_subplot(
                    nrows,
                    ncols,
                    i + 1,
                    projection=axis.projection,
                )
            axis.ax = ax

    def _draw(self):
        """Draw all axes."""
        for axis in self.axes:
            axis.draw()

    def _post_draw(self):
        """Apply operations after axes drawings complete."""
        if self.tight_layout:
            self.fig.tight_layout()
        self.fig.show()

    def draw(self):
        """Draw figure and all its axes content."""
        if self.fig is None:
            self.fig = (
                plt.figure()
                if self.figsize is None
                else plt.figure(figsize=self.figsize)
            )
        self._pre_draw()
        self._draw()
        self._post_draw()


class Axis:
    """This class is a wrapper around :class:`matplotlib.axes.Axes`

    It draws any number of :class:`mcda.plot.new_plot.Plot` on a same subplot.

    :param figure: figure holding the object
    :param plots: list of plots to draw
    :param ax: matplotlib axes
    :param title: title of the object
    :param xlabel: label to use for `x` axis
    :param ylabel: label to use for `y` axis
    :param projection:
        projection to use when creating `ax` attribute from scratch
    """

    def __init__(
        self,
        figure: Figure = None,
        plots: "List[Plot]" = None,
        ax: Any = None,
        title: str = None,
        xlabel: str = None,
        ylabel: str = None,
        projection: str = None,
    ):
        self.figure = figure
        self.plots = [] if plots is None else plots
        self.ax = ax
        self.title = title
        self.projection = projection
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.plots = []

    def draw(self):
        """Draw the subplot and all its plots."""
        if self.ax is None:
            fig = Figure()
            fig.add_axis(self)
            fig.draw()
            return

        for p in self.plots:
            p.draw()
        if self.title is not None:
            self.ax.set_title(self.title)
        if self.xlabel is not None:
            self.ax.set_xlabel(self.xlabel)
        if self.ylabel is not None:
            self.ax.set_ylabel(self.ylabel)

    def add_plot(self, plot: "Plot"):
        """Add a plot to the subplot.

        :param plot:
        """
        self.plots.append(plot)
        plot.axis = self


class Plot:
    """This class is the base of all plot objects of this package.

    :param axis: subplot on which to be plotted
    """

    def __init__(self, axis: Axis = None):
        self.axis = axis

    @property
    def default_axis(self) -> Axis:
        """Default subplot object on which to plot itself."""
        return Axis()

    @property
    def ax(self):
        """Matplotlib axes direct access"""
        return self.axis.ax

    def draw(self):
        """Draw this plot."""
        if self.axis is None:
            ax = self.default_axis
            ax.add_plot(self)
            ax.draw()
            return
        self._pre_draw()
        self._draw()
        self._post_draw()

    def _pre_draw(self):
        """Prepare this plot."""
        pass

    def _draw(self):
        """Do the actual drawing of this plot."""
        pass

    def _post_draw(self):
        """Apply necessary operations after plot is drawn."""
        pass


class CartesianPlot(Plot):
    """This class represents 2D cartesian plots.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    """

    def __init__(
        self,
        x: List[NumericValue],
        y: List[NumericValue],
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
    ):
        Plot.__init__(self, axis)
        self.x = x
        self.y = y
        self.xticks = xticks
        self.yticks = yticks
        self.xticklabels = xticklabels
        self.yticklabels = yticklabels
        self.xticklabels_tilted = xticklabels_tilted

    def _post_draw(self):
        """Set ticks and their labels."""
        if self.xticks is not None:
            self.ax.set_xticks(self.xticks)
            if self.xticklabels is not None:
                options = (
                    {"rotation": -45, "ha": "left", "rotation_mode": "anchor"}
                    if self.xticklabels_tilted
                    else {}
                )
                self.ax.set_xticklabels(self.xticklabels, **options)
        if self.yticks is not None:
            self.ax.set_yticks(self.yticks)
            if self.yticklabels is not None:
                self.ax.set_yticklabels(self.yticklabels)


class LinePlot(CartesianPlot):
    """This class draws a regular lines and points plot.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    """

    def _draw(self):
        """Draw the lines and points regular plot."""
        self.ax.plot(self.x, self.y)


class StemPlot(CartesianPlot):
    """This class draws a stem plot.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    """

    def _draw(self):
        """Draw the stem plot."""
        self.ax.stem(self.x, self.y)


class BarPlot(CartesianPlot):
    """This class draws a bar chart.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param width: width of the bars plotted
    """

    def __init__(
        self,
        x: List[NumericValue],
        y: List[NumericValue],
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        width: NumericValue = None,
    ):
        CartesianPlot.__init__(
            self,
            x,
            y,
            xticks,
            yticks,
            xticklabels,
            yticklabels,
            xticklabels_tilted,
            axis,
        )
        self.width = width

    def _draw(self):
        """Draw the bar chart."""
        if self.width is not None:
            self.ax.bar(self.x, self.y, width=self.width)
        self.ax.bar(self.x, self.y)


class PolarPlot(Plot):
    """This class represents polar plots.

    :param x: data labels to plot
    :param y: data values to plot
    :param axis: subplot on which to be plotted
    """

    def __init__(self, x: List[str], y: List[NumericValue], axis: Axis = None):
        Plot.__init__(self, axis)
        self.x = x
        self.y = y


class PiePlot(PolarPlot):
    """This class draws a pie chart.

    :param x: data labels to plot
    :param y: data values to plot
    :param axis: subplot on which to be plotted
    """

    def _draw(self):
        """Draw the pie chart."""
        self.ax.pie(self.y, labels=self.x)


class RadarPlot(PolarPlot):
    """This class draws a radar chart (also called spider plot).

    :param x: data labels to plot
    :param y: data values to plot
    :param alpha:
        if set, surface under the plot is colored with this transparency
    :param axis: subplot on which to be plotted
    :param rlimits: limits for radial axis

    .. warning::
        This type of plot must be used with a `radar` type projection.
        The projection must exist before drawing of this chart can occur.

    .. seealso::
        Function :func:`create_radar_projection`
            This function should be called before drawing this chart so the
            radar projection (with same number of variables) is already
            registered.
    """

    def __init__(
        self,
        x: List[str],
        y: List[NumericValue],
        alpha: float = None,
        axis: Axis = None,
        rlimits: List[NumericValue] = None,
    ):
        PolarPlot.__init__(self, x, y, axis)
        self.alpha = alpha
        self.rlimits = rlimits

    @property
    def default_axis(self) -> Axis:
        """Default subplot object on which to plot itself."""
        return Axis(projection=radar_projection_name(len(self.x)))

    def _draw(self):
        # calculate evenly-spaced axis angles
        theta = np.linspace(0, 2 * np.pi, len(self.x), endpoint=False)
        if self.rlimits is not None:
            self.ax.set_ylim(self.rlimits)
        self.ax.plot(theta, self.y)
        if self.alpha is not None:
            self.ax.fill(theta, self.y, alpha=self.alpha)

    def _post_draw(self):
        self.ax.set_varlabels(self.x)


def indifference_group_matrix(
    outranking_matrix: List[List[NumericValue]],
    alternative_dict: Dict[int, List[int]],
) -> Dict[int, List[int]]:
    """Associate every key of indifference alternatives for matrix

    This function is used to make a proper dictionary with associating the
    alternatives which are indifferent

    :param outranking_matrix: the matrix to display
    :param alternative_dict: the dictionary of every alternative
    """
    for index in range(len(outranking_matrix)):
        for j in range(len(outranking_matrix[index])):
            if (
                outranking_matrix[index][j] == 2.25
                or outranking_matrix[index][j] == -1.5
            ) and alternative_dict[index] != alternative_dict[j]:
                for element in alternative_dict[index]:
                    if j not in alternative_dict[element]:
                        alternative_dict[element] = list(
                            set(
                                alternative_dict[element] + alternative_dict[j]
                            )
                        )
                    alternative_dict[element].sort()
                for element in alternative_dict[j]:
                    alternative_dict[element] = alternative_dict[index]
    return alternative_dict


def plot_outranking(
    outranking_matrix: List[List[NumericValue]],
    alternatives: List[str] = None,
    edge_label: bool = False,
    cut_value: int = 0,
    transitive_reduction: bool = True,
) -> Digraph:
    """Create a graph for outranking matrix.

    This function creates a Graph using graphviz and display it.

    :param outranking_matrix: the matrix to display
    :param alternatives: (optional) the name for the actions
    :param edge_label: (optional) parameter to display the value of edges.
    :param cut_value: (optional) parameter to plot minimum value
    :param transitive_reduction: (optional) enable transitive reduction
    """

    outranking_graph = graphviz.Digraph("outranking", strict=True)
    _outranking_matrix = transitive_reduction_matrix(outranking_matrix)
    if alternatives is None:
        alternatives = []
        for index in range(len(outranking_matrix)):
            alternatives.append("a" + str(index))
    else:
        alternatives = [alternatives[i] for i in range(len(outranking_matrix))]
    outranking_graph.attr("node", shape="box")
    alternatives_dict = {}
    for i in range(len(alternatives)):
        alternatives_dict[i] = [i]
    alternative_dict = indifference_group_matrix(
        outranking_matrix, alternatives_dict
    )
    new_alternative_dict = get_names(alternative_dict, alternatives)
    outranking_graph.attr("node", shape="box")
    for key, value in new_alternative_dict.items():
        outranking_graph.node(value)
    for i in range(len(outranking_matrix)):
        for j in range(len(outranking_matrix[i])):
            label = ""
            if edge_label:
                label = str(outranking_matrix[i][j])
            if (
                outranking_matrix[i][j] >= cut_value
                and outranking_matrix[i][j] <= 1
                and i != j
                and (
                    transitive_reduction is False
                    or (
                        transitive_reduction
                        and outranking_matrix[i][j] == _outranking_matrix[i][j]
                    )
                )
            ):
                outranking_graph.edge(
                    new_alternative_dict[i],
                    new_alternative_dict[j],
                    label=label,
                )
    outranking_graph.render()
    return outranking_graph


def indifference_group(
    relation_list: List[Tuple[int, int, RelationType]],
    alternative_dict: Dict[int, List[int]],
) -> Dict[int, List[int]]:
    """Associate every key of indifference alternatives

    This function is used to make a proper dictionnary with associating the
    alternatives which are indifferent

    :param relation_list: the list of relation
    :param alternative_dict: the dictionnary of every alternatives
    """
    for index in range(len(relation_list)):
        if (
            relation_list[index][2] == RelationType.INDIFFERENCE
            and alternative_dict[relation_list[index][0]]
            != alternative_dict[relation_list[index][1]]
        ):
            for element in alternative_dict[relation_list[index][0]]:
                if relation_list[index][1] not in alternative_dict[element]:
                    alternative_dict[element] = list(
                        set(
                            alternative_dict[element]
                            + alternative_dict[relation_list[index][1]]
                        )
                    )
                alternative_dict[element].sort()
            for element in alternative_dict[relation_list[index][1]]:
                alternative_dict[element] = alternative_dict[
                    relation_list[index][0]
                ]
    return alternative_dict


def get_names(
    alternative_dict: Dict[int, List[int]], alternatives: List[str]
) -> Dict[int, str]:
    """Create a dictionary with the names of alternatives and their indexes.

    This function is used to make a proper dictionary with associating the
    right combination of alternatives names

    :param alternative_dict: the dictionary with the right key
    :param alternatives: the name for the actions
    """
    new_dict = {}
    for key, value in alternative_dict.items():
        temp = ""
        for element in value:
            if temp == "":
                temp += alternatives[element]
            else:
                temp += ", " + alternatives[element]
        new_dict[key] = temp
    return new_dict


def plot_relation(
    relation_list: List[Tuple[int, int, RelationType]],
    alternatives: List[str] = None,
) -> Digraph:
    """Create a graph for list of relation.

    This function creates a Graph using graphviz and display it.

    :param relation_list: the list of relation to display
    :param alternatives: (optional) the name for the actions
    :param edge_label: (optional) parameter to display the value of edges.
    """

    relation_graph = graphviz.Digraph("relation", strict=True)
    alternatives_dict = {}
    useful_alternatives_index = []
    # create a list using only useful value
    for relation in relation_list:
        if relation[0] not in useful_alternatives_index:
            useful_alternatives_index.append(relation[0])
        if relation[1] not in useful_alternatives_index:
            useful_alternatives_index.append(relation[1])
    # create a list of alternatives names

    if alternatives is None:
        alternatives = []
        for index in useful_alternatives_index:
            alternatives.append("a" + str(index))
    else:
        alternatives = [alternatives[i] for i in useful_alternatives_index]
    for i in range(len(alternatives)):
        alternatives_dict[i] = [i]
    alternative_dict = indifference_group(relation_list, alternatives_dict)
    new_alternative_dict = get_names(alternative_dict, alternatives)
    relation_graph.attr("node", shape="box")
    for key, value in new_alternative_dict.items():
        relation_graph.node(value)
    for i in range(len(relation_list)):
        label = ""
        if relation_list[i][2] == RelationType.PREFERENCE:
            relation_graph.edge(
                new_alternative_dict[relation_list[i][0]],
                new_alternative_dict[relation_list[i][1]],
                label=label,
            )
    relation_graph.render()
    return relation_graph


def plot_linear_ranking(
    alternatives_list: List[List[NumericValue]],
    alternatives: List[str] = None,
    edge_label=False,
):
    """Create a graph for list of alternatives.

    This function creates a Graph using graphviz and display it.

    :param alternatives_list: the alternatives number with the rank
    :param alternatives: (optional) the name for the actions
    :param edge_label: (optional) parameter to display the value of edges.
    """

    relation_graph = graphviz.Digraph("relation", strict=True)
    if alternatives is None:
        alternatives = []
        alt_sorted = sorted(alternatives_list, key=lambda x: x[0])
        for alt in alt_sorted:
            if "a" + str(alt[0]) not in alternatives:
                alternatives.append("a" + str(alt[0]))
    relation_graph.attr("node", shape="box")
    prev_alt = ""
    for alt in alternatives_list:
        label = ""
        index = int(alt[0])
        relation_graph.node(alternatives[index])
        if prev_alt != "":
            relation_graph.edge(
                prev_alt,
                alternatives[index],
                label=label,
            )
        prev_alt = alternatives[index]
    relation_graph.render()
    return relation_graph
