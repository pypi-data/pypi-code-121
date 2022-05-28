from pydantic import BaseModel,validator
from datetime import date,timedelta
from typing import Optional,List
from model.common.mixins import DurationMixin
from model.common.utils import makeList,Duration
from dateutil.parser import parse,ParserError

class EmploymentBase(BaseModel,DurationMixin):
    start_date:date
    end_date:Optional[date]
    job_title:str
    noc_code:str
    weekly_hours:float
    company:str
    city:str
    province:str
    country:str

    @validator("end_date")
    def endDateBigger(cls,end_date,values):
        start_date=values.get('start_date')
        the_date=end_date if end_date else date.today()
        if (the_date-start_date).days<=0:
            raise ValueError(f'End date {the_date} is earlier than start date {start_date}')
        end_date=end_date if end_date else "Present"
        return end_date
    
    @property
    def part_time(self):
        return "Part time" if self.weekly_hours<30 else ""
    
    @property
    def is_current(self):
        return True if self.end_date=='Present' else False

    @property
    def years(self):
        return Duration(self.start_date,self.end_date).years
    
    @property
    def months(self):
        return Duration(self.start_date,self.end_date).years
    
    def yearsOnDate(self,end_date):
        return Duration(self.start_date,self.end_date).yearsOnDate(end_date)
    
    def monthsOnDate(self,end_date):
        return Duration(self.start_date,self.end_date).monthsOnDate(end_date)
    
    @property
    def start_date_mmyyyy(self):
        return self.start_date.strftime('%b %Y')

    @property
    def end_date_mmyyyy(self):
        return self.end_date.strftime('%b %Y') if self.end_date else "Present"

    @property
    def is_present(self):
        return not self.end_date or self.end_date=="Present"
