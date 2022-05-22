from typing import Any, Dict, Union

import pydantic
from typing_extensions import Literal

from classiq.interface.backend.backend_preferences import IonqBackendPreferences
from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.executor.hamiltonian_minimization_problem import (
    HamiltonianMinimizationProblem,
)
from classiq.interface.executor.quantum_program import (
    QuantumInstructionSet,
    QuantumProgram,
)
from classiq.interface.generator.generation_metadata import GenerationMetadata


class GenerationMetadataExecution(GenerationMetadata):
    execution_type: Literal["generation_metadata"] = "generation_metadata"


class QuantumProgramExecution(QuantumProgram):
    execution_type: Literal["quantum_program"] = "quantum_program"


class HamiltonianMinimizationProblemExecution(HamiltonianMinimizationProblem):
    execution_type: Literal[
        "hamiltonian_minimization_problem"
    ] = "hamiltonian_minimization_problem"


class ExecutionRequest(pydantic.BaseModel):
    execution_payload: Union[
        GenerationMetadataExecution,
        QuantumProgramExecution,
        HamiltonianMinimizationProblemExecution,
    ]
    preferences: ExecutionPreferences = pydantic.Field(
        default_factory=ExecutionPreferences,
        description="preferences for the execution",
    )

    @pydantic.validator("preferences")
    def validate_ionq_backend(
        cls, preferences: ExecutionPreferences, values: Dict[str, Any]
    ):
        """
        This function implement the following check:
        BE \\ payload | IonQ program | Qasm program | Other
        --------------|--------------|--------------|------
        IonQ backend  |       V      |      V       |   X
        Other backend |       X      |      V       |   V
        Since:
        - We can't execute non-programs on the IonQ backends
        - We can't execute IonQ programs on non-IonQ backends
        """
        quantum_program = values.get("execution_payload")
        is_ionq_backend = isinstance(
            preferences.backend_preferences, IonqBackendPreferences
        )
        if isinstance(quantum_program, QuantumProgram):
            if (
                quantum_program.syntax == QuantumInstructionSet.IONQ
                and not is_ionq_backend
            ):
                raise ValueError("Can only execute IonQ code on IonQ backend.")
        else:
            # If we handle anything other than a program.
            if is_ionq_backend:
                raise ValueError(
                    "IonQ backend supports only execution of QuantumPrograms"
                )
        return preferences
