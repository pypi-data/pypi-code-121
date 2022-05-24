from pydantic import (
    BaseModel,
    root_validator
)

from typing import Optional, List, Dict

from captur_ml_sdk.dtypes.generics import Image, TrainingMeta
from captur_ml_sdk.dtypes.interfaces.validators import check_images_or_imagefile_has_data


class PreRunEventData(BaseModel):
    request_id: str
    meta: Optional[TrainingMeta]
    images: Optional[List[Image]]
    imagesfile: Optional[str]
    model_name: str
    prediction_type: str
    model_format: str
    base_model_id: Optional[str]
    include_data: Optional[List[str]]
    exclude_classes: Optional[List[str]]
    base_dataset_id: Optional[str]
    mapping: Optional[Dict[str, Dict[str, str]]]

    root_validator(check_images_or_imagefile_has_data)
