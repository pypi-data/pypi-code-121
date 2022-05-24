import operator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union

import torch
import torch.nn as nn

from .._typing import FilePath

__all__ = ["Checkpoint"]


@dataclass(order=True)
class Item:
    priority: Union[int, float]
    filename: str = field(compare=False)


class PriorityQueue:
    def __init__(self, *, capacity: int = 1, reverse: bool = False) -> None:
        if capacity < 1:
            raise ValueError(f"require capacity >= 1, got {capacity!r}")

        self._queue: List[Item] = []
        self._capacity = capacity
        self._reverse = reverse

        if reverse:
            self._cmp = operator.gt
        else:
            self._cmp = operator.lt

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def capacity(self) -> int:
        return self._capacity

    def check_priority(self, priority: Union[int, float]) -> bool:
        if len(self) < self.capacity:
            return True
        return self._cmp(priority, self._queue[-1].priority)

    def update(self, priority: Union[int, float], filename: str) -> Optional[Item]:
        last = None
        if len(self) == self.capacity:
            last = self.pop()
        self.push(priority, filename)
        return last

    def push(self, priority: Union[int, float], filename: str) -> None:
        if len(self) == self.capacity:
            raise ValueError("queue is full")
        item = Item(priority, filename)
        self._queue.append(item)
        self._queue.sort(reverse=self._reverse)

    def pop(self) -> Item:
        if not self:
            raise ValueError("queue is empty")
        return self._queue.pop()


class Checkpoint:
    def __init__(self, root: FilePath, filename_prefix: str, max_save: int = 1, reverse: bool = False) -> None:
        self.root = Path(root)
        self.filename_prefix = filename_prefix
        self.max_save = max_save
        self.queue = PriorityQueue(capacity=max_save, reverse=reverse)

        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        check_dict: Mapping[str, Any],
        metric_name: str,
        metric_value: Union[int, float],
        global_step: Optional[int] = None,
    ) -> None:
        if not self.queue.check_priority(metric_value):
            return

        filename = self.filename_prefix
        if global_step is not None:
            filename += f"_{global_step}"
        if isinstance(metric_value, int):
            filename += f"_{metric_name}={metric_value}.pt"
        else:
            filename += f"_{metric_name}={metric_value:.4f}.pt"

        state_dict = {}
        for key, obj in check_dict.items():
            if isinstance(obj, (nn.DataParallel, nn.parallel.DistributedDataParallel)):
                obj = obj.module
            state_dict[key] = obj.state_dict()
        torch.save(state_dict, self.root / filename)

        old = self.queue.update(metric_value, filename)
        if old is not None:
            oldpath = self.root / old.filename
            oldpath.unlink(missing_ok=True)

    @staticmethod
    def load(check_dict: Mapping[str, Any], filepath: FilePath, map_location: Any = None) -> None:
        state_dict = torch.load(filepath, map_location=map_location)
        for key, obj in check_dict.items():
            if key not in state_dict:
                raise ValueError(f"{key} does not exist")
            if isinstance(obj, (nn.DataParallel, nn.parallel.DistributedDataParallel)):
                obj = obj.module
            obj.load_state_dict(state_dict[key])
