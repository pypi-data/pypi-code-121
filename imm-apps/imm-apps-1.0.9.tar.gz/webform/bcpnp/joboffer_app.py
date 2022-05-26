from webform.bcpnp.dashboard import DashboardApp, DashboardReg
from webform.models.definition import Action
from webform.models.bcpnpmodel_app import BcpnpModelApp, BcpnpEEModelApp
from model.common.address import Addresses
from model.common.contact import Contacts
from webform.bcpnp.data import country_map, getLegalStructure, getCompanyIndustry
from typing import Union
from model.common.jobofferbase import JobofferBase


class JobofferApp:
    def __init__(self, person: Union[BcpnpModelApp, BcpnpEEModelApp]):
        self.person = person

    def fill(self):
        legal_other = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "If other, specify",
                    "id": "#BCPNP_App_Emp_Comp_LegalStructure_Other",
                    "value": self.person.general.other_explaination,
                    "required": True,
                    "length": 100,
                }
            ]
            if getLegalStructure(self.person.general.corporate_structure, "BC")
            == "Other"
            else []
        )
        legal_structure = [
            {
                "action_type": Action.Select.value,
                "label": "Company legal structure",
                "id": "#BCPNP_App_Emp_Comp_LegalStructure",
                "value": getLegalStructure(
                    self.person.general.corporate_structure, "BC"
                ),
            }
        ] + legal_other

        company_details = [
            {
                "action_type": Action.Input.value,
                "label": "Company legal name",
                "id": "#syncA_App_Emp_Comp_LegalName",
                "value": self.person.general.legal_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Company operating name",
                "id": "#syncA_App_Emp_Comp_OperName",
                "value": self.person.general.operating_name,
                "required": False,
                "length": 100,
            },
            *legal_structure,
            {
                "action_type": Action.Input.value,
                "label": "Incorporation or registration number",
                "id": "#syncA_App_Emp_IncorpNo",
                "value": self.person.general.registration_number,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Number of full-time equivalent employees",
                "id": "#syncA_App_Emp_EmployeesNo",
                "value": str(self.person.general.ft_employee_number),
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Input.value,
                "label": "Year established in B.C.",
                "id": "#BCPNP_App_Emp_YearBC",
                "value": self.person.general.establish_date,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Select.value,
                "label": "Company economic sector",
                "id": "#syncA_App_Emp_Sector",
                "value": getCompanyIndustry(self.person.general.industry),
            },
            {
                "action_type": Action.Input.value,
                "label": "Company website",
                "id": "#BCPNP_App_Emp_Website",
                "value": self.person.general.website,
                "required": False,
                "length": 100,
            },
        ]
        business_address = Addresses(self.person.eraddress).business
        business_location = [
            {
                "action_type": Action.Input.value,
                "label": "Unit number",
                "id": "#BCPNP_App_Emp_CompAddrUnit",
                "value": business_address.unit,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Street address",
                "id": "#BCPNP_App_Emp_BusAddr",
                "value": business_address.street_address,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "City/Town",
                "id": "#syncA_App_Emp_BusCity",
                "value": business_address.city,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Province",
                "id": "#BCPNP_App_Emp_BusProvince",
                "value": business_address.province,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Postal code",
                "id": "#syncA_App_Emp_BusPostal",
                "value": business_address.post_code,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Country",
                "id": "#BCPNP_App_Emp_BusCountry",
                "value": country_map[business_address.country],
                "required": True,
                "length": 100,
            },
        ]
        mailing_address = Addresses(self.person.eraddress).mailing
        is_same = [
            {
                "action_type": Action.Radio.value,
                "label": "Is the mailing address the same as the physical address? ",
                "id": "#BCPNP_App_MailAddrSame-Yes"
                if business_address == mailing_address
                else "#BCPNP_App_MailAddrSame-No",
            }
        ]
        mailing_location = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Unit number",
                    "id": "#BCPNP_App_Emp_CompAltAddrUnit",
                    "value": mailing_address.unit,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Street address",
                    "id": "#BCPNP_App_Emp_MailAddr",
                    "value": mailing_address.street_address,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City/Town",
                    "id": "#syncA_App_Emp_MailCity",
                    "value": mailing_address.city,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Province",
                    "id": "#BCPNP_App_Emp_MailProvince",
                    "value": mailing_address.province,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Postal code",
                    "id": "#BCPNP_App_Emp_MailPostal",
                    "value": mailing_address.post_code,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Country",
                    "id": "#BCPNP_App_Emp_MailCountry",
                    "value": country_map[mailing_address.country],
                    "required": True,
                    "length": 100,
                },
            ]
            if business_address != mailing_address
            else []
        )
        contact = Contacts(self.person.contact).preferredContact
        employer_contact = [
            {
                "action_type": Action.Input.value,
                "label": "Famil name",
                "id": "#syncA_App_Emp_ContactLname",
                "value": contact.last_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": "#syncA_App_Emp_ContactFname",
                "value": contact.first_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Job title",
                "id": "#syncA_App_Emp_ContactTitle",
                "value": contact.position,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Phone number",
                "id": "#syncA_App_Emp_ContactPhone",
                "value": contact.phone,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Email",
                "id": "#syncA_App_Emp_ContactEmail",
                "value": contact.email,
                "required": True,
                "length": 100,
            },
        ]
        with_joboffer = self.person.joboffer.noc != ""
        has_joboffer = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have an offer of full-time employment? ",
                "id": "#syncA_App_FullTimeEmpOffer-Yes"
                if with_joboffer
                else "#syncA_App_FullTimeEmpOffer-No",
            }
        ]
        indeterminate_joboffer = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have an indeterminate job offer? ",
                "id": "#syncA_App_FullTimeEmpOfferInd-Yes"
                if self.person.joboffer.permanent
                else "#syncA_App_FullTimeEmpOfferInd-No",
            }
        ]
        end_date = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "End date",
                    "id": "#syncA_App_Job_OfferEndDate",
                    "value": self.person.joboffer.work_end_date,
                    "required": True,
                    "length": 100,
                }
            ]
            if not self.person.joboffer.permanent
            else []
        )

        joboffer_details = [
            {
                "action_type": Action.Input.value,
                "label": "Job title",
                "id": "#syncA_App_Job_Title",
                "value": self.person.joboffer.job_title,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "NOC",
                "id": "#syncA_App_Job_NOC",
                "value": self.person.joboffer.noc,
                "required": False,
                "length": 100,
            },
            {
                "action_type": Action.Radio.value,
                "label": "Is the occupation regulated/licensed? ",
                "id": "#BCPNP_App_Job_IsRegulated-Yes"
                if self.person.joboffer.license_request
                else "#BCPNP_App_Job_IsRegulated-No",
            },
            {
                "action_type": Action.Input.value,
                "label": "Hours of work per week",
                "id": "#syncA_App_Job_HoursPerWeek",
                "value": self.person.joboffer.weekly_hours,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Hourly wage",
                "id": "#syncA_App_Job_HourlyWage",
                "value": self.person.joboffer.hourly_rate,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Annual Salary",
                "id": "#syncA_App_Job_AnnualWage",
                "value": self.person.joboffer.annual_rate,
                "required": True,
                "length": 100,
            },
        ]
        job_offer = has_joboffer + indeterminate_joboffer + end_date + joboffer_details
        work_addresses = Addresses(self.person.eraddress).workings
        locations = []
        for index, address in enumerate(work_addresses):
            values = [
                {
                    "action_type": Action.Input.value,
                    "label": "Unit number ",
                    "id": f"#BCPNP_App_Emp_WorkAddrUnit-{index}",
                    "value": address.unit,
                    "required": True,
                    "length": 10,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Street address",
                    "id": f"#syncA_App_Job_WorkLocationAddr-{index}",
                    "value": address.street_address,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City ",
                    "id": f"#syncA_App_Job_WorkLocationCity-{index}",
                    "value": address.city,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Phone number ",
                    "id": f"#syncA_App_Job_WorkLocationPhone-{index}",
                    "value": address.phone,
                },
            ]
            locations.append(values)
        work_locations = [
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(5) > div > div > uf-panel:nth-child(5) > div > uf-panel-body > div > div:nth-child(3) > uf-clone-repeatable > a > i",
                "value": locations,
            }
        ]

        dashboard = DashboardApp()
        actions = (
            dashboard.jump("Job Offer")
            + company_details
            + business_location
            + is_same
            + mailing_location
            + employer_contact
            + job_offer
            + work_locations
            + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Joboffer",
                "actions": actions,
                "id": None,
            }
        ]
