# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.dsl.data_app_events import EventProducer, DSLAlgoReturnType


class Timer(Widget, EventProducer):
    def __init__(self,
                 title: str, every: int, start_delay: int = None, times: int = None, hidden: bool = False,
                 **additional):
        Widget.__init__(self, self.__class__.__name__, "Timer", **additional)
        EventProducer.__init__(self)
        self.title = title
        self.every = every
        self.start_delay = start_delay
        self.times = times
        self.hidden = hidden

    def run(self, algorithm: DSLAlgoReturnType):
        return self._link_event("timer", self.parent_data_app, algorithm)

    def to_dict_widget(self):
        timer_dict = super().to_dict_widget()

        if self.start_delay is not None:
            timer_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.START_DELAY.value: self.start_delay
            })

        if self.times is not None:
            timer_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.TIMES.value: self.times
            })

        timer_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.TITLE.value: self.title,
            AttributeNames.EVERY.value: self.every,
            AttributeNames.HIDDEN.value: self.hidden,
            AttributeNames.EVENTS.value: [event.to_dict() for event in self.events]
        })
        return timer_dict
