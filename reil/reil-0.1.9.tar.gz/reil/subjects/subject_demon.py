# -*- coding: utf-8 -*-
'''
SubjectDemon class
==================

`SubjectDemon` class changes the behavior of a given subject.
'''
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from reil.datatypes.components import Reward, Statistic
from reil.datatypes.feature import FeatureGeneratorType, FeatureSet
from reil.reilbase import ReilBase
from reil.subjects.subject import Subject

T = TypeVar('T', FeatureSet, FeatureGeneratorType)


@dataclasses.dataclass
class Modifier(Generic[T]):
    name: str
    cond_state_def: Optional[str]
    condition_fn: Optional[Callable[[FeatureSet], bool]]
    modifier_fn: Callable[[T], T]

    def __post_init__(self):
        if self.condition_fn is not None:
            if self.cond_state_def is None:
                raise ValueError(
                    '`condition_fn` cannot be declared with '
                    '`cond_state_def=None`.')


class SubjectDemon(ReilBase):
    '''
    This class accepts a regular subject, and intervenes in its interaction
    with the agents. It can modify `state` representation or change
    the `possible_actions`.
    '''

    def __init__(
            self,
            subject: Optional[Subject] = None,
            action_modifier: Optional[
                Modifier[FeatureGeneratorType]] = None,
            state_modifier: Optional[Modifier[FeatureSet]] = None,
            **kwargs: Any):
        '''
        Arguments
        ---------
        subject:
            The `subject` that needs to be intervened with.

        action_modifier:
            A modifier instance for action.

        state_modifier:
            A modifier instance for state.

        '''
        super().__init__(**kwargs)

        self._subject: Subject
        self.reward: Reward
        self.statistic: Statistic

        if subject:
            self.__call__(subject)

        self._action_modifier = action_modifier
        self._state_modifier = state_modifier

    # @classmethod
    # def _empty_instance(cls):
    #     return cls(Subject())

    def __call__(self, subject: Subject) -> SubjectDemon:
        self._subject = subject
        self.reward = subject.reward
        self.statistic = subject.statistic
        self.is_terminated = subject.is_terminated
        self.take_effect = subject.take_effect
        self.reset = subject.reset

        return self

    def state(
            self, name: str,
            _id: Optional[int] = None) -> FeatureSet:
        '''
        Generate the component based on the specified `name` for the
        specified caller.

        Parameters
        ----------
        name:
            The name of the component definition.

        _id:
            ID of the caller.

        Returns
        -------
        :
            The component with the specified definition `name`.

        Raises
        ------
        ValueError
            Definition not found.
        '''
        original_state = self._subject.state(name, _id)
        modifier = self._state_modifier
        if (modifier is not None and
            (modifier.condition_fn is None
                or modifier.condition_fn(self._subject.state(
                    modifier.cond_state_def, _id)))):  # type: ignore
            return modifier.modifier_fn(original_state)

        return original_state

    def possible_actions(
            self, name: str,
            _id: Optional[int] = None
    ) -> Union[FeatureGeneratorType, None]:
        '''
        Generate the component based on the specified `name` for the
        specified caller.

        Parameters
        ----------
        name:
            The name of the component definition.

        _id:
            ID of the caller.

        Returns
        -------
        :
            The component with the specified definition `name`.

        Raises
        ------
        ValueError
            Definition not found.
        '''
        original_gen = self._subject.possible_actions(name, _id)
        modifier = self._action_modifier
        if (original_gen is not None and
            modifier is not None and
            (modifier.condition_fn is None
                or modifier.condition_fn(self._subject.state(
                    modifier.cond_state_def, _id)))):  # type: ignore
            return modifier.modifier_fn(original_gen)

        return original_gen

    # def load(
    #         self, filename: str,
    #         path: Optional[Union[str, pathlib.PurePath]]) -> None:
    #     super().load(filename, path)

    # def save(
    #         self,
    #         filename: Optional[str] = None,
    #         path: Optional[Union[str, pathlib.PurePath]] = None
    # ) -> pathlib.PurePath:
    #     return super().save(filename, path)

    def register(self, entity_name: str, _id: Optional[int] = None) -> int:
        return self._subject.register(entity_name, _id)

    def deregister(self, entity_id: int) -> None:
        return self._subject.deregister(entity_id)
