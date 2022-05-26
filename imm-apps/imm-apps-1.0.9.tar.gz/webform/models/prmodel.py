from termcolor import colored
from utils.utils import checkContinuity
from typing import List, Optional, Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.id import ID
from model.common.person import Person
from datetime import date
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.prportal.data.country_residence import country_residence


class PersonId(ID):
    pass


class PRCase(BaseModel):
    imm_program: str
    imm_category: str
    imm_under: Optional[str]
    communication_language: str
    interview_language: str
    need_translator: bool
    intended_province: str
    intended_city: str


class COR(BaseModel):
    start_date: date
    end_date: date
    country: str
    status: str
    explanation: Optional[str]

    @validator("country")
    def must_in_list(cls, v):
        if v not in country_residence.keys():
            similars = []
            # 全部变小写比较
            for key in country_residence.keys():
                if key.lower() == v.lower():
                    raise ValueError(
                        f"Please use correct upper letter. The country is {key}, but your input is {v}"
                    )
                elif v.lower() in key.lower():
                    similars.append(f"Possible matching country {key}")
            if similars:
                raise ValueError(
                    f"Your input {v} may matches:",
                    similars,
                    "Please correct it in your excel table-cor",
                )
        return v


class CORs(object):
    def __init__(self, cors: List[COR]):
        self.cors = cors

    @property
    def current(self):
        if len(self.cors) >= 1:
            return self.cors[0]
        else:
            raise ValueError(
                f"table-cor must have values, and the first line must be current residence country."
            )


class Marriage(BaseModel):
    marital_status: str
    married_date: Optional[date]
    sp_last_name: Optional[str]
    sp_first_name: Optional[str]
    previous_married: bool
    pre_sp_last_name: Optional[str]
    pre_sp_first_name: Optional[str]
    pre_sp_dob: Optional[date]
    pre_relationship_type: Optional[str]
    pre_start_date: Optional[date]
    pre_end_date: Optional[date]


class Personal(Person):
    used_last_name: Optional[str]
    used_first_name: Optional[str]
    native_last_name: str
    native_first_name: str
    height: int
    eye_color: str
    country_of_birth: str
    place_of_birth: str
    uci: Optional[str]
    citizen2: Optional[str]
    native_language: str
    english_french: str
    which_one_better: Optional[str]
    language_test: bool
    current_occupation: str
    intended_occupation: Optional[str]
    email: EmailStr
    primary_school_years: int
    secondary_school_years: int
    post_secondary_school_years: int
    other_school_years: int
    last_entry_date: Optional[date]
    last_entry_place: Optional[str]
    other_explanation: Optional[str]
    accompany_to_canada: bool
    relationship_to_pa: Optional[str]
    dependant_type: Optional[str]

    _normalize_used_first_name = validator(
        "used_first_name", allow_reuse=True, check_fields=False
    )(normalize)
    _normalize_used_last_name = validator(
        "used_last_name", allow_reuse=True, check_fields=False
    )(normalize)

    @root_validator
    def checkAnswers(cls, values):
        questions = ["english_french"]
        explanations = ["which_one_better"]
        qas = dict(zip(questions, explanations))
        for k, v in qas.items():
            if values.get(k) and values.get(k) == "Both" and not values.get(v):
                raise ValueError(
                    f"Since {k} is true, but you did not answer the question {v} in info-personal sheet"
                )
        return values


class Education(EducationBase):
    city: Optional[str]
    country: Optional[str]


class Family(BaseModel):
    relationship: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    native_last_name: Optional[str]
    native_first_name: Optional[str]
    date_of_birth: Optional[date]
    date_of_death: Optional[date]
    place_of_birth: Optional[str]
    birth_country: Optional[str]
    marital_status: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]


class Travel(BaseModel):
    start_date: date
    end_date: date
    length: int
    destination: str
    purpose: str


class PRBackground(BaseModel):
    q1: bool
    q2: bool
    q3: bool
    q4: bool
    q5: bool
    q6: bool
    q7: bool
    q8: bool
    q9: bool
    q10: bool
    q11: bool
    details: Optional[str]


class History(BaseModel):
    start_date: date
    end_date: Optional[date]
    activity: str
    city_and_country: str
    status: str
    name_of_company_or_school: str
    
    @property
    def __str__(self):
        return "table-history"


class Member(BaseModel):
    start_date: date
    end_date: date
    organization_name: str
    organization_type: str
    position: str
    city: str
    country: str


class Government(BaseModel):
    start_date: date
    end_date: date
    country: str
    department: str
    position: str


class Military(BaseModel):
    start_date: date
    end_date: date
    country: str
    service_detail: str
    rank: str
    combat_detail: Optional[str]
    reason_for_end: Optional[str]


class AddressHistory(BaseModel):
    start_date: date
    end_date: Optional[date]
    street_and_number: str
    city: str
    province: str
    country: str
    post_code: str
    
    @property
    def __str__(self):
        return "table-addresshistory"


class PrModel(CommonModel):
    personal: Personal
    cor: List[COR]
    marriage: Marriage
    address: List[Address]
    phone: List[Phone]
    personid: List[PersonId]
    prcase: PRCase
    family: List[Family]
    travel: List[Travel]
    prbackground: PRBackground
    education: List[Education]
    history: List[History]
    member: List[Member]
    government: List[Government]
    military: List[Military]
    addresshistory: List[AddressHistory]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None,check=True):
        if output_excel_file:
            excels=self.getExcels(['excel/pr.xlsx','excel/pa.xlsx'])
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())
        if check: [self.check(item,excels[0]) for item in [self.history,self.addresshistory]]
    
    def check(self,items:List[object],excel_file):
        results=[]
        # construct list suitable for checkContinuity
        for item in items:
            results.append(list(item.__dict__.values()))
        
        # check 
        continued, sorted_list,msg=checkContinuity(results)
        
        if not continued:
            print(colored(f"There are {len(msg)} error(s) in sheet {items[0].__str__}","red"))
            [print(index,"\t",m) for index,m in enumerate(msg)]
