# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Collection of testing utilities.
"""

from dataclasses import dataclass
from typing import (
    Callable,
    List,
    Optional,
)

import numpy as np
from mloop.interfaces import Interface
from mloop.learners import NelderMeadLearner


@dataclass
class CostFunctionResult:
    """
    Mock class for the CostFunctionResult object from the Boulder Opal API.
    """

    parameters: List[float]
    cost: float
    cost_uncertainty: Optional[float] = None


@dataclass
class BoxConstraint:
    """
    Mock class for the BoxConstraint object from the Boulder Opal API.
    """

    lower_bound: float
    upper_bound: float


@dataclass
class CrossEntropyInitializer:
    """
    Mock class for the CrossEntropyInitializer object from the Boulder Opal API.
    """

    elite_fraction: float
    rng_seed: Optional[int] = None


@dataclass
class GaussianProcessInitializer:
    """
    Mock class for the GaussianProcessInitializer object from the Boulder Opal API.
    """

    length_scale_bounds: List[BoxConstraint]
    bounds: List[BoxConstraint]
    rng_seed: Optional[int] = None


@dataclass
class Optimizer:
    """
    Mock class for the Optimizer object from the Boulder Opal API.
    """

    cross_entropy_initializer: Optional[CrossEntropyInitializer] = None
    gaussian_process_initializer: Optional[GaussianProcessInitializer] = None
    state: Optional[str] = None


@dataclass
class TestPoint:
    """
    Mock class for the TestPoint object from the Boulder Opal API.
    """

    parameters: List[float]


@dataclass
class Result:
    """
    Mock class for the Result object from the Boulder Opal API.
    """

    test_points: List[TestPoint]
    state: str
    action = None
    errors = None


# pylint: disable=invalid-name
@dataclass
class ClosedLoopOptimizationStep:
    """
    Mock class for the ClosedLoopOptimizationStep object from the Boulder Opal API.
    """

    CostFunctionResult = CostFunctionResult
    CrossEntropyInitializer = CrossEntropyInitializer
    GaussianProcessInitializer = GaussianProcessInitializer
    Optimizer = Optimizer
    Result = Result
    BoxConstraint = BoxConstraint
    TestPoint = TestPoint


# pylint: enable=invalid-name


@dataclass
class Types:
    """
    Mock class for the data type namespace from the Boulder Opal API.
    """

    closed_loop_optimization_step = ClosedLoopOptimizationStep()


class Functions:
    """
    Mock class for the functions namespace from the Boulder Opal API.
    """

    def __init__(
        self,
        get_parameters: Callable[
            [Optional[List[CostFunctionResult]], Optional[int]], List[List[float]]
        ],
        get_state: Callable[[Optional[List[CostFunctionResult]]], str],
    ):
        self._get_parameters = get_parameters
        self._get_state = get_state

    def calculate_closed_loop_optimization_step(
        self,
        optimizer: Optimizer,
        results: Optional[List[CostFunctionResult]] = None,
        test_point_count: Optional[int] = None,
    ) -> Result:
        """
        Mock optimizer that returns test points and results according to
        the callables that you passed.
        """
        assert isinstance(optimizer, Optimizer)
        if results is not None:
            assert all(isinstance(result, CostFunctionResult) for result in results)
        if test_point_count is not None:
            assert test_point_count > 0
            assert test_point_count % 1 == 0

        return Result(
            test_points=[
                TestPoint(list(parameters))
                for parameters in self._get_parameters(results, test_point_count)
            ],
            state=self._get_state(results),
        )


class Qctrl:  # pylint: disable=too-few-public-methods
    """
    Mock class for the Boulder Opal API.

    Arguments
    ---------
    get_parameters : callable
        Your custom implementation of the parameters returned by the mock
        `calculate_closed_loop_optimization_step` function. It takes two
        parameters: a list of `CostFunctionResult` objects corresponding to
        the `results` passed to the mock function, and an integer
        corresponding to the `test_point_count`. It returns a list of
        parameters for each test point.
    get_state : callable
        Your custom implementation of the state returned by the mock
        `calculate_closed_loop_optimization_step` function. It takes a list
        of `CostFunctionResult` objects, corresponding to the `results`
        passed to the mock function, and returns a string.
    """

    def __init__(
        self,
        get_parameters: Callable[
            [Optional[List[CostFunctionResult]], Optional[int]], List[List[float]]
        ],
        get_state: Callable[[Optional[List[CostFunctionResult]]], str],
    ):
        self.types = Types()
        self.functions = Functions(get_parameters, get_state)


class ParabolaInterface(Interface):
    """
    Interface with a parabolic cost function.
    """

    def get_next_cost_dict(self, params_dict):
        cost = sum(params_dict["params"] ** 2)
        return {"cost": cost}


class FixedSeedNelderMeadLearner(NelderMeadLearner):
    """
    Version of the NelderMeadLearner that allows the specification of a
    random seed, to ensure reproducibility of the tests.
    """

    def __init__(self, seed: int, **kwargs):
        np.random.seed(seed)
        super().__init__(**kwargs)
