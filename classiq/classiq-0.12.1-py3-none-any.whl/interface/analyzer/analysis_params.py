from typing import Dict, List

import pydantic

from classiq.interface.helpers.custom_pydantic_types import pydanticNonEmptyString


class AnalysisParams(pydantic.BaseModel):
    qasm: pydanticNonEmptyString


class AnalysisRBParams(pydantic.BaseModel):
    hardware: str
    counts: List[Dict[str, int]]
    num_clifford: List[int]
