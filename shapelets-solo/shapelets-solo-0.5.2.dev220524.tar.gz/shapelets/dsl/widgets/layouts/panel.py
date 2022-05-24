# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Tuple

from shapelets.dsl.widgets import Widget, AttributeNames


class Panel(Widget):
    """
    Container + Layout
    """

    def __init__(self,
                 panel_title: str = None,
                 panel_id: str = None,
                 **additional
                 ):
        super().__init__(
            widget_type=self.__class__.__name__,
            widget_id=panel_id,
            **additional
        )
        self.panel_title = panel_title
        self.widgets = list()

    def _place(self, *widget: Tuple[Widget, ...]):
        self.widgets.extend(widget)

    def to_dict_widget(self):
        panel_dict = super().to_dict_widget()
        if self.widgets is not None:
            widgets = [widget.to_dict_widget() for widget in self.widgets]
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.WIDGETS.value: widgets
            })
        if self.panel_title:
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.TITLE.value: self.panel_title
            })
        return panel_dict
