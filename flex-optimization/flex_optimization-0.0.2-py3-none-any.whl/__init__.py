# here to deal with crtl+C issue
# see https://stackoverflow.com/questions/15457786/ctrl-c-crashes-python-after-importing-scipy-stats
import os
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

import enum


class OptimizationType(enum.Enum):
    MIN = 0
    MAX = 1
    MINIMUM = 0
    MAXIMUM = 1


class NotSupported(Exception):
    pass


from flex_optimization.core.variable import DiscreteVariable, ContinuousVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.logger_ import logger
from flex_optimization.core.visualize import OptimizationVis

import flex_optimization.recorders as recorders
import flex_optimization.stop_criteria as stop_criteria
import flex_optimization.methods as methods
import flex_optimization.problems as problems
