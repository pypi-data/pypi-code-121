# -*- coding: utf-8 -*-
'''
UserAgent class
===============

An agent that prints the state and asks the user for action.
'''
from typing import Any, Tuple

from reil.agents.agent_base import AgentBase
from reil.datatypes.feature import FeatureGeneratorType, FeatureSet


class UserAgent(AgentBase):
    '''
    An agent that acts based on user input.
    '''

    def __init__(
            self,
            default_actions: Tuple[FeatureSet, ...] = (),
            **kwargs: Any):
        super().__init__(default_actions=default_actions, **kwargs)

    def act(self,
            state: FeatureSet,
            subject_id: int,
            actions: FeatureGeneratorType,
            iteration: int = 0) -> FeatureSet:
        '''
        Return a random action.

        Arguments
        ---------
        state:
            The state for which the action should be returned.

        actions:
            The set of possible actions to choose from.

        iteration:
            The iteration in which the agent is acting.

        Returns
        -------
        :
            The action
        '''
        query = (
            'return feature exclusive' if self._variable_action_count
            else 'return feature')
        possible_actions = tuple(actions.send(query))

        action = None
        while action is None:
            for i, a in enumerate(possible_actions):
                print(f'{i}. {a.value}')  # type: ignore
            action = int(input(
                'Choose action number for this state:'
                f'{state.value}'))  # type: ignore

        return possible_actions[action]
