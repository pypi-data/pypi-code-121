# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Functions for handling Q-CTRL styling.
"""

from contextlib import contextmanager
from typing import (
    Any,
    Dict,
)

from cycler import cycler
from matplotlib import rcParams
from matplotlib.style import context

BORDER_COLOR = "#D8E0E9"
TEXT_COLOR = "#6C5C71"

FIG_WIDTH = 10.0
FIG_HEIGHT = 5.0

QCTRL_STYLE_COLORS = [
    "#680CE9",
    "#D84144",
    "#32A4A8",
    "#A2A933",
    "#D84190",
    "#4177D8",
    "#D6722F",
    "#D543ED",
    "#32A857",
]


def get_qctrl_style() -> Dict[str, Any]:
    """
    Returns a dictionary representing the Q-CTRL styling in Matplotlib format.

    The returned dictionary is suitable for passing to Matplotlib functions such as
    ``matplotlib.style.use`` or ``matplotlib.style.context``.

    Returns
    -------
    dict
        The dictionary representing the Q-CTRL style.
    """
    style: Dict[str, Any] = {}

    # Set text color.
    style["text.color"] = TEXT_COLOR
    style["xtick.color"] = TEXT_COLOR
    style["ytick.color"] = TEXT_COLOR
    style["axes.labelcolor"] = TEXT_COLOR

    # Set font to Roboto.
    style["font.sans-serif"] = ["Roboto"] + rcParams["font.sans-serif"]

    # Set figure size.
    style["figure.figsize"] = [FIG_WIDTH, FIG_HEIGHT]

    # Set borders and their color.
    style["axes.spines.left"] = True
    style["axes.spines.right"] = True
    style["axes.spines.top"] = True
    style["axes.spines.bottom"] = True
    style["axes.edgecolor"] = BORDER_COLOR
    style["legend.edgecolor"] = BORDER_COLOR
    style["lines.color"] = BORDER_COLOR

    # Set font sizes.
    style["font.size"] = 14
    style["legend.title_fontsize"] = 14
    style["legend.fontsize"] = 14
    style["figure.titlesize"] = 16
    style["axes.titlesize"] = 14
    style["axes.labelsize"] = 14
    style["xtick.labelsize"] = 12
    style["ytick.labelsize"] = 12

    # Set padding around labels.
    style["axes.labelpad"] = 15.0

    # Set background color white.
    style["figure.facecolor"] = "white"

    # Set cycle of colors for lines.
    style["axes.prop_cycle"] = cycler(color=QCTRL_STYLE_COLORS)

    # Set line width.
    style["lines.linewidth"] = 2

    return style


@contextmanager
def qctrl_style():
    """
    A ``ContextDecorator`` that enables the Q-CTRL Matplotlib styling.

    The returned object can act as a decorator::

        @qctrl_style()
        def plot(*args):
            # Matplotlib calls made in this function will use Q-CTRL styling.
            pass

    The returned object can also act as a context manager::

        with qctrl_style():
            # Matplotlib calls made in this function will use Q-CTRL styling.
            pass
    """
    with context(get_qctrl_style()) as ctx:
        yield ctx
