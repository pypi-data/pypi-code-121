from webform.models.definition import Action
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from model.common.id import IDs
from model.common.phone import Phones
from model.common.address import Addresses
from webform.bcpnp.data import country_map
from typing import Union


class Register:
    def __init__(self, person: Union[BcpnpModelReg, BcpnpEEModelReg]):
        self.person = person

    def register(self):
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Create your profile",
                "actions": self.actions,
                "id": "#form > div.row > div > input",
            },
            {
                "action_type": Action.WebPage.value,
                "page_name": "Confirm your profile",
                "actions": [
                    {
                        "action_type": Action.Checkbox.value,
                        "label": "Confirm your information",
                        "id": "#fieldset-actions > div > div > label > input[type=checkbox]:nth-child(2)",
                    }
                ],
                "id": "#fieldset-actions > div > input.btn.btn-primary",
            },
        ]

    @property
    def gotoRegister(self):
        return [
            {
                "action_type": Action.GotoPage.value,
                "url": "https://www.pnpapplication.gov.bc.ca/user/register",
            }
        ]

    @property
    def login(self):
        return [
            {
                "action_type": Action.Input.value,
                "label": "Email address",
                "id": "#email",
                "value": self.person.personal.email,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Confirm Email address",
                "id": "#emailConfirmation",
                "value": self.person.personal.email,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "User ID",
                "id": "#userId",
                "value": self.person.personal.user_id,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Password",
                "id": "#pass",
                "value": self.person.personal.password,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Password confirmation",
                "id": "#passConfirmation",
                "value": self.person.personal.password,
                "required": True,
                "length": 100,
            },
        ]

    @property
    def security(self):
        actions = []
        question_answer_pairs = {
            "Your country": "China",
            "Your province": "Jiangsu",
            "Where is your city": "Nanjing",
        }
        i = 0
        for key, value in question_answer_pairs.items():
            # select q
            actions += [
                {
                    "action_type": Action.Select.value,
                    "label": f"Security questions {i}",
                    "value": "_other",
                    "id": f"#question{i}",
                }
            ]
            # own question
            actions += [
                {
                    "action_type": Action.Input.value,
                    "label": f"Enter your own question {i}",
                    "value": key,
                    "id": f"#questionOther{i}",
                    "required": True,
                    "length": 100,
                }
            ]
            # answer
            actions += [
                {
                    "action_type": Action.Input.value,
                    "label": f"Enter your answer {i}",
                    "value": value,
                    "id": f"#answer{i}",
                    "required": True,
                    "length": 100,
                }
            ]
            # wait for 2 seconds
            actions += [{"action_type": Action.Wait.value, "duration": 2000}]
            i += 1
        return actions

    @property
    def personal_info(self):
        name = [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "value": self.person.personal.last_name,
                "id": "#lastName",
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "value": self.person.personal.first_name,
                "id": "#firstName",
                "required": True,
                "length": 100,
            },
        ]

        has_used_name = [
            {
                "action_type": Action.Radio.value,
                "label": "Have you ever used any other name?",
                "id": "#form > fieldset:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(3) > label > input[type=radio]"
                if self.person.personal.used_first_name
                else "#otherNames",
            }
        ]

        used_name = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Used family name",
                    "value": self.person.personal.used_last_name,
                    "id": "#otherLastNames",
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Used given name",
                    "value": self.person.personal.used_first_name,
                    "id": "#otherFirstNames",
                    "required": True,
                    "length": 100,
                },
            ]
            if self.person.personal.used_first_name
            else []
        )

        dob = [
            {
                "action_type": Action.Input.value,
                "label": "Date of birth",
                "value": self.person.personal.dob.strftime("%Y-%m-%d"),
                "id": "#birthDate",
                "required": True,
                "length": 10,
            }
        ]

        birth_place = [
            {
                "action_type": Action.Select.value,
                "label": "Country of birth",
                "id": "#birthCountry",
                "value": country_map[self.person.personal.country_of_birth],
            },
            {
                "action_type": Action.Input.value,
                "label": "City of birth",
                "id": "#birthCity",
                "value": self.person.personal.place_of_birth,
            },
        ]

        gender = [
            {
                "action_type": Action.Select.value,
                "label": "Gender",
                "id": "#sex",
                "value": self.person.personal.sex,
            }
        ]

        return name + has_used_name + used_name + dob + birth_place + gender

    @property
    def passport(self):
        passport = IDs(self.person.personid).passport
        return [
            {
                "action_type": Action.Input.value,
                "label": "Passport number",
                "value": passport.number,
                "id": "#passportNo",
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Select.value,
                "label": "Passport country",
                "id": "#passportCountry",
                "value": passport.country,
            },
            {
                "action_type": Action.Input.value,
                "label": "Issue date",
                "value": passport.issue_date.strftime("%Y-%m-%d"),
                "id": "#passportIssueDate",
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Input.value,
                "label": "Date of passport expiry",
                "value": passport.expiry_date.strftime("%Y-%m-%d"),
                "id": "#passportExpiryDate",
                "required": True,
                "length": 10,
            },
        ]

    @property
    def contact(self):
        phone = Phones(self.person.phone).PreferredPhone
        return [
            {
                "action_type": Action.Input.value,
                "label": "Phone number",
                "value": str(phone.number),
                "id": "#phone",
                "required": True,
                "length": 100,
            }
        ]

    @property
    def address(self):
        address = Addresses(self.person.address).residential
        return [
            {
                "action_type": Action.Select.value,
                "label": "Country",
                "id": "#country",
                "value": country_map[address.country],
            },
            {
                "action_type": Action.Input.value,
                "label": "Address line",
                "value": address.line1,
                "id": "#addressLine",
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "City",
                "value": address.city,
                "id": "#city",
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Province",
                "value": address.province,
                "id": "#state",
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Postal code",
                "value": address.post_code,
                "id": "#postalCode",
                "required": True,
                "length": 100,
            },
        ]

    @property
    def additional(self):
        return [
            {
                "action_type": Action.Select.value,
                "label": "How did you learn about BCPNP",
                "id": "#bcpnpKnowledgeSource",
                "value": "CIC",
            }
        ]

    @property
    def continue_confirm(self):
        return [
            {
                "action_type": Action.Continue.value,
                "message": "Do you want to continue?",
            }
        ]

    @property
    def actions(self):
        return (
            self.gotoRegister
            + self.login
            + self.security
            + self.personal_info
            + self.passport
            + self.contact
            + self.address
            + self.additional
        )
