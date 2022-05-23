from collections import Hashable
from typing import Any


def is_hashable(obj: Any) -> bool:
    """
    Checks if the given object is hashable.

    :param obj: The object to check.
    :return:    True if the object is hashable,
                False if not.
    """
    return isinstance(obj, Hashable)
