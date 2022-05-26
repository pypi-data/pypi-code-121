from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.bcpnp.dashboard import DashboardReg
from model.common.language import Languages
from webform.bcpnp.data import language_map
from typing import Union


class Language:
    def __init__(self, person: Union[BcpnpModelReg, BcpnpEEModelReg]):
        self.person = person

    def fill(self):
        language = Languages(self.person.language).PreferredLanguage
        has_language_tested = [
            {
                "action_type": Action.Radio.value,
                "label": "Have you completed a valid language proficiency test within the past two years? ",
                "id": "#BCPNP_App_LangTest_Completed-Yes"
                if language
                else "#BCPNP_App_LangTest_Completed-No",
            }
        ]

        test_admin_info_head = []
        test_admin_info_foot = []

        match language.test_type:
            case "IELTS":
                test_admin_info_head = [
                    {
                        "action_type": Action.Input.value,
                        "label": "Date of administrator's signature",
                        "id": "#BCPNP_App_LangTest_Date",
                        "value": language.report_date.strftime("%Y-%m-%d"),
                        "required": True,
                        "length": 100,
                    }
                ]
                test_admin_info_foot = [
                    {
                        "action_type": Action.Input.value,
                        "label": "Test report form number",
                        "id": "#BCPNP_App_LangTest_CertNo",
                        "value": language.registration_number,
                        "required": True,
                        "length": 100,
                    }
                ]
        type_of_test = [
            {
                "action_type": Action.Select.value,
                "label": "Type of test taken",
                "id": "#BCPNP_App_LangTest_Type",
                "value": language_map[language.test_type],
            }
        ]
        language_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Listening score",
                    "id": "#BCPNP_App_LangTest_ResListening",
                    "value": str(language.listening),
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Reading score",
                    "id": "#BCPNP_App_LangTest_ResReading",
                    "value": str(language.reading),
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Writing score",
                    "id": "#BCPNP_App_LangTest_ResWriting",
                    "value": str(language.writting),
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Speaking score",
                    "id": "#BCPNP_App_LangTest_ResSpeaking",
                    "value": str(language.speaking),
                    "required": True,
                    "length": 100,
                },
            ]
            if language
            else []
        )

        dashboard = DashboardReg()
        actions = (
            dashboard.jump("Language")
            + has_language_tested
            + type_of_test
            + test_admin_info_head
            + language_details
            + test_admin_info_foot
            + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Language",
                "actions": actions,
                "id": None,
            }
        ]
