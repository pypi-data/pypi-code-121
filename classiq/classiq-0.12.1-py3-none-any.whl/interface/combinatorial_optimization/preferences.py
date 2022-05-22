from typing import List, Optional

import pydantic

from classiq.interface.combinatorial_optimization.solver_types import QSolver
from classiq.interface.generator.model.constraints import Constraints
from classiq.interface.generator.model.model import BackwardsCompatibleBaseModel
from classiq.interface.generator.model.preferences.preferences import (
    Preferences,
    TranspilationOption,
)


class QAOAPreferences(BackwardsCompatibleBaseModel):
    qsolver: QSolver = pydantic.Field(
        default=QSolver.QAOAPenalty,
        description="Indicates whether to use QAOA with penalty terms or constrained QAOA.",
    )
    qaoa_reps: pydantic.PositiveInt = pydantic.Field(
        default=1, description="Number of layers in qaoa ansatz."
    )
    penalty_energy: float = pydantic.Field(
        default=None,
        description="Penalty energy for invalid solutions. The value affects "
        "the converges rate. Small positive values are preferred",
    )
    initial_state: Optional[List[int]] = pydantic.Field(
        default=None,
        description="Initial state in QAOA ansatz. The state should be a single basis state in the "
        "computational basis. For problems with binary or integer variables the string "
        "consists of binary or integer values respectively.",
    )

    constraints: Constraints = pydantic.Field(default_factory=Constraints)
    preferences: Preferences = pydantic.Field(
        default=Preferences(transpilation_option=TranspilationOption.NONE)
    )

    @pydantic.validator("penalty_energy", pre=True, always=True)
    def check_penalty_energy(cls, penalty_energy, values):
        qsolver = values.get("qsolver")
        if penalty_energy is not None and qsolver != QSolver.QAOAPenalty:
            raise ValueError("Use penalty_energy only for QSolver.QAOAPenalty.")

        if penalty_energy is None and qsolver == QSolver.QAOAPenalty:
            penalty_energy = 2

        return penalty_energy
