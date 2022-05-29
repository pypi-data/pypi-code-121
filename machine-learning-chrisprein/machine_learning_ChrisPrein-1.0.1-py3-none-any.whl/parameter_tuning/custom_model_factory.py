from typing import Any, Callable, Dict
from .abstractions.model_factory import ModelFactory
from ..evaluation.abstractions.evaluation_metric import TModel

class CustomModelFactory(ModelFactory[TModel]):
    def __init__(self, expression: Callable[[Dict[str, Any]], TModel]):
        if expression is None:
            raise ValueError("expression can't be empty")

        self.__expression: Callable[[Dict[str, Any]], TModel] = expression

    def create(self, params: Dict[str, Any]) -> TModel:
        return self.__expression(params)