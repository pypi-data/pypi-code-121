import unittest
from typing import Any, Callable, Coroutine, List, Dict, Tuple, Type

from ..modeling.abstractions.model import Model
from ..experimentation.default_instance_factory import DefaultInstanceFactory
from ..evaluation.abstractions.evaluation_service import EvaluationService
from ..evaluation.multi_task_evaluation_service import MultiTaskEvaluationService
from ..experimentation.abstractions.machine_learning_experimentation_service import InstanceSettings

EvaluationServiceAlias = MultiTaskEvaluationService[float, float, Model[float, float]]

class DefaultInstanceFactoryTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_one_type_available_should_return_valid_instance(self):
        available_types: Dict[str, Type[EvaluationService[float, float, Model[float, float]]]] = {'multi_task_evaluation_service': EvaluationServiceAlias}

        default_instance_factory: DefaultInstanceFactory[EvaluationService[float, float, Model[float, float]]] = DefaultInstanceFactory[EvaluationService[float, float, Model[float, float]]](available_types=available_types)

        default_instance_settings: InstanceSettings = InstanceSettings(name="multi_task_evaluation_service", params={"batch_size": 10})

        instance: EvaluationService[float, float, Model[float, float]] = default_instance_factory.create(default_instance_settings)

        assert isinstance(instance, MultiTaskEvaluationService) 

    def test_create_one_factory_function_available_should_return_valid_instance(self):
        available_types: Dict[str, Callable[[InstanceSettings], EvaluationService[float, float, Model[float, float]]]] = {'multi_task_evaluation_service': lambda **params: EvaluationServiceAlias(**params)}

        default_instance_factory: DefaultInstanceFactory[EvaluationService[float, float, Model[float, float]]] = DefaultInstanceFactory[EvaluationService[float, float, Model[float, float]]](available_types=available_types)

        default_instance_settings: InstanceSettings = InstanceSettings(name="multi_task_evaluation_service", params={"batch_size": 10})

        instance: EvaluationService[float, float, Model[float, float]] = default_instance_factory.create(default_instance_settings)

        assert isinstance(instance, MultiTaskEvaluationService) 