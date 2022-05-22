from datetime import time
from typing import Dict, List

import pydantic

from classiq.interface.executor.vqe_result import VQEIntermediateData
from classiq.interface.generator.complex_type import Complex


class GroundStateExactResult(pydantic.BaseModel):
    energy: float
    nuclear_repulsion_energy: float
    total_energy: float
    hartree_fock_energy: float
    ground_state: Dict[str, Complex]


class GroundStateResult(GroundStateExactResult):
    time: time
    intermediate_results: List[VQEIntermediateData]
    optimal_parameters: Dict[str, float]
    convergence_graph_str: str
