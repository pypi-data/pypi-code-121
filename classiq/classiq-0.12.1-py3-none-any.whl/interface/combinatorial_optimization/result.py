from typing import List

import pydantic

from classiq.interface.status import Status


class AnglesResult(pydantic.BaseModel):
    status: Status
    details: List[float]


class PyomoObjectResult(pydantic.BaseModel):
    status: Status
    details: str
