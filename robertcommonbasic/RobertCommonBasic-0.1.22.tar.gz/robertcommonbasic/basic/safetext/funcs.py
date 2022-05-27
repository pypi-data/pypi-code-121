from typing import TypeVar, Optional, Callable


T = TypeVar('T')


def none_if(value: Optional[T],
            default_value: Optional[T] = None,
            converter: Callable = None) -> Optional[T]:
    if converter is None:
        return default_value if value is None else value
    else:
        return default_value if value is None else converter(value)