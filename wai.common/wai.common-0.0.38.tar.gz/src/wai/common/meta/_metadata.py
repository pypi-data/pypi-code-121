from typing import Any

from .._typing import T

META_DATA_KEY: str = "__metadata"


def with_metadata(obj: T, key: str, value: Any) -> T:
    """
    Adds meta-data to an object.

    :param obj:     The object to add meta-data to.
    :param key:     The key to store the meta-data under.
    :param value:   The meta-data value to store.
    :return:        obj.
    """
    # Create the meta-data map
    if not hasattr(obj, META_DATA_KEY):
        try:
            setattr(obj, META_DATA_KEY, {})
        except AttributeError as e:
            raise ValueError(f"Cannot set meta-data against objects of type {obj.__class__.__name__}") from e

    # Put this mapping in the map
    getattr(obj, META_DATA_KEY)[key] = value

    return obj


def get_metadata(obj: Any, key: str) -> Any:
    """
    Gets the meta-data from an object.

    :param obj:     The object to get meta-data from.
    :param key:     The meta-data key to extract from.
    :return:        The value of the meta-data.
    """
    return getattr(obj, META_DATA_KEY)[key]


def has_metadata(obj: Any, key: str) -> bool:
    """
    Checks if the given object has meta-data associated with
    the given key.

    :param obj:     The object to check.
    :param key:     The meta-data key.
    :return:        True if there is meta-data associated with the
                    given key, False if not.
    """
    return hasattr(obj, META_DATA_KEY) and key in getattr(obj, META_DATA_KEY)
