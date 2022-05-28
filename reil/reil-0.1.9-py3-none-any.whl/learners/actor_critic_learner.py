# -*- coding: utf-8 -*-
'''
A2CLearner class
================

The A2CLearner learner, comprised of an optional shared backbone, an actor
segment with softmax outputs, and a critic output.
'''

import datetime
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import tensorflow as tf
import tensorflow.keras.optimizers.schedules as k_sch
import tensorflow_probability as tfp
from reil.datatypes.feature import FeatureSet
from reil.learners.learner import Learner
from reil.utils.tf_utils import ActionRank, TF2UtilsMixin
from tensorflow import keras

ACLabelType = Tuple[Tuple[Tuple[int, ...], ...], float]

huber_loss = tf.keras.losses.Huber(reduction=tf.keras.losses.Reduction.SUM)

eps = np.finfo(np.float32).eps.item()


@keras.utils.register_keras_serializable(
    package='reil.learners.actor_critic_learner')
class DeepA2CModel(keras.Model):
    def __init__(
        self,
        output_lengths: Tuple[int, ...],
        learning_rate: Union[
            float, k_sch.LearningRateSchedule],
        shared_layer_sizes: Tuple[int, ...],
        actor_layer_sizes: Tuple[int, ...] = (),
        critic_layer_sizes: Tuple[int, ...] = (),
        critic_loss_coef: float = 1.0,
        entropy_loss_coef: float = 0.0,
    ):
        super().__init__()

        self._output_lengths = output_lengths
        self._shared_layer_sizes = shared_layer_sizes
        self._actor_layer_sizes = actor_layer_sizes
        self._critic_layer_sizes = critic_layer_sizes
        self._critic_loss_coef = critic_loss_coef
        self._entropy_loss_coef = entropy_loss_coef
        self._learning_rate = learning_rate

        self._actor_loss = tf.keras.metrics.Mean(
            'actor_loss', dtype=tf.float32)
        self._critic_loss = tf.keras.metrics.Mean(
            'critic_loss', dtype=tf.float32)
        self._entropy_loss = tf.keras.metrics.Mean(
            'entropy_loss', dtype=tf.float32)
        self._total_loss = tf.keras.metrics.Mean(
            'total_loss', dtype=tf.float32)
        self._actor_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(
            'actor_accuracy', dtype=tf.float32)
        self._action_rank = ActionRank()
        self._return = tf.keras.metrics.Mean(
            'return', dtype=tf.float32)

    def build(self, input_shape: Tuple[int, ...]):
        self._input_shape = [None, *input_shape[1:]]

        self._shared = TF2UtilsMixin.mpl_layers(
            self._shared_layer_sizes, 'relu', 'shared_{i:0>2}')
        self._actor_layers = TF2UtilsMixin.mpl_layers(
            self._actor_layer_sizes, 'relu', 'actor_{i:0>2}')
        self._critic_layers = TF2UtilsMixin.mpl_layers(
            self._critic_layer_sizes, 'relu', 'critic_{i:0>2}')
        self._actor_outputs = TF2UtilsMixin.mpl_layers(
            self._output_lengths, 'softmax', 'actor_output_{i:0>2}')

        self._critic_output = keras.layers.Dense(1, name='critic_output')

        self.compile(optimizer=keras.optimizers.Adam(  # type: ignore
            learning_rate=self._learning_rate))

    def get_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = dict(
            output_lengths=self._output_lengths,
            shared_layer_sizes=self._shared_layer_sizes,
            actor_layer_sizes=self._actor_layer_sizes,
            critic_layer_sizes=self._critic_layer_sizes,
            critic_loss_coef=self._critic_loss_coef,
            entropy_loss_coef=self._entropy_loss_coef,
            learning_rate=self._learning_rate)

        if isinstance(
                self._learning_rate, k_sch.LearningRateSchedule):
            config.update(
                {'learning_rate': k_sch.serialize(self._learning_rate)})

        return config

    @classmethod
    def from_config(cls, config, custom_objects=None):
        if 'learning_rate' in config:
            if isinstance(config['learning_rate'], dict):
                config['learning_rate'] = k_sch.deserialize(
                    config['learning_rate'], custom_objects=custom_objects)
        return cls(**config)

    # Keras cannot save the trace of this tf.function.
    # Also, it seems that Keras calls this inside a tf.function, so no need
    # to do it manually.
    # The line x.set_shape(...) is to make sure tf.function can trace
    # correctly.
    # @tf.function(
    #     input_signature=(
    #         tf.TensorSpec(shape=[None, None]), tf.TensorSpec(shape=[])))
    def call(
        self, inputs: tf.Tensor, training=None
    ) -> Tuple[List[tf.Tensor], List[tf.Tensor]]:
        x = inputs
        x.set_shape(self._input_shape)
        for layer in self._shared:
            x = layer(x, training=training)

        x_actor = x_critic = x

        for layer in self._actor_layers:
            x_actor = layer(x_actor, training=training)

        action_probs: List[tf.Tensor] = [
            layer(x_actor) for layer in self._actor_outputs]

        for layer in self._critic_layers:
            x_critic = layer(x_critic, training=training)

        values: List[tf.Tensor] = self._critic_output(x_critic)

        return action_probs, values

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='X'),
            tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='Y'),
            tf.TensorSpec(shape=[None], dtype=tf.float32, name='returns')))
    def _gradients(
            self, x: tf.Tensor, y: tf.Tensor, returns: tf.Tensor):
        print(f'tracing {self.__class__.__qualname__}._gradients')
        lengths = tf.constant(self._output_lengths)
        starts = tf.pad(lengths[:-1], [[1, 0]])
        ends = tf.math.cumsum(lengths)

        m = len(lengths)

        normalized_returns = tf.divide(
            returns - tf.math.reduce_mean(returns),
            tf.math.reduce_std(returns) + eps,
            name='normalized_returns')

        with tf.GradientTape() as tape:
            action_probs, values = self(x, training=True)
            logits_concat = tf.math.log(
                tf.concat(action_probs, axis=1, name='all_logits') + eps)
            values: tf.Tensor = tf.squeeze(values, name='values', axis=1)

            if self._entropy_loss_coef:
                entropy_loss = self._entropy_loss_coef * tf.reduce_sum(
                    logits_concat * tf.math.exp(logits_concat))
            else:
                entropy_loss = 0.0

            if self._critic_loss_coef:
                critic_loss = self._critic_loss_coef * huber_loss(
                    y_true=values, y_pred=normalized_returns)
            else:
                critic_loss = 0.0

            advantage = tf.stop_gradient(
                tf.subtract(normalized_returns, values, name='advantage'))

            actor_loss = tf.constant(0.0)
            for j in tf.range(m):
                logits_slice = logits_concat[  # type: ignore
                    :, starts[j]:ends[j]]
                y_slice = y[:, j]  # type: ignore
                action_probs = tfp.distributions.Categorical(
                    logits=logits_slice)
                log_prob = action_probs.log_prob(y_slice)
                _loss = -tf.reduce_sum(advantage * tf.squeeze(log_prob))
                actor_loss += _loss

                with tape.stop_recording():
                    self._actor_accuracy.update_state(y_slice, logits_slice)
                    self._action_rank.update_state(y_slice, logits_slice)

            total_loss = actor_loss + critic_loss + entropy_loss

        if self._critic_loss_coef:
            self._critic_loss.update_state(critic_loss)
        if self._entropy_loss_coef:
            self._entropy_loss.update_state(entropy_loss)

        self._actor_loss.update_state(actor_loss)
        self._total_loss.update_state(total_loss)

        return tape.gradient(total_loss, self.trainable_variables)

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='X'),
            tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='Y'),
            tf.TensorSpec(shape=[None], dtype=tf.float32, name='returns')))
    def _metrics_only(
            self, x: tf.Tensor, y: tf.Tensor, returns: tf.Tensor):
        print(f'tracing {self.__class__.__qualname__}._metrics_only')
        lengths = tf.constant(self._output_lengths)
        starts = tf.pad(lengths[:-1], [[1, 0]])
        ends = tf.math.cumsum(lengths)

        m = len(lengths)

        normalized_returns = tf.divide(
            returns - tf.math.reduce_mean(returns),
            tf.math.reduce_std(returns) + eps,
            name='normalized_returns')

        action_probs, values = self(x, training=False)
        logits_concat = tf.math.log(
            tf.concat(action_probs, axis=1, name='all_logits') + eps)
        values: tf.Tensor = tf.squeeze(values, name='values', axis=1)

        if self._entropy_loss_coef:
            entropy_loss = self._entropy_loss_coef * tf.reduce_sum(
                logits_concat * tf.math.exp(logits_concat))
        else:
            entropy_loss = 0.0

        if self._critic_loss_coef:
            critic_loss = self._critic_loss_coef * huber_loss(
                y_true=values, y_pred=normalized_returns)
        else:
            critic_loss = 0.0

        advantage = tf.stop_gradient(
            tf.subtract(normalized_returns, values, name='advantage'))

        actor_loss = tf.constant(0.0)
        for j in tf.range(m):
            logits_slice = logits_concat[  # type: ignore
                :, starts[j]:ends[j]]
            y_slice = y[:, j]  # type: ignore
            action_probs = tfp.distributions.Categorical(
                logits=logits_slice)
            log_prob = action_probs.log_prob(y_slice)
            _loss = -tf.reduce_sum(advantage * tf.squeeze(log_prob))
            actor_loss += _loss

            self._actor_accuracy.update_state(y_slice, logits_slice)
            self._action_rank.update_state(y_slice, logits_slice)

        total_loss = actor_loss + critic_loss + entropy_loss

        if self._critic_loss_coef:
            self._critic_loss.update_state(critic_loss)
        if self._entropy_loss_coef:
            self._entropy_loss.update_state(entropy_loss)

        self._actor_loss.update_state(actor_loss)
        self._total_loss.update_state(total_loss)

    def train_step(self, data):
        x, (y, returns) = data

        self._return.update_state(tf.reduce_mean(returns))

        gradient = self._gradients(x, y, returns)

        # If wanted to graph _gradients function in Tensorboard.
        # ------------------------------------------------------
        # if self._iteration:
        #     gradient = self._gradients(_X, _Y, G)
        # else:
        #     tf.summary.trace_on(graph=True, profiler=True)
        #     gradient = self._gradients(_X, _Y, G)
        #     with self._train_summary_writer.as_default():
        #         tf.summary.trace_export(
        #             name='gradient',
        #             step=0,
        #             profiler_outdir=str(self._tensorboard_path)
        #         )

        self.optimizer.apply_gradients(zip(gradient, self.trainable_variables))

        metrics = {metric.name: metric.result() for metric in self.metrics}

        metrics.update({loss.name: loss.result() for loss in self.losses})

        return metrics

    def test_step(self, data):
        x, (y, returns) = data

        self._return.update_state(returns[0])

        self._metrics_only(x, y, returns)

        metrics = {metric.name: metric.result() for metric in self.metrics}

        metrics.update({loss.name: loss.result() for loss in self.losses})

        return metrics


