from webform.models.definition import Action
from webform.models.bcpnpmodel_app import BcpnpModelApp, BcpnpEEModelApp
from webform.bcpnp.dashboard import DashboardApp
from typing import Union
from webform.bcpnp.data import city_map
from webform.bcpnp.data import status_in_canada_map, country_map, workpermit_type_map


class Applicant:
    def __init__(self, person: Union[BcpnpModelApp, BcpnpEEModelApp]):
        self.person = person

    def fill(self):
        intended_residence_place = [
            {
                "action_type": Action.Select.value,
                "label": "In which city/town will you live after nomination?",
                "id": "#syncA_App_IntendedResidence",
                "value": city_map[self.person.bcpnp.intended_city],
            }
        ]

        # Current/previous applications
        q1 = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have another active application or registration with BC PNP?",
                "id": "#BCPNP_App_ActiveApplication-Yes"
                if self.person.bcpnp.q1
                else "#BCPNP_App_ActiveApplication-No",
            }
        ]
        q1_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq1",
                    "value": self.person.bcpnp.q1_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q1
            else []
        )

        q2 = [
            {
                "action_type": Action.Radio.value,
                "label": "Have you had another Skills Immigration or Entrepreneur Immigration registration or application refused or approved with BC PNP?",
                "id": "#BCPNP_App_RejectedPrevPNP-Yes"
                if self.person.bcpnp.q2
                else "#BCPNP_App_RejectedPrevPNP-No",
            }
        ]
        q2_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq2",
                    "value": self.person.bcpnp.q2_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q2
            else []
        )

        q3 = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you have an active application for provincial nomination or permanent residence under any other federal or provincial program?",
                "id": "#BCPNP_App_ActivePNPAppReg-Yes"
                if self.person.bcpnp.q3
                else "#BCPNP_App_ActivePNPAppReg-No",
            }
        ]
        q3_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq3",
                    "value": self.person.bcpnp.q3_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q3
            else []
        )

        q4 = [
            {
                "action_type": Action.Radio.value,
                "label": "Have you ever had an application rejected for provincial nomination or permanent residence in Canada under any other federal or provincial program? ",
                "id": "#BCPNP_App_RejectedApplication-Yes"
                if self.person.bcpnp.q4
                else "#BCPNP_App_RejectedApplication-No",
            }
        ]
        q4_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq4",
                    "value": self.person.bcpnp.q4_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q4
            else []
        )

        q5 = [
            {
                "action_type": Action.Radio.value,
                "label": "Have you ever had an application rejected for a Canadian visitor visa, study permit, or temporary work permit?",
                "id": "#BCPNP_App_RejectedVisaPermit-Yes"
                if self.person.bcpnp.q5
                else "#BCPNP_App_RejectedVisaPermit-No",
            }
        ]
        q5_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq5",
                    "value": self.person.bcpnp.q5_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q5
            else []
        )

        q6 = [
            {
                "action_type": Action.Radio.value,
                "label": "Have you made a claim for refugee protection in Canada, or have you been refused refugee status in Canada? ",
                "id": "#BCPNP_App_RefusedRefugee-Yes"
                if self.person.bcpnp.q6
                else "#BCPNP_App_RefusedRefugee-No",
            }
        ]
        q6_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq6",
                    "value": self.person.bcpnp.q6_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q6
            else []
        )

        q7 = [
            {
                "action_type": Action.Radio.value,
                "label": "Are you under a removal order from Canada (e.g. departure order or exclusion order)?",
                "id": "#BCPNP_App_RemovalOrder-Yes"
                if self.person.bcpnp.q7
                else "#BCPNP_App_RemovalOrder-No",
            }
        ]
        q7_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Provide details",
                    "id": "#BCPNP_App_CurPrevApplicationsDetailsq7",
                    "value": self.person.bcpnp.q7_explaination,
                    "required": True,
                    "length": 200,
                }
            ]
            if self.person.bcpnp.q7
            else []
        )

        # Current status
        current_in_canada = [
            {
                "action_type": Action.Radio.value,
                "label": "Are you currently in Canada?",
                "id": "#syncA_App_InCanada-Yes"
                if self.person.status.current_country == "Canada"
                else "#syncA_App_InCanada-No",
            }
        ]
        status_or_country = (
            [
                {
                    "action_type": Action.Select.value,
                    "label": "Indicate your current status in Canada",
                    "id": "#syncA_App_InCanada_Status",
                    "value": status_in_canada_map[
                        self.person.status.current_country_status
                    ],
                }
            ]  # BCPNP_App_CurResidence_Country
            if self.person.status.current_country == "Canada"
            else [
                {
                    "action_type": Action.Select.value,
                    "label": "Indicate your current country of residence",
                    "id": "#BCPNP_App_CurResidence_Country",
                    "value": country_map[self.person.status.current_country],
                }
            ]
        )

        status_details = []

        def uci(id):
            return {
                "action_type": Action.Input.value,
                "label": "IRCC Client ID/UCI",
                "id": id,
                "value": self.person.personal.uci,
                "required": True,
                "length": 20,
            }

        def start_date(id):
            return {
                "action_type": Action.Input.value,
                "label": "Date of issue",
                "id": id,
                "value": self.person.status.current_status_start_date,
                "required": True,
                "length": 20,
            }

        def end_date(id):
            return {
                "action_type": Action.Input.value,
                "label": "Valid until",
                "id": id,
                "value": self.person.status.current_status_end_date,
                "required": True,
                "length": 20,
            }

        match self.person.status.current_country_status:
            case "Student":
                status_details = [
                    uci("#syncA_App_StudyPermit_ClientID"),
                    start_date("#BCPNP_App_StudyPermit_DateSigned"),
                    end_date("#syncA_App_StudyPermit_ValidUntil"),
                ]
            case "Worker":
                workpermit_type = {
                    "action_type": Action.Select.value,
                    "label": "Your work permit type",
                    "id": "#BCPNP_App_WorkPermit_Info",
                    "value": workpermit_type_map[
                        self.person.status.current_workpermit_type
                    ],
                }
                status_details = [
                    workpermit_type,
                    uci("#syncA_App_WorkPermit_ClientID"),
                    start_date("#BCPNP_App_WorkPermit_DateSigned"),
                    end_date("#syncA_App_WorkPermit_ValidUntil"),
                ]
            case "Visitor":
                has_visitor = {
                    "action_type": Action.Radio.value,
                    "label": "Do you have a visitor record? ",
                    "id": "#BCPNP_App_VisitorRecord-Yes"
                    if self.person.status.has_vr
                    else "#BCPNP_App_VisitorRecord-No",
                }
                enter_date = {
                    "action_type": Action.Input.value,
                    "label": "Date entered Canada",
                    "id": "#BCPNP_App_Visitor_EnteredCanada",
                    "value": self.person.status.last_entry_date,
                    "required": True,
                    "length": 20,
                }
                status_details = [
                    has_visitor,
                    uci("#BCPNP_App_Visitor_ClientID"),
                    enter_date,
                    start_date("#BCPNP_App_Visitor_DateSigned"),
                    end_date("#BCPNP_App_Visitor_ValidUntil"),
                ]
            case "Other":
                status_details = [
                    {
                        "action_type": Action.Input.value,
                        "label": "If other, please specify:",
                        "id": "#BCPNP_App_InCanada_Status_Other",
                        "value": self.person.status.other_status_explaination,
                        "required": True,
                        "length": 200,
                    }
                ]

        dashboard = DashboardApp()

        actions = (
            dashboard.jump("Applicant")
            + intended_residence_place
            + q1
            + q1_details
            + q2
            + q2_details
            + q3
            + q3_details
            + q4
            + q4_details
            + q5
            + q5_details
            + q6
            + q6_details
            + q7
            + q7_details
            + current_in_canada
            + status_or_country
            + status_details
            + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Applicant",
                "actions": actions,
                "id": None,
            }
        ]
