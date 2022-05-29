from abc import ABC, abstractmethod
from dataclasses import dataclass
import enum
from typing import TypeVar, List, Generic, Dict

from ...modeling.abstractions.model import Model
from ...modeling.abstractions.model import Model, TInput, TTarget
from ...parameter_tuning.abstractions.objective_function import OptimizationType
from ...evaluation.abstractions.evaluation_service import Score

TModel = TypeVar('TModel', bound=Model)

@dataclass
class TrainingContext(Generic[TInput, TTarget, TModel]):
    model: TModel
    dataset_name: str
    current_epoch: int
    current_iteration: int
    scores: Dict[str, List[Score[TInput, TTarget]]]
    _primary_objective: str

    @property
    def primary_scores(self) -> List[Score[TInput, TTarget]]:
        return self.scores[self._primary_objective]

    @property
    def current_scores(self) -> Dict[str, Score[TInput, TTarget]]:
        return {score_name: scores[self.current_epoch - 1] for score_name, scores in self.scores.items() if self.current_epoch > 0}

class StopCondition(Generic[TInput, TTarget, TModel], ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def is_satisfied(self, context: TrainingContext[TInput, TTarget, TModel]) -> bool:
        pass