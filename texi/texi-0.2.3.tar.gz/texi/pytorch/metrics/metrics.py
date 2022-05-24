# -*- coding: utf-8 -*-

import torch
from ignite.metrics import Accuracy, Fbeta, Precision, Recall, TopKCategoricalAccuracy

from texi.pytorch.metrics.mean_reciprocal_rank import MeanReciprocalRank
from texi.pytorch.metrics.sequence_labeling_metrics import SequenceLabelingMetrics


def classification_metrics(output_transform, train=True):
    if train:
        return {"accuracy": Accuracy(output_transform=output_transform)}

    metrics = {}
    precision = Precision(output_transform=output_transform, average=False)
    recall = Recall(output_transform=output_transform, average=False)
    metrics["accuracy"] = Accuracy(output_transform=output_transform)
    metrics["precision"] = precision
    metrics["recall"] = recall
    metrics["f1"] = Fbeta(
        1.0,
        average=False,
        precision=precision,
        recall=recall,
    )

    return metrics


def ranking_metrics(output_transform, train=True):
    if train:
        return {}

    metrics = {
        "mean_reciprocal_rank": MeanReciprocalRank(output_transform=output_transform)
    }
    for k in [1, 3, 5]:
        metrics[f"top{k}_accuracy"] = TopKCategoricalAccuracy(
            k=k, output_transform=output_transform
        )

    return metrics


def sequence_labeling_metrics(output_transform, labels, train=True):
    if train:
        return {}

    def _output_transform_for_confusion_matrix(output):
        x, y, logits = output
        output_y, output_y_pred = [], []
        for length, yi, y_predi in zip(x["length"], y, logits):
            output_y += [yi[:length]]
            output_y_pred += [y_predi[:length]]
        output_y = torch.cat(output_y, dim=0)
        output_y_pred = torch.cat(output_y_pred, dim=0)

        return output_y_pred, output_y

    metrics = {
        "sequence_labeling_metrics": SequenceLabelingMetrics(labels, output_transform),
    }

    return metrics


def question_answering_metrics(output_transform, train=True):
    if train:
        return {}

    metrics = {}

    return metrics
