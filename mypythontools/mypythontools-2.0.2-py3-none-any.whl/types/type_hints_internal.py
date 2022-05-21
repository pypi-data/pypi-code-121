"""Module with functions for 'type_hints' subpackage."""

from __future__ import annotations

# Import can be used in eval
from typing import (
    Any,
    Callable,
    Union,
    List,
    Dict,
    Tuple,
    Sequence,
    Iterable,
)  # pylint: disable=unused-import

from typing_extensions import get_type_hints


def get_return_type_hints(func: Callable) -> Any:
    """Return function return types.

    This is because `get_type_hints` result in error for some types in older
    versions of python and also that `__annotations__` contains only string, not types.

    Note:
        Sometimes it may use eval as literal_eval cannot use users globals so types like pd.DataFrame would
        fail. !!! Therefore do not use it for evaluating types of users input for sake of security !!!

    Args:
        func (Callable): Function with type hints.

    Returns:
        Any: Type of return. E.g. <class 'tuple'> or typing_extensions.Literal['int', 'float'].

    Example:
        >>> # You can use Union as well as Literal
        >>> def union_return() -> int | float:
        ...     return 1
        >>> inferred_type = get_return_type_hints(union_return)
        >>> 'int' in str(inferred_type) and 'float' in str(inferred_type)
        True
        >>> def literal_return() -> Literal[1, 2, 3]:
        ...     return 1
        >>> inferred_type = get_return_type_hints(literal_return)
        >>> 'Literal' in str(inferred_type)
        True
    """
    if isinstance(func, staticmethod):
        func = func.__func__

    try:
        types = get_type_hints(func).get("return")
    except Exception:
        types = func.__annotations__.get("return")

    if isinstance(types, str) and "Union" in types:
        types = eval(types, func.__globals__)

    # If Union operator |, e.g. int | str - get_type_hints() result in TypeError
    # Convert it to Union
    elif isinstance(types, str) and "|" in types:
        str_types = [i.strip() for i in types.split("|")]
        for i, j in enumerate(str_types):
            for k in ["list", "dict", "tuple"]:
                if k in j:
                    str_types[i] = j.replace(k, k.capitalize())
        try:
            evaluated_types = [eval(i, {**globals(), **func.__globals__}) for i in str_types]
        except Exception:
            raise RuntimeError("Evaluating of function return type failed. Try it on python 3.9+.")

        types = Union[evaluated_types[0], evaluated_types[1]]  # type: ignore

        if len(evaluated_types) > 2:
            for i in evaluated_types[2:]:
                types = Union[types, i]

    return types
