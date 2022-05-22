from typing import Union

import pydantic
from typing_extensions import Literal

from classiq.interface.chemistry.ground_state_problem import GroundStateProblem
from classiq.interface.generator import function_params


class HartreeFock(function_params.FunctionParams):
    gs_problem: Union[Literal["ground_state_problem"], GroundStateProblem]
    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    @pydantic.validator("gs_problem")
    def validate_gs_problem(cls, gs_problem):
        if not isinstance(gs_problem, GroundStateProblem):
            raise ValueError("ground state problem must be of type GroundStateProblem")
        return gs_problem
