# -*- coding: utf-8 -*-
'''
AgentDemon class
================

`AgentDemon` class changes the behavior of a given agent.
'''
from __future__ import annotations

import pathlib
from typing import Any, Callable, Literal, Optional, Union

from reil import reilbase
from reil.agents.agent_base import AgentBase
from reil.datatypes import History
from reil.datatypes.components import State, Statistic
from reil.datatypes.entity_register import EntityRegister
from reil.datatypes.feature import FeatureGeneratorType, FeatureSet


class AgentDemon(AgentBase):
    '''
    This class accepts a regular `agent`, and intervenes in its interaction
    with the subjects. A substitute `agent` acts whenever a condition is
    satisfied.
    '''

    def __init__(
            self,
            sub_agent: AgentBase,
            condition_fn: Callable[[FeatureSet, int], bool],
            main_agent: Optional[AgentBase] = None,
            **kwargs: Any):
        '''
        Arguments
        ---------
        sub_agent:
            An `agent` that acts instead of the `main_agent`.

        condition_fn:
            A function that accepts the current state and ID of the subject
            and decides whether the `main_agent` should act or the `sub_agent`.

        main_agent:
            The `agent` that needs to be intervened with.
        '''
        reilbase.ReilBase.__init__(self, **kwargs)

        self.state: State
        self.statistic: Statistic
        self._entity_list: EntityRegister
        self._training_trigger: Literal[
            'none', 'termination', 'state', 'action', 'reward']

        self._main_agent: Optional[AgentBase] = main_agent
        self._sub_agent: AgentBase = sub_agent
        self._condition_fn = condition_fn

        if main_agent is not None:
            self.__call__(main_agent)

    @classmethod
    def _empty_instance(cls):
        return cls(AgentBase(), lambda f, i: True, None)

    def __call__(self, main_agent: AgentBase) -> AgentDemon:
        self._main_agent = main_agent
        self.state = main_agent.state
        self.statistic = main_agent.statistic
        self._entity_list = main_agent._entity_list
        self._training_trigger = main_agent._training_trigger

        return self

    def load(
            self, filename: str,
            path: Optional[Union[str, pathlib.PurePath]]) -> None:
        _path = pathlib.Path(path or self._path)
        super().load(filename, _path)

        self._main_agent = (self._main_agent or AgentBase).from_pickle(
            filename, _path / 'main_agent')
        self._sub_agent = self._sub_agent.from_pickle(
            filename, _path / 'sub_agent')

        self.__call__(self._main_agent)

    def save(
            self,
            filename: Optional[str] = None,
            path: Optional[Union[str, pathlib.PurePath]] = None
    ) -> pathlib.PurePath:

        full_path = super().save(filename, path)
        if self._main_agent:
            self._main_agent.save(
                full_path.name, full_path.parent / 'main_agent')
        self._sub_agent.save(
            full_path.name, full_path.parent / 'sub_agent')

        return full_path

    def register(self, entity_name: str, _id: Optional[int] = None) -> int:
        if self._main_agent is None:
            raise ValueError('main_agent is not set.')

        from_main = self._main_agent.register(entity_name, _id)
        from_sub = self._sub_agent.register(entity_name, _id)
        if from_main != from_sub:
            raise RuntimeError(f'ID from the main agent {from_main} does not '
                               f'match the ID from the sub agent {from_sub}.')

        return from_main

    def deregister(self, entity_id: int) -> None:
        self._sub_agent.deregister(entity_id)

        if self._main_agent is None:
            raise ValueError('main_agent is not set.')
        self._main_agent.deregister(entity_id)

    def reset(self):
        if self._main_agent:
            self._main_agent.reset()
        self._sub_agent.reset()

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
        if self._condition_fn(state, subject_id):
            return self._sub_agent.act(state, subject_id, actions, iteration)

        if self._main_agent is None:
            raise ValueError('main_agent is not set.')

        return self._main_agent.act(state, subject_id, actions, iteration)

    def learn(self, history: History) -> None:
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
        if self._main_agent is None:
            raise ValueError('main_agent is not set.')

        if self._training_trigger != 'none':
            self._main_agent.learn(history)  # type: ignore

    def __getstate__(self):
        state = super().__getstate__()

        state['_main_agent'] = type(self._main_agent)
        state['_sub_agent'] = type(self._sub_agent)
        del state['state']
        del state['statistic']

        return state
