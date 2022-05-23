import json
import os
import threading
from typing import Dict, Any

import numpy as np
# import tensorflow as tf
from sklearn import metrics as sklearn_metrics

import kolibri
from kolibri.data.text.generators import DataGenerator
from kolibri.backend.tensorflow.tasks.base_model import TaskBaseModel
from kolibri.backend.tensorflow.layers import L
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.logger import get_logger
import tensorflow as tf
logger = get_logger(__name__)

from kdmt.ml.metrics.multi_label_classification import multi_label_classification_report

threading._DummyThread._Thread__stop = lambda x: 42


class BaseAudioClassificationModel(TaskBaseModel):
    """
    Abstract Audio Classification Model
    """

    __task__ = 'classification'

    def to_dict(self) -> Dict:
        info = super(BaseAudioClassificationModel, self).to_dict()
        info['config']['multi_label'] = self.multi_label
        return info

    def __init__(self, sequence_length=None, hyper_parameters=None, multi_label: bool = False, label_indexer=None):
        """

        Args:
            embedding: embedding object
            sequence_length: target sequence length_train
            hyper_parameters: hyper_parameters to overwrite
            multi_label: is multi-label classification
            label_indexer: label processor
        """
        super().__init__(sequence_length, hyper_parameters, multi_label, label_indexer)

    def _activation_layer(self) -> L.Layer:
        if self.multi_label:
            return L.Activation('sigmoid')
        else:
            return L.Activation('softmax')

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
        self.build_model_generator([train_gen])

    def build_model_generator(self, generators):
        self.label_indexer.build_vocab_generator(generators)

        if self.tf_model is None:
            self.build_model_arc()
        self.compile_model()

    @classmethod
    def get_default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError

    def build_model_arc(self) -> None:
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
        if loss is None:
            if self.multi_label:
                loss = 'binary_crossentropy'
            else:
                loss = 'sparse_categorical_crossentropy'
        if optimizer is None:
            optimizer = 'adam'
        if metrics is None:
            metrics = ['accuracy']

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)

    def fit(self, x_train, y_train, x_validate=None, y_validate=None,
            *,
            batch_size: int = 64,
            epochs: int = 5,
            callbacks=None,
            fit_kwargs={}):
        """
        Trains the model for a given number of epochs with given texts set list.
        """
        train_gen = tf.data.Dataset.from_tensor_slices((x_train, y_train))
        if x_validate is not None:
            valid_gen = tf.data.Dataset.from_tensor_slices((x_validate, y_validate))
        else:
            valid_gen = None
        return self.fit_generator(train_sample_gen=train_gen,
                                  valid_sample_gen=valid_gen,
                                  batch_size=batch_size,
                                  epochs=epochs,
                                  callbacks=callbacks,
                                  fit_kwargs=fit_kwargs)

    def fit_generator(self, train_sample_gen, valid_sample_gen=None,
                      *,
                      batch_size: int = 64,
                      epochs: int = 5,
                      callbacks=None,
                      fit_kwargs: Dict = {}):

        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])

        model_summary = []
        self.tf_model.summary(print_fn=lambda x: model_summary.append(x))
        logger.debug('\n'.join(model_summary))

        train_set = train_sample_gen
        train_set.label_indexer = self.label_indexer
        train_set.batch_size = batch_size

        if fit_kwargs is None:
            fit_kwargs = {}
        valid_gen = None
        if valid_sample_gen:
            valid_gen = valid_sample_gen
            valid_gen.label_indexer = self.label_indexer
            valid_gen.batch_size = batch_size

            fit_kwargs['validation_data'] = valid_gen
            fit_kwargs['validation_steps'] = len(valid_gen)

        return super(BaseAudioClassificationModel, self).fit(train_set, valid_gen, callbacks, fit_kwargs)

    def predict(self, x_data, *,
                batch_size: int = 32,
                truncating: bool = False,
                multi_label_threshold: float = 0.5,
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
        with kolibri.backend.custom_object_scope():
            if truncating:
                seq_length = self.sequence_length
            else:
                seq_length = None

            # for i in range(len(self.wav_paths)):
            #     rate, wav = wavfile.read(self.wav_paths[i])
            #     yield wav.reshape(1, -1), self.y_values[i]
            tensor = x_data
            logger.debug(f'predict input shape {np.array(tensor).shape}')
            pred = self.tf_model.predict(tensor, batch_size=batch_size, **predict_kwargs)
            logger.debug(f'predict output shape {pred.shape}')
            if self.multi_label:
                multi_label_binarizer = self.label_indexer.multi_label_binarizer  # type: ignore
                res = multi_label_binarizer.inverse_transform(pred,
                                                              threshold=multi_label_threshold)
            else:
                pred_argmax = pred.argmax(-1)
                res = [dict(zip(self.label_indexer.inverse_transform([i for i in range(0, len(p))]), p)) for p in pred]
                logger.debug(f'predict output argmax: {pred_argmax}')

        return res

    def evaluate(self, x_data, y_data, *,
                 batch_size: int = 32,
                 digits: int = 4,
                 multi_label_threshold: float = 0.5,
                 truncating: bool = False, ):
        y_pred = self.predict(x_data,
                              batch_size=batch_size,
                              truncating=truncating,
                              multi_label_threshold=multi_label_threshold)

        if self.multi_label:
            report = multi_label_classification_report(y_data,  # type: ignore
                                                       y_pred,  # type: ignore
                                                       binarizer=self.label_indexer.multi_label_binarizer)  # type: ignore

        else:
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
        from kolibri.backend.tensorflow.layers import Melspectrogram, Normalization2D
        model_config_path = os.path.join(model_path, 'model_config.json')
        model_config = json.loads(open(model_config_path, 'r').read())
        model = load_data_object(model_config)
        model.epoch = model_config['epoch']
        model.label_indexer = load_data_object(model_config['label_indexer'])

        tf_model_str = json.dumps(model_config['tf_model'])
        model.tf_model = tf.keras.models.model_from_json(tf_model_str, {'Melspectrogram': Melspectrogram,
                                                                        'Normalization2D': Normalization2D})

        model.tf_model.load_weights(os.path.join(model_path, 'model_weights.h5'))

        return model


if __name__ == "__main__":
    pass
