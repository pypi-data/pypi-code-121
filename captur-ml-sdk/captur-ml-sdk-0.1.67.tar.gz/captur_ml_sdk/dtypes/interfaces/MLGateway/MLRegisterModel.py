from pydantic import BaseModel, root_validator

from captur_ml_sdk.dtypes.generics import Meta
from captur_ml_sdk.dtypes.interfaces.validators import check_model_exists_in_gcp
from typing import Optional

class ModelRegisterRequest(BaseModel):
    meta: Optional[Meta]
    name: str
    version: str
    dataset_id: str
    model_type: Optional[str]

    _model_exists = root_validator(check_model_exists_in_gcp, allow_reuse=True)
