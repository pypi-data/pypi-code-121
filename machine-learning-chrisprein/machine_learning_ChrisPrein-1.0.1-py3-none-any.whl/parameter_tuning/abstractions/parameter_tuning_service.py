from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Tuple, Union
from torch.utils.data.dataset import Dataset

from .model_factory import ModelFactory

from .objective_function import ObjectiveFunction

from ...modeling.abstractions.model import TInput, TTarget
from ...evaluation.abstractions.evaluation_metric import TModel

class ParameterTuningService(Generic[TInput, TTarget, TModel], ABC):

    @abstractmethod
    async def search(self, model_factory: ModelFactory[TModel], params: Dict[str, List[Any]], dataset: Dataset[Tuple[TInput, TTarget]], objective_functions: Dict[str, ObjectiveFunction[TInput, TTarget, TModel]], primary_objective: str) -> Dict[str, Any]:
        pass