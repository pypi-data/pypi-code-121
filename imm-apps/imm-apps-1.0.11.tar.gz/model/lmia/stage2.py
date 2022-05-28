from datetime import date
from typing import Optional,List
from pydantic import BaseModel
from model.common.commonmodel import CommonModel
import os


class Joboffer(BaseModel):
    has_probation:bool
    probation_duration:int
    disability_insurance:bool
    dental_insurance:bool
    empolyer_provided_persion:bool
    extended_medical_insurance:bool
    extra_benefits:str
    supervisor_name:str
    supervisor_title:str
    employer_rep:str
    employer_rep_title:str
    vacation_pay_weeks:int
    vacation_pay_percentage:float
    english_french:bool
    oral:bool
    writing:bool
    reason_for_no:str
    other_language_required:bool
    reason_for_other:Optional[str]
    skill_experience_requirement:Optional[str]
    other_requirements:Optional[str]

    
class Employee_list(BaseModel):
    employee:str
    job_title:str
    wage:float
    hours_per_week:float
    immigration_status:str	
    employment_start_date:date
    remark:str

class Lmi(BaseModel):
    laid_off_in_12:bool
    laid_off_canadians:Optional[int]
    laid_off_tfw:Optional[int]
    laid_off_reason:Optional[str]
    is_work_sharing:bool
    work_sharing_info:Optional[str]
    labour_dispute:bool
    labour_dispute_info:Optional[str]
    
class LmiaAssess(CommonModel):
    general:General
    employee_list:List[Employee_list]
    lmi:Lmi
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/er.xlsx','excel/lmia.xlsx'])
            
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())

