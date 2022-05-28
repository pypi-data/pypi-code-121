from turtle import position
from typing import List
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Contact, General
from model.common.person import Person
from model.common.contact import Contacts
from datetime import date
import os
from model.common.xmlfiller import XmlFiller


class Personal(Person):
    def __str__(self):
        return self.full_name
        
class RepFormModel(CommonModel):
    general:General
    contact:List[Contact]
    personal:Personal

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/er.xlsx','excel/pa.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())
    
    @property
    def selected_contact(self):
        contacts=Contacts(self.contact)
        return contacts.preferredContact
    
    @property
    def person(self):
        return {
            "first_name":self.personal.first_name,
            "last_name":self.personal.last_name,
            "dob":self.personal.dob.strftime('%d-%b-%Y'),
        }

class RepFormDocxAdaptor():
    def __init__(self,repform_obj:RepFormModel):
        self.repform_obj=repform_obj
        
    def re_generate_dict(self):
        summary_info={
            'personal':self.repform_obj.person,
            'date_signed':date.today(),
            "contact_last_name":self.repform_obj.selected_contact.last_name,
            "contact_first_name":self.repform_obj.selected_contact.first_name,
        }
        return {**self.repform_obj.dict(),**summary_info}

    def make(self,output_xml):
        path=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        template_path=path+"/template/xml/bcpnp_rep.xml"            
        xf=XmlFiller(template_path,self.re_generate_dict())
        xf.save(output_xml)