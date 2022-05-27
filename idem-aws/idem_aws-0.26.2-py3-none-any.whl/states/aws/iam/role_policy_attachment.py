import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub, ctx, name: str, role_name: str, policy_arn: str, resource_id: str = None
) -> Dict[str, Any]:
    """
    Attaches the specified managed policy to the specified IAM role. When you attach a managed policy to a role,
     the managed policy becomes part of the role's permission (access) policy.

    Args:
        hub:
        ctx:
        name(Text): A name to represent the operation. This name is only for logging purpose. It is not used to
         attach a policy to a role.
        role_name(Text): The name (friendly name, not ARN) of the role to attach a policy.
         This parameter allows (through its regex pattern ) a string of characters consisting of upper and lowercase
          alphanumeric characters with no spaces. You can also include any of the following characters: _+=,.@-
        policy_arn(Text): The Amazon Resource Name (ARN) of the IAM policy you want to attach.
        resource_id(Text, Optional): The identifier for this object

    Request Syntax:
        [iam-attach-role-policy-name]:
          aws.iam.role_policy_attachment.present:
          - resource_id: 'string'
          - role_name: 'string'
          - policy_arn: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            idem-test-policy-temp-name:
              aws.iam.role_policy_attachment.present:
                - role_name: idem-test-role-name
                - policy_arn: arn:aws:iam::aws:policy/ReadOnlyAccess

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    try:
        before_ret = (
            await hub.exec.aws.iam.role_policy_attachment.is_role_policy_attached(
                ctx, role_name=role_name, policy_arn=policy_arn
            )
        )
    except hub.tool.boto3.exception.ClientError as e:
        result["comment"] = (f"{e.__class__.__name__}: {e}",)
        result["result"] = False
        return result

    # If before_ret has False result and has an error message in comment, then immediately return with the error,
    # unless this is a 'test' context - and if role does not exists - NoSuchEntityException is expected
    if (
        before_ret["result"] is False
        and before_ret["comment"]
        and not ctx.get("test", False)
    ):
        result["result"] = False
        result["comment"] = before_ret["comment"]
        return result

    if before_ret["result"]:
        result[
            "old_state"
        ] = hub.tool.aws.iam.conversion_utils.convert_raw_role_policy_attachment_to_present(
            role_name, policy_arn
        )
        result["new_state"] = copy.deepcopy(result["old_state"])
        result["comment"] = (f"aws.iam.role_policy_attachment '{name}' already exists",)
    else:
        try:
            if ctx.get("test", False):
                result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "role_name": role_name,
                        "policy_arn": policy_arn,
                    },
                )
                result["comment"] = (
                    f"Would create aws.iam.role_policy_attachment. Role {role_name}, policy {policy_arn}",
                )
                return result

            ret = await hub.exec.boto3.client.iam.attach_role_policy(
                ctx,
                RoleName=role_name,
                PolicyArn=policy_arn,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            result["comment"] = (f"Created aws.iam.role_policy_attachment '{name}'",)
            result[
                "new_state"
            ] = hub.tool.aws.iam.conversion_utils.convert_raw_role_policy_attachment_to_present(
                role_name, policy_arn
            )
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    return result


async def absent(
    hub, ctx, name: str, role_name: str, policy_arn: str
) -> Dict[str, Any]:
    """

    Removes the specified managed policy from the specified role.

    Args:
        name(Text): The name of the AWS IAM role policy.
        role_name(Text): The name (friendly name, not ARN) of the role to attach a policy.
         This parameter allows (through its regex pattern ) a string of characters consisting of upper and lowercase
          alphanumeric characters with no spaces. You can also include any of the following characters: _+=,.@-
        policy_arn(Text): The Amazon Resource Name (ARN) of the IAM policy you want to attach.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.iam.role_policy_attachment.absent:
                - name: value
                - role_name: value
                - policy_arn: value
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    try:
        before_ret = (
            await hub.exec.aws.iam.role_policy_attachment.is_role_policy_attached(
                ctx, role_name=role_name, policy_arn=policy_arn
            )
        )
    except hub.tool.boto3.exception.ClientError as e:
        result["comment"] = (f"{e.__class__.__name__}: {e}",)
        result["result"] = False
        return result

    if before_ret["result"] is False and before_ret["comment"]:
        if "NoSuchEntityException" in before_ret["comment"][0]:
            result["comment"] = (
                f"aws.iam.role_policy_attachment '{name}' already absent",
            )
        else:
            result["result"] = False
            result["comment"] = before_ret["comment"]
        return result

    if not before_ret["result"]:
        result["comment"] = (f"aws.iam.role_policy_attachment '{name}' already absent",)
    else:
        try:
            result[
                "old_state"
            ] = hub.tool.aws.iam.conversion_utils.convert_raw_role_policy_attachment_to_present(
                role_name, policy_arn
            )
            if ctx.get("test", False):
                result["comment"] = (
                    f"Would detach aws.iam.role_policy_attachment. Role '{role_name}', policy '{policy_arn}'",
                )
                return result

            ret = await hub.exec.boto3.client.iam.detach_role_policy(
                ctx, RoleName=role_name, PolicyArn=policy_arn
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
            result["comment"] = (
                f"Detached aws.iam.role_policy_attachment. Role '{role_name}', policy '{policy_arn}'",
            )
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = (f"{e.__class__.__name__}: {e}",)
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    """

    Describe the resource in a way that can be recreated/managed with the corresponding "present" function


    Lists the names of the attached managed policies of all IAM roles. If there are no managed policies attached
     to the specified role, the operation returns an empty dict.


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.iam.role_policy_attachment

    """

    result = {}
    # To describe all the attached role policies of all the roles, we first need to list all the roles, then get all the
    # attached policies
    ret_roles = await hub.exec.boto3.client.iam.list_roles(ctx)
    if not ret_roles["result"]:
        hub.log.debug(f"Could not describe role {ret_roles['comment']}")
        return {}
    role_name_list = [role.get("RoleName") for role in ret_roles["ret"]["Roles"]]
    for role_name in role_name_list:
        ret_attached_policies = (
            await hub.exec.boto3.client.iam.list_attached_role_policies(
                ctx=ctx, RoleName=role_name
            )
        )
        if not ret_attached_policies["result"]:
            hub.log.warning(
                f"Could not get attached policy list with role {role_name} with error"
                f" {ret_attached_policies['comment']} . Describe will skip this role and continue."
            )
        else:
            resources = ret_attached_policies["ret"].get("AttachedPolicies")
            for resource in resources:
                translated_resource = hub.tool.aws.iam.conversion_utils.convert_raw_role_policy_attachment_to_present(
                    role_name, resource.get("PolicyArn")
                )
                resource_id = f"{role_name}-{translated_resource['policy_arn']}"
                result[resource_id] = {
                    "aws.iam.role_policy_attachment.present": [
                        {parameter_key: parameter_value}
                        for parameter_key, parameter_value in translated_resource.items()
                    ]
                }

    return result
