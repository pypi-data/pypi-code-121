# -*- coding: utf-8 -*-
'''
subject class
=============

This `subject` class is the base class of all subject classes.
'''

from abc import abstractmethod
from typing import Any, Dict, Optional

from reil import stateful
from reil.datatypes.components import ActionSet, Reward
from reil.datatypes.feature import FeatureGeneratorType, FeatureSet


class Subject(stateful.Stateful):
    '''
    The base class of all subject classes.
    '''

    def __init__(
            self,
            sequential_interaction: bool = True,
            **kwargs: Any):
        '''
        Arguments
        ---------
        sequential_interaction:
            If `True`, `agents` can only act on the `subject` in the order they
            are added.

        Notes
        -----
        `sequential_interaction` is not enforced (implemented) yet!
        '''
        super().__init__(**kwargs)

        self._sequential_interaction = sequential_interaction
        self.reward = Reward(
            name='reward',
            state=self.state,
            default_definition=self._default_reward_definition,
            enabled=False, pickle_stripped=True)

        self.possible_actions = ActionSet(
            name='action',
            state=self.state,
            default_definition=self._default_action_definition,
            enabled=True, pickle_stripped=True)

        Subject._generate_reward_defs(self)

    def _default_reward_definition(self, _id: Optional[int] = None) -> float:
        return 0.0

    def _default_action_definition(
            self, _id: Optional[int] = None) -> FeatureGeneratorType:
        raise NotImplementedError

    def _generate_reward_defs(self) -> None:
        if 'no_reward' not in self.reward.definitions:
            self.reward.add_definition(
                'no_reward', lambda _: 0.0, 'default')

    def _generate_action_defs(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_terminated(self, _id: Optional[int] = None) -> bool:
        '''
        Determine if the `subject` is terminated for the given `agent` ID.

        Arguments
        ---------
        _id:
            ID of the agent that checks termination. In a multi-agent setting,
            e.g. an RTS game, one agent might die and another agent might still
            be alive.

        Returns
        -------
        :
            `False` as long as the subject can accept new actions from the
            `agent`. If `_id` is `None`, then returns `True` if no `agent`
            can act on the `subject`.
        '''
        raise NotImplementedError

    def take_effect(
            self, action: FeatureSet, _id: int = 0
    ) -> FeatureSet:
        '''
        Receive an `action` from `agent` with ID=`_id` and transition to
        the next state.

        Arguments
        ---------
        action:
            The action sent by the `agent` that will affect this `subject`.

        _id:
            ID of the `agent` that has sent the `action`.
        '''
        if not self.reward._enabled:
            self.reward.enable()

        taken_action = self._take_effect(action, _id)
        return taken_action

    @abstractmethod
    def _take_effect(
            self, action: FeatureSet, _id: int = 0
    ) -> FeatureSet:
        '''
        Receive an `action` from `agent` with ID=`_id` and transition to
        the next state.

        This method implements the actual act of receiving and applying the
        action. `take_effect` is the method to use, since it checks to see if
        the `reward` is enabled.

        Arguments
        ---------
        action:
            The action sent by the `agent` that will affect this `subject`.

        _id:
            ID of the `agent` that has sent the `action`.
        '''
        raise NotImplementedError

    def reset(self) -> None:
        '''Reset the `subject`, so that it can resume accepting actions.'''
        super().reset()
        self.reward.disable()

    def __setstate__(self, state: Dict[str, Any]) -> None:
        super().__setstate__(state)
        try:
            self.reward.set_state(self.state)
        except ValueError:
            self._logger.warning(
                'Primary component is already set for `reward` to .'
                f'{self.reward._state}. Resetting the value!')
            self.reward._state = self.state

        self.reward.set_default_definition(
            self._default_reward_definition)

        try:
            self.possible_actions.set_state(self.state)
        except ValueError:
            self._logger.warning(
                'Primary component is already set for `possible_actions` to .'
                f'{self.possible_actions._state}. '
                'Resetting the value!')
            self.possible_actions._state = self.state

        self.possible_actions.set_default_definition(
            self._default_action_definition)

        if '_action_taken' not in self.__dict__:
            self._actions_taken = []

        # try:
        #     self._generate_reward_defs()
        # except NotImplementedError:
        #     pass

        # try:
        #     self._generate_action_defs()
        # except NotImplementedError:
        #     pass
