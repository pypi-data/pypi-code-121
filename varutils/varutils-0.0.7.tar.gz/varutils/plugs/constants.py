from types import MappingProxyType
from typing import Mapping, Any

__all__ = (
    'empty_mapping_proxy',
)

empty_mapping_proxy: Mapping[str, Any] = MappingProxyType({})
