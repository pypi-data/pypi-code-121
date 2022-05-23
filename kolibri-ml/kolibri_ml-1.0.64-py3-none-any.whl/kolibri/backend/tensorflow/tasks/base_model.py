import json
import os
import pathlib
import tempfile
import time
from abc import abstractmethod
from typing import Dict, Any

import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, LambdaCallback

import kolibri

from kolibri.logger import get_logger

logger = get_logger(__name__)


class TaskBaseModel(object):

    def __init__(self, sequence_length=None, hyper_parameters=None):#, multi_label=False, label_indexer=None):

        self.hyper_parameters = self.get_default_hyper_parameters()
        # combine with base class hyperparameters
        self.hyper_parameters.update(TaskBaseModel.get_default_hyper_parameters())

        if hyper_parameters:
            self.update_hyper_parameters(hyper_parameters)
        self.epoch = 0
        self.tf_model: tf.keras.Model = None
        self.checkpoint_model_path = ""
        self.sequence_length: int
        self.sequence_length = sequence_length
#        self.multi_label = multi_label
#        if label_indexer is None:
#            self.label_indexer = LabelIndexer(multi_label=multi_label)

    def to_dict(self) -> Dict[str, Any]:
        model_json_str = self.tf_model.to_json()

        return {
            'tf_version': tf.__version__,  # type: ignore
            'kolibri_version': kolibri.__version__,
#            'label_indexer': self.label_indexer.to_dict(),
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'epoch': self.epoch,
            'config': {
                'hyper_parameters': self.hyper_parameters,  # type: ignore
            },
            'tf_model': json.loads(model_json_str)
        }

    def update_hyper_parameters(self, parameters):
        if self.hyper_parameters is None:
            return

        for k, v in parameters.items():
            if k in self.hyper_parameters:
                self.hyper_parameters[k] = v

    @classmethod
    def get_default_hyper_parameters(cls):

        return {
            'save_best': False,
            'early_stop': False,
            'monitor': 'val_accuracy',
            'mode': 'max',
            'early_stopping_patience': 3,
            'epochs': 2
        }

    def fit(self, train_data_gen, val_data_gen, callbacks, fit_kwargs):

        def on_epoch_end(_a, _b):
            self.epoch += 1

        if val_data_gen is not None:
            if callbacks is None:
                callbacks = []
            if LambdaCallback(on_epoch_end=on_epoch_end) not in callbacks:
                callbacks.append(LambdaCallback(on_epoch_end=on_epoch_end))

            if self.hyper_parameters['save_best']:
                self.checkpoint_model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
                pathlib.Path(self.checkpoint_model_path).mkdir(parents=True, exist_ok=True)
                self.checkpoint_model_path = os.path.join(self.checkpoint_model_path, 'best_weights.h5')
                callbacks.append(
                    ModelCheckpoint(filepath=self.checkpoint_model_path, monitor=self.hyper_parameters['monitor'],
                                    save_best_only=True, verbose=1, mode=self.hyper_parameters['mode']))
            if self.hyper_parameters['early_stop']:
                callbacks.append(EarlyStopping(monitor=self.hyper_parameters['monitor'],
                                               patience=self.hyper_parameters['early_stopping_patience']))

        history = self.tf_model.fit(train_data_gen,
                                    steps_per_epoch=len(train_data_gen),
                                    epochs=self.epoch + self.hyper_parameters['epochs'],
                                    initial_epoch=self.epoch,
                                    callbacks=callbacks,
                                    **fit_kwargs)
        if os.path.exists(self.checkpoint_model_path):
            self.tf_model.load_weights(self.checkpoint_model_path)

        return self.tf_model

    def save(self, model_path: str) -> str:
        """
        Save model
        Args:
            model_path:
        """
        pathlib.Path(model_path).mkdir(exist_ok=True, parents=True)
        model_path = os.path.abspath(model_path)
        with open(os.path.join(model_path, 'model_config.json'), 'w') as f:
            info_dict = self.to_dict()
            f.write(json.dumps(info_dict, indent=2, default=str, ensure_ascii=False))
            f.close()

        self.tf_model.save_weights(os.path.join(model_path, 'model_weights.h5'))  # type: ignore
        logger.info('model saved to {}'.format(os.path.abspath(model_path)))
        return model_path

    @classmethod
    def load_model(cls, model_path):
        raise NotImplementedError

    @abstractmethod
    def build_model(self,
                    x_data: Any,
                    y_data: Any) -> None:
        raise NotImplementedError


if __name__ == "__main__":
    path = ''
    m = TaskBaseModel.load_model(path)
    m.tf_model.summary()
