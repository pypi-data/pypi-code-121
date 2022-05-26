from pydantic import BaseModel,validator,EmailStr
from datetime import date
from typing import Optional,List
from model.common.employerbase import EmployerBase
from model.common.jobofferbase import JobofferBase
from model.common.address import Address,Addresses
from model.common.utils import makeList
from pydantic.class_validators import root_validator

class ErAddress(Address):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
class ErAddresses(Addresses):
    def __init__(self, address_list: List[Address]) -> None:
        super().__init__(address_list)
    

class General(EmployerBase):
    company_intro:str
    business_intro:str
    recruit_email:EmailStr
        
class JobOffer(JobofferBase):
    offer_date:date
    supervisor_name:Optional[str]
    supervisor_title:Optional[str]
    vacation_pay_weeks:int
    vacation_pay_percentage:float
    employer_rep:str
    employer_rep_title:str
    payment_way:str
    has_probation:bool
    probation_duration:Optional[int]
    duties_brief:str
    duties:list

    _str2bool_duties=validator('duties',allow_reuse=True,pre=True)(makeList)

    
    
    @root_validator
    def checkProbation(cls,values):
        if values.get('has_probation') and not values.get('probation_duration'):
                raise ValueError("Since it is has probation period, but you did not specify the probation duration in info-joboffer sheet")
        return values
    
    @property
    def date_of_offer(self):
        return self.offer_date.strftime("%b %d, %Y")
    
    @property
    def vacation_pay_percent(self):
        return '{:,.1f}%'.format(self.vacation_pay_percentage*100)
    