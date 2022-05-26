import logging

import pandas as pd
from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from mlfoundry.constants import (
    MULTI_DIMENSIONAL_METRICS,
    NON_MULTI_DIMENSIONAL_METRICS,
    PROB_MULTI_DIMENSIONAL_METRICS,
    PROB_NON_MULTI_DIMENSIONAL_METRICS,
)
from mlfoundry.metrics.v1.base_metrics import BaseMetrics

logger = logging.getLogger(__name__)


class TimeSeriesMetrics(BaseMetrics):
    TYPE_OF_MODEL = "timeseries"
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    R2_SCORE = "r2_score"
    ROOT_MEAN_SQUARE_ERROR = "root_mean_squared_error"

    def __init__(self):
        super().__init__()
        self.timeseries_metrics = {
            NON_MULTI_DIMENSIONAL_METRICS: {
                self.MEAN_SQUARED_ERROR: self.compute_mean_squared_error,
                self.MEAN_ABSOLUTE_ERROR: self.compute_mean_absolute_error,
                self.R2_SCORE: self.compute_r2_score,
                self.ROOT_MEAN_SQUARE_ERROR: self.compute_root_mean_squared_error,
            },
            MULTI_DIMENSIONAL_METRICS: {},
            PROB_NON_MULTI_DIMENSIONAL_METRICS: {},
            PROB_MULTI_DIMENSIONAL_METRICS: {},
        }

    def compute_metrics(
        self, features_df, predictions, labels, pred_probabilities=None
    ):
        """
        Compute metrics for timeseries models.This method calls the parent class as well for any supported metrics.
        :param features_df:
        :param predictions:
        :param labels:
        :return:
            metrics_dict
        """
        metrics_from_parent = super().compute_metrics(
            features_df, predictions, labels, pred_probabilities
        )

        all_metrics = metrics_from_parent
        for metric in self.timeseries_metrics[NON_MULTI_DIMENSIONAL_METRICS].keys():
            all_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                metric
            ] = self.timeseries_metrics[NON_MULTI_DIMENSIONAL_METRICS][metric](
                labels, predictions
            )
        for metric in self.timeseries_metrics[MULTI_DIMENSIONAL_METRICS].keys():
            all_metrics[MULTI_DIMENSIONAL_METRICS][metric] = self.timeseries_metrics[
                MULTI_DIMENSIONAL_METRICS
            ][metric](labels, predictions)

        if pred_probabilities:
            for metric in self.timeseries_metrics[
                PROB_NON_MULTI_DIMENSIONAL_METRICS
            ].keys():
                all_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                    metric
                ] = self.timeseries_metrics[PROB_NON_MULTI_DIMENSIONAL_METRICS][metric](
                    labels, pred_probabilities
                )
            for metric in self.timeseries_metrics[
                PROB_MULTI_DIMENSIONAL_METRICS
            ].keys():
                all_metrics[MULTI_DIMENSIONAL_METRICS][
                    metric
                ] = self.timeseries_metrics[PROB_MULTI_DIMENSIONAL_METRICS][metric](
                    labels, pred_probabilities
                )

        return all_metrics

    @staticmethod
    def compute_mean_squared_error(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return mean_squared_error(y_true, y_pred)

    @staticmethod
    def compute_mean_absolute_error(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return mean_absolute_error(y_true, y_pred)

    @staticmethod
    def compute_r2_score(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return r2_score(y_true, y_pred)

    @staticmethod
    def compute_root_mean_squared_error(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return mean_squared_error(y_true, y_pred, squared=False)
