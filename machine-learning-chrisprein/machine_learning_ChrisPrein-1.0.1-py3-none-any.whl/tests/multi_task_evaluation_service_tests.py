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

class MultiTaskEvaluationServiceTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.samples: List[Tuple[str, str]] = [(fake.first_name(), fake.last_name()) for i in range(10)]

        self.model: Model[str, str] = MagicMock(spec=Model)

        self.model.predict_batch = Mock(return_value=[fake.last_name() for i in range(10)])

        self.evaluation_metric_1: EvaluationMetric[str, str, Model[str, str]] = MagicMock(spec=EvaluationMetric)

        self.evaluation_metric_1.calculate_score = Mock(return_value=fake.pyfloat(positive=True))

        self.evaluation_metric_2: EvaluationMetric[str, str, Model[str, str]] = MagicMock(spec=EvaluationMetric)

        self.evaluation_metric_2.calculate_score = Mock(return_value=fake.pyfloat(positive=True))

        self.dataset: Dataset[Tuple[str, str]] = Mock()
        self.dataset.__getitem__ = Mock(return_value=random.choice(self.samples))
        self.dataset.__len__ = Mock(return_value=self.samples.__len__())

        self.event_loop = asyncio.get_event_loop()

        self.evaluation_service: MultiTaskEvaluationService[str, str, Model[str, str]] = MultiTaskEvaluationService[str, str, Model[str, str]](event_loop=self.event_loop)

    def tearDown(self):
        pass

    def test_evaluate_valid_model_metrics_and_dataset_should_return_results_for_each_metric(self):
        evaluation_routine: Coroutine[Any, Any, Dict[str, float]] = self.evaluation_service.evaluate(self.model, self.dataset, 
                    {'metric 1': self.evaluation_metric_1, 'metric 2': self.evaluation_metric_2})

        result: Dict[str, float] = self.event_loop.run_until_complete(evaluation_routine)

        assert len(result.items()) == 2

    def test_evaluation_on_multiple_datasets_valid_model_metrics_and_datasets_should_return_results_for_each_metric_on_each_dataset(self):
        datasets: Dict[str, Dataset[Tuple[str, str]]] = {"set_1": self.dataset, "set_2": self.dataset}

        evaluation_routine: Coroutine[Any, Any, Dict[str, Dict[str, float]]] = self.evaluation_service.evaluate_on_multiple_datasets(self.model, datasets, 
            {'metric 1': self.evaluation_metric_1, 'metric 2': self.evaluation_metric_2})

        result: Dict[str, Dict[str, float]] = self.event_loop.run_until_complete(evaluation_routine)

        assert len(result.items()) == 2