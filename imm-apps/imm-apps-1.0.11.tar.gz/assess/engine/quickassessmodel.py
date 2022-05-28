from .context import BASEDIR
from model.common.commonmodel import CommonModel
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, Union, List
import os


class Facts(BaseModel):
    dob: date
    # asset
    liquid_assets: Optional[float]
    net_worth: Optional[float]
    
    #language
    reading: Optional[Union[int, float]]
    writting: Optional[Union[int, float]]
    speaking: Optional[Union[int, float]]
    listening: Optional[Union[int, float]]
    test_format: Optional[str]
    
    #work experience
    start_date: date
    end_date: date
    work_noc: str
    term: str = "Fulltime"
    work_country: str = "Other"
    job_title: str
    work_province: str = "Other"
    share_percentage: float = 0
    
    # edu
    level: str = "Bachelor"
    edu_country: str = "Other"
    edu_province: str = "Other"
    graduate_date: date

    # relative
    relative_dob: Optional[date]
    relative_province: Optional[str]
    canada_status: Optional[str]
    relationship: Optional[str]
    
    # job offer
    job_offer:bool
    joboffer_noc:Optional[str]
    joboffer_province:Optional[str]


class QuickAssessModel(CommonModel):
    facts: Facts

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(["excel/quickassess.xlsx"])
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    'You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels, output_excel_file, globals())
