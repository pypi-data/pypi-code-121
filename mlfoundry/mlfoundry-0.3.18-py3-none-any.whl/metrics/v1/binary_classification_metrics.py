import logging

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    dcg_score,
    f1_score,
    log_loss,
    ndcg_score,
    precision_recall_curve,
    roc_curve,
)

from mlfoundry.constants import (
    MULTI_DIMENSIONAL_METRICS,
    NON_MULTI_DIMENSIONAL_METRICS,
    PROB_MULTI_DIMENSIONAL_METRICS,
    PROB_NON_MULTI_DIMENSIONAL_METRICS,
)
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.metrics.v1.base_metrics import BaseMetrics

logger = logging.getLogger(__name__)


class BinaryClassificationMetrics(BaseMetrics):
    TYPE_OF_MODEL = "binary_classification"
    ACCURACY = "accuracy"
    F1_SCORE = "f1_score"
    COHEN_KAPPA_SCORE = "cohen_kappa_score"
    CONFUSION_MATRIX = "confusion_matrix"
    DCG_SCORE = "dcg_score"
    NDCG_SCORE = "ndcg_score"
    LOG_LOSS = "log_loss"
    ROC_CURVE = "roc_curve"
    PR_CURVE = "precision_recall_curve"

    def __init__(self):
        super().__init__()
        self.binary_classification_metrics = {
            NON_MULTI_DIMENSIONAL_METRICS: {
                self.ACCURACY: self.compute_accuracy,
                self.F1_SCORE: self.compute_f1_score,
                self.COHEN_KAPPA_SCORE: self.compute_cohen_kappa_score,
            },
            MULTI_DIMENSIONAL_METRICS: {
                self.CONFUSION_MATRIX: self.compute_confusion_matrix,
            },
            PROB_NON_MULTI_DIMENSIONAL_METRICS: {
                # self.DCG_SCORE: self.compute_dcg_score,
                # self.NDCG_SCORE: self.compute_ndcg_score,
                self.LOG_LOSS: self.compute_log_loss,
            },
            PROB_MULTI_DIMENSIONAL_METRICS: {
                self.ROC_CURVE: self.compute_roc_curve,
                self.PR_CURVE: self.compute_pr_curve,
            },
        }

    def compute_metrics(
        self, features_df, predictions, labels, pred_probabilities=None
    ):
        """
        Compute metrics for binary classification models.
        This method calls the parent class as well for any supported metrics.
        :param features_df:
        :param predictions:
        :param labels:
        :param pred_probabilities:
        :return:
            metrics_dict
        """

        metrics_from_parent = super().compute_metrics(
            features_df, predictions, labels, pred_probabilities
        )

        all_metrics = metrics_from_parent
        for metric in self.binary_classification_metrics[
            NON_MULTI_DIMENSIONAL_METRICS
        ].keys():
            all_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                metric
            ] = self.binary_classification_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                metric
            ](
                labels, predictions
            )
        for metric in self.binary_classification_metrics[
            MULTI_DIMENSIONAL_METRICS
        ].keys():
            all_metrics[MULTI_DIMENSIONAL_METRICS][
                metric
            ] = self.binary_classification_metrics[MULTI_DIMENSIONAL_METRICS][metric](
                labels, predictions
            )

        if pred_probabilities:
            for metric in self.binary_classification_metrics[
                PROB_NON_MULTI_DIMENSIONAL_METRICS
            ].keys():
                all_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                    metric
                ] = self.binary_classification_metrics[
                    PROB_NON_MULTI_DIMENSIONAL_METRICS
                ][
                    metric
                ](
                    labels, pred_probabilities
                )
            for metric in self.binary_classification_metrics[
                PROB_MULTI_DIMENSIONAL_METRICS
            ].keys():
                all_metrics[MULTI_DIMENSIONAL_METRICS][
                    metric
                ] = self.binary_classification_metrics[PROB_MULTI_DIMENSIONAL_METRICS][
                    metric
                ](
                    labels, pred_probabilities
                )

        return all_metrics

    @staticmethod
    def compute_accuracy(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return accuracy_score(y_true, y_pred)

    @staticmethod
    def compute_f1_score(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return f1_score(y_true, y_pred)

    @staticmethod
    def compute_cohen_kappa_score(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return cohen_kappa_score(y_true, y_pred)

    @staticmethod
    def compute_confusion_matrix(y_true, y_pred):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_pred:
        :return:
        """
        return confusion_matrix(y_true, y_pred)

    @staticmethod
    def compute_dcg_score(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        return dcg_score(y_true, y_prob)

    @staticmethod
    def compute_ndcg_score(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        return ndcg_score(y_true, y_prob)

    @staticmethod
    def compute_log_loss(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        return log_loss(y_true, y_prob)

    @staticmethod
    def compute_roc_curve(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        classes = np.unique(y_true)
        if len(classes) != 2:
            raise MlFoundryException(
                "given data doesn't belong to binary classification"
            )

        y_pred = np.asarray(y_prob)
        fpr, tpr, thresholds = roc_curve(y_true, y_pred[:, 0], pos_label=classes[0])
        return {
            "fpr": fpr,
            "tpr": tpr,
            "thresholds": thresholds,
        }

    @staticmethod
    def compute_pr_curve(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        classes = np.unique(y_true)
        if len(classes) != 2:
            raise MlFoundryException(
                "given data doesn't belong to binary classification"
            )

        y_pred = np.asarray(y_prob)
        precision, recall, thresholds = precision_recall_curve(
            y_true, y_pred[:, 0], pos_label=classes[0]
        )
        return {
            "precision": precision,
            "recall": recall,
            "thresholds": thresholds,
        }
