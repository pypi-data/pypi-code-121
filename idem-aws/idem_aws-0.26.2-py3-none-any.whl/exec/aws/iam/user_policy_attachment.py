from typing import Any
from typing import Dict


async def get_policy_if_attached_to_user(
    hub, ctx, user_name: str, policy_arn: str
) -> Dict[str, Any]:
    """
    Check if a managed policy is attached to a user

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        user_name: The name (friendly name, not ARN) of the IAM user to attach the policy to.
         This parameter allows (through its regex pattern ) a string of characters consisting of upper and lowercase alphanumeric characters with no spaces.
         You can also include any of the following characters: _+=,.@-
        policy_arn(Text): The Amazon Resource Name (ARN) of the IAM policy you want to attach.

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}
    """
    result = dict(comment="", result=False, ret=None)
    user_policies_list = await hub.exec.boto3.client.iam.list_attached_user_policies(
        ctx, UserName=user_name
    )
    if user_policies_list["result"]:
        attached_user_policies_list = user_policies_list["ret"].get("AttachedPolicies")
        if attached_user_policies_list:
            policy_arn_list = [
                policy.get("PolicyArn") for policy in attached_user_policies_list
            ]
            if policy_arn in policy_arn_list:
                result["result"] = True
                result["ret"] = {"PolicyArn": policy_arn}
    else:
        result["comment"] = user_policies_list["comment"]
    return result
