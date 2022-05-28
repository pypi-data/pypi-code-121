# -*- coding: utf-8 -*-
'''
Agent class
===========

This `agent` class is the base class of all agent classes that can learn from
`history`.
'''

from typing import (Any, Dict, Generator, Generic, List, Literal, Optional, Tuple,
                    TypeVar, Union)

import scipy.signal

from reil.agents.agent_base import AgentBase
from reil.datatypes import History
from reil.datatypes.dataclasses import Observation
from reil.datatypes.feature import FeatureGeneratorType, FeatureSet
from reil.learners.learner import LabelType, Learner
from reil.utils.exploration_strategies import (ConstantEpsilonGreedy,
                                               ExplorationStrategy)

InputType = TypeVar('InputType')
TrainingData = Tuple[
    Tuple[InputType, ...], Tuple[LabelType, ...], Dict[str, Any]]


class Agent(AgentBase, Generic[InputType, LabelType]):
    '''
    The base class of all agent classes that learn from history.
    '''

    def __init__(
            self,
            learner: Learner[InputType, LabelType],
            exploration_strategy: Union[float, ExplorationStrategy],
            discount_factor: float = 1.0,
            tie_breaker: Literal['first', 'last', 'random'] = 'random',
            training_trigger: Literal[
                'none', 'termination',
                'state', 'action', 'reward'] = 'termination',
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

        tie_breaker:
            how to choose the `action` if more than one is candidate
            to be chosen.

        training_trigger:
            When to learn from observations. This arguments is used in
            `observe` method to determine when `learn` method should be called.
            `none` avoids any call to `learn`; `state`, `action` and `reward`
            trigger the `learn` method after receiving their corresponding
            value; `termination` waits until `.close()` method of the generator
            is called.
        '''
        self._tie_breaker: Literal['first', 'last', 'random']

        super().__init__(tie_breaker, **kwargs)

        self._learner: Learner[InputType, LabelType] = learner
        if not 0.0 <= discount_factor <= 1.0:
            self._logger.warning(
                f'{self.__class__.__qualname__} discount_factor should be in'
                f' [0.0, 1.0]. Got {discount_factor}. Set to 1.0.')
        self._discount_factor = min(discount_factor, 1.0)
        if isinstance(exploration_strategy, float):
            self._exploration_strategy = ConstantEpsilonGreedy(
                exploration_strategy)
        else:
            self._exploration_strategy = exploration_strategy

        self._training_trigger: Literal[
            'none', 'termination', 'state', 'action', 'reward'
        ] = training_trigger

    @classmethod
    def _empty_instance(cls):
        return cls(Learner._empty_instance(), ConstantEpsilonGreedy())

    @staticmethod
    def discounted_cum_sum(r: List[float], discount: float) -> List[float]:
        # Copied from OpenAI SpinUp: algos/tf1/ppo/core.py
        return scipy.signal.lfilter(  # type: ignore
            [1], [1, float(-discount)], r[::-1], axis=0)[::-1]

    @staticmethod
    def extract_reward(
            history: History,
            min_clip: Optional[float] = None,
            max_clip: Optional[float] = None) -> List[float]:
        rewards: List[float] = [
            a.reward for a in history
            if a.reward is not None]

        if min_clip is not None:
            rewards = [max(r, min_clip) for r in rewards]
        if max_clip is not None:
            rewards = [min(r, max_clip) for r in rewards]

        return rewards

    @staticmethod
    def get_active_history(history: History) -> History:
        '''
        Extract active history.

        When history is one complete trajectory, the last observation
        contains only the terminal state. In this case, we don't have an
        action and a reward for the last observation, so we should clip it in
        Q-learning, actor critic, and similar methods.
        '''
        for h in history[:-1]:
            if h.state is None or (
                    h.action is None and h.action_taken is None):
                raise ValueError(f'state and action cannot be None.\n{h}')

        if history[-1].action_taken is None and history[-1].action is None:
            active_history = history[:-1]
        else:
            active_history = history

        return active_history

    def act(self,
            state: FeatureSet,
            subject_id: int,
            actions: FeatureGeneratorType,
            iteration: int = 0) -> FeatureSet:
        '''
        Return an action based on the given state.

        Arguments
        ---------
        state:
            the state for which the action should be returned.

        subject_id:
            the ID of the `subject` on which action should occur.

        actions:
            the set of possible actions to choose from.

        iteration:
            the iteration in which the agent is acting.

        Raises
        ------
        ValueError
            Subject with `subject_id` not found.

        Returns
        -------
        :
            the action
        '''
        if subject_id not in self._entity_list:
            raise ValueError(f'Subject with ID={subject_id} not found.')

        if (self._training_trigger != 'none' and
                self._exploration_strategy.explore(iteration)):
            action = actions.send('choose feature exclusive')
        else:
            action = super().act(
                state=state, subject_id=subject_id,
                actions=actions, iteration=iteration)

        return action

    def reset(self):
        '''Reset the agent at the end of a learning iteration.'''
        super().reset()
        if self._training_trigger != 'none':
            self._learner.reset()

    def _prepare_training(
            self, history: History) -> TrainingData[InputType, LabelType]:
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
        raise NotImplementedError

    def learn(self, history: History) -> Dict[str, float]:
        '''
        Learn using history.

        Arguments
        ---------
        subject_id:
            the ID of the `subject` whose history is being used for learning.

        next_state:
            The new `state` of the `subject` after taking `agent`'s action.
            Some methods
        '''
        training_data: TrainingData[Any] = (), (), {}
        if history is not None:
            training_data = self._prepare_training(history)

        X, Y, kwargs = training_data
        metrics = {}
        if Y:
            metrics = self._learner.learn(X, Y, **kwargs)
            self._metrics.update(metrics)

        return metrics

    def observe(  # noqa: C901
            self, subject_id: int, stat_name: Optional[str],
    ) -> Generator[Union[FeatureSet, None], Dict[str, Any], None]:
        '''
        Create a generator to interact with the subject (`subject_id`).
        Extends `AgentBase.observe`.

        This method creates a generator for `subject_id` that
        receives `state`, yields `action` and receives `reward`
        until it is closed. When `.close()` is called on the generator,
        `statistics` are calculated.

        Arguments
        ---------
        subject_id:
            the ID of the `subject` on which action happened.

        stat_name:
            The name of the `statistic` that should be computed at the end of
            each trajectory.

        Raises
        ------
        ValueError
            Subject with `subject_id` not found.
        '''
        if subject_id not in self._entity_list:
            raise ValueError(f'Subject with ID={subject_id} not found.')

        trigger = self._training_trigger
        learn_on_state = trigger == 'state'
        learn_on_action = trigger == 'action'
        learn_on_reward = trigger == 'reward'
        learn_on_termination = trigger == 'termination'

        history: History = []
        new_observation = None
        while True:
            try:
                new_observation = Observation()
                temp: Dict[str, Any] = yield
                state: FeatureSet = temp['state']
                actions: FeatureGeneratorType = temp['actions']
                iteration: int = temp['iteration']

                new_observation.state = state
                if learn_on_state:
                    self._metrics.update(
                        self.learn([history[-1], new_observation]))

                if actions is not None:
                    new_observation.action = self.act(
                        state=state, subject_id=subject_id,
                        actions=actions, iteration=iteration)

                    new_observation.action_taken = (
                        yield new_observation.action)['action_taken']

                    if learn_on_action:
                        self._metrics.update(
                            self.learn([history[-1], new_observation]))

                    new_observation.reward = (yield None)['reward']

                    history.append(new_observation)

                    if learn_on_reward:
                        self._metrics.update(self.learn(history[-2:]))
                else:  # No actions to take, so skip the reward.
                    yield

            except GeneratorExit:
                if new_observation is None:
                    new_observation = Observation()
                if new_observation.reward is None:  # terminated early!
                    history.append(new_observation)

                if learn_on_termination:
                    metrics = self.learn(history)
                    self._metrics.update({
                        key: val[0]  # type: ignore
                        for key, val in metrics.items()})

                if stat_name is not None:
                    self.statistic.append(stat_name, subject_id)

                return

    def get_parameters(self) -> Any:
        return self._learner.get_parameters()

    def set_parameters(self, parameters: Any):
        self._learner.set_parameters(parameters)

    # def load(
    #         self, filename: str,
    #         path: Optional[Union[str, pathlib.PurePath]] = None) -> None:
    #     '''
    #     Load an object from a file.

    #     Arguments
    #     ---------
    #     filename:
    #         the name of the file to be loaded.

    #     path:
    #         the path in which the file is saved.

    #     Raises
    #     ------
    #         ValueError
    #             Filename is not specified.
    #     '''
    #     _path = pathlib.Path(path or self._path)
    #     super().load(filename, _path)

    #     # when loading, self._learner is the object type, not an instance.
    #     self._learner = self._learner.from_pickle(  # type: ignore
    #         filename, _path.parent / 'learner')

    # def save(
    #         self,
    #         filename: Optional[str] = None,
    #         path: Optional[Union[str, pathlib.PurePath]] = None
    # ) -> pathlib.PurePath:
    #     '''
    #     Save the object to a file.

    #     Arguments
    #     ---------
    #     filename:
    #         the name of the file to be saved.

    #     path:
    #         the path in which the file should be saved.

    #     data_to_save:
    #         a list of variables that should be pickled. If omitted,
    #         the `agent` is saved completely.

    #     Returns
    #     -------
    #     :
    #         a `Path` object to the location of the saved file and its name as
    #         `str`
    #     '''
    #     full_path = super().save(filename, path)
    #     self._learner.save(full_path.name, full_path.parent / 'learner')

    #     return full_path

    # def __getstate__(self):
    #     state = super().__getstate__()

    #     state['_learner'] = type(self._learner)

    #     return state
