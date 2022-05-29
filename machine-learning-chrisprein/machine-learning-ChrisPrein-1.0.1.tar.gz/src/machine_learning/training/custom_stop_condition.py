from abc import ABC, abstractmethod
from typing import TypeVar, List, Generic, Callable

from ..evaluation.abstractions.evaluation_metric import TModel
from .abstractions.stop_condition import StopCondition, TrainingContext
from ..modeling.abstractions.model import Model, TInput, TTarget

class CustomStopCondition(StopCondition[TInput, TTarget, TModel], ABC):
    def __init__(self, expression: Callable[[TrainingContext[TInput, TTarget, TModel]], bool]):
        if expression is None:
            raise ValueError("expression can't be empty")

        self.expression: Callable[[TrainingContext[TInput, TTarget, TModel]], bool] = expression

    def reset(self):
        pass

    def is_satisfied(self, context: TrainingContext[TInput, TTarget, TModel]) -> bool:
        return self.expression(context)