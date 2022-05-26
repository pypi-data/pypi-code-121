"""
Various small helper functions.
"""
import os
import inspect
import numpy
from numbers import Number
from typing import Any, Callable, Iterable, Type, Union, Tuple
from collections.abc import Collection


def is_numerical(value: Any) -> bool:
    """Test if a value is numerical based on its type.

    Currently type considered as numerical are:

    - int; but not bool
    - float; including numpy.inf and numpy.nan
    - complex
    - numpy.ndarray of dtype numpy.number
    - Collection convertible in a numpy array of dtype derived from numpy.number

    Parameters
    ----------
    value : Any
        Value to test

    Returns
    -------
    bool
        Is the value numerical type?
    """
    if isinstance(value, (bool, str)):
        # to avoid bool being considered as int
        # and because str is Collection
        return False
    if isinstance(value, Number):
        return True
    if isinstance(value, numpy.ndarray):
        return numpy.issubdtype(value.dtype, numpy.number)
    if isinstance(value, Collection) and len(value) > 0:
        return all(is_numerical(v) for v in value)
    return False


def is_number(value: Any) -> bool:
    """Test if a value is a Number or a 0d numerical array

    Currently type considered as numerical are:

    - int; but not bool
    - float; including numpy.inf and numpy.nan
    - complex
    - numpy.ndarray of dtype numpy.number and ndim == 0

    Parameters
    ----------
    value : Any
        Value to test

    Returns
    -------
    bool
        Is the value numerical type?
    """
    if isinstance(value, bool):
        # to avoid bool being considered as int
        return False
    if isinstance(value, Number):
        return True
    if isinstance(value, numpy.ndarray) and value.ndim == 0:
        return numpy.issubdtype(value.dtype, numpy.number)
    return False


def get_typename(dtype: Union[Type, Tuple[Type]], multiformat="({})") -> str:
        if inspect.isclass(dtype):
            return dtype.__qualname__
        return multiformat.format(", ".join(set(t.__qualname__ for t in dtype)))


def check_arg(
    arg: Any,
    argname: str,
    dtype: Union[Type, Iterable[Type]],
    value_ok: Callable[[Any], bool] = None,
    stack_shift: int = 0,
):
    """
    Utility function for argument type and value validation.
    Raises a TypeError exception if type(arg) is not in type list given by 'dtype'.
    Raises a ValueError exception if value_ok(arg) is False, where 'value_ok' is a
    boolean function defining a validity criterion.

    For example:
    >>> check_arg(-0.12, 'my_var', float)
    does not raise any exception, as -0.12 is a float

    >>> check_arg(-0.12, 'my_var', (int, str))
    raises TypeError, as first argument is neither an int, not a str

    >>> check_arg(-0.12, 'my_var', float, value_ok = lambda x: x > 0)
    raises ValueError, as first argument is not strictly positive
    """
    def get_caller():
        level = 3 + max(0, stack_shift)
        stack = inspect.stack()
        return stack[level] if len(stack) > level else stack[-1]

    def get_context(caller):
        try:
            context = caller.code_context[0]
        except:
            context = ""
        return os.path.basename(caller.filename), caller.lineno, context

    # Check type
    if not isinstance(arg, dtype):
        valid = get_typename(dtype, multiformat="one of ({})")
        caller = get_caller()
        raise TypeError("argument '{}' should be {}; got {} {!r}\nIn {}, line #{}: \n{}".format(
            argname, valid, type(arg).__qualname__, arg, *get_context(caller)))
    # Check value
    if isinstance(value_ok, Callable) and not value_ok(arg):
        caller = get_caller()
        raise ValueError("argument {!r} was given invalid value {!r}\nIn {}, line #{}: \n{}".format(
            argname, arg, *get_context(caller)))
