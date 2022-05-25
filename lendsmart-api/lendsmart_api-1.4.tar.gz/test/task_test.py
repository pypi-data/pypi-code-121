from lendsmart_api import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """
"""

object_meta_data = {
 "name": "normal_task",
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
metadata={}
status = {
    "phase": "Pending",
    }
data = {
    'object_meta': object_meta_data,
    'status':status,
    "metadata": metadata,
    "task_type": "General Upload & Text Input",
    "invite_type": "",
    "due_date": "12/18/2020",
    "comment": "Task created by lambda events",
    "assigned_at":"12/19/2020"
}
l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
tasks = l.task.get_task_by_role_id('1668766902063456256')
print(tasks)
create_new_loe = l.task.create_task(data=data)
print(create_new_loe)
