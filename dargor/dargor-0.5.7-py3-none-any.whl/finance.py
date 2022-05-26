#
# Copyright (c) 2022, Gabriel Linder <linder.gabriel@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

from matplotlib.axes import Axes  # type: ignore[import]
from matplotlib.dates import date2num  # type: ignore[import]
from matplotlib.lines import Line2D  # type: ignore[import]
from matplotlib.patches import Rectangle  # type: ignore[import]
from pandas import DataFrame  # type: ignore[import]


def bar_chart(ax: Axes, df: DataFrame, *, color: str = 'black',
              width: float = .6, alpha: float = 1.) -> None:
    # The vertical line represents the high and low for the period, while
    # the line to the left marks the open price and the line to the right
    # marks the closing price. This entire structure is called a bar.
    offset = width / 2.
    for t, row in df.iterrows():
        t = date2num(t)
        o, h, l, c = row['Open'], row['High'], row['Low'], row['Close']
        ax.add_line(Line2D(xdata=(t, t), ydata=(l, h),
                           color=color, alpha=alpha, zorder=0))
        ax.add_line(Line2D(xdata=(t - offset, t), ydata=(o, o),
                           color=color, alpha=alpha, zorder=0))
        ax.add_line(Line2D(xdata=(t, t + offset), ydata=(c, c),
                           color=color, alpha=alpha, zorder=0))


def candlestick_chart(
    ax: Axes, df: DataFrame, *, heikin_ashi: bool = False,
    colorup: str = 'forestgreen', colordown: str = 'orangered',
    width: float = .6, alpha: float = 1.,
) -> None:
    # The area between the open and the close prices is called the body,
    # price excursions above and below the body are shadows (also called
    # wicks). Wicks illustrate the highest and lowest traded prices of an
    # asset during the time interval represented. The body illustrates the
    # opening and closing trades. This entire structure is called a candle.
    offset = width / 2.
    prev = None
    for t, row in df.iterrows():
        t = date2num(t)
        o0, h0, l0, c0 = row['Open'], row['High'], row['Low'], row['Close']
        if heikin_ashi:
            # pylint: disable=W8201
            if prev is None:
                oP, hP, lP, cP = o0, h0, l0, c0
            else:
                oP, hP, lP, cP = prev
            c = (o0 + h0 + l0 + c0) / 4.
            o = (oP + cP) / 2.
            h = max(h0, o, c)
            l = min(l0, o, c)
            prev = o, h, l, c
        else:
            o, h, l, c = o0, h0, l0, c0  # pylint: disable=W8201
        if c >= o:
            color = colorup
            lower = o
            upper = c
        else:
            color = colordown
            lower = c
            upper = o
        height = upper - lower
        ax.add_line(Line2D(xdata=(t, t), ydata=(lower, l),
                           color=color, alpha=alpha))
        ax.add_line(Line2D(xdata=(t, t), ydata=(upper, h),
                           color=color, alpha=alpha))
        ax.add_patch(Rectangle(xy=(t - offset, lower),
                               width=width, height=height,
                               facecolor=color, edgecolor=color,
                               alpha=alpha))
