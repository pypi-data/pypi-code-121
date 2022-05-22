from collections import defaultdict
from enum import Enum
from typing import Dict, Optional, Union

import pydantic

from classiq.interface.generator.transpiler_basis_gates import TranspilerBasisGates


class OptimizationParameter(str, Enum):
    WIDTH = "width"
    DEPTH = "depth"
    NO_OPTIMIZATION = "no_opt"


OptimizationParameterType = Union[OptimizationParameter, TranspilerBasisGates]


class Constraints(pydantic.BaseModel):
    """
    Input constraints for the generated quantum circuit.
    """

    max_width: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="Maximum number of qubits in generated quantum circuit",
    )
    max_depth: Optional[pydantic.PositiveInt] = None

    max_gate_count: Dict[
        TranspilerBasisGates, pydantic.NonNegativeInt
    ] = pydantic.Field(default_factory=lambda: defaultdict(int))

    optimization_parameter: OptimizationParameterType = pydantic.Field(
        default=OptimizationParameter.NO_OPTIMIZATION,
        description="If set, the synthesis engine optimizes the solution"
        " according to that chosen parameter",
    )

    class Config:
        extra = "forbid"
