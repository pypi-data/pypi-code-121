from typing import Union, Optional, Sequence, Tuple, List, Dict
import plotly.graph_objects as go
from ._scatter import scatter

Coord = Tuple[int, int, int, int]


def lines(coords: Union[Coord, List[Coord]],
          text: Optional[Sequence] = None,
          width: float = 1,
          col: str = "black",
          opacity: Optional[float] = None,
          use_shape: bool = False,
          xref: str = "x",
          yref: str = "y",
          layer: str = "above",
          name: Optional[str] = None,
          show_legend: bool = False,
          show_init: bool = True,
          use_webgl: bool = True) -> List[go.Scatter]:
    """For a collection of lines with same width and color.

    positional arguments:
      @ coords : (A list of) coordinate (x0, y0, x1, y1).

    optional arguments:
      @ width       : Line width applied to all lines.
      @ col         : Line color applied to all lines.
      @ use_shape   : If True, return (a list of) Shape object instead of
                      a list of Trace objects.
      @ opacity     : Opacity of the lines.

    optional arguments valid only if `use_shape` is True:
      @ [x|y]ref    : Must be one of {'[x|y]', 'paper'}.
                      If "paper", values of `[x|y]0,1` must be within [0, 1]
                      and are interpreted as relative positions in the entire
                      [x|y]-axis.
      @ layer       : Drawing layer. Must be one of {'above', 'below'}.

    optional arguments valid only if `use_shape` is False:
      @ text        : Texts for each data.
      @ name        : Display name of the trace in the legend.
      @ show_legend : Show this trace in legend.
      @ use_webgl   : Use WebGL instead of SVG.
    """
    def coord_to_shape(coord: Coord) -> Dict:
        x0, y0, x1, y1 = coord
        return dict(type="line",
                    xref=xref,
                    yref=yref,
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    line=dict(color=col,
                              width=width),
                    opacity=opacity,
                    layer=layer)

    if use_shape:
        assert xref in ("x", "paper") and yref in ("y", "paper"), \
            "`[x|y]ref` must be '[x|y]' or 'paper'"
        assert layer in ("above", "below"), \
            "`layer` must be one of {'above' or 'below'}"
        return (coord_to_shape(coords) if not isinstance(coords, list)
                else list(map(coord_to_shape, coords)))

    if not isinstance(coords, list):
        coords = [coords]
    return scatter(x=[x for x0, _, x1, _ in coords
                      for x in (x0, x1, None)],
                   y=[y for _, y0, _, y1 in coords
                      for y in (y0, y1, None)],
                   text=([x for t in text for x in (t, t, None)]
                         if text is not None else text),
                   mode="lines",
                   line_width=width,
                   col=col,
                   opacity=opacity,
                   name=name,
                   show_legend=show_legend,
                   show_init=show_init,
                   use_webgl=use_webgl)