@keras.utils.register_keras_serializable(
    package='reil.learners.actor_critic_learner')
class DeepA2CActionProximityModel(DeepA2CModel):
    def __init__(
            self,
            output_lengths: Tuple[int, ...],
            learning_rate: Union[float, k_sch.LearningRateSchedule],
            shared_layer_sizes: Tuple[int, ...],
            actor_layer_sizes: Tuple[int, ...] = (),
            critic_layer_sizes: Tuple[int, ...] = (),
            critic_loss_coef: float = 1.,
            entropy_loss_coef: float = 0.,
            effect_widths: Union[int, Tuple[int, ...]] = 0,
            effect_decay_factors: Union[float, Tuple[float, ...]] = 0.,
            effect_temporal_decay_factors: Union[float, Tuple[float, ...]] = 1.
    ):
        super().__init__(
            output_lengths=output_lengths,
            learning_rate=learning_rate,
            shared_layer_sizes=shared_layer_sizes,
            actor_layer_sizes=actor_layer_sizes,
            critic_layer_sizes=critic_layer_sizes,
            critic_loss_coef=critic_loss_coef,
            entropy_loss_coef=entropy_loss_coef,
        )

        output_heads = len(output_lengths)
        if isinstance(effect_widths, int):
            _effect_widths = [effect_widths] * output_heads
        elif not effect_widths:
            _effect_widths = [0] * output_heads
        elif len(effect_widths) != output_heads:
            raise ValueError(
                'effect_widths should be an int or a tuple of size '
                f'{output_heads}.')
        else:
            _effect_widths = effect_widths

        if isinstance(effect_decay_factors, float) or not effect_decay_factors:
            _effect_decay_factors = [effect_decay_factors] * output_heads
        elif not effect_decay_factors:
            _effect_decay_factors = [0.] * output_heads
        elif len(effect_decay_factors) != output_heads:
            raise ValueError(
                'effect_decay_factors should be a float or a tuple of size '
                f'{output_heads}.')
        else:
            _effect_decay_factors = effect_decay_factors

        if isinstance(effect_temporal_decay_factors, float):
            _effect_temporal_decay_factors = (
                [effect_temporal_decay_factors] * output_heads)
        elif not effect_temporal_decay_factors:
            _effect_temporal_decay_factors = [0.] * output_heads
        elif len(effect_temporal_decay_factors) != output_heads:
            raise ValueError(
                'effect_temporal_decay_factors should be a float or '
                f' a tuple of size {output_heads}.')
        else:
            _effect_temporal_decay_factors = effect_temporal_decay_factors

        self._effect_widths = tf.constant(
            _effect_widths, name='effect_width', dtype=tf.int32)
        self._effect_decay_factors = tf.constant(
            _effect_decay_factors, name='effect_decay_factors',
            dtype=tf.float32)
        self._effect_temporal_decay_factors = tf.constant(
            _effect_temporal_decay_factors,
            name='effect_temporal_decay_factors', dtype=tf.float32)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update(dict(
            effect_widths=tuple(self._effect_widths.numpy()),
            effect_decay_factors=tuple(self._effect_decay_factors.numpy()),
            effect_temporal_decay_factors=tuple(
                self._effect_temporal_decay_factors.numpy()),
        ))

        return config

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='X'),
            tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='Y'),
            tf.TensorSpec(shape=[None], dtype=tf.float32, name='returns'),
            # tf.TensorSpec(shape=[], dtype=tf.int32, name='iteration')
        ))
    def _gradients(
            self, x: tf.Tensor, y: tf.Tensor,
            returns: tf.Tensor):  # , iteration: tf.Tensor):
        # To avoid "UserWarning: Converting sparse IndexedSlices to a dense
        # Tensor of unknown shape", I used `tf.dynamic_partition` instead of
        # `tf.gather`
        print(f'tracing {self.__class__.__qualname__}._gradients')
        lengths = tf.constant(self._output_lengths)
        starts = tf.pad(lengths[:-1], [[1, 0]])
        ends = tf.math.cumsum(lengths)

        m = len(lengths)

        returns = tf.divide(
            returns - tf.math.reduce_mean(returns),
            tf.math.reduce_std(returns) + eps,
            name='normalized_returns')

        with tf.GradientTape() as tape:
            action_probs, values = self(x, training=True)
            logits_concat = tf.math.log(
                tf.concat(action_probs, axis=1, name='all_logits') + eps)
            values: tf.Tensor = tf.squeeze(values, name='values', axis=1)

            if self._entropy_loss_coef:
                entropy_loss = self._entropy_loss_coef * tf.reduce_sum(
                    logits_concat * tf.math.exp(logits_concat))
            else:
                entropy_loss = 0.0

            if self._critic_loss_coef:
                critic_loss = self._critic_loss_coef * huber_loss(
                    y_true=values, y_pred=returns)
            else:
                critic_loss = 0.0

            advantage = tf.stop_gradient(
                tf.subtract(returns, values, name='advantage'))

            actor_loss = tf.constant(0.0)
            for j in tf.range(m):
                logits_slice = logits_concat[  # type: ignore
                    :, starts[j]:ends[j]]
                action_probs = tfp.distributions.Categorical(
                    logits=logits_slice)
                y_slice = y[:, j]  # type: ignore
                j_one_hot = tf.one_hot(j, depth=m, dtype=tf.int32)

                # effect_width = tf.gather(self._effect_widths, j)
                effect_width = tf.dynamic_partition(  # type: ignore
                    self._effect_widths, j_one_hot, 2)[1][0]
                if tf.equal(effect_width, 0):
                    log_prob = action_probs.log_prob(y_slice)
                    _loss = -tf.reduce_sum(advantage * tf.squeeze(log_prob))
                    actor_loss += _loss
                else:
                    for diff in tf.range(-effect_width, effect_width + 1):
                        temp = y_slice + diff
                        # _length = tf.less(temp, tf.gather(lengths, j))
                        _length = tf.dynamic_partition(  # type: ignore
                            lengths, j_one_hot, 2)[1][0]
                        in_range_indicator = tf.logical_and(
                            tf.greater_equal(temp, 0),
                            tf.less(temp, _length))

                        if not tf.reduce_all(in_range_indicator):
                            continue

                        in_range_indices = tf.cast(
                            in_range_indicator, tf.int32)

                        advantage_in_range = tf.dynamic_partition(  # type: ignore
                            advantage, in_range_indices, 2)[1]

                        log_prob = action_probs.log_prob(
                            tf.where(in_range_indicator, temp, 0))
                        log_prob_in_range = tf.dynamic_partition(  # type: ignore
                            log_prob, in_range_indices, 2)[1]

                        abs_diff = tf.cast(tf.abs(diff), dtype=tf.float32)
                        # effect_decay = tf.gather(self._effect_decay_factors, j)
                        effect_decay = tf.dynamic_partition(  # type: ignore
                            self._effect_decay_factors, j_one_hot, 2)[1][0]
                        effect = tf.pow(
                            effect_decay, abs_diff
                        )  # * tf.pow(
                        #    self._effect_temporal_decay_factors[j], abs_diff)

                        _loss = -tf.reduce_sum(
                            effect * advantage_in_range * log_prob_in_range)
                        actor_loss += _loss

                self._actor_accuracy.update_state(y_slice, logits_slice)
                self._action_rank.update_state(y_slice, logits_slice)

            total_loss = actor_loss + critic_loss + entropy_loss

        if self._critic_loss_coef:
            self._critic_loss.update_state(critic_loss)
        if self._entropy_loss_coef:
            self._entropy_loss.update_state(entropy_loss)

        self._actor_loss.update_state(actor_loss)
        self._total_loss.update_state(total_loss)

        return tape.gradient(total_loss, self.trainable_variables)

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='X'),
            tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='Y'),
            tf.TensorSpec(shape=[None], dtype=tf.float32, name='returns')))
    def _metrics_only(
            self, x: tf.Tensor, y: tf.Tensor, returns: tf.Tensor):
        print(f'tracing {self.__class__.__qualname__}._metrics_only')
        lengths = tf.constant(self._output_lengths)
        starts = tf.pad(lengths[:-1], [[1, 0]])
        ends = tf.math.cumsum(lengths)

        m = len(lengths)

        returns = tf.divide(
            returns - tf.math.reduce_mean(returns),
            tf.math.reduce_std(returns) + eps,
            name='normalized_returns')

        action_probs, values = self(x, training=False)
        logits_concat = tf.math.log(
            tf.concat(action_probs, axis=1, name='all_logits') + eps)
        values: tf.Tensor = tf.squeeze(values, name='values', axis=1)

        if self._entropy_loss_coef:
            entropy_loss = self._entropy_loss_coef * tf.reduce_sum(
                logits_concat * tf.math.exp(logits_concat))
        else:
            entropy_loss = 0.0

        if self._critic_loss_coef:
            critic_loss = self._critic_loss_coef * huber_loss(
                y_true=values, y_pred=returns)
        else:
            critic_loss = 0.0

        advantage = tf.subtract(returns, values, name='advantage')

        actor_loss = tf.constant(0.0)
        for j in tf.range(m):
            logits_slice = logits_concat[  # type: ignore
                :, starts[j]:ends[j]]
            action_probs = tfp.distributions.Categorical(
                logits=logits_slice)
            y_slice = y[:, j]  # type: ignore
            effect_width = tf.gather(self._effect_widths, j)

            if tf.equal(effect_width, 0):
                log_prob = action_probs.log_prob(y_slice)
                _loss = -tf.reduce_sum(advantage * tf.squeeze(log_prob))
                actor_loss += _loss
            else:
                for diff in tf.range(-effect_width, effect_width + 1):
                    temp = y_slice + diff
                    in_range_indicator = tf.logical_and(
                        tf.greater_equal(temp, 0),
                        tf.less(temp, tf.gather(lengths, j)))

                    if not tf.reduce_all(in_range_indicator):
                        continue

                    in_range_indices = tf.cast(
                        in_range_indicator, tf.int32)

                    advantage_in_range = tf.dynamic_partition(  # type: ignore
                        advantage, in_range_indices, 2)[1]

                    log_prob = action_probs.log_prob(
                        tf.where(in_range_indicator, temp, 0))
                    log_prob_in_range = tf.dynamic_partition(  # type: ignore
                        log_prob, in_range_indices, 2)[1]

                    abs_diff = tf.cast(tf.abs(diff), dtype=tf.float32)
                    effect = tf.pow(
                        tf.gather(self._effect_decay_factors, j), abs_diff
                    )  # * tf.pow(
                    #    self._effect_temporal_decay_factors[j], abs_diff)

                    _loss = -tf.reduce_sum(
                        effect * advantage_in_range * log_prob_in_range)
                    actor_loss += _loss

            self._actor_accuracy.update_state(y_slice, logits_slice)
            self._action_rank.update_state(y_slice, logits_slice)

        total_loss = actor_loss + critic_loss + entropy_loss

        if self._critic_loss_coef:
            self._critic_loss.update_state(critic_loss)
        if self._entropy_loss_coef:
            self._entropy_loss.update_state(entropy_loss)

        self._actor_loss.update_state(actor_loss)
        self._total_loss.update_state(total_loss)


