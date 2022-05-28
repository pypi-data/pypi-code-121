from typing import Union
from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.bcpnp.dashboard import DashboardReg
from model.common.employmenthistory import EmploymentHistory
from datetime import datetime


class Employment:
    def __init__(self, person: Union[BcpnpModelReg, BcpnpEEModelReg]):
        self.person = person

    def has_work_experience(self, jobs):
        return [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have directly related work experience at the same or greater NOC level in the past 10 years, including the Job Offer?",
                "id": "#BCPNP_App_Job_Work_ExperienceRelated-Yes"
                if len(jobs) > 0
                else "#BCPNP_App_Job_Work_ExperienceRelated-No",
            }
        ]

    def block(self, job, index):
        id_present = (
            "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(3) > div > uf-panel > div > uf-panel-body > div > div > div.ng-pristine.ng-untouched.ng-valid.ng-isolate-scope.ng-not-empty > div > uf-row:nth-child(4) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div > label"
            if index == 0
            else f"body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(3) > div > uf-panel > div > uf-panel-body > div > div > div.ng-pristine.ng-untouched.ng-valid.ng-isolate-scope.ng-not-empty > div:nth-child({index+1}) > uf-row:nth-child(4) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div"
        )
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
                "id": id_present,
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
                "action_type": Action.Radio.value,
                "label": "Was this work in Canada? ",
                "id": f"#BCPNP_App_WorkExp_InCan-{index}-Yes"
                if job.country == "Canada"
                else f"#BCPNP_App_WorkExp_InCan-{index}-No",
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
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(3) > div > uf-panel > div > uf-panel-body > div > div > div:nth-child(2) > uf-clone-repeatable > a > i",
                "value": self.repeat_blocks(jobs),
            }
        ]
        dashboard = DashboardReg()
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
