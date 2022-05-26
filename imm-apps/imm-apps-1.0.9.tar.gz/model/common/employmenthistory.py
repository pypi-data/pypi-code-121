from pydantic import BaseModel,validator
from datetime import date,timedelta
from typing import Optional,List
from model.common.mixins import DurationMixin
from model.common.utils import makeList,Duration
from dateutil.parser import parse,ParserError
from model.common.employmentbase import EmploymentBase

class EmploymentHistory():
    def __init__(self,employment_list: List[EmploymentBase]):
        self.employment_list=employment_list
        for emp in employment_list:
            if not isinstance(emp,EmploymentBase):
                raise ValueError(f'{employment_list} is not a list of EmploymentBase objects')

    @property    
    def initial_start_date(self):
        return min([ emp.start_date for emp in self.employment_list])
    
    @property    
    def final_end_date(self):
        end_dates=[]
        for emp in self.employment_list:
            if emp.is_current: return "Present"
            end_dates.append(emp.end_date)
        return max(end_dates)
    
    @property
    def position_number(self):
        return len(set([emp.job_title for emp in self.employment_list]))
    
    @property
    def position_number_say(self):
        number= len(set([emp.job_title for emp in self.employment_list]))
        return str(number)+" position" if number<=1 else str(number)+" positions"
    
    def qualified_employment(self,program):
        return [job for job in self.employment_list if getattr(job,program)]

    