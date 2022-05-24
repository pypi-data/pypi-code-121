# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Union

import torch
from carton.collections import flatten_dict
from ignite.metrics import Metric
from ignite.metrics.metric import reinit__is_reduced, sync_all_reduce

from texi.metrics import prf1


class ReMetrics(Metric):
    def __init__(
        self,
        relation_index2label: Mapping,
        negative_relation_index: int,
        relation_filter_threshold: float,
        prefix: str = "",
        output_transform: Callable = lambda x: x,
        device: Union[str, torch.device] = torch.device("cpu"),
    ):
        self.relation_index2label = relation_index2label
        self.negative_relation_index = negative_relation_index
        self.relation_filter_threshold = relation_filter_threshold
        self.prefix = prefix

        super().__init__(output_transform, device=device)

    @reinit__is_reduced
    def reset(self) -> None:
        # TP, FP, FN
        self.tpfpfn = torch.zeros((3,), device=self._device)
        self.typed_tpfpfn = torch.zeros(
            (len(self.relation_index2label), 3), device=self._device
        )

    @reinit__is_reduced
    def update(self, output: tuple[Mapping, Mapping]) -> None:
        def _expand_entities(y):
            # Expand head/tail index by corresponding entity type and span.

            # label: [B, R, R']
            # pair: [B, R, 2]
            # mask: [B, R]
            label = (y["label"] > self.relation_filter_threshold).long()

            batch_size = y["label"].size(0)
            indices = torch.arange(batch_size).view(batch_size, 1, 1)

            # entity_span: [B, R, 4]
            # entity_label: [B, R, 2]
            # entity: [B, R, 6]
            entity_span = y["entity_span"][indices, y["pair"]].flatten(start_dim=-2)
            entity_label = y["entity_label"][indices, y["pair"]]
            entity = torch.cat([entity_span, entity_label], dim=-1)

            return {
                "label": label,
                "entity": entity,
                "mask": y["mask"],
            }

        def _update(y, y_pred, stat, index=None):
            # Compare head/tail entity for each relation. Separate the
            # head/tail comparison because relation labels are assumed
            # one-hot encoded. The separation makes the following steps
            # easier.

            # Use negative/sample mask to filter non-related relations.
            num_relation_types = len(self.relation_index2label)
            negative_mask = torch.arange(num_relation_types, device=self._device)
            negative_mask = negative_mask[None, None, :]
            if index is None:
                negative_mask = negative_mask == self.negative_relation_index
            else:
                negative_mask = negative_mask != index

            def _filter_negatives(label, sample_mask):
                sample_mask = sample_mask.unsqueeze(dim=-1).bool()
                mask = negative_mask | ~sample_mask

                return label.masked_fill(mask, 0)

            y_label = _filter_negatives(y["label"], y["mask"])
            y_pred_label = _filter_negatives(y_pred["label"], y_pred["mask"])

            def _generate_relations(label, entity):
                nz = label.nonzero(as_tuple=True)
                # relation: [#R, 1 + 1 + 6]
                # where #R = numbers of non-negative relations in whole batch.
                relation = torch.cat(
                    [
                        nz[0][:, None],
                        nz[2][:, None],
                        entity[nz[:-1]],
                    ],
                    dim=-1,
                )

                return relation

            y_rel = _generate_relations(y_label, y["entity"])
            y_pred_rel = _generate_relations(y_pred_label, y_pred["entity"])

            # matrix: [#R, #R', 8]
            matrix = y_rel.unsqueeze(dim=1) == y_pred_rel.unsqueeze(dim=0)

            # tp: [#R, #R', 8] -> [#R, #R'] -> [#R] -> [0]
            tp = matrix.all(dim=-1).any(dim=-1).sum()
            fp = y_pred_label.sum() - tp
            fn = y_label.sum() - tp

            stat[0] += tp.sum().to(self._device)
            stat[1] += fp.sum().to(self._device)
            stat[2] += fn.sum().to(self._device)

        y_pred, y = output
        y_pred = {k: v.detach() for k, v in y_pred.items()}
        y = {k: v.detach() for k, v in y.items()}

        y = _expand_entities(y)
        y_pred = _expand_entities(y_pred)

        _update(y, y_pred, self.tpfpfn)
        for i in range(len(self.relation_index2label)):
            if i != self.negative_relation_index:
                _update(y, y_pred, self.typed_tpfpfn[i], i)

    @sync_all_reduce("tpfpfn:SUM", "typed_tpfpfn:SUM")
    def compute(self) -> dict[str, float]:
        metrics = prf1(self.tpfpfn[0], self.tpfpfn[1], self.tpfpfn[2])
        typed_metrics = {
            self.relation_index2label[i]: prf1(
                self.typed_tpfpfn[i][0],
                self.typed_tpfpfn[i][1],
                self.typed_tpfpfn[i][2],
            )
            for i in range(len(self.relation_index2label))
            if i != self.negative_relation_index
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
