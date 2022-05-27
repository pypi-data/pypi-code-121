"""Useful objects/functions for federated learning.

This is primarily intended for use by modules outside of the `federated` package.
It cannot be imported by most modules in the `federated` package because it would
introduce circular imports.
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Dict, Mapping, Type, Union, cast

import bitfount.federated.aggregators.base as aggregators
import bitfount.federated.algorithms.base as algorithms
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import _DistributedModelMixIn
import bitfount.federated.protocols.base as protocols
import bitfount.models.base_models as model_structures
from bitfount.models.base_models import (
    NeuralNetworkModelStructure,
    NeuralNetworkPredefinedModel,
    _BaseModel,
)
import bitfount.models.models as core_models
from bitfount.types import DistributedModelProtocol

logger = _get_federated_logger(__name__)

# This is a read-only dictionary mapping the name of an aggregator to the class itself
_AGGREGATORS: Mapping[
    str, Type[aggregators._BaseAggregatorFactory]
] = aggregators.registry


# This is a read-only dictionary mapping the name of an algorithm to the class itself
_ALGORITHMS: Mapping[str, Type[algorithms._BaseAlgorithmFactory]] = algorithms.registry


# This is a read-only dictionary mapping the name of a protocol to the class itself
_PROTOCOLS: Mapping[str, Type[protocols._BaseProtocolFactory]] = protocols.registry


_MODEL_STRUCTURES: Dict[
    str, Type[Union[NeuralNetworkPredefinedModel, NeuralNetworkModelStructure]]
] = {
    name: class_
    for name, class_ in vars(model_structures).items()
    if inspect.isclass(class_)
    and issubclass(class_, (NeuralNetworkPredefinedModel, NeuralNetworkModelStructure))
    and not inspect.isabstract(class_)
}


def _load_models_from_module(module: ModuleType) -> Dict[str, Type[_BaseModel]]:
    """Load all concrete classes subclassing _BaseModel from a module.

    Args:
        module (ModuleType): The module to load models from.

    Returns:
        Dict[str, Type[_BaseModel]]: A dict of class name to class for all models found
    """
    found_models: Dict[str, Type[_BaseModel]] = {}

    # Load any concrete classes that extend DistributedModelMixIn and _BaseModel
    for cls_name, class_ in vars(module).items():
        if (
            inspect.isclass(class_)
            and issubclass(class_, _BaseModel)
            and not inspect.isabstract(class_)
        ):
            found_models[cls_name] = class_

    return found_models


def _load_backend_models() -> Dict[str, Type[_BaseModel]]:
    """Load model definitions from backends.

    Load all models defined in model.py modules for backends in the
    bitfount.backends package.

    Returns:
        Dict[str, Type[_BaseModel]]: A dict of class name to class for all models found
    """
    found_models: Dict[str, Type[_BaseModel]] = {}

    try:
        import bitfount.backends
    except ModuleNotFoundError:
        logger.warning("Unable to import bitfount.backends; does it exist?")
        return {}

    backend_path = bitfount.backends.__path__
    backend_prefix = f"{bitfount.backends.__name__}."

    # Find all top-level modules in the backend directory
    for _finder, name, _ispkg in pkgutil.iter_modules(backend_path, backend_prefix):
        models_module = None
        try:
            # Import their models.py file
            models_module = f"{name}.models.models"
            module = importlib.import_module(models_module)
            found_models.update(_load_models_from_module(module))
        except ImportError as ie:
            loc = models_module if models_module else name
            logger.error(f"Unable to import models from backend {loc}: {ie}")
    return found_models


# This is a dictionary mapping the name of a model to the model class itself
# Load all models in main models.py
_MODELS: Dict[str, Type[_BaseModel]] = _load_models_from_module(core_models)
# Load any models in a backend's models.py
_MODELS.update(_load_backend_models())

# This is a dictionary mapping the name of a distributed model to the model class itself
_DISTRIBUTED_MODELS: Dict[str, Type[DistributedModelProtocol]] = {}

# We take a subset of MODELS that additionally subclass DistributedModelMixIn
for model_name, model_class in _MODELS.items():
    if issubclass(model_class, _DistributedModelMixIn):
        _DISTRIBUTED_MODELS[model_name] = cast(
            Type[DistributedModelProtocol], model_class
        )
