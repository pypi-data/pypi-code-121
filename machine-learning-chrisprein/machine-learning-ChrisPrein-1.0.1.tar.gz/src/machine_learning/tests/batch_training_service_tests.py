from asyncio import coroutine
import asyncio
from dataclasses import dataclass
from re import S
import unittest
from unittest.mock import MagicMock, Mock, patch
from torch import isin
from torch.utils.data import Dataset
from dataset_handling.dataloader import DataLoader
from typing import Any, Coroutine, List, Dict, Tuple
from faker import Faker
import random
from ..evaluation.abstractions.evaluation_metric import EvaluationMetric
from ..evaluation.multi_task_evaluation_service import MultiTaskEvaluationService
from ..modeling.abstractions.model import Model, TInput, TTarget
from ..training.batch_training_service import BatchTrainingService
from ..training.abstractions.stop_condition import StopCondition
from ..parameter_tuning.abstractions.objective_function import ObjectiveFunction

class BatchTrainingServiceTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.samples: List[Tuple[str, str]] = [(fake.first_name(), fake.last_name()) for i in range(100)]

        self.model: Model[str, str] = MagicMock(spec=Model)
        self.model.predict_batch = Mock(return_value=[fake.last_name() for i in range(10)])

        self.objective_function_1: ObjectiveFunction[str, str, Model[str, str]] = MagicMock(spec=ObjectiveFunction)
        self.objective_function_1.calculate_score = Mock(return_value=fake.pyfloat(positive=True))

        self.objective_function_2: ObjectiveFunction[str, str, Model[str, str]] = MagicMock(spec=ObjectiveFunction)
        self.objective_function_2.calculate_score = Mock(return_value=fake.pyfloat(positive=True))

        self.dataset: Dataset[Tuple[str, str]] = Mock()
        self.dataset.__getitem__ = Mock(return_value=random.choice(self.samples))
        self.dataset.__len__ = Mock(return_value=self.samples.__len__())

        self.event_loop = asyncio.get_event_loop()

        self.training_service: BatchTrainingService[str, str, Model[str, str]] = BatchTrainingService[str, str, Model[str, str]](train_hook=lambda w, x, y, z: x, event_loop=self.event_loop)

    def tearDown(self):
        pass

    def test_train_valid_objectives_and_dataset_should_return_trained_model(self):
        evaluation_routine: Coroutine[Any, Any, Model[str, str]] = self.training_service.train(self.model, self.dataset, {}, 
                    {'objective 1': self.objective_function_1, 'objective 2': self.objective_function_2}, None)

        trained_model: Model[str, str] = self.event_loop.run_until_complete(evaluation_routine)

    def test_train_on_multiple_datasets_valid_objectives_and_datasets_should_return_trained_model(self):
        datasets: Dict[str, Dataset[Tuple[str, str]]] = {"set_1": self.dataset, "set_2": self.dataset}

        evaluation_routine: Coroutine[Any, Any, Model[str, str]] = self.training_service.train_on_multiple_datasets(self.model, datasets, {},
            {'objective 1': self.objective_function_1, 'objective 2': self.objective_function_2}, None)

        trained_model: Model[str, str] = self.event_loop.run_until_complete(evaluation_routine)