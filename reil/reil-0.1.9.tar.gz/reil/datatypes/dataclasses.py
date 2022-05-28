# -*- coding: utf-8 -*-
'''
InteractionProtocol class
=========================

A datatype that accepts initial value and feature generator, and generates
new values. This datatype uses `Entity` to specify an `agent` or a `subject`.
'''
import dataclasses
from typing import List, Literal, Optional, Tuple

from reil.datatypes.feature import FeatureSet


@dataclasses.dataclass(frozen=True)
class Entity:
    '''
    The datatype to specify an `agent` or a `subject`.
    Used in `InteractionProtocol`.
    '''
    name: str
    demon_name: Optional[str] = None
    statistic_name: Optional[str] = None
    groupby: Optional[Tuple[str, ...]] = None
    aggregators: Optional[Tuple[str, ...]] = None
    trajectory_name: Optional[str] = None

    def __post_init__(self):
        if self.groupby is not None:
            self.__dict__['groupby'] = tuple(self.groupby)
        if self.aggregators is not None:
            self.__dict__['aggregators'] = tuple(self.aggregators)


@dataclasses.dataclass
class InteractionProtocol:
    '''
    The datatype to specify how an `agent` should interact with a `subject` in
    an `environment`.
    '''
    agent: Entity
    subject: Entity
    state_name: str
    action_name: str
    reward_name: str
    n: int
    unit: Literal['interaction', 'instance', 'iteration']


@dataclasses.dataclass
class Observation:
    # the state received from the subject
    state: Optional[FeatureSet] = None
    # the action chosen by the agent
    action: Optional[FeatureSet] = None
    # the action taken by the subject
    action_taken: Optional[FeatureSet] = None
    # the reward of taking the action at the state
    reward: Optional[float] = None


History = List[Observation]
