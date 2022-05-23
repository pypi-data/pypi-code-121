from pydantic import BaseModel
from typing import Dict, Optional


class TrainingEvalEventData(BaseModel):
    model_id: str
    request_type: str
    request_id: str
    mapping: Optional[str]
