from abc import ABC, abstractmethod
from typing import TypeVar, List, Generic
from dataclasses import dataclass
from ...modeling.abstractions.model import Model, TInput, TTarget

TModel = TypeVar('TModel', bound=Model)

@dataclass(frozen=True)
class Prediction(Generic[TInput, TTarget]):
    input: TInput
    prediction: TTarget
    target: TTarget

@dataclass(frozen=True)
class EvaluationContext(Generic[TInput, TTarget, TModel], ABC):
    model: TModel
    dataset_name: str
    predictions: List[Prediction[TInput, TTarget]]

class EvaluationMetric(Generic[TInput, TTarget, TModel], ABC):
    
    @abstractmethod
    def calculate_score(self, context: EvaluationContext[TInput, TTarget, TModel]) -> float:
        pass

    def __call__(self, context: EvaluationContext[TInput, TTarget, TModel]) -> float:
        return self.calculate_score(context)