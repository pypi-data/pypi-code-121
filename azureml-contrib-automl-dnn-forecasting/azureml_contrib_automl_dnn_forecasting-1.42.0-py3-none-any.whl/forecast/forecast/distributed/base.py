import abc
from typing import List, Optional, Sequence
from typing_extensions import Protocol

import torch.cuda

from forecast.callbacks import Callback


class Communicator(Protocol):
    def allgather(self, t: torch.Tensor) -> torch.Tensor:
        pass

    def allreduce(self, t: torch.Tensor) -> torch.Tensor:
        pass


class DistributionStrategy(abc.ABC):
    def __init__(self, *, set_device: bool = True):
        self._set_device = set_device
        if self._set_device and torch.cuda.is_available():
            torch.cuda.set_device(self.local_rank())

    @abc.abstractmethod
    def get_callback(self) -> Optional[Callback]:
        raise NotImplementedError

    @abc.abstractmethod
    def filter_callbacks(self, callbacks: Sequence[Callback]) -> List[Callback]:
        raise NotImplementedError

    @abc.abstractmethod
    def size(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def rank(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def local_rank(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def communicator(self) -> Communicator:
        pass
