from typing import Any
from typing import Dict


async def is_role_policy_attached(
    hub, ctx, role_name: str, policy_arn: str
) -> Dict[str, Any]:
    """
    Check if a managed policy is attached to a role

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        role_name: The name (friendly name, not ARN) of the role to list attached policies for.
         This parameter allows (through its regex pattern ) a string of characters consisting of upper and lowercase
          alphanumeric characters with no spaces. You can also include any of the following characters: _+=,.@-
        policy_arn: The Amazon Resource Name (ARN) of the IAM policy you want to search.

    Returns:
        {"result": True|False, "comment": Tuple, "ret": None}
    """
    result = dict(comment=(), result=False, ret=None)
    ret_list = await hub.exec.boto3.client.iam.list_attached_role_policies(
        ctx, RoleName=role_name
    )
    if ret_list["result"]:
        if ret_list["ret"].get("AttachedPolicies"):
            attached_role_policies_list = ret_list["ret"].get("AttachedPolicies")
            policy_arn_list = [
                policy.get("PolicyArn") for policy in attached_role_policies_list
            ]
            if policy_arn in policy_arn_list:
                result["result"] = True
                result["ret"] = {"PolicyArn": policy_arn}
    else:
        result["comment"] = ret_list["comment"]
    return result
