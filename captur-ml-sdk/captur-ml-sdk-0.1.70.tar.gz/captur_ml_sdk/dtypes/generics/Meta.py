from pydantic import (
    BaseModel, HttpUrl
)
from typing import Optional


class Meta(BaseModel):
    webhooks: Optional[HttpUrl]


class TrainingMeta(BaseModel):
    webhooks: Optional[HttpUrl]
    budget_milli_node_hours: Optional[int] = 8000


class EvaluationMeta(BaseModel):
    webhooks: Optional[HttpUrl]
    write_to_file: Optional[bool]
    last_file: Optional[bool]
    request_id: Optional[str]
    prediction_model_name: Optional[str]
    label_model_name: Optional[str]
