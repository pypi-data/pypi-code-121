from abc import ABC, abstractmethod
from ast import Call
from typing import Optional, TypeVar, Generic, List, Dict, Any, Callable, Union
from .abstractions.model import Model, TInput, TTarget
import torch
import torch.nn as nn

class PytorchModel(Model[TInput, TTarget]):
    def __init__(self, pytorch_module: nn.Module, device: torch.device, loss_function: nn.Module, optimizer: Union[torch.optim.Optimizer, Callable[[], torch.optim.Optimizer]], scheduler: Optional[Union[torch.optim.lr_scheduler._LRScheduler, Callable[[], torch.optim.lr_scheduler._LRScheduler]]] = None):
        self.inner_module: nn.Module = pytorch_module

        self.device: torch.device = device

        self.loss_function: nn.Module = loss_function

        self.optimizer_factory: Optional[Callable[[], torch.optim.Optimizer]] = optimizer if not isinstance(optimizer, torch.optim.Optimizer) else None
        self.scheduler_factory: Optional[Callable[[], torch.optim.lr_scheduler._LRScheduler]] = scheduler if not isinstance(scheduler, torch.optim.lr_scheduler._LRScheduler) else None

        self.optimizer: Optional[torch.optim.Optimizer] = optimizer if isinstance(optimizer, torch.optim.Optimizer) else None
        self.scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = scheduler if isinstance(scheduler, torch.optim.lr_scheduler._LRScheduler) else None

    def predict(self, input: TInput) -> TTarget:
        self.inner_module.train(False)

        return self.inner_module(input)

    def predict_batch(self, input_batch: List[TInput]) -> List[TTarget]:
        self.inner_module.train(False)

        return self.inner_module(input_batch)

    __call__ : Callable[..., Any] = predict