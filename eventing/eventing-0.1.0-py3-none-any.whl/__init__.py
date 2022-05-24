"""Eventing package for Python.

A pythonic event emitter inspired by Node.js'
EventEmitter and Python's logging libraries.
"""

from __future__ import annotations

__version__ = "0.1.0"

from collections import defaultdict
import warnings

from .validation import event_name_validator
from .validation import validate_arguments


class Manager:
    def __init__(self, root_node: EventEmitter):
        self.root = root_node
        self.emitter_dict: dict[str, EventEmitter] = {}

    def get_emitter(self, name: str) -> EventEmitter:
        if not isinstance(name, str):
            raise TypeError("An emitter name must be a string")
        try:
            return self.emitter_dict[name]
        except KeyError:
            emitter = EventEmitter(name)
            self.emitter_dict[name] = emitter
            return emitter


class EventEmitter:
    manager: Manager
    root: RootEmitter

    def __init__(self, name: str):
        self.name = name
        self._listeners: defaultdict[str, list] = defaultdict(list)

    @validate_arguments(event_name_validator)
    def listener_count(self, event_name: str, /) -> int:
        return len(self._listeners[event_name])

    @validate_arguments(event_name_validator)
    def listeners(self, event_name: str, /) -> list[EventEmitter]:
        return self._listeners[event_name]

    @validate_arguments(event_name_validator)
    def add_listener(self, event_name: str, /, listener) -> EventEmitter:
        self._listeners[event_name].append(listener)
        return self

    @validate_arguments(event_name_validator)
    def remove_listener(self, event_name: str, /, listener) -> EventEmitter:
        try:
            self._listeners[event_name].remove(listener)
        except ValueError:
            warnings.warn("Attempted to remove listener not present.")
        return self

    @validate_arguments(event_name_validator)
    def emit(self, event_name: str, /, *args, **kwargs) -> bool:
        listeners = self._listeners[event_name]
        for listener in listeners:
            listener(*args, **kwargs)

        return bool(listeners)


class RootEmitter(EventEmitter):
    def __init__(self):
        super().__init__("root")


root = RootEmitter()
EventEmitter.root = root
EventEmitter.manager = Manager(root)


def get_emitter(name: str = "") -> EventEmitter:
    if name in ("", root.name):
        return root
    else:
        return EventEmitter.manager.get_emitter(name)
