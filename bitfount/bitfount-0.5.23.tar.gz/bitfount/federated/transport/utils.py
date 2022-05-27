"""Helper module for federated transport."""
from typing import Dict, Mapping, Sequence

from numpy import mean


def _average_training_metrics(
    validation_metrics: Sequence[Mapping[str, str]]
) -> Dict[str, float]:
    """Average training metrics from each worker."""
    averaged_metrics = dict()
    if validation_metrics:
        # What should happen if one (or all) of the pods does not respond in time?
        for metric_key in validation_metrics[0]:
            averaged_metrics[metric_key] = mean(
                [
                    float(worker_metrics[metric_key])
                    for worker_metrics in validation_metrics
                ]
            )
    return averaged_metrics
