from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Bcpnp, General,JobOffer,ErAddress
from model.common.jobposition import Position
from model.common.rcic import Rcic
from model.common.advertisement import Advertisement,Advertisements,InterviewRecord,InterviewRecords,RecruitmentSummary
from model.common.person import Person,PersonalAssess
from model.common.address import Addresses
from model.common.wordmaker import WordMaker
import os

class Personal(Person):
    def __str__(self):
        return self.full_name
        
class EmployerTrainingModel(CommonModel):
    eraddress:List[ErAddress]
    general:General
    position:Position
    personal:Personal
    joboffer:JobOffer
    personalassess:PersonalAssess
    bcpnp:Bcpnp
    rcic:Rcic
    advertisement:List[Advertisement]
    interviewrecord:List[InterviewRecord]
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
    def work_location(self):
        addresses=Addresses(self.eraddress)
        return addresses.working
    
    @property
    def selected_contact(self):
        contacts=Contacts(self.contact)
        return contacts.preferredContact
    
    @property
    def summary(self):
        return InterviewRecords(self.interviewrecord)
    
    @property
    def advertisements(self):
        return Advertisements(self.advertisement)
    
    @property
    def person(self):
        return {
            "full_name":self.personal.full_name,
            "attributive":self.personal.attributive,
            "object":self.personal.object,
            "subject":self.personal.subject,
            'short_name':self.personal.short_name
        }

class EmployerTrainingDocxAdaptor():
    def __init__(self,employer_training_obj:EmployerTrainingModel):
        self.employer_training_obj=employer_training_obj
        
    def re_generate_dict(self):
        summary_info={
            'resume_num':self.employer_training_obj.summary.resume_num,
            'canadian_num':self.employer_training_obj.summary.canadian_num,
            'unknown_num':self.employer_training_obj.summary.unknown_num,
            "foreigner_num":self.employer_training_obj.summary.foreigner_num,
            "total_canadian":self.employer_training_obj.summary.total_canadian,
            "total_interviewed_canadians":self.employer_training_obj.summary.total_interviewed_canadians,
            "canadian_records":self.employer_training_obj.summary.canadian_records,
            "advertisement":self.employer_training_obj.advertisements,
            'personal':self.employer_training_obj.person,
            "date_of_offer":self.employer_training_obj.joboffer.date_of_offer,
            "work_start_date":self.employer_training_obj.joboffer.start_date_say,
            'joboffer_date':self.employer_training_obj.joboffer.date_of_offer,
            'work_location':self.employer_training_obj.work_location
        }
        return {**self.employer_training_obj.dict(),**summary_info}

    def make(self,output_docx):
        template_path=os.path.abspath(os.path.join(DATADIR,"word/bcpnp_facts_brief_employer.docx")) 
        wm=WordMaker(template_path,self.re_generate_dict(),output_docx)
        wm.make()
