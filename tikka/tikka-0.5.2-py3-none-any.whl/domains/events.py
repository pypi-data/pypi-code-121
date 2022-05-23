# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Callable

from tikka.interfaces.entities.events import EventInterface


class EventDispatcher:
    """
    Generic event dispatcher which listen and dispatch events
    """

    def __init__(self) -> None:
        """
        Init EventDispatcher instance

        :return:
        """
        self._events: dict = {}

    def __del__(self):
        """
        Remove all listener references at destruction time

        :return:
        """
        self._events = None

    def has_listener(self, event_type: str, listener: Callable) -> bool:
        """
        Return true if listener is registered to event_type

        :param event_type: Type of event
        :param listener: Callable method or function to call when event occurs
        :return:
        """
        # Check for event type and for the listener
        if event_type in self._events:
            return listener in self._events[event_type]

        return False

    def dispatch_event(self, event: EventInterface) -> None:
        """
        Dispatch an instance of Event class

        :param event: Event instance
        :return:
        """
        # Dispatch the event to all the associated listeners
        if event.type in self._events:
            listeners = self._events[event.type]

            for listener in listeners:
                listener(event)

    def add_event_listener(self, event_type: str, listener: Callable) -> None:
        """
        Add an event listener for an event type

        :param event_type: Type of event
        :param listener: Callable method or function to call when event occurs
        :return:
        """
        # Add listener to the event type
        if not self.has_listener(event_type, listener):
            listeners = self._events.get(event_type, [])

            listeners.append(listener)

            self._events[event_type] = listeners

    def remove_event_listener(self, event_type: str, listener: Callable) -> None:
        """
        Remove event listener.

        :param event_type: Type of event
        :param listener: Callable method or function to call when event occurs
        :return:
        """
        # Remove the listener from the event type
        if self.has_listener(event_type, listener):
            listeners = self._events[event_type]

            if len(listeners) == 1:
                # Only this listener remains so remove the key
                del self._events[event_type]

            else:
                # Update listeners chain
                listeners.remove(listener)

                self._events[event_type] = listeners
