from __future__ import annotations

from collections.abc import Collection
from enum import Enum
from numbers import Number
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pydantic
from numpy.typing import ArrayLike

from classiq.interface.generator.function_params import FunctionParams
from classiq.interface.generator.preferences.optimization import (
    StatePrepOptimizationMethod,
)
from classiq.interface.generator.range_types import NonNegativeFloatRange, Range
from classiq.interface.helpers.custom_pydantic_types import pydanticProbabilityFloat


class Metrics(str, Enum):
    KL = "KL"
    L2 = "L2"
    L1 = "L1"
    MAX_PROBABILITY = "MAX_PROBABILITY"
    LOSS_OF_FIDELITY = "LOSS_OF_FIDELITY"

    @classmethod
    def from_sp_optimization_method(
        cls, sp_opt_method: StatePrepOptimizationMethod
    ) -> Metrics:
        try:
            return Metrics(sp_opt_method.value)
        except ValueError:
            raise ValueError(f"Failed to convert {sp_opt_method} to an error metric")


def is_power_of_two(pmf):
    n = len(pmf)
    is_power_of_two = (n != 0) and (n & (n - 1) == 0)
    if not is_power_of_two:
        raise ValueError("Probabilities length must be power of 2")
    return pmf


class PMF(pydantic.BaseModel):
    pmf: Tuple[pydanticProbabilityFloat, ...]

    @pydantic.validator("pmf")
    def is_sum_to_one(cls, pmf):
        if round(sum(pmf), 8) != 1:
            raise ValueError("Probabilities do not sum to 1")
        return pmf

    _is_pmf_valid = pydantic.validator("pmf", allow_reuse=True)(is_power_of_two)


class GaussianMoments(pydantic.BaseModel):
    mu: float
    sigma: pydantic.PositiveFloat


class GaussianMixture(pydantic.BaseModel):
    gaussian_moment_list: Tuple[GaussianMoments, ...]


PossibleProbabilities = Union[PMF, GaussianMixture]


class HardwareConstraints(pydantic.BaseModel):
    # this will be moved to model preferences
    # it will be a dictionary of gates and their corresponding errors
    two_qubit_gate_error: Optional[pydanticProbabilityFloat]


FlexibleNonNegativeFloatRange = Union[
    None, float, ArrayLike, NonNegativeFloatRange, dict
]
FlexiblePossibleProbabilities = Union[PossibleProbabilities, ArrayLike, dict]


class StatePreparation(FunctionParams):
    def __init__(
        __pydantic_self__,
        probabilities: FlexiblePossibleProbabilities,
        depth_range: FlexibleNonNegativeFloatRange = None,
        cnot_count_range: FlexibleNonNegativeFloatRange = None,
        **kwargs,
    ):
        super().__init__(
            probabilities=__pydantic_self__._initialize_probabilities(probabilities),
            depth_range=__pydantic_self__._initialize_flexible_non_negative_float_range(
                depth_range
            ),
            cnot_count_range=__pydantic_self__._initialize_flexible_non_negative_float_range(
                cnot_count_range
            ),
            **kwargs,
        )

    @staticmethod
    def _initialize_probabilities(probabilities: FlexiblePossibleProbabilities):
        if isinstance(probabilities, PossibleProbabilities.__args__):  # type: ignore[attr-defined]
            return probabilities
        if isinstance(probabilities, dict):  # a pydantic object
            return probabilities

        probabilities = np.array(probabilities).squeeze()
        if probabilities.ndim == 1:
            return PMF(pmf=probabilities.tolist())

        raise ValueError("Invalid NonNegativeFloatRange given")

    @staticmethod
    def _initialize_flexible_non_negative_float_range(
        obj: FlexibleNonNegativeFloatRange,
    ):
        if obj is None:
            return NonNegativeFloatRange(lower_bound=0, upper_bound=1e100)
        elif isinstance(obj, Number):
            return NonNegativeFloatRange(lower_bound=0, upper_bound=obj)
        # This should be `isinstance(obj, NonNegativeFloatRange)`, but mypy...
        elif isinstance(obj, Range):
            return obj
        elif isinstance(obj, dict):  # a pydantic object
            return obj
        elif isinstance(obj, Collection):
            if len(obj) == 1:
                return NonNegativeFloatRange(lower_bound=0, upper_bound=obj[0])
            elif len(obj) == 2:
                return NonNegativeFloatRange(lower_bound=obj[0], upper_bound=obj[1])
        raise ValueError("Invalid NonNegativeFloatRange given")

    probabilities: Union[PMF, GaussianMixture]
    depth_range: NonNegativeFloatRange = NonNegativeFloatRange(
        lower_bound=0, upper_bound=1e100
    )
    cnot_count_range: NonNegativeFloatRange = NonNegativeFloatRange(
        lower_bound=0, upper_bound=1e100
    )
    error_metric: Dict[Metrics, NonNegativeFloatRange] = pydantic.Field(
        default_factory=lambda: {
            Metrics.KL: NonNegativeFloatRange(lower_bound=0, upper_bound=1e100)
        }
    )
    optimization_method: StatePrepOptimizationMethod = StatePrepOptimizationMethod.KL
    # This will be fixed by the validator.
    # See https://github.com/samuelcolvin/pydantic/issues/259#issuecomment-420341797
    num_qubits: int = None  # type: ignore[assignment]
    is_uniform_start: bool = True
    hardware_constraints: HardwareConstraints = pydantic.Field(
        default_factory=HardwareConstraints
    )

    @pydantic.validator("error_metric")
    def use_fidelity_with_hw_constraints(cls, error_metric, values):
        if values.get("hardware_constraints") is None:
            return error_metric
        error_metrics = {
            error_metric
            for error_metric in error_metric.keys()
            if error_metric is not Metrics.LOSS_OF_FIDELITY
        }
        if error_metrics:
            raise ValueError(
                "Enabling hardware constraints requires the use of only the loss of fidelity as an error metric"
            )

    @pydantic.validator("num_qubits", always=True, pre=True)
    def validate_num_qubits(cls, num_qubits, values):
        assert isinstance(num_qubits, int) or num_qubits is None
        probabilities: Optional[Union[PMF, GaussianMixture]] = values.get(
            "probabilities"
        )
        if probabilities is None:
            raise ValueError("Can't validate num_qubits without valid probabilities")
        if isinstance(probabilities, GaussianMixture):
            if num_qubits is None:
                raise ValueError("num_qubits must be set when using gaussian mixture")
            return num_qubits
        num_state_qubits = len(probabilities.pmf).bit_length() - 1
        if num_qubits is None:
            num_qubits = max(
                2 * num_state_qubits - 2, 1
            )  # Maximum with MCMT auxiliary requirements
        if num_qubits < num_state_qubits:
            raise ValueError(
                f"Minimum of {num_state_qubits} qubits needed, got {num_qubits}"
            )
        return num_qubits

    class Config:
        extra = "forbid"
