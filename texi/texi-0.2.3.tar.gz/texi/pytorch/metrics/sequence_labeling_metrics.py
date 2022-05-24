# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Sequence
from typing import Optional, Union

import torch
from ignite.exceptions import NotComputableError
from ignite.metrics import Metric
from ignite.metrics.metric import reinit__is_reduced, sync_all_reduce

from texi.apps.ner import conlleval
from texi.metrics import confusion_matrix


class SequenceLabelingMetrics(Metric):
    _required_output_keys = ("x", "y", "y_pred")

    def __init__(
        self,
        labels: Iterable[str],
        output_transform: Callable = lambda x: x,
        device: Optional[Union[str, torch.device]] = None,
    ):
        super().__init__(output_transform, device=device)
        self.labels = list(labels)

    @reinit__is_reduced
    def reset(self) -> None:
        self._x = []  # type: list[list[str]]
        self._y = []  # type: list[list[str]]
        self._y_pred = []  # type: list[list[str]]

    @reinit__is_reduced
    def update(self, output: Sequence) -> None:
        x, y, y_pred = output
        self._x += x
        self._y += y
        self._y_pred += y_pred

    @sync_all_reduce("_x", "_y_pred", "_y")
    def compute(self) -> dict:
        if not self._x:
            raise NotComputableError(
                "SequenceLabelingMetrics must have at"
                "least one example before it can be computed."
            )

        output = conlleval(zip(self._x, self._y, self._y_pred))
        metrics = {**output["metrics"]}
        for tag, tag_metrics in output["tags"].items():
            for tag_metric, value in tag_metrics.items():
                metrics["_".join([tag, tag_metric])] = value

        y = [*itertools.chain.from_iterable(self._y)]
        y_pred = [*itertools.chain.from_iterable(self._y_pred)]

        metrics["confusion"] = confusion_matrix(y, y_pred, labels=self.labels)

        return metrics
