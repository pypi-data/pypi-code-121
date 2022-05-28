from webform.models.definition import Action
from abc import ABC, abstractclassmethod


class Dashboard:
    @abstractclassmethod
    def jump(self, page: str):
        pass

    @property
    def save(self):
        return [
            {
                "action_type": Action.Button.value,
                "label": "Save",
                "id": "#tabset-navigation > div > div > div.form-group.pull-right > uf-save-button > button",
            }
        ]


class DashboardReg(Dashboard):
    def jump(self, page: str):
        pages = {
            "Registrant": "object:135",
            "Education": "object:136",
            "Work Experience": "object:137",
            "Job Offer": "object:138",
            "Language": "object:139",
            "Submit": "object:140",
        }
        return [
            {
                "action_type": Action.Select.value,
                "label": "Jump to tab",
                "id": "#navigate-to",
                "value": pages[page],
            }
        ]


class DashboardApp(Dashboard):
    def jump(self, page: str):
        pages = {
            "Applicant": "object:224",
            "Education": "object:225",
            "Work Experience": "object:226",
            "Family": "object:227",
            "Job Offer": "object:228",
            "Attachments": "object:230",
            "Submit": "object:231",
        }
        return [
            {
                "action_type": Action.Select.value,
                "label": "Jump to tab",
                "id": "#navigate-to",
                "value": pages[page],
            }
        ]
