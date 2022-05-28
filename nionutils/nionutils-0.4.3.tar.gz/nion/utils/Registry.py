"""
A registry for objects by component type.

A registry is used to look up objects by their name (component type).

It is useful when an object used by an application is determined at run time. In that case it insulates the application
from having to know the specific object being used.

It is also useful when more than one object can be registered as a specific component type. In that case, the
application can ask for all objects registered of a specific type.
"""

# standard libraries
import typing

# local libraries
from . import Event

# third party libraries
# None


class Singleton(type):
    def __init__(cls, name: str, bases: typing.Tuple[typing.Type[typing.Any], ...], d: typing.Dict[str, typing.Any]) -> None:
        super(Singleton, cls).__init__(name, bases, d)
        cls.instance: typing.Any = None

    def __call__(cls, *args: typing.Any, **kw: typing.Any) -> typing.Any:
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


_ComponentType = typing.Any


class ComponentManager(metaclass=Singleton):
    """The ComponentManager is a Singleton that implements the registry."""
    def __init__(self) -> None:
        self.__component_types: typing.Dict[_ComponentType, typing.Set[str]] = dict()
        self.__components_by_type: typing.Dict[str, typing.Set[_ComponentType]] = dict()
        self.component_registered_event = Event.Event()
        self.component_unregistered_event = Event.Event()

    @property
    def _component_types(self) -> typing.Mapping[_ComponentType, typing.Set[str]]:
        return self.__component_types

    @property
    def _components_by_type(self) -> typing.Mapping[str, typing.Set[_ComponentType]]:
        return self.__components_by_type

    def get_components_by_type(self, component_type: str) -> typing.Set[_ComponentType]:
        return set(self.__components_by_type.get(component_type, set()))

    def register(self, component: _ComponentType, component_types: typing.Set[str]) -> None:
        for component_type in component_types:
            assert component not in self.__components_by_type.get(component_type, set())
        for component_type in component_types:
            component_set = self.__components_by_type.setdefault(component_type, set())
            component_set.add(component)
        self.__component_types.setdefault(component, set()).update(component_types)
        self.component_registered_event.fire(component, component_types)

    def unregister(self, component: _ComponentType, component_types: typing.Optional[typing.Set[str]] = None) -> None:
        actual_component_types = component_types if component_types is not None else self.__component_types.get(component, set())
        for component_type in actual_component_types:
            assert component in self.__components_by_type.get(component_type, set())
        for component_type in actual_component_types:
            self.__components_by_type.get(component_type, set()).remove(component)
        self.__component_types[component].difference_update(actual_component_types)
        if len(self.__component_types[component]) == 0:
            self.__component_types.pop(component)
        self.component_unregistered_event.fire(component, actual_component_types)


def get_components_by_type(component_type: str) -> typing.Set[typing.Any]:
    """Returns set of components matching component_type."""
    return ComponentManager().get_components_by_type(component_type)


def get_component(component_type: str) -> typing.Optional[typing.Any]:
    """Returns a single component matching component type.

    If there are multiple components matching, sorts by priority (if available) and then arbitrary.

    Priority range is 0 (low) to 100 (high). Default priority is 50.
    """
    components = get_components_by_type(component_type)

    def attrgetter(attrname: str, default: typing.Optional[int] = None) -> typing.Callable[[typing.Any], int]:
        def inside(obj: typing.Any) -> int:
            return int(typing.cast(int, getattr(obj, attrname, default)))

        return inside

    sorted_components = sorted(components, key=attrgetter("priority", 50), reverse=True)

    if len(sorted_components) > 0:
        return tuple(sorted_components)[0]

    return None

def register_component(component: _ComponentType, component_types: typing.Set[str]) -> None:
    """Register a component and associated it with the set of types. This will trigger a component_registered_event."""
    # if component_types.intersection({"hardware_source_manager", "stem_controller", "hardware_source", "scan_hardware_source", "scan_device", "document_model"}):
    #     print(f">> REGISTER {component} {component_types}")
    # if component_types.intersection({"stem_controller"}):
    #     print(f">> REGISTER {component} {component_types}")
    #     import traceback
    #     traceback.print_stack()
    ComponentManager().register(component, component_types)


def unregister_component(component: _ComponentType, component_types: typing.Optional[typing.Set[str]] = None) -> None:
    """Unregister a component. This will trigger a component_unregistered_event. The component must have been previously registered."""
    # if component_types.intersection({"hardware_source_manager", "stem_controller", "hardware_source", "scan_hardware_source", "scan_device", "document_model"}):
    #     print(f">> UNREGISTER {component} {component_types}")
    ComponentManager().unregister(component, component_types)


def listen_component_registered_event(listener_fn: typing.Callable[[_ComponentType, typing.Set[str]], None]) -> Event.EventListener:
    """Add a listener for the component registered event."""
    return ComponentManager().component_registered_event.listen(listener_fn)


def listen_component_unregistered_event(listener_fn: typing.Callable[[_ComponentType, typing.Set[str]], None]) -> Event.EventListener:
    """Add a listener for the component unregistered event."""
    return ComponentManager().component_unregistered_event.listen(listener_fn)


def fire_existing_component_registered_events(component_type: str) -> None:
    for component in get_components_by_type(component_type):
        ComponentManager().component_registered_event.fire(component, {component_type})
