from typing import List

import pydantic

from classiq.interface.generator import function_params

LENGTH_ERROR_MESSAGE = "Input length error: Length of weights vector has to be identical to the number of input qubits"
STATE = "state"
SUM = "sum"


class pydanticStrictNonNegativeInteger(pydantic.ConstrainedInt):
    strict = True
    ge = 0


class WeightedAdder(function_params.FunctionParams):
    """
    Creates a circuit implementing a scalar product between an n-qubit state |q1,q2,...,qn> and an n-length non-negative
    integer vector (w1,w2,...wn), such that the result of the output register is |q1*w1+q2*w2+...qn*wn>.
    If no weights are provided, they are default to 1 for every qubit.
    """

    num_state_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of input qubits"
    )
    weights: List[pydanticStrictNonNegativeInteger] = pydantic.Field(
        default=None,
        description="List of non-negative integers corresponding to the weight of each qubit",
    )
    inverse: bool = pydantic.Field(
        default=False, description="Create the inverse gate of weighted adder"
    )

    @pydantic.validator("weights", always=True, pre=True)
    def validate_weights(cls, weights, values):
        num_state_qubits = values.get("num_state_qubits")
        if weights is None:
            return [1] * num_state_qubits
        if len(weights) != num_state_qubits:
            raise ValueError(LENGTH_ERROR_MESSAGE)
        return weights

    def _create_io_names(self):
        if self.inverse:
            self._input_names = [STATE, SUM]
        else:
            self._input_names = [STATE]
        self._output_names = [STATE, SUM]
