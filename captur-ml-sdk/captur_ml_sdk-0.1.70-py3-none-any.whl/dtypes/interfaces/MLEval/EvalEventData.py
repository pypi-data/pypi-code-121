from captur_ml_sdk.dtypes.generics import Image
from pydantic import BaseModel
from typing import List, Optional, Dict

class EvalEventData(BaseModel):
    request_id: str
    webhooks: str
    images: Optional[List[Image]]
    evaluation_file: Optional[str]
    last_file: Optional[bool]
    prediction_model_name: str
    label_model_name: str
    model_id: str
    model_type: str
    mapping: Optional[Dict[str, Dict[str, str]]]
