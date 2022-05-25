from pydantic import BaseModel
from typing import Optional


class Altinn3CloudEvent(BaseModel):
    alternativesubject: str
    data: Optional[str]
    datacontenttype: Optional[str]
    id: str
    source: str
    specversion: str
    subject: str
    time: str
    type: str
