"""Defines functions which compute metrics."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from functools import partial
import logging
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
    cast,
)

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kstest
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

from bitfount.models.base_models import ClassifierMixIn, _BaseModel

if TYPE_CHECKING:
    from bitfount.types import DistributedModelProtocol

__all__: List[str] = [
    "BINARY_CLASSIFICATION_METRICS",
    "ClassificationMetric",
    "MULTICLASS_CLASSIFICATION_METRICS",
    "MULTILABEL_CLASSIFICATION_METRICS",
    "Metric",
    "MetricCollection",
    "MetricsProblem",
    "REGRESSION_METRICS",
    "sum_fpr_curve",
]


@dataclass
class Metric:
    """A metric used for assessing ML model performance.

    Attributes:
        func: function which computes the metric. Must take two arguments:
            y_true and y_pred and return a metric as a float.
    """

    func: Callable[[np.ndarray, np.ndarray], float]


@dataclass
class ClassificationMetric(Metric):
    """A classification metric used for assessing ML model performance.

    Args:
        probabilities: whether y_pred needs to be classes or probabilities
    """

    probabilities: bool


MULTICLASS_CLASSIFICATION_METRICS: Dict[str, Metric] = {
    "AUC": ClassificationMetric(
        partial(roc_auc_score, multi_class="ovr", average="macro"), True
    ),
    "F1": ClassificationMetric(partial(f1_score, average="macro"), False),
    "Recall": ClassificationMetric(partial(recall_score, average="macro"), False),
    "Precision": ClassificationMetric(
        partial(precision_score, average="macro", zero_division=0), False
    ),
    "Accuracy": ClassificationMetric(accuracy_score, False),
}

MULTILABEL_CLASSIFICATION_METRICS: Dict[str, Metric] = {
    "AUC": ClassificationMetric(
        partial(roc_auc_score, multi_class="ovr", average="micro"), True
    ),
    "F1": ClassificationMetric(partial(f1_score, average="micro"), False),
    "Recall": ClassificationMetric(partial(recall_score, average="micro"), False),
    "Precision": ClassificationMetric(
        partial(precision_score, average="micro", zero_division=0), False
    ),
    "Accuracy": ClassificationMetric(accuracy_score, False),
}

BINARY_CLASSIFICATION_METRICS: Dict[str, Metric] = {
    "AUC": ClassificationMetric(
        partial(roc_auc_score, multi_class="ovr", average="macro"), True
    ),
    "F1": ClassificationMetric(partial(f1_score, average="binary"), False),
    "Recall": ClassificationMetric(partial(recall_score, average="binary"), False),
    "Precision": ClassificationMetric(
        partial(precision_score, average="binary", zero_division=0), False
    ),
    "Accuracy": ClassificationMetric(accuracy_score, False),
    "BrierLoss": ClassificationMetric(brier_score_loss, True),
}

_rmse_func: Callable = lambda x, y: np.sqrt(mean_squared_error(x, y))

REGRESSION_METRICS: Dict[str, Metric] = {
    "MAE": Metric(mean_absolute_error),
    "MSE": Metric(mean_squared_error),
    "RMSE": Metric(_rmse_func),
    "R2": Metric(r2_score),
    "KS": Metric(kstest),
}


class MetricsProblem(Enum):
    """Simple wrapper for different problem types for MetricCollection."""

    BINARY_CLASSIFICATION = auto()
    MULTICLASS_CLASSIFICATION = auto()
    MULTILABEL_CLASSIFICATION = auto()
    REGRESSION = auto()


class MetricCollection:
    """Container class for metrics to calculate."""

    def __init__(
        self,
        problem: MetricsProblem,
        metrics: Optional[MutableMapping[str, Metric]] = None,
    ):
        self.problem = problem
        self.metrics = metrics if metrics is not None else self._get_metrics()
        self.optimal_threshold: Optional[float] = None
        self.results: Dict[str, float] = {}
        self.thresholds = np.linspace(0, 100, 201, endpoint=True) / 100
        self.threshold_metrics: Optional[Mapping[str, Iterable[float]]] = None

    @classmethod
    def create_from_model(
        cls,
        model: Union[_BaseModel, DistributedModelProtocol],
        metrics: Optional[MutableMapping[str, Metric]] = None,
    ) -> MetricCollection:
        """Creates a MetricCollection object from a _BaseModel.

        Args:
            model: _BaseModel
            metrics: metrics dictionary.
                Defaults to None.

        Returns:
            Instance of MetricCollection
        """
        # The casts are to reassure mypy that a subclass of both _BaseModel and
        # ClassifierMixIn can exist (the ._Schema attribute causes problems)
        if isinstance(cast(ClassifierMixIn, model), ClassifierMixIn):
            classifier_model = cast(ClassifierMixIn, model)
            if classifier_model.multilabel:
                problem = MetricsProblem.MULTILABEL_CLASSIFICATION
            elif classifier_model.n_classes > 2:
                problem = MetricsProblem.MULTICLASS_CLASSIFICATION
            else:
                problem = MetricsProblem.BINARY_CLASSIFICATION
        else:
            problem = MetricsProblem.REGRESSION

        return cls(problem=problem, metrics=metrics)

    def compute(
        self,
        test_target: np.ndarray,
        test_preds: np.ndarray,
        metric_to_optimise: str = "F1",
        threshold: Optional[float] = None,
    ) -> Dict[str, float]:
        """Compute list of metrics and save results in self.results.

        Args:
            test_target: list of targets
            test_preds: list of predictions
            metric_to_optimise: what metric to optimize in order to compute the
                optimal threshold. This will have no effect if there aren't any metrics
                to which a threshold is applied. Must be present in 'self.metrics'
            threshold: If this argument is provided, this threshold will be
                used instead of optimising the threshold as per 'optimise'

        NOTE: thresholds do not apply to multiclass problems.
        """
        if (
            self.problem is MetricsProblem.BINARY_CLASSIFICATION
            and np.asarray(test_preds).ndim == 2
        ):
            test_preds = np.asarray([row[1] for row in test_preds])

        if (
            self.problem is MetricsProblem.REGRESSION
            or self.problem is MetricsProblem.BINARY_CLASSIFICATION
        ):
            test_preds = np.asarray(test_preds).squeeze()
            test_target = np.asarray(test_target).squeeze()

        for metric_name, metric in self.metrics.items():
            if isinstance(metric, ClassificationMetric) and not metric.probabilities:
                test_probs_or_classes = self._get_prediction_classes(
                    test_target, test_preds, metric_to_optimise, threshold
                )
            else:
                test_probs_or_classes = test_preds
            try:
                self.results[metric_name] = cast(
                    float,
                    self._round(metric.func(test_target, test_probs_or_classes), 4),
                )
                # metric.func always returns a float, so the _round
                # function will return a float as well
            except (ValueError, IndexError):
                # This usually occurs when the targets do not have all possible classes
                self.results[metric_name] = np.inf
                logging.warning(
                    "Unable to compute metric: " + metric_name + " setting to np.inf"
                )

        return self.results

    @staticmethod
    def _round(
        metric: Union[float, Tuple[float]], num_decimal_places: int
    ) -> Union[float, Tuple[float, ...]]:
        """Simply rounds metric by num_decimal_places and returns it."""
        if isinstance(metric, tuple):
            rounded_metric = tuple(round(i, num_decimal_places) for i in metric)
        elif isinstance(metric, float):
            rounded_metric = round(metric, num_decimal_places)  # type: ignore[arg-type] # reason: see below # noqa: B950
            # mypy raises the following error: Argument 1 to
            # "round" has incompatible type "float".

        return rounded_metric

    def get_results_df(self) -> pd.DataFrame:
        """Calls get_results and returns results as a dataframe."""
        return pd.DataFrame.from_dict(
            cast(Dict, self.results), orient="index", columns=["value"]
        )

    def view_thresholds(self) -> matplotlib.figure.Figure:
        """Displays chart of how thresholds affect relevant metrics."""
        fig, ax = plt.subplots()

        for metric_name, metric_vals in cast(
            Mapping[str, Iterable[float]], self.threshold_metrics
        ).items():
            plt.plot(self.thresholds, metric_vals, label=metric_name)
        ax.legend()
        ax.set_title("Metric values at various thresholds")
        ax.set_ylabel("Metric value")
        ax.set_xlabel("Threshold")
        plt.close()

        return fig

    def _get_metrics(
        self,
    ) -> Dict[str, Metric]:
        """Returns metrics appropriate for the task, otherwise simply returns `metrics`.

        Args:
            metrics: Optional. Metrics to be computed.

        Returns:
            Dict[str, Metric]: Dictionary of metrics to be computed
        """
        if self.problem is MetricsProblem.REGRESSION:
            metrics = REGRESSION_METRICS
        elif self.problem is MetricsProblem.BINARY_CLASSIFICATION:
            metrics = BINARY_CLASSIFICATION_METRICS
        elif self.problem is MetricsProblem.MULTICLASS_CLASSIFICATION:
            metrics = MULTICLASS_CLASSIFICATION_METRICS
        else:
            metrics = MULTILABEL_CLASSIFICATION_METRICS

        return metrics

    def _get_prediction_classes(
        self,
        test_target: np.ndarray,
        test_preds: np.ndarray,
        metric_to_optimise: str,
        threshold: Optional[float] = None,
    ) -> np.ndarray:
        """Returns test_preds as class labels.

        This is done after applying or optimising a threshold.
        """
        if (
            threshold is None
            and self.optimal_threshold is None
            and self.problem is not MetricsProblem.MULTICLASS_CLASSIFICATION
        ):
            self._optimise_threshold(test_target, test_preds, metric_to_optimise)

        return self._apply_threshold(test_preds, threshold)

    def _apply_threshold(
        self,
        preds: np.ndarray,
        threshold: Optional[float] = None,
    ) -> np.ndarray:
        """Applies a threshold to a list of predictions and returns the classes.

        For binary and multilabel problems, a threshold is computed and applied.

        For multiclass problems, it simply assumes that every prediction must
        have exactly 1 positive class and this is given to the class corresponding
        to the highest probability.
        """
        if threshold is None:
            threshold = self.optimal_threshold
        test_preds_cls: np.ndarray
        if self.problem is MetricsProblem.BINARY_CLASSIFICATION:
            test_preds_cls = np.where(preds < threshold, 0, 1)
        elif self.problem is MetricsProblem.MULTILABEL_CLASSIFICATION:
            test_preds_cls = np.asarray(
                [[0 if prob < threshold else 1 for prob in output] for output in preds]
            )
        else:
            test_preds_cls = np.array([np.argmax(output) for output in preds])
        return test_preds_cls

    def _optimise_threshold(
        self,
        test_target: np.ndarray,
        test_preds: np.ndarray,
        metric_to_optimise: str,
    ) -> None:
        """Optimise decision threshold by tuning metric_to_optimise.

        Finds the argmax of given metric by modifying the decision threshold and sets
        self.optimal_threshold

        Args:
            test_target: targets
            test_preds: predictions
            metric_to_optimise: metric to optimise

        Raises:
            ValueError: if metric_to_optimise does not exist in self.metrics
        """
        if metric_to_optimise not in self.metrics:
            raise ValueError("Chosen optimisation metric is not defined.")

        optimal_threshold = 0
        max_metric: float = 0

        # Dictionary of relevant metrics (i.e. those where a threshold is applied)
        # and the computed value for every threshold stored as a list
        threshold_metrics: Dict[str, List[float]] = {}
        for m in self.metrics:
            if (
                isinstance(self.metrics[m], ClassificationMetric)
                and not cast(ClassificationMetric, self.metrics[m]).probabilities
            ):
                threshold_metrics[m] = []
        # Loop through every threshold and apply it to our predictions
        for threshold in self.thresholds:
            test_preds_cls = self._apply_threshold(test_preds, threshold)

            # Loop through every metric in threshold_metrics and compute the value
            for metric_name in threshold_metrics:
                metric = self.metrics[metric_name]
                metric_val = metric.func(test_target, test_preds_cls)

                # Store the computed value in `threshold_metrics`
                threshold_metrics[metric_name].append(metric_val)

                # Update optimal threshold if the metric is the one we are optimising
                # and if the value is better than the previous best value
                if metric_name == metric_to_optimise and metric_val > max_metric:
                    max_metric = metric_val
                    optimal_threshold = threshold

        self.optimal_threshold = optimal_threshold
        self.threshold_metrics = threshold_metrics


def sum_fpr_curve(
    test_target: List[float],
    test_pred: List[float],
    test_var_to_sum: List[float],
    test_var_margin: Optional[List[float]] = None,
    granularity: int = 100,
) -> Tuple[List[float], List[float]]:
    """Returns the false positive rate to sums of a given variable.

    Returns this sum as a tuple of arrays (fpr, sums).

    This is calculated by moving a threshold that is used for deciding to
    accept/reject a given entry and then summing the associated variable. This
    can be used, for example, to calculate the total profit that would be
    achieved according to different false positive rates.

    Granularity is the number of regions to have that split up the threshold space.
    """
    thresholds = list(range(0, granularity + 1, 1))
    fprs = []
    test_vars = []

    for threshold in thresholds:
        test_preds_thresh = [
            0 if prob < threshold / granularity else 1 for prob in test_pred
        ]
        true_neg, false_pos, _, _ = confusion_matrix(
            test_target, test_preds_thresh
        ).ravel()
        fpr = 1 - (true_neg / (true_neg + false_pos))
        fprs.append(fpr)
        test_var = _sum_var(test_preds_thresh, test_var_to_sum, test_var_margin)
        test_vars.append(test_var)

    return fprs, test_vars


def _sum_var(
    test_preds_thresh: List[int],
    test_var_to_sum: List[float],
    test_var_margin: Optional[List[float]] = None,
) -> float:
    """Performs the required sum on the variable provided for every prediction."""
    cum_var: float = 0
    cum_margin: float = 0
    for index, val in enumerate(test_preds_thresh):
        if val == 1:
            cum_var += test_var_to_sum[index]
            if test_var_margin:
                cum_margin += test_var_margin[index]

    if test_var_margin:
        return cum_var / max(cum_margin, 1)

    return cum_var
