import inspect
from typing import Optional, Dict, Any

from .typing import AnyCallable


def has_been_overridden(function, obj) -> bool:
    """
    Determines if the given base-class function has been overridden
    by the given object.

    :param function:    A class method (can be bound).
    :param obj:         The object to test for overriding.
    :return:            True if the given object overrides the base-class method,
                        False if not.
    """
    # Unbind the function
    function = unbind(function)

    # Abort if not a function
    if not inspect.isfunction(function):
        raise ValueError(f"{function} is not a function")

    # Get the base class from the function
    function_base_class = get_class_from_function(function)

    # Make sure the function is a class function
    if function_base_class is None:
        raise ValueError("Given function is not a class-function")

    # Get the class of the object
    object_base_class = obj if inspect.isclass(obj) else type(obj)

    # Make sure the object class derives from the base class
    if not issubclass(object_base_class, function_base_class):
        raise ValueError("Given object does not inherit from function base-class")

    # Get the function of the same name from the object base class
    object_base_class_function = unbind(getattr(object_base_class, function.__name__))

    return object_base_class_function is not function


def get_class_from_function(function) -> Optional[type]:
    """
    Gets the class that the given function is defined in.

    :param function:    The function to get the class from.
    :return:            The class, or None if the function is not
                        a class function.
    """
    # If given a bound method, unbind it
    function = unbind(function)

    # Abort if not a function
    if not inspect.isfunction(function):
        return None

    # Get the dotted name of the function
    qual_name = function.__qualname__

    # Split on the dots
    name_parts = qual_name.split(".")

    # If there is only one part, it's not a class function
    if len(name_parts) < 2:
        return None

    # Get the part that should be a class name
    class_name = name_parts[-2]

    # The class should be in the function's global dict
    if class_name not in function.__globals__:
        return None

    # Get the class
    cls = function.__globals__[class_name]

    # Make sure it actually is a class
    if not inspect.isclass(cls):
        return None

    return cls


def is_class_function(function) -> bool:
    """
    Checks if the given function is defined in a class.

    :param function:    The function to check.
    :return:            True if the function is a class function,
                        False if not.
    """
    return get_class_from_function(function) is not None


def unbind(method):
    """
    Unbinds a bound method.

    :param method:  The method to unbind.
    :return:        The unbound function of the given method,
                    or the method itself if it's not bound.
    """
    if not inspect.ismethod(method):
        return method

    return method.__func__


def does_not_raise(func: AnyCallable, *args, **kwargs) -> bool:
    """
    Calls the given function with the given arguments, and reports
    whether it raised an exception or not.

    :param func:    The function to call.
    :param args:    The positional arguments to the function.
    :param kwargs:  The keyword arguments to the function.
    :return:        True if the call completed without raising an exception,
                    False if an exception was raised.
    """
    try:
        func(*args, **kwargs)
    except Exception:
        return False

    return True


def all_as_kwargs(function: AnyCallable, *args, **kwargs) -> Dict[str, Any]:
    """
    Gets a dictionary of the arguments that would be passed to the
    given function by name, resolving positional arguments into
    keyword arguments.

    :param function:    The function.
    :param args:        The positional arguments to the function.
    :param kwargs:      The keyword arguments to the function.
    :return:            All arguments to the function, keyed by parameter name.
                        Includes defaults.
    """
    # Get the function's signature
    signature = inspect.signature(function)

    # Apply the given arguments and defaults
    binding: inspect.BoundArguments = signature.bind(*args, **kwargs)
    binding.apply_defaults()

    return dict(binding.arguments)
