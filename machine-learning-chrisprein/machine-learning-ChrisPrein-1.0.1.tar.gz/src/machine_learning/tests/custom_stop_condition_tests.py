import unittest
from unittest.mock import Mock, PropertyMock, patch
from typing import Any, Coroutine, List, Dict, Tuple
from faker import Faker

from ..evaluation.custom_evaluation_metric import CustomEvaluationMetric
from ..evaluation.abstractions.evaluation_metric import EvaluationContext, Prediction, TTarget, TModel, TInput
from ..training.abstractions.stop_condition import TrainingContext, StopCondition
from ..training.custom_stop_condition import CustomStopCondition
from ..modeling.abstractions.model import Model

class CustomStopConditionTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.training_context_patcher = patch('machine_learning.training.abstractions.stop_condition.TrainingContext', new=TrainingContext[float, float, Model[float, float]])

        self.training_context: TrainingContext[float, float, Model[float, float]] = self.training_context_patcher.start()

    def tearDown(self):
        self.training_context_patcher.stop()

    def test_is_satisfied_should_return_true(self):
        stop_condition: StopCondition[TInput, TTarget, Model[float, float]] = CustomStopCondition[float, float, Model[float, float]](expression=lambda x: True)

        assert stop_condition.is_satisfied(self.training_context)