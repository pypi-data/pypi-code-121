from ..models import InjectableRegistration
from ..utils import get_or_add_attribute
from typing import Any, Callable, Type, TypeVar

T = TypeVar("T")

def injectable(contract_type: Type[Any]) -> Callable[[Type[T]], Type[T]]:
    """Marks a class as an injectable.

    :param contract_type: The type of the contract by which an instance of the object is injectable.
    :type contract_type: Type[Any]
    :return: A decorator that returns the same class that it decorates.
    :rtype: Callable[[Type[T]], Type[T]]
    """

    def decorator(wrapped_class: Type[T]) -> Type[T]:
        registration = get_or_add_attribute(
            wrapped_class,
            InjectableRegistration.PROPERTY_NAME,
            lambda: InjectableRegistration(wrapped_class))
        registration.contract_types.add(contract_type)
        return wrapped_class

    return decorator
