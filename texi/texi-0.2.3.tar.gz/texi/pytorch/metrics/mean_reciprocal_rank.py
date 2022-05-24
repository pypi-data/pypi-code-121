# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Optional, Union

import torch
import torch.nn.functional as F
from ignite.exceptions import NotComputableError
from ignite.metrics import Metric
from ignite.metrics.metric import reinit__is_reduced, sync_all_reduce


class MeanReciprocalRank(Metric):
    def __init__(
        self,
        output_transform: Callable = lambda x: x,
        device: Optional[Union[str, torch.device]] = None,
    ):
        super().__init__(output_transform, device=device)

    @reinit__is_reduced
    def reset(self) -> None:
        self._ranks = []  # type: list[torch.Tensor]

    @reinit__is_reduced
    def update(self, output: Sequence) -> None:
        y_pred, y = output
        if y.dim() == 1:
            y = F.one_hot(y, num_classes=y_pred.size()[1])
        ranks = y_pred.argsort(dim=-1, descending=True).argsort(dim=-1)
        rank = ranks.masked_select(y > 0).float()
        self._ranks += [1 / (rank + 1)]

    @sync_all_reduce("_ranks")
    def compute(self) -> Union[float, torch.Tensor]:
        if self._num_examples == 0:
            raise NotComputableError(
                "MeanReciprocalRank must have at"
                "least one example before it can be computed."
            )

        return torch.mean(torch.cat(self._ranks, dim=0)).item()
