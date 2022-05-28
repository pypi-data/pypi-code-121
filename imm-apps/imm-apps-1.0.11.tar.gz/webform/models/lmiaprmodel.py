from typing import List, Optional, Union
from model.common.address import Address
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from datetime import date
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.prportal.data.country_residence import country_residence

class General(BaseModel):
    legal_name:str
    operating_name:Optional[str]
    website:Optional[str]
    recruit_email:EmailStr
    company_intro:str
    business_intro:str


class LMIAPrModel(CommonModel):
    general:General
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/er.xlsx','excel/pa.xlsx'])
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())

class LMIAHWSModel(CommonModel):
    pass
