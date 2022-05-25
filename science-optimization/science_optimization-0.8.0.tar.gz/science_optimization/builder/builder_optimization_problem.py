"""
Builders base class
"""
import abc


class BuilderOptimizationProblem(metaclass=abc.ABCMeta):
    """Add various parts of an optimization problem.

    This class is responsible for constructing all the parts of a problem.

    """

    @abc.abstractmethod
    def build_objectives(self):
        pass

    @abc.abstractmethod
    def build_constraints(self):
        pass

    @abc.abstractmethod
    def build_variables(self):
        pass
