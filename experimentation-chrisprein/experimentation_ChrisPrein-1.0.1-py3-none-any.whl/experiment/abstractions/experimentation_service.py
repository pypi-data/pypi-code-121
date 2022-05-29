from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar, Union
from uuid import UUID
from .experiment_settings import ExperimentSettings
from .experiment_result import ExperimentResult

TExperimentSettings = TypeVar('TExperimentSettings', bound=ExperimentSettings)
TExperimentResult = TypeVar('TExperimentResult', bound=ExperimentResult)

class ExperimentationService(Generic[TExperimentSettings, TExperimentResult], ABC):

    @abstractmethod
    async def run_experiment(self, experiment_settings: TExperimentSettings, experiment_id: Optional[UUID] = None) -> TExperimentResult:
        pass

    @abstractmethod
    async def run_experiments(self, experiment_settings: Dict[str, TExperimentSettings]) -> Dict[str, TExperimentResult]:
        pass