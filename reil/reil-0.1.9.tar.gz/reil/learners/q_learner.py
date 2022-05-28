# -*- coding: utf-8 -*-
'''
Dense class
===========

The Dense learner.
'''
import datetime
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import tensorflow as tf
import tensorflow.keras.optimizers.schedules as k_sch
from reil.datatypes.feature import FeatureSet
from reil.learners.learner import Learner
from reil.utils.tf_utils import (ArgMaxLayer, BroadcastAndConcatLayer,
                                 MaxLayer, TF2UtilsMixin)
from tensorflow import keras


class DeepQModel(keras.Model):
    def __init__(
            self,
            learning_rate: Union[
                float, keras.optimizers.schedules.LearningRateSchedule],
            validation_split: float = 0.0,
            hidden_layer_sizes: Tuple[int, ...] = (1,)):
        super().__init__()

        if not 0.0 <= validation_split < 1.0:
            raise ValueError('validation split should be in [0.0, 1.0).')

        self._validation_split = validation_split
        self._hidden_layer_sizes = hidden_layer_sizes
        self._learning_rate = learning_rate

    def build(self, input_shape: Tuple[Tuple[int, ...], Tuple[int, ...]]):
        self._state_shape = [None, *input_shape[0][1:]]
        self._action_shape = [None, *input_shape[1][1:]]

        self._concat = BroadcastAndConcatLayer(name='concat')

        self._dense_layers = [
            keras.layers.Dense(
                size, activation='relu', name=f'layer_{i:0>2}')
            for i, size in enumerate(self._hidden_layer_sizes, 1)]

        self._output = keras.layers.Dense(1, name='Q')

        self._max_layer = MaxLayer(name='max')
        self._argmax_layer = ArgMaxLayer(name='argmax')

        # self._model = keras.Model(self._inputs, self._output, name='Q_network')
        # self._max = keras.Model(self._inputs, max_layer, name='max_Q')
        # self._argmax = keras.Model(self._inputs, argmax_layer, name='argmax_Q')

        self.compile(
            optimizer=keras.optimizers.Adam(  # type: ignore
                learning_rate=self._learning_rate), loss='mae')

    def call(self, inputs):
        x = inputs
        x[0].set_shape(self._state_shape)
        x[1].set_shape(self._action_shape)

        x = self._concat(x)
        for layer in self._dense_layers:
            x = layer(x)

        return self._output(x)

    @tf.function(
        input_signature=((
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='states'),
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='actions')),))
    def max(self, inputs):
        return self._max_layer(self(inputs))

    @tf.function(
        input_signature=((
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='states'),
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='actions')),))
    def argmax(self, inputs):
        return self._argmax_layer(self(inputs))

    def fit(
            self, x=None, y=None, batch_size=None, epochs=1, verbose=1,
            callbacks=None, validation_split=0, validation_data=None,
            shuffle=True, class_weight=None, sample_weight=None,
            initial_epoch=0, steps_per_epoch=None, validation_steps=None,
            validation_batch_size=None, validation_freq=1,
            max_queue_size=10, workers=1, use_multiprocessing=False):

        try:
            return super().fit(
                x, y, batch_size, epochs, verbose, callbacks,
                validation_split or self._validation_split, validation_data,
                shuffle, class_weight, sample_weight,
                initial_epoch, steps_per_epoch,
                validation_steps, validation_batch_size, validation_freq,
                max_queue_size, workers, use_multiprocessing)
        except RuntimeError:
            self.__call__(x)
            return super().fit(
                x, y, batch_size, epochs, verbose, callbacks,
                validation_split or self._validation_split, validation_data,
                shuffle, class_weight, sample_weight,
                initial_epoch, steps_per_epoch,
                validation_steps, validation_batch_size, validation_freq,
                max_queue_size, workers, use_multiprocessing)

    def get_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = dict(
            validation_split=self._validation_split,
            hidden_layer_sizes=self._hidden_layer_sizes)

        if isinstance(
                self._learning_rate, k_sch.LearningRateSchedule):
            config.update(
                {'learning_rate': k_sch.serialize(self._learning_rate)})
        else:
            config['learning_rate'] = self._learning_rate

        return config

    @classmethod
    def from_config(cls, config, custom_objects=None):
        if 'learning_rate' in config:
            if isinstance(config['learning_rate'], dict):
                config['learning_rate'] = k_sch.deserialize(
                    config['learning_rate'], custom_objects=custom_objects)

        return cls(**config)


