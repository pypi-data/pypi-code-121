from typing import Tuple, Dict, Any, Set

from .constants import ABSTRACT_METHOD_ATTRIBUTE, ABSTRACT_CLASS_ATTRIBUTE


def get_abstract_methods(bases: Tuple, namespace: Dict[str, Any]):
    """
    Gets the names of the abstract methods that will result from
    a class created with the given base-class set and namespace.

    :param bases:       The base-class set.
    :param namespace:   The namespace.
    :return:            The set of abstract method names.
    """
    abstract_methods = set()

    for base in bases:
        abstract_methods.update(abstract_methods_of(base))

    for name, value in namespace.items():
        if is_abstract_function(value):
            abstract_methods.add(name)
        elif name in abstract_methods:
            abstract_methods.remove(name)

    return abstract_methods


def will_be_abstract(bases: Tuple, namespace: Dict[str, Any]):
    """
    Determines if a class made with the given set of base-classes
    and namespace will be abstract or concrete.

    :param bases:       The set of base classes.
    :param namespace:   The namespace of the new class.
    :return:            True if the newly-created class will be abstract,
                        False if it will be concrete.
    """
    return len(get_abstract_methods(bases, namespace)) > 0


def is_abstract_function(func):
    """
    Whether the given function is abstract in its class.

    :param func:    The function to check.
    :return:        True if the function is abstract,
                    False if not.
    """
    return getattr(func, ABSTRACT_METHOD_ATTRIBUTE, False)


def abstract_methods_of(cls) -> Set[str]:
    """
    Gets the abstract methods of a class.

    :param cls:     The class to get the abstract methods from.
    :return:
    """
    return getattr(cls, ABSTRACT_CLASS_ATTRIBUTE, set())


def is_abstract_class(cls) -> bool:
    """
    Checks if the given class is abstract.

    :param cls:     The class to check.
    :return:        True if the given class is abstract,
                    False if not.
    """
    return len(abstract_methods_of(cls)) > 0
