from pydantic import BaseModel, EmailStr
from typing import Optional,List
from datetime import date

from model.common.commonmodel import CommonModel

class Family(BaseModel):
    relationship:Optional[str]
    last_name:Optional[str]	
    first_name:Optional[str]	
    native_last_name:Optional[str]	
    native_first_name:Optional[str]
    date_of_birth:Optional[date]	
    date_of_death:Optional[date]
    place_of_birth:Optional[str]
    birth_country:Optional[str]	
    marital_status:Optional[str]	
    email:Optional[EmailStr]	
    address:Optional[str]

class M5406Model(CommonModel):
    family:List[Family]
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/pa.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        super().__init__(excels,output_excel_file,globals())