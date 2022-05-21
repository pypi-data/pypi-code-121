from typing import TypeVar, MutableMapping, Optional, Callable, Dict, Mapping

from pkm.utils.types import Hashable

_K = TypeVar("_K", bound=Hashable)
_V = TypeVar("_V")
_M = TypeVar("_M", bound=MutableMapping)
_IM = TypeVar("_IM", bound=Mapping)
_MISSING = object()


def put_if_absent(d: MutableMapping[_K, _V], key: _K, value: _V) -> bool:
    """
    sets `d[key]=value` if `key not in d`
    :param d: the dict to mutate
    :param key: the key to assign
    :param value: the value to set if `key not in d`
    :return: true if `value` was set (`key` was not in `d`), false otherwise.
    """
    if key in d:
        return False
    d[key] = value
    return True


def get_or_put(d: MutableMapping[_K, _V], key: _K, value_provider: Callable[[], _V]) -> _V:
    """
    :param d: the dict to look in
    :param key: the key to get
    :param value_provider: function providing a new value for `d[key]` in the case where no such value already exists
    :return: `d[key]` if such value exists otherwise set `d[key] = value_provider()` and then returns `d[key]`
    """
    if (value := d.get(key, _MISSING)) is _MISSING:
        d[key] = value = value_provider()

    return value


def get_or_compute(d: Mapping[_K, _V], key: _K, value_provider: Callable[[], _V]) -> _V:
    """
    :param d: the dict to look in
    :param key: the key to get
    :param value_provider: function providing a new value for `d[key]` in the case where no such value already exists
    :return: `d[key]` if such value exists otherwise value_provider(), does not modifies `d`.
    """
    if (value := d.get(key, _MISSING)) is _MISSING:
        return value_provider()

    return value


def get_or_raise(d: MutableMapping[_K, _V], key: _K, err_provider: Callable[[], Exception]) -> _V:
    """
    attempt to get a value from `d` with the given `key`, if no such value exists raise the
    exception returned by `err_provider`
    :param d: the mapping to look in
    :param key: the key to look for
    :param err_provider: callable that may be called to provide an exception instance in case where `key` is not in `d`
    :return: the value `d[key]`
    """

    if (result := d.get(key, _MISSING)) is _MISSING:
        raise err_provider()

    return result


def without_keys(d: Mapping[_K, _V], *keys: _K) -> Dict[_K, _V]:
    """
    creates a new dict with the same content as `d` minus the keys that are in `keys`
    :param d: the mapping to clone
    :param keys: the keys to leave out
    :return: the newly created dict
    """
    remove_set = set(keys)
    return {k: v for k, v in d.items() if k not in remove_set}


def remove_none_values(d: _M) -> _M:
    """
    remove from `d` all items with value equals to None and return back `d`
    :param d: the dict to remove from
    :return: `d` after the required changes
    """
    return remove_by_value(d)


def remove_by_value(
        d: _M, value: Optional[_V] = None,
        match: Optional[Callable[[_V], bool]] = None) -> _M:
    """
    remove items from [d] if they either match the given [match] function
    or if no [match] function given, if they are equals to the given [value]

    :param d: the dict to remove items from
    :param value: if supplied, the value to remove
    :param match: if supplied, matcher for the values to remove
    :return: [d]
    """

    if match:
        keys_to_remove = [k for k, v in d.items() if match(v)]
    else:
        keys_to_remove = [k for k, v in d.items() if v == value]

    for k in keys_to_remove:
        del d[k]

    return d


