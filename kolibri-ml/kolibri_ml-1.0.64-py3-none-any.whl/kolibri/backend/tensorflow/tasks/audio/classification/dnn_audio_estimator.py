import numpy as np
from sklearn.utils import class_weight

from kolibri import settings
from kolibri.backend.tensorflow.tasks.audio.classification.models import get_model
from kolibri.backend.tensorflow.tasks.dnn_estimator import DnnEstimator
from kolibri.indexers.label_indexer import LabelIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)

KOLIBRI_MODEL_FILE_NAME = "classifier_kolibri.pkl"
DNN_MODEL_FILE_NAME = "classifier_dnn"


class DnnAudioEstimator(DnnEstimator):
    """classifier using the sklearn framework"""

    _estimator_type = 'estimator'

    name = 'dnn_audio_classifier'

    provides = ["classification", "target_ranking"]

    requires = []

    defaults = {

        # the models used in the classifier if several models are given they will be combined
        "models": "conv_1d",
        "multi-label": False,
        "epochs": 10,
        "loss": 'categorical_crossentropy',
        "class-weight": False,
        "project-dir": "."
    }

    def __init__(self, component_config=None):

        """Construct a new class classifier using the sklearn framework."""

        super().__init__(component_config)
        self.indexer = LabelIndexer(multi_label=self.component_config["multi-label"])

        self.clf = get_model(self.component_config['models'], hyper_parameters=self.component_config)

#        print(self.clf.tf_model.summary())
    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y, X_val=None, y_val=None):
        fit_kwargs = {}
        if self.component_config['class-weight']:
            class_weights = class_weight.compute_class_weight('balanced', np.unique(y), y)
            fit_kwargs = {"class_weight": class_weights}
        self.clf.fit(X, y, x_validate=X_val, y_validate=y_val, epochs=self.component_config["epochs"],
                     batch_size=self.component_config["batch_size"],
                     fit_kwargs=fit_kwargs)
        self.classifier_type = type(self.clf)
    def transform(self, document):

        return self.clf.transform(document, )




    def process(self, document, **kwargs):
        """Return the most likely class and its probability for a document."""
        raw_results = None
        if not self.clf:
            # component is either not trained or didn't
            # receive enough training texts
            target = None
            target_ranking = []
        else:
            X = np.array(document.tokens)
            raw_results = self.clf.predict_top_k_class([X], top_k=settings.modeling['TARGET_RANKING_LENGTH'])

            if len(raw_results) > 0:

                target = {"name": raw_results[0]['label'], "confidence": raw_results[0]['confidence']}

                target_ranking = raw_results[0]['confidence']
            else:
                target = {"name": None, "confidence": 0.0}
                target_ranking = []

        document.label = target
        document.raw_prediction_results = raw_results
        document.set_output_property("raw_prediction_results")
        document.set_output_property("label")
        document.target_ranking = target_ranking
        document.set_output_property("target_ranking")

