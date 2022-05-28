from pydantic import BaseModel, EmailError, EmailStr,validator
from model.common.utils import Duration
from datetime import date
from typing import Optional,List
from model.common.mixins import DurationMixin

class Advertisement(BaseModel,DurationMixin):
    method:str
    media:str
    website:str
    advertisement_id:Optional[str]
    start_date:date	
    end_date:date
    
    @property
    def days(self):
        return Duration(self.start_date,date.today()).days
    
    def daysOnDate(self,end_date=date.today()):
        return Duration(self.start_date,end_date).daysOnDate(end_date)
    
    @validator("end_date")
    def endDateBigger(cls,end_date,values):
        start_date=values.get('start_date')
        the_date=end_date if end_date else date.today()
        if (the_date-start_date).days<=0:
            raise ValueError(f'End date {the_date} is earlier than start date {start_date}')
        end_date=end_date if end_date else "Present"
        return end_date
    

class Advertisements():
    def __init__(self,advertisments:List[Advertisement]):
        self.advertisements=advertisments
        
    @property
    def amount(self):
        return len(self.advertisements)
    
    @property
    def earliest(self):
        return min([ day.start_date for day in self.advertisements])
    
    @property
    def latest(self):
        return max([ day.start_date for day in self.advertisements])
    
    
    @property
    def earliest_say(self):
        return self.earliest.strftime("%b %d, %Y")
    
    @property
    def min_days(self):
        return (date.today()-self.latest).days
    
    @property
    def max_days(self):
        return (date.today()-self.earliest).days
    
    @property
    def summary(self):
        medias=[ adv.media for adv in self.advertisements]
        return (f"""We posted {self.amount} job advertisements on {', '.join(medias[:-1])+", and "+medias[-1]} since {self.earliest_say} for at least {self.min_days} days.""")
        
class InterviewRecord(BaseModel):
    candidate:str
    canadian_status:str
    interviewed:Optional[bool]
    record:str
    offered:Optional[bool]
    accepted:Optional[bool]
    
    @property
    def is_interviewed(self):
        return "Yes" if self.interviewed else "No"
    
    @property
    def is_offered(self):
        return "Yes" if self.offered else "No"
    
    @property
    def is_accepted(self):
        return "Yes" if self.accepted else "No"
    
    @property
    def is_canadian(self):
        return True if self.canadian_status.upper()=="CITIZEN" or  self.canadian_status.upper()=="PR" else False
    
    @property
    def is_unknown(self):
        return True if self.canadian_status.upper()=="UNKNOWN"  else False
    
    @property
    def is_foreigner(self):
        return True if self.canadian_status.upper()=="FOREIGNER"  else False

class InterviewRecords():
    def __init__(self,interview_records:List[InterviewRecord]):
        self.interview_records=interview_records
        
    @property
    def resume_num(self):
        return len(self.interview_records)
    
    @property
    def canadian_num(self):
        return len([record for record in self.interview_records if record.is_canadian])
    
    @property
    def unknown_num(self):
        return len([record for record in self.interview_records if record.is_unknown])
    
    @property
    def foreigner_num(self):
        return len([record for record in self.interview_records if record.is_foreigner])
    
    @property
    def total_canadian(self):
        return self.unknown_num+self.canadian_num
    
    @property
    def total_interviewed_canadians(self):
        return len([ applicant for applicant in self.interview_records if applicant.interviewed==True])
    
    @property
    def canadian_records(self):
        records=[]
        i=1
        for applicant in self.interview_records:
            if applicant.is_canadian or applicant.is_unknown:
                records.append({**{'no':i},**applicant.dict()})
                i+=1
        return records
    
    @property
    def summary(self):
        return (f"""Totally, we have received {self.resume_num} resumes consisting of {self.canadian_num } Canadian(s), {self.unknown_num } Unknown status, and {self.foreigner_num } foreign national(s) (who claimed their nationality, work permit, or study permit holder or visitors) during the first screening. We assume that all candidates with unknown status are also Canadians, so there are {self.total_canadian } Canadian(s), among which {self.total_interviewed_canadians} were reached out for interview.""")
    
class RecruitmentSummary(BaseModel):
    apply_email:EmailStr
    referral:Optional[str]
    reply2apply:bool
    emails_for_making_interview:bool
    interview_date:date
    interview_way:str
    interviewer_name:str
    interviewer_position:str
    interview_record:bool
    interview_process_evidence:bool
    emails_for_certificates:bool
    emais_for_references:bool
    reference_checked:bool
    reference_check_evidence:bool
    joboffer_email:bool
    joboffer_email_reply:bool
    after_offer_coomunication:bool
    reasons_not_hire_canadians:str

