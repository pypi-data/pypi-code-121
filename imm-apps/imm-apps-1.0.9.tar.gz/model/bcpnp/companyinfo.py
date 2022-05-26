from .context import DATADIR
from model.common.commonmodel import CommonModel
from model.bcpnp.data import General
from model.common.jobposition import Position
from model.common.wordmaker import WordMaker
import os

        
class CompanyInfoModel(CommonModel):
    general:General
    position:Position
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/er.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())

class CompanyInfoDocxAdaptor():
    def __init__(self,employer_training_obj:CompanyInfoModel):
        self.employer_training_obj=employer_training_obj
        
    def make(self, output_docx):
        template_path=os.path.abspath(os.path.join(DATADIR,"word/bcpnp_company_information.docx")) 
        wm = WordMaker(template_path, self.employer_training_obj, output_docx)
        wm.make()
        