class QLearner(TF2UtilsMixin, Learner[Tuple[FeatureSet, ...], float]):
    '''
    The Dense learner for Q learning.

    This class uses `tf.keras` to build a sequential dense network with one
    output.
    '''

    def __init__(
            self,
            model: DeepQModel,
            tensorboard_path: Optional[Union[str, pathlib.PurePath]] = None,
            tensorboard_filename: Optional[str] = None,
            **kwargs: Any) -> None:
        '''
        Arguments
        ---------
        learning_rate:
            A `LearningRateScheduler` object that determines the learning rate
            based on iteration. If any scheduler other than constant is
            provided, the model uses the `new_rate` method of the scheduler
            to determine the learning rate at each iteration.

        validation_split:
            How much of the training set should be used for validation?

        hidden_layer_sizes:
            A list of number of neurons for each layer.

        input_lengths:
            Size of the input data. If not supplied, the network will be
            generated based on the size of the first data point in `predict` or
            `learn` methods. The inputs correspond to states and actions in
            `Qlearning`.

        tensorboard_path:
            A path to save tensorboard outputs. If not provided,
            tensorboard will be disabled.

        Raises
        ------
        ValueError
            Validation split not in the range of (0.0, 1.0).
        '''

        super().__init__({'_model': type(model)}, **kwargs)

        self._iteration: int = 0

        self._model = model

        self._callbacks: List[Any] = []
        self._tensorboard_path: Optional[pathlib.PurePath] = None
        self._tensorboard_filename = tensorboard_filename
        if (tensorboard_path or tensorboard_filename) is not None:
            current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self._tensorboard_path = pathlib.PurePath(
                tensorboard_path or './logs')
            filename = current_time + (f'-{tensorboard_filename}' or '')

            self._tensorboard = keras.callbacks.TensorBoard(
                log_dir=self._tensorboard_path / filename)
            # , histogram_freq=1)  #, write_images=True)
            self._callbacks.append(self._tensorboard)

    @classmethod
    def _empty_instance(cls):  # type: ignore
        return cls(keras.Model())  # type: ignore

    def argmax(
            self, states: Tuple[FeatureSet, ...],
            actions: Tuple[FeatureSet, ...]) -> Tuple[FeatureSet, FeatureSet]:
        _X = [self.convert_to_tensor(states), self.convert_to_tensor(actions)]

        index = self._model.argmax(_X).numpy()[0]
        try:
            state = states[index]
        except IndexError:
            state = states[0]

        try:
            action = actions[index]
        except IndexError:
            action = actions[0]

        return state, action

    def max(
            self, states: Tuple[FeatureSet, ...],
            actions: Tuple[FeatureSet, ...]) -> float:
        return self._model.max([
            self.convert_to_tensor(states), self.convert_to_tensor(actions)])

    def predict(
            self, X: Tuple[Tuple[FeatureSet, ...], ...],
            training: Optional[bool] = None) -> Tuple[float, ...]:
        return self._model(
            [self.convert_to_tensor(x) for x in X])

    def learn(
            self, X: Tuple[Tuple[FeatureSet, ...], ...],
            Y: Tuple[float, ...]) -> Dict[str, float]:
        '''
        Learn using the training set `X` and `Y`.

        Arguments
        ---------
        X:
            A list of `FeatureSet` as inputs to the learning model.

        Y:
            A list of float labels for the learning model.
        '''
        _X = [self.convert_to_tensor(x) for x in X]

        self._iteration += 1

        return self._model.fit(  # type: ignore
            _X, tf.convert_to_tensor(Y),  # type: ignore
            initial_epoch=self._iteration, epochs=self._iteration + 1,
            callbacks=self._callbacks,
            verbose=0).history

    def get_parameters(self) -> Any:
        return self._model.get_weights()

    def set_parameters(self, parameters: Any):
        self._model.set_weights(parameters)

    def reset(self) -> None:
        '''
        reset the learner.
        '''
        self._iteration += 1


if tf.__version__[0] == '1':  # type: ignore
    raise RuntimeError('Dense requires TF version 2.')
