from webform.bcpnp.dashboard import DashboardReg
from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from model.common.address import Addresses
from webform.bcpnp.data import city_map
from typing import Union


class Joboffer:
    def __init__(self, person: Union[BcpnpModelReg, BcpnpEEModelReg]):
        self.person = person

    def fill(self):
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
        ]
        address = Addresses(self.person.eraddress).working
        work_location = [
            {
                "action_type": Action.Input.value,
                "label": "Unit number",
                "id": "#BCPNP_App_Job_WorkLocationAddrUnit",
                "value": address.unit,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Street address",
                "id": "#BCPNP_App_Job_WorkLocationAddr",
                "value": address.street_address,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Select.value,
                "label": "City/Town",
                "id": "#syncA_App_Job_WorkLocationCity",
                "value": city_map[address.city],
            },
            {
                "action_type": Action.Input.value,
                "label": "Postal code",
                "id": "#syncA_App_Job_WorkLocationPostal",
                "value": address.post_code,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Phone number",
                "id": "#BCPNP_App_Job_WorkLocationPhone",
                "value": self.person.joboffer.phone,
                "required": True,
                "length": 100,
            },
        ]

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
                "required": False,
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
            {
                "action_type": Action.Radio.value,
                "label": "Are you currently working for the employer in the job being offered? ",
                "id": "#BCPNP_App_Job_Work_AtOfferedJob-Yes"
                if self.person.joboffer.is_working
                else "#BCPNP_App_Job_Work_AtOfferedJob-No",
            },
        ]

        working_fulltime = (
            [
                {
                    "action_type": Action.Radio.value,
                    "label": "Are you working full-time in B.C. in the job being offered? ",
                    "id": "#BCPNP_App_Job_Work_CurrentOffer-Yes"
                    if float(self.person.joboffer.weekly_hours) >= 30
                    else "#BCPNP_App_Job_Work_CurrentOffer-No",
                },
            ]
            if self.person.joboffer.is_working
            else []
        )

        dashboard = DashboardReg()
        actions = (
            dashboard.jump("Job Offer")
            + company_details
            + work_location
            + joboffer_details
            + working_fulltime
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
