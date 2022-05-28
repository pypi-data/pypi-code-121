"""
    Model classes. Useful for bindings.
"""
from __future__ import annotations

# standard libraries
import asyncio
import operator
import typing

# third party libraries
# none

# local libraries
import weakref

from . import Event
from . import Observable
from . import Stream
from .ReferenceCounting import weak_partial

EqualityOperator = typing.Callable[[typing.Any, typing.Any], bool]

T = typing.TypeVar('T')


class PropertyModel(Observable.Observable, typing.Generic[T]):
    """Holds a value which can be observed for changes.

    The value can be any type that supports equality test.

    An optional on_value_changed method gets called when the value changes.
    """

    def __init__(self, value: typing.Optional[T] = None, cmp: typing.Optional[typing.Callable[[typing.Optional[T], typing.Optional[T]], bool]] = None):
        super().__init__()
        self.__value = value
        self.__cmp = cmp if cmp else typing.cast(typing.Callable[[typing.Optional[T], typing.Optional[T]], bool], operator.eq)
        self.on_value_changed : typing.Optional[typing.Callable[[typing.Optional[T]], None]] = None

    def close(self) -> None:
        pass

    @property
    def value(self) -> typing.Optional[T]:
        return self.__value

    @value.setter
    def value(self, value: typing.Optional[T]) -> None:
        if self.__value is None:
            not_equal = value is not None
        elif value is None:
            not_equal = self.__value is not None
        else:
            not_equal = not self.__cmp(value, self.__value)
        if not_equal:
            self._set_value(value)
            if self.on_value_changed:
                self.on_value_changed(value)

    def _set_value(self, value: typing.Optional[T]) -> None:
        self.__value = value
        self.notify_property_changed("value")


class FuncStreamValueModel(PropertyModel[T], typing.Generic[T]):
    """Converts a stream of functions to a property model, evaluated asynchronously, on a thread."""

    def __init__(self, value_func_stream: Stream.AbstractStream[typing.Callable[[], T]],
                 event_loop: asyncio.AbstractEventLoop, value: typing.Optional[T] = None,
                 cmp: typing.Optional[EqualityOperator] = None):
        super().__init__(value=value, cmp=cmp)
        self.__value_func_stream = value_func_stream
        self.__event_loop = event_loop
        self.__pending_task = Stream.StreamTask(None, event_loop)
        self.__value_fn_ref: typing.List[typing.Callable[[], typing.Any]] = [lambda: None]
        self.__event = asyncio.Event()
        self.__evaluating = [False]

        # Python 3.9: use ReferenceType[FuncStreamValueModel] for model_ref
        async def update_value(event: asyncio.Event, evaluating: typing.List[bool], model_ref: typing.Any, value_fn_ref: typing.Sequence[typing.Callable[[], typing.Any]]) -> None:
            while True:
                await event.wait()
                evaluating[0] = True
                event.clear()
                value = None

                def eval() -> None:
                    nonlocal value
                    try:
                        value = value_fn_ref[0]()
                    except Exception as e:
                        pass

                await event_loop.run_in_executor(None, eval)
                model = model_ref()
                if model:
                    model.value = value
                    model = None  # immediately release value for gc
                evaluating[0] = event.is_set()

        self.__pending_task.create_task(update_value(self.__event, self.__evaluating, weakref.ref(self), self.__value_fn_ref))
        self.__stream_listener = value_func_stream.value_stream.listen(weak_partial(FuncStreamValueModel.__handle_value_func, self))
        value_func = self.__value_func_stream.value
        if value_func:
            self.__handle_value_func(value_func)

        def finalize(pending_task: Stream.StreamTask) -> None:
            pending_task.clear()

        weakref.finalize(self, finalize, self.__pending_task)

    def _run_until_complete(self) -> None:
        while True:
            self.__event_loop.stop()
            self.__event_loop.run_forever()
            if not self.__evaluating[0]:
                break

    def _evaluate_immediate(self) -> typing.Optional[T]:
        value_func = self.__value_func_stream.value
        assert value_func
        return value_func()

    def __handle_value_func(self, value_func: typing.Callable[[], typing.Any]) -> None:
        self.__value_fn_ref[0] = value_func
        self.__event.set()


class StreamValueModel(PropertyModel[T], typing.Generic[T]):
    """Converts a stream to a property model."""

    def __init__(self, value_stream: Stream.AbstractStream[T], value: typing.Optional[T] = None,
                 cmp: typing.Optional[EqualityOperator] = None) -> None:
        super().__init__(value=value, cmp=cmp)
        self.__value_stream = value_stream

        def handle_value(model: StreamValueModel[T], value: typing.Any) -> None:
            model.value = value

        self.__stream_listener = value_stream.value_stream.listen(weak_partial(handle_value, self))

        handle_value(self, value_stream.value)


class PropertyChangedPropertyModel(PropertyModel[T], typing.Generic[T]):
    """Observes a property on another item and makes it a standard property model.

    When the observed property changes, update this value.

    When this value changes, update the observed property.
    """

    def __init__(self, observable: Observable.Observable, property_name: str) -> None:
        super().__init__(getattr(observable, property_name, None))
        self.__observable = observable
        self.__property_name = property_name

        def property_changed(property_model: PropertyChangedPropertyModel[T], observable: Observable.Observable, property_name: str, property_name_: str) -> None:
            # check if changed property matches property name for this object
            if property_name_ == property_name:
                property_model.value = getattr(observable, property_name)

        self.__listener = self.__observable.property_changed_event.listen(weak_partial(property_changed, self, observable, property_name))

    def _set_value(self, value: typing.Optional[T]) -> None:
        super()._set_value(value)
        # set the property on the observed object. this will trigger a property changed, but will be ignored since
        # the value doesn't change.
        setattr(self.__observable, self.__property_name, value)
