import typing

import numpy as np
import plotly.express as px
from plotly.colors import sequential
from plotly.graph_objects import Figure

import polisher


def prepare_correlation_matrix(
        correlation: "pd.DataFrame", colors: typing.List = sequential.Blues, precision: str = ".2"
) -> Figure:
    """
    Display correlation table from a dataframe. Use should pass the df.corr().
    You can change precission to .2% to add percentage.
    """
    mask = np.zeros_like(correlation, dtype=bool)
    mask[np.triu_indices_from(mask)] = True
    correlation[mask] = np.nan
    fig = px.imshow(
        correlation,
        text_auto=precision,
        color_continuous_scale=colors,
        range_color=[0, 1]
    ).update_xaxes(dtick=1).update_yaxes(dtick="M1")
    polisher.send_to_background(fig, keep_trace_colors=True)
    polisher.remove_grids(fig)
    return fig


def prepare_cohort(
        correlation: "pd.DataFrame", colors: typing.List = sequential.Blues, precision: str = ".2"
) -> Figure:
    """
    Display correlation table from a dataframe. Use should pass the df.corr().
    You can change precision to .2% to add percentage.
    """
    fig = px.imshow(
        correlation,
        text_auto=precision,
        color_continuous_scale=colors,
        range_color=[0, 1]
    ).update_xaxes(side="top", dtick=1).update_yaxes(dtick="M1")
    polisher.send_to_background(fig, keep_trace_colors=True)
    polisher.remove_background(fig)
    return fig
