from .context import DATADIR
from email.policy import default
from textwrap import indent
from typing import List,Optional
from model.experience.resumedata import Personal,Language,PersonalAssess,Education, Employment
from model.common.commonmodel import CommonModel
from model.common.phone import Phone,Phones 
from model.common.address import Address,Addresses
from datetime import date
from model.common.wordmaker import WordMaker
import os,json

class ResumeModel(CommonModel):
    personal:Personal
    phone:List[Phone]
    personalassess:PersonalAssess
    education:List[Education]
    language:Optional[List[Language]]
    employment:Optional[List[Employment]]
    address:List[Address]
    
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/pa.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())
        
class ResumeModelDocxAdapater():
    """This is an adapater to bridging resume model data and docx data
    """

    def __init__(self,resume_obj: ResumeModel):
        # get original resume obj, which will be used to generate some value based on it's object methods. 
        self.resume_obj=resume_obj
        #从列表中挑选element出来，并替换该列表
        phones=Phones(self.resume_obj.phone)
        addresses=Addresses(self.resume_obj.address)
        
        self.resume_obj.phone=phones.PreferredPhone
        self.resume_obj.address=addresses.PreferredAddress

    def make(self,output_docx,template_no=None):
        template_no = template_no or 1
        filename="word/resume-regular"+str(template_no)+".docx"
        template_path=os.path.abspath(os.path.join(DATADIR,filename))    
        wm=WordMaker(template_path,self.resume_obj,output_docx)
        wm.make()



