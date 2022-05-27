""" This module contains code to mark flask routes as public API methods.
"""
import typing as t
import inspect
import functools
import dataclasses

from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import Literal
from ._mapping import BaseFixedMapping

__all__ = ('swaggerize', )

_CallableT = t.TypeVar('_CallableT', bound=t.Callable)


@dataclasses.dataclass(frozen=True)
class _SwaggerFunc:
    if _USE_SLOTS:
        __slots__ = (
            'operation_name',
            'no_data',
            'func',
            'query_parser',
        )
    operation_name: str
    no_data: bool
    func: t.Callable
    query_parser: t.Optional['BaseFixedMapping']


_SWAGGER_FUNCS: t.Dict[str, t.Dict[t.Optional[str], _SwaggerFunc]] = {}

_NameT = t.Union[str, t.Mapping[Literal['GET', 'POST', 'PATCH', 'DELETE',
                                        'PUT'], str]]


def swaggerize(
    operation_name: _NameT,
    *,
    no_data: bool = False,
) -> t.Callable[[_CallableT], _CallableT]:
    """Mark this function as a function that should be included in the open api
    docs.

    :param operation_name: The name that the route should have in the client
        API libraries.
    :param no_data: If this is a route that can take input data (``PATCH``,
        ``PUT``, ``POST``), but doesn't you should pass ``True`` here. If you
        don't the function should contain a call to ``from_flask`` as the first
        statement of the function.
    """
    def __wrapper(func: _CallableT) -> _CallableT:
        if func.__name__ in _SWAGGER_FUNCS:  # pragma: no cover
            raise AssertionError(
                'The function {} was already registered.'.format(
                    func.__name__
                )
            )
        wrapped_func = process_query_params(func)
        query_parser = wrapped_func.__cg_query_parser__  # type: ignore

        func_dict = _SWAGGER_FUNCS.setdefault(func.__name__, {})
        if isinstance(operation_name, str):
            func_dict[None] = _SwaggerFunc(
                operation_name=operation_name,
                no_data=no_data,
                func=func,
                query_parser=query_parser
            )
        else:
            for method, name in operation_name.items():
                func_dict[method] = _SwaggerFunc(
                    operation_name=name,
                    no_data=no_data,
                    func=func,
                    query_parser=query_parser
                )

        return wrapped_func

    return __wrapper


def process_query_params(func: _CallableT) -> _CallableT:
    """Process query parameters of the given function.

    All parameters prefixed with ``query_`` are retrieved and parsed from the
    query parameters.
    """
    query_params = [
        inspect.Parameter(
            name=value.name[len('query_'):],
            kind=value.kind,
            default=value.default,
            annotation=value.annotation,
        ) for value in inspect.signature(func).parameters.values()
        if value.name.startswith('query_')
    ]
    if not query_params:
        query_parser = None
    else:
        query_parser = BaseFixedMapping.from_function_parameters_list(
            query_params,
            from_query=True,
        )

    func.__cg_query_parser__ = query_parser  # type: ignore
    if query_parser is None:
        return func

    # We need flask in ``__inner``, but importing it here is faster

    import flask  # pylint: disable=import-outside-toplevel

    # Mypy know that this is never ``None`` so we can use it without check.
    _parser = query_parser

    @functools.wraps(func)
    def __inner(*args: t.Any, **kwargs: t.Any) -> t.Any:
        for key, value in _parser.try_parse_and_log(
            flask.request.args,
            msg='Query parameters processed',
        ).items():
            kwargs[f'query_{key}'] = value
        return func(*args, **kwargs)

    return t.cast(_CallableT, __inner)
