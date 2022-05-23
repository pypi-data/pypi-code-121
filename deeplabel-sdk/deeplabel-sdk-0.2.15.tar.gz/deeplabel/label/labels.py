from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import validator

from pydantic import Field
from deeplabel.basemodel import MixinConfig, DeeplabelBase
import deeplabel.client


class DetectionLabelType(Enum):
    OBJECT = "OBJECT"
    ACTION = "ACTION"


class DetectionLabelCategory(Enum):
    DETECTION = "DETECTION"
    CLASSIFICATION = "CLASSIFICATION"

class DetectionLabel(DeeplabelBase):
    """Detection Label"""
    color: str  # hashvalue eg. \#efbg17
    name: str
    type: DetectionLabelType
    category: DetectionLabelCategory
    id:Optional[str]
    label_id: Optional[str]
    is_deleted:bool = False
    client:Any = Field(None, exclude=True)

    @validator('label_id', always=True)
    def validate_label_id(cls, v, values):
        if v is None:
            assert 'id' in values, f"DetectionLabel should either have label_id or id key. {v} ; {values}"
            return values['id']
        return v

    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["DetectionLabel"]:
        resp = client.get("/labels", params=params)
        labels = resp.json()["data"]["labels"]
        return [cls(**label, client=client) for label in labels]
