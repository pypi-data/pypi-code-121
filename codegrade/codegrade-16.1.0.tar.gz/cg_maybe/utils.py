"""This module contains various utils for working with ``Maybe``s.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import typing as t

from ._just import Just
from ._maybe import Maybe
from ._nothing import Nothing
from ._type_helpers import Literal

_S = t.TypeVar('_S')
_T = t.TypeVar('_T')


def merge2(maybe_s: Maybe[_S], maybe_t: Maybe[_T]) -> Maybe[t.Tuple[_S, _T]]:
    """Merge two maybes together in a tuple if both just.

    >>> from . import Just, Nothing
    >>> merge2(Just(5), Just(6))
    Just((5, 6))
    >>> merge2(Nothing, Just(6))
    Nothing
    >>> merge2(Just(6), Nothing)
    Nothing
    """
    return maybe_s.chain(lambda s: maybe_t.map(lambda t: (s, t)))


def from_nullable(val: t.Optional[_T]) -> Maybe[_T]:
    """Covert a nullable to a maybe.

    >>> from_nullable(5)
    Just(5)
    >>> from_nullable(None)
    Nothing
    """
    if val is None:
        return Nothing
    return Just(val)


def maybe_from_nullable(val: t.Union[None, _T, Maybe[_T]]) -> Maybe[_T]:
    """Convert a nullalbe to a maybe if it isn't already a maybe.

    >>> maybe_from_nullable(Just(5))
    Just(5)
    >>> maybe_from_nullable(5)
    Just(5)
    >>> maybe_from_nullable(None)
    Nothing
    >>> maybe_from_nullable(Nothing)
    Nothing
    """
    if isinstance(val, Just):
        return val
    elif Nothing.is_nothing_instance(val):
        return val  # type: ignore
    return from_nullable(val)  # type: ignore


def from_bool(val: bool) -> Maybe[Literal[True]]:
    """Convert a boolean to a maybe.

    >>> from_bool(True)
    Just(True)
    >>> from_bool(False)
    Nothing
    """
    return Just(True) if val else Nothing


def from_predicate(pred: t.Callable[[_T], bool], val: _T) -> Maybe[_T]:
    """Convert a value to a ``Maybe`` using a given predicate.

    >>> pred = lambda x: x == 5
    >>> from_predicate(pred, 6)
    Nothing
    >>> from_predicate(pred, 5)
    Just(5)
    """
    if pred(val):
        return Just(val)
    return Nothing


def of(value: _T) -> Maybe[_T]:  # pylint: disable=invalid-name
    """Construct a ``Just`` from a given value, but annotated as a ``Maybe``.

    This makes it easy to do something like:

    .. code:: python

        if val == my_value:
            res = of(val)
        else:
            res = Nothing
    """
    return Just(value)


def from_map(mapping: t.Mapping[_T, _S], key: _T) -> Maybe[_S]:
    """Maybe get a value from a mapping.

    >>> mapping = {'a': 'b', 'c': 'd'}
    >>> from_map(mapping, 'a')
    Just('b')
    >>> from_map(mapping, 'b')
    Nothing
    """
    if key in mapping:
        return Just(mapping[key])
    return Nothing


def first(maybes: t.Sequence[Maybe[_T]]) -> Maybe[_T]:
    """Return the first ``Just`` in a sequence.

    >>> first([Just(0), Just(1)])
    Just(0)
    >>> first([Nothing, Just(1)])
    Just(1)
    >>> first([Nothing, Nothing])
    Nothing
    """
    for maybe in maybes:
        if maybe.is_just:
            return maybe
    return Nothing


def encase(
    producer: t.Callable[[], _T],
    exceptions: t.Union[t.Type[Exception], t.Tuple[t.Type[Exception], ...]]
) -> Maybe[_T]:
    """Wrap the result of ``producer`` in a ``Just`` if it does not raise an
    exception.

    >>> def make_raiser(exc):
    ...     def raiser():
    ...         raise exc
    ...     return raiser
    >>> encase(make_raiser(ValueError()), ValueError)
    Nothing
    >>> encase(lambda: 5, ValueError)
    Just(5)
    >>> encase(make_raiser(AssertionError()), ValueError)
    Traceback (most recent call last):
    ...
    AssertionError

    :param producer: The function that will return the value to wrap.
    :param exceptions: The exceptions that should be caught and transformed
        into a ``Nothing``.

    :returns: The returned value or ``Nothing``.
    """
    try:
        val = producer()
    except exceptions:
        return Nothing
    else:
        return Just(val)
