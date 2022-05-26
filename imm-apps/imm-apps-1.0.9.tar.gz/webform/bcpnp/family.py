from typing import List, Union
from webform.models.definition import Action
from webform.models.bcpnpmodel_app import BcpnpModelApp, BcpnpEEModelApp
from webform.bcpnp.dashboard import DashboardApp
from model.common.employmenthistory import EmploymentHistory
from datetime import datetime
from webform.bcpnp.data import country_map
from model.common.family import FamilyMembers
from webform.bcpnp.data import marriage_map, province_map, family_imm_status_canada_map


class Family:
    def __init__(self, person: Union[BcpnpModelApp, BcpnpEEModelApp]):
        self.person = person
        self.spouse = FamilyMembers(self.person.family).spouse
        self.dependants = FamilyMembers(self.person.family).dependants
        self.mother = FamilyMembers(self.person.family).mother
        self.father = FamilyMembers(self.person.family).father
        self.siblings = FamilyMembers(self.person.family).siblings

    @property
    def spouse_details(self):
        is_married = [
            {
                "action_type": Action.Radio.value,
                "label": "Are you currently married or in a common-law relationship? ",
                "id": "#syncA_App_MaritalStatus-Yes"
                if self.person.marriage.marital_status in ["Common-Law", "Married"]
                else "#syncA_App_MaritalStatus-No",
            }
        ]
        sp = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Family name",
                    "id": "#syncA_App_Spouse_Lname",
                    "value": self.person.marriage.sp_last_name,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Given name",
                    "id": "#syncA_App_Spouse_Fname",
                    "value": self.person.marriage.sp_first_name,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Gender",
                    "id": "#syncA_App_Spouse_Sex",
                    "value": "Male"
                    if self.person.personal.sex == "Female"
                    else "Female",
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Date of birth",
                    "id": "#syncA_App_Spouse_DOB",
                    "value": self.spouse.date_of_birth,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Country of birth",
                    "id": "#syncA_App_Spouse_BirthPlace",
                    "value": country_map[self.spouse.birth_country],
                },
                {
                    "action_type": Action.Select.value,
                    "label": "Country of citizen",
                    "id": "#syncA_App_Spouse_Citizenship",
                    "value": country_map[self.spouse.country_of_citizenship],
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Present address",
                    "id": "#BCPNP_App_Spouse_Addr",
                    "value": self.spouse.address,
                    "required": True,
                    "length": 200,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Date into marriage or common-law",
                    "id": "#BCPNP_App_Spouse_MarriageDate",
                    "value": self.person.marriage.married_date,
                    "required": True,
                    "length": 10,
                },
            ]
            if self.person.marriage.marital_status in ["Common-Law", "Married"]
            else []
        )
        in_canada = [
            {
                "action_type": Action.Radio.value,
                "label": "Spouse or common-law partner status in Canada",
                "id": "#BCPNP_App_spouse_InCanada-Yes"
                if self.person.marriage.sp_in_canada
                else "#BCPNP_App_spouse_InCanada-No",
            }
        ]
        in_canada_status = (
            [
                {
                    "action_type": Action.Select.value,
                    "label": "Status in Canada",
                    "id": "#BCPNP_App_Spouse_InCanada_Status",
                    "value": self.person.marriage.sp_canada_status,
                },
            ]
            if self.person.marriage.sp_in_canada
            else []
        )

        other = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "If other, specify",
                    "id": "#BCPNP_App_Spouse_InCanada_Status_Other",
                    "value": self.person.marriage.sp_in_canada_other,
                    "required": True,
                    "length": 10,
                }
            ]
            if self.person.marriage.sp_canada_status == "Other"
            else []
        )

        status_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Date spouse or common-law partner documents expire",
                    "id": "#BCPNP_syncA_App_Spouse_Status_Expires",
                    "value": self.person.marriage.sp_canada_status_end_date,
                    "required": True,
                    "length": 10,
                }
            ]
            if self.person.marriage.sp_canada_status
            in ["Worker", "Student", "Visitor", "Other"]
            else []
        )

        # spouse work
        in_canada_work = (
            [
                {
                    "action_type": Action.Radio.value,
                    "label": "Is your spouse or common-law partner currently working?",
                    "id": "#BCPNP_App_spousePartnerWorking-Yes"
                    if self.person.marriage.sp_in_canada_work
                    else "#BCPNP_App_spousePartnerWorking-No",
                },
            ]
            if self.person.marriage.sp_in_canada
            else []
        )

        work_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Spouse or common-law partner occupation",
                    "id": "#BCPNP_App_Spouse_Occupation",
                    "value": self.person.marriage.sp_canada_occupation,
                    "required": True,
                    "length": 200,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Spouse or common-law partner employer",
                    "id": "#BCPNP_App_Spouse_Employer",
                    "value": self.person.marriage.sp_canada_employer,
                    "required": True,
                    "length": 200,
                },
            ]
            if self.person.marriage.sp_in_canada
            and self.person.marriage.sp_in_canada_work
            else []
        )

        return (
            is_married
            + sp
            + in_canada
            + in_canada_status
            + other
            + status_details
            + in_canada_work
            + work_details
        )

    def dependant_block(self, dependant, index):
        return [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": f"#BCPNP_App_Child_Lname-{index}",
                "value": dependant.last_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": f"#BCPNP_App_Child_Fname-{index}",
                "value": dependant.first_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Date of birth",
                "id": f"#BCPNP_App_Child_DOB-{index}",
                "value": dependant.date_of_birth,
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Select.value,
                "label": "Country of birth",
                "id": f"#BCPNP_App_Child_BirthPlace-{index}",
                "value": country_map[dependant.birth_country],
            },
            {
                "action_type": Action.Select.value,
                "label": "Citizen country",
                "id": f"#BCPNP_App_Child_Citizenship-{index}",
                "value": country_map[dependant.country_of_citizenship],
            },
            {
                "action_type": Action.Input.value,
                "label": "Present address",
                "id": f"#BCPNP_App_Child_Addr-{index}",
                "value": dependant.address,
                "required": True,
                "length": 300,
            },
        ]

    def sibling_block(self, sibling, index):
        sibling_deceased = True if sibling.date_of_death else False
        basic = [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": f"#BCPNP_App_Sibling_Lname-{index}",
                "value": sibling.last_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": f"#BCPNP_App_Sibling_Fname-{index}",
                "value": sibling.first_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Date of birth",
                "id": f"#BCPNP_App_Sibling_DOB-{index}",
                "value": sibling.date_of_birth,
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Select.value,
                "label": "Country of birth",
                "id": f"#BCPNP_App_Sibling_BirthPlace-{index}",
                "value": country_map[sibling.birth_country],
            },
            {
                "action_type": Action.Select.value,
                "label": "Marital stutus",
                "id": f"#BCPNP_App_Sibling_MaritalStatus-{index}",
                "value": marriage_map[sibling.marital_status],
            },
            {
                "action_type": Action.Checkbox.value,
                "label": "Deceased?",
                "id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(4) > div > uf-panel:nth-child(7) > div > uf-panel-body > div > uf-panel > div > uf-panel-body > div > div.ng-pristine.ng-untouched.ng-valid.ng-scope.ng-isolate-scope.ng-not-empty > div > uf-row:nth-child(6) > div > uf-switcher > div > div.checkbox > label > ng-transclude > span",
                "value": sibling_deceased,
            },
        ]

        address = (
            []
            if sibling_deceased
            else [
                {
                    "action_type": Action.Input.value,
                    "label": "Present address",
                    "id": f"#BCPNP_App_Sibling_Addr-{index}",
                    "value": sibling.address,
                    "required": True,
                    "length": 300,
                }
            ]
        )
        return basic + address

    def other_block(self, other, index):
        return [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": f"#BCPNP_App_CANFam_Lname-{index}",
                "value": other.last_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": f"#BCPNP_App_CANFam_Fname-{index}",
                "value": other.first_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Select.value,
                "label": "Gender",
                "id": f"#BCPNP_App_CANFam_Sex-{index}",
                "value": other.sex,
            },
            {
                "action_type": Action.Input.value,
                "label": "Relationship to applicant",
                "id": f"#BCPNP_App_CANFam_RelType-{index}",
                "value": other.relationship,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "City/town of relative",
                "id": f"#BCPNP_App_CANFam_City-{index}",
                "value": other.city,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Select.value,
                "label": "Province",
                "id": f"#BCPNP_App_CANFam_Province-{index}",
                "value": province_map[other.province],
            },
            {
                "action_type": Action.Select.value,
                "label": "Immigration status in Canada",
                "id": f"#BCPNP_App_CANFam_Status-{index}",
                "value": family_imm_status_canada_map[other.status],
            },
            {
                "action_type": Action.Input.value,
                "label": "Years in Canada",
                "id": f"#BCPNP_App_CANFam_CANYears-{index}",
                "value": str(other.years_in_canada),
                "required": True,
                "length": 10,
            },
        ]

    @property
    def dependant_children(self):
        has_dependants = {
            "action_type": Action.Radio.value,
            "label": "Do you have any children that meet Immigration, Refugees and Citizenship Canada (IRCC) definition of dependent child? ",
            "id": "#BCPNP_App_HaveDepChildren-Yes"
            if len(self.dependants) > 0
            else "#BCPNP_App_HaveDepChildren-No",
        }

        return [
            has_dependants,
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(4) > div > uf-panel:nth-child(3) > div > uf-panel-body > div > uf-panel > div > uf-panel-body > div > div:nth-child(2) > uf-clone-repeatable > a > i",
                "value": self.repeat_blocks(self.dependants, self.dependant_block),
            },
        ]

    @property
    def number_of_members(self):
        spouse = 1 if self.spouse else 0
        number = str(
            len(self.dependants) + spouse + 1
        )  # applicant self, plus spouse, and dependant children
        return [
            {
                "action_type": Action.Input.value,
                "label": "Family members in application",
                "id": "#syncA_App_FamMembers",
                "value": number,
                "required": True,
                "length": 2,
            }
        ]

    @property
    def parents(self):
        mother_deceased = True if self.mother.date_of_death else False
        father_deceased = True if self.father.date_of_death else False
        mother = [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": "#BCPNP_App_Mother_Lname",
                "value": self.mother.last_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": "#BCPNP_App_Mother_Fname",
                "value": self.mother.first_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Date of birth",
                "id": "#BCPNP_App_Mother_DOB",
                "value": self.mother.date_of_birth,
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Select.value,
                "label": "Country of birth",
                "id": "#BCPNP_App_Mother_BirthPlace",
                "value": country_map[self.mother.birth_country],
            },
            {
                "action_type": Action.Checkbox.value,
                "label": "Deceased?",
                "id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(4) > div > uf-panel:nth-child(5) > div > uf-panel-body > div > uf-row:nth-child(6) > div > uf-switcher > div > div.checkbox > label",
                "value": mother_deceased,
            },
        ]
        mother_present_address = (
            []
            if mother_deceased
            else [
                {
                    "action_type": Action.Input.value,
                    "label": "Present address",
                    "id": "#BCPNP_App_Mother_Addr",
                    "value": self.mother.address,
                    "required": True,
                    "length": 200,
                }
            ]
        )

        father = [
            {
                "action_type": Action.Input.value,
                "label": "Family name",
                "id": "#BCPNP_App_Father_Lname",
                "value": self.father.last_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Given name",
                "id": "#BCPNP_App_Father_Fname",
                "value": self.father.first_name,
                "required": True,
                "length": 100,
            },
            {
                "action_type": Action.Input.value,
                "label": "Date of birth",
                "id": "#BCPNP_App_Father_DOB",
                "value": self.father.date_of_birth,
                "required": True,
                "length": 10,
            },
            {
                "action_type": Action.Select.value,
                "label": "Country of birth",
                "id": "#BCPNP_App_Father_BirthPlace",
                "value": country_map[self.father.birth_country],
            },
            {
                "action_type": Action.Checkbox.value,
                "label": "Deceased?",
                "id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(4) > div > uf-panel:nth-child(6) > div > uf-panel-body > div > uf-row:nth-child(6) > div > uf-switcher > div > div.checkbox > label",
                "value": father_deceased,
            },
        ]
        father_present_address = (
            []
            if father_deceased
            else [
                {
                    "action_type": Action.Input.value,
                    "label": "Present address",
                    "id": "#BCPNP_App_Father_Addr",
                    "value": self.father.address,
                    "required": True,
                    "length": 200,
                }
            ]
        )

        return mother + mother_present_address + father + father_present_address

    @property
    def siblings_details(self):
        has_siblings = {
            "action_type": Action.Radio.value,
            "label": "Do you have any Siblings, including half- and step- Siblings?  ",
            "id": "#BCPNP_App_HaveSiblings-Yes"
            if len(self.dependants) > 0
            else "#BCPNP_App_HaveSiblings-No",
        }

        return [
            has_siblings,
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(4) > div > uf-panel:nth-child(7) > div > uf-panel-body > div > uf-panel > div > uf-panel-body > div > div:nth-child(2) > uf-clone-repeatable > a > ng-transclude > span",
                "value": self.repeat_blocks(self.siblings, self.sibling_block),
            },
        ]

    @property
    def others(self):
        has_others = {
            "action_type": Action.Radio.value,
            "label": "Do you have any family members in Canada, excluding those included in this application?  ",
            "id": "#BCPNP_App_HaveCANFam-Yes"
            if len(self.person.canadarelative) > 0
            else "#BCPNP_App_HaveCANFam-No",
        }

        return [
            has_others,
            {
                "action_type": Action.RepeatSection.value,
                "button_id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(4) > div > uf-panel:nth-child(8) > div > uf-panel-body > div > uf-panel > div > uf-panel-body > div > div:nth-child(2) > uf-clone-repeatable > a > ng-transclude > span",
                "value": self.repeat_blocks(
                    self.person.canadarelative, self.other_block
                ),
            },
        ]

    def repeat_blocks(self, sources: List, processor):
        blocks = []
        for index, source in enumerate(sources):
            blocks.append(processor(source, index))
        return blocks

    def fill(self):
        dashboard = DashboardApp()
        actions = (
            dashboard.jump("Family")
            + self.spouse_details
            + self.dependant_children
            + self.number_of_members
            + self.parents
            + self.siblings_details
            + self.others
            + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Family",
                "actions": actions,
                "id": None,
            }
        ]
