import os

import joblib
import numpy as np
from scipy.sparse import vstack
from sklearn.utils import class_weight

from kolibri.config import override_defaults
from kolibri.core.component import Component
from kolibri.logger import get_logger
from sklearn.model_selection import train_test_split
from kolibri.evaluators.classifier_evaluator import ClassifierEvaluator
logger = get_logger(__name__)

KOLIBRI_MODEL_FILE_NAME = "classifier_kolibri.pkl"
DNN_MODEL_FILE_NAME = "classifier_dnn"


class DnnEstimator(Component):
    """classifier using the sklearn framework"""

    _estimator_type = 'estimator'

    name = ''

    provides = []

    requires = []

    defaults = {

        # the models used in the classifier if several models are given they will be combined
        'fixed':{
            "embeddings": None,
            "multi-label": False,
            "sequence_length": 'auto',
            "epochs": 1,
            "loss": 'categorical_crossentropy',
            "class-weight": False,
            "test_size": 0.3
        },
        'tunable':{}

    }

    def __init__(self, component_config=None):

        """Construct a new class classifier using the sklearn framework."""

        self.defaults = override_defaults(
            super(DnnEstimator, self).defaults, self.defaults)
        super().__init__(parameters=component_config)


    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y, X_val=None, y_val=None):
        fit_kwargs = {}
        if self.component_config['class-weight']:
            class_weights = class_weight.compute_class_weight('balanced',
                                                              np.unique(y),
                                                              y)
            fit_kwargs = {"class_weight": class_weights}

        if X_val ==None or y_val==None:
            X, X_val, y,y_val = train_test_split(X, y, test_size=self.component_config["test_size"])


        self.clf.fit(X, y, x_validate=X_val, y_validate=y_val, epochs=self.component_config["epochs"],
                     fit_kwargs=fit_kwargs)

        print(self.clf.evaluate(X_val, y_val))
        y_pred=self.clf.predict(X_val)
        self.performance_report=ClassifierEvaluator.get_performance_report(y_val, y_pred[0][:,0], None)

    def transform(self, document):

        return self.clf.transform(document, )

    def predict(self, X):
        """Given a bow vector of an input text, predict most probable label.

        Return only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second,
                 its probability."""

        return self.clf.predict(X)

    def train(self, training_data, **kwargs):

        y = [document.label for document in training_data]
        X = vstack([document.vector for document in training_data])
        self.fit(X, y)

    def process(self, document, **kwargs):
        raise NotImplementedError

    def __getstate__(self):
        """Return state values to be pickled."""
        return (self.hyperparameters, self.classifier_type)

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.hyperparameters, self.classifier_type = state


    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):


        classifier_file_name = model_metadata.get("classifier_file", KOLIBRI_MODEL_FILE_NAME)
        dnn_file_name = model_metadata.get("dnn_file", DNN_MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, classifier_file_name)
        if os.path.exists(classifier_file):
            # Load saved model
            model = joblib.load(classifier_file)

            clf = model.classifier_type.load_model(os.path.join(model_dir, dnn_file_name))

            model.clf = clf
            return model
        else:
            return cls(model_metadata)

    def persist(self, model_dir):
        """Persist this model into the passed directory.

        Returns the metadata necessary to load the model again."""
        classifier_file = os.path.join(model_dir, KOLIBRI_MODEL_FILE_NAME)
        joblib.dump(self, classifier_file)
        dnn_file = os.path.join(model_dir, DNN_MODEL_FILE_NAME)
        if self.clf:
            self.clf.save(dnn_file)


        return {"classifier_file": KOLIBRI_MODEL_FILE_NAME, "dnn_file": DNN_MODEL_FILE_NAME}
