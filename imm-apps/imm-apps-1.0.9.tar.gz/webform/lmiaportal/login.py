from webform.models.definition import Action
from webform.models.lmiaprmodel import LMIAPrModel,LMIAHWSModel
from typing import Union
import base64

# This step includs actions of signing in, picking Skill Immigration automatically, select and confirm which stream to apply through
class Login:
    def __init__(
        self,
        lmia: Union[LMIAPrModel,LMIAHWSModel],
    ):
        self.lmia = lmia

    def encode(self, password):
        password_bytes = password.encode("ascii")
        base64_bytes = base64.b64encode(password_bytes)
        return base64_bytes.decode("ascii")

    def login(self,user_id,password,security_answers:object ):
        login_actions= [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Log in",
                "actions": [
                    {
                        "action_type": Action.GotoPage.value,
                        "url": "https://tfwp-jb.lmia.esdc.gc.ca/employer/",
                    },
                    {
                        "action_type": Action.Login.value,
                        "label": "Login",
                        "account": user_id,
                        "password": self.encode(password),
                        "account_element_id": "#loginForm\\:input-email",
                        "password_element_id": "#loginForm\\:input-password",
                        "login_button_id": "#loginForm\\:j_id_43",
                    },
                ],
                "id": None,  #
            }
        ]
        security_actions=[
            {
                "action_type": Action.WebPage.value,
                "page_name": "Security check",
                "actions": [
                    {
                        "action_type":Action.Security.value,
                        "portal":"lmiaportal",
                        "question_element_id":"#securityForm > fieldset > div > p",
                        "answer_element_id": "#securityForm\\:input-security-answer",
                        "continue_element_id": "#continueButton",
                        "security_answers":security_answers
                    }],
                "id":None,
            },
            {
                "action_type": Action.WebPage.value,
                "page_name": "Important message",
                "actions": [],
                "id":"#modal-accept"
            }
            ]

        return login_actions+security_actions
