from typing import List

import numpy as np
import pydantic

from classiq.interface.generator import function_params
from classiq.interface.generator.complex_type import Complex


class StatePropagator(function_params.FunctionParams):
    """
    Creates a quantum circuit that propagates the start state vector to the end state vector,
    both are assumed to be pure states.
    The default start state vector is |000...0>.
    """

    end_state_vector: List[Complex] = pydantic.Field(
        description="The desired state vector at the end of the operator."
        " Must be of size 2**num_qubits. Does not have to be "
        "normalized"
    )

    start_state_vector: List[Complex] = pydantic.Field(
        default_factory=list,
        description="The  state vector at the input of the operator."
        " Must be of size 2**num_qubits. Does not have to be"
        " normalized",
    )

    _input_names: List[str] = pydantic.PrivateAttr(default=["IN"])
    _output_names: List[str] = pydantic.PrivateAttr(default=["OUT"])

    @pydantic.validator("start_state_vector", always=True)
    def validate_start_state(cls, start_state_vector, values):
        end_state_vector = values.get("end_state_vector")
        num_qubits = int(np.log2(len(end_state_vector)))
        if len(start_state_vector) == 0:
            default_start_state_vector = [0.0 for _ in range(2**num_qubits)]
            default_start_state_vector[0] = 1.0
            start_state_vector = default_start_state_vector

        if len(start_state_vector) != len(end_state_vector):
            raise ValueError("Start and end state vectors are of non-equal length")

        return start_state_vector
