from webform.models.definition import Action, Role
from webform.models.prmodel import PrModel
from model.common.address import Addresses
from typing import List
from webform.models.prmodel import Family


class F5406:
    # map of input and output marital status
    marital_map = {
        "Annulled Marriage": "1: 09",
        "Common-Law": "2: 03",
        "Divorced": "3: 04",
        "Married": "5: 01",
        "Separated": "4: 05",
        "Single": "7: 02",
        "Unknown": "9: 00",
        "Widowed": "8: 06",
    }
    # dict of field ids
    fild_id = {
        "pa": {
            "fn": "#applicantFullName",
            "dob": "#applicantDOB",
            "birth_place": "#applicantBirthplace",
            "marital_status": "#applicantMaritalStatus",
            "email": "#applicantEmail",
            "address": "#applicantAddress",
        },
        "sp": {
            "fn": "#partnerFullName",
            "dob": "#partnerDOB",
            "birth_place": "#partnerBirthplace",
            "marital_status": "#partnerMaritalStatus",
            "email": "#partnerEmail",
            "address": "#partnerAddress",
        },
        "mom": {
            "fn": "#motherFullName",
            "dob": "#motherDOB",
            "birth_place": "#motherBirthplace",
            "marital_status": "#motherMaritalStatus",
            "email": "#motherEmail",
            "address": "#motherAddress",
        },
        "dad": {
            "fn": "#fatherFullName",
            "dob": "#fatherDOB",
            "birth_place": "#fatherBirthplace",
            "marital_status": "#fatherMaritalStatus",
            "email": "#fatherEmail",
            "address": "#fatherAddress",
        },
    }

    def __init__(self, pa: PrModel, sp: PrModel | None, dps: List[PrModel]):
        self.pa = pa
        self.sp = sp
        self.dps = dps

    @property
    def pdf(self):
        return [{"action_type": Action.Pdf.value}]

    def goTo5406(self):
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Start/Edit for 5406 form",
                "actions": [],
                "id": "body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > pra-web-form-table > div > table > tbody > tr:nth-child(13) > td:nth-child(5) > button",
            }
        ]

    def add_family_member(self):
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Add new family member",
                "actions": [],
                "next_page_tag":"#fatherAddress",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5406 > pra-imm5406-start > pra-family-table > button",
            }
        ]

    def pick_whom(self, role):
        return [
            {
                "action_type": Action.Radio.value,
                "label": "Indicate whether you are filling out this form for",
                "id": "#principalAppYes" if role == Role.PA else "#principalAppNo",
            }
        ]

    def completeReturn(self):
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Complete and return to application",
                "actions": [],
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > div.intake-landing-page_submit-application.ng-star-inserted > button",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5406 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionABlock(
        self, relationship, person: PrModel = None, family_member: Family = None
    ):
        return [
            {
                "action_type": "Input",
                "label": "Full name",
                "value": person.personal.first_name + " " + person.personal.last_name +" / "+person.personal.native_first_name+" "+person.personal.native_last_name
                if person
                else family_member.first_name + " " + family_member.last_name+" / "+family_member.native_first_name+"  "+family_member.native_last_name,
                "id": F5406.fild_id[relationship]["fn"],
                "length": 63,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Date of birth",
                "value": person.personal.dob.strftime("%Y/%m/%d")
                if person
                else family_member.date_of_birth.strftime("%Y/%m/%d"),
                "id": F5406.fild_id[relationship]["dob"],
                "length": 11,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Country or territory of birth",
                "value": person.personal.country_of_birth
                + "/"
                + person.personal.place_of_birth
                if person
                else family_member.birth_country + "/" + family_member.place_of_birth,
                "id": F5406.fild_id[relationship]["birth_place"],
                "length": 30,
                "required": True,
            },
            {
                "action_type": "Select",
                "label": "Marital status",
                "value": F5406.marital_map[person.marriage.marital_status]
                if person
                else F5406.marital_map[family_member.marital_status],
                "id": F5406.fild_id[relationship]["marital_status"],
            },
            {
                "action_type": "Input",
                "label": "Email",
                "value": person.personal.email if person else family_member.email,
                "id": F5406.fild_id[relationship]["email"],
                "length": 40,
                "required": False,
            },
            {
                "action_type": "Input",
                "label": "Address",
                "value": Addresses(person.address).residential
                if person
                else family_member.address,
                "id": F5406.fild_id[relationship]["address"],
                "length": 80,
                "required": True,
            },
        ]

    def makeSectionB(self, children: List[Family]):
        value = []

        for index, child in enumerate(children):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "Relationship",
                    "id": "#relationship" + str(index),
                    "value": child.relationship,
                    "length": 27,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Full name",
                    "id": "#fullName" + str(index),
                    "value": child.first_name + " " + child.last_name+" / "+child.native_first_name+" "+child.native_last_name,
                    "length": 63,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Date of birth",
                    "id": "#dob" + str(index),
                    "value": child.date_of_birth.strftime("%Y/%m/%d"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Country",
                    "id": "#countryOfBirth" + str(index),
                    "value": child.birth_country + "/" + child.place_of_birth,
                    "length": 30,
                    "required": True,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Maritial status",
                    "id": "#maritalStatus" + str(index),
                    "value": F5406.marital_map[child.marital_status],
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Email",
                    "id": "#emailAddress" + str(index),
                    "value": child.email,
                    "length": 40,
                    "required": False,
                },
                {
                    "action_type": Action.Areatext.value,
                    "label": "Address",
                    "id": "#address" + str(index),
                    "value": child.address,
                    "length": 80,
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
        ]

    def makeSectionC(self, siblings: List[Family]):
        value = []

        for index, sibling in enumerate(siblings):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "Relationship",
                    "id": "#relationship" + str(index),
                    "value": sibling.relationship,
                    "length": 27,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Full name",
                    "id": "#fullName" + str(index),
                    "value": sibling.first_name + " " + sibling.last_name+" /  "+sibling.native_first_name+" "+sibling.native_last_name,
                    "length": 63,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Date of birth",
                    "id": "#dob" + str(index),
                    "value": sibling.date_of_birth.strftime("%Y/%m/%d"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Country",
                    "id": "#countryOfBirth" + str(index),
                    "value": sibling.birth_country + "/" + sibling.place_of_birth,
                    "length": 30,
                    "required": True,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Maritial status",
                    "id": "#maritalStatus" + str(index),
                    "value": F5406.marital_map[sibling.marital_status],
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Email",
                    "id": "#emailAddress" + str(index),
                    "value": sibling.email,
                    "length": 40,
                    "required": False,
                },
                {
                    "action_type": Action.Areatext.value,
                    "label": "Address",
                    "id": "#address" + str(index),
                    "value": sibling.address,
                    "length": 80,
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
        ] if len(siblings)>0 else []

    def sectionA(self, person: PrModel, role):
        applicant = self.sectionABlock("pa", person=person)

        # spouse = self.sectionABlock("sp", self.sp) if self.sp else []
        spouse_obj=[person for person in person.family if person.relationship.lower()=="spouse"]
        mother_obj = [
            person
            for person in person.family
            if person.relationship.lower() == "mother"
        ]
        father_obj = [
            person
            for person in person.family
            if person.relationship.lower() == "father"
        ]
        spouse=self.sectionABlock("sp",family_member=spouse_obj[0]) if spouse_obj else []
        mother = (
            self.sectionABlock("mom", family_member=mother_obj[0]) if mother_obj else []
        )
        father = (
            self.sectionABlock("dad", family_member=father_obj[0]) if father_obj else []
        )
        whom = []
        match role:
            case Role.PA:
                whom = self.pick_whom(Role.PA)
            case Role.SP:
                whom = self.pick_whom(Role.SP)
            case Role.DP:
                whom = self.pick_whom(Role.DP)
        actions = whom + applicant + spouse + mother + father + self.pdf
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Imm5406 additional family information Section A",
                "actions": actions,
                "next_page_tag":"#address0",
                "screen_shoot":{
                    "format":"Pdf",
                    "wait_for":"#fatherAddress"
                },
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5406 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionB(self, person: PrModel):
        children = [p for p in person.family if p.relationship in ["Daughter", "Son"]]
        actions = self.makeSectionB(children) + self.pdf
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Imm5406 additional family information Section B: Children",
                "actions": actions,
                "next_page_tag":"#emailAddress0",
                "screen_shoot":{
                    "format":"Pdf",
                    "wait_for":"#address0"
                },
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5406 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionC(self, person: PrModel):
        siblings = [p for p in person.family if p.relationship in ["Brother", "Sister"]]
        actions = self.makeSectionC(siblings) + self.pdf
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Imm5406 additional family information Section C: Siblings",
                "actions": actions,
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-imm5406 > lib-navigation-buttons > div > button.btn.btn-primary",
                "screen_shoot":{
                    "format":"Pdf",
                    "wait_for":"#address1"
                },
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5406 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def fill(self):
        pa_form = (
            self.add_family_member()
            + self.sectionA(self.pa, role=Role.PA)
            + self.sectionB(self.pa)
            + self.sectionC(self.pa)
        )
        sp_form = (
            self.add_family_member()
            + self.sectionA(self.sp, role=Role.SP)
            + self.sectionB(self.sp)
            + self.sectionC(self.sp)
            if self.sp
            else []
        )
        dp_forms = []
        for dp in self.dps:
            if dp.personal.age >= 18:
                dp_forms += (
                    self.add_family_member()
                    + self.sectionA(dp, role=Role.DP)
                    + self.sectionB(dp)
                    + self.sectionC(dp)
                )

        return self.goTo5406() + pa_form + sp_form + dp_forms + self.completeReturn()
