from pydantic import validator,EmailStr
from typing import Optional,List
from model.common.employerbase import EmployerBase
from model.common.jobofferbase import JobofferBase
from model.common.address import Address,Addresses
from model.common.utils import makeList


class General(EmployerBase):
    company_intro:str
    business_intro:str
    recruit_email:EmailStr
        
class JobOffer(JobofferBase):
    # education_level:Optional[str]
    disability_insurance:bool
    dental_insurance:bool
    empolyer_provided_persion:bool
    extended_medical_insurance:bool
    extra_benefits:Optional[str]
    duties_brief:str
    duties:list
    specific_edu_requirement:str
    skill_experience_requirement:str
    other_requirements:Optional[list]

    _str2bool_duties=validator('duties',allow_reuse=True,pre=True)(makeList)
    _str2bool_other_requirements=validator('other_requirements',allow_reuse=True,pre=True)(makeList)
    
    @property
    def benefits(self):
        bs=[]
        if self.disability_insurance:bs.append('Disability insurance')
        if self.dental_insurance:bs.append('Dental insurance')
        if self.empolyer_provided_persion:bs.append('Employer provided persion')
        if self.extended_medical_insurance:bs.append('Extended medical insurance')
        if self.extra_benefits: bs.append(self.extra_benefits)
        return ', '.join(bs)

class ErAddress(Address):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
class ErAddresses(Addresses):
    def __init__(self, address_list: List[Address]) -> None:
        super().__init__(address_list)

    




