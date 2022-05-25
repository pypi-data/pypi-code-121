from typing import Union, Optional, Tuple, List, Dict
import plotly.graph_objects as go


def layout(width: Optional[int] = None,
           height: Optional[int] = None,
           font: Optional[str] = None,
           font_col: Optional[str] = None,
           font_size: Optional[int] = None,
           title: Optional[str] = None,
           x_title: Optional[str] = None,
           y_title: Optional[str] = None,
           x_standoff: Optional[int] = None,
           y_standoff: Optional[int] = None,
           x_range: Optional[Tuple[Optional[float], Optional[float]]] = None,
           y_range: Optional[Tuple[Optional[float], Optional[float]]] = None,
           x_logscale: Optional[bool] = None,
           y_logscale: Optional[bool] = None,
           x_grid: Optional[bool] = None,
           y_grid: Optional[bool] = None,
           x_zeroline: Optional[bool] = None,
           y_zeroline: Optional[bool] = None,
           x_reversed: Optional[bool] = None,
           y_reversed: Optional[bool] = None,
           x_ticks: Optional[Union[str, bool]] = None,
           y_ticks: Optional[Union[str, bool]] = None,
           x_dtick: Optional[int] = None,
           y_dtick: Optional[int] = None,
           x_ticklabel: Optional[bool] = None,
           y_ticklabel: Optional[bool] = None,
           anchor_axes: Optional[bool] = None,
           grid_col: Optional[str] = None,
           zeroline_col: Optional[str] = None,
           tick_len: Optional[float] = None,
           tick_width: Optional[float] = None,
           tick_col: Optional[str] = None,
           show_legend: Optional[bool] = None,
           legend_horizontal: Optional[bool] = None,
           legend_coord: Optional[Tuple[Optional[float], Optional[float]]] = None,
           legend_border_col: Optional[str] = None,
           legend_border_width: Optional[int] = None,
           margin: Optional[Dict] = None,
           shapes: Optional[List[Dict]] = None,
           barmode: Optional[str] = None,
           hovermode: Optional[Union[str, bool]] = None) -> go.Layout:
    """Create a minimal Layout object.

    optional arguments:
      @ width                : Width of the plot.
      @ height               : Height of the plot.
      @ font                 : Font of characters in the plots.
      @ font_col             : Font color of charactoers in the plots.
      @ font_size_[title|axis_title|axis_tick|legend]
                             : Font size of title/x,y_title/x,y_tick/legend.
      @ title                : Title of the plot.
      @ [x|y]_title          : Title of [x|y]-axis of the plot.
      @ [x|y]_standoff       : Size (in px) of the margin between tick labels and axis title.
      @ [x|y]_range          : Range on [x|y]-axis to be drawn in the plot.
      @ [x|y]_grid           : Show grid on [x|y]-axis if True.
      @ [x|y]_zeroline       : Show zeroline on [x|y]-axis if True.
      @ [x|y]_reversed       : Reverse [x|y]-axis if True.
      @ [x|y]_ticks          : {"" (default), "outside", "inside"}.
      @ [x|y]_dtick          : Distance between two adjacent ticks.
      @ [x|y]_ticklabel      : Show tick labels of [x|y]-axis if True.
      @ anchor_axes          : Use same scale for both x/y axes.
      @ [grid|zeroline]_col  : Color of the grids and the zerolines.
      @ tick_[len|width|col] : Length/width/color of the ticks.
      @ show_legend          : Show legend if True.
      @ legend_horizontal    : Shoe legend horizontally if True.
      @ legend_coord         : Relative coordinate (x, y) of the legend.
                               Default: (x, y) = (1.02, 1).
      @ legend_border_[col|width]
                             : Color/width for the borderlines of the legend box.
      @ margin               : Margin of the plot. Any number of keys can be specified.
                               Default: `dict(t=50, b=10, l=10, r=10, pad=0)`.
      @ shapes               : List of non-interactive shape objects.
      @ barmode              : {"group" (default), "stack", "overlay", "relative"}.
      @ hovermode            : {"closest" (default), "[x|y] [unified]", False}.
    """
    return go.Layout(
        width=width,
        height=height,
        hovermode=hovermode,
        font=dict(family=font,
                  size=font_size,
                  color=font_col),
        title=dict(text=title),
        xaxis=dict(title=dict(text=x_title, standoff=x_standoff),
                   type="log" if x_logscale is True else None,
                   autorange="reversed" if x_reversed is True else None,
                   showgrid=x_grid,
                   zeroline=x_zeroline,
                   showticklabels=x_ticklabel,
                   range=x_range,
                   ticks="outside" if x_ticks is True else "" if x_ticks is False else x_ticks,
                   dtick=x_dtick,
                   ticklen=tick_len,
                   tickwidth=tick_width,
                   gridcolor=grid_col,
                   tickcolor=tick_col,
                   zerolinecolor=zeroline_col),
        yaxis=dict(title=dict(text=y_title, standoff=y_standoff),
                   type="log" if y_logscale is True else None,
                   autorange="reversed" if y_reversed is True else None,
                   scaleanchor="x" if anchor_axes is True else None,
                   showgrid=y_grid,
                   zeroline=y_zeroline,
                   showticklabels=y_ticklabel,
                   range=y_range,
                   ticks="outside" if y_ticks is True else "" if y_ticks is False else y_ticks,
                   dtick=y_dtick,
                   ticklen=tick_len,
                   tickwidth=tick_width,
                   gridcolor=grid_col,
                   tickcolor=tick_col,
                   zerolinecolor=zeroline_col),
        showlegend=show_legend,
        legend=dict(orientation='h' if legend_horizontal else None,
                    bordercolor=legend_border_col,
                    borderwidth=legend_border_width,
                    x=None if legend_coord is None else legend_coord[0],
                    y=None if legend_coord is None else legend_coord[1]),
        margin=margin,
        shapes=shapes,
        barmode=barmode)


def merge_layout(base_layout, *layouts) -> go.Layout:
    """Merge multiple layouts. The `base_layout` is iteratively updated by each 
    of the other layouts in the order of arguments.
    """
    if not isinstance(base_layout, go.Layout):
        base_layout = layout().update(base_layout)
    for _layout in layouts:
       base_layout = base_layout.update(_layout)
    return base_layout
