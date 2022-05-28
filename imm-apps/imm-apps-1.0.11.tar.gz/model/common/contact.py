from pydantic import BaseModel,EmailStr
from typing import Optional,List
from collections import namedtuple
from model.common.mixins import EqMixin

class ContactBase(BaseModel):
    contact_variable:Optional[str]
    contact_type:Optional[str]
    last_name:Optional[str]
    first_name:Optional[str]
    phone:Optional[str]
    email:Optional[EmailStr]

    class Config:
        anystr_lower=True 

class Contacts(object):
    def __init__(self, contacts: List[ContactBase]):
        self.contacts=contacts
    
    def _specific_contact(self,v_type):
        contact=[contact for contact in self.contacts if contact.contact_variable==v_type]
        return contact[0] if contact else None
    
    @property
    def primary(self):
        return self._specific_contact('primary')
    
    @property
    def second(self):
        return self._specific_contact('second')
    
    @property
    def preferredContact(self):
        for contact_type in ['primary','second']:
            contact=self._specific_contact(contact_type)
            if contact: return contact
    

