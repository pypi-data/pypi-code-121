from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.bcpnp.dashboard import DashboardReg
from model.common.educationbase import EducationHistory
from webform.bcpnp.data import getEducation, eca_map
from typing import Union


class Education:
    def __init__(self, person: Union[BcpnpModelReg, BcpnpEEModelReg]):
        self.person = person

    def fill(self):
        # get highest edu level
        highest_edu = EducationHistory(self.person.education).highestEducation
        is_trade = highest_edu.is_trade
        highest_section = [
            {
                "action_type": Action.Select.value,
                "lable": "Highest level of education",
                "id": "#BCPNP_App_Edu_HighestLevel",
                "value": getEducation(highest_edu.education_level, is_trade=True)
                if is_trade
                else getEducation(highest_edu.education_level),
            },
            {
                "action_type": Action.Input.value,
                "label": "Date highest level of education completed?",
                "value": highest_edu.end_date.strftime("%Y-%m-%d"),
                "id": "#BCPNP_App_Edu_HighestLevel_Loc",
            },
        ]
        edu_in_canada = [
            {
                "action_type": Action.Radio.value,
                "label": "Did you obtain this education in Canada? ",
                "id": "#BCPNP_App_Edu_HighestLevel_Can-Yes"
                if highest_edu.country == "Canada"
                else "#BCPNP_App_Edu_HighestLevel_Can-No",
            }
        ]
        edu_in_bc = (
            [
                {
                    "action_type": Action.Radio.value,
                    "label": "Did you obtain this education in British Columbia?",
                    "id": "#syncA_App_Edu_HighestLevel_BC-Yes"
                    if highest_edu.country == "Canada"
                    else "#syncA_App_Edu_HighestLevel_BC-No",
                }
            ]
            if highest_edu.country == "Canada"
            else []
        )

        has_eca = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have an Education Credential Assessment?  ",
                "id": "#BCPNP_App_Edu_CA-Yes"
                if self.person.personal.did_eca
                else "#BCPNP_App_Edu_CA-No",
            }
        ]
        eca = (
            [
                {
                    "action_type": Action.Select.value,
                    "lable": "Qualified suppliers",
                    "id": "#BCPNP_App_Edu_CA_Cert_Supplier",
                    "value": eca_map[self.person.personal.eca_supplier],
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Certificate number",
                    "value": highest_edu.end_date.strftime("%Y-%m-%d"),
                    "id": "#BCPNP_App_Edu_CA_CertNo",
                },
            ]
            if self.person.personal.did_eca
            else [
                {
                    "action_type": Action.Radio.value,
                    "lable": "Has the Industry Training Authority (ITA) assessed your training and experience?",
                    "id": "#BCPNP_App_Edu_ITA-Yes"
                    if self.person.personal.ita_assessed
                    else "#BCPNP_App_Edu_ITA-No",
                }
            ]
        )

        ita_assessed = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Certificate number",
                    "value": self.person.personal.ita_assess_number,
                    "id": "#BCPNP_App_Edu_ITA_Cert_No",
                }
            ]
            if self.person.personal.ita_assessed
            else []
        )
        if self.person.personal.did_eca:
            ita_assessed = []

        dashboard = DashboardReg()
        actions = (
            dashboard.jump("Education")
            + highest_section
            + edu_in_canada
            + edu_in_bc
            + has_eca
            + eca
            + ita_assessed
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
