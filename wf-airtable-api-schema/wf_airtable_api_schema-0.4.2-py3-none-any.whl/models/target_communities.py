from typing import Optional

from pydantic import BaseModel

MODEL_TYPE = "target_community"


class APITargetCommunityFields(BaseModel):
    name: Optional[str] = None
