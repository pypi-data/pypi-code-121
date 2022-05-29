from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, TypeVar
from experimentation.experiment.abstractions.experiment_settings import ExperimentSettings
from experimentation.experiment.abstractions.experiment_result import ExperimentResult
from experimentation.experiment.abstractions.experimentation_service import ExperimentationService

from ...modeling.abstractions.model import TInput, TTarget
from ...evaluation.abstractions.evaluation_metric import TModel, EvaluationContext

@dataclass
class InstanceSettings:
    name: str
    params: Dict[str, Any]

@dataclass
class MachineLearningExperimentResult(Generic[TModel], ExperimentResult):
    model: TModel
    scores: Dict[str, float]

@dataclass    
class MachineLearningExperimentSettings(ExperimentSettings):    
    model_settings: List[InstanceSettings]
    training_service_settings: List[InstanceSettings]
    evaluation_service_settings: List[InstanceSettings]
    evaluation_dataset_settings: List[Dict[str, InstanceSettings]]
    training_dataset_settings: List[Dict[str, InstanceSettings]]
    evaluation_metric_settings: List[Dict[str, InstanceSettings]]
    objective_function_settings: List[Dict[str, InstanceSettings]]
    stop_condition_settings: List[Dict[str, InstanceSettings]]

@dataclass    
class MachineLearningRunSettings():    
    experiment_name: str
    model_settings: InstanceSettings
    training_service_settings: InstanceSettings
    evaluation_service_settings: InstanceSettings
    evaluation_dataset_settings: Dict[str, InstanceSettings]
    training_dataset_settings: Dict[str, InstanceSettings]
    evaluation_metric_settings: Dict[str, InstanceSettings]
    objective_function_settings: Dict[str, InstanceSettings]
    stop_condition_settings: Dict[str, InstanceSettings]

@dataclass 
class MachineLearningRunResult(Generic[TModel]):
    run_settings: MachineLearningRunSettings
    model: TModel
    scores: Dict[str, float]

@dataclass
class MachineLearningExperimentResult(Generic[TModel], ExperimentResult):
    run_results: List[MachineLearningRunResult[TModel]]

class MachineLearningExperimentationService(Generic[TModel], 
ExperimentationService[MachineLearningExperimentSettings, MachineLearningExperimentResult[TModel]]):
    pass