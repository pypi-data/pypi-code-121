from typing import Any, Union, Optional, Sequence, Mapping
from numbers import Number
from collections import Counter
import numpy as np
import plotly.graph_objects as go
from ._bar import bar
from ._line import lines


class RelCounter(Counter):
    """Subclass of Counter with a method returning the relative frequencies."""

    def relative(self):
        tot = sum(self.values())
        return {k: v / tot * 100 for k, v in self.items()}


def hist(data: Union[Sequence, Mapping[Any, int]],
         text: Optional[Sequence] = None,
         start: Optional[int] = None,
         end: Optional[int] = None,
         bin_size: Optional[int] = None,
         bin_num: int = 10,
         relative: bool = False,
         col: Optional[str] = None,
         opacity: float = 1,
         use_lines: bool = False,
         line_width: float = 1,
         use_webgl: bool = True,
         use_histogram: bool = False,
         name: Optional[str] = None,
         show_legend: bool = False,
         show_init: bool = True) -> Union[go.Bar, go.Histogram]:
    """Create a simple Trace object of a histogram.

    positional arguments:
      @ data : Raw data of numbers or counter of numbers

    optional arguments:
      @ text          : Texts for each data.
      @ start         : Start position of the plot range.
      @ end           : End position of the plot range.
      @ bin_size      : Size of each bin.
      @ bin_num       : Number of bins. Ignored if `bin_size` is set.
      @ relative      : Convert values in y-axis to relative frequencies.
      @ col           : Color of bars.
      @ opacity       : Opacity of bars.
      @ use_lines     : If True, draw as lines of a scatter plot.
                        Use this for large datasets.
      @ use_histogram : If True, force to use `go.Histogram`.
                        This is not recommended in most cases.
      @ name          : Display name of the trace in legend.
      @ show_legend   : Show this trace in legend.
      @ show_init       : Show this trace initially.

    optional arguments valid only if `use_lines` is True:
      @ line_width    : Corresponds to bin width.
      @ use_webgl     : Use WebGL instead of SVG.
    """
    def _to_trace(x, y) -> Union[go.Bar, go.Scatter]:
        if use_lines:
            return lines([(_x, 0, _x, _y) for _x, _y in zip(x, y)],
                         text=text,
                         width=line_width,
                         col=col,
                         opacity=opacity,
                         name=name,
                         show_legend=show_legend,
                         show_init=show_init,
                         use_webgl=use_webgl)
        else:
            return bar(x=x,
                       y=y,
                       text=text,
                       col=col,
                       opacity=opacity,
                       name=name,
                       show_legend=show_legend,
                       show_init=show_init)

    assert len(data) > 0, "Empty data"

    # Use the original histogram function anyway (not recommended)
    if use_histogram:
        assert isinstance(data, Sequence), \
            "Only Sequence objects are supported if `use_histogram`."
        return go.Histogram(x=data,
                            xbins=dict(start=start,
                                       end=end,
                                       size=bin_size),
                            histnorm="percent" if relative else "",
                            marker=dict(color=col),
                            opacity=opacity,
                            name=name,
                            showlegend=show_legend,
                            visible=None if show_init else "legendonly")

    # Already a dictionary (counter), or non-numerical, categorical data
    if isinstance(data, Mapping) or not isinstance(next(iter(data)), Number):
        counter = RelCounter(data)
        if relative:
            counter = counter.relative()
        if text is not None:
            assert len(counter) == len(text), \
                f"Length of `text` ({len(text)}) != # of data ({len(counter)})"
        return _to_trace(*zip(*counter.items()))
    # Numerical data
    if start is None:
        start = min(data)
    if end is None:
        end = max(data)
    if bin_size is not None:
        bin_num = -int(-(end - start + bin_size) // bin_size)
    else:
        bin_size = (end - start) / bin_num
    counts, bin_edges = np.histogram(data,
                                     weights=(np.ones(len(data))/float(len(data))
                                              if relative else None),
                                     range=(start - bin_size / 2,
                                            end + bin_size / 2),
                                     bins=bin_num)
    if text is not None:
        assert len(counts) == len(text), \
            f"Length of `text` ({len(text)}) != # of bins ({len(counts)})"
    return _to_trace([(bin_edges[i] + bin_edges[i + 1]) / 2
                      for i in range(len(bin_edges) - 1)],
                     counts)
