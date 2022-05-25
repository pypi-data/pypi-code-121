from typing import Any, Union, Optional, Sequence, Set
import numpy as np
import plotly.graph_objects as go
import plotly.tools as tls
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles
from matplotlib import pyplot as plt

DataSet = Union[Sequence, Set[Any]]


def venn(data: Sequence[DataSet],
         labels: Sequence[str],
         cols: Optional[Sequence[str]] = None,
         line_col: str = "black",
         line_width: float = 2,
         area_proportional: bool = True,
         opacity: float = 1,
         width: int = 500,
         height: int = 500,
         dpi: int = 100,
         title: Optional[str] = "") -> None:
    """Create a static plot of a Venn diagram.

    positional arguments:
      @ data   : Raw data sets.
      @ labels : Labels for each data set.

    optional arguments:
      @ cols       : Color of bars. If not specified, white is applied.
      @ line_col   : Color of the border circle.
      @ line_width : Width of the border circle.
      @ opacity    : Of the colors inside the circles.
      @ width, height, dpi
                   : Of the figure. The font size is adjusted by the
                     combination of them.
      @ title      : Of the figure.
    """
    N = len(data)
    assert N in (2, 3), f"len(data) ({N}) must be 2 or 3"
    assert len(data) == len(labels), \
        f"len(data)={len(data)} != len(labels)={len(labels)}"
    assert cols is None or len(data) == len(cols), \
        f"len(data)={len(data)} != len(cols)={len(cols)}"

    data_sets = [set(x) for x in data]
    fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    ax = fig.add_subplot(111, title=title)
    (venn2 if N == 2 else venn3)(data_sets,
                                 set_labels=labels,
                                 set_colors=("white",) * N if cols is None else cols,
                                 alpha=opacity, ax=ax)
    (venn2_circles if N == 2 else venn3_circles)(data_sets,
                                                 color=line_col,
                                                 linewidth=line_width, ax=ax)
    plt.show()
    return
