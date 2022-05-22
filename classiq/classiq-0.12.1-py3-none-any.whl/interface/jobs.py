from enum import Enum
from typing import Any, Dict, Generic, TypeVar, Union

import pydantic
from pydantic.generics import GenericModel

JSONObject = Dict[str, Any]
T = TypeVar("T", bound=Union[pydantic.BaseModel, JSONObject])
AUTH_HEADER = "Classiq-BE-Auth"


class JobID(pydantic.BaseModel):
    job_id: str


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    READY = "READY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

    def is_final(self) -> bool:
        return self in (self.COMPLETED, self.FAILED, self.CANCELLED)


class JobDescription(GenericModel, Generic[T]):
    status: JobStatus
    description: T

    @pydantic.validator("description")
    def check_details(cls, description: T, values):
        status: JobStatus = values["status"]
        if status.is_final():
            has_details = (
                hasattr(description, "details")
                if isinstance(description, pydantic.BaseModel)
                else "details" in description
            )
            if not has_details:
                raise ValueError("Description of finished job is missing details")
        return description
