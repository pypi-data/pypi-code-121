from typing import Callable

from machine_learning.modeling.abstractions.model import TTarget, TInput
from .abstractions.evaluation_metric import EvaluationContext, EvaluationMetric, TModel

class CustomEvaluationMetric(EvaluationMetric[TInput, TTarget, TModel]):
    def __init__(self, expression: Callable[[EvaluationContext[TInput, TTarget, TModel]], float]):
        if expression is None:
            raise ValueError("expression can't be empty")

        self.expression: Callable[[EvaluationContext[TInput, TTarget, TModel]], float] = expression

    def calculate_score(self, context: EvaluationContext[TInput, TTarget, TModel]) -> float:
        return self.expression(context)