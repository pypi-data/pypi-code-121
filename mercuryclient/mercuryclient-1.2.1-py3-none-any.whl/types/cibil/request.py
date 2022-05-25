from datetime import date
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator

from ..common import NormalizedString
from ..common import Pincode
from .enums import AddressType
from .enums import Gender
from .enums import IdentityType
from .enums import PhoneNumberType
from .enums import Purpose
from .enums import RelationType
from .enums import ResidenceType
from .enums import ScoreType
from .enums import State


class Identity(BaseModel):
    id_number: NormalizedString
    id_type: IdentityType


class PhoneNumber(BaseModel):
    phone_number: NormalizedString
    number_type: PhoneNumberType


class Address(BaseModel):
    address_type: Optional[AddressType]
    address_line_1: NormalizedString
    address_line_2: Optional[NormalizedString]
    city: NormalizedString
    pincode: Pincode
    residence_type: Optional[ResidenceType]
    state: State


class Relation(BaseModel):
    relation_type: RelationType
    relation_name: NormalizedString


class Applicant(BaseModel):
    first_name: NormalizedString
    middle_name: Optional[NormalizedString]
    last_name: NormalizedString
    date_of_birth: date
    gender: Gender
    email: Optional[NormalizedString]
    company_name: Optional[NormalizedString]
    identities: Optional[List[Identity]]
    other_identities: Optional[List[Identity]] = Field(max_items=3)
    phone_numbers: Optional[List[PhoneNumber]]
    addresses: List[Address] = Field(min_items=1)
    nominee: Optional[Relation]
    key_person: Optional[Relation]
    other_relations: Optional[List[Relation]]
    account_numbers: Optional[List[NormalizedString]]

    @root_validator
    def check_one_relation(cls, values: dict):
        identities = list()
        identities.extend(values.get("identities", []) or [])
        identities.extend(values.get("other_identities", []) or [])
        identities.extend(values.get("phone_numbers", []) or [])
        assert any(
            identities
        ), "at least one of the following is required: identities, other_identities, phone_numbers"

        return values


class CibilRequest(BaseModel):
    purpose: Purpose
    amount: int
    gst_state: State
    score_type: ScoreType
    applicant: Applicant
