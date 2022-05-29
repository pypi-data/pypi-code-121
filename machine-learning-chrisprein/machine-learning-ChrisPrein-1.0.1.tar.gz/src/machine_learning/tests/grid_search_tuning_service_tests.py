import asyncio
import unittest
from unittest.mock import Mock, patch
from torch.utils.data import Dataset
from typing import Any, Coroutine, List, Dict, Tuple
from faker import Faker
import random

from ..evaluation.abstractions.evaluation_metric import EvaluationContext
from ..parameter_tuning.abstractions.model_factory import ModelFactory
from ..parameter_tuning.abstractions.objective_function import ObjectiveFunction
from ..parameter_tuning.grid_search_tuning_service import GridSearchTuningService
from ..evaluation.multi_task_evaluation_service import MultiTaskEvaluationService
from ..modeling.abstractions.model import Model, TInput, TTarget

class GridSearchTuningServiceTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.samples: List[Tuple[float, float]] = [(fake.pyfloat(positive=True), fake.pyfloat(positive=True)) for i in range(10)]

        self.parameter_tuning_service: GridSearchTuningService[float, float] = GridSearchTuningService[float, float](folds=5)

        self.event_loop = asyncio.get_event_loop()

        self.model_patcher = patch('machine_learning.modeling.abstractions.model.Model', new=Model[float, float])

        model: Model[float, float] = self.model_patcher.start()

        model.predict_batch = Mock(return_value=[fake.pyfloat(positive=True) for i in range(10)])
        model.train = lambda X, y: None
        model.predict = lambda X: fake.pyfloat(positive=True)
        model.__init__ = Mock(return_value=None)
        # model.__class__ = Model[float, float]
        model.__class__.__init__ = lambda x, y: None

        self.model_factory_patcher = patch('machine_learning.parameter_tuning.abstractions.model_factory.ModelFactory')

        self.model_factory: ModelFactory[Model[float, float]] = self.model_factory_patcher.start()
        self.model_factory.create = lambda x: model

        self.dataset_patcher = patch('torch.utils.data.Dataset')

        self.dataset: Dataset[Tuple[float, float]] = self.dataset_patcher.start()
        self.dataset.__getitem__ = lambda x, y: random.choice(self.samples)#Mock(return_value=random.choice([(fake.pyfloat(positive=True), fake.pyfloat(positive=True)) for i in range(10)]))
        self.dataset.__iter__ = lambda x: self.samples.__iter__()#Mock(return_value=[(fake.pyfloat(positive=True), fake.pyfloat(positive=True)) for i in range(10)].__iter__())
        self.dataset.__len__ = lambda : self.samples.__len__()#Mock(return_value=[(fake.pyfloat(positive=True), fake.pyfloat(positive=True)) for i in range(10)].__len__())

        self.objective_function_patcher = patch('machine_learning.parameter_tuning.abstractions.objective_function.ObjectiveFunction')

        self.objective_function: ObjectiveFunction[float, float, Model[float, float]] = self.objective_function_patcher.start()

        self.objective_function.calculate_score = Mock(return_value=fake.pyfloat(positive=True))

    def tearDown(self):
        self.model_patcher.stop()
        self.model_factory_patcher.stop()
        self.dataset_patcher.stop()
        self.objective_function_patcher.stop()

    def test_search_valid_params_should_return_best_params(self):
        search_routine: Coroutine[Any, Any, Dict[str, Any]] = self.parameter_tuning_service.search(model_factory=self.model_factory, params={}, dataset=self.dataset, objective_functions={'test': self.objective_function}, primary_objective='test')

        result: Dict[str, Any] = self.event_loop.run_until_complete(search_routine)