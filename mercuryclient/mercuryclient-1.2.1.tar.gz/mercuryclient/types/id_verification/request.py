from datetime import date

from pydantic import BaseModel

from .enums import Countries, Gender, PassportTypes


class PassportDetails(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    expiry_date: date
    gender: Gender
    passport_type: PassportTypes
    country: Countries
