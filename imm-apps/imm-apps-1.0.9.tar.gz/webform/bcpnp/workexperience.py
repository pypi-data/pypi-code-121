from typing import Union
from webform.models.definition import Action
from webform.models.bcpnpmodel_app import BcpnpModelApp, BcpnpEEModelApp
from webform.bcpnp.dashboard import DashboardApp
from model.common.employmenthistory import EmploymentHistory
from datetime import datetime
from webform.bcpnp.data import country_map


class WorkExperience:
    def __init__(self, person: Union[BcpnpModelApp, BcpnpEEModelApp]):
        self.person = person

    def has_work_experience(self, jobs):
        return [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have work experience in the past ten years?",
                "id": "#BCPNP_App_WorkExp-Yes"
                if len(jobs) > 0
                else "#BCPNP_App_WorkExp-No",
            }
        ]

    def block(self, job, index):
        return [
            {
                "action_type": Action.Input.value,
                "label": "Job title",
                "id": f"#BCPNP_App_Work_Title-{index}",
                "value": job.job_title,
                "required": True,
                "length": 200,
            },
            {
                "action_type": Action.Input.value,
                "label": "NOC (4 digits)",
                "id": f"#BCPNP_App_Work_NOC-{index}",
                "value": job.noc_code,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Radio.value,
                "label": "Job hours ",
                "id": f"#BCPNP_App_Work_JobHours-{index}-full-time"
                if job.weekly_hours >= 30
                else f"#BCPNP_App_Work_JobHours-{index}-part-time",
            },
            {
                "action_type": Action.Input.value,
                "label": "Start date",
                "id": f"#BCPNP_App_Work_From-{index}",
                "value": job.start_date.strftime("%Y-%m-%d"),
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Input.value,
                "label": "End date",
                "id": f"#BCPNP_App_Work_To-{index}",
                "value": datetime.today().strftime("%Y-%m-%d")
                if job.is_present
                else job.end_date.strftime("%Y-%m-%d"),
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Checkbox.value,
                "label": "Present",
                "id": f"body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(3) > div > uf-panel > div > uf-panel-body > div > div > div.ng-pristine.ng-untouched.ng-valid.ng-isolate-scope.ng-not-empty > div:nth-child({index+1}) > uf-row:nth-child(3) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div > label",
                "value": True if job.end_date else False,
            },
            {
                "action_type": Action.Input.value,
                "label": "Company name",
                "id": f"#BCPNP_App_Work_Company-{index}",
                "value": job.company,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Company phone number",
                "id": f"#BCPNP_App_Work_CompPhone-{index}",
                "value": job.phone_of_certificate_provider,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Company website",
                "id": f"#BCPNP_App_Work_CompWebsite-{index}",
                "value": job.website,
                "required": False,
                "length": 200,
            },
            {
                "action_type": Action.Input.value,
                "label": "Unit number",
                "id": f"#BCPNP_App_Work_CompAddrUnit-{index}",
                "value": job.unit,
                "required": False,
                "length": 200,
            },
            {
                "action_type": Action.Input.value,
                "label": "Address",
                "id": f"#BCPNP_App_Work_CompAddr-{index}",
                "value": job.street_address,
                "required": True,
                "length": 200,
            },
            {
                "action_type": Action.Input.value,
                "label": "City",
                "id": f"#BCPNP_App_Work_CompCity-{index}",
                "value": job.city,
                "required": True,
                "length": 200,
            },
            {
                "action_type": Action.Input.value,
                "label": "Province",
                "id": f"#BCPNP_App_Work_CompProvince-{index}",
                "value": job.province,
                "required": True,
                "length": 200,
            },
            {
                "action_type": Action.Select.value,
                "label": "Country",
                "id": f"#BCPNP_App_Work_CompCountry-{index}",
                "value": country_map[job.country],
            },
            {
                "action_type": Action.Input.value,
                "label": "Postal code",
                "id": f"#BCPNP_App_Work_CompPostal-{index}",
                "value": job.postcode,
                "required": True,
                "length": 200,
            },
            {
                "action_type": Action.Areatext.value,
                "label": "Your responsibilities ",
                "id": f"#BCPNP_App_Work_Duties-{index}",
                "value": job.duties,
                "required": True,
                "length": 3000,
            },
        ]

    def repeat_blocks(self, jobs):
        blocks = []
        for index, job in enumerate(jobs):
            blocks.append(self.block(job, index))
        return blocks

    def fill(self):
        # get highest edu level
        jobs = EmploymentHistory(self.person.employment).qualified_employment(
            "bcpnp_qualified"
        )
        employment = [
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(3) > div > uf-panel > div > uf-panel-body > div > div > div:nth-child(3) > uf-clone-repeatable > a > ng-transclude > span",
                "value": self.repeat_blocks(jobs),
            }
        ]
        dashboard = DashboardApp()
        actions = (
            dashboard.jump("Work Experience")
            + self.has_work_experience(jobs)
            + employment
            + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Work Experience",
                "actions": actions,
                "id": None,
            }
        ]
