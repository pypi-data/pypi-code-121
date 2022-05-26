from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel
from model.lmia.data import LmiaCase,Finance,Lmi,Emp5626,Emp5627,Emp5593,General,JobOffer,PersonalAssess,Rcic
from model.common.jobposition import Position
from model.common.advertisement import InterviewRecord,Advertisement
from model.common.person import Person
from model.common.wordmaker import WordMaker
import os


class Personal(Person):
    def __str__(self):
        return self.full_name
        
class SubmissionLetterModel(CommonModel):
    general:General
    position:Position
    personal:Personal
    joboffer:JobOffer
    personalassess:PersonalAssess
    lmiacase:LmiaCase
    finance:List[Finance]
    lmi:Lmi
    rcic:Rcic
    advertisement:List[Advertisement]
    interviewrecord:List[InterviewRecord]
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(["excel/er.xlsx",'excel/pa.xlsx','excel/recruitment.xlsx','excel/lmia.xlsx','rep.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())
        
    def makeDocx(self,output_docx):
        template_path=os.path.abspath(os.path.join(DATADIR,"word/lmia_submission_letter.docx"))      
        wm=WordMaker(template_path,self,output_docx)
        wm.make()
    
class M5593SubmissionLetterModel(SubmissionLetterModel):
    pass
    
class M5626ubmissionLetterModel(SubmissionLetterModel):
    pass
    
class M5627SubmissionLetterModel(SubmissionLetterModel):
    pass

