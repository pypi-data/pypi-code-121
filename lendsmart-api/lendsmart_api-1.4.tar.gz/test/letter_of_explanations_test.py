from lendsmart_api import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """
"""

object_meta_data = {
 "name": "0001_bank_statement_large_deposit",
 "account": "1586153061640871936",
 "owner_references": [{
    "kind": "LoanApp",
    "api_version": "v1",
    "name": "1668766894756790272",
    "uid": "1668766894756790272",
    "block_owner_deletion": False
},{
    "kind": "LoanAppRole",
    "api_version": "v1",
    "name": "1668766902063456256",
    "uid": "1668766902063456256",
    "block_owner_deletion": False
}]}
status = {
    "phase": "Pending",
    "message":"Letter of Explanation created by advisor",
    "reason": "LetterOfExplanationOriginated",
    "conditions":[]
    }
asks = {
    "template": "0001_BANK_STATEMENT_LARGE_DEPOSIT",
    "filled": {
    "0001_BANK_NAME":"ABCD",
    "0001_TRANSACTION_TYPE":"Deposit",
    "0001_AMOUNT":"2500",
    "0001_DATE":"1608227326",
    "0000_EXPLANATIONS":"Acme"
    },
    "sign_status":{
    "signers":[
        {
            "email":"",
            "date":"",
            "viewed":""
        }
    ],
    "signed":"Pending"
    },
    "description":"",
    "located_at":""
    }
data = {
    'object_meta': object_meta_data,
    'status':status,
    "asks": asks
}
l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
get_loe_by_loan_id = l.letter_of_explanations.get_loe_by_loanid('1668766902063456256')
print(get_loe_by_loan_id)
create_new_loe = l.letter_of_explanations.create_loe(data=data)
print(create_new_loe)
