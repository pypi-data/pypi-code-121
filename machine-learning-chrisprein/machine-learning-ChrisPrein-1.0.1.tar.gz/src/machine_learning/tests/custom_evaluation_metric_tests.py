import unittest
from unittest.mock import Mock, PropertyMock, patch
from typing import Any, Coroutine, List, Dict, Tuple
from faker import Faker

from ..evaluation.custom_evaluation_metric import CustomEvaluationMetric
from ..evaluation.abstractions.evaluation_metric import EvaluationContext, Prediction, TTarget, TModel, TInput
from ..modeling.abstractions.model import Model

def accuracy(context: EvaluationContext[float, float, Model[float, float]]) -> float:
    predictions: List[float] = [prediction.prediction for prediction in context.predictions]
    targets: List[float] = [prediction.target for prediction in context.predictions]
    number_samples: int = len(predictions)

    return (predictions == targets) / number_samples

class CustomEvaluationMetricTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.evaluation_context_patcher = patch('machine_learning.evaluation.abstractions.evaluation_metric.EvaluationContext', new=EvaluationContext[float, float, Model[float, float]])

        self.evaluation_context: EvaluationContext[float, float, Model[float, float]] = self.evaluation_context_patcher.start()

        self.evaluation_context.predictions = PropertyMock(return_value=[Prediction[float, float](fake.pyfloat(positive=True), fake.pyfloat(positive=True), fake.pyfloat(positive=True)) for i in range(10)])

    def tearDown(self):
        self.evaluation_context_patcher.stop()

    def test_calculate_score_valid_predictions_should_return_accuracy_score(self):
        accuracy_metric: CustomEvaluationMetric[float, float, Model[float, float]] = CustomEvaluationMetric[float, float, Model[float, float]](expression=accuracy)

        assert accuracy_metric.calculate_score(self.evaluation_context) == accuracy(self.evaluation_context)