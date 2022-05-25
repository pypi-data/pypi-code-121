from datetime import date
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ..common import Pincode
from ..validators import normalize_str
from .enums import EmploymentStatus
from .enums import EnquiryReason
from .enums import FinancePurpose
from .enums import Gender
from .enums import MaritalStatus
from .enums import PhoneNumberType
from .enums import State


class PhoneNumber(BaseModel):
    phone_number: str = Field(max_length=20)
    extension: Optional[str] = Field(max_length=10)
    number_type: Optional[PhoneNumberType]

    _normalize_num = validator("phone_number", allow_reuse=True, pre=True)(
        normalize_str
    )


class Identity(BaseModel):
    id_number: str
    issue_date: Optional[date]
    expiration_date: Optional[date]

    _normalize_str = validator("id_number", allow_reuse=True, pre=True)(normalize_str)

    @root_validator
    def check_issue__before_expiration(cls, values: dict):
        if values.get("issue_date") and values.get("expiration_date"):
            assert (
                values["issue_date"] < values["expiration_date"]
            ), "issue date must be before expiration date"

        return values


class Address(BaseModel):
    address_line_1: str = Field(max_length=200)
    address_line_2: Optional[str] = Field(max_length=200)
    address_line_3: Optional[str] = Field(max_length=200)
    city: str = Field(max_length=50)
    landmark: Optional[str] = Field(max_length=40)
    state: State
    pincode: Pincode

    _normalize_strs = validator("address_line_1", "city", allow_reuse=True, pre=True)(
        normalize_str
    )


class Applicant(BaseModel):
    first_name: str = Field(max_length=40)
    middle_name_1: Optional[str] = Field(max_length=40)
    middle_name_2: Optional[str] = Field(max_length=40)
    middle_name_3: Optional[str] = Field(max_length=40)
    last_name: str = Field(max_length=60)
    gender: Gender
    date_of_birth: date
    email: Optional[str] = Field(max_length=80)
    phone_number: Optional[PhoneNumber]
    mobile_number: Optional[str] = Field(max_length=20)
    income: Optional[str] = Field(max_length=15)
    marital_status: Optional[MaritalStatus]
    employment_status: Optional[EmploymentStatus]
    time_with_employer: Optional[str] = Field(max_length=3)
    number_of_major_credit_cards_held: Optional[int] = Field(lt=1000)
    pan: Optional[Identity]
    passport: Optional[Identity]
    voter_id: Optional[Identity]
    drivers_licence: Optional[Identity]
    ration_card: Optional[Identity]
    uid: Optional[Identity]
    addresses: List[Address] = Field(min_items=1, max_items=2)

    _normalize_strs = validator("first_name", "last_name", allow_reuse=True, pre=True)(
        normalize_str
    )

    @root_validator
    def check_min_one_identity(cls, values: dict):
        identities = list()
        if values.get("phone_number"):
            identities.append(values["phone_number"].phone_number)

        identity_keys = ["pan", "passport", "voter_id"]
        for key in identity_keys:
            if values.get(key):
                identities.append(values[key].id_number)

        assert any(
            identities
        ), "at least one of the following is required: phone_number, pan, passport, voter_id"

        return values


class ExperianRequest(BaseModel):
    ft_reference_number: Optional[str] = Field(max_length=6)
    customer_reference_number: Optional[str] = Field(max_length=12)
    enquiry_reason: EnquiryReason
    finance_purpose: FinancePurpose
    amount_financed: int
    duration_of_agreement: int = Field(lt=1000)
    applicant: Applicant
