from typing import Optional, Dict


def rect(x0: float, y0: float, x1: float, y1: float,
         xref: str = "x",
         yref: str = "y",
         fill_col: str = "grey",
         opacity: float = 1.,
         frame_width: float = 0,
         frame_col: Optional[str] = None,
         layer: str = "above") -> Dict:
    """Create a (non-interactive) rectangle object.

    positional arguments:
      @ [x|y][0|1] : Diagonal line is from (x0, y0) to (x1, y1).

    positional arguments:
      @ [x|y]ref    : Must be one of {'[x|y]', 'paper'}.
                      If "paper", values of `[x|y]0,1` must be within [0, 1]
                      and are interpreted as relative positions in the entire
                      [x|y]-axis.
      @ fill_col    : Color of the rectangle.
      @ opacity     : Opacity of the rectangle.
      @ frame_width : Line width of the frame.
      @ frame_col   : Color of the frame.
      @ layer       : Drawing layer. Must be one of {'above', 'below'}.

    `xref` must be one of {"x" (default), "paper"}. "paper" means `x0` and `x1` indicate
    horizontal relative positions of the entire plot (values are in [0, 1]).
    (Same goes for `yref`.)
    `layer` must be one of {"above" (default), "below"}.
    """
    assert xref in ("x", "paper") and yref in ("y", "paper"), \
        "`[x|y]ref` must be '[x|y]' or 'paper'"
    assert layer in ("above", "below"), \
        "`layer` must be 'above' or 'below'"
    return dict(type="rect",
                xref=xref,
                yref=yref,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                fillcolor=fill_col,
                opacity=opacity,
                line=dict(color=frame_col,
                          width=frame_width),
                layer=layer)
