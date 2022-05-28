from .context import DATADIR
from typing import List

from pydantic import EmailStr
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Bcpnp, General,JobOffer,ErAddress
from model.common.jobposition import Position
from model.common.rcic import Rcic
from model.common.advertisement import Advertisement,Advertisements,RecruitmentSummary
from model.common.person import Person,PersonalAssess
from model.common.address import Address,Addresses
from model.common.phone import Phone,Phones
from model.common.wordmaker import WordMaker
import os

class Personal(Person):
    email:EmailStr
    def __str__(self):
        return self.full_name
        
class EmployeeTrainingModel(CommonModel):
    eraddress:List[ErAddress]
    general:General
    position:Position
    personal:Personal
    phone:List[Phone]
    address:List[Address]
    joboffer:JobOffer
    personalassess:PersonalAssess
    bcpnp:Bcpnp
    rcic:Rcic
    advertisement:List[Advertisement]
    recruitmentsummary:RecruitmentSummary

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/er.xlsx','excel/pa.xlsx','excel/recruitment.xlsx','bcpnp.xlsx','rep.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())
    
    @property
    def residential_address(self):
        addresses=Addresses(self.address)
        return addresses.residential
        
    @property
    def work_location(self):
        addresses=Addresses(self.eraddress)
        return addresses.working
    
    @property
    def selected_contact(self):
        contacts=Contacts(self.contact)
        return contacts.preferredContact
    
    @property
    def advertisements(self):
        return Advertisements(self.advertisement)
    
    @property
    def phone_number(self):
        return Phones(self.phone).PreferredPhone
    
    @property
    def person(self):
        return {
            "full_name":self.personal.full_name,
            "attributive":self.personal.attributive,
            "object":self.personal.object,
            "subject":self.personal.subject,
            'short_name':self.personal.short_name,
            'email':self.personal.email,
            'phone':self.phone_number,
            'address':self.residential_address
        }

class EmployeeTrainingDocxAdaptor():
    def __init__(self,employer_training_obj:EmployeeTrainingModel):
        self.employer_training_obj=employer_training_obj
        
    def re_generate_dict(self):
        summary_info={
            "advertisement":self.employer_training_obj.advertisements,
            'personal':self.employer_training_obj.person,
            "date_of_offer":self.employer_training_obj.joboffer.date_of_offer,
            "work_start_date":self.employer_training_obj.joboffer.start_date_say,
            'joboffer_date':self.employer_training_obj.joboffer.date_of_offer,
            'work_location':self.employer_training_obj.work_location
        }
        return {**self.employer_training_obj.dict(),**summary_info}

    def make(self, output_docx):
        template_path=os.path.abspath(os.path.join(DATADIR,"word/bcpnp_facts_brief_employee.docx")) 
        wm = WordMaker(template_path, self.re_generate_dict(), output_docx)
        wm.make()
