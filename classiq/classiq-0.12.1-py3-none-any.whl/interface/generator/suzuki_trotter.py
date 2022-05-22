import pydantic

from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator import function_params
from classiq.interface.generator.parameters import ParameterFloatType


class SuzukiParameters(pydantic.BaseModel):
    order: pydantic.PositiveInt = pydantic.Field(
        default=1,
        description="The order of the Suzuki-Trotter. Supports only order equals to 1 or an even number",
    )
    repetitions: pydantic.NonNegativeInt = pydantic.Field(
        default=1, description="The number of repetitions in the Suzuki-Trotter"
    )

    @pydantic.validator("order")
    def validate_order(cls, order) -> int:
        if order != 1 and order % 2:
            raise NotImplementedError
        return order


class SuzukiTrotter(function_params.FunctionParams):
    """
    Suzuki trotterization of a Hermitian operator
    """

    pauli_operator: PauliOperator = pydantic.Field(
        description="A weighted sum of Pauli strings."
    )
    evolution_coefficient: ParameterFloatType = pydantic.Field(
        default=1.0, description="A global coeffient multiplying the operator."
    )
    use_naive_evolution: bool = pydantic.Field(
        default=False, description="Whether to evolve the operator naively."
    )
    suzuki_parameters: SuzukiParameters = pydantic.Field(
        default_factory=SuzukiParameters, description="The Suziki parameters."
    )
    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    @pydantic.validator("pauli_operator")
    def validate_is_hermitian(cls, pauli_operator: PauliOperator):
        if not pauli_operator.to_hermitian():
            raise ValueError("Cefficients of the Hamiltonian must be real numbers")
        return pauli_operator
