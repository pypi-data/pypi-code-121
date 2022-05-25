from lendsmart_api import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """
"""
data = {"object_meta":
{"name": "0de89f40-aa08-11e9-867b-f55772be7ead", "account": "1673727821004808192"},
"metadata": {"team": "1673114419252764672", "loan_id": "1673114482038800384", "source_id": "1292639905278050304", "advisor_id": "1667296677577285632", "invite_to_name": "John Dragos", "invitation_type": "lendsmart_sh/invite_my_advisor", "invite_to_email": "johnsmith11012018@gmail.com", "invite_from_name": "John", "invite_to_gender": "", "invite_from_email": "demo@lendsmart.ai", "invite_to_address": "chester", "invite_to_persona": "realtors", "invite_to_avatar_url": "https://www.huntington.com/-/media/hcom/pages/mortgage/MLOs/MLO-Dragos-John.jpg?rev=6caca3c8150a48428b2f83ccec6b31d3&h=193&w=154&la=en&hash=8E2B655E07B908A07831F07D852279AB", "invite_to_business_name": "Huntington Bank", "invite_to_business_address": "chester"}, "status": {"phase": "Pending"}}

update_data ={'id': '1673863508366286848', 'type_meta': {'kind': 'TeamMember', 'api_version': 'v1'}, 'object_meta': {'name': '0de89f40-aa08-11e9-867b-f55772be7ead', 'account': '1673727821004808192', 'labels': {}, 'annotations': {}, 'owner_references': [], 'namespace': ''}, 'metadata': {'advisor_id': '1667296677577285632', 'invitation_type': 'lendsmart_sh/invite_my_advisor', 'invite_from_email': 'demo@lendsmart.ai', 'invite_from_name': 'John', 'invite_to_address': 'chester', 'invite_to_avatar_url': 'https://www.huntington.com/-/media/hcom/pages/mortgage/MLOs/MLO-Dragos-John.jpg?rev=6caca3c8150a48428b2f83ccec6b31d3&h=193&w=154&la=en&hash=8E2B655E07B908A07831F07D852279AB', 'invite_to_business_address': 'chester', 'invite_to_business_name': 'Huntington bank', 'invite_to_email': 'johnsmith11012018@gmail.com', 'invite_to_gender': '', 'invite_to_name': 'John Dragos', 'invite_to_persona': 'realtors', 'loan_id': '1673114482038800384', 'source_id': '1292639905278050304', 'team': '1673114419252764672'}, 'created_at': '2020-12-24T10:37:50.635923+00:00', 'spec': {'advisor_profile': None}, 'status': {'phase': 'Pending', 'message': '', 'reason': '', 'conditions': []}, 'updated_at': '2020-12-24T10:37:50.635923+00:00'}


test_id = "1673863508366286848"
l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
created_team_member = l.team_members.create_team_member(data=data)
get_team_member_by_id = l.team_members.get_team_member_by_id(test_id)
updated_team_member = l.team_members.update_team_member(data=update_data)

print("============created team member================================")
print(created_team_member)
print("====================================================================")
print("===================team member profile by id =========================",test_id)
print(get_team_member_by_id)
print("====================================================================")
print("=======================updated_team_member=======================")
print(updated_team_member)
print("====================================================================")
