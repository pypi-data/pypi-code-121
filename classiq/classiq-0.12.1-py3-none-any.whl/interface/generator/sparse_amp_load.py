from typing import List

import numpy as np
import pydantic

from classiq.interface.generator import function_params
from classiq.interface.generator.complex_type import Complex
from classiq.interface.generator.state_preparation import is_power_of_two

OUTPUT_STATE = "OUTPUT_STATE"


def amplitudes_sum_to_one(amp):
    if round(sum(abs(np.array(amp)) ** 2), 8) != 1:
        raise ValueError("Probabilities do not sum to 1")
    return amp


class SparseAmpLoad(function_params.FunctionParams):
    """
    loads a sparse amplitudes vector
    """

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits in the circuit."
    )
    amplitudes: List[Complex] = pydantic.Field(description="amplitudes vector to load")

    _is_power_of_two = pydantic.validator("amplitudes", allow_reuse=True)(
        is_power_of_two
    )
    _is_sum_to_one = pydantic.validator("amplitudes", allow_reuse=True)(
        amplitudes_sum_to_one
    )

    _input_names = pydantic.PrivateAttr(default_factory=list)
    _output_names = pydantic.PrivateAttr(default=[OUTPUT_STATE])
