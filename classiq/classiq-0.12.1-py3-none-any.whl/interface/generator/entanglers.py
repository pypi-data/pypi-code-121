import pydantic

from classiq.interface.helpers.custom_pydantic_types import pydanticLargerThanOneInteger


class SquareClusterEntanglerParameters(pydantic.BaseModel):
    num_of_qubits: pydanticLargerThanOneInteger
    schmidt_rank: pydantic.NonNegativeInt


class Open2DClusterEntanglerParameters(pydantic.BaseModel):
    qubit_count: pydanticLargerThanOneInteger
    schmidt_rank: pydantic.NonNegativeInt
