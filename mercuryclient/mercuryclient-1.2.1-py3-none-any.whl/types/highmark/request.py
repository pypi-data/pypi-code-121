from datetime import date
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ..common import Pincode
from ..validators import normalize_str
from .enums import AddressType
from .enums import CreditRequestType
from .enums import Gender
from .enums import IdentityType
from .enums import InquiryPurposeType
from .enums import InquiryPurposeTypeDescription
from .enums import InquiryStage
from .enums import PhoneNumberType
from .enums import RelationType
from .enums import State


class Identity(BaseModel):
    id_type: IdentityType
    id_number: str = Field(max_length=30)

    _normalize_id_num = validator("id_number", allow_reuse=True, pre=True)(
        normalize_str
    )


class Relation(BaseModel):
    relation_type: RelationType
    relation_name: str = Field(max_length=30)

    _normalize_name = validator("relation_name", allow_reuse=True, pre=True)(
        normalize_str
    )


class PhoneNumber(BaseModel):
    number_type: PhoneNumberType
    phone_number: str = Field(max_length=20)

    _normalize_num = validator("phone_number", allow_reuse=True, pre=True)(
        normalize_str
    )


class Address(BaseModel):
    address_type: AddressType
    address_line_1: str = Field(min_length=5, max_length=150)
    city: str = Field(max_length=20)
    state: State
    pincode: Pincode

    _normalize_strs = validator("address_line_1", "city", allow_reuse=True, pre=True)(
        normalize_str
    )


class Applicant(BaseModel):
    name: str = Field(max_length=100, strip_whitespace=True)
    other_names: Optional[List[str]] = Field(max_items=4)
    date_of_birth: date
    gender: Optional[Gender]
    identities: List[Identity] = Field(min_items=1)
    nominee: Optional[Relation]
    key_person: Optional[Relation]
    other_relations: Optional[List[Relation]] = Field(max_items=4)
    phone_numbers: Optional[List[PhoneNumber]]
    addresses: List[Address] = Field(min_items=1)

    _normalize_strs = validator("name", allow_reuse=True, pre=True)(normalize_str)
    _normalize_str_list = validator(
        "other_names", allow_reuse=True, pre=True, each_item=True
    )(normalize_str)

    @root_validator
    def check_min_one_relation(cls, values: dict):
        relations = list()
        relations.append(values.get("nominee"))
        relations.append(values.get("key_person"))
        relations.extend(values.get("other_relations", []) or [])
        assert any(
            relations
        ), "at least one of the following is required: nominee, key_person, other_relations"

        return values


class HighmarkRequest(BaseModel):
    inquiry_reference_number: str = Field(max_length=50)
    credit_request_type: CreditRequestType
    credit_transaction_id: str = Field(max_length=50)
    inquiry_purpose_type: InquiryPurposeType
    inquiry_purpose_type_desc: InquiryPurposeTypeDescription
    inquiry_stage: InquiryStage
    kendra_id: Optional[str] = Field(max_length=30)
    branch_id: Optional[str] = Field(max_length=30)
    los_app_id: str = Field(max_length=50)
    loan_amount: Optional[int]
    applicant: Applicant

    _normalize_strs = validator(
        "inquiry_reference_number",
        "credit_transaction_id",
        "los_app_id",
        allow_reuse=True,
        pre=True,
    )(normalize_str)