class A2CLearner(TF2UtilsMixin, Learner[FeatureSet, ACLabelType]):
    '''
    The DenseSoftMax learner, comprised of a fully-connected with a softmax
    in the output layer.

    This class uses `tf.keras` to build a sequential dense network with one
    output.
    '''

    def __init__(
            self,
            model: DeepA2CModel,
            tensorboard_path: Optional[Union[str, pathlib.PurePath]] = None,
            tensorboard_filename: Optional[str] = None,
            **kwargs: Any) -> None:
        '''
        Arguments
        ---------
        tensorboard_path:
            A path to save tensorboard outputs. If not provided,
            tensorboard will be disabled.
        '''

        super().__init__(models={'_model': type(model)}, **kwargs)

        self._model = model

        self._iteration = 0

        self._tensorboard_path: Optional[pathlib.PurePath] = None
        if (tensorboard_path or tensorboard_filename) is not None:
            current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self._tensorboard_path = pathlib.PurePath(
                tensorboard_path or './logs')
            self._tensorboard_filename = current_time + (
                f'-{tensorboard_filename}' or '')
            self._train_summary_writer = \
                tf.summary.create_file_writer(  # type: ignore
                    str(
                        self._tensorboard_path /
                        self._tensorboard_filename / 'train'))

            # self._validation_summary_writer = \
            #     tf.summary.create_file_writer(  # type: ignore
            #     str(
            #         self._tensorboard_path /
            #         self._tensorboard_filename / 'validation'))

    def predict(
            self, X: Tuple[FeatureSet, ...], training: Optional[bool] = None
    ) -> Tuple[ACLabelType, ...]:
        '''
        predict `y` for a given input list `X`.

        Arguments
        ---------
        X:
            A list of `FeatureSet` as inputs to the prediction model.

        training:
            Whether the learner is in training mode. (Default = None)

        Returns
        -------
        :
            The predicted `y`.
        '''
        return self._model(self.convert_to_tensor(X), training=training)

    def learn(
            self, X: Tuple[FeatureSet, ...],
            Y: Tuple[ACLabelType, ...]) -> Dict[str, float]:
        '''
        Learn using the training set `X` and `Y`.

        Arguments
        ---------
        X:
            A list of `FeatureSet` as inputs to the learning model.

        Y:
            A list of float labels for the learning model.
        '''
        _X = self.convert_to_tensor(X)
        if len(_X.shape) == 1:
            _X = tf.expand_dims(_X, axis=0)

        Y_temp, G_temp = tuple(zip(*Y))
        G = tf.convert_to_tensor(G_temp, dtype=tf.float32)
        _Y: tf.Tensor = tf.convert_to_tensor(Y_temp)

        metrics = self._model.fit(
            x=_X, y=(_Y, G), verbose=0).history  # type: ignore

        if self._train_summary_writer:
            training_metrics = {
                key: value
                for key, value in metrics.items()
                if not key.startswith('val_')}

            # validation_metrics = {
            #     key[4:]: value
            #     for key, value in metrics.items()
            #     if key.startswith('val_')}

            with self._train_summary_writer.as_default(step=self._iteration):
                for name, value in training_metrics.items():
                    tf.summary.scalar(name, value[0])

            # with self._validation_summary_writer.as_default(
            #         step=self._iteration):
            #     for name, value in validation_metrics.items():
            #         tf.summary.scalar(name, value[0])

        self._iteration += 1

        return metrics

    def get_parameters(self) -> Any:
        return self._model.get_weights()

    def set_parameters(self, parameters: Any):
        self._model.set_weights(parameters)

    def __getstate__(self):
        state = super().__getstate__()
        state['_train_summary_writer'] = None
        # state['_validation_summary_writer'] = None
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        super().__setstate__(state)

        if self._tensorboard_path:
            self._train_summary_writer = \
                tf.summary.create_file_writer(  # type: ignore
                    str(
                        self._tensorboard_path /
                        self._tensorboard_filename / 'train'))

            # self._validation_summary_writer = \
            #     tf.summary.create_file_writer(  # type: ignore
            #     str(
            #         self._tensorboard_path /
            #         self._tensorboard_filename / 'validation'))
