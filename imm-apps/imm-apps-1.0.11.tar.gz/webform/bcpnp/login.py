from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.models.bcpnpmodel_app import BcpnpEEModelApp, BcpnpModelApp
from typing import Union
import base64

# This step includs actions of signing in, picking Skill Immigration automatically, select and confirm which stream to apply through
class Login:
    def __init__(
        self,
        person: Union[BcpnpModelReg, BcpnpEEModelReg, BcpnpEEModelApp, BcpnpModelApp],
    ):
        self.person = person

    def encode(self, password):
        password_bytes = password.encode("ascii")
        base64_bytes = base64.b64encode(password_bytes)
        return base64_bytes.decode("ascii")

    def login(self, initial=True):
        sign_in = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Sign in",
                "actions": [
                    {
                        "action_type": Action.GotoPage.value,
                        "url": "https://www.pnpapplication.gov.bc.ca/user/sign-in",
                    },
                    {
                        "action_type": Action.Login.value,
                        "label": "Login",
                        "account": self.person.personal.user_id,
                        "password": self.encode(self.person.personal.password),
                        "account_element_id": "#userId",
                        "password_element_id": "#pass",
                        "login_button_id": "#form > div:nth-child(4) > div > input",
                    },
                ],
                "id": None,  #
            }
        ]

        pick_sk_immigration = [
            # pick skill immigration
            {
                "action_type": Action.WebPage.value,
                "page_name": "Pick skill immigration",
                "actions": [],
                "id": "body > div > main > div.layout-container > div > div > div > div:nth-child(1) > a",
            },
        ]

        # pick a stream of bcpnp
        case_stream = {
            "EE-Skilled Worker": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(1) > a",
                "confirm": "#skills-express-skilled > form > div > label > input[type=checkbox]",
                "start": "#skills-express-skilled > form > input",
            },
            "EE-International Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(2) > a",
                "confirm": "#skills-express-intl-grad > form > div > label > input[type=checkbox]",
                "start": "#skills-express-intl-grad > form > input",
            },
            "EE-International Post-Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(3) > a",
                "confirm": "#skills-express-intl-postgrad > form > div > label > input[type=checkbox]",
                "start": "#skills-express-intl-postgrad > form > input",
            },
            "EE-Health Authority": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(4) > a",
                "confirm": "#skills-express-health-care > form > div > label > input[type=checkbox]",
                "start": "#skills-express-health-care > form > input",
            },
            "Skilled Worker": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(1) > a",
                "confirm": "#skills-skilled > form > div > label > input[type=checkbox]",
                "start": "#skills-skilled > form > input",
            },
            "International Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(2) > a",
                "confirm": "#skills-intl-grad > form > div > label > input[type=checkbox]",
                "start": "#skills-intl-grad > form > input",
            },
            "Entry-Level and Semi-Skilled Worker": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(3) > a",
                "confirm": "#skills-entry-level > form > div > label > input[type=checkbox]",
                "start": "#skills-entry-level > form > input",
            },
            "International Post-Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(4) > a",
                "confirm": "#skills-intl-postgrad > form > div > label > input[type=checkbox]",
                "start": "#skills-intl-postgrad > form > input",
            },
            "Health Authority": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(5) > a",
                "confirm": "#skills-health-care > form > div > label > input[type=checkbox]",
                "start": "#skills-health-care > form > input",
            },
        }
        pick_stream = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Pick skill immigration",
                "actions": [
                    {
                        "action_type": Action.Button.value,
                        "label": "Pick which stream to apply through",
                        "id": case_stream[self.person.bcpnp.case_stream]["link"],
                    },
                    {
                        "action_type": Action.Checkbox.value,
                        "label": "I confirm that I qualify all the category requirements",
                        "id": case_stream[self.person.bcpnp.case_stream]["confirm"],
                    },
                ],
                "id": case_stream[self.person.bcpnp.case_stream]["start"],
            }
        ]

        confirm_profile = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Confirm profile and representative",
                "actions": [],
                "id": "body > div > main > div.layout-container > div > div > form > button",
            }
        ]

        continue_page = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Continue my registration",
                "actions": [],
                "id": "body > div.page > main > div > div > div > div > div:nth-child(2) > div > div.col-sm-5.col-sm-offset-2.tile > div > div.buttons > a.btn.btn-primary",
            },
        ]

        return (
            sign_in + pick_sk_immigration + pick_stream + confirm_profile
            if initial
            else sign_in + continue_page
        )
