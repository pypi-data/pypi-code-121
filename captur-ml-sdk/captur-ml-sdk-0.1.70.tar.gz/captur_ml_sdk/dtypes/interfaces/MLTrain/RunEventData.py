from pydantic import BaseModel
from typing import Optional, Dict


class RunEventData(BaseModel):
    gcs_source: str
    model_name: str
    prediction_type: str
    model_format: str
    base_model_id: Optional[str]
    training_display_name: str
    request_id: str
    request_type: str
    mapping: Optional[Dict[str, Dict[str, str]]]
    webhooks: str
    budget_milli_node_hours: int
    percentage_images_included: Optional[float]
