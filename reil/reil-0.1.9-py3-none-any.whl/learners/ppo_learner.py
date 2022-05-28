# -*- coding: utf-8 -*-
'''
PPOLearner class
================

'''

import datetime
import pathlib
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np

import tensorflow as tf
import tensorflow.keras.optimizers.schedules as k_sch
from reil.datatypes.feature import FeatureSet
from reil.learners.learner import Learner
from reil.utils.tf_utils import ActionRank, TF2UtilsMixin
from tensorflow import keras

ACLabelType = Tuple[Tuple[Tuple[int, ...], ...], float]

eps = np.finfo(np.float32).eps.item()


@keras.utils.register_keras_serializable(
    package='reil.learners.ppo_learner')
class PPOModel(TF2UtilsMixin):
    def __init__(
            self,
            input_shape: Tuple[int, ...],
            output_lengths: Tuple[int, ...],
            actor_learning_rate: Union[
                float, k_sch.LearningRateSchedule],
            critic_learning_rate: Union[
                float, k_sch.LearningRateSchedule],
            actor_layer_sizes: Tuple[int, ...],
            critic_layer_sizes: Tuple[int, ...],
            actor_train_iterations: int,
            critic_train_iterations: int,
            clip_ratio: float,
            GAE_lambda: float,
            target_kl: float,
            critic_loss_coef: float = 1.0,
            entropy_loss_coef: float = 0.0) -> None:

        super().__init__(models={})

        self._input_shape = input_shape
        self._output_lengths = output_lengths
        self._actor_learning_rate = actor_learning_rate
        self._critic_learning_rate = critic_learning_rate
        self._actor_layer_sizes = actor_layer_sizes
        self._critic_layer_sizes = critic_layer_sizes
        self._actor_train_iterations = actor_train_iterations
        self._critic_train_iterations = critic_train_iterations
        self._clip_ratio = clip_ratio
        self._GAE_lambda = GAE_lambda
        self._target_kl = target_kl
        self._critic_loss_coef = critic_loss_coef
        self._entropy_loss_coef = entropy_loss_coef

        input_ = keras.Input(self._input_shape)
        actor_layers = TF2UtilsMixin.mlp_functional(
            input_, self._actor_layer_sizes, 'relu', 'actor_{i:0>2}')
        logit_heads = TF2UtilsMixin.mpl_layers(
            self._output_lengths, 'softmax', 'actor_output_{i:0>2}')
        logits = [output(actor_layers) for output in logit_heads]

        self.actor = keras.Model(inputs=input_, outputs=[logits])

        critic_layers = TF2UtilsMixin.mlp_functional(
            input_, self._critic_layer_sizes, 'relu', 'critic_{i:0>2}')
        critic_output = keras.layers.Dense(
            1, name='critic_output')(critic_layers)
        self.critic = keras.Model(inputs=input_, outputs=critic_output)

        self._actor_optimizer = keras.optimizers.Adam(
            learning_rate=self._actor_learning_rate)
        self._critic_optimizer = keras.optimizers.Adam(
            learning_rate=self._critic_learning_rate)

        self._actor_loss = tf.keras.metrics.Mean(
            'actor_loss', dtype=tf.float32)
        self._critic_loss = tf.keras.metrics.Mean(
            'critic_loss', dtype=tf.float32)
        self._advantage_mean = tf.keras.metrics.Mean(
            'critic_loss', dtype=tf.float32)
        self._advantage_std = tf.keras.metrics.Mean(
            'critic_loss', dtype=tf.float32)
        self._actor_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(
            'actor_accuracy', dtype=tf.float32)
        self._action_rank = ActionRank()

        self._models = {
            'actor': type(self.actor),
            'critic': type(self.critic)}

    def __call__(self, inputs, training: Optional[bool] = None) -> Any:
        logits = self.actor(inputs, training)
        values = self.critic(inputs, training)
        return logits, values

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='x'),
            tf.TensorSpec(shape=[None, 1], dtype=tf.int32, name='action_indices'),
            tf.TensorSpec(shape=[None], dtype=tf.float32, name='advantage'),
        )
    )
    def train_actor(
        self, x: tf.Tensor, action_indices: tf.Tensor, advantage: tf.Tensor
    ):
        y = self.actor(x)
        initial_logprobs = self.logprobs(
            y, action_indices, self._output_lengths[0])
        self._action_rank.update_state(tf.squeeze(action_indices), y[0])
        self._advantage_mean.update_state(tf.reduce_mean(advantage))
        self._advantage_std.update_state(tf.math.reduce_std(advantage))
        advantage = tf.divide(
            advantage - tf.math.reduce_mean(advantage),
            tf.math.reduce_std(advantage) + eps,
            name='normalized_advantage')

        for _ in tf.range(self._actor_train_iterations):
            with tf.GradientTape() as tape:
                ratio = tf.exp(
                    self.logprobs(
                        self.actor(x), action_indices, self._output_lengths[0])
                    - initial_logprobs)
                min_advantage = tf.where(
                    tf.greater(advantage, 0.0),
                    tf.multiply(1 + self._clip_ratio, advantage),
                    tf.multiply(1 - self._clip_ratio, advantage)
                )

                actor_loss = -tf.reduce_mean(
                    tf.minimum(ratio * advantage, min_advantage)
                )
            self._actor_loss.update_state(actor_loss)
            trainable_vars = self.actor.trainable_variables
            policy_grads = tape.gradient(actor_loss, trainable_vars)
            self._actor_optimizer.apply_gradients(
                zip(policy_grads, trainable_vars))

            kl = tf.reduce_mean(
                initial_logprobs - self.logprobs(
                    self.actor(x), action_indices, self._output_lengths[0]))
            # kl = tf.reduce_sum(kl)
            if kl > 1.5 * self._target_kl:  # Early Stopping
                break

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None], dtype=tf.float32, name='x'),
            tf.TensorSpec(shape=[None], dtype=tf.float32, name='returns'),
        )
    )
    def train_critic(self, x, returns):
        for _ in tf.range(self._critic_train_iterations):
            with tf.GradientTape() as tape:
                critic_loss = tf.reduce_mean((returns - self.critic(x)) ** 2)

            self._critic_loss.update_state(critic_loss)
            trainable_vars = self.critic.trainable_variables
            value_grads = tape.gradient(critic_loss, trainable_vars)
            self._critic_optimizer.apply_gradients(
                zip(value_grads, trainable_vars))

    @staticmethod
    def logprobs(logits, action_indices, action_count):
        logprobabilities_all = tf.nn.log_softmax(logits)
        logprobability = tf.reduce_sum(
            tf.squeeze(
                tf.one_hot(action_indices, action_count)
            ) * tf.squeeze(logprobabilities_all),
            axis=1)
        # logprobability = tf.reduce_sum(
        #     tf.one_hot(action_indices, action_count) * logprobabilities_all,
        #     axis=1)

        return logprobability

    def train_step(self, data):
        x, (action_indices, returns, advantage) = data
        self.train_actor(x, action_indices, advantage)
        self.train_critic(x, returns)

        metrics = {
            'actor_loss': [self._actor_loss.result()],
            'critic_loss': [self._critic_loss.result()]
        }

        metrics['total_loss'] = [sum(x[0] for x in metrics.values())]

        metrics['action_rank'] = [self._action_rank.result()]
        metrics['advantage_mean'] = [self._advantage_mean.result()]
        metrics['advantage_std'] = [self._advantage_std.result()]

        self._actor_loss.reset_states()
        self._critic_loss.reset_states()
        self._actor_accuracy.reset_states()
        self._action_rank.reset_states()
        self._advantage_mean.reset_states()
        self._advantage_std.reset_states()

        return metrics


class PPOLearner(Learner[FeatureSet, ACLabelType]):
    '''
    PPO Learner
    '''

    def __init__(
            self,
            model: PPOModel,
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

        super().__init__(**kwargs)

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
        return self._model(TF2UtilsMixin.convert_to_tensor(X), training=training)

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
        _X = TF2UtilsMixin.convert_to_tensor(X)
        if len(_X.shape) == 1:
            _X = tf.expand_dims(_X, axis=0)

        action_index_temp, return_temp, advantage_temp = tuple(zip(*Y))
        action_index: tf.Tensor = tf.convert_to_tensor(action_index_temp)
        returns = tf.convert_to_tensor(return_temp, dtype=tf.float32)
        advantage = tf.convert_to_tensor(advantage_temp, dtype=tf.float32)

        metrics = self._model.train_step(
            (_X, (action_index, returns, advantage)))

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
        return (
            self._model.actor.get_weights(), self._model.critic.get_weights())

    def set_parameters(self, parameters: Any):
        self._model.actor.set_weights(parameters[0])
        self._model.critic.set_weights(parameters[1])

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
