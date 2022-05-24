# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Union

import torch
from carton.collections import flatten_dict
from ignite.metrics import Metric
from ignite.metrics.metric import reinit__is_reduced, sync_all_reduce

from texi.metrics import prf1


class NerMetrics(Metric):
    def __init__(
        self,
        entity_index2label: Mapping,
        negative_entity_index: int,
        prefix: str = "",
        output_transform: Callable = lambda x: x,
        device: Union[str, torch.device] = torch.device("cpu"),
    ):
        self.entity_index2label = entity_index2label
        self.negative_entity_index = negative_entity_index
        self.prefix = prefix

        super().__init__(output_transform, device=device)

    @reinit__is_reduced
    def reset(self) -> None:
        # TP, FP, FN
        self.tpfpfn = torch.zeros((3,), device=self._device)
        self.typed_tpfpfn = torch.zeros(
            (len(self.entity_index2label), 3), device=self._device
        )

    @reinit__is_reduced
    def update(self, output: tuple[Mapping, Mapping]) -> None:
        def _combine_span_and_label(y):
            # label: [B, E]
            # span: [B, E, 2]
            # mask: [B, E]
            labeled_span = torch.cat([y["label"].unsqueeze(dim=-1), y["span"]], axis=-1)
            negative_mask = ~y["mask"].unsqueeze(dim=-1).bool()
            labeled_span.masked_fill_(negative_mask, self.negative_entity_index)

            return labeled_span

        def _update(y, y_pred, stat, index=None):
            # y: [B, E1, 3]
            # y_pred: [B, E2, 3]

            if index is not None:
                y_mask = y[..., 0] == index
                y_pred_mask = y_pred[..., 0] == index
            else:
                y_mask = y[..., 0] != self.negative_entity_index
                y_pred_mask = y_pred[..., 0] != self.negative_entity_index

            # For each entity in `y`, compare it to all entities in
            # `y_pred`.
            # matrix: [B, E1, E2, 3]
            matrix = y.unsqueeze(dim=2) == y_pred.unsqueeze(dim=1)

            # A TP means:
            # 1. All fields (label, start, end) must match -> `.all()`.
            # 2. For each entity in `y`, check if any entity in `y_pred`
            #    matches it -> `.any()`.
            # tp: [B, E1, E2] -> [B, E1] -> [0]
            tp = matrix.all(dim=-1).any(dim=-1).masked_fill(~y_mask, 0).sum()
            fp = y_pred_mask.sum() - tp
            fn = y_mask.sum() - tp

            stat[0] += tp.to(self._device)
            stat[1] += fp.to(self._device)
            stat[2] += fn.to(self._device)

        y_pred, y = output
        y_pred = {k: v.detach() for k, v in y_pred.items()}
        y = {k: v.detach() for k, v in y.items()}

        y = _combine_span_and_label(y)
        y_pred = _combine_span_and_label(y_pred)

        _update(y, y_pred, self.tpfpfn)
        for i in range(len(self.entity_index2label)):
            if i != self.negative_entity_index:
                _update(y, y_pred, self.typed_tpfpfn[i], i)

    @sync_all_reduce("tpfpfn:SUM", "typed_tpfpfn:SUM")
    def compute(self) -> dict[str, float]:
        metrics = prf1(self.tpfpfn[0], self.tpfpfn[1], self.tpfpfn[2])
        typed_metrics = {
            self.entity_index2label[i]: prf1(
                self.typed_tpfpfn[i][0],
                self.typed_tpfpfn[i][1],
                self.typed_tpfpfn[i][2],
            )
            for i in range(len(self.entity_index2label))
            if i != self.negative_entity_index
        }

        macros = {
            key: sum(typed_metrics[type_][key] for type_ in typed_metrics)
            / len(typed_metrics)
            for key in ["precision", "recall", "f1"]
        }

        outputs = {"micro": metrics, "macro": macros, **typed_metrics}
        outputs = flatten_dict(outputs, ".")
        if self.prefix:
            outputs = {f"{self.prefix}.{k}": v for k, v in outputs.items()}

        return outputs  # type: ignore
