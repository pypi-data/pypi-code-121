from .context import DATADIR
from model.experience.ecdata import Employment
from model.common.employmenthistory import EmploymentHistory
from datetime import date
from source.excel import Excel
from model.common.id import ID,IDs
from model.common.person import Person
from model.common.wordmaker import WordMaker
import os

class EmploymentModel():
    
    #使用excels keyword参数是为了配合其他模块，用excel文件名列表输入。
    def __init__(self,excels=None): # excel includes data
        self.data_excel=excels[0]
    
    def getData(self):
        e = Excel(self.data_excel)
        #Get company set
        try:
            company_set = set([emp['company'] for emp in e.dict['employment'] if emp['employment_certificate'][0].upper() == 'Y'])
        except KeyError as err:
            raise ValueError(f'key error in employment sheet. Please check "company","employment","employment_certificate"')
        # pick a company for employment certificate generation
        companies = list(company_set)
        [print(index, company) for index, company in enumerate(companies)]
        which_one = input("Please input the number of the employer: ")
        company = companies[int(which_one)]

        # get validated data
        m_ec = []
        is_current=False
        works = [emp for emp in e.dict['employment'] if emp['company'] == company]
        
        for i, employment in enumerate(works):
            if not employment["end_date"]: is_current=True
            m_ec.append(Employment(**employment))
        #get summary info
        history=EmploymentHistory(m_ec)
        start_date=history.initial_start_date
        end_date=history.final_end_date
        position_number=history.position_number_say
        # person info
        personal=Person(**e.dict['personal'])
        iddds=e.dict['personid']
        id_list=[ID(**id) for id in iddds]
        ids=IDs(id_list)

        # get company brief, and hr rep's information from the list of positions in one company. The rep info could be in any period, but only get one of them.
        def getContent(field):
            for w in m_ec:
                value = getattr(w,field)
                if value:
                    return value
            return None

        context={
            # 'company_brief':company_brief,
            'company_brief':getContent('company_brief'),
            'hr_rep_name':getContent('fullname_of_certificate_provider'),
            'hr_rep_position':getContent('position_of_certificate_provider'),
            'hr_rep_department':getContent('department_of_certificate_provider'),
            'hr_rep_phone':getContent('phone_of_certificate_provider'),
            'hr_rep_email':getContent('email_of_certificate_provider'),
            "passport":ids.passport.number,
            "work":m_ec,
            'personal':personal,
            'more_than_1':len(m_ec)>1,
            'position_number':position_number,
            'is_current':is_current,
            'start_date':start_date.strftime('%b %Y'),
            'end_date':end_date
            }
        
        return context
    
    
        

class EmploymentModelDocxAdapater():
    """This is an adapater to bridging resume model data and docx data
    """
    def __init__(self,emp_obj: EmploymentModel):
        # get original resume obj, which will be used to generate some value based on it's object methods. 
        self.emp_obj=emp_obj
    
    def make(self,output_docx):
        template_path=os.path.abspath(os.path.join(DATADIR,"word/employment_certificate.docx"))     
        wm=WordMaker(template_path,self.emp_obj.getData(),output_docx)
        wm.make()
    
