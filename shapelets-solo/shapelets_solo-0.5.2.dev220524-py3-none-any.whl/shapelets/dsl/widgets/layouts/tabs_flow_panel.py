# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.dsl.widgets.layouts.panel import Panel


class TabsFlowPanel(Panel):

    def __init__(self, panel_title: str = None, panel_id: str = None, **additional):
        super().__init__(panel_title=panel_title, panel_id=panel_id, **additional)
        self.tabs = list()

    def place(self, widget: Widget, tab_title: str = None):
        super()._place(widget)
        tab_title = tab_title if tab_title else f"Tab {len(self.tabs)}"
        self.tabs.append(tab_title)

    def to_dict_widget(self):
        panel_dict = super().to_dict_widget()
        panel_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.TABS.value: [{"title": tab} for tab in self.tabs]
        })
        return panel_dict
