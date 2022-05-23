from typing import TypeVar, Dict, Callable, Tuple, Any, NoReturn, Optional, Type

from ..meta import fully_qualified_name

# Generic type variable
T = TypeVar("T")

# The types of the 'cli_repr'/'from_cli_repr' methods
CLI_REPR_METHOD_TYPE = Callable[[T], str]
FROM_CLI_REPR_METHOD_TYPE = Callable[[str], T]


# For use when honarary member methods aren't implemented (yet)
def NOT_IMPLEMENTED(method_name: str) -> Callable[[Any], NoReturn]:
    def method(*args, **kwargs):
        raise NotImplementedError(method_name)

    return method


def type_from_cli_repr(cli_string: str) -> type:
    """
    Imports a class from its CLI representation.
    TODO: Move to meta package

    :param cli_string:  The CLI representation of the class.
    :return:            The class.
    """
    locals_ = dict(locals())
    parts = cli_string.split(".")
    for i in range(len(parts) - 1, 0, -1):
        code = f"from {'.'.join(parts[:i])} import {parts[i]} as result"
        if i != len(parts) - 1:
            code += f"\nresult = result.{'.'.join(parts[i+1:])}"
        try:
            exec(code, globals(), locals_)
        except ImportError:
            pass
        else:
            return locals_["result"]

    raise ImportError(f"Couldn't import class '{cli_string}'")


# Honorary CLI-representable types and their 'cli_repr'/'from_cli_repr' methods
HONORARY_MEMBERS: Dict[Type[T], Tuple[CLI_REPR_METHOD_TYPE[T], FROM_CLI_REPR_METHOD_TYPE[T]]] = {
    int: (repr, int),
    str: (lambda self: self, lambda cli_string: cli_string),
    float: (repr, float)
}


class CLIRepresentable:
    """
    Interface for objects which can represent themselves
    as a value on the command-line.
    """
    def cli_repr(self) -> str:
        """
        Gets the CLI representation of this object.

        :return:        The CLI string.
        """
        raise NotImplementedError(CLIRepresentable.cli_repr.__qualname__)

    @classmethod
    def from_cli_repr(cls: Type[T], cli_string: str) -> T:
        """
        Gets an instance of the type from its CLI representation.

        :param cli_string:  The CLI representation.
        :return:            The instance.
        """
        raise NotImplementedError(CLIRepresentable.from_cli_repr.__qualname__)


def get_cli_repr_functions(cls: Type[T]) -> Optional[Tuple[CLI_REPR_METHOD_TYPE[T], FROM_CLI_REPR_METHOD_TYPE[T]]]:
    """
    Gets the cli_repr/from_cli_repr functions for a given type.

    :param cls:     The type to get the functions for.
    :return:        The pair of functions, or None if none available.
    """
    # See if the type is an honorary member
    if cls in HONORARY_MEMBERS:
        return HONORARY_MEMBERS[cls]

    # If the class inherits from CLIRepresentable, return its cli_repr method
    if issubclass(cls, CLIRepresentable):
        return cls.cli_repr, cls.from_cli_repr

    # If the class is a meta-class (i.e. it's values are classes),
    # then represent it by it's fully-qualified name, and parse
    # it by importing it
    if issubclass(cls, type):
        return fully_qualified_name, type_from_cli_repr

    return None


def get_cli_repr_function(value: T) -> Optional[CLI_REPR_METHOD_TYPE[T]]:
    """
    Gets the function to call to get the CLI representation of a value.

    :param value:   The value to get the cli_repr function for.
    :return:        The cli_repr function, or None if none available.
    """
    # Get the value's type
    cls = type(value)

    # Get the functions for the type
    cli_repr_functions = get_cli_repr_functions(cls)

    # If the functions exist, return the cli_repr function
    if cli_repr_functions is not None:
        return cli_repr_functions[0]

    return None


def get_from_cli_repr_function(cls: Type[T]) -> Optional[CLI_REPR_METHOD_TYPE[T]]:
    """
    Gets the function to call to parse the CLI representation of a value.

    :param cls:     The type to get the from_cli_repr function for.
    :return:        The from_cli_repr function, or None if none available.
    """
    # Get the functions for the type
    cli_repr_functions = get_cli_repr_functions(cls)

    # If the functions exist, return the from_cli_repr function
    if cli_repr_functions is not None:
        return cli_repr_functions[1]

    return None


def is_cli_representable_type(cls: Type[T]) -> bool:
    """
    Checks if the given class is a CLI-representable type.

    :param cls:     The type to check.
    :return:        True if the type is CLI-representable.
    """
    return get_cli_repr_functions(cls) is not None


def is_cli_representable(value: T) -> bool:
    """
    Checks if the given value is CLI-representable.

    :param value:   The value to check.
    :return:        True if the value is CLI-representable.
    """
    return is_cli_representable_type(type(value))


def cli_repr(value: T) -> str:
    """
    Gets the CLI representation of a CLI-representable value.

    :param value:   The value.
    :return:        The CLI string.
    :raises TypeError:  If the type is not CLI-representable.
    """
    # Get the cli_repr function for the value
    cli_repr_function = get_cli_repr_function(value)

    # If it doesn't have a function, it's not CLI-representable
    if cli_repr_function is None:
        raise TypeError(f"Values of type '{type.__name__}' are not CLI-representable")

    return cli_repr_function(value)


def from_cli_repr(cls: Type[T], cli_string: str) -> T:
    """
    Gets a value of a CLI-representable type from its CLI representation.

    :param cls:         The type of value to get.
    :param cli_string:  The CLI representation.
    :return:            The value.
    :raises TypeError:  If the type is not CLI-representable.
    """
    # Get the from_cli_repr function for the type
    from_cli_repr_function = get_from_cli_repr_function(cls)

    # If it doesn't have a function, it's not CLI-representable
    if from_cli_repr_function is None:
        raise TypeError(f"'{cls.__qualname__}' is not a CLI-representable type")

    return from_cli_repr_function(cli_string)
