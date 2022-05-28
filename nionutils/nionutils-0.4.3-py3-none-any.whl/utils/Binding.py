"""
    Binding classes.
"""
from __future__ import annotations

# standard libraries
import functools
import typing
import weakref

# third party libraries
# none

# local libraries
from . import Converter
from . import Observable
from . import Validator
from .ReferenceCounting import weak_partial


class Binding:
    """Binding between two objects.

    Binds two objects, a source and target, together. Typically, the model object would
    be the source and the UI object would be the target. Also facilitates a converter
    object between the source and target to convert between value types. Observes the
    source object for changes.

    Bindings can be one way (from source to target) or two way (from source to target
    and back). The converter object, if used, must always supply a convert method. If
    this binding is two way, then it must also supply a convert_back method. The validator,
    if used, must supply a validate method (on the converted value and return a value).

    This class is not intended to be used directly. Instead, subclasses will implement
    specific source bindings by configuring the source_setter and source_getter methods
    and by using update_target appropriately.

    Clients of this class will set target_setter to directly connect the target, typically
    a UI element.

    The owner should call close on this object.

    Bindings are not sharable. They are meant to be used to bind one ui element to one
    value. However, conversions and binding sources can be shared between bindings in most
    cases.
    """

    def __init__(self, source: typing.Optional[Observable.ObservableLike], *,
                 converter: typing.Optional[Converter.ConverterLike[typing.Any, typing.Any]] = None,
                 validator: typing.Optional[Validator.ValidatorLike[typing.Any]] = None,
                 fallback: typing.Optional[typing.Any] = None) -> None:
        super().__init__()
        self.__converter = converter
        self.__validator = validator
        self.fallback = fallback
        self.source_getter: typing.Optional[typing.Callable[[], typing.Any]] = None
        self.source_setter: typing.Optional[typing.Callable[[typing.Any], None]] = None
        self.target_setter: typing.Optional[typing.Callable[[typing.Any], None]] = None
        # Python 3.9+: should weakref.ReferenceType
        self.__source_ref: typing.Optional[typing.Any] = weakref.ref(source) if source else None
        self._closed = False

    # not thread safe
    def close(self) -> None:
        pass

    @property
    def source(self) -> typing.Optional[typing.Any]:
        """Return the source of the binding. Thread safe."""
        return self.__source_ref() if self.__source_ref else None

    @property
    def converter(self) -> typing.Optional[Converter.ConverterLike[typing.Any, typing.Any]]:
        """Return the converter (from source to target). Thread safe."""
        return self.__converter

    @property
    def validator(self) -> typing.Optional[Validator.ValidatorLike[typing.Any]]:
        """Return the validator (of converted value). Thread safe."""
        return self.__validator

    # thread safe
    def __back_converted_value(self, target_value: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        """Return the back converted value (from target to source). Thread safe."""
        return self.__converter.convert_back(target_value) if self.__converter else target_value

    # thread safe
    def __converted_value(self, source_value: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        """Return the converted value (from source to target). Thread safe."""
        return self.__converter.convert(source_value) if self.__converter else source_value

    # thread safe
    def __validated_value(self, source_value: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        """Return the converted value (from source to target). Thread safe."""
        return self.__validator.validate(source_value) if self.__validator else source_value

    # public methods. subclasses must make sure these methods work as expected.

    # thread safe
    def update_source(self, target_value: typing.Optional[typing.Any]) -> None:
        """Update source with back converted target value.

        Update the source from the target value. The target value will be back converted.
        This is typically called by a target (UI element) to update the source (model).

        This method is required for two-way binding.

        Thread safe.
        """
        if callable(self.source_setter):
            converted_value = self.__validated_value(self.__back_converted_value(target_value))
            self.source_setter(converted_value)

    # not thread safe
    def update_target(self, source_value: typing.Optional[typing.Any]) -> None:
        """Update target with converted source value.

        Call the target setter with the unconverted value from the source.
        This is typically called by subclasses to update the target (UI element)
        when the source (model) changes.

        Required for both one-way and two-way bindings. It uses update_target_direct
        to call the target setter.

        Not thread safe.
        """
        self.update_target_direct(self.__converted_value(source_value))

    # not thread safe
    def update_target_direct(self, converted_value: typing.Optional[typing.Any]) -> None:
        """Update target directly with converted value.

        Call the target setter with the already converted value.
        This is typically called by subclasses to handle target setting
        when the conversion is already done, for instance for implementing
        a fallback, default, or placeholder value.

        Required for both one-way and two-way bindings.

        Not thread safe.
        """
        if callable(self.target_setter):
            self.target_setter(converted_value)

    # thread safe
    def get_target_value(self) -> typing.Optional[typing.Any]:
        """Return target value by converting source.

        Get the value from the source that will be set on the target.
        This is typically used by the target object to initialize its value.

        Required for both one-way and two-way bindings.

        Thread safe.
        """
        if callable(self.source_getter):
            source = self.source_getter()
            if source is not None:
                return self.__converted_value(source)
        return self.fallback


class PropertyBinding(Binding):
    """Two way binding from a source property to a target.

    Observes property changed event on a source and if the event matches the
    property name, calls the functions assigned to target_setter field.

    Source must support property_changed_event with the signature:
        property_changed(property_name: str) -> None

    Source must also support get/set attribute for the given property_name.

    Client should set the target_setter function to a callable with the signature:
        target_setter(value: Any) -> None

    The owner should call close on this object.
    """

    # TODO: generalize to 'getter binding'
    # TODO: generalize to 'two way getter connection'

    def __init__(self, source: Observable.ObservableLike, property_name: str, *,
                 converter: typing.Optional[Converter.ConverterLike[typing.Any, typing.Any]] = None,
                 validator: typing.Optional[Validator.ValidatorLike[typing.Any]] = None,
                 fallback: typing.Optional[typing.Any] = None) -> None:
        super().__init__(source, converter=converter, validator=validator, fallback=fallback)
        self.__property_name = property_name

        # thread safe. careful not to have reference to self, otherwise binding can't be garbage collected.
        def property_changed(binding: typing.Optional[PropertyBinding], property_name_: str) -> None:
            assert binding and not binding._closed
            if property_name_ == binding.property_name:
                assert callable(binding.source_getter)
                value = binding.source_getter()
                if value is not None:
                    binding.update_target(value)
                else:
                    binding.update_target_direct(binding.fallback)

        self.__property_changed_listener = source.property_changed_event.listen(weak_partial(property_changed, self))

        def set_property_value(source: typing.Any, value: typing.Any) -> None:
            try:
                if source:
                    setattr(source, property_name, value)
            except AttributeError as exc:
                raise AttributeError(property_name) from None

        def get_property_value(source: typing.Any) -> typing.Any:
            return getattr(source, property_name) if source else None

        # configure setting/getter, being careful not to hold references to self
        self.source_setter = weak_partial(set_property_value, self.source)
        self.source_getter = weak_partial(get_property_value, self.source)

    @property
    def property_name(self) -> str:
        return self.__property_name


class PropertyAttributeBinding(Binding):
    """Two way binding from an attribute within a source property object to a target.

    Observes property changed event on a source and if the event matches the
    property name, calls the functions assigned to target_setter field.

    Source must support property_changed_event with the signature:
        property_changed(property_name: str) -> None

    Source must also support get/set attribute for the given property_name and it
    must return/take an object with an attribute matching attribute_name.

    Client should set the target_setter function to a callable with the signature:
        target_setter(value: Any) -> None

    The owner should call close on this object.
    """

    def __init__(self, source: Observable.Observable, property_name: str, attribute_name: str, *,
                 converter: typing.Optional[Converter.ConverterLike[typing.Any, typing.Any]] = None,
                 fallback: typing.Optional[typing.Any] = None,
                 update_attribute_fn: typing.Optional[typing.Callable[[typing.Any, str, typing.Any], typing.Any]] = None) -> None:
        super().__init__(source, converter=converter, fallback=fallback)
        self.__property_name = property_name
        self.__attribute_name = attribute_name

        # thread safe
        def property_changed(binding: typing.Optional[PropertyAttributeBinding], property_name_: str) -> None:
            if binding and property_name_ == property_name:
                # perform on the main thread
                value = getattr(source, property_name)
                if value is not None and hasattr(value, attribute_name):
                    binding.update_target(getattr(value, attribute_name))
                else:
                    binding.update_target_direct(binding.fallback)

        self.__property_changed_listener = source.property_changed_event.listen(weak_partial(property_changed, self))

        def source_setter(source: typing.Any, value: typing.Any) -> None:
            source_value = getattr(source, property_name) if source else None
            if callable(update_attribute_fn):
                source_value = update_attribute_fn(source_value, attribute_name, value)
            else:
                setattr(source_value, attribute_name, value)
            setattr(source, property_name, source_value)

        def source_getter(source: typing.Any) -> typing.Any:
            source_value = getattr(source, property_name) if source else None
            return getattr(source_value, attribute_name) if source_value is not None and hasattr(source_value, attribute_name) else None

        # configure setting/getter, being careful not to hold references to self
        self.source_setter = weak_partial(source_setter, self.source)
        self.source_getter = weak_partial(source_getter, self.source)


class TuplePropertyBinding(Binding):
    """Two way binding from an element within a source property tuple to a target.

    Observes property changed event on a source and if the event matches the
    property name, calls the functions assigned to target_setter field.

    Source must support property_changed_event with the signature:
        property_changed(property_name: str) -> None

    Source must also support get/set attribute for the given property_name and it
    must return/take a tuple.

    Client should set the target_setter function to a callable with the signature:
        target_setter(value: Any) -> None

    The owner should call close on this object.
    """

    def __init__(self, source: Observable.Observable, property_name: str, tuple_index: int, *,
                 converter: typing.Optional[Converter.ConverterLike[typing.Any, typing.Any]] = None,
                 fallback: typing.Optional[typing.Any] = None) -> None:
        super().__init__(source, converter=converter, fallback=fallback)
        self.__property_name = property_name

        # thread safe
        def property_changed(binding: TuplePropertyBinding, property_name_: str) -> None:
            if property_name_ == property_name:
                # perform on the main thread
                value = getattr(source, property_name)
                if value is not None and tuple_index < len(value):
                    binding.update_target(value[tuple_index])
                else:
                    binding.update_target_direct(binding.fallback)

        self.__property_changed_listener = source.property_changed_event.listen(weak_partial(property_changed, self))

        def source_setter(source: typing.Any, value: typing.Any) -> None:
            source_tuple = getattr(source, property_name)
            tuple_as_list = list(source_tuple) if source_tuple is not None else list()
            while len(tuple_as_list) <= tuple_index:
                tuple_as_list.append(None)
            tuple_as_list[tuple_index] = value
            setattr(source, property_name, tuple(tuple_as_list))

        def source_getter(source: typing.Any) -> typing.Any:
            tuple_value = getattr(source, property_name)
            return tuple_value[tuple_index] if tuple_value is not None and tuple_index < len(tuple_value) else None

        self.source_setter = weak_partial(source_setter, self.source)
        self.source_getter = weak_partial(source_getter, self.source)
