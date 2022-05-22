from typing import Optional

import pydantic


class HardwareEfficientConstraints(pydantic.BaseModel):
    num_qubits: int
    num_two_qubit_gates: Optional[int] = None
    num_one_qubit_gates: Optional[int] = None
    max_depth: Optional[int] = None


class HardwareEfficient(pydantic.BaseModel):
    structure: str
    constraints: HardwareEfficientConstraints
