"""
Module for working with meta-data on objects in an iterable.
"""
from typing import Any, Iterable, Iterator

from .._typing import T
from ._ConstantIterator import ConstantIterator


def with_metadata(iterable: Iterable[T], key: str, value: Any) -> Iterator[T]:
    """
    Adds meta-data to each object in an iterator.

    :param iterable:    The object iterable.
    :param key:         The meta-data key.
    :param value:       The meta-data value.
    :return:            An iterator over the objects with added meta-data.
    """
    return zip_metadata(iterable, ConstantIterator[str](key), ConstantIterator[str](value))


def zip_metadata(iterable: Iterable[T], keys: Iterable[str], values: Iterable[Any]) -> Iterator[T]:
    """
    Adds meta-data to each object in an iterator.

    :param iterable:    The object iterable.
    :param keys:        The meta-data key iterable.
    :param values:      The meta-data iterable.
    :return:            An iterator over the objects with added meta-data.
    """
    from ..meta import with_metadata
    return (with_metadata(obj, key, value) for obj, key, value in zip(iterable, keys, values))


def get_metadata(iterable: Iterable, key: str) -> Iterator:
    """
    Iterates over the meta-data attached to the objects in
    the given iterable under the given key.

    :param iterable:    The object iterable.
    :param key:         The meta-data key.
    :return:            An iterator over the meta-data.
    """
    return unzip_metadata(iterable, ConstantIterator[str](key))


def unzip_metadata(iterable: Iterable, keys: Iterable[str]) -> Iterator:
    """
    Iterates over the meta-data attached to the objects in
    the given iterable under the given keys.

    :param iterable:    The object iterable.
    :param keys:        The meta-data key iterable.
    :return:            An iterator over the meta-data.
    """
    from ..meta import get_metadata
    return (get_metadata(obj, key) for obj, key in zip(iterable, keys))
