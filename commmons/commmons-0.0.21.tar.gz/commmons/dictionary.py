from functools import reduce

__all__ = [
    "merge"
]


def _merge_single(first: dict, second: dict) -> dict:
    for key, value in second.items():
        if isinstance(value, dict):
            if key in first and not isinstance(first[key], dict):
                raise ValueError("Incompatible types")
            node = first.setdefault(key, {})
            _merge_single(node, value)
        else:
            first[key] = value
    return first


def merge(*dictionaries):
    return reduce(_merge_single, dictionaries, dict())
