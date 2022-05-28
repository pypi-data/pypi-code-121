# -*- coding: utf-8 -*-
'''
PPO class
=========

A Proximal Policy Optimization Policy Gradient `agent`.
'''

from typing import Any, Optional, Tuple
import numpy as np

import tensorflow as tf
from reil.agents.actor_critic import A2C
from reil.agents.agent import TrainingData
from reil.datatypes import History
from reil.datatypes.buffers.buffer import Buffer
from reil.datatypes.feature import FeatureSet
from reil.learners.ppo_learner import PPOLearner
from reil.utils.exploration_strategies import NoExploration


ACLabelType = Tuple[Tuple[Tuple[int, ...], ...], float]


class PPO(A2C):
    '''
    A Proximal Policy Optimization `agent`.
    '''

    def __init__(
            self,
            learner: PPOLearner,
            buffer: Buffer[FeatureSet, Tuple[Tuple[int, ...], float, float]],
            reward_clip: Tuple[Optional[float], Optional[float]] = (None, None),
            gae_lambda: float = 1.0,
            **kwargs: Any):
        '''
        Arguments
        ---------
        learner:
            the `Learner` object that does the learning.

        discount_factor:
            by what factor should future rewards be discounted?

        training_mode:
            whether the agent is in training mode or not.

        tie_breaker:
            how to choose the `action` if more than one is candidate
            to be chosen.
        '''
        super(A2C, self).__init__(
            learner=learner, exploration_strategy=NoExploration(),
            variable_action_count=False,
            **kwargs)

        self._buffer = buffer
        self._buffer.setup(buffer_names=['state', 'y_r_a'])
        self._reward_clip = reward_clip
        self._gae_lambda = gae_lambda

    def _prepare_training(
            self, history: History) -> TrainingData[FeatureSet, int]:
        '''
        Use `history` to create the training set in the form of `X` and `y`
        vectors.

        Arguments
        ---------
        history:
            a `History` object from which the `agent` learns.

        Returns
        -------
        :
            a `TrainingData` object that contains `X` and 'y` vectors

        :meta public:
        '''
        state: FeatureSet
        action_index: Tuple[int, ...]

        discount_factor = self._discount_factor
        active_history = self.get_active_history(history)

        # add zero to the end to have the correct length of `deltas`
        rewards = self.extract_reward(
            active_history, *self._reward_clip) + [0.0]
        disc_reward = self.discounted_cum_sum(rewards, discount_factor)

        state_list: Tuple[FeatureSet, ...] = tuple(  # type: ignore
            h.state for h in active_history)
        # add zero to the end to have the correct length of `deltas`
        values = np.append(
            tf.reshape(self._learner.predict(state_list)[1], -1), 0.0)
        deltas = rewards[:-1] + discount_factor * values[1:] - values[:-1]
        advantage = self.discounted_cum_sum(
            deltas, discount_factor * self._gae_lambda)

        for h, r, a in zip(active_history, disc_reward, advantage):
            state = h.state  # type: ignore
            action_index = tuple((
                h.action_taken or h.action).index.values())  # type: ignore
            self._buffer.add(
                {'state': state, 'y_r_a': (action_index, r, a)})

        temp = self._buffer.pick()

        return temp['state'], temp['y_r_a'], {}  # type: ignore
