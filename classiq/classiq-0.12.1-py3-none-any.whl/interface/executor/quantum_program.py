from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

import pydantic

from classiq.interface.backend.ionq import ionq_quantum_program
from classiq.interface.backend.pydantic_backend import pydanticArgumentNameType
from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet

Arguments = Optional[Dict[pydanticArgumentNameType, Any]]


class QuantumProgram(pydantic.BaseModel):
    syntax: QuantumInstructionSet = pydantic.Field(
        ..., description="The syntax of the program."
    )
    code: Union[str, ionq_quantum_program.IonqQuantumCircuit] = pydantic.Field(
        ..., description="The textual representation of the program"
    )
    arguments: Arguments = pydantic.Field(
        None,
        description="The parameters dictionary for a parametrized quantum program. "
        "Relevant for Q# programs only.",
    )

    @pydantic.validator("code")
    def load_quantum_program(cls, code: str, values: Dict[str, Any]):
        if not isinstance(code, str):
            return code

        syntax = values.get("syntax")
        if syntax == QuantumInstructionSet.IONQ:
            return ionq_quantum_program.IonqQuantumCircuit.parse_raw(code)

        return code

    @pydantic.validator("arguments")
    def validate_arguments(cls, arguments: Arguments, values: Dict[str, Any]):
        if arguments and values.get("syntax") != QuantumInstructionSet.QSHARP:
            raise ValueError("Only Q# programs support arguments")
        return arguments

    @staticmethod
    def from_file(
        file_path: Union[str, Path],
        syntax: Optional[Union[str, QuantumInstructionSet]] = None,
        arguments: Optional[Arguments] = None,
    ) -> QuantumProgram:
        path = Path(file_path)
        code = path.read_text()
        if syntax is None:
            syntax = path.suffix.lstrip(".")
        return QuantumProgram(syntax=syntax, code=code, arguments=arguments)
