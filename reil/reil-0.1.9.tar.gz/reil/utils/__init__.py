# -*- coding: utf-8 -*-
'''
Utils module for reinforcement learning
=======================================

This module provides different utilities used in the `reil` package.

Submodules
----------
exploration_strategies:
    A module that provides different exploration strategies for `agents`.

functions:
    Contains different useful functions.

reil_functions:
    A set of special objects that are used to define and compute different
    statistics, rewards, etc.

Classes
-------
ActionGenerator:
    A class that accepts categorical and numerical components, and
    generates lists of actions as `FeatureSet` objects.

CategoricalComponent:
    A class used to define categorical parts of actions.

NumericalComponent:
    A class used to define numerical parts of actions.

InstanceGenerator:
    Accepts any object derived from `ReilBase`, and generates instances.

CommandlineArgument:
    A dataclass to define a commandline argument by specifying its name, type
    and default value.

CommandlineParser:
    A class to define and parse commandline arguments

ConfigParser:
    A class to read and parse `YAML` config files.

OutputWriter:
    A class to write statistics to a `csv` file.

MNKBoard:
    An m-by-n board in which k similar horizontal, vertical, or diagonal
    sequence is a win. Used in `subjects` such as `TicTacToe`.

WekaClusterer:
    A clustering class based on Weka's clustering capabilities (disabled)
'''
import reil.utils.exploration_strategies  # noqa: W0611
import reil.utils.functions  # noqa: W0611
import reil.utils.reil_functions  # noqa: W0611
import reil.utils.yaml_tools  # noqa: W0611

from .action_generator import (ActionGenerator,  # noqa: W0611
                               CategoricalComponent, NumericalComponent)
from .instance_generator import InstanceGenerator  # noqa: W0611
from .instance_generator_batch import InstanceGeneratorBatch  # noqa: W0611

from .argument_parser import (CommandlineArgument,   # noqa: W0611
                              CommandlineParser, ConfigParser)
from .output_writer import OutputWriter  # noqa: W0611

from .mnkboard import MNKBoard  # noqa: W0611
