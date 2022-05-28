from webform.models.definition import Action
from datetime import datetime

class Application():
    def __init__(self,pa):
        self.pa=pa
    
    def pick(self):
        return [
            {
                "action_type":Action.WebPage.value,
                "page_name":"Pick or create an application",
                "actions":[{
                    "action_type":Action.PrPortalPick.value,
                    "email":self.pa.personal.email
                }],
                'id':None
                }
        ]
        
    
    def create(self):
        turnpage_create={
            "action_type": Action.Turnpage.value,
            "label": "Create new application",
            "id": "body > pra-root > pra-localized-app > main > div > pra-rep-dashboard > div > div.search-row.ng-star-inserted > div > button",
        }
        section_client = [
                {
                    "action_type": Action.Input.value,
                    "lable": "Client given name",
                    "id": "#clientGiveName",
                    "value": self.pa.personal.first_name,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "lable": "Client family name",
                    "id": "#clientFamilyName",
                    "value": self.pa.personal.last_name,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "lable": "Client email",
                    "id": "#clientEmail",
                    "value": self.pa.personal.email,
                    "required": True,
                },
                {
                    "action_type": Action.Input.value,
                    "lable": "Confirm client's email (required)",
                    "id": "#clientEmailVerified",
                    "value": self.pa.personal.email,
                    "required": True,
                }
            ]
        # program and category 
        programs={
            "Economic": "1: 1",
            "Family": "2: 2",
            "Refugee": "3: 3",
            "Other": "4: 4"
        }
        categories={
            # Economic
            "Agri-Food Pilot": "1: 1",
            "Home Support Worker Pilot": "2: 6",
            "Rural and Northern Immigration Program": "3: 9",
            "Provincial Nominee Program (PNP)": "4: 10",
            "Self-Employed Persons Class": "5: 11",
            "Start-Up Business Class": "6: 12",
            "Quebec Skilled Workers Program": "7: 13",
            "Quebec Selected Investor Program": "8: 14",
            "Quebec Entrepreneur Program": "9: 15",
            "Quebec Self-Employed Persons Program": "10: 16",
            "Atlantic Immigration Program": "11: 28",
            # Family
            "Spouse": "1: 17",
            "Common-law Partner": "2: 18",
            "Conjugal Partner": "3: 19",
            "Dependent Child": "4: 21",
            "Other Relative": "5: 22",
            "Adopted child/Child to be adopted in Canada": "6: 23"
        }
        under={
            "Spouse or common-law partner in Canada class": "1: true",
            "Family class (outside Canada)": "2: false"
        }
        # make application name
        app_name=self.pa.prcase.imm_category+"-"+datetime.today().strftime("%Y%m%d%H%M%S")
        if_family_category=[
            {
                "action_type":"Wait",
                "duration":2000
            },
            {
                "action_type": "Select",
                "lable": "Are you applying under",
                "id": "#lobClass",
                "value": under[self.pa.prcase.imm_under]
            }    
        
        ] if self.pa.prcase.imm_category=='Spouse' or self.pa.prcase.imm_category=="Common-law Partner" else []
        section_program = [
            {
                "action_type": "DependantSelect",
                "select1": {
                "action_type": "Select",
                "lable": "Select the permanent resience program",
                "id": "#lobProgram",
                "value": programs[self.pa.prcase.imm_program]
                },
                "select2": {
                "action_type": "Select",
                "lable": "Category under which you are applying (required)",
                "id": "#lobCategory",
                "value": categories[self.pa.prcase.imm_category]
                },
            },
            *if_family_category,
            {
                "action_type": Action.Input.value,
                "lable": "Application name",
                "id": "#applicationName",
                "value": app_name,
                "required": True,
            },
            
        ];
        index=5 if self.pa.prcase.imm_category=='Spouse' or self.pa.prcase.imm_category=="Common-law Partner" else 4
        turnpage_save={
            "action_type": Action.Turnpage.value,
            "label": "Continue",
            "id": f"body > pra-root > pra-localized-app > main > div > pra-intake-landing-page > section:nth-child({index}) > pra-program-selection-form > button"
        }
        
        return [
            {
                "action_type":Action.WebPage.value,
                "page_name":"Pick or create an application",
                "actions":[turnpage_create,*section_client,*section_program,turnpage_save],
                'id':None
                }
        ]
