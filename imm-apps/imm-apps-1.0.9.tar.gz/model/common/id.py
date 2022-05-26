from datetime import date
from pydantic import BaseModel,validator
from dateutil.parser import parse,ParserError
from typing import List,Optional


class ID(BaseModel):
    variable_type:Optional[str]
    display_type:Optional[str]
    number:Optional[str]
    country:Optional[str]
    issue_date:Optional[date]
    expiry_date:Optional[date]

    @property
    def is_expired(self):
        return True if self.expiry_date and date.today()>=self.expiry_date else False
    
    def will_be_expired(self,the_day=date.today()):
        try:
            the_day=the_day if isinstance(the_day,date) else parse(the_day)
        except ParserError as err:
            raise ParserError(f'{err.args[0]}," in file ",{__file__}')
        return True if self.expiry_date and the_day>=self.expiry_date else False
    
    @validator("expiry_date")
    def endDateBigger(cls,expiry_date,values):
        start_date=values.get('issue_date')
        if not start_date: return expiry_date
        the_date=expiry_date or date.today()
        if (the_date-start_date).days<=0:
            raise ValueError(f'Expiry date {the_date} is earlier than issue date {start_date} for the ID')
        expiry_date=expiry_date if expiry_date else "Present"
        return expiry_date
    

class IDs():
    def __init__(self,ids:List[ID]) -> None:
        self.ids=ids
    
    @property
    def passport(self):
        passport=[ id for id in self.ids if id.variable_type.lower()=='passport']
        return passport and passport[0]
    
    @property
    def national_id(self):
        national_id=[ id for id in self.ids if id.variable_type.lower()=='id']
        return national_id and national_id[0]
    
    @property
    def pr(self):
        pr=[ id for id in self.ids if id.variable_type.lower()=='pr']
        return pr and pr[0]
    
    