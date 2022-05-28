# -*- coding: utf-8 -*-
'''
DeepQLearning class
===================

A Q-learning `agent` with a Neural Network Q-function approximator.
'''
from typing import Any, Literal, Tuple, Union

import numpy as np

from reil.agents.agent import Agent, TrainingData
from reil.datatypes import History
from reil.datatypes.buffers import Buffer
from reil.datatypes.feature import FeatureSet
from reil.learners.q_learner import QLearner
from reil.utils.exploration_strategies import (ConstantEpsilonGreedy,
                                               ExplorationStrategy)

Feature_or_Tuple_of_Feature = Union[Tuple[FeatureSet, ...], FeatureSet]


class DeepQLearning(Agent[Tuple[FeatureSet, ...], float]):
    '''
    A Deep Q-learning `agent`.
    '''

    def __init__(
            self,
            learner: QLearner,
            buffer: Buffer[FeatureSet, float],
            exploration_strategy: Union[float, ExplorationStrategy],
            method: Literal['forward', 'backward'] = 'backward',
            default_actions: Tuple[FeatureSet, ...] = (),
            **kwargs: Any):
        '''
        Arguments
        ---------
        learner:
            the `Learner` object that does the learning.

        exploration_strategy:
            an `ExplorationStrategy` object that determines
            whether the `action` should be exploratory or not for a given
            `state` at a given `iteration`.

        discount_factor:
            by what factor should future rewards be discounted?

        default_actions:
            a tuple of default actions.

        training_mode:
            whether the agent is in training mode or not.

        tie_breaker:
            how to choose the `action` if more than one is candidate
            to be chosen.
        '''
        super().__init__(
            learner=learner, exploration_strategy=exploration_strategy,
            variable_action_count=True,
            **kwargs)
        self._learner: QLearner

        self._method: Literal['forward', 'backward'] = method
        if method not in ('backward', 'forward'):
            self._logger.warning(
                f'method {method} is not acceptable. Should be '
                'either "forward" or "backward". Will use "backward".')
            self._method = 'backward'

        if method == 'forward' and not default_actions:
            raise ValueError(
                'forward method requires `default_actions` to be non-empty.')

        self._default_actions = default_actions
        self._buffer = buffer
        self._buffer.setup(buffer_names=['state', 'action', 'Y'])

    @classmethod
    def _empty_instance(cls):  # type: ignore
        return cls(
            QLearner._empty_instance(), Buffer(), ConstantEpsilonGreedy())

    def _q(
            self, states: Tuple[FeatureSet, ...],
            actions: Tuple[FeatureSet, ...]) -> Tuple[float, ...]:
        '''
        Return the Q-value of `state` `action` pairs.

        Arguments
        ---------
        states:
            A tuple of states for which Q-value is returned.

        actions:
            A tuple of actions for which Q-value is returned.
            If not supplied, `default_actions` will be used.

        Notes
        -----
        If one of state or action is one item, it will be broadcasted to
        match the size of the other one. If both are lists, the should match in
        size.


        :meta public:
        '''
        return self._learner.predict((states, actions))

    def _max_q(self, state: FeatureSet) -> float:
        '''
        Return `max(Q)` of one state or a list of states.

        Arguments
        ---------
        state:
            One state or a list of states for which MAX(Q) is returned.


        :meta public:
        '''
        try:
            max_q = self._learner.max((state,), self._default_actions)
        except ValueError:
            max_q = 0.0

        return max_q

    def _prepare_training(
            self, history: History) -> TrainingData[Tuple[FeatureSet, ...], float]:
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
        action: FeatureSet
        next_state: FeatureSet
        reward: float

        discount_factor = self._discount_factor
        active_history = self.get_active_history(history)

        if self._method == 'forward':
            for i, h in enumerate(active_history):
                state = h.state  # type: ignore
                action = (h.action_taken or h.action).feature  # type: ignore
                reward = h.reward or 0.0

                try:
                    next_state = history[i + 1].state  # type: ignore
                    new_q = reward + discount_factor * \
                        self._max_q(next_state)
                except IndexError:
                    new_q = reward

                self._buffer.add(
                    {'state': state, 'action': action, 'Y': new_q})

        else:  # backward
            rewards = self.extract_reward(active_history)
            disc_reward = self.discounted_cum_sum(rewards, discount_factor)

            for h, r in zip(active_history, disc_reward):
                state = h.state  # type: ignore
                action = h.action_taken or h.action  # type: ignore
                self._buffer.add(
                    {'state': state, 'action': action, 'Y': r})

        temp = self._buffer.pick()

        return (temp['state'], temp['action']), temp['Y'], {}  # type: ignore

    def best_actions(
            self,
            state: FeatureSet,
            actions: Tuple[FeatureSet, ...]) -> Tuple[FeatureSet, ...]:
        '''
        Find the best `action`s for the given `state`.

        Arguments
        ---------
        state:
            The state for which the action should be returned.

        actions:
            The set of possible actions to choose from.

        Returns
        -------
        :
            A list of best actions.
        '''
        try:
            return (self._learner.argmax((state,), actions)[1],)
        except AttributeError:
            q_values = self._q((state,), actions)
            max_q: float = np.max(q_values)  # type: ignore
            result = tuple(
                actions[i]
                for i in np.flatnonzero(q_values == max_q))

            return result

    def reset(self) -> None:
        '''Resets the agent at the end of a learning iteration.'''
        super().reset()
        self._buffer.reset()
