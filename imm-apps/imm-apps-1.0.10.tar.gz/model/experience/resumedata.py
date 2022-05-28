from pydantic import BaseModel,validator,EmailStr
from datetime import date
from typing import Optional
from model.common.utils import makeList
from model.common.person import Person
from model.common.mixins import DurationMixin
from model.common.employmentbase import EmploymentBase
from model.common.educationbase import EducationBase

class PersonalAssess(BaseModel):
    self_description:Optional[str]
    skill_list:list
    activity:Optional[list]
    
    _str2bool_activity=validator('activity',allow_reuse=True,pre=True)(makeList)
    _str2bool_skill_list=validator('skill_list',allow_reuse=True,pre=True)(makeList)

class Personal(Person):
    email:Optional[EmailStr]
    
    @property
    def birth_day(self):
        return self.dob.strftime('%b %d, %Y')
    
class Education(EducationBase):
    city:str
    country:str
    description:Optional[str]

class Language(BaseModel):
    reading:str
    writting:str
    listening:str
    speaking:str
    test_type: str
    remark: str
    
class Employment(EmploymentBase):
    duties:list
    
    _str2bool_duties=validator('duties',allow_reuse=True,pre=True)(makeList)
