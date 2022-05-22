from enum import Enum
from typing import Optional

import pydantic

from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator import function_params


class ExponentiationOptimization(str, Enum):
    MINIMIZE_DEPTH = "MINIMIZE_DEPTH"
    MINIMIZE_ERROR = "MINIMIZE_ERROR"


class ExponentiationConstraints(pydantic.BaseModel):
    max_depth: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None, description="Maximum depth of the exponentiation circuit."
    )
    max_error: Optional[pydantic.PositiveFloat] = pydantic.Field(
        default=None,
        description="Maximum approximation error of the exponentiation circuit.",
    )


class Exponentiation(function_params.FunctionParams):
    """
    Exponantiation of a Hermitian Pauli sum operator.
    """

    pauli_operator: PauliOperator = pydantic.Field(
        description="A weighted sum of Pauli strings."
    )
    evolution_coefficient: float = pydantic.Field(
        default=1.0, description="A global coeffient multiplying the operator."
    )
    constraints: ExponentiationConstraints = pydantic.Field(
        default_factory=ExponentiationConstraints,
        description="Constraints for the exponentiation.",
    )
    optimization: ExponentiationOptimization = pydantic.Field(
        default=ExponentiationOptimization.MINIMIZE_DEPTH,
        description="What attribute to optimize.",
    )
    use_naive_evolution: bool = pydantic.Field(
        default=False, description="Whether to evolve the operator naively"
    )
    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    @pydantic.validator("pauli_operator")
    def validate_is_hermitian(cls, pauli_operator: PauliOperator):
        if not pauli_operator.to_hermitian():
            raise ValueError("Cefficients of the Hamiltonian must be real numbers")
        return pauli_operator
