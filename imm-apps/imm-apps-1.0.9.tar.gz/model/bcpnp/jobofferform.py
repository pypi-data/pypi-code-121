from typing import List
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Bcpnp, Contact, General,JobOffer,ErAddress
from model.common.jobposition import Position
from model.common.rcic import Rcic
from model.common.advertisement import Advertisement,Advertisements,InterviewRecord,InterviewRecords,RecruitmentSummary
from model.common.person import Person,PersonalAssess
from model.common.contact import Contacts
from model.common.address import Addresses
from model.common.phone import Phone,Phones
from datetime import date
from model.common.xmlfiller import XmlFiller
import os


class Personal(Person):
    def __str__(self):
        return self.full_name
        
class JobOfferFormModel(CommonModel):
    eraddress:List[ErAddress]
    phone:List[Phone]
    general:General
    contact:List[Contact]
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
            excels=self.getExcels(['excel/er.xlsx','excel/pa.xlsx','excel/recruitment.xlsx','excel/bcpnp.xlsx','excel/rep.xlsx'])
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
    def phones(self):
        return Phones(self.phone)
    
    @property
    def selected_contact(self):
        contacts=Contacts(self.contact)
        return contacts.preferredContact
    
    @property
    def interviews(self):
        return InterviewRecords(self.interviewrecord)
    
    @property
    def advertisements(self):
        return Advertisements(self.advertisement)
    
    @property
    def businessaddress(self):
        eraddress=Addresses(self.eraddress)
        return eraddress.business
    
    @property
    def mailingaddress(self):
        eraddress=Addresses(self.eraddress)
        return eraddress.mailing
    
    @property
    def person(self):
        return {
            "first_name":self.personal.first_name,
            "last_name":self.personal.last_name,
            "full_name":self.personal.full_name,
            "attributive":self.personal.attributive,
            "object":self.personal.object,
            "subject":self.personal.subject,
            'short_name':self.personal.short_name,
            'why_tfw':self.personalassess.why_qualified_say
        }

class JobOfferFormDocxAdaptor():
    def __init__(self,jobofferform_obj:JobOfferFormModel):
        self.jobofferform_obj=jobofferform_obj
        
    def re_generate_dict(self):
        summary_info={
            'personal':self.jobofferform_obj.person,
            "date_of_offer":self.jobofferform_obj.joboffer.date_of_offer,
            "work_start_date":self.jobofferform_obj.joboffer.start_date_say,
            'joboffer_date':self.jobofferform_obj.joboffer.date_of_offer,
            'annual_rate':float(self.jobofferform_obj.joboffer.annual_rate),
            'hourly_rate':float(self.jobofferform_obj.joboffer.hourly_rate),
            'work_location':self.jobofferform_obj.work_location,
            'b_address':self.jobofferform_obj.businessaddress.line1,
            'b_city':self.jobofferform_obj.businessaddress.city,
            'b_province':self.jobofferform_obj.businessaddress.province,
            'b_country':self.jobofferform_obj.businessaddress.country,
            'b_postcode':self.jobofferform_obj.businessaddress.post_code,
            'm_address':self.jobofferform_obj.mailingaddress.line1,
            'm_city':self.jobofferform_obj.mailingaddress.city,
            'm_province':self.jobofferform_obj.mailingaddress.province,
            'm_country':self.jobofferform_obj.mailingaddress.country,
            'm_postcode':self.jobofferform_obj.mailingaddress.post_code,
            'w_address':self.jobofferform_obj.work_location.line1,
            'w_city':self.jobofferform_obj.work_location.city,
            'w_province':self.jobofferform_obj.work_location.province,
            'w_country':self.jobofferform_obj.work_location.country,
            'w_postcode':self.jobofferform_obj.work_location.post_code,
            'date_signed':date.today(),
            # position 3c
            #TODO: is new position , ...
            # "under_cba":
            "which_union":self.jobofferform_obj.position.which_union,
            "lmia_refused":"Yes_5"  if self.jobofferform_obj.position.lmia_refused else "No_5",
            "lmia_refused_reason": self.jobofferform_obj.position.lmia_refused_reason if self.jobofferform_obj.position.lmia_refused else "",
            # "other_language_required":self.jobofferform_obj.joboffer.other_language_required #TODO: ,
            "what_language":self.jobofferform_obj.joboffer.reason_for_other,
            
            # "license_required":
            "which_license":self.jobofferform_obj.joboffer.license_description,
            
            # 4. recruitment summary
            "active_recruitment":"Yes_7" if self.jobofferform_obj.advertisements.amount>0 else "No_7",
            "min_days":self.jobofferform_obj.advertisements.min_days,
            "total_applicant":self.jobofferform_obj.interviews.resume_num,
            'recruitment_summary':self.jobofferform_obj.advertisements.summary+self.jobofferform_obj.interviews.summary+self.jobofferform_obj.position.how_did_you_find,

            "contact_email":self.jobofferform_obj.selected_contact.email,
            "contact_last_name":self.jobofferform_obj.selected_contact.last_name,
            "contact_first_name":self.jobofferform_obj.selected_contact.first_name,
            "contact_phone":self.jobofferform_obj.selected_contact.phone,
            'contact_position':self.jobofferform_obj.selected_contact.position,
            'business_phone':self.jobofferform_obj.phones.business.international_format_full,
            
        }
        return {**self.jobofferform_obj.dict(),**summary_info}

    def make(self,output_xml):
        path=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        template_path=path+"/template/xml/bcpnp_job_offer_form.xml"            
        xf=XmlFiller(template_path,self.re_generate_dict())
        xf.save(output_xml)