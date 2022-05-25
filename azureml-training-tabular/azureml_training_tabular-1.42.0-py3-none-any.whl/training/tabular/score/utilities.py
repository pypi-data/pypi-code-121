# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
from typing import Dict, Tuple

import numpy as np

from . import constants


def get_all_nan(task: str) -> Dict[str, float]:
    """Create a dictionary of metrics to values for the given task.

    All metric values are set to nan initially
    :param task: one of constants.Tasks.
    :return: returns a dictionary of nans for each metric for the task.
    """
    return {m: np.nan for m in constants.METRICS_TASK_MAP[task]}


def get_metric_ranges(task: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Get the metric range for the task.

    :param task: Machine learning task.
    :return: Tuple with dictionaries of minimum and maximum scores.
    """
    minimums = get_min_values(task)
    maximums = get_max_values(task)
    return minimums, maximums


def get_worst_values(task: str) -> Dict[str, float]:
    """
    Get the worst possible scores for metrics of the task.

    :param task: Machine learning task.
    :return: Dictionary from metric names to the worst scores.
    """
    minimums, maximums = get_metric_ranges(task)
    task_objectives = constants.OBJECTIVES_TASK_MAP[task]

    worst_scores = dict()
    for metric_name, objective in task_objectives.items():
        if metric_name == constants.TRAIN_TIME:
            worst_scores[metric_name] = constants.SCORE_UPPER_BOUND
            continue

        if objective == constants.MAXIMIZE:
            worst_scores[metric_name] = minimums[metric_name]
        else:
            worst_scores[metric_name] = maximums[metric_name]
    return worst_scores


def get_min_values(task: str) -> Dict[str, float]:
    """Get the minimum values for metrics for the task.

    :param task: string "classification" or "regression"
    :return: returns a dictionary of metrics with the min values.
    """
    task_ranges = constants.RANGES_TASK_MAP[task]  # type: Dict[str, Tuple[float, float]]
    return {metric_name: lower for metric_name, (lower, _) in task_ranges.items()}


def get_max_values(task: str) -> Dict[str, float]:
    """
    Get the maximum scores for metrics of the task.

    :param task: Machine learning task.
    :return: Dictionary of metrics with the maximum scores.
    """
    task_ranges = constants.RANGES_TASK_MAP[task]  # type: Dict[str, Tuple[float, float]]
    return {metric_name: upper for metric_name, (_, upper) in task_ranges.items()}


def is_scalar(metric_name: str) -> bool:
    """
    Check whether a given metric is scalar or nonscalar.

    :param metric_name: the name of the metric found in constants.py
    :return: boolean for if the metric is scalar
    """
    if metric_name in constants.FULL_SCALAR_SET or metric_name in constants.CLASSIFICATION_MULTILABEL_SET:
        return True
    elif metric_name in constants.FULL_NONSCALAR_SET:
        return False
    elif metric_name in constants.CLASSIFICATION_CLASSWISE_SET:
        return False
    raise NotImplementedError


def is_classwise(metric_name: str) -> bool:
    """
    Check whether a given metric is a classwise metric.

    :param metric_name: the name of the metric found in constants.py
    :return: boolean for if the metric is scalar
    """
    return metric_name in constants.CLASSIFICATION_CLASSWISE_SET
