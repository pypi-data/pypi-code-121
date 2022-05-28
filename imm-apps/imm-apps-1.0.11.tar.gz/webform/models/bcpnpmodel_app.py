from email.errors import ObsoleteHeaderDefect
from optparse import Option
from typing import List, Optional, Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.employmentbase import EmploymentBase
from model.common.jobofferbase import JobofferBase
from model.common.id import ID
from model.common.person import Person
from model.common.cor import CORs, COR
from model.common.status import Status
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.prportal.data.country_residence import country_residence
from model.common.contact import ContactBase
from model.common.family import FamilyBase


class PersonId(ID):
    pass


class CanadaRelative(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    sex: Optional[str]
    relationship: Optional[str]
    status: Optional[str]
    age: Optional[int]
    city: Optional[str]
    province: Optional[str]
    years_in_canada: Optional[int]


class Rcic(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]


class General(BaseModel):
    legal_name: str
    operating_name: Optional[str]
    corporate_structure: str
    other_explaination: Optional[str]
    establish_date: date
    industry: str
    registration_number: str
    ft_employee_number: int
    establish_date: date
    website: Optional[str]


class Contact(ContactBase):
    position: str


class ErAddress(Address):
    phone: str


class Joboffer(JobofferBase):
    phone: str
    is_working: bool
    license_request: bool


class Employment(EmploymentBase):
    bcpnp_qualified: bool
    phone_of_certificate_provider: Optional[str]
    website: Optional[str]
    unit: Optional[str]
    street_address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    postcode: Optional[str]
    duties: Optional[str]


class Marriage(BaseModel):
    marital_status: Optional[str]
    married_date: Optional[date]
    sp_last_name: Optional[str]
    sp_first_name: Optional[str]
    sp_in_canada: Optional[bool]
    sp_canada_status: Optional[str]
    sp_canada_status_end_date: Optional[date]
    sp_in_canada_other: Optional[str]
    sp_in_canada_work: Optional[bool]
    sp_canada_occupation: Optional[str]
    sp_canada_employer: Optional[str]


class Personal(Person):
    uci: Optional[str]

    _normalize_used_first_name = validator(
        "used_first_name", allow_reuse=True, check_fields=False
    )(normalize)
    _normalize_used_last_name = validator(
        "used_last_name", allow_reuse=True, check_fields=False
    )(normalize)

    @property
    def user_id(self):
        dob = self.dob.strftime(("%Y-%m-%d"))
        return (
            self.last_name[0].upper()
            + self.first_name[0]
            + dob.split("-")[0]
            + dob.split("-")[1]
            + dob.split("-")[2]
        )

    @property
    def password(self):
        return "Super" + str(datetime.today().year) + "!"


class Education(EducationBase):
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    is_trade: Optional[bool]
    graduate_date: Optional[date]


class Family(FamilyBase):
    country_of_citizenship: Optional[str]
    address: Optional[str]
    date_of_death: Optional[date]
    marital_status: Optional[str]


class Bcpnp(BaseModel):
    intended_city: str
    # has_current_app: bool
    # has_applied_before: bool
    # pre_file_no: Optional[str]
    case_stream: Optional[str]
    q1: bool
    q1_explaination: Optional[str]
    q2: bool
    q2_explaination: Optional[str]
    q3: bool
    q3_explaination: Optional[str]
    q4: bool
    q4_file_number: Optional[str]
    q4_explaination: Optional[str]
    q5: bool
    q5_explaination: Optional[str]
    q6: bool
    q6_explaination: Optional[str]
    q7: bool
    q7_explaination: Optional[str]


class Ee(BaseModel):
    ee_profile_no: str
    ee_expiry_date: date
    ee_jsvc: str
    ee_score: str
    ee_noc: str
    ee_job_title: str


class BcpnpModelApp(CommonModel):
    personal: Personal
    marriage: Marriage
    cor: List[COR]
    status: Status
    general: General
    joboffer: Joboffer
    family: List[Family]
    eraddress: List[ErAddress]
    contact: List[Contact]
    bcpnp: Bcpnp
    education: List[Education]
    employment: List[Employment]
    rcic: Rcic
    canadarelative: List[CanadaRelative]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/er.xlsx','excel/pa.xlsx','excel/bcpnp.xlsx'])
        else:
            if excels is None or len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())


class BcpnpEEModelApp(BcpnpModelApp):
    ee: Ee

    def __init__(self, excels=None, output_excel_file=None):
        super().__init__(excels=excels, output_excel_file=output_excel_file)
