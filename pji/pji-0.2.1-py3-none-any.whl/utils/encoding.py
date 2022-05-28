from typing import Union, Callable, TypeVar

from hbutils.encoding import auto_decode


def _auto_encode(s: str) -> bytes:
    return s.encode()


_T = TypeVar('_T')


def auto_encode_support(func: Callable[[Union[bytes, bytearray], ], _T]) \
        -> Callable[[Union[bytes, bytearray, str], ], _T]:
    def _func(data: Union[bytes, bytearray, str]) -> _T:
        if isinstance(data, (bytes, bytearray)):
            return func(data)
        elif isinstance(data, str):
            return func(_auto_encode(data))
        else:
            raise TypeError("Unknown type to encode support - {cls}".format(cls=type(data).__class__))

    return _func


def auto_decode_support(func: Callable[..., Union[bytes, bytearray, str]]) -> Callable[..., str]:
    def _func(*args, **kwargs) -> str:
        result = func(*args, **kwargs)
        if isinstance(result, (bytes, bytearray)):
            return auto_decode(result)
        elif isinstance(result, str):
            return result
        else:
            raise TypeError("Unknown type to decode support - {cls}".format(cls=type(result).__class__))

    return _func
