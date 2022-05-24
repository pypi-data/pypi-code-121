# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl.data_app_events import (
    DSLAlgoReturnType,
    EventProducer
)
from shapelets.dsl.widgets import Widget, AttributeNames


class Button(Widget, EventProducer):
    def __init__(self,
                 widget_name: str = None,
                 text_button: str = "",
                 **additional):
        Widget.__init__(self, self.__class__.__name__, widget_name, **additional)
        EventProducer.__init__(self)
        self.text = text_button

    def on_click(self, algorithm: DSLAlgoReturnType):
        return self._link_event("click", self.parent_data_app, algorithm)

    def to_dict_widget(self):
        button_dict = super().to_dict_widget()
        button_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.TEXT.value: self.text,
            AttributeNames.EVENTS.value: [event.to_dict() for event in self.events]
        })
        return button_dict
