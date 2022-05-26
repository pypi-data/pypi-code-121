
from pydantic import BaseModel
from typing import Optional,List

class Address(BaseModel):
    variable_type:str    # this is the identifier variable 
    display_type: str # actually it is the prompt information
    po_box:Optional[str]
    unit:Optional[str]
    street_number:Optional[str]
    street_name:Optional[str]
    district:Optional[str]
    city:Optional[str]
    province:Optional[str]
    country:Optional[str]
    post_code:Optional[str]
    
    @property
    def full_address(self):
        fa=self.po_box+' ' if self.po_box else ''
        fa+=self.unit+' ' if self.unit else ''
        fa+=self.street_number+" " if self.street_number else ""
        fa+=self.street_name
        fa+=", "+self.district+', ' if self.district else ""
        fa+=self.city+', '+self.province+', '+self.country+' '+self.post_code
        return fa
    
    @property
    def line1(self):
        l1=self.po_box+' ' if self.po_box else ''
        l1+=self.unit+' ' if self.unit else ''
        l1+=self.street_number+" " if self.street_number else ""
        l1+=self.street_name
        l1+=", "+self.district+', ' if self.district else ""
        return l1

    @property
    def line2(self):
        l2=self.city+', '+self.province+', '+self.country+' '+self.post_code
        return l2
    
    @property
    def street_address(self):
        l1=self.street_number+" " if self.street_number else ""
        l1+=self.street_name if self.street_name else ""
        l1+=", "+self.district+', ' if self.district else ""
        return l1
        
    def __eq__(self,another):
        for k,v in self.__dict__.items():
            if k not in ['variable_type','display_type'] and v != getattr(another,k,None):
                return False
        return True
        
    def __str__(self):
        return self.full_address


class Addresses(object):
    def __init__(self, address_list: List[Address]) -> None:
        self.addresses=address_list
    
    def _specific_address(self,v_type):
        address=[address for address in self.addresses if address.variable_type==v_type]
        return address[0] if address else None
    
    @property
    def mailing(self):
        return self._specific_address('mailing_address')
    
    @property
    def residential(self):
        return self._specific_address('residential_address')
    
    @property
    def business(self):
        return self._specific_address('business_address')
    
    # return the first work location
    @property
    def working(self):
        return self._specific_address('working_address')
    
    # return all work locations
    @property
    def workings(self):
        return [address for address in self.addresses if address.variable_type=='working_address']

    @property
    def PreferredAddress(self):
        for addr_type in ['business_address','residential_address','mailing_address','working_address']:
            addr=self._specific_address(addr_type)
            if addr: return addr 
    
    def getPreferredAddressFromList(self,type_list):
        for addr_type in type_list:
            addr=self._specific_address(addr_type)
            if addr: return addr
    
    

