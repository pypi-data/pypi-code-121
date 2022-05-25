from typing import Union, Optional, Sequence, Tuple
from numbers import Number
import plotly.graph_objects as go
import numpy as np


def scatter(x: Sequence,
            y: Sequence,
            text: Optional[Sequence] = None,
            text_pos: Optional[str] = None,
            text_size: Optional[float] = None,
            text_col: Optional[str] = None,
            opacity: Optional[float] = None,
            mode: str = "markers",
            marker_size: float = 5,
            marker_width: int = None,
            line_width: float = 1,
            col: Optional[Union[str, Sequence[Union[int, str]]]] = None,
            col_range: Tuple[Optional[float], Optional[float]] = (None, None),
            col_scale: Optional[str] = None,
            reverse_scale: bool = False,
            show_col_bar: bool = False,
            col_bar_title: Optional[str] = None,
            col_bar_ticks: Optional[Sequence[int]] = None,
            col_bar_x: Optional[float] = None,
            col_bar_y: Optional[float] = None,
            name: Optional[str] = None,
            show_legend: bool = False,
            show_init: bool = True,
            use_webgl: bool = True) -> go.Scatter:
    """Create a simple Trace object of a scatter plot.

    positional arguments:
      @ x : Coordinates of data on x-axis.
      @ y : Coordinates of data on y-axis.

    optional arguments:
      @ text            : Texts for each data.
      @ text_pos        : Specify positions of `text`.
                          Format is: "[top|middle|bottom] [left|center|right]".
      @ text_size       : Size of `text`.
      @ text_col        : Color of `text`.
      @ opacity         : Opacity of the trace.
      @ mode            : "markers", "lines", "markers+lines", "text", etc.
      @ marker_size     : For "markers" mode.
      @ marker_width    : For "markers" mode.
      @ line_width      : For "lines" mode.
      @ col             : Color of markers and lines.
      @ col_range       : Value range for color scale.
      @ col_scale       : Color scale for markers and lines.
      @ reverse_scale   : Reverse `col_scale`.
      @ show_col_bar    : Show a color scale bar.
      @ col_bar_title   : Title text of the color scale bar.
      @ col_bar_ticks   : Tick values of the color scale bar.
      @ col_bar_[x|y]   : Relative position of the color scale bar.
                          (x, y) = (1.02, 0.5) by default.
      @ name            : Display name of the trace in legend.
      @ show_legend     : Show this trace in legend.
      @ show_init       : Show this trace initially.
      @ use_webgl       : Use WebGL instead of SVG for speed.
    """
    assert len(x) == len(y), "`x` and `y` must have same size"
    if text is not None:
        assert len(x) == len(text), "`text` must have same size as data"
    if col_bar_ticks is not None:
        assert (isinstance(col, Sequence)
                and isinstance(col.__iter__().__next__(), Number)), \
            "`col` must be a list of numbers if `col_bar_ticks` specified"
        col_bar_ticks = sorted(col_bar_ticks)
        col_range = (min(min(col),
                         col_bar_ticks[0],
                         np.inf if col_range[0] is None else col_range[0]),
                     max(max(col),
                         col_bar_ticks[-1],
                         -np.inf if col_range[0] is None else col_range[1]))
    return (go.Scattergl if use_webgl else go.Scatter)(
        x=x,
        y=y,
        text=text,
        opacity=opacity,
        mode=mode,
        name=name,
        hoverinfo="text" if text is not None else None,
        textposition=text_pos,
        textfont=dict(size=text_size,
                      color=text_col),
        marker=(None if mode == "lines" else
                dict(size=marker_size,
                     color=col,
                     colorbar=dict(title=col_bar_title,
                                   tickmode=None if col_bar_ticks is None else "array",
                                   tickvals=col_bar_ticks,
                                   x=col_bar_x,
                                   y=col_bar_y),
                     colorscale=col_scale,
                     reversescale=reverse_scale,
                     showscale=show_col_bar,
                     cmin=col_range[0],
                     cmax=col_range[1],
                     line=dict(width=marker_width))),
        line=(None if mode == "markers" else
              dict(width=line_width,
                   color=col)),
        showlegend=show_legend,
        visible=None if show_init else "legendonly")
