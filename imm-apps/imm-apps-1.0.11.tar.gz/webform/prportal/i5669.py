from audioop import add
from datetime import datetime
from webform.models.definition import Action, Role
from webform.models.prmodel import PrModel
from model.common.address import Addresses
from typing import List
from webform.models.prmodel import Family


class F5669:
    # dict of field ids
    fild_id = {
        "pa": {
            "last_name": "#familyName",
            "first_name": "#givenName",
            "native_fullname": "#nativeFullName",
            "dob": "#dob",
        },
        "dad": {
            "last_name": "#familyNameFather",
            "first_name": "#givenNameFather",
            "dob": "#sectionAFormFatherDOB",
            "death_date": "#sectionAFormFatherDeceasedDate",
            "city": "#sectionAFormFatherCityOfBirth",
            "country": "#sectionAFormFatherCountryOfBirth",
        },
        "mom": {
            "last_name": "#familyNameMother",
            "first_name": "#givenNameMother",
            "dob": "#sectionAFormMotherDOB",
            "death_date": "#sectionAFormMotherDeceasedDate",
            "city": "#sectionAFormMotherCityOfBirth",
            "country": "#sectionAFormMotherCountryOfBirth",
        },
    }

    def __init__(self, pa: PrModel, sp: PrModel | None, dps: List[PrModel]):
        self.pa = pa
        self.sp = sp
        self.dps = dps

    @property
    def pdf(self):
        return [{"action_type": Action.Pdf.value}]

    def goTo5669(self):
        return [
            {
                "action_type": "WebPage",
                "page_name": "Go to Imm5669 ",
                "actions": [],
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-imm5669 > pra-imm5669-start > pra-family-table > button",
                "id": "body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > pra-web-form-table > div > table > tbody > tr:nth-child(25) > td:nth-child(5) > button",
            }
        ]

    def add_family_member(self):
        return [
            {
                "action_type": "WebPage",
                "page_name": "Add new family member",
                "actions": [],
                "next_page_tag":"#sectionAFormMotherCountryOfBirth",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > pra-imm5669-start > pra-family-table > button",
            }
        ]

    def pick_whom(self, role):
        return [
            {
                "action_type": Action.Radio.value,
                "label": "Indicate whether you are filling out this form for",
                "id": "#principalApplicant" if role == Role.PA else "#principalOther",
            }
        ]

    def back2Application(self):
        return [
            {
                "action_type": "WebPage",
                "page_name": "Complete and return to application",
                "actions": [],
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-secondary",
            }
        ]

    def sectionABlockApplicant(self, person: PrModel):
        return [
            {
                "action_type": "Input",
                "label": "Family name",
                "value": person.personal.last_name,
                "id": F5669.fild_id["pa"]["last_name"],
                "length": 57,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Given name",
                "value": person.personal.first_name,
                "id": F5669.fild_id["pa"]["first_name"],
                "length": 57,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Full name",
                "value": person.personal.native_first_name
                + " "
                + person.personal.native_last_name,
                "id": F5669.fild_id["pa"]["native_fullname"],
                "length": 90,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Birth information",
                "value": person.personal.dob.strftime("%Y/%m/%d"),
                "id": F5669.fild_id["pa"]["dob"],
                "length": 10,
                "required": True,
            },
        ]

    def sectionABlock(self, relationship, family_member: Family):
        return [
            {
                "action_type": "Input",
                "label": "Family name",
                "value": family_member.last_name+"  "+family_member.native_last_name,
                "id": F5669.fild_id[relationship]["last_name"],
                "length": 57,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Given name",
                "value": family_member.first_name+"  "+family_member.native_first_name,
                "id": F5669.fild_id[relationship]["first_name"],
                "length": 57,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Date of birth",
                "value": family_member.date_of_birth.strftime("%Y/%m/%d"),
                "id": F5669.fild_id[relationship]["dob"],
                "length": 10,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Date of death",
                "value": family_member.date_of_death.strftime("%Y/%m/%d")
                if family_member.date_of_death
                else None,
                "id": F5669.fild_id[relationship]["death_date"],
                "length": 10,
                "required": False,
            },
            {
                "action_type": "Input",
                "label": "Town",
                "value": family_member.place_of_birth,
                "id": F5669.fild_id[relationship]["city"],
                "length": 31,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Town",
                "value": family_member.birth_country,
                "id": F5669.fild_id[relationship]["country"],
                "length": 31,
                "required": True,
            },
        ]

    def makeSectionB(self, person: PrModel):
        return [
            {
                "action_type": Action.Radio.value,
                "id": "#isConvictedInCanada_yes"
                if person.prbackground.q1
                else "#isConvictedInCanada_no",
                "label": "Yes" if person.prbackground.q1 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isConvictedOutsideCanada_yes"
                if person.prbackground.q2
                else "#isConvictedOutsideCanada_no",
                "label": "Yes" if person.prbackground.q2 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isClaimedRefugeeProtection_yes"
                if person.prbackground.q3
                else "#isClaimedRefugeeProtection_no",
                "label": "Yes" if person.prbackground.q3 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isConvictedInCanada_yes"
                if person.prbackground.q3
                else "#isConvictedInCanada_no",
                "label": "Yes" if person.prbackground.q3 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isRefusedRefugeeOrVisa_yes"
                if person.prbackground.q4
                else "#isRefusedRefugeeOrVisa_no",
                "label": "Yes" if person.prbackground.q4 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isOrderedToLeaveCountry_yes"
                if person.prbackground.q5
                else "#isOrderedToLeaveCountry_no",
                "label": "Yes" if person.prbackground.q5 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isWarCriminal_yes"
                if person.prbackground.q6
                else "#isWarCriminal_no",
                "label": "Yes" if person.prbackground.q6 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isCommittedActOfViolence_yes"
                if person.prbackground.q7
                else "#isCommittedActOfViolence_no",
                "label": "Yes" if person.prbackground.q7 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isAssociatedWithViolentGroup_yes"
                if person.prbackground.q8
                else "#isAssociatedWithViolentGroup_no",
                "label": "Yes" if person.prbackground.q8 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isMemberOfCriminalOrg_yes"
                if person.prbackground.q9
                else "#isMemberOfCriminalOrg_no",
                "label": "Yes" if person.prbackground.q9 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isDetainedOrJailed_yes"
                if person.prbackground.q10
                else "#isDetainedOrJailed_no",
                "label": "Yes" if person.prbackground.q10 else "No",
            },
            {
                "action_type": Action.Radio.value,
                "id": "#isPhysicalOrMentalDisorder_yes"
                if person.prbackground.q11
                else "#isPhysicalOrMentalDisorder_no",
                "label": "Yes" if person.prbackground.q11 else "No",
            },
            {
                "action_type": Action.Input.value,
                "id": "#additionalDetails",
                "label": "Explanation",
                "value": person.prbackground.details,
                "length": 679,
                "required": False,
            },
        ]

    def makeSectionC(self, person: PrModel):
        # education summary
        edu_summary = [
            {
                "action_type": Action.Input.value,
                "label": "Primary school years",
                "id": "#elementarySchoolYears",
                "value": str(person.personal.primary_school_years),
                "length": 2,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Secondary school years",
                "id": "#secondarySchoolYears",
                "value": str(person.personal.secondary_school_years),
                "length": 2,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "University school years",
                "id": "#universityAndCollegeYears",
                "value": str(person.personal.post_secondary_school_years),
                "length": 2,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Other school years",
                "id": "#otherSchoolYears",
                "value": str(person.personal.other_school_years),
                "length": 2,
                "required": True,
            },
        ]

        # loop each educaton
        value = []
        for index, edu in enumerate(person.education):
            if edu.end_date=='Present':edu.end_date=None
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from" + str(index),
                    "value": edu.start_date.strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#to" + str(index),
                    "value": edu.end_date.strftime("%Y/%m") if edu.end_date else None,
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "School name",
                    "id": "#nameOfInstitution" + str(index),
                    "value": edu.school_name,
                    "length": 24,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City and country",
                    "id": "#cityAndCountry" + str(index),
                    "value": edu.city + "/" + edu.country
                    if edu.city and edu.country
                    else None,
                    "length": 21,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Type of certificate",
                    "id": "#typeOfDiploma" + str(index),
                    "value": edu.education_level,
                    "length": 17,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Field of study",
                    "id": "#fieldOfStudy" + str(index),
                    "value": edu.field_of_study,
                    "length": 17,
                    "required": True,
                },
            ]
            value.append(block)

        return edu_summary + [
            {
                "action_type": Action.RepeatSection.value,
                "button_text": "Add another",
                "value": value,
            }
        ]

    def makeSectionD(self, person: PrModel):
        # loop each personal history
        value = []
        for index, history in enumerate(person.history):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from" + str(index),
                    "value": history.start_date.strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#to" + str(index),
                    "value": history.end_date.strftime("%Y/%m")
                    if history.end_date
                    else datetime.today().strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Activity",
                    "id": "#activity" + str(index),
                    "value": history.activity,
                    "length": 21,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City and country",
                    "id": "#cityAndCountry" + str(index),
                    "value": history.city_and_country,
                    "length": 62,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Status",
                    "id": "#status" + str(index),
                    "value": history.status,
                    "length": 14,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Name of employer or school",
                    "id": "#nameOfEmployerOrSchool" + str(index),
                    "value": history.name_of_company_or_school,
                    "length": 27,
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

    def makeSectionE(self, person: PrModel):
        # loop each political member history
        value = []
        for index, member in enumerate(person.member):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from" + str(index),
                    "value": member.start_date.strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#to" + str(index),
                    "value": member.end_date.strftime("%Y/%m")
                    if member.end_date
                    else datetime.today().strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Name of organization",
                    "id": "#nameOfOrganization" + str(index),
                    "value": member.organization_name,
                    "length": 17,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Type of organization",
                    "id": "#typeOfOrganization" + str(index),
                    "value": member.organization_type,
                    "length": 20,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Activity",
                    "id": "#activity" + str(index),
                    "value": member.position,
                    "length": 26,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City and country",
                    "id": "#cityAndCountry" + str(index),
                    "value": member.city + "/" + member.country,
                    "length": 17,
                    "required": True,
                },
            ]
            value.append(block)

        return (
            [
                {
                    "action_type": Action.RepeatSection.value,
                    "button_text": "Add another",
                    "value": value,
                }
            ]
            if len(person.member) > 0
            else [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from0",
                    "value": "None",
                    "length": 7,
                    "required": True,
                }
            ]
        )

    def makeSectionF(self, person: PrModel):
        # loop each government position
        value = []
        for index, government in enumerate(person.government):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#dateFrom" + str(index),
                    "value": government.start_date.strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#to" + str(index),
                    "value": government.end_date.strftime("%Y/%m")
                    if government.end_date
                    else datetime.today().strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Country",
                    "id": "#cityAndCountry" + str(index),
                    "value": government.country,
                    "length": 29,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Department",
                    "id": "#department" + str(index),
                    "value": government.department,
                    "length": 30,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Activity",
                    "id": "#activity" + str(index),
                    "value": government.position,
                    "length": 21,
                    "required": True,
                },
            ]
            value.append(block)

        return (
            [
                {
                    "action_type": Action.RepeatSection.value,
                    "button_text": "Add another",
                    "value": value,
                }
            ]
            if len(person.government) > 0
            else [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#dateFrom0",
                    "value": "None",
                    "length": 7,
                    "required": True,
                }
            ]
        )

    def makeSectionG(self, person: PrModel):
        # loop each military service
        value = []
        for index, military in enumerate(person.military):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "Country",
                    "id": "#country" + str(index),
                    "value": military.country,
                    "length": 30,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Branch",
                    "id": "#branchOfService" + str(index),
                    "value": military.service_detail,
                    "length": 64,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from" + str(index),
                    "value": military.start_date.strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#to" + str(index),
                    "value": military.end_date.strftime("%Y/%m")
                    if military.end_date
                    else datetime.today().strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Rank",
                    "id": "#rank" + str(index),
                    "value": military.rank,
                    "length": 14,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Reaons for end of service",
                    "id": "#reasonsEndService" + str(index),
                    "value": military.rank,
                    "length": 200,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Combat details",
                    "id": "#combatDetails" + str(index),
                    "value": military.combat_detail,
                    "length": 679,
                    "required": True,
                },
            ]
            value.append(block)

        return (
            [
                {
                    "action_type": Action.RepeatSection.value,
                    "button_text": "Add another",
                    "value": value,
                }
            ]
            if len(person.military) > 0
            else [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from0",
                    "value": "None",
                    "length": 7,
                    "required": True,
                }
            ]
        )

    def makeSectionH(self, person: PrModel):
        # loop each military service
        value = []
        for index, address in enumerate(person.addresshistory):
            block = [
                {
                    "action_type": Action.Input.value,
                    "label": "From",
                    "id": "#from" + str(index),
                    "value": address.start_date.strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "To",
                    "id": "#to" + str(index),
                    "value": address.end_date.strftime("%Y/%m")
                    if address.end_date
                    else datetime.today().strftime("%Y/%m"),
                    "length": 7,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Street and number",
                    "id": "#street" + str(index),
                    "value": address.street_and_number,
                    "length": 30,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "City",
                    "id": "#city" + str(index),
                    "value": address.city,
                    "length": 14,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Province",
                    "id": "#provinceOrState" + str(index),
                    "value": address.province,
                    "length": 14,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Country",
                    "id": "#country" + str(index),
                    "value": address.country,
                    "length": 14,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Post code",
                    "id": "#postalCode" + str(index),
                    "value": address.post_code,
                    "length": 9,
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

    def sectionA(self, person: PrModel, role):
        applicant = self.sectionABlockApplicant(person)

        father_obj = [
            person
            for person in person.family
            if person.relationship.lower() == "father"
        ]
        mother_obj = [
            person
            for person in person.family
            if person.relationship.lower() == "mother"
        ]
        father = self.sectionABlock("dad", father_obj[0]) if father_obj else []
        mother = self.sectionABlock("mom", mother_obj[0]) if mother_obj else []
        whom = []
        match role:
            case Role.PA:
                whom = self.pick_whom(role=Role.PA)
            case Role.SP:
                whom = self.pick_whom(role=Role.SP)
            case Role.DP:
                whom = self.pick_whom(role=Role.DP)

        actions = whom + applicant + father + mother + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section A: Personal details",
                "actions": actions,
                "next_page_tag":"#isPhysicalOrMentalDisorder_no",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionB(self, person: PrModel):
        actions = self.makeSectionB(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section B: Questionarie",
                "actions": actions,
                "next_page_tag":"#fieldOfStudy0",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionC(self, person: PrModel):
        actions = self.makeSectionC(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section C: Education",
                "actions": actions,
                "next_page_tag":"#nameOfEmployerOrSchool0",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionD(self, person: PrModel):
        actions = self.makeSectionD(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section D: Personal history",
                "actions": actions,
                "next_page_tag":"#activities0",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionE(self, person: PrModel):
        actions = self.makeSectionE(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section E: Membership and association with organization",
                "actions": actions,
                "next_page_tag":"#department0",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionF(self, person: PrModel):
        actions = self.makeSectionF(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section F: Government positions",
                "actions": actions,
                "next_page_tag":"#combatDetails0",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionG(self, person: PrModel):
        actions = self.makeSectionG(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section G: Military and paramilitary service",
                "actions": actions,
                "next_page_tag":"#postalCode0",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def sectionH(self, person: PrModel):
        actions = self.makeSectionH(person) + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Section H: Addresses",
                "actions": actions,
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-imm5669 > pra-imm5669-start > pra-family-table > button",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm5669 > lib-navigation-buttons > div > button.btn.btn-primary",
            }
        ]

    def fill(self):
        pa_form = (
            self.add_family_member()
            + self.sectionA(self.pa, role=Role.PA)
            + self.sectionB(self.pa)
            + self.sectionC(self.pa)
            + self.sectionD(self.pa)
            + self.sectionE(self.pa)
            + self.sectionF(self.pa)
            + self.sectionG(self.pa)
            + self.sectionH(self.pa)
        )
        sp_form = (
            self.add_family_member()
            + self.sectionA(self.sp, role=Role.SP)
            + self.sectionB(self.sp)
            + self.sectionC(self.sp)
            + self.sectionD(self.sp)
            + self.sectionE(self.sp)
            + self.sectionF(self.sp)
            + self.sectionG(self.sp)
            + self.sectionH(self.sp)
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
                    + self.sectionD(dp)
                    + self.sectionE(dp)
                    + self.sectionF(dp)
                    + self.sectionG(dp)
                    + self.sectionH(dp)
                )

        return self.goTo5669() + pa_form + sp_form + dp_forms + self.back2Application()
