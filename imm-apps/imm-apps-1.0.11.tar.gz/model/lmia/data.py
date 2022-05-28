from ast import Str
from pydantic import BaseModel,validator,EmailStr
from datetime import date
from typing import Optional,List,Union
from model.common.employerbase import EmployerBase
from model.common.jobofferbase import JobofferBase
from model.common.contact import ContactBase
from pydantic.class_validators import root_validator

from model.common.utils import Duration


# employer classes
class General(EmployerBase):
    company_intro:str
    business_intro:str
    recruit_email:EmailStr

class Contact(ContactBase):
    position:Optional[str]
    
#personal classes
class JobOffer(JobofferBase):
    offer_date:date

    @property
    def date_of_offer(self):
        return self.offer_date.strftime("%b %d, %Y")
    
    @property
    def requirements(self):
        return [r for r in [self.specific_edu_requirement,self.skill_experience_requirement,*self.other_requirements] if r is not None]

class PersonalAssess(BaseModel):
    work_experience_brief:str
    education_brief:str
    competency_brief:str
    language_brief:Optional[str]
    performance_remark:Optional[str]
    
    @property
    def why_qualified(self):
        qualifications=[self.work_experience_brief,self.education_brief,self.competency_brief,self.language_brief,self.performance_remark]
        return [q for q in qualifications if q is not None]

# lmia classes    
class LmiaCase(BaseModel):
    purpose_of_lmia:str
    stream_of_lmia:str
    number_of_tfw:int
    area_median_wage:float
    provincial_median_wage:float
    duration_number:int
    duration_unit:str
    duration_reason:str
    has_attestation:bool
    
    @property
    def purpose_say(self):
        return self.purpose_of_lmia
    
    @property
    def stream_say(self):
        return self.stream_of_lmia
    
    @property
    def duration_say(self):
        return str(self.duration_number)+" "+self.duration_unit+"s" if self.duration_number>1 else str(self.duration_number)+" "+self.duration_unit
    
    @property
    def stars(self):
        return 2 if self.stream_of_lmia.lower() in ['low wage stream','lws'] else 4

class Finance(BaseModel):
    year:int
    revenue:float
    net_income:float
    retained_earning:float
    
    @property
    def formatted_revenue(self):
        return '{:,.0f}'.format(self.revenue)
    
    @property
    def formatted_net_income(self):
        return '{:,.0f}'.format(self.net_income)
    
    @property
    def formatted_retained_earning(self):
        return '{:,.0f}'.format(self.retained_earning)
    
        
class Lmi(BaseModel):
    brief_benefit:str
    job_creation_benefit:Optional[str]
    skill_transfer_benefit:Optional[str]
    fill_shortage_benefit:Optional[str]
    other_benefit:Optional[str]

    @property
    def benefits(self):
        return [b for b in [self.job_creation_benefit,self.skill_transfer_benefit,self.fill_shortage_benefit,self.other_benefit] if b is not None]

# RCIC
class Rcic(BaseModel):
    first_name:str
    last_name:str
    sex:str
    rcic_number:str
    company:str
    
    @property
    def name(self):
        return self.first_name+' '+self.last_name
        
    
class Emp5593(BaseModel):
    pass

class Emp5626(BaseModel):
    is_seasonal:bool
    start_month:Optional[str]
    end_month:Optional[str]
    last_canadian_number:Optional[int]
    last_tfw_number:Optional[int]
    current_canadian_number:int
    current_tfw_number:int
    tp_waivable:bool
    waive_creteria:Optional[str]
    has_finished_tp:bool
    finished_tp_result:Optional[str]
    activity1_title:Optional[str]
    activity1_decription:Optional[str]
    activity1_outcome:Optional[str]
    activity1_commnet:Optional[str]
    activity2_title:Optional[str]
    activity2_decription:Optional[str]
    activity2_outcome:Optional[str]
    activity2_commnet:Optional[str]
    activity3_title:Optional[str]
    activity3_decription:Optional[str]
    activity3_outcome:Optional[str]
    activity3_commnet:Optional[str]
    activity4_title:Optional[str]
    activity4_decription:Optional[str]
    activity4_outcome:Optional[str]
    activity4_commnet:Optional[str]
    activity5_title:Optional[str]
    activity5_decription:Optional[str]
    activity5_outcome:Optional[str]
    activity5_commnet:Optional[str]

class Emp5627(BaseModel):
    provide_accommodation:bool
    description:Optional[str]
    rent_unit:str
    rent_amount:float
    accommodation_type:str
    explain:Optional[str]
    bedrooms:int
    people:int
    bathrooms:int
    other:Optional[str]
