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
from sklearn.preprocessing import label_binarize

from mlfoundry.constants import (
    MULTI_DIMENSIONAL_METRICS,
    NON_MULTI_DIMENSIONAL_METRICS,
    PROB_MULTI_DIMENSIONAL_METRICS,
    PROB_NON_MULTI_DIMENSIONAL_METRICS,
)
from mlfoundry.metrics.v1.base_metrics import BaseMetrics

logger = logging.getLogger(__name__)


class MultiClassClassificationMetrics(BaseMetrics):
    TYPE_OF_MODEL = "multiclass_classification"
    ACCURACY = "accuracy"
    COHEN_KAPPA_SCORE = "cohen_kappa_score"
    CONFUSION_MATRIX = "confusion_matrix"
    DCG_SCORE = "dcg_score"
    NDCG_SCORE = "ndcg_score"
    LOG_LOSS = "log_loss"
    ROC_CURVE = "roc_curve"
    PR_CURVE = "precision_recall_curve"

    def __init__(self):
        super().__init__()
        self.multiclass_classification_metrics = {
            NON_MULTI_DIMENSIONAL_METRICS: {
                self.ACCURACY: self.compute_accuracy,
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
        Compute numerical metrics for multi class classification models.
        This method calls the parent class as well for any supported metrics.
        :param features_df:
        :param predictions:
        :param labels:
        :return:
            metrics_dict
        """
        metrics_from_parent = super().compute_metrics(features_df, predictions, labels)

        all_metrics = metrics_from_parent
        for metric in self.multiclass_classification_metrics[
            NON_MULTI_DIMENSIONAL_METRICS
        ].keys():
            all_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                metric
            ] = self.multiclass_classification_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                metric
            ](
                labels, predictions
            )
        for metric in self.multiclass_classification_metrics[
            MULTI_DIMENSIONAL_METRICS
        ].keys():
            all_metrics[MULTI_DIMENSIONAL_METRICS][
                metric
            ] = self.multiclass_classification_metrics[MULTI_DIMENSIONAL_METRICS][
                metric
            ](
                labels, predictions
            )

        if pred_probabilities:
            for metric in self.multiclass_classification_metrics[
                PROB_NON_MULTI_DIMENSIONAL_METRICS
            ].keys():
                all_metrics[NON_MULTI_DIMENSIONAL_METRICS][
                    metric
                ] = self.multiclass_classification_metrics[
                    PROB_NON_MULTI_DIMENSIONAL_METRICS
                ][
                    metric
                ](
                    labels, pred_probabilities
                )
            for metric in self.multiclass_classification_metrics[
                PROB_MULTI_DIMENSIONAL_METRICS
            ].keys():
                all_metrics[MULTI_DIMENSIONAL_METRICS][
                    metric
                ] = self.multiclass_classification_metrics[
                    PROB_MULTI_DIMENSIONAL_METRICS
                ][
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
        y_pred = np.asarray(y_prob)
        return ndcg_score(y_true, y_pred)

    @staticmethod
    def compute_log_loss(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        y_pred = np.asarray(y_prob)
        return log_loss(y_true, y_pred)

    @staticmethod
    def compute_roc_curve(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        classes = np.unique(y_true)
        fpr = []
        tpr = []
        thresholds = []

        y_pred = np.asarray(y_prob)

        for i in range(len(classes)):
            fpr_elem, tpr_elem, thresholds_elem = roc_curve(
                y_true, y_pred[:, i], pos_label=classes[i]
            )
            fpr.append(fpr_elem)
            tpr.append(tpr_elem)
            thresholds.append(thresholds_elem)

        return {"fpr": fpr, "tpr": tpr, "thresholds": thresholds}

    @staticmethod
    def compute_pr_curve(y_true, y_prob):
        """
        Sklearn metric compute.
        :param y_true:
        :param y_prob:
        :return:
        """
        classes = np.unique(y_true)
        precision = []
        recall = []
        thresholds = []

        y_pred = np.asarray(y_prob)

        for i in range(len(classes)):
            precision_elem, recall_elem, thresholds_elem = precision_recall_curve(
                y_true, y_pred[:, i], pos_label=classes[i]
            )
            precision.append(precision_elem)
            recall.append(recall_elem)
            thresholds.append(thresholds_elem)

        return {"precision": precision, "recall": recall, "thresholds": thresholds}
