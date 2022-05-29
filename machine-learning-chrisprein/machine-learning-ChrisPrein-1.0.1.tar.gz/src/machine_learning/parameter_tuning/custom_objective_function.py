from ast import Call
from typing import Callable, Optional, Union
from .abstractions.objective_function import ObjectiveFunction, OptimizationType
from ..modeling.abstractions.model import Model, TInput, TTarget
from ..evaluation.abstractions.evaluation_metric import EvaluationMetric, TModel, EvaluationContext


class CustomObjectiveFunction(ObjectiveFunction[TInput, TTarget, TModel]):
    def __init__(self, expression: Union[Callable[[EvaluationContext[TInput, TTarget, TModel]], float], EvaluationMetric[TInput, TTarget, TModel]], optimization_type: Optional[OptimizationType] = OptimizationType.MAX):
        if expression is None:
            raise ValueError("expression can't be empty")

        self.expression: Union[Callable[[EvaluationContext[TInput, TTarget, TModel]], float], EvaluationMetric[TInput, TTarget, TModel]] = expression

        self.__optimization_type: OptimizationType = optimization_type

    @property
    def optimization_type(self) -> OptimizationType:
        return self.__optimization_type

    def calculate_score(self, context: EvaluationContext[TInput, TTarget, TModel]) -> float:
        return self.expression(context)