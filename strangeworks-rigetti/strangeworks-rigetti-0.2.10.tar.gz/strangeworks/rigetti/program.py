from __future__ import annotations
from pyquil import Program
import pyquil
from pyquil.api import QuantumExecutable, EncryptedProgram
import base64
import pickle
from typing import Dict, Union
from rpcq.messages import ParameterAref


class CompiledProgram(Program):
    def __init__(
        self,
        prg: Program,
        compiled_quil: str = None,
        encrypted_program: str = None,
        pickled_executable: str = None,
        digest: str = None,
    ):
        super().__init__(prg)
        self.compiled_quil = compiled_quil
        self.encrypted_program = encrypted_program
        self.digest = digest
        self.pyquil_program = prg
        self.pickled_executable = pickled_executable

    @classmethod
    def from_json(cls, program: Program, payload: dict) -> CompiledProgram:
        pickled_executable = None
        digest = None
        if program is None:
            pickled_program = payload["pickled_program"]
            pickle_bytes = base64.b64decode(pickled_program)
            program = pickle.loads(pickle_bytes)
        if "pickled_executable" in payload:
            pickled_executable = payload["pickled_executable"]
            digest = payload["digest"]
        return cls(
            prg=program,
            compiled_quil=payload["compiled_quil"],
            pickled_executable=pickled_executable,
            digest=digest,
        )

    def to_dict(cls) -> dict:
        pickle_bytes = pickle.dumps(exec)
        pickled_executable = base64.b64encode(pickle_bytes).decode("ascii")
        return {
            "compiled_quil": cls.compiled_quil,
            "pickled_program": pickled_executable,
        }

    def __str__(self):
        return self.compiled_quil


def executable_from_json(payload: dict) -> QuantumExecutable:
    pickled_executable = payload["pickled_executable"]
    pickle_bytes = base64.b64decode(pickled_executable)
    exec = pickle.loads(pickle_bytes)
    return exec


def encrypted_program_to_json(exec: EncryptedProgram) -> dict:
    pickle_bytes = pickle.dumps(exec)
    pickled_executable = base64.b64encode(pickle_bytes).decode("ascii")
    return {
        "compiled_quil": "",
        "pickled_executable": pickled_executable,
    }


def program_to_json(prg: Program) -> dict:
    pickled_bytes = pickle.dumps(prg)
    pickled_program = base64.b64encode(pickled_bytes).decode("ascii")
    return {
        "circuit": {
            "pickled_program": pickled_program,
        },
        "version": pyquil.pyquil_version,
        "circuit_type": "pyquil.Program",
    }