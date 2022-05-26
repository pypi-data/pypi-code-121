from pydantic import BaseModel,validator,EmailStr
from datetime import date
from model.common.utils import makeList,Duration
from model.common.person import Person
from model.common.id import ID,IDs
from typing import Optional,List
from model.common.employmentbase import EmploymentBase

class Employment(EmploymentBase):
    department:Optional[str]
    duties:list
    company_brief:str
    fullname_of_certificate_provider:Optional[str]
    position_of_certificate_provider:Optional[str]
    department_of_certificate_provider:Optional[str]
    phone_of_certificate_provider:Optional[str]
    email_of_certificate_provider:Optional[EmailStr]
    employment_certificate:bool
    
    _normalize_duties=validator('duties',allow_reuse=True,pre=True)(makeList)
    
