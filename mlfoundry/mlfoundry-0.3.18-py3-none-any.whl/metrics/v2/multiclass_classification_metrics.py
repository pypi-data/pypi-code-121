import logging
import typing

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    log_loss,
    precision_recall_curve,
    roc_curve,
)

from mlfoundry.enums import ModelType
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.metrics.v2.base_metrics import BaseMetrics
from mlfoundry.metrics.v2.custom_metric_types import (
    ClassificationReport,
    ConfusionMatrix,
    PrCurve,
    RocCurve,
)

logger = logging.getLogger(__name__)


class MultiClassClassificationMetrics(BaseMetrics):
    ACCURACY = "accuracy"
    COHEN_KAPPA_SCORE = "cohen_kappa_score"
    CONFUSION_MATRIX = "confusion_matrix"
    LOG_LOSS = "log_loss"
    ROC_CURVE = "roc_curve"
    PR_CURVE = "precision_recall_curve"
    CLASSIFICATION_REPORT = "classification_report"

    @property
    def model_type(self) -> ModelType:
        return ModelType.MULTICLASS_CLASSIFICATION

    def get_metric_name_to_function_map(self) -> typing.Dict[str, typing.Callable]:
        return {
            self.ACCURACY: self.compute_accuracy,
            self.COHEN_KAPPA_SCORE: self.compute_cohen_kappa_score,
            self.CONFUSION_MATRIX: self.compute_confusion_matrix,
            self.LOG_LOSS: self.compute_log_loss,
            self.ROC_CURVE: self.compute_roc_curve,
            self.PR_CURVE: self.compute_pr_curve,
            self.CLASSIFICATION_REPORT: self.compute_classification_report,
        }

    def validate(
        self,
        predictions,
        actuals,
        prediction_probabilities,
        class_names,
    ):
        if prediction_probabilities is not None and class_names is None:
            raise MlFoundryException(
                "class names are required if prediction probability is passed"
            )
        if predictions is None:
            raise MlFoundryException("predictions cannot be None")
        if actuals is None:
            raise MlFoundryException("actuals cannot be none")
        if prediction_probabilities is not None:
            prediction_probabilities = np.asarray(prediction_probabilities, dtype=float)
            if prediction_probabilities.ndim != 2 and prediction_probabilities.shape[
                1
            ] != len(class_names):
                raise MlFoundryException(
                    "prediction_probabilities should have two dimension\n"
                    "the number of columns should match the number of class_names"
                )

    @staticmethod
    def compute_accuracy(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return accuracy_score(actuals, predictions)

    @staticmethod
    def compute_cohen_kappa_score(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return cohen_kappa_score(actuals, predictions)

    @staticmethod
    def compute_confusion_matrix(actuals, predictions, class_names, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return ConfusionMatrix(
            matrix=confusion_matrix(actuals, predictions, labels=class_names).tolist(),
            class_names=class_names,
        )

    @staticmethod
    def compute_log_loss(actuals, prediction_probabilities, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param prediction_probabilities:
        :return:
        """
        if prediction_probabilities is None:
            logger.info(
                "prediction_probabilities not passed, skipping compute_log_loss"
            )
            return None
        predictions = np.asarray(prediction_probabilities)
        return log_loss(actuals, predictions)

    @staticmethod
    def compute_roc_curve(actuals, prediction_probabilities, class_names, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param prediction_probabilities:
        :return:
        """
        if prediction_probabilities is None:
            logger.info(
                "prediction_probabilities not passed, skipping compute_roc_curve"
            )
            return None
        result = {}

        prediction_probabilities = np.asarray(prediction_probabilities)

        for i, class_name in enumerate(class_names):
            fpr, tpr, thresholds = roc_curve(
                actuals, prediction_probabilities[:, i], pos_label=class_name
            )
            result[class_name] = RocCurve(
                fpr=fpr.tolist(),
                tpr=tpr.tolist(),
                thresholds=thresholds.tolist(),
            )

        return result

    @staticmethod
    def compute_pr_curve(actuals, prediction_probabilities, class_names, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param prediction_probabilities:
        :return:
        """
        if prediction_probabilities is None:
            logger.info(
                "prediction_probabilities not passed, skipping compute_pr_curve"
            )
            return None
        result = {}

        prediction_probabilities = np.asarray(prediction_probabilities)

        for i, class_name in enumerate(class_names):
            precision, recall, thresholds = precision_recall_curve(
                actuals, prediction_probabilities[:, i], pos_label=class_name
            )
            result[class_name] = PrCurve(
                precision=precision.tolist(),
                recall=recall.tolist(),
                thresholds=thresholds.tolist(),
            )

        return result

    @staticmethod
    def compute_classification_report(actuals, predictions, class_names, **kwargs):
        report = classification_report(
            y_true=actuals, y_pred=predictions, labels=class_names, output_dict=True
        )
        report = {
            class_name: ClassificationReport(**report[str(class_name)])
            for class_name in class_names
        }
        return report
