from lendsmart_api import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """
"""
data = {
    "object_meta":
    {"name": "smith-NXUnTUX123",
     "namespace": "dev",
     "labels": {},
     "account": "1673727821004808192",
     "annotations": {}, "owner_references": []},
     "source_id": "548",
     "email": "relator11@lendsmart.ai",
     "first_name": "relator",
      "last_name": "",
      "address":
        {"city": "", "state": "", "street": "", "country": "", "zip_code": ""},
         "gender": "",
         "phone": "",
         "business_name": "",
         "license": {"lendsmart_sh/mls_id": "845"},
          "persona": "realtors",
          "description": "",
          "image": "https://s3.us-east-2.amazonaws.com/lendsmartpub/geico.png",
          "user_name": "relator11@lendsmart.ai",
          "status": {"phase": "Pending", "reason": "initalize new advisor profile"}
}
update_data ={'id': '1673814386155601920',
'source_id': '548',
'type_meta': {'kind': 'AdvisorProfile', 'api_version': 'v1'},
'object_meta': {'name': 'smith-NXUnTUX123', 'account': '1673727821004808192', 'labels': {}, 'annotations': {}, 'owner_references': [], 'namespace': 'dev'},
'email': 'relator11@lendsmart.ai',
'first_name': 'relator',
'last_name': '',
'social_security_no': '',
'birth_day': '',
'address': {'street': '258', 'city': 'New your', 'state': 'NJ', 'country': 'USA', 'zip_code': ''},
'gender': '',
'phone': '',
'user_name': 'relator11@lendsmart.ai',
'metadata': {},
'business_name': '',
'license': {'lendsmart_sh/mls_id': '845'},
'persona': 'realtor',
'description': '',
'avatar': '',
'created_at': '2020-12-24T09:00:14.811802+00:00',
'status': {'phase': 'Pending', 'message': '', 'reason': 'initalize new advisor profile', 'conditions': []}}

test_email = "relator11@lendsmart.ai"
l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
create_advisor_profile = l.advisor_profile.create(data=data)
get_advisor_profile = l.advisor_profile.get_advisor_profile_by_email(test_email)
updated_advisor_profile = l.advisor_profile.update(data=update_data)

print("============created advisor profile================================")
print(create_advisor_profile)
print("====================================================================")
print("===================advisor profile bt email =========================",test_email)
print(get_advisor_profile)
print("====================================================================")
print("=======================updated advisor profile=======================")
print(updated_advisor_profile)
print("====================================================================")
