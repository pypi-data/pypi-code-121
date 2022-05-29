from abc import ABC, abstractmethod
from enum import Enum

from ...modeling.abstractions.model import Model
from ...evaluation.abstractions.evaluation_metric import EvaluationMetric, TModel
from ...modeling.abstractions.model import Model, TInput, TTarget

class OptimizationType(Enum):
    MIN = 1,
    MAX = 2

class ObjectiveFunction(EvaluationMetric[TInput, TTarget, TModel], ABC):
    @property
    @abstractmethod
    def optimization_type(self) -> OptimizationType:
        pass
