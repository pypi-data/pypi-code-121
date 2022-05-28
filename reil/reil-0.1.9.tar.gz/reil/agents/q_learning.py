# -*- coding: utf-8 -*-
'''
QLearning class
===============

A Q-learning `agent`.


'''

from typing import Any, Literal, Tuple, Union

import numpy as np
from reil.agents.agent import Agent, TrainingData
from reil.datatypes import History
from reil.datatypes.buffers import Buffer
from reil.datatypes.feature import FeatureSet
from reil.learners import Learner
from reil.utils.exploration_strategies import (ConstantEpsilonGreedy,
                                               ExplorationStrategy)

Feature_or_Tuple_of_Feature = Union[Tuple[FeatureSet, ...], FeatureSet]


class QLearning(Agent[FeatureSet, float]):
    '''
    A Q-learning `agent`.
    '''

    def __init__(
            self,
            learner: Learner[FeatureSet, float],
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
        self._buffer.setup(buffer_names=['X', 'Y'])

    @classmethod
    def _empty_instance(cls):  # type: ignore
        return cls(
            Learner._empty_instance(), Buffer(), ConstantEpsilonGreedy())

    def _q(
            self, state: Feature_or_Tuple_of_Feature,
            action: Feature_or_Tuple_of_Feature) -> Tuple[float, ...]:
        '''
        Return the Q-value of `state` `action` pairs.

        Arguments
        ---------
        state:
            One state or a list of states for which Q-value is returned.

        action:
            One action or a list of actions for which Q-value is returned.
            If not supplied, `default_actions` will be used.

        Notes
        -----
        If one of state or action is one item, it will be broadcasted to
        match the size of the other one. If both are lists, the should match in
        size.


        :meta public:
        '''
        if isinstance(action, FeatureSet):
            action_list = (action,)
            len_action = 1
        else:
            action_list = action
            len_action = len(action_list)

        if isinstance(state, FeatureSet):
            state_list = [state] * len_action
            len_state = len_action
        else:
            state_list = state
            len_state = len(state_list)

        if len_state == len_action:
            x = tuple(s + a
                      for s, a in zip(state_list, action_list))
        elif len_state == 1:
            x = tuple(state_list[0] + a
                      for a in action_list)
        elif len_action == 1:
            x = tuple(s + action_list[0]
                      for s in state_list)
        else:
            raise ValueError(
                'State and action should be of the same size'
                ' or at least one should be of size one.')

        return self._learner.predict(x)

    def _max_q(self, state: Feature_or_Tuple_of_Feature) -> float:
        '''
        Return `max(Q)` of one state or a list of states.

        Arguments
        ---------
        state:
            One state or a list of states for which MAX(Q) is returned.


        :meta public:
        '''
        try:
            q_values = self._q(state, self._default_actions)
            max_q: float = np.max(q_values)  # type: ignore
        except ValueError:
            max_q = 0.0

        return max_q

    def _prepare_training(
            self, history: History) -> TrainingData[FeatureSet, float]:
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

        for h in history[:-1]:
            if h.state is None or (
                    h.action is None and h.action_taken is None):
                raise ValueError(f'state and action cannot be None.\n{h}')

        # When history is one complete trajectory, the last observation
        # contains only the terminal state. In this case, we don't have an
        # action and a reward for the last observation, so we do not compute
        # its new Q value.
        if history[-1].action is None or history[-1].action_taken is None:
            active_history = history[:-1]
        else:
            active_history = history

        if self._method == 'forward':
            for i, h in enumerate(active_history):
                state = h.state  # type: ignore
                action = (h.action_taken or h.action).feature  # type: ignore
                reward = h.reward or 0.0

                try:
                    next_state = history[i+1].state  # type: ignore
                    new_q = reward + discount_factor * \
                        self._max_q(next_state)
                except IndexError:
                    new_q = reward

                self._buffer.add(
                    {'X': state + action, 'Y': new_q})

        else:  # backward
            q_list = [0.0] * 2
            for i in range(len(active_history)-1, -1, -1):
                state = active_history[i].state  # type: ignore
                action = (
                    active_history[i].action_taken or
                    active_history[i].action)  # type: ignore
                reward = active_history[i].reward or 0.0
                q_list[0] = reward + discount_factor * q_list[1]

                self._buffer.add(
                    {'X': state + action, 'Y': q_list[0]})

                q_list[1] = q_list[0]

        temp = self._buffer.pick()

        return temp['X'], temp['Y'], {}  # type: ignore

    def best_actions(
            self,
            state: FeatureSet,
            actions: Tuple[FeatureSet, ...]
    ) -> Tuple[FeatureSet, ...]:
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
        q_values = self._q(state, actions)
        max_q: float = np.max(q_values)  # type: ignore
        result = tuple(
            actions[i]
            for i in np.flatnonzero(q_values == max_q))

        return result

    def reset(self) -> None:
        '''Resets the agent at the end of a learning iteration.'''
        super().reset()
        self._buffer.reset()
