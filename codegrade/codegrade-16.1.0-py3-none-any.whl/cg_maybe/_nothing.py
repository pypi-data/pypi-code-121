"""This module implements the ``Nothing`` part of the ``Maybe`` monad.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

from ._type_helpers import Literal
from ._type_helpers import SupportsLessThan as _SupportsLessThan
from ._type_helpers import SupportsGreaterOrEqual as _SupportsGreaterOrEqual

if t.TYPE_CHECKING or os.getenv('CG_GENERATING_DOCS'):  # pragma: no cover
    # pylint: disable=unused-import,invalid-name
    import cg_maybe

_T = t.TypeVar('_T', covariant=True)
_TT = t.TypeVar('_TT', covariant=True)
_Y = t.TypeVar('_Y')
_Z = t.TypeVar('_Z')


class _Nothing(t.Generic[_T]):
    """Singleton class to represent the ``Nothing`` part of a ``Maybe``.
    """
    __slots__ = ()

    is_just: Literal[False] = False
    is_nothing: Literal[True] = True

    @classmethod
    def _set_doc(cls) -> None:
        # pylint: disable=import-outside-toplevel
        from ._just import Just
        for attr in dir(cls):
            value = getattr(cls, attr)
            if (
                not attr.startswith('_') and hasattr(Just, attr) and
                not value.__doc__
            ):
                value.__doc__ = getattr(Just, attr).__doc__

    # pylint: disable=no-self-use,missing-function-docstring,unused-argument
    def map(self, mapper: t.Callable[[_T], _TT]) -> '_Nothing[_TT]':
        return Nothing

    def map_or_default(
        self,
        mapper: t.Callable[[_T], _Y],
        default: _Y,
    ) -> _Y:
        return default

    def chain_nullable(
        self, chainer: t.Callable[[_T], t.Optional['_TT']]
    ) -> '_Nothing[_TT]':
        # pylint: disable=import-outside-toplevel
        return Nothing

    def chain(
        self, chainer: t.Callable[[_T], 'cg_maybe._maybe.Maybe[_TT]']
    ) -> '_Nothing[_TT]':
        return Nothing

    def alt(
        self, alternative: 'cg_maybe._maybe.Maybe[_T]'
    ) -> 'cg_maybe._maybe.Maybe[_T]':
        return alternative

    def alt_lazy(
        self, maker: t.Callable[[], 'cg_maybe._maybe.Maybe[_Y]']
    ) -> 'cg_maybe._maybe.Maybe[t.Union[_Y, _T]]':
        return maker()

    def or_default(self, value: _Y) -> _Y:
        return value

    def or_none(self) -> None:
        return None

    def or_default_lazy(self, producer: t.Callable[[], _Y]) -> _Y:
        return producer()

    def unsafe_extract(self) -> _T:
        raise AssertionError('Tried to extract a _Nothing')

    def case_of(
        self,
        *,
        just: t.Callable[[_T], _TT],
        nothing: t.Callable[[], _TT],
    ) -> _TT:
        return nothing()

    def if_just(self, callback: t.Callable[[_T], object]) -> '_Nothing[_T]':
        return self

    def if_nothing(self, callback: t.Callable[[], object]) -> '_Nothing[_T]':
        callback()
        return self

    def try_extract(
        self, make_exception: t.Union[t.Callable[[], Exception], Exception]
    ) -> t.NoReturn:
        if isinstance(make_exception, BaseException):
            raise make_exception
        raise make_exception()

    def __repr__(self) -> str:
        return 'Nothing'

    def __structlog__(self) -> t.Mapping[str, object]:
        return {'type': 'Nothing'}

    @staticmethod
    def is_nothing_check(obj: 'cg_maybe._maybe.Maybe[t.Any]') -> bool:
        """Static method to check if an object is a ``Nothing``.

        >>> from ._just import Just
        >>> Nothing.is_nothing_check(Just(5))
        False
        >>> Nothing.is_nothing_check(Nothing)
        True

        :param obj: The object to check.
        """
        return obj.is_nothing

    @classmethod
    def is_nothing_instance(cls, obj: object) -> bool:
        """Check if the given object is a Nothing object.

        >>> from ._just import Just
        >>> Nothing.is_nothing_instance(5)
        False
        >>> Nothing.is_nothing_instance(Nothing)
        True
        >>> Nothing.is_nothing_instance(Just(5))
        False

        :param obj: The object that will be checked to be an instance of
            ``_Nothing``.
        """
        return obj is Nothing or isinstance(obj, cls)

    def __bool__(self) -> Literal[False]:
        raise Exception('Do not check Nothing for boolean value')

    def attr(self, attr: str) -> object:
        return Nothing

    def join(self: '_Nothing[cg_maybe._maybe.Maybe[_Y]]') -> '_Nothing[_Y]':
        return Nothing

    def filter(self, _pred: t.Callable[[_T], bool]) -> '_Nothing[_T]':
        return self

    def eq(
        self: '_Nothing[_Y]',
        val: _Y,
    ) -> Literal[False]:
        return False

    ne = eq  # pylint: disable=invalid-name

    def lt(  # pylint: disable=invalid-name
        self: '_Nothing[_SupportsLessThan[_T]]',
        val: _SupportsLessThan[_T],
    ) -> Literal[False]:
        return False

    def le(
        self: '_Nothing[_SupportsGreaterOrEqual[_T]]',
        val: _SupportsGreaterOrEqual[_T],
    ) -> Literal[False]:
        return False

    def gt(  # pylint: disable=invalid-name
        self: '_Nothing[_SupportsLessThan[_T]]',
        val: _SupportsLessThan[_T],
    ) -> Literal[False]:
        return False

    def ge(
        self: '_Nothing[_SupportsGreaterOrEqual[_T]]',
        val: _SupportsGreaterOrEqual[_T],
    ) -> Literal[False]:
        return False

    # pylint: enable=no-self-use,missing-function-docstring,unused-argument


Nothing: _Nothing[t.Any] = _Nothing()
