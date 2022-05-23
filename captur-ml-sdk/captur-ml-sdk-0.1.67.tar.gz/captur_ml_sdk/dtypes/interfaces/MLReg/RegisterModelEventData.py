from captur_ml_sdk.dtypes.generics.Meta import Meta
from pydantic import BaseModel
from typing import Optional


class RegisterModelEventData(BaseModel):
    model_name: str
    model_id: str
    dataset_id: str
    model_type: Optional[str]
    meta: Optional[Meta]
