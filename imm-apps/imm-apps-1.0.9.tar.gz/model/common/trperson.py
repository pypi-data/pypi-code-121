from datetime import date
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from model.common.educationbase import EducationBase
from model.common.person import Person
from model.common.utils import normalize
from pydantic.class_validators import root_validator


class Personal(Person):
    used_last_name: Optional[str]
    used_first_name: Optional[str]
    uci: Optional[str]
    country_of_birth: str
    place_of_birth: str
    email: EmailStr

    native_language: str
    english_french: str
    which_one_better: Optional[str]
    language_test: bool

    _normalize_used_first_name = validator(
        "used_first_name", allow_reuse=True, check_fields=False
    )(normalize)
    _normalize_used_last_name = validator(
        "used_last_name", allow_reuse=True, check_fields=False
    )(normalize)

    # @root_validator
    # def checkAnswers(cls,values):
    #     questions=['english_french']
    #     explanations=['which_one_better']
    #     qas=dict(zip(questions,explanations))
    #     for k,v in qas.items():
    #         if values.get(k) and not values.get(v):
    #                 raise ValueError(f"Since {k} is true, but you did not answer the question {v} in info-position sheet")
    #     return values


class Marriage(BaseModel):
    marital_status: str
    married_date: Optional[date]
    sp_last_name: Optional[str]
    sp_first_name: Optional[str]
    sp_is_canadian: Optional[bool]
    previous_married: bool
    pre_sp_last_name: Optional[str]
    pre_sp_first_name: Optional[str]
    pre_relationship_type: Optional[str]
    pre_sp_dob: Optional[date]
    pre_start_date: Optional[date]
    pre_end_date: Optional[date]


class PersonId(BaseModel):
    variable_type: str
    display_type: str
    number: Optional[str]
    country: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]


# Not everyone has education. So, it's optional. Without start date and end date, the app will regard having no education
class Education(EducationBase):
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]


# Not everyone has employment experience. So, it's optional. Without start date and end date, the app will regard having no post secondary education
class Employment(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    job_title: Optional[str]
    company: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]


class Travel(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    length: Optional[int]
    destination: Optional[str]
    purpose: Optional[str]


class Family(BaseModel):
    last_name: str
    first_name: str
    native_last_name: str
    native_first_name: str
    marital_status: str
    date_of_birth: Optional[date]
    # place_of_birth:str
    birth_country: str
    # country_of_citizenship:str
    address: str
    occupation: str
    relationship: str
    # email:Optional[EmailStr]
    # date_of_death:Optional[date]
    # place_of_death:Optional[str]
    accompany_to_canada: bool


# Countries of Residence
class COR(BaseModel):
    start_date: date
    end_date: Optional[date]
    country: str
    status: str
