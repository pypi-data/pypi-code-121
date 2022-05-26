from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel
from model.lmia.data import LmiaCase,Contact,General
from model.common.advertisement import Advertisement,InterviewRecord,InterviewRecords,Advertisements
from model.common.person import Person
from model.common.contact import Contacts
import os
from model.common.wordmaker import WordMaker

class Personal(Person):
    def __str__(self):
        return self.full_name
        
class RecruitmnetSummaryModel(CommonModel):
    general:General
    contact:List[Contact]
    lmiacase:LmiaCase
    advertisement:List[Advertisement]
    interviewrecord:List[InterviewRecord]
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(["excel/recruitment.xlsx","excel/lmia.xlsx","excel/er.xlsx"])
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
    def summary(self):
        return InterviewRecords(self.interviewrecord)
    
    @property
    def advertisements(self):
        records=[]
        i=1
        for adv in self.advertisement:
            records.append({**{'days':adv.days},**adv.dict()})
            i+=1
        return records    
    
    
    

class RecruitmnetSummaryDocxAdaptor():
    def __init__(self,recruitment_summary_obj:RecruitmnetSummaryModel):
        self.recruitment_summary_obj=recruitment_summary_obj
        
    def re_generate_dict(self):
        summary_info={
            'resume_num':self.recruitment_summary_obj.summary.resume_num,
            'canadian_num':self.recruitment_summary_obj.summary.canadian_num,
            'unknown_num':self.recruitment_summary_obj.summary.unknown_num,
            "foreigner_num":self.recruitment_summary_obj.summary.foreigner_num,
            "total_canadian":self.recruitment_summary_obj.summary.total_canadian,
            "total_interviewed_canadians":self.recruitment_summary_obj.summary.total_interviewed_canadians,
            "canadian_records":self.recruitment_summary_obj.summary.canadian_records,
            'contact':self.recruitment_summary_obj.selected_contact,
            "advertisement":self.recruitment_summary_obj.advertisements
        }
        return {**self.recruitment_summary_obj.dict(),**summary_info}

    def make(self,output_docx,template_no=None):
        template_path=os.path.abspath(os.path.join(DATADIR,"word/lmia_recruitment_summary.docx"))      
        wm=WordMaker(template_path,self.re_generate_dict(),output_docx)
        wm.make()
    
