from webform.models.definition import Action, Role
from webform.models.prmodel import PrModel
from model.common.address import Addresses
from model.common.phone import Phones
from model.common.id import IDs
from model.common.educationbase import EducationHistory
from typing import List
from webform.prportal.data.d0008 import *
from webform.prportal.data.citizen import citizen
from webform.prportal.data.country_birth import country_birth
from webform.prportal.data.country_residence import country_residence
from webform.models.prmodel import CORs


class F0008:
    def __init__(self, pa: PrModel, sp: PrModel | None, dps: List[PrModel]):
        self.pa = pa
        self.sp = sp
        self.dps = dps

    @property
    def pdf(self):
        return [{"action_type": Action.Pdf.value}]

    def goTo0008(self):
        return [
            {
                "action_type": "WebPage",
                "page_name": "Start/Edit for 0008 form",
                "actions": [],
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-imm0008-page1 > div > a.btn.btn-primary",
                "id": "body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > pra-web-form-table > div > table > tbody > tr:nth-child(1) > td:nth-child(5) > button",
            },
            {
                "action_type": "WebPage",
                "page_name": "Start/Edit for 0008 form, Continue",
                "actions": [],
                "next_page_tag":"#city",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm0008-page1 > div > a.btn.btn-primary",
            },
        ]

    def saveContinue(self, page):
        return f"body > pra-root > pra-localized-app > main > div > pra-imm0008-page{page} > div > button"

    def saveContinueDep(self):
        return "body > pra-root > pra-localized-app > main > div > pra-imm0008-dependant > div.buttons-container > button"

    def saveContinueDep1(self):
        return "body > pra-root > pra-localized-app > main > div > pra-imm0008-dependant > div.buttons-container > button.btn.btn-primary.ng-star-inserted"

    def completeBack(self):
        return [
            {
                "action_type": "WebPage",
                "page_name": "Complete and return to application",
                "actions": [],
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm0008 > lib-navigation-buttons > div > button.btn.btn-secondary",
            }
        ]

    # page 2 application details
    def applicationDetails(self):
        actions = [
            {
                "action_type": "Select",
                "label": "Correspondence",
                "value": english_french_map[self.pa.prcase.communication_language],
                "id": "#correspondence",
            },
            {
                "action_type": "Select",
                "label": "Interview",
                "value": all_languages[self.pa.prcase.interview_language],
                "id": "#interview",
            },
            {
                "action_type": "Select",
                "label": "Interpreter requested",
                "value": interpreter_map["Yes"]
                if self.pa.prcase.need_translator
                else interpreter_map["No"],
                "id": "#interpreterRequested",
            },
            {
                "action_type": "Select",
                "label": "Province",
                "value": province_map[self.pa.prcase.intended_province],
                "id": "#province",
            },
            {
                "action_type": "Select",
                "label": "City",
                "value": city_map[self.pa.prcase.intended_province][
                    self.pa.prcase.intended_city
                ],
                "id": "#city",
            },
        ] + self.pdf
        return [
            {
                "action_type": "WebPage",
                "page_name": "Application details",
                "actions": actions,
                "next_page_tag":"#personalDetailsForm-previouslyMarriedOrCommonLaw-no",
                "id": self.saveContinue(2),
            }
        ]

    # page 3 personal details
    def makePreviousCOR(self,person):
        value = []
        cor = person.cor
        cor.pop(0)  # the first line is current cor
        for index, c in enumerate(cor):
            block = [
                {
                    "action_type": "Select",
                    "label": "Country",
                    "value": country_residence[c.country],
                    "id": "#personalDetailsForm-prevCountry" + str(index),
                },
                {
                    "action_type": "Select",
                    "label": "Immigration status",
                    "value": immigration_status[c.status],
                    "id": "#personalDetailsForm-prevImmigrationStatus" + str(index),
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Start date",
                    "id": "#personalDetailsForm-prevStartDateOfImmigrationStatus"
                    + str(index),
                    "value": c.start_date.strftime("%Y/%m/%d"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "End date",
                    "id": "#personalDetailsForm-prevEndDateOfImmigrationStatus"
                    + str(index),
                    "value": c.end_date.strftime("%Y/%m/%d"),
                    "length": 10,
                    "required": True,
                },
            ]
            other = [
                {
                    "action_type": Action.Input.value,
                    "label": "Other explanation",
                    "id": "#personalDetailsForm-prevOtherImmigrationStatus"
                    + str(index),
                    "value": c.explanation,
                    "length": 30,
                    "required": True,
                }
            ]
            block = block + other if c.status == "Other" else block
            value.append(block)
        return [
            {
                "action_type": Action.RepeatSection.value,
                "button_text": "Add another",
                "value": value[0:2],  # max is 2
            }
        ]

    # page 3 personal details
    def personalDetails(self, person: PrModel, role: Role):
        relationship2pa = {
            "action_type": "Select",
            "label": "Relationship",
            "value": relationship_to_pa[person.personal.relationship_to_pa]
            if person.personal.relationship_to_pa
            else None,
            "id": "#dependantDetailsForm-relationshipToPA",
            "delay":1500
        }
        sp_dp = (
            [
                {
                    "action_type": "Radio",
                    "label": "Accompany to Canada",
                    "id": "#dependantDetailsForm-accompanyingPA-yes"
                    if person.personal.accompany_to_canada
                    else "#dependantDetailsForm-accompanyingPA-no"
                    
                },
                relationship2pa,
            ]
            if role != Role.PA
            else []
        )

        dependant_type_set = (
            [
                {
                    "action_type": "Select",
                    "label": "Dependant type",
                    "value": dependant_type[person.personal.dependant_type]
                    if person.personal.dependant_type
                    else None,
                    "id": "#dependantDetailsForm-dependantType",
                }
            ]
            if role != Role.PA
            and person.personal.relationship_to_pa
            in [
                "Adopted Child",
                "Child",
                "Grandchild",
                "Step-Child",
                "Step-Grandchild",
                "Parent",
                "Adoptive Parent",
            ]
            else []
        )

        dependant_type_set = (
            [
                dependant_type_set[0]
            ]
            if dependant_type_set
            else []
        )  # 如果是spouse，common-law则没有后续选择
        dependant_type_set = (
            dependant_type_set if role != Role.PA else []
        )  # 如果是PA， 则没有dependant_type_set

        name = [
            {
                "action_type": "Input",
                "label": "Family name",
                "value": person.personal.last_name,
                "id": "#personalDetailsForm-familyName",
                "length": 100,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Given name",
                "value": person.personal.first_name,
                "id": "#personalDetailsForm-givenName",
                "length": 100,
                "required": True,
            },
        ]
        has_used_name = True if person.personal.used_first_name else False
        used_name = [
            {
                "action_type": "Radio",
                "label": "Have used name?",
                "value": has_used_name,
                "id": "#personalDetailsForm-usedOtherName-yes"
                if has_used_name
                else "#personalDetailsForm-usedOtherName-no",
            }
        ]
        used_name += (
            [
                {
                    "action_type": "Input",
                    "label": "Used family name",
                    "value": person.personal.used_last_name,
                    "id": "#personalDetailsForm-otherFamilyName",
                    "length": 100,
                    "required": True,
                },
                {
                    "action_type": "Input",
                    "label": "Used given name",
                    "value": person.personal.used_first_name,
                    "id": "#personalDetailsForm-otherGivenName",
                    "length": 100,
                    "required": True,
                },
            ]
            if has_used_name
            else []
        )
        uci = [
            {
                "action_type": "Input",
                "label": "UCI",
                "value": person.personal.uci,
                "id": "#personalDetailsForm-uci",
                "length": 100,
                "required": False,
            }
        ]
        physical_characteristics = [
            {
                "action_type": "Select",
                "label": "Sex",
                "value": sex_map[person.personal.sex],
                "id": "#personalDetailsForm-sex",
            },
            {
                "action_type": "Select",
                "label": "Eye color",
                "value": eye_color[person.personal.eye_color],
                "id": "#personalDetailsForm-eyeColour",
            },
            {
                "action_type": "Input",
                "label": "Height",
                "value": str(person.personal.height),
                "id": "#personalDetailsForm-heightInCM",
                "length": 3,
                "required": True,
            },
        ]
        birth_info = [
            {
                "action_type": "Input",
                "label": "DOB",
                "value": person.personal.dob.strftime("%Y/%m/%d"),
                "id": "#personalDetailsForm-dob",
                "length": 10,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Place of birth",
                "value": person.personal.place_of_birth,
                "id": "#personalDetailsForm-cityOfBirth",
                "length": 30,
                "required": True,
            },
            {
                "action_type": "Select",
                "label": "Country of birth",
                "value": country_birth[person.personal.country_of_birth],
                "id": "#personalDetailsForm-countryOfBirth",
            },
        ]
        citizens = [
            {
                "action_type": "Select",
                "label": "Citizen 1",
                "value": citizen[person.personal.citizen],
                "id": "#personalDetailsForm-citizenship1",
            },
            {
                "action_type": "Select",
                "label": "Citizen 2",
                "value": citizen[person.personal.citizen2]
                if person.personal.citizen2
                else None,
                "id": "#personalDetailsForm-citizenship2",
            },
        ]
        ccor = CORs(person.cor).current
        current_cor = [
            {
                "action_type": "Select",
                "label": "Current country of residence",
                "value": country_residence[ccor.country],
                "id": "#personalDetailsForm-currentCountry",
            },
            {
                "action_type": "Select",
                "label": "Status",
                "value": immigration_status[ccor.status],
                "id": "#personalDetailsForm-immigrationStatus",
            },
        ]
        ccor_period = [
            {
                "action_type": "Input",
                "label": "From",
                "value": ccor.start_date.strftime("%Y/%m/%d"),
                "id": "#personalDetailsForm-startDateofImmigrationStatus",
                "length": 10,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "To",
                "value": ccor.end_date.strftime("%Y/%m/%d"),
                "id": "#personalDetailsForm-endDateOfImmigrationStatus",
                "length": 10,
                "required": True,
            },
        ]
        last_entry = [
            {
                "action_type": "Input",
                "label": "Date of last entry",
                "value": person.personal.last_entry_date.strftime("%Y/%m/%d")
                if person.personal.last_entry_date
                else None,
                "id": "#personalDetailsForm-dateOfLastEntry",
                "length": 10,
                "required": True,
            },
            {
                "action_type": "Input",
                "label": "Place of last entry",
                "value": person.personal.last_entry_place,
                "id": "#personalDetailsForm-placeOfLastEntry",
                "length": 30,
                "required": True,
            },
        ]
        other = [
            {
                "action_type": "Input",
                "label": "details",
                "value": person.personal.other_explanation,
                "id": "#personalDetailsForm-otherImmigrationStatus",
                "length": 30,
                "required": True,
            }
        ]

        match ccor.status:
            case "Citizen" | "Permanent Resident":
                current_cor += last_entry if ccor.country == "Canada" else current_cor
            case "Worker" | "Student" | "Visitor":
                current_cor += (
                    ccor_period + last_entry
                    if ccor.country == "Canada"
                    else ccor_period
                )
            case "Refugess":
                current_cor += last_entry if ccor.country == "Canada" else current_cor
            case "Other":
                current_cor += (
                    ccor_period + other + last_entry
                    if ccor.country == "Canada"
                    else ccor_period + other
                )

        has_previous_cor = True if len(person.cor) > 1 else False
        previous_cor = [
            {
                "action_type": "Radio",
                "label": "Previous countries of residence",
                "id": "#personalDetailsForm-hasPreviousCountries-yes"
                if has_previous_cor
                else "#personalDetailsForm-hasPreviousCountries-no",
            }
        ]
        previous_cor = (
            previous_cor + self.makePreviousCOR(person) if has_previous_cor else previous_cor
        )
        # marriage
        marital_status = [
            {
                "action_type": "Select",
                "label": "Current marital status",
                "value": current_marital_status[person.marriage.marital_status],
                "id": "#personalDetailsForm-maritalStatus",
            }
        ]
        married_date = [
            {
                "action_type": Action.Input.value,
                "label": "Married date",
                "id": "#personalDetailsForm-dateOfMarriageOrCommonLaw",
                "value": person.marriage.married_date.strftime("%Y/%m/%d")
                if person.marriage.married_date
                else None,
                "length": 10,
                "required": True,
            }
        ]
        spouse_name = [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": "#personalDetailsForm-familyNameOfSpouse",
                "value": person.marriage.sp_last_name,
                "length": 100,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": "#personalDetailsForm-givenNameOfSpouse",
                "value": person.marriage.sp_first_name,
                "length": 100,
                "required": True,
            },
        ]
        match person.marriage.marital_status:
            case "Annulled Marriage" | "Divorced" | "Separated" | "Single" | "Unknown" | "Widowed":
                pass
            case "Common-Law" | "Married":
                marital_status += married_date + spouse_name
        # previous marriage
        has_pre_marriage = [
            {
                "action_type": "Radio",
                "label": "Has previous marriage",
                "id": "#personalDetailsForm-previouslyMarriedOrCommonLaw-yes"
                if person.marriage.previous_married
                else "#personalDetailsForm-previouslyMarriedOrCommonLaw-no",
            }
        ]
        
        pre_spouse_dob=[{
                "action_type": Action.Input.value,
                "label": "Date of birth",
                "id": "#previousRelationshipForm-previousSpouseDob",
                "value": person.marriage.pre_sp_dob.strftime("%Y/%m/%d")
                if person.marriage.pre_sp_dob
                else None,
                "length": 10,
                "required": True,
            }] if role==Role.PA else []
        
        pre_marriage = [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": "#previousRelationshipForm-previousSpouseFamilyName",
                "value": person.marriage.pre_sp_last_name,
                "length": 100,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": "#previousRelationshipForm-previousSpouseGivenName",
                "value": person.marriage.pre_sp_first_name,
                "length": 100,
                "required": True,
            },
            *pre_spouse_dob,
            {
                "action_type": "Select",
                "label": "Type of relationship",
                "value": previous_marital_status[person.marriage.pre_relationship_type]
                if person.marriage.pre_relationship_type
                else None,
                "id": "#previousRelationshipForm-typeOfRelationship",
            },
            {
                "action_type": Action.Input.value,
                "label": "Start date of relationship",
                "id": "#previousRelationshipForm-startDateofRelationship",
                "value": person.marriage.pre_start_date.strftime("%Y/%m/%d")
                if person.marriage.pre_start_date
                else None,
                "length": 10,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "End date of relationship",
                "id": "#previousRelationshipForm-endDateOfRelationship",
                "value": person.marriage.pre_end_date.strftime("%Y/%m/%d")
                if person.marriage.pre_end_date
                else None,
                "length": 10,
                "required": True,
            },
        ]
        has_pre_marriage += pre_marriage if person.marriage.previous_married else []
        # summary
        save_continue_id = (
            self.saveContinue(3) if role == Role.PA else self.saveContinueDep()
        )

        actions = (
            sp_dp
            + dependant_type_set
            + name
            + used_name
            + uci
            + physical_characteristics
            + birth_info
            + citizens
            + current_cor
            + previous_cor
            + marital_status
            + has_pre_marriage
            + self.pdf
        )
        return [
            {
                "action_type": "WebPage",
                "page_name": "Page 3 personal details"
                if role == Role.PA
                else "Dependant personal details",
                "actions": actions,
                "next_page_tag":"#contactNo" if role==Role.PA else "#intendedOccupation",
                "id": save_continue_id,
            }
        ]

    def makeAddress(self, address, type):
        types = {
            "mailing": {
                "unit": "#MailingAptUnit",
                "street_number": "#MailingStreetNum",
                "street_name": "#MailingStreetName",
                "city": "#MailingCityTown",
                "country": "#MailingCountry",
                "province": "#MailingProvinceState",
                "country": "#MailingCountry",
                "post_code": "#MailingPostalCode",
                "district": "#MailingDistrict",
            },
            "residential": {
                "unit": "#ResidentialAptUnit",
                "street_number": "#ResidentialStreetNum",
                "street_name": "#ResidentialStreetName",
                "city": "#ResidentialCityTown",
                "country": "#ResidentialCountry",
                "province": "#ResidentialProvinceState",
                "post_code": "#ResidentialPostalCode",
                "district": "#ResidentialDistrict",
            },
        }
        the_address = [
            {
                "action_type": Action.Input.value,
                "label": "Apt/Unit",
                "id": types[type]["unit"],
                "value": address.unit if address.unit else None,
                "length": 10,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Street number",
                "id": types[type]["street_number"],
                "value": address.street_number if address.street_number else None,
                "length": 10,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Street name",
                "id": types[type]["street_name"],
                "value": address.street_name if address.street_name else None,
                "length": 100,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "City",
                "id": types[type]["city"],
                "value": address.city if address.city else None,
                "length": 30,
                "required": True,
            },
            {
                "action_type": "Select",
                "label": "Country",
                "value": country_residence[address.country]
                if address.country
                else None,
                "id": types[type]["country"],
            },
        ]
        province = [
            {
                "action_type": "Select",
                "label": "Province",
                "value": province_map[address.province] if address.province else None,
                "id": types[type]["province"],
            }
        ]
        post_code = [
            {
                "action_type": Action.Input.value,
                "label": "Post code",
                "id": types[type]["post_code"],
                "value": address.post_code if address.post_code else None,
                "length": 7,
                "required": True,
            }
        ]
        district = [
            {
                "action_type": Action.Input.value,
                "label": "District",
                "id": types[type]["district"],
                "value": address.district if address.district else None,
                "length": 100,
                "required": True,
            }
        ]
        the_address += (
            province + post_code
            if address.country == "Canada"
            else post_code + district
        )
        return the_address

    # page 4 contact information
    def contactInfo(self):
        addresses = Addresses(self.pa.address)
        mailing = addresses.mailing
        residential = addresses.residential
        po = [
            {
                "action_type": Action.Input.value,
                "label": "PO box",
                "id": "#mailingPOBox",
                "value": mailing.po_box if mailing.po_box else None,
                "length": 15,
                "required": False,
            }
        ]
        is_same_address = [
            {
                "action_type": "Radio",
                "label": "Same address?",
                "id": "#yes" if mailing == residential else "#no",
            }
        ]
        mailing_address = po + self.makeAddress(mailing, "mailing")
        residential_address = (
            self.makeAddress(residential, "residential")
            if mailing != residential
            else []
        )

        phone = Phones(self.pa.phone).PreferredPhone
        primary_phone = [
            {
                "action_type": "Radio",
                "label": "Canada/US or other",
                "id": "#primaryNA" if phone.isCanadaUs else "#primaryOther",
            },
            {
                "action_type": "Select",
                "label": "Type",
                "value": phone_type[phone.variable_type],
                "id": "#PrimaryType",
            },
        ]
        country_code = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Country code",
                    "id": "#PrimaryCountryCode",
                    "value": phone.country_code,
                    "length": 4,
                    "required": False,
                }
            ]
            if not phone.isCanadaUs
            else []
        )
        number_ext = [
            {
                "action_type": Action.Input.value,
                "label": "Country code",
                "id": "#PrimaryNumber",
                "value": "-".join(phone.NA_format_list)
                if phone.isCanadaUs
                else phone.number,
                "length": 20,
                "required": False,
            },
            {
                "action_type": Action.Input.value,
                "label": "Extension",
                "id": "#PrimaryExtension",
                "value": phone.ext,
                "length": 5,
                "required": False,
            },
        ]
        contact_using_the_email = [
            {
                "action_type": "Radio",
                "label": "Contact using the email in account",
                "id": "#contactYes",
            }
        ]
        primary_phone += country_code + number_ext
        actions = (
            mailing_address
            + is_same_address
            + residential_address
            + primary_phone
            + contact_using_the_email
            + self.pdf
        )
        return [
            {
                "action_type": "WebPage",
                "page_name": "Page 4: Contact information ",
                "actions": actions,
                "next_page_tag":'#validPassportNo',
                "id": self.saveContinue(4),
            }
        ]

    def passport_id(self, person: PrModel, role: Role):
        ids = IDs(person.personid)
        has_passport = [
            {
                "action_type": Action.Radio.value,
                "label": "Passport / travel document",
                "id": "#validPassportYes"
                if ids.passport.number
                else "#validPassportNo",
            }
        ]
        has_id = [
            {
                "action_type": Action.Radio.value,
                "label": "Has national id",
                "id": "#NICYes" if ids.national_id.number else "#NICNo",
            }
        ]
        passport_content = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Passport number",
                    "id": "#passportNumber",
                    "value": ids.passport.number,
                    "length": 20,
                    "required": True,
                },
                {
                    "action_type": "Select",
                    "label": "Country of issue",
                    "value": country_residence[ids.passport.country]
                    if ids.passport.country
                    else None,
                    "id": "#countryOfIssue",
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Issue date",
                    "id": "#issueDate",
                    "value": ids.passport.issue_date.strftime("%Y/%m/%d"),
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Expiry date",
                    "id": "#expiryDate",
                    "value": ids.passport.expiry_date.strftime("%Y/%m/%d"),
                    "length": 10,
                    "required": True,
                },
            ]
            if ids.passport.number
            else []
        )
        id_content = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "ID number",
                    "id": "#nationalIdentityNumber",
                    "value": ids.national_id.number,
                    "length": 20,
                    "required": True,
                },
                {
                    "action_type": "Select",
                    "label": "Country of issue",
                    "value": country_residence[ids.national_id.country]
                    if ids.national_id.country
                    else None,
                    "id": "#countryOfIssue",
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Issue date",
                    "id": "#issueDate",
                    "value": ids.national_id.issue_date.strftime("%Y/%m/%d")
                    if ids.national_id.issue_date
                    else None,
                    "length": 10,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Expiry date",
                    "id": "#expiryDate",
                    "value": ids.national_id.expiry_date.strftime("%Y/%m/%d")
                    if ids.national_id.expiry_date
                    else None,
                    "length": 10,
                    "required": True,
                },
            ]
            if ids.national_id.number
            else []
        )

        passport = has_passport + passport_content if ids.passport else has_passport
        national_id = has_id + id_content if ids.national_id else has_id
        passport_continue_id = (
            self.saveContinue(5) if role == Role.PA else self.saveContinueDep1()
        )
        national_id_continue_id = (
            self.saveContinue(6) if role == Role.PA else self.saveContinueDep1()
        )
        return [
            {
                "action_type": "WebPage",
                "page_name": "Page 5: Passport"
                if role == Role.PA
                else "Dependant passport",
                "actions": passport + self.pdf,
                "next_page_tag":"#NICNo",
                "id": passport_continue_id,
            },
            {
                "action_type": "WebPage",
                "page_name": "Page 6: National ID"
                if role == Role.PA
                else "Dependant national id",
                "actions": national_id + self.pdf,
                "next_page_tag":"#intendedOccupation" if role==Role.PA else "body > pra-root > pra-localized-app > main > div > pra-imm0008-page9 > pra-imm0008-view-dependant-form > button",
                "id": national_id_continue_id,
            },
        ]

    def education(self, person: PrModel, role: Role):
        edu = EducationHistory(person.education)
        highest_eud = edu.highest
        years = (
            person.personal.primary_school_years
            + person.personal.secondary_school_years
            + person.personal.post_secondary_school_years
            + person.personal.other_school_years
        )
        education_set = [
            {
                "action_type": "Select",
                "label": "Education level",
                "value": education_level[highest_eud] if highest_eud else None,
                "id": "#educationLevel",
            },
            {
                "action_type": Action.Input.value,
                "label": "Number of education years",
                "id": "#numberOfYear",
                "value": str(years),
                "length": 2,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Current occupation",
                "id": "#currentOccupation",
                "value": self.pa.personal.current_occupation,
                "length": 50,
                "required": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Intended occupation",
                "id": "#intendedOccupation",
                "value": self.pa.personal.intended_occupation,
                "length": 50,
                "required": True,
            },
        ]
        save_continue_id = (
            self.saveContinue(7) if role == Role.PA else self.saveContinueDep1()
        )
        return [
            {
                "action_type": "WebPage",
                "page_name": "Page 7 Education"
                if role == Role.PA
                else "Dependant education",
                "actions": education_set + self.pdf,
                "next_page_tag":"#testing-no",
                "id": save_continue_id,
            }
        ]

    def language(self, person: PrModel, role: Role):
        language = [
            {
                "action_type": "Select",
                "label": "Native language",
                "value": all_languages[person.personal.native_language],
                "id": "#nativeLanguage",
            },
            {
                "action_type": "Select",
                "label": "English or French ",
                "value": english_french[person.personal.english_french],
                "id": "#language",
            },
        ]
        which_one_better = (
            [
                {
                    "action_type": "Select",
                    "label": "Which one is better ",
                    "value": english_french_map[person.personal.which_one_better]
                    if person.personal.which_one_better
                    else None,
                    "id": "#preferredLanguage",
                }
            ]
            if person.personal.english_french == "Both"
            else []
        )

        taken_test = [
            {
                "action_type": Action.Radio.value,
                "label": "Taken language test",
                "id": "#testing-yes"
                if person.personal.language_test
                else "#testing-no",
            }
        ]
        save_continue_id = (
            self.saveContinue(8) if role == Role.PA else self.saveContinueDep1()
        )
        return [
            {
                "action_type": "WebPage",
                "page_name": "Page 8 language detail"
                if role == Role.PA
                else "Dependant language detail",
                "actions": language + which_one_better + taken_test + self.pdf,
                "next_page_tag":"body > pra-root > pra-localized-app > main > div > pra-imm0008-page9 > div.buttons-container > button" if role==Role.PA else "#validPassportNo",
                "id": save_continue_id,
            }
        ]

    def gotoPage(self, page_num: int):
        pages = []
        for page in range(2, page_num):
            pages += [
                {
                    "action_type": "WebPage",
                    "page_name": f"Page {page}",
                    "actions": [],
                    "id": self.saveContinue(page),
                }
            ]
        return pages

    def gotoPageDependants(self):
        return self.gotoPage(9)

    def addDependants(self):
        actions = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have dependants to add",
                "id": "#dependantNo"
                if not self.sp and len(self.dps) == 0
                else "#dependantYes",
            }
        ]
        return [
            {
                "action_type": "WebPage",
                "page_name": "Add dependants or return to applicaton",
                "actions": actions,
                "next_page_tag":"#dependantDetailsForm-accompanyingPA-yes",
                "id": "body > pra-root > pra-localized-app > main > div > pra-imm0008-page9 > pra-imm0008-view-dependant-form > button"
                if self.sp or len(self.dps) > 0
                else "body > pra-root > pra-localized-app > main > div > pra-imm0008-page9 > div.buttons-container > button",
            }
        ]

    def fill(self):
        pa_form = (
            self.applicationDetails()
            + self.personalDetails(self.pa, Role.PA)
            + self.contactInfo()
            + self.passport_id(self.pa, Role.PA)
            + self.education(self.pa, Role.PA)
            + self.language(self.pa, Role.PA)
        )

        sp_form = (
            self.addDependants()
            + self.personalDetails(self.sp, Role.SP)
            + self.education(self.sp, Role.SP)
            + self.language(self.sp, Role.SP)
            + self.passport_id(self.sp, Role.SP)
            if self.sp
            else []
        )
        dp_forms = []
        for dp in self.dps:
            if dp.personal.age >= 18:
                dp_forms += (
                    self.addDependants()
                    + self.personalDetails(dp, Role.DP)
                    + self.education(dp, Role.DP)
                    + self.language(dp, Role.DP)
                    + self.passport_id(dp, Role.DP)
                )

        return self.goTo0008() + pa_form + sp_form + dp_forms

    def fill_pa(self):
        return (
            self.goTo0008()
            + self.applicationDetails()
            + self.personalDetails(self.pa, Role.PA)
            + self.contactInfo()
            + self.passport_id(self.pa, Role.PA)
            + self.education(self.pa, Role.PA)
            + self.language(self.pa, Role.PA)
        )

    def fill_dp(self):
        sp_form = (
            self.addDependants()
            + self.personalDetails(self.sp, Role.SP)
            + self.education(self.sp, Role.SP)
            + self.language(self.sp, Role.SP)
            + self.passport_id(self.sp, Role.SP)
            if self.sp
            else []
        )
        dp_forms = []
        for dp in self.dps:
            # if dp.personal.age >= 18:
            dp_forms += (
                self.addDependants()
                + self.personalDetails(dp, Role.DP)
                + self.education(dp, Role.DP)
                + self.language(dp, Role.DP)
                + self.passport_id(dp, Role.DP)
            )
        return self.goTo0008() + self.gotoPageDependants() + sp_form + dp_forms
