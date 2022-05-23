from typing import Generic, TypeVar
from weakref import WeakKeyDictionary

ValueType = TypeVar("ValueType")


class InstanceProperty(Generic[ValueType]):
    """
    A basic property which simply holds a value for each instance object. As
    instances of classes which use this property are used as the key to a dictionary
    holding the value, the instances must be hashable, and the hash must not rely on
    the property for its hash calculation.
    """
    def __init__(self, default_value: ValueType = None):
        self._cache = WeakKeyDictionary()
        self._default: ValueType = default_value

    def __get__(self, instance, owner) -> ValueType:
        if instance in self._cache:
            return self._cache[instance]

        return self._default

    def __set__(self, instance, value: ValueType):
        self._cache[instance] = value

    def __delete__(self, instance):
        del self._cache[instance]
