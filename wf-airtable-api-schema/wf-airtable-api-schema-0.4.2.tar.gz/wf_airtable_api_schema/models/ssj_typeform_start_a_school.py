from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from . import response as response_models

MODEL_TYPE = "ssj_typeform_start_a_school"


class CreateApiSSJTypeformStartASchoolFields(BaseModel):
    first_name: str = None
    last_name: str = None
    email: str = None

    is_montessori_certified: bool = False
    is_seeking_montessori_certification: bool = False
    montessori_certification_certifier: Optional[str] = None
    montessori_certification_year: Optional[int] = None
    montessori_certification_levels: Optional[list[str]] = []

    school_location_city: str = None
    school_location_state: str = None
    school_location_country: str = None
    school_location_community: str = None
    contact_location_city: str = None
    contact_location_state: str = None
    contact_location_country: str = None

    has_interest_in_joining_another_school: bool = False
    is_willing_to_move: bool = False
    age_classrooms_interested_in_offering: Optional[list[str]] = []

    socio_economic_race_and_ethnicity: Optional[list[str]] = []
    socio_economic_race_and_ethnicity_other: Optional[str] = None
    socio_economic_lgbtqia_identifying: Optional[str] = None
    socio_economic_pronouns: Optional[str] = None
    socio_economic_pronouns_other: Optional[str] = None
    socio_economic_gender: Optional[str] = None
    socio_economic_gender_other: Optional[str] = None
    socio_economic_household_income: Optional[str] = None
    socio_economic_primary_language: Optional[str] = None
    socio_economic_primary_language_other: Optional[str] = None

    message: str = None
    equity_reflection: str = None
    receive_communications: bool = False

    entry_date: datetime = None


class ApiSSJTypeformStartASchoolFields(CreateApiSSJTypeformStartASchoolFields):
    response_id: str = None
    created_at: datetime = None


class ApiSSJTypeformStartASchoolData(response_models.APIData):
    fields: ApiSSJTypeformStartASchoolFields


class ApiSSJTypeformStartASchoolResponse(response_models.APIResponse):
    data: ApiSSJTypeformStartASchoolData
