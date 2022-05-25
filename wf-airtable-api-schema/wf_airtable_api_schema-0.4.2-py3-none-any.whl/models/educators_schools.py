from datetime import date
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel

from . import response as response_models

MODEL_TYPE = "educator_school"


class APIEducatorSchoolRoles(str, Enum):
    FOUNDER = "Founder"
    TEACHER_LEADER = "Teacher Leader"
    EMERGING_TEACHER_LEADER = "Emerging Teacher Leader"
    CLASSROOM_STAFF = "Classroom Staff"
    FELLOW = "Fellow"
    OTHER = "Other"


class CommonAPIEducatorSchoolFields(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    roles: Optional[list[APIEducatorSchoolRoles]] = None
    currently_active: Optional[bool] = None
    mark_for_deletion: Optional[bool] = None


class CreateUpdateAPIEducatorSchoolFields(CommonAPIEducatorSchoolFields):
    educator_id: str = None
    school_id: str = None


class APIEducatorSchoolFields(CommonAPIEducatorSchoolFields):
    pass


class APIEducatorSchoolRelationships(BaseModel):
    educator: Optional[response_models.APILinksAndData] = None
    school: Optional[response_models.APILinksAndData] = None


class APIEducatorSchoolData(response_models.APIData):
    fields: APIEducatorSchoolFields


class ListAPIEducatorSchoolData(BaseModel):
    __root__: list[APIEducatorSchoolData]


class APIEducatorSchoolResponse(response_models.APIResponse):
    data: APIEducatorSchoolData


class ListAPIEducatorSchoolResponse(response_models.ListAPIResponse):
    data: list[Union[APIEducatorSchoolData, dict]]
