import functools
from typing import List, Callable, Any, Iterable, TypeVar, Tuple, Dict, cast, Iterator

ReturnType = TypeVar('ReturnType')
F = TypeVar('F', bound=Callable[...,ReturnType])
T = TypeVar('T')
T2 = TypeVar('T2')

def assign(func: Callable[[], T]) -> T: return func()
def assign_list(func:Callable[..., Iterator[T]]) -> List[T]: return list(func()) # TODO: prefer `@assign @list_from_iter`, which also allows cacheing
def assign_dict(func:Callable[..., Iterator[Tuple[T,T2]]]) -> Dict[T,T2]: return dict(func())

def only_once(func: F) -> F:
    already_ran = [False]
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not already_ran[0]:
            already_ran[0] = True
            return func(*args, **kwargs)
    return cast(F, wrapper)

# TODO: this isn't checking that their args/kwargs are the same.
def list_from_iter(func: Callable[..., Iterable[T]]) -> Callable[..., List[T]]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))
    return cast(Callable[..., List[T]], wrapper)

def dict_from_iter(func: Callable[..., Iterable[Tuple[T, T2]]]) -> Callable[..., Dict[T, T2]]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return dict(func(*args, **kwargs))
    return cast(Callable[..., Dict[T,T2]], wrapper)

# Too complex to typecheck
def apply_to_result(*result_wrapper_funcs):
    def wrap(func):
        @functools.wraps(func)
        def f(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            for result_wrapper_func in result_wrapper_funcs:
                result = result_wrapper_func(result)
            return result
        return f
    return wrap


def show(f:F) -> F:
    @functools.wraps(f)
    def wrapper(*args:object, **kwargs:object):
        ret: Any = f(*args, **kwargs)
        params: List[str] = []
        for arg in args: params.append(repr(arg))
        for k,v in kwargs.items(): params.append(f'{k}={repr(v)}')
        print(f'{f.__name__}({", ".join(params)}) = {ret}')
        return ret
    return cast(F, wrapper)
