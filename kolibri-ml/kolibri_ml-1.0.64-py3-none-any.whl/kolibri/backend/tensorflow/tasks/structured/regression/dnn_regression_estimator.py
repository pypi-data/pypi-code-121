
from kolibri.core.component import Component
import pathlib, os, json
from kolibri.backend.tensorflow.tasks.structured.regression.models import get_model
import tensorflow as tf
import kolibri
from kolibri.config import override_defaults
from kolibri.logger import get_logger
from kolibri.backend.tensorflow.tasks.dnn_estimator import DnnEstimator
logger = get_logger(__name__)

KOLIBRI_MODEL_FILE_NAME = "regressor_kolibri.pkl"
DNN_MODEL_FILE_NAME = "regressor_dnn"


class DnnRegressionEstimator(DnnEstimator):
    """regression using the tensorflow framework"""

#    name = 'dnn_regression_estimatator'

    component_type = "estimator"

    provides = ["regression", "target_ranking"]

    requires = ["numerical_features"]

    defaults = {
        'fixed':{
        "model": "lstm",
        "epochs": 10,
        "steps_per_epoch":150,
        "loss": 'mse',
        "project-dir": ".",
        "patience":150},
        'tunable':{}
    }

    def __init__(self, component_config=None):

        """Construct a new class classifier using the sklearn framework."""

        self.defaults = override_defaults(
            super().defaults, self.defaults)

        super().__init__(component_config)


        self.clf = get_model(self.get_parameter('model'), hyper_parameters=self.hyperparameters)
        self.classifier_type = type(self.clf)

    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y, X_val=None, y_val=None):
        fit_kwargs = {}

        self.clf.fit(X,
                       y, epochs=self.get_parameter("epochs"), steps_per_epoch=self.get_parameter("steps_per_epoch"),
                       x_val=(X_val, y_val), patience=self.get_parameter("patience"))

        self.classifier_type = type(self.clf)


from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(DnnRegressionEstimator.name, DnnRegressionEstimator)
