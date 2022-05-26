import logging
import typing

from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from mlfoundry.enums import ModelType
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.metrics.v2.base_metrics import BaseMetrics

logger = logging.getLogger(__name__)


class RegressionMetrics(BaseMetrics):
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    R2_SCORE = "r2_score"
    ROOT_MEAN_SQUARE_ERROR = "root_mean_squared_error"
    EXPLAINED_VARIANCE_SCORE = "explained_variance_score"

    @property
    def model_type(self) -> ModelType:
        return ModelType.REGRESSION

    def get_metric_name_to_function_map(self) -> typing.Dict[str, typing.Callable]:
        return {
            self.MEAN_SQUARED_ERROR: self.compute_mean_squared_error,
            self.MEAN_ABSOLUTE_ERROR: self.compute_mean_absolute_error,
            self.R2_SCORE: self.compute_r2_score,
            self.ROOT_MEAN_SQUARE_ERROR: self.compute_root_mean_squared_error,
            self.EXPLAINED_VARIANCE_SCORE: self.compute_explained_variance_score,
        }

    def validate(self, predictions, actuals, **kwargs):
        if predictions is None:
            raise MlFoundryException("predictions cannot be None")
        if actuals is None:
            raise MlFoundryException("actuals cannot be none")

    @staticmethod
    def compute_mean_squared_error(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return mean_squared_error(actuals, predictions)

    @staticmethod
    def compute_mean_absolute_error(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return mean_absolute_error(actuals, predictions)

    @staticmethod
    def compute_r2_score(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return r2_score(actuals, predictions)

    @staticmethod
    def compute_root_mean_squared_error(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return mean_squared_error(actuals, predictions, squared=False)

    @staticmethod
    def compute_explained_variance_score(actuals, predictions, **kwargs):
        """
        Sklearn metric compute.
        :param actuals:
        :param predictions:
        :return:
        """
        return explained_variance_score(actuals, predictions)
