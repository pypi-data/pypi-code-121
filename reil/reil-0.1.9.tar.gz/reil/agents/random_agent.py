# -*- coding: utf-8 -*-
'''
RandomAgent class
=================

An agent that randomly chooses an action
'''

from typing import Any, Tuple

from reil.agents.agent_base import AgentBase
from reil.datatypes.feature import FeatureGeneratorType, FeatureSet


class RandomAgent(AgentBase):
    '''
    An agent that acts randomly.
    '''

    def __init__(
            self, default_actions: Tuple[FeatureSet, ...] = (),
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
        return actions.send('choose feature exclusive')
