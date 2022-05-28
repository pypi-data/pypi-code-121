from dataclasses import dataclass
from datetime import date
from email.errors import ObsoleteHeaderDefect
from pydantic import BaseModel
from typing import Optional, List
from model.common.address import Address


class TrCase(BaseModel):
    service_in: str
    application_purpose: Optional[str]  # 5257需要，1294 5 不需要
    same_as_cor: bool
    applying_country: Optional[str]
    applying_status: Optional[str]
    applying_start_date: Optional[date]
    applying_end_date: Optional[date]
    consent_of_info_release: bool
    submission_date: Optional[date]


class TrCaseIn(BaseModel):
    service_in: str
    application_purpose: Optional[str]  # TODO: consider
    original_entry_date: date
    original_entry_place: str
    original_purpose: str
    original_other_reason: Optional[str]
    most_recent_entry_date: date
    most_recent_entry_place: str
    doc_number: Optional[str]
    consent_of_info_release: bool
    submission_date: Optional[date]


class Visa(BaseModel):
    visit_purpose: str
    duration_from: date
    duration_to: date
    funds_available: int
    name1: Optional[str]
    relationship1: Optional[str]
    address1: Optional[str]
    name2: Optional[str]
    relationship: Optional[str]
    address2: Optional[str]


class Sp(BaseModel):
    school_name: str
    study_level: str
    study_field: str
    province: str
    city: str
    address: str
    dli: str
    student_id: str
    duration_from: date
    duration_to: date
    tuition_cost: Optional[str]
    room_cost: Optional[str]
    other_cost: Optional[str]
    fund_available: str
    paid_person: str
    other: Optional[str]


class Wp(BaseModel):
    work_permit_type: str
    other_explain: Optional[str]
    employer_name: Optional[str]
    employer_address: Optional[str]
    work_province: Optional[str]
    work_city: Optional[str]
    work_address: Optional[str]
    job_title: Optional[str]
    brief_duties: Optional[str]
    duration_from: date
    duration_to: date
    lmia_num_or_offer_num: Optional[str]
    # pnp_certificated: bool
    caq_number: Optional[str]
    expiry_date: Optional[date]


class VrInCanada(BaseModel):
    application_purpose: str
    visit_purpose: str
    other_explain: Optional[str]
    duration_from: date
    duration_to: date
    funds_available: int
    paid_by: str
    other_payer_explain: Optional[str]
    name1: Optional[str]
    relationship1: Optional[str]
    address1: Optional[str]
    name2: Optional[str]
    relationship2: Optional[str]
    address2: Optional[str]


class SpInCanada(BaseModel):
    application_purpose: str
    apply_work_permit: bool
    work_permit_type: Optional[str]
    caq_number: Optional[str]
    expiry_date: Optional[date]
    school_name: str
    study_level: str
    study_field: str
    province: str
    city: str
    address: str
    dli: str
    student_id: str
    duration_from: date
    duration_to: date
    tuition_cost: Optional[str]
    room_cost: Optional[str]
    other_cost: Optional[str]
    fund_available: str
    paid_person: str
    other: Optional[str]


class WpInCanada(BaseModel):
    application_purpose: str
    caq_number: Optional[str]
    expiry_date: Optional[date]
    work_permit_type: str
    employer_name: Optional[str]
    employer_address: Optional[str]
    work_province: Optional[str]
    work_city: Optional[str]
    work_address: Optional[str]
    job_title: Optional[str]
    brief_duties: Optional[str]
    duration_from: Optional[date]
    duration_to: Optional[date]
    lmia_num_or_offer_num: Optional[str]
    pnp_certificated: bool


class TrBackground(BaseModel):
    q1a: bool
    q1b: bool
    q1c: Optional[str]
    q2a: bool
    q2b: bool
    q2c: bool
    q2d: Optional[str]
    q3a: bool
    q3b: Optional[str]
    q4a: bool
    q4b: Optional[str]
    q5: bool
    q6: bool
