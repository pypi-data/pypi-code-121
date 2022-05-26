from termcolor import colored
from pydantic import BaseModel
from functools import reduce
from typing import List,Optional
from model.common.address import Address
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from utils.utils import checkContinuity
from datetime import date
from pprint import pprint

class Family(BaseModel):
    last_name:str
    first_name:str	
    native_last_name:Optional[str]	
    native_first_name:Optional[str] 
    date_of_birth:date  
    date_of_death:Optional[date]
    place_of_birth:str
    birth_country:str 
    relationship:str
    
class Personal(BaseModel):
    last_name:str
    first_name:str
    native_last_name:str
    native_first_name:str
    dob:date	

class PRBackground(BaseModel):
    q1:bool
    q2:bool
    q3:bool
    q4:bool
    q5:bool
    q6:bool
    q7:bool
    q8:bool
    q9:bool
    q10:bool
    q11:bool
    details:Optional[str]

class Education(BaseModel):
    start_date:Optional[date]
    end_date:Optional[date]
    school_name:Optional[str]
    city:Optional[str]
    country:Optional[str]
    education_level:Optional[str]	
    field_of_study:Optional[str]

class History(BaseModel):
    start_date:date
    end_date:Optional[date]
    activity:str	
    city_and_country:str	
    status:str	
    name_of_company_or_school:str
    
    @property
    def __str__(self) -> str:
        return "table-history"

class Member(BaseModel):
    start_date:date	
    end_date:date	
    organization_name:str	
    organization_type:str	
    position:str	
    city:str	
    country:str

class Government(BaseModel):
    start_date:date	
    end_date:date	
    country:str	
    department:str	
    position:str

class Military(BaseModel):
    start_date:date	
    end_date:date
    country:str	
    service_detail:str	
    rank:str	
    combat_detail:Optional[str]	
    reason_for_end:Optional[str]

class AddressHistory(BaseModel):
    start_date:date	
    end_date:Optional[date]	
    street_and_number:str	
    city:str	
    province:str	
    country:str	
    post_code:str    
    
    @property
    def __str__(self) -> str:
        return "table-addresshistory"
    
class M5669Model(CommonModel):
    personal:Personal
    family:List[Family]
    prbackground:PRBackground
    education:List[Education]
    history:List[History]
    member:List[Member]
    government:List[Government]
    military:List[Military]
    addresshistory:List[AddressHistory]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None,check=False):
        if output_excel_file:
            excels=self.getExcels(["excel/pr.xlsx","excel/pa.xlsx"])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        
        super().__init__(excels,output_excel_file,globals())
        
        if check: [self.check(item) for item in [self.history,self.addresshistory]]
    
    def check(self,items:List[object]):
        results=[]
        # construct list suitable for checkContinuity
        for item in items:
            results.append(list(item.__dict__.values()))
        
        # check 
        continued, sorted_list,msg=checkContinuity(results)
        
        if not continued:
            print(colored(f"There are {len(msg)} error(s) in sheet {items[0].__str__}","red"))
            [print(index,"\t",m) for index,m in enumerate(msg)]
    