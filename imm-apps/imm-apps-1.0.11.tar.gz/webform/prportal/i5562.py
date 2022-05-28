from webform.models.definition import Action, Role
from webform.models.prmodel import PrModel
from typing import List


class F5562:
    def __init__(self, pa: PrModel, sp: PrModel | None, dps: List[PrModel]):
        self.pa = pa
        self.sp = sp
        self.dps = dps

    @property
    def pdf(self):
        return [{"action_type": Action.Pdf.value}]

    def didNotTravel(self, value):
        return [
            {
                "action_type": "Checkbox",
                "label": "Did not travel",
                "id": "#haveNotTravelled",
                "value": value,
            }
        ]

    def goTo5562(self):
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Start/Edit for 5562 form",
                "actions": [],
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-imm5562 > lib-navigation-buttons > div > button.btn.btn-primary",
                "id": "body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > pra-web-form-table > div > table > tbody > tr:nth-child(22) > td:nth-child(5) > button",
            },
            {
                "action_type": Action.WebPage.value,
                "page_name": "Continue for 5562 form",
                "actions": [],
                "next_page_tag":"#haveNotTravelled",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5562 > lib-navigation-buttons > div > button.btn.btn-primary",
            },
        ]

    def makeContentPaSp(self, role):
        value = []
        destination_id = {
            Role.PA: "#trip-destination-",
            Role.SP: "#sectionB-destination-",
        }
        person_obj = self.pa if role == Role.PA else self.sp

        for index, t in enumerate(person_obj.travel):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#trip-from-" + str(index),
                    "value": t.start_date.strftime("%Y/%m"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#trip-to-" + str(index),
                    "value": t.end_date.strftime("%Y/%m"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Destination",
                    "id": destination_id[role] + str(index),
                    "value": t.destination,
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Length",
                    "id": "#trip-length-" + str(index),
                    "value": str(t.length),
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Purpose of travel",
                    "id": "#trip-purpose-" + str(index),
                    "value": t.purpose,
                    "length": 100,
                    "required": True,
                },
            ]
            value.append(block)
        return [
            {
                "action_type": Action.RepeatSection.value,
                "button_text": "Add another",
                "value": value,
            }
        ] + self.pdf

    def makeContentDp(self, dp: PrModel, start_index=0):
        value = []

        for index, t in enumerate(dp.travel):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "Given name",
                    "id": "#trip-givenName-" + str(index + start_index),
                    "value": dp.personal.first_name+" "+dp.personal.native_first_name,
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#trip-from-" + str(index + start_index),
                    "value": t.start_date.strftime("%Y/%m"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#trip-to-" + str(index + start_index),
                    "value": t.end_date.strftime("%Y/%m"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Destination",
                    "id": "#sectionC-destination-" + str(index + start_index),
                    "value": t.destination,
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Length",
                    "id": "#trip-length-" + str(index + start_index),
                    "value": str(t.length),
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Purpose of travel",
                    "id": "#trip-purpose-" + str(index + start_index),
                    "value": t.purpose,
                    "length": 100,
                    "required": True,
                },
            ]
            value.append(block)
        return value

    def makeFormDps(self):
        start_index = 0
        values = []
        for dp in self.dps:
            values += self.makeContentDp(dp, start_index)
            start_index += len(dp.travel)

        actions = (
            self.didNotTravel(False)
            + [
                {
                    "action_type": Action.RepeatSection.value,
                    "button_text": "Add another",
                    "value": values,
                },
            ]
            + self.pdf
            if len(values) > 0
            else self.didNotTravel(True) + self.pdf
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Imm5562 page 4 for dependants",
                "actions": actions,
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > div.intake-landing-page_submit-application.ng-star-inserted > button",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5562 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def makeFormPaSp(self):
        # make pa form
        pa = [
            {
                "action_type": Action.Input.value,
                "label": "Your family name",
                "value": self.pa.personal.last_name+"  "+self.pa.personal.native_last_name,
                "id": "#familyName",
                "length": 100,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Your given name",
                "value": self.pa.personal.first_name+" "+self.pa.personal.native_first_name,
                "id": "#givenName",
                "length": 100,
                "required": True,
            },
        ]
        if len(self.pa.travel) > 0:
            pa_travel_content = (
                self.didNotTravel(False) + pa + self.makeContentPaSp(Role.PA)
            )
        else:
            pa_travel_content = self.didNotTravel(True)
        # make sp form
        if self.sp and len(self.sp.travel) > 0:
            sp_travel_content = self.didNotTravel(False) + self.makeContentPaSp(Role.SP)
        else:
            sp_travel_content = self.didNotTravel(True)

        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Imm5562 page 2 for principal applicant",
                "actions": pa_travel_content,
                "next_page_tag":"#haveNotTravelled",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5562 > lib-navigation-buttons > div > button.btn.btn-primary",
            },
            {
                "action_type": Action.WebPage.value,
                "page_name": "Imm5562 page 3 for spouse",
                "actions": sp_travel_content,
                "next_page_tag":"#haveNotTravelled",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5562 > lib-navigation-buttons > div > button.btn.btn-primary",
            },
        ]

    def fill(self):
        return self.goTo5562() + self.makeFormPaSp() + self.makeFormDps()
