# -*- coding: utf-8 -*-

import collections

import numpy as np
import torch
from ignite.exceptions import NotComputableError
from ignite.metrics import Metric
from ignite.metrics.metric import reinit__is_reduced, sync_all_reduce


class GeneralAccuracy(Metric):
    @reinit__is_reduced
    def reset(self):
        self._num_correct = torch.tensor(0, device=self._device)
        self._num_examples = 0
        super().reset()

    @reinit__is_reduced
    def update(self, output):
        y_pred, y = output

        if type(y_pred) is not type(y):
            raise TypeError("`y_pred` and `y` should have same type")

        if isinstance(y, torch.Tensor):
            y_pred, y = y_pred.detach(), y.detach()
            self._num_correct += (y_pred == y).sum()
            self._num_examples += y.size(0)

        elif isinstance(y, np.ndarray):
            self._num_correct += (y_pred == y).sum()
            self._num_examples += y.shape[0]

        elif isinstance(y, collections.abc.Sized):
            self._num_correct += sum(yi_pred == yi for yi_pred, yi in zip(y_pred, y))
            self._num_examples += len(y)
        else:
            raise ValueError(
                "Both `y_pred` and `y` should be instance of `torch.Tensor` or "
                "`numpy.ndarray` or `collections.abc.Size`"
            )

    @sync_all_reduce("_num_examples", "_num_correct")
    def compute(self):
        if self._num_examples == 0:
            raise NotComputableError(
                (
                    "GeneralAccuracy must have at least one example "
                    "before it can be computed."
                )
            )
        return self._num_correct.item() / self._num_examples
