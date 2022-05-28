from typing import List,Optional,Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.id import ID
from datetime import date
from pydantic import BaseModel, EmailStr,root_validator,validator
from model.common.utils import normalize

class PersonId(ID):
    pass

class PRCase(BaseModel):
    imm_program:str
    imm_category:str
    imm_under:Optional[str]
    communication_language:str
    interview_language:str
    need_translator:bool
    intended_province:str
    intended_city:str

class COR(BaseModel):
    start_date:date
    end_date:Union[date,None]
    country:str
    status:str
    
    def is_current(self):
        return not self.end_date

class Marriage(BaseModel):
    marital_status:str
    married_date:Optional[date]
    sp_last_name:Optional[str]
    sp_first_name:Optional[str]
    previous_married:bool
    pre_sp_last_name:Optional[str]
    pre_sp_first_name:Optional[str]
    pre_sp_dob:Optional[date]
    pre_relationship_type:Optional[str]
    pre_start_date:Optional[date]
    pre_end_date:Optional[date]

class Personal(BaseModel):
    last_name:str
    first_name:str
    used_last_name:Optional[str]
    used_first_name:Optional[str]
    sex:str
    height:int
    eye_color:str
    dob:date
    country_of_birth:str
    place_of_birth:str
    uci:Optional[str]
    citizen:str
    citizen2:Optional[str]
    native_language:str
    english_french:str
    which_one_better:Optional[str]
    language_test:bool
    current_occupation:str
    intended_occupation:Optional[str]
    email:EmailStr
    
    _normalize_used_first_name=validator('used_first_name',allow_reuse=True,check_fields=False)(normalize)
    _normalize_used_last_name=validator('used_last_name',allow_reuse=True,check_fields=False)(normalize)
    
    @root_validator
    def checkAnswers(cls,values):
        questions=['english_french']
        explanations=['which_one_better']
        qas=dict(zip(questions,explanations))
        for k,v in qas.items():  
            if values.get(k) and values.get(k)=="Both" and not values.get(v):
                    raise ValueError(f"Since {k} is true, but you did not answer the question {v} in info-personal sheet")
        return values

class Education(EducationBase):
    pass

class M0008Model(CommonModel):
    personal:Personal
    cor:List[COR]
    marriage:Marriage
    address:List[Address]
    phone:List[Phone]
    personid:List[PersonId]
    education:List[Education]
    prcase:PRCase
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(["excel/pr.xlsx",'excel/pa.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        super().__init__(excels,output_excel_file,globals())