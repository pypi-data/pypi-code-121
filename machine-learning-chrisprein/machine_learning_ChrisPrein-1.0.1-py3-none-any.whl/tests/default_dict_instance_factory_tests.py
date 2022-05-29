import unittest
from typing import Any, Callable, Coroutine, List, Dict, Tuple, Type

from torch import isin

from ..modeling.abstractions.model import Model
from ..experimentation.default_dict_instance_factory import DefaultDictInstanceFactory
from ..evaluation.abstractions.evaluation_service import EvaluationService
from ..evaluation.multi_task_evaluation_service import MultiTaskEvaluationService
from ..evaluation.abstractions.evaluation_metric import EvaluationMetric
from ..evaluation.custom_evaluation_metric import CustomEvaluationMetric
from ..experimentation.abstractions.machine_learning_experimentation_service import InstanceSettings

CustomEvaluationMetricAlias = CustomEvaluationMetric[float, float, Model[float, float]]

class DefaultDictInstanceFactoryTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_multiple_factory_function_available_should_return_valid_instances(self):
        available_types: Dict[str, Type[EvaluationMetric[float, float, Model[float, float]]]] = {'metric_1': lambda **params: CustomEvaluationMetricAlias(lambda x: 1), 'metric_2': lambda **params: CustomEvaluationMetricAlias(lambda x: 0.5)}

        default_instance_factory: DefaultDictInstanceFactory[EvaluationMetric[float, float, Model[float, float]]] = DefaultDictInstanceFactory[EvaluationMetric[float, float, Model[float, float]]](available_types=available_types)

        default_instance_settings: Dict[str, InstanceSettings] = {'metric_1': InstanceSettings(name="metric_1", params={}), 'metric_2': InstanceSettings(name="metric_2", params={})}

        instances: Dict[str, EvaluationMetric[float, float, Model[float, float]]] = default_instance_factory.create(default_instance_settings)

        assert "metric_1" in instances.keys()
        assert "metric_2" in instances.keys()
        assert isinstance(instances["metric_1"], CustomEvaluationMetric)
        assert isinstance(instances["metric_2"], CustomEvaluationMetric)