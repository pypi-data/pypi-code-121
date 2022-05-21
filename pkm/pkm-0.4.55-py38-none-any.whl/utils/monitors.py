import inspect
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Type, Dict, Optional, Generator

from pkm.utils.dicts import get_or_put
from pkm.utils.properties import cached_property
from pkm.utils.strings import startswith_any


@dataclass
class _Callback:
    parent: Optional["_Callback"] = None
    enter_method: Optional[Callable] = None
    leave_method: Optional[Callable] = None
    fail_method: Optional[Callable] = None


# noinspection PyUnusedLocal
class _Monitor:

    @cached_property
    def _callbacks(self) -> Dict[Type, _Callback]:
        return {}

    def add_listeners(self, **callbacks):
        new_callbacks: Dict[Type, _Callback] = self._create_callbacks(callbacks)
        for type_, callback in new_callbacks.items():
            self._callbacks[type_] = callback

    @contextmanager
    def listen(self, **callbacks):

        method_name: str
        new_callbacks: Dict[Type, _Callback] = self._create_callbacks(callbacks)
        for type_, callback in new_callbacks.items():
            self._callbacks[type_] = callback

        try:
            yield
        finally:
            for type_, callback in new_callbacks.items():
                self._callbacks[type_] = callback.parent

    def _create_callbacks(self, callbacks: Dict[str, Any]) -> Dict[Type, _Callback]:
        new_callbacks: Dict[Type, _Callback] = {}
        for method_name, method in callbacks.items():
            if (mode := startswith_any(method_name, ("enter_", "leave_", "on_", "failed_", "with_"))) \
                    and isinstance(method, Callable):

                arg_inspection = inspect.getfullargspec(method)
                if len(arg_inspection.args) == 0:
                    continue

                first_arg = arg_inspection.args[0]
                if first_arg_type := arg_inspection.annotations.get(first_arg):
                    callback: _Callback = get_or_put(
                        new_callbacks, first_arg_type,
                        lambda: _Callback(self._callbacks.get(first_arg_type)))

                    if mode in ("enter_", "on_"):
                        callback.enter_method = method
                    elif mode == "leave_":
                        callback.leave_method = method
                    elif mode == "failed_":
                        callback.fail_method = method
                    else:  # mode == with_

                        def create(method_):
                            coroutines: Dict[int, Generator] = {}

                            def enter(x, *args, **kwargs):
                                if isinstance(coroutine := method_(x, *args, **kwargs), Generator):
                                    try:
                                        coroutine.__next__()
                                        coroutines[id(x)] = coroutine
                                    except StopIteration:
                                        pass

                            def leave(x, *args, **kwargs):
                                if coroutine := coroutines.pop(id(x), None):
                                    try:
                                        coroutine.__next__()
                                    except StopIteration:
                                        pass

                            def fail(x: Any, err: Exception, *args, **kwargs):
                                if coroutine := coroutines.pop(id(x), None):
                                    coroutine.throw(err)

                            callback.enter_method = enter
                            callback.leave_method = leave
                            callback.fail_method = fail

                        create(method)
        return new_callbacks

    @contextmanager
    def enter(self, context: Any):

        cb = self._callbacks.get(type(context))
        if isinstance(context, _Monitor):
            context._parent_monitor = self

        try:
            cb and cb.enter_method and cb.enter_method(context)
            yield
        except Exception as e:
            cb and cb.fail_method and cb.fail_method(context, e)
        finally:
            cb and cb.leave_method and cb.leave_method(context)

    def notify(self, event: Any):
        (cb := self._callbacks.get(type(event))) and cb.enter_method(event)


Monitor = _Monitor()


class MonitoredEvent:
    def notify(self, monitor: _Monitor = Monitor):
        monitor.notify(self)


class MonitoredOperation(_Monitor):
    def __enter__(self):
        # noinspection PyProtectedMember
        if hasattr(self, '_parent_monitor'):
            parent = self._parent_monitor
        else:
            parent = Monitor

        cb = self._callback = parent._callbacks.get(type(self))

        cb and cb.enter_method and cb.enter_method(self)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cb = self._callback

        if exc_type:
            cb and cb.fail_method and cb.fail_method(self, exc_val)

        cb and cb.leave_method and cb.leave_method(self)
