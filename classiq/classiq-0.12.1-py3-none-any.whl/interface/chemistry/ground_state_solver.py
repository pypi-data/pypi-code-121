from typing import Optional, Union

import pydantic

from classiq.interface.backend.backend_preferences import BackendPreferencesTypes
from classiq.interface.chemistry.ground_state_problem import GroundStateProblem
from classiq.interface.executor.optimizer_preferences import GroundStateOptimizer
from classiq.interface.generator.result import GeneratedCircuit


class GroundStateSolver(pydantic.BaseModel):
    ground_state_problem: GroundStateProblem = pydantic.Field(
        description="GroundStateProblem object"
    )
    ansatz: Union[str, GeneratedCircuit, None] = pydantic.Field(
        description="GeneratedCircuit object or a str of the ansztz circuit"
    )
    optimizer_preferences: Optional[GroundStateOptimizer] = pydantic.Field(
        description="GroundStateOptimizer object"
    )
    backend_preferences: Optional[BackendPreferencesTypes] = pydantic.Field(
        description="BackendPreferences object"
    )
