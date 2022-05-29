"""Utilities functions and classes


"""
from typing import Any, Callable, Dict, Sequence, Type

import numpy as np

OneVariableFunction = Callable[[Any], Any]


def _raise(e: Exception):
    """Raise an exception.

    This function is useful to enable lambda functions to raise exceptions.

    :param e: exception to raise
    :type e: Exception
    :raises Exception: e
    """
    raise e


def is_unique_sequence(sequence: Sequence) -> bool:
    """Check whether every elements of a sequence are unique.

    :param sequence:
    :return:
    """
    return len(set(sequence)) == len(sequence)


class PolymorphicFunction:
    """This class implements a generic single-argument polymorphic function.

    It keeps a dictionary with all versions of the functions to call
    depending on the argument type. A default function is called if input
    type is uncovered (raising a :class:`TypeError` if not provided).

    :param functions: functions to call as values and argument types as keys
    :param default: default function to call if type not covered

    .. warning:: all functions given must have only one argument
    """

    def __init__(
        self,
        functions: Dict[Type, OneVariableFunction] = None,
        default: OneVariableFunction = None,
    ):
        """Constructor method"""
        self._functions = {}
        if functions is not None:
            self._functions.update(functions)
        if default is None:
            self._default = lambda x: _raise(
                TypeError(f"type {type(x)} " "unrecognized")
            )
        else:
            self._default = default

    def _types(self) -> Sequence[Type]:
        """Return set of all covered argument types"""
        return list(self._functions.keys())

    def __call__(self, x: Any) -> Any:
        """Call the function matching argument type.

        :param x:
        :raises TypeError:
            if `default` function not provided and type(`x`) unknown
        :return:
        """
        if type(x) in self._functions:
            return self._functions[type(x)](x)
        return self._default(x)


class VectorizedFunction(PolymorphicFunction):
    """This class implements a vectorized function.

    This class creates multiple version of the input function for typical
    sequence types:

    * :class:`list`
    * :class:`dict`
    * :class:`np.ndarray`

    If `functions` is provided, with some of the typical sequence types
    covered, they are used instead of the automatically-built ones.

    The input function `function` is the default function to apply
    to single valued arguments.


    :param functions: functions to call as values and argument types as keys
    :param function: function to call for single-valued argument
    """

    def __init__(
        self,
        functions: Dict[Type, OneVariableFunction] = None,
        function: OneVariableFunction = None,
    ):
        """Constructor method"""
        PolymorphicFunction.__init__(self, functions, default=function)
        if list not in self._functions:
            self._functions[list] = lambda x: [self.__call__(xx) for xx in x]
        if dict not in self._functions:
            self._functions[dict] = lambda x: {
                k: self.__call__(xx) for k, xx in x.items()
            }
        if np.ndarray not in self._functions:
            self._functions[np.ndarray] = lambda x: np.array(
                self.__call__(x.tolist())
            )


class FunctionConfigurator:
    """
    .. todo::
        class that gathers functions and their default arguments as options
    """

    pass
