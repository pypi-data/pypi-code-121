"""Base Aggregator classes.

Attributes:
    registry: A read-only dictionary of aggregator factory names to their implementation
        classes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import inspect
from types import MappingProxyType
from typing import Any, ClassVar, Dict, Generic, Mapping, Optional, Type

from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.roles import _RolesMixIn
from bitfount.federated.shim import _load_default_tensor_shim
from bitfount.federated.types import AggregatorType
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _SerializedWeights,
    _Weights,
)

logger = _get_federated_logger(__name__)


class _BaseAggregator(ABC):
    """Base Aggregator from which all other aggregators must inherit."""

    def __init__(self, **kwargs: Any):
        self._tensor_shim = _load_default_tensor_shim()


class _BaseModellerAggregator(_BaseAggregator, Generic[T_DTYPE], ABC):
    """Base modeller-side aggregator."""

    @abstractmethod
    def run(
        self,
        parameter_updates: Mapping[str, _SerializedWeights],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> _Weights:
        """Run the modeller-side aggregator."""
        pass


class _BaseWorkerAggregator(_BaseAggregator, ABC):
    """Base worker-side aggregator."""

    @abstractmethod
    async def run(
        self, parameter_update: _Weights, **kwargs: Any
    ) -> _SerializedWeights:
        """Run the worker-side aggregator."""
        pass


# The mutable underlying dict that holds the registry information
_registry: Dict[str, Type[_BaseAggregatorFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, Type[_BaseAggregatorFactory]] = MappingProxyType(_registry)


class _AggregatorWorkerFactory(ABC):
    """Defines the base worker() factory method for aggregation."""

    @abstractmethod
    def worker(self, **kwargs: Any) -> _BaseWorkerAggregator:
        """Return worker side of the Aggregator."""
        pass


class _BaseAggregatorFactory(ABC, _BaseSerializableObjectMixIn, _RolesMixIn):
    """Base aggregator factory from which all others should inherit."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(self, **kwargs: Any) -> None:
        self.class_name = AggregatorType[type(self).__name__].value

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Protocol registry")
            _registry[cls.__name__] = cls

    @abstractmethod
    def modeller(self, **kwargs: Any) -> _BaseModellerAggregator:
        """Return modeller side of the Aggregator."""
        ...
