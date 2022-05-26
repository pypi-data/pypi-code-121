import pyquil
from pyquil.api import AbstractCompiler, QuantumExecutable
from pyquil.quil import Program
from typing import Optional
import strangeworks

from strangeworks.rigetti.program import (
    CompiledProgram,
    executable_from_json,
    program_to_json,
)


class StrangeworksCompiler(AbstractCompiler):
    def __init__(self, target: str, as_qvm: str):
        self.target = target
        self.as_qvm = as_qvm

    def quil_to_native_quil(
        self, prg: Program, *, protoquil: Optional[bool] = None
    ) -> Program:
        payload = program_to_json(prg)
        payload["target"] = self.target
        payload["as_qvm"] = self.as_qvm
        payload["shots"] = prg.num_shots
        if protoquil:
            payload["protoquil"] = str(protoquil)
        res = strangeworks.client.rest_client.post(
            "/plugins/rigetti/compile?return_executable=False", json=payload
        )
        compiled_program = CompiledProgram.from_json(program=prg, payload=res)
        return compiled_program.pyquil_program

    def native_quil_to_executable(self, nq_program: Program) -> QuantumExecutable:
        payload = program_to_json(nq_program)
        payload["target"] = self.target
        payload["as_qvm"] = self.as_qvm
        payload["shots"] = nq_program.num_shots
        res = strangeworks.client.rest_client.post(
            "/plugins/rigetti/compile?return_executable=True", json=payload
        )
        return executable_from_json(res)

    def get_calibration_program(self, force_refresh: bool = False) -> Program:
        payload = {
            "as_qvm": self.as_qvm,
            "circuit": "",
            "circuit_type": "pyquil.Program",
            "version": pyquil.pyquil_version,
        }
        payload["target"] = self.target
        res = strangeworks.client.rest_client.post(
            "/plugins/rigetti/compile?get_calibration_program=True", json=payload
        )
        return CompiledProgram.from_json(program=None, payload=res)
