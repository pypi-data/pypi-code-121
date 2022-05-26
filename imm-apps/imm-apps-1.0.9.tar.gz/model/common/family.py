from pydantic import BaseModel
from typing import List,Optional
from datetime import date

class FamilyBase(BaseModel):
    last_name:str
    first_name:str	
    native_last_name:Optional[str]	
    native_first_name:Optional[str] 
    date_of_birth:date  
    date_of_death:Optional[date]
    place_of_birth:str
    birth_country:str 
    relationship:str
    

class FamilyMembers():
    
    def __init__(self,members:List[FamilyBase]):
        self.members=members
        
    @property
    def spouse(self):
        s=[ s for s in self.members if s.relationship=='Spouse']
        return s[0] if len(s)==1 else None
    
    @property
    def siblings(self):
        s=[ s for s in self.members if s.relationship in ['Brother','Sister']]
        return s
    
    @property
    def dependants(self):
        s=[ s for s in self.members if s.relationship in ['Son','Daughter']]
        return s
    
    @property
    def father(self):
        s=[ s for s in self.members if s.relationship == 'Father']
        return s[0] if len(s)==1 else None
    
    @property
    def mother(self):
        s=[ s for s in self.members if s.relationship == 'Mother']
        return s[0] if len(s)==1 else None
    
    @property
    def parents(self):
        s=[ s for s in self.members if s.relationship in  ['Father','Mother']]
        return s

