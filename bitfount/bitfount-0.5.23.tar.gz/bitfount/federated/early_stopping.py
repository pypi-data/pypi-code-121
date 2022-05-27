"""Federated early stopping."""
from dataclasses import dataclass
from typing import Dict, List

from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger(__name__)


@dataclass
class FederatedEarlyStopping:
    """Describes a criterion for early stopping of federated model training.

    This is only applicable in the federated context where a Modeller is retrieving
    validation results from multiple workers over a training job and wants to signal
    to the workers to stop training if results are getting worse. Models already have
    their own local early stopping which is separate.

    Args:
        metric: the metric whose value is checked every iteration. Must be one
            of the metrics that is calculated by the model
        patience: number of iterations of worsening values before training is
            stopped
        delta: how much the metric needs to improve by each iteration to count
            as an improvement
    """

    metric: str
    patience: int
    delta: float

    def __post_init__(self) -> None:
        self.counter: int = 0

    def check(self, results: List[Dict[str, float]]) -> bool:
        """Checks if early stopping criteria has been met.

        Args:
            results: List of metrics

        Returns:
            True if the model training should stop training early, otherwise False.
        """
        num_results = len(results)
        if self.metric not in results[0]:
            logger.warning(
                f"Early stopping ignored. Metric {self.metric} not reported by model."
            )
        elif num_results > 1:
            one_epoch_metric_diff = results[-1][self.metric] - results[-2][self.metric]
            patience_index = -1 - self.patience if num_results > self.patience else 0
            patience_metric_diff = (
                results[-1][self.metric] - results[patience_index][self.metric]
            )
            if "loss" in self.metric:
                one_epoch_metric_diff = -one_epoch_metric_diff
                patience_metric_diff = -patience_metric_diff

            if one_epoch_metric_diff < self.delta:
                self.counter += 1
            elif patience_metric_diff >= self.delta:
                # noinspection PyAttributeOutsideInit
                #   defined in __post_init__
                self.counter = 0

        return self.counter > self.patience
