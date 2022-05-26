from pydantic import BaseModel,validator
from typing import Optional
from datetime import date,timedelta
from pydantic.class_validators import root_validator
    
class JobofferBase(BaseModel):
    job_title:str
    noc:str
    hours:float
    wage_unit:str
    wage_rate:float
    ot_ratio:float
    permanent:bool
    work_start_date:Optional[date]
    job_duration:Optional[float]
    job_duration_unit:Optional[str]
    
    @root_validator
    def checkDuration(cls,values):
        if not values.get('permanent') and (not values.get('job_duration') or not values.get('job_duration_unit')):
                raise ValueError("Since it is not permanent job offer, so you have to specify the job duration and job duration unit in info-joboffer sheet")
        return values
    
    @property
    def term(self):
        if self.permanent:
            return "Permanent"
        else:
            if not self.job_duration or not self.job_duration_unit:
                raise ValueError('Since you claimed the job offer is not permanent, you must spcify the job duration and duration unit')
            return str(self.job_duration)+" "+self.job_duration_unit
    
    @property
    def full_part_time(self):
        return "full-time" if self.hours>=30 else 'part-time'
    
    @property
    def salary(self):
        return '{:,.1f}'.format(self.wage_rate) 
    
    @property
    def weekly_hours(self):
        return '{:,.1f}'.format(self.hours)
    
    @property    
    def hourly_rate(self):
        rate=0
        match self.wage_unit:
            case 'annually':
                rate=self.wage_rate/52/self.hours
            case 'monthly':
                rate= self.wage_rate*12/52/self.hours
            case 'weekly':
                rate= self.wage_rate/self.hours
            case 'hourly':
                rate= self.wage_rate
        return '{0:.4g}'.format(rate)

    @property    
    def hourly_rate_say(self):
        return f'${self.hourly_rate} per hour'
    
    @property    
    def overtime_rate(self):
        return float(self.hourly_rate)*self.ot_ratio
    
    @property
    def overtime_rate_say(self):
        return '${rate:,.0f} per hour'.format(rate=float(self.overtime_rate))
    
    @property
    def weekly_rate(self):
        rate=0
        match self.wage_unit:
            case 'annually':
                rate=self.wage_rate/52
            case 'monthly':
                rate= self.wage_rate*12/52
            case 'weekly':
                rate= self.wage_rate
            case 'hourly':
                rate= self.wage_rate*self.hours
        return '{0:.0f}'.format(rate)
    
    @property
    def weekly_rate_say(self):
        return '${rate:,.0f} per week'.format(rate=float(self.weekly_rate))
    
    @property
    def monthly_rate(self):
        rate=0
        match self.wage_unit:
            case 'annually':
                rate=self.wage_rate/12
            case 'monthly':
                rate= self.wage_rate
            case 'weekly':
                rate= self.wage_rate*52/12
            case 'hourly':
                rate= self.wage_rate*self.hours*52/12
        return '{0:.0f}'.format(rate)
    
    @property    
    def monthly_rate_say(self):
        return '${rate:,.0f} per month'.format(rate=float(self.monthly_rate))
    
    @property
    def annual_rate(self):
        rate=0
        match self.wage_unit:
            case 'annually':
                rate=self.wage_rate
            case 'monthly':
                rate= self.wage_rate*12
            case 'weekly':
                rate= self.wage_rate*52
            case 'hourly':
                rate= self.wage_rate*self.hours*52
        return '{0:.0f}'.format(rate)
    
    @property    
    def annual_rate_say(self):
        return '${rate:,.0f} per year'.format(rate=float(self.annual_rate))
    
    @property
    def requirements(self):
        reqs=[self.specific_edu_requirement,self.skill_experience_requirement,*self.other_requirements]
        return [req for req in reqs if req]

    # work start date + days (base on job_duration and job_duration_unit)
    @property
    def work_end_date(self):
        days=0
        
        match self.job_duration_unit:
            case "day":
                return self.work_start_date+timedelta(days=int(self.job_duration))
            case "week":
                return self.work_start_date+timedelta(weeks=int(self.job_duration))
            case "month":
                return self.work_start_date+timedelta(days=int(self.job_duration*30))
            case "year":
                return self.work_start_date+timedelta(days=int(self.job_duration*365))

            
        