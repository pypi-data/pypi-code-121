from lendsmart_api import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """
"""

data = {"object_meta":
{"name": "07d148a0-7196-11e9-bb98-5b4e95f7250a-QSK3wRC",
"account":"1673727821004808192",
 "owner_references": [
     {"uid": "1673863508366286848", "kind": "TeamMember", "name": "1673863508366286848", "api_version": "v1", "block_owner_deletion": True}, 
     {"uid": "1673114482038800384", "kind": "LoanApp", "name": "1673114482038800384", "api_version": "v1", "block_owner_deletion": True}
     ]}, 
     "advisor_id": "1667296677577285632", 
     "loanapp_id": "1673114482038800384", 
     "metadata": {"loan_id": "1673114482038800384"}}

update_data = {'id': '1673879725387243520',
'type_meta': {'kind': 'OriginatingLoanPermission', 'api_version': 'v1'},
'object_meta': {'name': '07d148a0-7196-11e9-bb98-5b4e95f7250a-QSK3wRC', 'account': '1673727821004808192', 'labels': {}, 'annotations': {}, 'owner_references': [{'kind':'TeamMember', 'api_version':'v1', 'name':'1673863508366286848', 'uid':'1673863508366286848', 'block_owner_deletion':True}, {'kind':'LoanApp', 'api_version':'v1', 'name':'1673114482038800384', 'uid':'1673114482038800384', 'block_owner_deletion':True}], 'namespace': ''},
'advisor_id': '1667296677577285632',
'loanapp_id': '1673114482038800384',
'metadata': {'loan_id': '1673114482038800384'},
'created_at': '2020-12-24T11:10:03.856078+00:00'}

advisor_id = '1585983990311952384'
l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
created_origination_loan_permission = l.origination_loan_permission.create_originating_loan_permission(data=data)
updated_origination_loan_permission = l.origination_loan_permission.update_loan_permission(data=update_data)
originate_loan_permission_for_given_advisor_id = l.originating_loan_permissions.get_originating_loan_permission_by_advisor_id(advisor_id)
print("============created  loan permission================================")
print(created_origination_loan_permission)
print("====================================================================")
print("===================updated originationg loan permission =========================",test_email)
print(updated_origination_loan_permission)
print("====================================================================")
print(originate_loan_permission_for_given_advisor_id)
