from typing import List

import pydantic

from classiq.interface.generator import function_params


class QFT(function_params.FunctionParams):
    """
    Creates a quantum Fourier transform on a specified number of qubits.
    Use the inverse flag to create the inverse QFT circuit.
    """

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits on which the QFT acts."
    )
    approximation_degree: pydantic.NonNegativeInt = pydantic.Field(
        default=0,
        description="The degree of approximation (0 for no approximation). The smallest "
        "'approximation_degree' rotation angles are dropped from the QFT.",
    )
    do_swaps: bool = pydantic.Field(
        default=True, description="Whether to include the final swaps in the QFT."
    )
    inverse: bool = pydantic.Field(
        default=False,
        description="If True, the inverse Fourier transform is constructed.",
    )

    _input_names: List[str] = pydantic.PrivateAttr(default=["IN"])
    _output_names: List[str] = pydantic.PrivateAttr(default=["OUT"])
