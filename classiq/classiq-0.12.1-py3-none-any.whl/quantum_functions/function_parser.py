import sys
from types import FunctionType, MethodType
from typing import Any, Callable, Tuple, _GenericAlias  # type: ignore[attr-defined]

if sys.version_info >= (3, 9):
    from types import GenericAlias
else:
    GenericAlias = _GenericAlias


from classiq.exceptions import ClassiqQFuncError


class FunctionParser:
    def __init__(self, func: FunctionType):
        self._func = func

    @staticmethod
    def _extract_function_output_by_execution(func: FunctionType) -> Any:
        # Todo: Parse the type (annotations) of the arguments, and remove only those inheriting from QReg
        if func.__code__.co_kwonlyargcount:
            raise ClassiqQFuncError("kw only args are not supported")

        arg_count = func.__code__.co_argcount - ("self" in func.__code__.co_varnames)
        nones = [None] * arg_count
        return func(*nones)

    def extract_function_output(self) -> Any:
        output = self._extract_function_output_by_execution(func=self._func)

        self._validate_function_output(output)

        return output

    @staticmethod
    def _validate_function_output(output: Any) -> None:
        # Todo: validate QASM

        if type(output) is not str:
            raise ClassiqQFuncError(
                "Invalid output. Please return a string of OpenQASM2.0."
            )


def _convert_class_to_function(cls: type) -> Tuple[FunctionType, str]:
    # Create instance
    try:
        inst = cls()
    except TypeError as exc:
        raise ClassiqQFuncError("Unable to initialize class") from exc

    return inst.__call__, inst.__class__.__name__


def convert_callable_to_function(func: Callable) -> Tuple[FunctionType, str]:
    # There's a story to be told here:
    # Functions vs Methods.
    # It's a centuries old fight, which won't end soon..
    # Functions, being functions, always have a way of telling us about their functionality
    #   This is done using `func.__code__`
    # Methods, being the heigher form of functions, are too proud to have a `__code__` attribute.
    #   Thus, `"__code__" in method` is false
    #   However, `method.__code__` exists
    #   Since it is inherited from the class that initialized the instance who owns the method
    # Thus, we reach the important conclusion:
    # Methods are shy functions. They are functions, but they don't like telling us that they're functions.
    if not callable(func):
        raise ClassiqQFuncError("Invalid callable given.")

    if isinstance(func, (FunctionType, MethodType)):
        return func, func.__name__  # type: ignore[return-value]

    # Assuming `func` is an instance of some class
    return _convert_class_to_function(func)  # type: ignore[arg-type]
