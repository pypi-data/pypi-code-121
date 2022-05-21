from typing import TypeVar, Iterable, Callable, Dict, List, Optional, Tuple, Iterator

from pkm.utils.commons import NoSuchElementException
from pkm.utils.types import Hashable

_T = TypeVar("_T")
_U = TypeVar("_U")
_K = TypeVar("_K", bound=Hashable)
_SENTINAL = object()


def groupby(seq: Iterable[_T], key: Callable[[_T], _K]) -> Dict[_K, List[_T]]:
    """
    :param seq: sequence to group
    :param key: a key function, the seq items will be grouped by it
    :return:
    """
    result: Dict[_U, List[_T]] = {}
    for item in seq:
        k = key(item)
        lst = result.get(k)
        if lst is None:
            result[k] = lst = []
        lst.append(item)

    return result


def find_first(seq: Iterable[_T], match: Callable[[_T], bool], none_value: Optional[_T] = None) -> Optional[_T]:
    """
    :param seq: the sequence to look in
    :param match: predicate for items in the sequence
    :param none_value: result for no match
    :return: the first item in the sequence that match or non_value if such not found
    """
    return next((it for it in seq if match(it)), none_value)


def partition(seq: Iterable[_T], match: Callable[[_T], bool]) -> Tuple[List[_T], List[_T]]:
    """
    :param seq: the sequence to partition
    :param match: predicate for item in the sequence
    :return: two lists, the first with items that match and the second containing the rest
    """

    t, f = [], []
    for item in seq:
        if match(item):
            t.append(item)
        else:
            f.append(item)

    return t, f


def single_or_raise(seq: Iterable[_T]) -> _T:
    """
    :param seq: the iterable to access
    :return: the first element of this iterable if the number of elements in it is 1 otherwise raise `ValueError`
    """

    result = single_or(seq, _SENTINAL)
    if result is _SENTINAL:
        raise ValueError(f"expecting single element but found 0 or more than 1")

    return result


def single_or(seq: Iterable[_T], default_value: Optional[_T] = None) -> Optional[_T]:
    """
    :param seq: the iterable to access
    :param default_value: the value to return in case where iterable does not contain a single element
    :return: the first element of this iterable if the number of elements in it is 1 otherwise `default_value`
    """
    i = iter(seq)
    if (single := next(i, _SENTINAL)) is _SENTINAL:
        return default_value
    if next(i, _SENTINAL) is not _SENTINAL:
        return default_value

    return single


def distinct(it: Iterable[_T], key: Callable[[_T], _K] = lambda x: x) -> Iterator[_T]:
    """
    :param it: the iterator to run over
    :param key: key function by which to perform the comparison
    :return: iterator over `it` which only contain each item in it once
    """
    s = set()
    for item in it:
        item_key = key(item)
        if item_key not in s:
            s.add(item_key)
            yield item


def without(it: Iterable[_T], predicate: Callable[[_T], bool]) -> Iterator[_T]:
    """
    :param it: the iterator to run over
    :param predicate: predicate for items in `it`
    :return: iterator containing only items in `it` which `predicate` returned `False` for
    """
    return (v for v in it if not predicate(v))


def without_nones(it: Iterable[Optional[_T]]) -> Iterator[_T]:
    """
    :param it: the iterator to run over
    :return: iterator containing all the non-none items in `it`
    """
    return without(it, lambda x: x is None)


def first(it: Iterable[_T], default: _T) -> _T:
    """
    return the first value in the given iterable (does not have to be subscriptable)
    :param it: the iterator to run over
    :param default: the value to return if `it` if empty
    :return: the first value in `it` or `default` if `it` is empty
    """
    return next(iter(it), default)


def first_or_none(it: Iterable[_T]) -> Optional[_T]:
    """
    same as calling `first(it, None)`
    :param it: the iterator to run over
    :return: the first value in `it` or None if `it` is empty
    """
    return first(it, None)


def first_or_raise(it: Iterable[_T]) -> Optional[_T]:
    """
    same as calling `first(it)` but throws exception in case where `it` has no elements
    :param it: the iterator to run over
    :return: the first value in `it`
    """
    if (result := first(it, _SENTINAL)) is _SENTINAL:
        raise NoSuchElementException("empty")
    return result


def strs(it: Iterable[_T]) -> Iterator[str]:
    """
    :param it: the iterable to extract items from
    :return: iterable yielding `str(item)` for each item in `iter`
    """
    return (str(it) for it in it)
