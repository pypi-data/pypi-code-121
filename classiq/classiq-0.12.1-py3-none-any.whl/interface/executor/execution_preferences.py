from typing import List, Optional, Union

import pydantic

from classiq.interface.backend.backend_preferences import (
    BackendPreferencesTypes,
    backend_preferences_field,
)
from classiq.interface.backend.quantum_backend_providers import IBMQBackendNames
from classiq.interface.executor.error_mitigation import ErrorMitigationMethod
from classiq.interface.executor.optimizer_preferences import OptimizerPreferences
from classiq.interface.generator.model.preferences.randomness import create_random_seed
from classiq.interface.generator.noise_properties import NoiseProperties
from classiq.interface.helpers.custom_pydantic_types import pydanticProbabilityFloat


class AmplitudeEstimation(pydantic.BaseModel):
    alpha: float = pydantic.Field(
        default=0.05, description="Confidence level of the AE algorithm"
    )
    epsilon: float = pydantic.Field(
        default=0.01, description="precision for estimation target `a`"
    )
    binary_search_threshold: Optional[pydanticProbabilityFloat] = pydantic.Field(
        default=None,
        description="The required probability on the tail of the distribution (1 - percentile)",
    )

    objective_qubits: List[int] = pydantic.Field(
        default_factory=list,
        description="list specifying on which qubits to perform the amplitude estimation",
    )


class AmplitudeAmplification(pydantic.BaseModel):
    iterations: Optional[Union[List[int], int]] = pydantic.Field(
        default=None,
        description="Number or list of numbers of iteration to use",
    )
    growth_rate: Optional[float] = pydantic.Field(
        default=None,
        description="Number of iteration used is set to round(growth_rate**iterations)",
    )
    sample_from_iterations: bool = pydantic.Field(
        default=False,
        description="If True, number of iterations used is picked randomly from "
        "[1, iteration] range",
    )


class ExecutionPreferences(pydantic.BaseModel):
    num_shots: pydantic.PositiveInt = 100
    timeout_sec: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="If set, limits the execution runtime. Value is in seconds. "
        "Not supported on all platforms.",
    )
    amplitude_estimation: Optional[AmplitudeEstimation] = pydantic.Field(
        default=None,
        description="Settings related to amplitude estimation execution, used during the finance execution.",
    )
    amplitude_amplification: AmplitudeAmplification = pydantic.Field(
        default_factory=AmplitudeAmplification,
        description="Settings related to amplitude amplification execution, used during the grover execution.",
    )
    optimizer_preferences: OptimizerPreferences = pydantic.Field(
        default_factory=OptimizerPreferences,
        description="Settings related to VQE execution.",
    )
    error_mitigation_method: Optional[ErrorMitigationMethod] = pydantic.Field(
        default=None,
        description="Error mitigation method. Currently supports complete and tensored "
        "measurement calibration.",
    )
    noise_properties: Optional[NoiseProperties] = pydantic.Field(
        default=None, description="Properties of the noise in the circuit"
    )
    random_seed: int = pydantic.Field(
        default_factory=create_random_seed,
        description="The random seed used for the generation",
    )
    backend_preferences: BackendPreferencesTypes = backend_preferences_field(
        backend_name=IBMQBackendNames.IBMQ_AER_SIMULATOR_STATEVECTOR
    )
