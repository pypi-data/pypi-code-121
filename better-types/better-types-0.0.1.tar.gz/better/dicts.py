

from typing import Any, TypeAlias, TypeVar

T = TypeVar("T")

Data: TypeAlias = dict[str, T]


# def deep_get(obj: Any, *keys: Any, default: Any = None) -> Any:
#     iter_keys = iter(keys)
#     try:
#         while obj:
#             next_key = next(iter_keys)
#             obj = obj.get(next_key)
#     except AttributeError:
#         obj = default
#     except StopIteration:
#         pass
#     return obj or default

# @staticmethod
# def merge_dicts(*dicts: dict[T, U]) -> dict[T, U]:
#     """Deep merge multiple dict into a single one.
#     Order matters: dict are merged from left to right.
#     """

#     def _merge(d1: dict, d2: dict):
#         merged_dict = {}
#         for key in set(d1.keys()).union(d2.keys()):
#             if (
#                 key in d1
#                 and key in d2
#                 and isinstance(d1[key], dict)
#                 and isinstance(d2[key], dict)
#             ):
#                 merged_dict[key] = _merge(d1[key], d2[key])
#             elif key in d2:
#                 merged_dict[key] = d2[key]
#             else:
#                 merged_dict[key] = d1[key]
#         return merged_dict

#     return reduce(_merge, dicts, {})
