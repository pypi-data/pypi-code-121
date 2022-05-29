import unittest
from unittest.mock import Mock, PropertyMock, patch
from faker import Faker

from ..parameter_tuning.custom_model_factory import CustomModelFactory
from ..modeling.abstractions.model import Model

class CustomModelFactoryTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.model_patcher = patch('machine_learning.modeling.abstractions.model', new=Model[float, float])

        self.model: Model[float, float] = self.model_patcher.start()

    def tearDown(self):
        self.model_patcher.stop()

    def test_create_valid_params_should_return_model_instance(self):
        model_factory: CustomModelFactory[Model[float, float]] = CustomModelFactory[Model[float, float]](expression=lambda params: self.model)

        model = model_factory.create({})

        assert not model is None