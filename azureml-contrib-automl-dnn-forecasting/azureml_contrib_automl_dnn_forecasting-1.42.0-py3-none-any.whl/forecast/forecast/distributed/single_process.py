from typing import Optional, Sequence, List

import torch

from forecast.callbacks import Callback
from forecast.distributed import DistributionStrategy
from forecast.distributed.base import Communicator


class _NullCommunicator:
    def allgather(self, t: torch.Tensor) -> torch.Tensor:
        return t

    def allreduce(self, t: torch.Tensor) -> torch.Tensor:
        return t


class SingleProcessDistributionStrategy(DistributionStrategy):
    def __init__(self, *, set_device: bool = True):
        super().__init__(set_device=set_device)
        self._communicator = _NullCommunicator()

    def get_callback(self, set_device: bool = True) -> Optional[Callback]:
        return None

    def filter_callbacks(self, callbacks: Sequence[Callback]) -> List[Callback]:
        return list(callbacks)

    def size(self) -> int:
        return 1

    def rank(self) -> int:
        return 0

    def local_rank(self) -> int:
        return 0

    @property
    def communicator(self) -> Communicator:
        return self._communicator
