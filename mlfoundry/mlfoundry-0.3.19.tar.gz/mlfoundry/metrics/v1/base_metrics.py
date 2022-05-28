import logging

from mlfoundry.constants import (
    MULTI_DIMENSIONAL_METRICS,
    NON_MULTI_DIMENSIONAL_METRICS,
    PROB_MULTI_DIMENSIONAL_METRICS,
    PROB_NON_MULTI_DIMENSIONAL_METRICS,
)

logger = logging.getLogger(__name__)


class BaseMetrics:
    PERCENTAGE_FEATURE_NULL = "percentage_feature_null"

    def __init__(self):
        self.metrics_base = {
            NON_MULTI_DIMENSIONAL_METRICS: {},
            MULTI_DIMENSIONAL_METRICS: {},
            PROB_NON_MULTI_DIMENSIONAL_METRICS: {},
            PROB_MULTI_DIMENSIONAL_METRICS: {},
        }

    def compute_metrics(
        self, features_df, predictions, labels, pred_probabilities=None
    ):
        """
        Compute metrics for all models.
        :param features_df:
        :param predictions:
        :param labels:
        :param pred_probabilities:
        :return:
            metrics_dict
        """

        all_metrics = {
            NON_MULTI_DIMENSIONAL_METRICS: {},
            MULTI_DIMENSIONAL_METRICS: {},
            PROB_NON_MULTI_DIMENSIONAL_METRICS: {},
            PROB_MULTI_DIMENSIONAL_METRICS: {},
        }
        for metric in self.metrics_base[NON_MULTI_DIMENSIONAL_METRICS].keys():
            all_metrics[NON_MULTI_DIMENSIONAL_METRICS][metric] = self.metrics_base[
                NON_MULTI_DIMENSIONAL_METRICS
            ][metric]()
        for metric in self.metrics_base[MULTI_DIMENSIONAL_METRICS].keys():
            all_metrics[MULTI_DIMENSIONAL_METRICS][metric] = self.metrics_base[
                MULTI_DIMENSIONAL_METRICS
            ][metric]()

        if pred_probabilities:
            for metric in self.metrics_base[PROB_NON_MULTI_DIMENSIONAL_METRICS].keys():
                all_metrics[NON_MULTI_DIMENSIONAL_METRICS][metric] = self.metrics_base[
                    PROB_NON_MULTI_DIMENSIONAL_METRICS
                ][metric]()
            for metric in self.metrics_base[PROB_MULTI_DIMENSIONAL_METRICS].keys():
                all_metrics[MULTI_DIMENSIONAL_METRICS][metric] = self.metrics_base[
                    PROB_MULTI_DIMENSIONAL_METRICS
                ][metric]()

        return all_metrics
