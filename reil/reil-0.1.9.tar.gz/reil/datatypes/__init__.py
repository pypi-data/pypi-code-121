# -*- coding: utf-8 -*-
'''
datatypes module for reinforcement learning
===========================================

This module contains datatypes used in `reil`

Submodules
----------
buffers:
    A module that contains different types of `Buffers` used in `reil`
    package.

Classes
-------
Feature:
    A datatype that accepts initial value and feature generator and
    generates new values.

Entity:
    A datatype to specify `agent` or `subject` information. Used in
    `InteractionProtocol`.

InteractionProtocol:
    A datatype to specifies how an `agent` and a `subject`
    interact in an `environment`.

FeatureSet:
    The main datatype used to communicate `state`s, `action`s, and `reward`s,
    between objects in `reil`. `FeatureSet` is basically a dictionary that
    contains instances of `Feature`.

Feature:
    An immutable dataclass that accepts name, value, and is_numerical.

Categorical:
    A factory class that creates `Feature` objects with categories.

Numerical:
    A factory class that creates `Feature` objects with lower and upper
    bounds.

State:
    A datatype that is being used mostly by children of `Stateful` to include
    a `State`, e.g. a state. It allows defining different
    definitions for the component, and call the instance to calculate them.

SecondayComponent:
    A datatype that is being used mostly by children of `Subject` to include
    a `SecondayComponent`, e.g. a statistic or a reward. It allows defining
    different definitions for the component, and call the instance to calculate
    them.
'''
from . import buffers  # noqa: W601
from .feature import (Feature, FeatureSet, FeatureGenerator,  # noqa: W601
                      FeatureGeneratorSet, FeatureGeneratorType)
from .feature_array_dumper import FeatureSetDumper  # noqa: W0611
from .components import (ActionSet, Reward, State,  # noqa: W601
                         SecondayComponent, Statistic)
from .dataclasses import (Entity, History, InteractionProtocol,  # noqa: W601
                          Observation)
from .entity_register import EntityRegister  # noqa: W601
