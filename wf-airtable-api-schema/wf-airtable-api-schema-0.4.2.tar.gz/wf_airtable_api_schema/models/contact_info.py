from typing import Optional

from pydantic import BaseModel

MODEL_TYPE = "contact_info"


class CreateAPIContactInfoFields(BaseModel):
    type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = False


class APIContactInfoFields(CreateAPIContactInfoFields):
    pass
