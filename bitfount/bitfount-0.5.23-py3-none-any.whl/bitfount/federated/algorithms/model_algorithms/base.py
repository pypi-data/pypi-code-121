"""Base classes for all model-based algorithms.

Attributes:
    registry: A read-only dictionary of model algorithm factory names to their
        implementation classes.
"""
from __future__ import annotations

from abc import ABC
import inspect
import os
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generic,
    Mapping,
    Optional,
    Type,
    Union,
    cast,
)

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    _BaseAlgorithmFactory,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.models.base_models import MAIN_MODEL_REGISTRY, ModelContext
from bitfount.schemas.utils import bf_dump
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _SerializedWeights,
    _StrAnyDict,
)

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub
    from bitfount.types import _DistributedModelTypeOrReference


logger = _get_federated_logger(__name__)


class _BaseModelAlgorithm(Generic[T_DTYPE], _BaseAlgorithm, ABC):
    """Blueprint for either the modeller side or the worker side of ModelAlgorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.pretrained_file = pretrained_file

    @property
    def tensor_precision(self) -> T_DTYPE:
        """Returns model tensor precision."""
        return self.model.tensor_precision()


class _BaseModellerModelAlgorithm(_BaseModelAlgorithm, _BaseModellerAlgorithm, ABC):
    """Modeller side of the algorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ):
        super().__init__(model=model, pretrained_file=pretrained_file, **kwargs)

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm as required."""
        if not self.model.initialised:
            self.model.initialise_model(context=ModelContext.MODELLER)

        # This needs to occur AFTER model initialization so the model is correctly
        # created. deserialize() may cause initialization but we can not rely on it
        # in this instance because we need to pass in context information.
        # This should be reviewed as part of [BIT-536].
        if self.pretrained_file is not None:
            logger.info(f"Deserializing model from {self.pretrained_file}.")
            self.model.deserialize(self.pretrained_file)


class _BaseWorkerModelAlgorithm(_BaseModelAlgorithm, _BaseWorkerAlgorithm, ABC):
    """Worker side of the algorithm."""

    def __init__(self, *, model: DistributedModelProtocol, **kwargs: Any):
        super().__init__(model=model, **kwargs)

    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        model_params: Optional[_SerializedWeights] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm as required."""
        # Apply pod DP settings if needed. Needs to occur before model
        # initialization so the right DP settings are applied during initialization.

        self._apply_pod_dp(pod_dp)
        self.model.initialise_model(data=datasource, context=ModelContext.WORKER)
        if model_params:
            tensor_model_params = self.model.deserialize_params(model_params)
            self.model.update_params(tensor_model_params)

    def _apply_pod_dp(self, pod_dp: Optional[DPPodConfig]) -> None:
        """Applies pod-level Differential Privacy constraints if supported.

        The model must inherit from `DifferentiallyPrivate` for DP to be supported.

        Args:
            pod_dp: The pod DP constraints to apply or None if no constraints.
        """
        try:
            # only applied if model supports DP so can ignore attr-defined
            self.model.apply_pod_dp(pod_dp)  # type: ignore[attr-defined]  # Reason: caught by try-except  # noqa: B950
        except AttributeError:
            pass


# The mutable underlying dict that holds the registry information
_registry: Dict[str, Type[_BaseModelAlgorithmFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, Type[_BaseModelAlgorithmFactory]] = MappingProxyType(_registry)


class _BaseModelAlgorithmFactory(_BaseAlgorithmFactory, ABC):
    """Base factory for algorithms involving an underlying model."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"model": MAIN_MODEL_REGISTRY}

    def __init__(
        self,
        *,
        model: _DistributedModelTypeOrReference,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.pretrained_file = pretrained_file

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Model Algorithm registry")
            _registry[cls.__name__] = cls

    @property
    def model_schema(self) -> _StrAnyDict:
        """Returns underlying model Schema."""
        self.model = cast(DistributedModelProtocol, self.model)
        return bf_dump(self.model)

    def _get_model_from_reference(
        self, hub: Optional[BitfountHub] = None
    ) -> DistributedModelProtocol:
        """Returns underlying model if BitfountModelReference.

        If not, just returns self.model.
        """
        # TODO: [BIT-890] perhaps move this logic one level higher so that the algorithm
        # factory always takes a DistributedModelProtocol
        if isinstance(self.model, BitfountModelReference):
            if hub is not None:
                self.model.hub = hub
            model = self.model.get_model()(
                datastructure=self.model.datastructure,
                schema=self.model.schema,
                **self.model.hyperparameters,
            )
            self.model = cast(DistributedModelProtocol, model)
            return self.model
        else:
            return self.model
