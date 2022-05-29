"""Utility methods for dictionaries."""

from typing import Callable, Dict, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

def get_or_add(dictionary: Dict[TKey, TValue], key: TKey, value_factory: Callable[[TKey], TValue]) -> TValue:
    """Gets the value associated to the specified key from the specified dictionary,
    or adds the specified value if the key cannot be found.

    :param dictionary: The dictionary to use.
    :type dictionary: Dict[TKey, TValue]
    :param key: The key to look for.
    :type key: TKey
    :param value_factory: The value to add when the key cannot be found.
    :type value_factory: Callable[[TKey], TValue]
    :return: If exists, the value currently present in the dictionary; otherwise, the newly added value.
    :rtype: TValue
    """

    existing_value = dictionary.get(key, None)
    if not existing_value:
        dictionary[key] = existing_value = value_factory(key)
    return existing_value
