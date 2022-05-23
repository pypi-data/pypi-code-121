import json
import os
import threading
from typing import Dict, Any

import numpy as np
import tempfile, time
from sklearn import metrics as sklearn_metrics

import kolibri
from kolibri.data.text.generators import DataGenerator
from kolibri.backend.tensorflow.tasks.base_model import TaskBaseModel
from kolibri.backend.tensorflow.layers import L
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.logger import get_logger
import tensorflow as tf
logger = get_logger(__name__)

threading._DummyThread._Thread__stop = lambda x: 42


class BaseStructuredModel(TaskBaseModel):
    """
    Abstract Audio Classification Model
    """

    __task__ = 'classification'

    def to_dict(self):
        model_json_str = self.tf_model.to_json()
        base_dict = super(BaseStructuredModel, self).to_dict()
        base_dict.update({
            'tf_model': json.loads(model_json_str)
        })
        return base_dict

    def __init__(self, sequence_length=None, hyper_parameters=None):
        """

        Args:
            embedding: embedding object
            sequence_length: target sequence length_train
            hyper_parameters: hyper_parameters to overwrite
            multi_label: is multi-label classification
            label_indexer: label processor
        """
        super().__init__(sequence_length, hyper_parameters)

    def build_model(self,
                    x_train,
                    y_train):
        """
        Build Model with x_data and y_data

        This function will setup a :class:`CorpusGenerator`,
         then call py:meth:`BaseTextClassificationModel.build_model_gen` for preparing processor and model

        Args:
            x_train:
            y_train:

        Returns:

        """

        train_gen = DataGenerator(x_train, y_train)
        self.build_model_generator(train_gen)

    def build_model_generator(self, generators):

        if self.tf_model is None:
            self.build_model_arc(generators)
        self.compile_model()

    @classmethod
    def get_default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError

    def build_model_arc(self, generators) -> None:
        raise NotImplementedError

    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:
        """
        Configures the model for training.
        call :meth:`tf.keras.Model.predict` to compile model with custom loss, optimizer and metrics
        """
        loss =self.hyper_parameters["loss"]

        if optimizer is None:
            optimizer = 'adam'
        if metrics is None:
            metrics = ['accuracy']

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)

    def fit(self, X_train, y_train, x_val=None,epochs=500,steps_per_epoch=150, patience=10, EVALUATION_INTERVAL=15):
        self.build_model(X_train, y_train)
        self.checkpoint_model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
        self.history = self.tf_model.fit(X_train, y_train, epochs=epochs, steps_per_epoch=steps_per_epoch,
                                              validation_data=x_val,
                                              validation_steps=50, verbose=1,
                                              callbacks=[
                                                  tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0,
                                                                                   patience=patience, verbose=1, mode='min'),
                                                  tf.keras.callbacks.ModelCheckpoint(self.checkpoint_model_path, monitor='val_loss',
                                                                                     save_best_only=True, mode='min',
                                                                                     verbose=0)])


    def predict(self, x_data, *,
                batch_size: int = 32,
                predict_kwargs: Dict = None):
        """
        Generates output predictions for the input samples.

        Computation is done in batches.

        Args:
            x_data: The input texts, as a Numpy array (or list of Numpy arrays if the model has multiple inputs).
            batch_size: Integer. If unspecified, it will default to 32.
            truncating: remove values from sequences larger than `model.embedding.sequence_length`
            multi_label_threshold:
            predict_kwargs: arguments passed to ``predict()`` function of ``tf.keras.Model``

        Returns:
            array(s) of predictions.
        """
        if predict_kwargs is None:
            predict_kwargs = {}

            tensor = x_data
            logger.debug(f'predict input shapes {np.array(tensor[0]).shape} and  {np.array(tensor[1]).shape}')
            pred = self.tf_model.predict(tensor, batch_size=batch_size, **predict_kwargs)
            logger.debug(f'predict output shape {pred.shape}')


        return pred

    def evaluate(self, x_data, y_data, *,
                 batch_size: int = 32,
                 digits: int = 4,
                 multi_label_threshold: float = 0.5,
                 truncating: bool = False, ):
        y_pred = self.predict(x_data,
                              batch_size=batch_size,
                              truncating=truncating,
                              multi_label_threshold=multi_label_threshold)

        original_report = sklearn_metrics.classification_report(y_data,
                                                                    y_pred,
                                                                    output_dict=True,
                                                                    digits=digits)
        print(sklearn_metrics.classification_report(y_data,
                                                        y_pred,
                                                        output_dict=False,
                                                        digits=digits))
        report = {
                'detail': original_report,
                **original_report['weighted avg']
            }
        return report

    @classmethod
    def load_model(cls, model_path):

        model_config_path = os.path.join(model_path, 'model_config.json')
        model_config = json.loads(open(model_config_path, 'r').read())
        model = load_data_object(model_config)
        model.epoch = model_config['epoch']

        tf_model_str = json.dumps(model_config['tf_model'])
        model.tf_model = tf.keras.models.model_from_json(tf_model_str)

        model.tf_model.load_weights(os.path.join(model_path, 'model_weights.h5'))

        return model


if __name__ == "__main__":
    pass
