# flake8: noqa F401

from .base import GenericBaseRepository
from .cached import CacheRepository
from .composition import MappedRepository
from .exceptions import CrudException, InvalidPayloadException, ItemNotFoundException
from .mapper import ConstructorMapper, LambdaMapper, Mapper, ToFunctionArgsMapper

__all__ = [
    # Base classes
    "GenericBaseRepository",
    # Cache-based implementations:
    "CacheRepository",
    # Composition:
    "MappedRepository",
    "ConstructorMapper",
    "LambdaMapper",
    "Mapper",
    "ToFunctionArgsMapper",
    # Exceptions:
    "CrudException",
    "InvalidPayloadException",
    "ItemNotFoundException",
]

try:
    from .database import DatabaseRepository
except ImportError:  # pragma nocover
    pass
else:
    __all__ += ["DatabaseRepository"]

try:
    from .http import HttpRepository
except ImportError:  # pragma nocover
    pass
else:
    __all__ += ["HttpRepository"]

try:
    from .pydantic import PydanticDictMapper, PydanticObjectMapper
except ImportError:  # pragma nocover
    pass
else:
    __all__ += ["PydanticDictMapper", "PydanticObjectMapper"]
