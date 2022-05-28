from webform.models.bcpnpmodel_app import BcpnpEEModelApp, BcpnpModelApp
from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.bcpnp.dashboard import DashboardApp, DashboardReg
from model.common.educationbase import EducationHistory
from webform.bcpnp.data import (
    getEducation,
    country_map,
    province_map,
    city_map,
    getFieldofStudy,
)
from typing import Union


class EducationApp:
    def __init__(self, person: Union[BcpnpModelApp, BcpnpEEModelApp]):
        self.person = person

    @property
    def high_school(self):
        high_school_value = []
        high_school = EducationHistory(self.person.education).high_school

        for index, edu in enumerate(high_school):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#BCPNP_App_EduSec_From-" + str(index),
                    "value": edu.start_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#BCPNP_App_EduSec_To-" + str(index),
                    "value": edu.end_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Checkbox.value,
                    "label": "Currently Enrolled",
                    "id": f"body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(2) > div > uf-panel-body > div > div.ng-pristine.ng-untouched.ng-valid.ng-scope.ng-isolate-scope.ng-not-empty > div:nth-child({index+1}) > uf-row:nth-child(2) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div > label",
                    "value": False if edu.graduate_date else True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Name of Institution",
                    "id": "#BCPNP_App_EduSec_School-" + str(index),
                    "value": edu.school_name,
                    "length": 200,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City/town",
                    "id": "#BCPNP_App_EduSec_City-" + str(index),
                    "value": edu.city,
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Country",
                    "id": "#BCPNP_App_EduSec_Country-" + str(index),
                    "value": country_map[edu.country],
                },
                {
                    "action_type": Action.Radio.value,
                    "label": "Did you successfully complete high school",
                    "id": "#BCPNP_App_EduSec_Completion-" + str(index) + "-Yes"
                    if edu.graduate_date
                    else "#BCPNP_App_EduSec_Completion-" + str(index) + "-No",
                },
            ]
            high_school_value.append(block)
        return [
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(2) > div > uf-panel-body > div > div:nth-child(2) > uf-clone-repeatable > a > i",
                "value": high_school_value,
            }
        ]

    @property
    def post_cecondary_in_bc(self):
        value = []
        education = EducationHistory(self.person.education).post_secondary_in_ca_prov(
            "BC"
        )

        has_post_edu_in_bc = {
            "action_type": Action.Radio.value,
            "label": "Have you enrolled in or completed a post-secondary program within B.C.?",
            "id": "#BCPNP_App_EduBC-Yes"
            if len(education) > 0
            else "#BCPNP_App_EduBC-No",
        }
        for index, edu in enumerate(education):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#BCPNP_App_EduBC_From-" + str(index),
                    "value": edu.start_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#syncA_App_EduBC_To-" + str(index),
                    "value": edu.end_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Checkbox.value,
                    "label": "Currently Enrolled",
                    "id": f"body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(3) > div > uf-panel-body > div > div > div.ng-pristine.ng-untouched.ng-valid.ng-isolate-scope.ng-not-empty > div:nth-child({index+1}) > uf-row:nth-child(1) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div > label",
                    "value": False if edu.graduate_date else True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Name of Institution",
                    "id": "#syncA_App_EduBC_Institution-" + str(index),
                    "value": edu.school_name,
                    "length": 200,
                    "required": True,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "City/town",
                    "id": "#syncA_App_EduBC_City-" + str(index),
                    "value": city_map[edu.city],
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Level of post-secondary education attained",
                    "id": "#syncA_App_EduBC_Level-" + str(index),
                    "value": getEducation(
                        edu.education_level, edu.is_trade, is_reg=False
                    ),
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Field of study",
                    "id": "#syncA_App_EduBC_Field-" + str(index),
                    "value": getFieldofStudy(edu.field_of_study),
                },
            ]
            other_field = (
                [
                    {
                        "action_type": Action.Input.value,
                        "label": "If other, enter field of study",
                        "id": "#BCPNP_App_EduBC_OtherField-" + str(index),
                        "value": edu.field_of_study,
                        "length": 200,
                        "required": True,
                    }
                ]
                if getFieldofStudy(edu.field_of_study)
                == "OTH"  # "Other" returned value is OTH
                else []
            )

            value.append(block + other_field)
        return [
            has_post_edu_in_bc,
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div.page > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(3) > div > uf-panel-body > div > div > div:nth-child(2) > uf-clone-repeatable > a > i",
                "value": value,
            },
        ]

    @property
    def post_secondary_in_canada(self):
        value = []
        education = EducationHistory(
            self.person.education
        ).post_secondary_in_ca_but_not_in_prov("BC")

        has_post_edu_in_ca = {
            "action_type": Action.Radio.value,
            "label": "Have you enrolled in or completed a post-secondary program in Canada but not in B.C.?",
            "id": "#BCPNP_App_EduCAN-Yes"
            if len(education) > 0
            else "#BCPNP_App_EduCAN-No",
        }
        for index, edu in enumerate(education):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#BCPNP_App_EduCAN_From-" + str(index),
                    "value": edu.start_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#syncA_App_EduCAN_To-" + str(index),
                    "value": edu.end_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Checkbox.value,
                    "label": "Currently Enrolled",
                    "id": f"body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(4) > div > uf-panel-body > div > div > div.ng-pristine.ng-untouched.ng-valid.ng-isolate-scope.ng-not-empty > div:nth-child({index+1}) > uf-row:nth-child(1) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div > label",
                    "value": False if edu.graduate_date else True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Name of Institution",
                    "id": "#syncA_App_EduCAN_Institution-" + str(index),
                    "value": edu.school_name,
                    "length": 200,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City/town",
                    "id": "#BCPNP_App_EduCAN_City-" + str(index),
                    "value": edu.city,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Province/territory",
                    "id": "#BCPNP_App_EduCAN_Province-" + str(index),
                    "value": province_map[edu.province],
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Level of post-secondary education attained",
                    "id": "#syncA_App_EduCAN_Level-" + str(index),
                    "value": getEducation(
                        edu.education_level, edu.is_trade, is_reg=False
                    ),
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Field of study",
                    "id": "#syncA_App_EduCAN_Field-" + str(index),
                    "value": getFieldofStudy(edu.field_of_study),
                },
            ]
            other_field = (
                [
                    {
                        "action_type": Action.Input.value,
                        "label": "If other, enter field of study",
                        "id": "#BCPNP_App_EduCAN_OtherField-" + str(index),
                        "value": edu.field_of_study,
                        "length": 200,
                        "required": True,
                    }
                ]
                if getFieldofStudy(edu.field_of_study)
                == "OTH"  # "Other" returned value is OTH
                else []
            )

            value.append(block + other_field)
        return [
            has_post_edu_in_ca,
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(4) > div > uf-panel-body > div > div > div:nth-child(2) > uf-clone-repeatable > a > i",
                "value": value,
            },
        ]

    @property
    def post_secondary_out_of_canada(self):
        value = []
        education = EducationHistory(self.person.education).post_secondary_not_in_ca

        has_post_edu_out_of_ca = {
            "action_type": Action.Radio.value,
            "label": "Have you enrolled in or completed a post-secondary program outside of Canada?",
            "id": "#BCPNP_App_EduNCAN-Yes"
            if len(education) > 0
            else "#BCPNP_App_EduNCAN-No",
        }
        for index, edu in enumerate(education):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#BCPNP_App_EduPostSec_From-" + str(index),
                    "value": edu.start_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#BCPNP_App_EduPostSec_To-" + str(index),
                    "value": edu.end_date,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Checkbox.value,
                    "label": "Currently Enrolled",
                    "id": f"body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(5) > div > uf-panel-body > div > div > div.ng-pristine.ng-untouched.ng-valid.ng-isolate-scope.ng-not-empty > div:nth-child({index+1}) > uf-row:nth-child(1) > div > uf-date:nth-child(2) > div > div.form-inline.present-checkbox-container > div > label",  # TODO: see if needed to change
                    "value": False if edu.graduate_date else True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Name of Institution",
                    "id": "#BCPNP_App_EduPostSec_Institution-" + str(index),
                    "value": edu.school_name,
                    "length": 200,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City/town",
                    "id": "#BCPNP_App_EduPostSec_City-" + str(index),
                    "value": edu.city,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Country",
                    "id": "#BCPNP_App_EduPostSec_Country-" + str(index),
                    "value": country_map[edu.country],
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Level of post-secondary education attained",
                    "id": "#BCPNP_App_EduPostSec_Level-" + str(index),
                    "value": getEducation(
                        edu.education_level, edu.is_trade, is_reg=False
                    ),
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Field of study",
                    "id": "#BCPNP_App_EduPostSec_Field-" + str(index),
                    "value": getFieldofStudy(edu.field_of_study),
                },
            ]
            other_field = (
                [
                    {
                        "action_type": Action.Input.value,
                        "label": "If other, enter field of study",
                        "id": "#BCPNP_App_EduPostSec_OtherField-" + str(index),
                        "value": edu.field_of_study,
                        "length": 200,
                        "required": True,
                    }
                ]
                if getFieldofStudy(edu.field_of_study)
                == "OTH"  # "Other" returned value is OTH
                else []
            )

            value.append(block + other_field)
        return [
            has_post_edu_out_of_ca,
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div.page > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(2) > div > uf-panel:nth-child(5) > div > uf-panel-body > div > div > div:nth-child(2) > uf-clone-repeatable > a > i",
                "value": value,
            },
        ]

    def fill(self):
        dashboard = DashboardApp()
        actions = (
            dashboard.jump("Education")
            + self.high_school
            + self.post_cecondary_in_bc
            + self.post_secondary_in_canada
            + self.post_secondary_out_of_canada
            + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Education",
                "actions": actions,
                "id": None,
            }
        ]
