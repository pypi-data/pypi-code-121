from typing import Any
from typing import Dict


async def is_target_policy_attached(
    hub, ctx, policy_id: str, target_id: str
) -> Dict[str, Any]:
    """
    Check if a organization policy is attached to a target

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        policy_id(str): The unique identifier (ID) of the policy that you want to attach to the target.
                    You can get the ID for the policy by calling the ListPolicies operation.
        target_id(str): The unique identifier (ID) of the root, OU, or account that you want to attach the policy to.


    Returns:
        {"result": True|False, "comment": "A message", "ret": None}
    """
    result = dict(comment="", result=False, ret=None)
    ret_list = await hub.exec.boto3.client.organizations.list_policies_for_target(
        ctx, TargetId=target_id, Filter="SERVICE_CONTROL_POLICY"
    )
    if ret_list["result"]:
        if ret_list["ret"].get("Policies"):
            attached_policies_list = ret_list["ret"].get("Policies")
            policy_id_list = [policy.get("Id") for policy in attached_policies_list]
            if policy_id in policy_id_list:
                result["result"] = True
                result["ret"] = {"PolicyId": policy_id}
    else:
        result["comment"] = ret_list["comment"]
    return result
