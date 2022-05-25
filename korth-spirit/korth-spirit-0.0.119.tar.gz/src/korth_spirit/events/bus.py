# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from typing import Union

from korth_spirit.sdk import CallBackEnum, EventEnum

from .event import Event
from .translations import TRANSLATIONS

EventType = Union[EventEnum, CallBackEnum]
class EventBus:
    def _hook_aw_event(self, event: EventType) -> None:
        """
        Republish AW events to the bus.

        Args:
            event (EventType): The event to publish and hook.
        """
        from korth_spirit.sdk import AW_CALLBACK, aw_callback_set, aw_event_set

        @AW_CALLBACK
        def mini_pub() -> None:
            self.publish(event)

        self._refs[event] = mini_pub

        if type(event) is EventEnum:
            aw_event_set(event, mini_pub)
        elif type(event) is CallBackEnum:
            aw_callback_set(event, mini_pub)

    def __init__(self):
        self._refs = {}
        self._subscribers = {}

    def subscribe(self, event: EventType, subscriber: callable) -> "EventBus":
        """
        Subscribe to an event.

        Args:
            event (EventType): The event to subscribe to.
            subscriber (callable): The subscriber to the event.

        Returns:
            EventBus: The event bus.
        """
        if event not in self._subscribers:
            self._subscribers[event] = []
            self._hook_aw_event(event)
        self._subscribers[event].append(subscriber)

        return self

    def unsubscribe(self, event: EventType, subscriber: callable) -> "EventBus":
        """
        Unsubscribe from an event.

        Args:
            event (EventType): The event to unsubscribe from.
            subscriber (callable): The subscriber to the event.

        Returns:
            EventBus: The event bus.
        """
        if event in self._subscribers:
            self._subscribers[event].remove(subscriber)

        return self

    def unsubscribe_all(self) -> "EventBus":
        """
        Unsubscribe from all events.

        Args:
            event (EventType): The event to unsubscribe from.

        Returns:
            EventBus: The event bus.
        """
        for ref in self._refs:
            from korth_spirit.sdk import aw_callback_set, aw_event_set

            if type(ref) is EventEnum:
                aw_event_set(ref, None)
            elif type(ref) is CallBackEnum:
                aw_callback_set(ref, None)

        self._refs = {}
        self._subscribers = {}

        return self

    def publish(self, event: EventType, *args, **kwargs) -> "EventBus":
        """
        Publish an event.

        Args:
            event (EventType): The event to publish.
            *args: The arguments to pass to the subscribers.
            **kwargs: The keyword arguments to pass to the subscribers.

        Returns:
            EventBus: The event bus.
        """
        translations = TRANSLATIONS.get(event, {})
        wrapped_event = Event(event, translations)
        if event in self._subscribers:
            for subscriber in self._subscribers[event]:
                subscriber(wrapped_event, *args, **kwargs)
        
        return self
