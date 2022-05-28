"""
An event object to which to attach listeners.
"""

from __future__ import annotations

# standard libraries
import threading
import traceback
import sys
import types
import typing
import weakref

# third party libraries
# None

# local libraries
# None


WeakListenerType = typing.Any  # should be weakref.ReferenceType[EventListener] after Python 3.9
EventListenerCallableType = typing.Callable[..., typing.Any]


def void(*args: typing.Any, **kwargs: typing.Any) -> None:
    pass


class EventListener:

    def __init__(self, listener_fn: EventListenerCallableType, trace: bool) -> None:
        self.tb = traceback.extract_stack() if trace else None
        # the call function is very performance critical; make it fast by using a property
        # instead of a method lookup.
        if callable(listener_fn):
            self.call = listener_fn
        else:
            self.call = void

    def close(self) -> None:
        """Optional. Replaces call to confirm the event is not triggered after called."""
        call = self.call

        def void(*args: typing.Any, **kwargs: typing.Any) -> None:
            print(f"CALL AFTER CLOSE {call}")

        self.call = void

    def __enter__(self) -> EventListener:
        return self

    def __exit__(self, exception_type: typing.Optional[typing.Type[Exception]], value: typing.Optional[Exception],
                 traceback: typing.Optional[types.TracebackType]) -> None:
        self.close()


class Event:
    """An event object that to which listeners can be attached."""

    def __init__(self, trace: bool = False) -> None:
        self.__weak_listeners: typing.List[WeakListenerType] = list()
        self.__weak_listeners_mutex = threading.RLock()
        self.__listeners: typing.Dict[int, typing.Tuple[EventListener, WeakListenerType]] = dict()
        self.__trace = trace

    @property
    def listener_count(self) -> int:
        return len(self.__weak_listeners)

    @property
    def listeners(self) -> typing.Sequence[typing.Optional[EventListener]]:
        return [w() for w in self.__weak_listeners]

    def listen(self, listener_fn: EventListenerCallableType, *, owner: typing.Any = None, trace: bool = False) -> EventListener:
        """Add a listener function and return listener. Listener can be closed or unreferenced to unlisten."""
        listener = EventListener(listener_fn, self.__trace)

        def remove_listener(weak_listener: WeakListenerType) -> None:
            if trace:
                traceback.print_stack()
            with self.__weak_listeners_mutex:
                self.__weak_listeners.remove(weak_listener)

        weak_listener = weakref.ref(listener, remove_listener)
        with self.__weak_listeners_mutex:
            self.__weak_listeners.append(weak_listener)
        if owner:
            def owner_gone(weak_owner: typing.Any) -> None:
                del self.__listeners[id(weak_owner)]

            weak_owner = weakref.ref(owner, owner_gone)
            self.__listeners[id(weak_owner)] = listener, weak_owner
        return listener

    def __print_event_exception(self, exc_listener: EventListener) -> None:
        print("Event Fire Traceback (most recent call last):", file=sys.stderr)
        etype, value, tb = sys.exc_info()
        value = value or Exception()
        # tb = tb or TracebackType
        frame_summaries = typing.cast(typing.List[typing.Any], traceback.extract_stack()[:-2])
        for line in traceback.StackSummary.from_list(frame_summaries).format():
            print(line, file=sys.stderr, end="")
        if exc_listener.tb is not None:
            print(f"Event Listener Traceback (most recent call last)", file=sys.stderr)
            frame_summaries = typing.cast(typing.List[typing.Any], exc_listener.tb[:-2])
            for line in traceback.StackSummary.from_list(frame_summaries).format():
                print(line, file=sys.stderr, end="")
        print(f"Event Handler Traceback (most recent call last)", file=sys.stderr)
        traceback_exception = traceback.TracebackException(type(value), value, typing.cast(typing.Any, tb))
        frame_summaries = typing.cast(typing.List[typing.Any], traceback_exception.stack[1:])
        traceback_exception.stack = traceback.StackSummary.from_list(frame_summaries)
        setattr(traceback_exception, "exc_traceback", None)  # prevent printing of header
        for line in traceback_exception.format(chain=True):
            print(line, file=sys.stderr, end="")

    def fire(self, *args: typing.Any, **keywords: typing.Any) -> None:
        """Calls listeners (in order added) unconditionally."""
        listener = None
        if self.__weak_listeners:
            try:
                # copy the weak listeners; be careful to unreference listener just after use.
                with self.__weak_listeners_mutex:
                    weak_listeners = list(self.__weak_listeners)
                for weak_listener in weak_listeners:
                    listener = weak_listener()
                    if listener:
                        listener.call(*args, **keywords)
                    listener = None
            except Exception as e:
                if listener:
                    self.__print_event_exception(listener)

    def fire_any(self, *args: typing.Any, **keywords: typing.Any) -> bool:
        """Calls listeners (in order added) until one returns True or else return False."""
        listener = None
        if self.__weak_listeners:
            try:
                # copy the weak listeners; be careful to unreference listener just after use.
                with self.__weak_listeners_mutex:
                    weak_listeners = list(self.__weak_listeners)
                for weak_listener in weak_listeners:
                    listener = weak_listener()
                    if listener:
                        if listener.call(*args, **keywords):
                            return True
                    listener = None
            except Exception as e:
                if listener:
                    self.__print_event_exception(listener)
        return False

    def fire_all(self, *args: typing.Any, **keywords: typing.Any) -> bool:
        """Calls listeners (in order added) until one returns False or else return True."""
        listener = None
        if self.__weak_listeners:
            try:
                # copy the weak listeners; be careful to unreference listener just after use.
                with self.__weak_listeners_mutex:
                    weak_listeners = list(self.__weak_listeners)
                for weak_listener in weak_listeners:
                    listener = weak_listener()
                    if listener:
                        if not listener.call(*args, **keywords):
                            return False
                    listener = None
            except Exception as e:
                if listener:
                    self.__print_event_exception(listener)
        return True
