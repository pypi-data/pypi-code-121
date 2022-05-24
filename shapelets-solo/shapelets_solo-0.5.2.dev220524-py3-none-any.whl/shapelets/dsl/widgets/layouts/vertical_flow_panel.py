# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Tuple

from shapelets.dsl.widgets import Widget
from shapelets.dsl.widgets.layouts.panel import Panel


class VerticalFlowPanel(Panel):
    """
        TO BE FILLED
    """

    def place(self, *widget: Tuple[Widget, ...]):
        super()._place(*widget)

    def to_dict_widget(self):
        return super().to_dict_widget()
