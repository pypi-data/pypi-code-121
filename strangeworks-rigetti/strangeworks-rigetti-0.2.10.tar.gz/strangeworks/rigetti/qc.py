import pyquil
from pyquil import Program
from pyquil.api import QuantumComputer, EncryptedProgram
from pyquil.api._qam import QAMExecutionResult
from strangeworks.errors.error import StrangeworksError
import strangeworks
from strangeworks.rigetti.program import (
    CompiledProgram,
    encrypted_program_to_json,
    program_to_json,
)
from strangeworks.rigetti.compiler import StrangeworksCompiler
from strangeworks.rigetti.result import StrangeworksExecutionResult
from strangeworks.backend.backends import Backend


class QuantumComputer(QuantumComputer):
    def __init__(self, ogc: QuantumComputer, backend: Backend, as_qvm: bool):
        self.as_qvm = "True" if as_qvm else "False"
        self.sw_backend = backend
        super().__init__(
            name=ogc.name,
            qam=ogc.qam,
            compiler=StrangeworksCompiler(target=ogc.name, as_qvm=self.as_qvm),
        )

    def compile(self, program: Program) -> CompiledProgram:
        nq_program = self.compiler.quil_to_native_quil(program)
        return self.compiler.native_quil_to_executable(nq_program)

    def run(self, program, shots: int = 1) -> StrangeworksExecutionResult:
        payload = {"as_qvm": self.as_qvm}
        if isinstance(program, CompiledProgram):
            payload = self.__serialize_compiled_program(program)
            shots = program.num_shots
        elif isinstance(program, EncryptedProgram):
            payload = self.__serialize_encrypted_program(program)
        elif isinstance(program, Program):
            payload = self.__serialize_program(program)
            shots = program.num_shots
        else:
            raise StrangeworksError.invalid_argument(
                "must pass either a Program or CompiledProgram to execute"
            )

        results = strangeworks.client.circuit_runner.run(
            payload=payload,
            shots=shots,
            backend=self.sw_backend,
            async_execution=True,
        )

        return StrangeworksExecutionResult.from_json(results)

    def __serialize_compiled_program(self, qe: CompiledProgram) -> dict:
        return {
            "as_qvm": self.as_qvm,
            "circuit": qe.to_dict(),
            "circuit_type": "strangeworks.rigetti.CompiledProgram",
            "version": pyquil.pyquil_version,
        }

    def __serialize_encrypted_program(self, qe: EncryptedProgram) -> dict:
        return {
            "as_qvm": self.as_qvm,
            "circuit": encrypted_program_to_json(qe),
            "circuit_type": "pyquil.EncryptedProgram",
            "version": pyquil.pyquil_version,
        }

    def __serialize_program(self, p: Program) -> dict:
        d = program_to_json(p)
        d["as_qvm"] = self.as_qvm
        return d
