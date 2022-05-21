"""Module with functions for 'plots' subpackage."""

from __future__ import annotations
from typing import TYPE_CHECKING

from typing_extensions import Literal

from .. import misc
from ..paths import PathLike, get_desktop_path
from ..system import check_library_is_available

# Lazy imports
# from pathlib import Path

# import plotly as pl
# import matplotlib.pyplot as plt
# from IPython import get_ipython

if TYPE_CHECKING:
    import pandas as pd


class GetPlotlyLayouts:
    """Plotly configs for particular plot types.

    Use `fig.layout.update(get_plotly_layout.categorical_scatter(title="My title"))'
    """

    def general(self, title):
        """General layout used in various plots."""
        return {
            "title": {
                "text": title,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "y": 0.9 if misc.GLOBAL_VARS.jupyter else 0.95,
            },
            "titlefont": {"size": 28},
            "font": {"size": 17},
        }

    def categorical_scatter(self, title):
        """If there are categories sharing an axis."""
        return {
            **self.general(title),
            "margin": {"l": 320, "r": 150, "b": 180, "t": 130},
            "titlefont": {"size": 34},
            "font": {"size": 22},
            "yaxis": {"tickfont": {"size": 18}, "ticksuffix": " ", "title": {"standoff": 20}},
        }

    def time_series(self, title, showlegend, yaxis="Values"):
        """Good for time series prediction."""
        return {
            **self.general(title),
            "yaxis": {"title": yaxis},
            "showlegend": showlegend,
            "legend_orientation": "h",
            "hoverlabel": {"namelength": -1},
            "margin": {"l": 160, "r": 130, "b": 160, "t": 110},
        }


get_plotly_layout = GetPlotlyLayouts()


def check_if_column_in_df(df: pd.DataFrame, column, parameter):
    """Check if column exists in DataFrame and if not, raise an KeyError."""
    if not column in df.columns:
        raise KeyError(
            f"Column {column} from parameter {parameter} not found in DataFrame. "
            f"Possible columns are: {df.columns}"
        )


def plot(
    df: pd.DataFrame,
    plot_library: Literal["plotly", "matplotlib"] = "plotly",
    title: str = "Plot",
    legend: bool = True,
    y_axis_name="Values",
    blue_column="",
    black_column="",
    grey_area: None | list[str] = None,
    save_path: None | PathLike = None,
    return_div: bool = False,
    show: bool = True,
) -> None | str:
    """Plots the data.

    Plotly or matplotlib can be used. It is possible to highlite two columns with different
    formating. It is usually used for time series visualization, but it can be used for different use case of
    course.

    Args:
        df (pd.DataFrame): Data to be plotted.
        plot_library (Literal['plotly', 'matplotlib'], optional): 'plotly' or 'matplotlib'
            Defaults to "plotly".
        legend (bool, optional): Whether display legend or not. Defaults to True.
        blue_column (str, optional): Column name that will be formatted differently (blue). Defaults to "".
        black_column (str, optional): Column name that will be formatted differently (black, wider).
            And is surrounded by grey_area. Can be empty (if grey_area is None). Defaults to "".
        grey_area (None | list[str]), optional): Whether to show grey area surrounding the black_column.
            Can be None, or list of ['lower_bound_column', 'upper_bound_column']. Both columns has to be
            in df. Defaults to None.
        save_path (None | PathLike, optional): Whether save the plot.  If False or "", do not save,
            if Path as str path, save to defined path. If "DESKTOP" save to desktop. Defaults to None.
        return_div (bool, optional): If True, return html div with plot as string. If False, just plot and
            do not return. Defaults to False.
        show (bool, optional): Can be evaluated, but not shown (testing reasons). Defaults to True.

    Returns:
        None | str: Only if return_div is True, else None.

    Examples:
        Plot DataFrame with

        >>> import pandas as pd
        >>> df = pd.DataFrame([[None, None, 1], [None, None, 2], [3, 3, 6], [3, 2.5, 4]])
        >>> plot(df, show=False)  # Show False just for testing reasons

        Example of filling grey area between columns

        >>> df = pd.DataFrame(
        ...     [[None, None, 0], [None, None, 2], [3, 3, 3], [2, 5, 4]], columns=["0", "1", "2"]
        ... )
        >>> plot(df, grey_area=["0", "1"], show=False)

        You can use matplotlib

        >>> plot(df, plot_library="matplotlib")

    Raises:
        KeyError: If defined column not found in DataFrame
    """
    if save_path == "DESKTOP":
        save_path = get_desktop_path() / "plot.html"

    if plot_library == "matplotlib":
        check_library_is_available("matplotlib")
        check_library_is_available("IPython")

        if misc.GLOBAL_VARS.jupyter:

            from IPython import get_ipython

            get_ipython().run_line_magic("matplotlib", "inline")  # type: ignore

        import matplotlib.pyplot as plt
        from matplotlib import rcParams

        rcParams["figure.figsize"] = (12, 8)

        df.plot()
        if legend:
            plt.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.05),
                ncol=3,
                fancybox=True,
                shadow=True,
            )

        if save_path:
            plt.savefig(save_path)

        if show:
            plt.show()

    elif plot_library == "plotly":

        check_library_is_available("plotly")

        import plotly as pl

        if misc.GLOBAL_VARS.jupyter:
            pl.io.renderers.default = "notebook_connected"

        used_columns = list(df.columns)

        graph_data = []

        if grey_area:
            check_if_column_in_df(df, grey_area[0], "grey_area[0]")
            check_if_column_in_df(df, grey_area[1], "grey_area[1]")

            upper_bound = pl.graph_objs.Scatter(
                name="Upper bound",
                x=df.index,
                y=df[grey_area[1]],
                line={"width": 0},
            )

            used_columns.remove(grey_area[1])
            graph_data.append(upper_bound)

            lower_bound = pl.graph_objs.Scatter(
                name="Lower bound",
                x=df.index,
                y=df[grey_area[0]],
                line={"width": 0},
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
            )

            used_columns.remove(grey_area[0])
            graph_data.append(lower_bound)

        if black_column:
            check_if_column_in_df(df, black_column, "black_column")

            surrounded = pl.graph_objs.Scatter(
                name=black_column,
                x=df.index,
                y=df[black_column],
                line={
                    "color": "rgb(51, 19, 10)",
                    "width": 5,
                },
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty" if grey_area else None,
            )

            used_columns.remove(black_column)
            graph_data.append(surrounded)

        if blue_column:

            check_if_column_in_df(df, blue_column, "blue_column")

            blue_column_ax = pl.graph_objs.Scatter(
                name=str(blue_column),
                x=df.index,
                y=df[blue_column],
                line={
                    "color": "rgb(31, 119, 180)",
                    "width": 2,
                },
            )

            used_columns.remove(blue_column)
            graph_data.append(blue_column_ax)

        fig = pl.graph_objs.Figure(data=graph_data)

        for i in df.columns:
            if i in used_columns:

                # Can be multiindex
                name = " - ".join([str(j) for j in i]) if isinstance(i, tuple) else i

                fig.add_trace(pl.graph_objs.Scatter(x=df.index, y=df[i], name=name))

        fig.layout.update(get_plotly_layout.time_series(title, legend, y_axis_name))

        if show:
            fig.show()

        if save_path:
            fig.write_html(save_path)

        if return_div:

            fig.layout.update(
                title=None,
                height=290,
                paper_bgcolor="#d9f0e8",
                margin={"b": 35, "t": 35, "pad": 4},
            )

            return pl.offline.plot(
                fig,
                include_plotlyjs=False,
                output_type="div",
            )
