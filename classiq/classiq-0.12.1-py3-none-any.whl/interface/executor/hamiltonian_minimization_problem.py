import pydantic

from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.executor.quantum_program import QuantumProgram


class HamiltonianMinimizationProblem(pydantic.BaseModel):
    ansatz: QuantumProgram
    hamiltonian: PauliOperator
