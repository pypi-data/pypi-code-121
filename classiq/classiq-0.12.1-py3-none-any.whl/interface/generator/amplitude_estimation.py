from typing import TYPE_CHECKING, List, Union

import pydantic

from classiq.interface.generator import function_params

if TYPE_CHECKING:
    pydanticNonEmptyNonNegativeIntList = List[int]
else:
    pydanticNonEmptyNonNegativeIntList = pydantic.conlist(
        pydantic.conint(ge=0), min_items=1
    )


class AmplitudeEstimation(function_params.FunctionParams):
    """
    Creates a quantum circuit for ampitude estimation
    Provide the state preparation with a qasm string
    """

    state_preparation: str = pydantic.Field(
        description='The state preparation circuit in qasm format. Replace "..." with '
        "'...'. The total number of qubits is the sum of the state preparation qubits "
        "and `num_eval_qubits`"
    )

    objective_qubits: Union[
        pydanticNonEmptyNonNegativeIntList, pydantic.NonNegativeInt
    ] = pydantic.Field(
        default=0,
        description='The list of "good" qubits. The good states are the ones that have '
        "1's in the positions defined by objective qubits. The indices in this list "
        "must be in the range defined by `state_preparation`",
    )

    num_eval_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits to evaluate on the amplitude estimation. "
        "More evaluation qubits provide a better estimate of the good states' amplitude"
    )

    @pydantic.validator("state_preparation")
    def vscode_qasm2circuit(cls, v):
        VSCODE_QUOTE = "'"
        QASM_QUOTES = '"'
        return v.replace(VSCODE_QUOTE, QASM_QUOTES)
