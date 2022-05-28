from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel
from model.recruit.jobofferdata import JobOffer,General,ErAddress,ErAddresses
from model.common.address import Address,Addresses
from model.common.person import Person
from model.common.wordmaker import WordMaker
import os

class Personal(Person):
    def __str__(self):
        return self.full_name
        
class JobofferModel(CommonModel):
    general:General
    joboffer:JobOffer
    eraddress:List[ErAddress]
    personal:Personal
    address:List[Address]
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/pa.xlsx','excel/er.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())
        
class JobofferModelDocxAdapater():
    """This is an adapater to bridging job ad model data and docx data
    """

    def __init__(self,joboffer_obj: JobofferModel):
        # get original obj, which will be used to generate some value based on it's object methods. 
        # 此处用来处理list里面的一些内容。 
        self.joboffer_obj=joboffer_obj
        eraddresses=ErAddresses(self.joboffer_obj.eraddress)
        self.joboffer_obj.eraddress=eraddresses.working
        
        addresses=Addresses(self.joboffer_obj.address)
        self.joboffer_obj.address=addresses.residential
        
    def make(self,output_docx,template_no=None):
        file_name="word/joboffer"+str(template_no)+".docx"     
        template_path=os.path.abspath(os.path.join(DATADIR,file_name))        
        wm=WordMaker(template_path,self.joboffer_obj,output_docx)
        wm.make()
    

