"""Contains models for running on the Bitfount platform."""
from typing import List

from bitfount.models.base_models import (
    ClassifierMixIn,
    CNNModelStructure,
    EarlyStopping,
    FeedForwardModelStructure,
    LoggerConfig,
    ModelContext,
    NeuralNetworkMixIn,
    NeuralNetworkModelStructure,
    NeuralNetworkPredefinedModel,
    Optimizer,
    RegressorMixIn,
    Scheduler,
)
from bitfount.models.bitfount_model import BitfountModel
from bitfount.models.models import LogisticRegressionClassifier, RegBoostRegressor

__all__: List[str] = [
    "BitfountModel",
    "ClassifierMixIn",
    "CNNModelStructure",
    "EarlyStopping",
    "FeedForwardModelStructure",
    "LoggerConfig",
    "LogisticRegressionClassifier",
    "ModelContext",
    "NeuralNetworkMixIn",
    "NeuralNetworkModelStructure",
    "NeuralNetworkPredefinedModel",
    "Optimizer",
    "RegBoostRegressor",
    "RegressorMixIn",
    "Scheduler",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
