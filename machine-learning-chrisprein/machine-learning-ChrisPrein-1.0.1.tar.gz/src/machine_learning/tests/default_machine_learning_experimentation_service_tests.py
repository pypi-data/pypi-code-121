from asyncio import coroutine
import asyncio
from dataclasses import dataclass
from re import S
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from torch import isin
from torch.utils.data import Dataset
from dataset_handling.dataloader import DataLoader
from typing import Any, Coroutine, List, Dict, Tuple
from faker import Faker
import random
from ..evaluation.abstractions.evaluation_metric import EvaluationMetric
from ..evaluation.multi_task_evaluation_service import MultiTaskEvaluationService
from ..evaluation.abstractions.evaluation_service import EvaluationService
from ..training.abstractions.training_service import TrainingService
from ..modeling.abstractions.model import Model, TInput, TTarget
from ..training.batch_training_service import BatchTrainingService
from ..training.abstractions.stop_condition import StopCondition
from ..parameter_tuning.abstractions.objective_function import ObjectiveFunction
from ..experimentation.abstractions.machine_learning_experimentation_service import MachineLearningExperimentSettings, InstanceSettings
from ..experimentation.default_machine_learning_experimentation_service import DefaultMachineLearningExperimentationService, MachineLearningExperimentResult, MachineLearningExperimentSettings

class DefaultMachineLearningExperimentationTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.samples: List[Tuple[str, str]] = [(fake.first_name(), fake.last_name()) for i in range(100)]

        self.model: Model[str, str] = AsyncMock(spec=Model)
        self.model.__class__ = AsyncMock

        self.objective_function: ObjectiveFunction[str, str, Model[str, str]] = AsyncMock(spec=ObjectiveFunction)
        self.objective_function.__class__ = AsyncMock

        self.stop_condition: StopCondition[str, str, Model[str, str]] = AsyncMock(spec=StopCondition)
        self.stop_condition.__class__ = AsyncMock

        self.evaluation_metric: EvaluationMetric[str, str, Model[str, str]] = AsyncMock(spec=EvaluationMetric)
        self.stop_condition.__class__ = AsyncMock

        self.evaluation_service: EvaluationService[str, str, Model[str, str]] = AsyncMock(spec=EvaluationService)
        self.evaluation_service.__class__ = AsyncMock

        self.training_service: TrainingService[str, str, Model[str, str]] = AsyncMock(spec=TrainingService)
        self.training_service.__class__ = AsyncMock

        self.dataset: Dataset[Tuple[str, str]] = AsyncMock()
        self.dataset.__class__ = AsyncMock

        self.event_loop = asyncio.get_event_loop()

        self.experimentation_service: DefaultMachineLearningExperimentationService[Model[str, str]] = DefaultMachineLearningExperimentationService[Model[str, str]](logger=None, 
        model_factory=lambda x: self.model, training_service_factory=lambda x: self.training_service, evaluation_service_factory=lambda x: self.evaluation_service, 
        training_dataset_factory=lambda x: self.dataset, test_dataset_factory=lambda x: self.dataset, evaluation_metric_factory=lambda x: self.evaluation_metric, 
        objective_function_factory=lambda x: self.objective_function, stop_condition_factory=lambda x: self.stop_condition, event_loop=self.event_loop)

    def tearDown(self):
        pass

    def test_run_experiment_valid_settings_should_return_experiment_result(self):
        experiment_settings: MachineLearningExperimentSettings = MachineLearningExperimentSettings(name="experiment 1", model_settings=[InstanceSettings(name="", params={})], 
        training_service_settings=[InstanceSettings(name="test 1", params={}), InstanceSettings(name="test 2", params={})], evaluation_service_settings=[InstanceSettings(name="", params={})], training_dataset_settings=[{"": InstanceSettings(name="", params={})}], 
        evaluation_dataset_settings=[{"": InstanceSettings(name="test 1", params={})}, {"": InstanceSettings(name="test 2", params={})}], evaluation_metric_settings=[{"": InstanceSettings(name="", params={})}],
        objective_function_settings=[{"": InstanceSettings(name="", params={})}], stop_condition_settings=[{"": InstanceSettings(name="", params={})}])

        evaluation_routine: Coroutine[Any, Any, MachineLearningExperimentResult[Model[str, str]]] = self.experimentation_service.run_experiment(experiment_settings)

        result: MachineLearningExperimentResult[Model[str, str]] = self.event_loop.run_until_complete(evaluation_routine)

        assert len(result.run_results) == 4

    def test_run_experiments_valid_settings_should_return_experiment_result_for_each_setting(self):
        experiment_settings_1: MachineLearningExperimentSettings = MachineLearningExperimentSettings(name="experiment 1", model_settings=[InstanceSettings(name="", params={})], 
        training_service_settings=[InstanceSettings(name="test 1", params={}), InstanceSettings(name="test 2", params={})], evaluation_service_settings=[InstanceSettings(name="", params={})], training_dataset_settings=[{"": InstanceSettings(name="", params={})}], 
        evaluation_dataset_settings=[{"": InstanceSettings(name="test 1", params={})}, {"": InstanceSettings(name="test 2", params={})}], evaluation_metric_settings=[{"": InstanceSettings(name="", params={})}],
        objective_function_settings=[{"": InstanceSettings(name="", params={})}], stop_condition_settings=[{"": InstanceSettings(name="", params={})}])

        experiment_settings_2: MachineLearningExperimentSettings = MachineLearningExperimentSettings(name="experiment 2", model_settings=[InstanceSettings(name="", params={})], 
        training_service_settings=[InstanceSettings(name="test 1", params={}), InstanceSettings(name="test 2", params={})], evaluation_service_settings=[InstanceSettings(name="", params={})], training_dataset_settings=[{"": InstanceSettings(name="", params={})}], 
        evaluation_dataset_settings=[{"": InstanceSettings(name="test 1", params={})}, {"": InstanceSettings(name="test 2", params={})}], evaluation_metric_settings=[{"": InstanceSettings(name="", params={})}],
        objective_function_settings=[{"": InstanceSettings(name="", params={})}], stop_condition_settings=[{"": InstanceSettings(name="", params={})}])

        evaluation_routine: Coroutine[Any, Any, Dict[str, MachineLearningExperimentResult[Model[str, str]]]] = self.experimentation_service.run_experiments({"ex 1": experiment_settings_1, "ex 2": experiment_settings_2})

        result: Dict[str, MachineLearningExperimentResult[Model[str, str]]] = self.event_loop.run_until_complete(evaluation_routine)

        assert len(list(result.items())) == 2

        for key, item in result.items():
            assert len(item.run_results) == 4