from typing import Any, Tuple, Type, TypeVar, Union, overload

T = TypeVar("T")
U = TypeVar("U")


# Overloads are provided for the common case and for the general case separately since python has poor support for
# variadic type variables.


@overload
def validate_type(
    obj: Any, expected_type: Type[T], operation: str, exception_type: Type[Exception]
) -> T:
    ...


@overload
def validate_type(
    obj: Any,
    expected_type: Tuple[Type[T], Type[U]],
    operation: str,
    exception_type: Type[Exception],
) -> Union[T, U]:
    ...


@overload
def validate_type(
    obj: Any,
    expected_type: Tuple[Type[T], ...],
    operation: str,
    exception_type: Type[Exception],
) -> Any:
    ...


def validate_type(
    obj: Any,
    expected_type: Union[Tuple[type, ...], type],
    operation: str,
    exception_type: Type[Exception],
) -> Any:
    operation = operation[0].upper() + operation[1:]
    if not isinstance(obj, expected_type):
        expected_types: Tuple[type, ...]
        if isinstance(expected_type, type):
            expected_types = (expected_type,)
        else:
            expected_types = expected_type
        type_str = " or ".join(t.__name__ for t in expected_types)
        raise exception_type(
            f"{operation} error: Got object of type {type(obj).__name__} and not {type_str}"
        )
    return obj
