from typing import Union, Optional, Sequence, Dict
from IPython.display import Image, display
import plotly.express as px
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType
from plotly.subplots import make_subplots
from skimage import io
from . import _layout as pll
from ._type import Traces


def figure(traces: Traces,
           layout: Optional[go.Layout] = None) -> go.Figure:
    """Same as go.Figure(), just for compatibility.

    positional arguments:
      @ traces : A trace or list of traces.

    optional arguments:
      @ layout         : A layout object.
    """
    return go.Figure(data=traces, layout=layout)


def show(traces: Union[Traces, go.Figure],
         layout: Optional[go.Layout] = None,
         out_image: Optional[str] = None,
         out_html: Optional[str] = None,
         embed_plotlyjs: bool = True,
         do_not_display: bool = False) -> None:
    """Plot a figure in Jupyter Notebook.

    positional arguments:
      @ traces : A trace, list of traces, or a Figure object.

    optional arguments:
      @ layout         : A layout object.
      @ out_html       : HTML file name to which the plot is output.
      @ out_image      : Image file name to which the plot is output.
                         .[png|jpeg|svg|pdf|eps] are supported.
      @ embed_plotlyjs : If True, embed plotly.js codes (~3 MB) in `out_html`.
      @ do_not_display : If True, do not draw the plot.
    """
    if isinstance(traces, go.Figure):
        fig = traces
        if layout is not None:
            fig.layout = pll.merge_layout(fig.layout, layout)
    else:
        fig = figure(traces, layout)

    if not do_not_display:
        fig.show()
    if out_image is not None:
        fig.write_image(out_image)
    if out_html is not None:
        fig.write_html(file=out_html,
                       include_plotlyjs=embed_plotlyjs)


def show_mult(figs: Sequence[Union[BaseTraceType, go.Figure]],
              layout: Optional[go.Layout] = None,
              n_col: int = 2,
              horizontal_spacing: Optional[float] = 0.1,
              vertical_spacing: Optional[float] = 0.2,
              shared_xaxes: Union[bool, str] = False,
              shared_yaxes: Union[bool, str] = False,
              out_image: Optional[str] = None,
              out_html: Optional[str] = None,
              embed_plotlyjs: bool = True,
              do_not_display: bool = False) -> None:
    """Plot a figure with multiple subplots in Jupyter Notebook.

    positional arguments:
      @ figs : List of Trace or Figure objects. If an element is a Figure object,
               its layout is used for that subplot.

    optional arguments:
      @ layout           : A layout object for the overall figure.
      @ n_col            : Number of columns of plots. Number of rows is automatically determined.
      @ [horizontal|vertical]_spacing:
                         : Size of spaces between subplots. Must be in [0, 1].
                           Default: horizontal = 0.1 / #cols, vertical = 0.2 / #rows.
      @ shared_[x|y]axes : Must be boolean or one of {"columns", "rows", "all"}.
      @ out_html         : HTML file name to which the plot is output.
      @ out_image        : Image file name to which the plot is output.
                           .[png|jpeg|svg|pdf|eps] are supported.
      @ embed_plotlyjs   : If True, embed plotly.js codes (~3 MB) in `out_html`.
      @ do_not_display   : If True, do not draw the plot.
    """
    N = len(figs)
    n_row = N // n_col + (0 if N % n_col == 0 else 1)

    # Decompose Figure (or Trace) into Traces & Layout
    sub_tracess, sub_layouts = zip(*[(fig.data, fig.layout) if isinstance(fig, go.Figure)
                                     else ((fig,), pll.layout())
                                     for fig in figs])
    sub_titles = [l.title.text for l in sub_layouts]
    if all([x is None for x in sub_titles]):
        sub_titles = None

    # Make entire figure, add each traces & layout, and add overall layout
    fig = make_subplots(rows=n_row,
                        cols=n_col,
                        shared_xaxes=shared_xaxes,
                        shared_yaxes=shared_yaxes,
                        horizontal_spacing=horizontal_spacing,
                        vertical_spacing=vertical_spacing,
                        subplot_titles=sub_titles)
    for i in range(n_row):
        for j in range(1, n_col + 1):
            if i * n_col + j > N:
                continue
            idx = i * n_col + j - 1
            sub_traces = sub_tracess[idx]
            for sub_trace in sub_traces:
                fig.add_trace(sub_trace, row=i + 1, col=j)
            l = sub_layouts[idx]
            fig.update_xaxes(**l.xaxis.to_plotly_json(), row=i + 1, col=j)
            fig.update_yaxes(**l.yaxis.to_plotly_json(), row=i + 1, col=j)
    fig.update_layout(margin=dict(t=70, l=40))
    fig.update_layout(layout)

    if not do_not_display:
        fig.show()
    if out_image is not None:
        fig.write_image(out_image)
    if out_html is not None:
        fig.write_html(file=out_html,
                       include_plotlyjs=embed_plotlyjs)


def show_image(fname: str,
               interactive: bool = False,
               width: Optional[int] = None,
               height: Optional[int] = None,
               margin: Dict = dict(l=0, r=0, t=0, b=0)) -> None:
    """Plot an image file in Jupyter Notebook.

    positional arguments:
      @ fname : Name of the image file.

    optional arguments:
      @ interactive : If True, plot an interective (but very large) plot.
      @ width  : Of the image.
      @ height : Of the image.
    """
    if not interactive:
        display(Image(fname, width=width, height=height))
    else:
        fig = px.imshow(io.imread(fname))
        fig.update_layout(width=width,
                          height=height,
                          xaxis=dict(showgrid=False,
                                     zeroline=False,
                                     showticklabels=False),
                          yaxis=dict(showgrid=False,
                                     zeroline=False,
                                     showticklabels=False),
                          margin=margin)
        fig.show()
