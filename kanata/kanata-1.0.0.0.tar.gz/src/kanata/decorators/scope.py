from ..models import InjectableRegistration, InjectableScopeType
from ..utils import get_or_add_attribute
from typing import Callable, Type, TypeVar

T = TypeVar("T")

def scope(scope_type: InjectableScopeType) -> Callable[[Type[T]], Type[T]]:
    """Specifies the scope type of an injectable class.

    :param scope_type: The lifetime scope of the created instances.
    :type scope_type: InjectableScopeType, optional
    :return: A decorator that returns the same class that it decorates.
    :rtype: Callable[[Type[T]], Type[T]]
    """
    def decorator(wrapped_class: Type[T]) -> Type[T]:
        registration = get_or_add_attribute(
            wrapped_class,
            InjectableRegistration.PROPERTY_NAME,
            lambda: InjectableRegistration(wrapped_class))
        registration.scope = scope_type
        return wrapped_class

    return decorator
