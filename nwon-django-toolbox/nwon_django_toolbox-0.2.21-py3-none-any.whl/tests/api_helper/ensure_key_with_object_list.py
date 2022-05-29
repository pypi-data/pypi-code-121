from typing import List

from nwon_baseline.typings import AnyDict


def ensure_key_with_object_list(outer_object: AnyDict, key: str) -> List[AnyDict]:
    """
    Ensures outer_object has a key that contains a list of objects.
    """

    assert key in outer_object, f"Key {key} is missing in object."
    inner_list_of_objects = outer_object[key]

    assert isinstance(inner_list_of_objects, list), f"Property {key} is not a list."
    for index, inner_object in enumerate(inner_list_of_objects):
        assert isinstance(
            inner_object, dict
        ), f"entry {index} in list is not an object."

    return inner_list_of_objects


__all__ = ["ensure_key_with_object_list"]
