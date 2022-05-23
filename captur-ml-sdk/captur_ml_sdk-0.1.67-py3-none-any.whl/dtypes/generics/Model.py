from captur_ml_sdk.dtypes.interfaces.validators import (
    check_model_exists,
    fetch_model_type
)

from pydantic import BaseModel, root_validator
from typing import Optional


class Model(BaseModel):
    name: str
    version: Optional[str] = "HEAD"
    type: Optional[str] = "classification"

    class Config:
        arbitrary_types_allowed = True

    _model_exists = root_validator(check_model_exists, allow_reuse=True)
    _get_model_type = root_validator(fetch_model_type, allow_reuse=True)
