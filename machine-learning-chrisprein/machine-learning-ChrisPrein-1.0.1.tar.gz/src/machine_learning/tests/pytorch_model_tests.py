from asyncio import coroutine
import asyncio
from dataclasses import dataclass
from re import S
import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, patch
import torch
from torch.utils.data import Dataset
from dataset_handling.dataloader import DataLoader
from typing import Any, Coroutine, List, Dict, Tuple
from faker import Faker
import random

from ..modeling.pytorch_model import PytorchModel

from torch.nn import Module
from torch.optim import Optimizer

class PytorchModelTestCase(unittest.TestCase):
    def setUp(self):
        fake = Faker()

        self.module_patcher = patch('torch.nn.Module', new=Module)
        self.optimizer_patcher = patch('torch.optim.Optimizer', new=Optimizer)
        self.loss_function_patcher = patch('torch.nn.Module', new=Module)

        self.module: Module = self.module_patcher.start()

        self.module.__init__ = Mock(return_value=None)
        self.module.train = Mock()

        self.optimizer: Optimizer = MagicMock(spec=Optimizer)

        self.optimizer.zero_grad = Mock()
        self.optimizer.step = Mock()

        self.loss_function: Module = self.loss_function_patcher.start()

        self.loss_function.__init__ = Mock(return_value=None)
        self.loss_function.backward = Mock()

        self.model: PytorchModel[float, float] = PytorchModel[float, float](pytorch_module=self.module, device=torch.device('cpu'), loss_function=self.loss_function, optimizer=self.optimizer)

        self.inputs: List[float] = [fake.pyfloat(positive=True) for i in range(10)]
        self.targets: List[float] = [fake.pyfloat(positive=True) for i in range(10)]

    def tearDown(self):
        self.module_patcher.stop()
        self.optimizer_patcher.stop()
        self.loss_function_patcher.stop()

    def test_predict_small_dataset_should_set_model_to_predict_and_call_it(self):
        self.model.predict(input=self.inputs[0])

        self.module.train.assert_called()
        self.module.__init__.assert_called()

    def test_predict_batch_small_dataset_should_set_model_to_predict_and_call_it(self):
        self.model.predict_batch(input_batch=self.inputs)

        self.module.train.assert_called()
        self.module.__init__.assert_called()