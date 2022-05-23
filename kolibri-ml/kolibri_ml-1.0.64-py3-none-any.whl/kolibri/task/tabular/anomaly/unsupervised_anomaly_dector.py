import os
from pathlib import Path

import numpy as np
from scipy.sparse import vstack
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import ModelCheckpoint

import kolibri
from kolibri.core.component import Component
from kolibri.task.tabular.anomaly.models import get_model

ANOMALY_MODEL_FILE_NAME = "anomaly_model"


class UnsupervisedAnomalyDetector(Component):
    _estimator_type = 'estimator'

    name = 'unsupervised_anomaly_detector'

    provides = ["classification", "target_ranking"]

    requires = ["text_features"]

    defaults = {

        # the models used in the classifier if several models are given they will be combined
        "models": "mlp",
        "epochs": 10,
        "batch_size": 32,
        "loss": 'mean_squared_error',
        "project-dir": ".",
        "threshold": None,
        "estimated_negative_sample_ratio": 0.99,
        "validation_split": 0.2,
        "shuffle": True
    }

    def __init__(self, component_config=None, model=None, normalize_data=True):
        super().__init__(component_config)
        self.normalize_data = normalize_data
        if self.normalize_data and 'output' not in self.hyperparameters:
            self.hyperparameters['output'] = {
                'activation': 'sigmoid'
            }
        self.model = None
        if model:
            self.model = get_model(model, self.hyperparameters)
        else:
            network_parmaters=None
            if 'graph' in component_config:
                network_parmaters=component_config['graph']

            self.model = get_model(component_config['models'], network_parmaters)

        self.input_dim = None
        self.threshold = self.hyperparameters['threshold']

        self.normalizer = MinMaxScaler()

    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y=None, X_val=None, y_val=None):

        if self.normalize_data:
            X = self.normalizer.fit_transform(X)

        dir_path = os.path.join(self.hyperparameters["project-dir"], ANOMALY_MODEL_FILE_NAME)

        Path(dir_path).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(dir_path, 'model_weights.h5')

        checkpoint = ModelCheckpoint(filepath,
                                     monitor='val_loss',
                                     verbose=1,
                                     save_best_only=True,
                                     mode='max')
        callbacks_list = [checkpoint]

        self.model.fit(X, batch_size=self.hyperparameters['batch_size'], epochs=self.hyperparameters["epochs"],
                       shuffle=self.hyperparameters["shuffle"],
                       validation_split=self.hyperparameters["validation_split"], callbacks=callbacks_list)

        return self

    def transform(self, document):

        raise NotImplementedError

    def predict(self, X):
        """Given a bow vector of an input text, predict most probable label.

        Return only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second,
                 its probability."""

        if self.normalize_data:
            X = self.normalizer.transform(X)
        target_data = self.model.predict(X)
        dist = np.mean((target_data - X) ** 2, axis=-1)
        cut_point = int(self.hyperparameters['estimated_negative_sample_ratio'] * len(dist))
        self.threshold = sorted(dist)[cut_point]

        return zip(dist >= self.threshold, dist)

    def train(self, training_data, **kwargs):

        X = vstack([document.vector for document in training_data])
        self.fit(X)

    def process(self, document, **kwargs):
        raise NotImplementedError

    @classmethod
    def load(cls,
             model_dir=None,
             model_metadata=None,
             cached_component=None,
             **kwargs
             ):

        meta = model_metadata.for_component(cls.name)

        model_file = os.path.join(model_dir, ANOMALY_MODEL_FILE_NAME)

        if os.path.exists(model_file):
            ent_tagger = kolibri.dnn.utils.load_model(model_file)
            return cls(meta, ent_tagger)
        else:
            return cls(meta)

    def persist(self, model_dir):
        """Persist this model into the passed directory.

        Returns the metadata necessary to load the model again."""

        if self.clf:
            model_file_name = os.path.join(model_dir, ANOMALY_MODEL_FILE_NAME)

            self.clf.save_info(model_file_name)

        return {"classifier_file": ANOMALY_MODEL_FILE_NAME}
