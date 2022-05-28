from pydantic import BaseModel,EmailStr,validator
from typing import Optional
from model.common.utils import normalize,trimString
from datetime import date,datetime
from dateutil.parser import parse,ParserError

    
class Person(BaseModel):
    last_name:str
    first_name:str
    sex:str
    dob:date
    citizen:str
    
    _normalize_first_name=validator('first_name',allow_reuse=True,check_fields=False)(normalize)
    _normalize_last_name=validator('last_name',allow_reuse=True,check_fields=False)(normalize)
    
    @property
    def full_name(self):
        return self.first_name+" "+self.last_name

    @property
    def age(self):
        the_day= date.today()
        try:
            return the_day.year - self.dob.year - ((the_day.month, the_day.day) < (self.dob.month, self.dob.day))
        except (ValueError,TypeError,ParserError) as err:
            print(err.args[0]," in file ",__file__)
    
    def ageOnDate(self,the_day= date.today()):
        if not isinstance(the_day,date):
            try:
                the_day=datetime.strptime(the_day,"%Y-%m-%d")
                return the_day.year - self.dob.year - ((the_day.month, the_day.day) < (self.dob.month, self.dob.day))
            except (ValueError,TypeError) as err:
                print(err.args[0]," in file ",__file__)
    
    # Third person subject 
    @property
    def subject(self):
        return "he" if self.sex.upper()=='M' or self.sex.upper()=="MALE" else 'she'
    
    # Third person object
    @property
    def object(self):
        return "him" if self.sex.upper()=='M' or self.sex.upper()=="MALE" else 'her'

    # third person attributive
    @property
    def attributive(self):
        return "his" if self.sex.upper()=='M' or self.sex.upper()=="MALE" else 'her'
    
    # salutation
    @property
    def salutation(self):
        return "Mr." if self.sex.upper()=='M' or self.sex.upper()=="MALE" else 'Ms.'
    
    @property
    def short_name(self):
        return self.salutation+' '+self.last_name

class PersonalAssess(BaseModel):
    work_experience_brief:str
    education_brief:str
    competency_brief:str
    language_brief:Optional[str]
    performance_remark:Optional[str]
    
    @property
    def why_qualified(self):
        qualifications=[self.work_experience_brief,self.education_brief,self.competency_brief,self.language_brief,self.performance_remark]
        return [q for q in qualifications if q is not None]
    
    @property
    def why_qualified_say(self):
        return ' '.join(self.why_qualified)

def main():
    p1={
        'first_name':'jacky',
        'last_name':"zhang",
        'dob':"1969-02-11",
        'sex':"Male",
        'citizen':"China"
    }
    jacky=Person(**p1)
    print(jacky.full_name,jacky.age,jacky.ageOnDate('2056-02-11'))

if __name__=="__main__":
    main()
    