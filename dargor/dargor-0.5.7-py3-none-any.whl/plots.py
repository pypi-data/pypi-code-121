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

import numpy as np
from matplotlib.axes import Axes  # type: ignore[import]
from matplotlib.backend_bases import LocationEvent  # type: ignore[import]
from matplotlib.figure import Figure  # type: ignore[import]


class CursorLines:

    def __init__(self, fig: Figure, *, color: str = 'black', ls: str = ':'):
        lineprops = {
            'color': color,
            'ls': ls,
            'visible': False,
            'animated': True,
        }
        self.fig = fig
        self.hlines = {
            ax: ax.axhline(np.nan, **lineprops)
            for ax in fig.axes
        }
        self.vlines = [
            ax.axvline(np.nan, **lineprops)
            for ax in fig.axes
        ]
        self.background = None
        self.background_rotten = True
        # we need to keep these references to avoid garbage collection
        self._on_draw = fig.canvas.mpl_connect('draw_event',
                                               self.on_draw)
        self._on_resize = fig.canvas.mpl_connect('resize_event',
                                                 self.on_resize)
        self._on_motion = fig.canvas.mpl_connect('motion_notify_event',
                                                 self.on_motion)
        # this one is needed if you patch your figure with CursorLines(fig)
        # instead of cl = CursorLines(fig)
        self.fig._CursorLines = self

    def on_draw(self, _ev: LocationEvent) -> None:
        self.background_rotten = True

    def on_resize(self, _ev: LocationEvent) -> None:
        self.background_rotten = True

    def on_motion(self, ev: LocationEvent) -> None:
        canvas = self.fig.canvas

        try:
            canvas.widgetlock(self)
        except ValueError:
            # already locked
            return

        try:

            if self.background_rotten:
                canvas.draw()
                self.background = canvas.copy_from_bbox(canvas.figure.bbox)
                self.background_rotten = False
            else:
                canvas.restore_region(self.background)

            if ev.inaxes:
                xdata = (ev.xdata, ev.xdata)
                ydata = (ev.ydata, ev.ydata)
                for vline in self.vlines:
                    ax = vline.axes
                    vline.set_xdata(xdata)
                    vline.set_visible(True)
                    ax.draw_artist(vline)
                    if ev.inaxes != ax:
                        continue
                    hline = self.hlines[ax]
                    hline.set_ydata(ydata)
                    hline.set_visible(True)
                    ax.draw_artist(hline)

            canvas.blit(canvas.figure.bbox)

        finally:
            canvas.widgetlock.release(self)


def maybe_add_legend(ax: Axes, *, loc: str = 'best') -> None:
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(handles, labels, loc=loc)
