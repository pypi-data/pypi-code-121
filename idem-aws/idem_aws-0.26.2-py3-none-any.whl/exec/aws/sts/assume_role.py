from typing import Any
from typing import Dict
from typing import List


async def credentials(
    hub,
    ctx,
    role_arn: str,
    role_session_name: str,
    *,
    policy_arns: List[Dict[str, Any]] = None,
    policy: str = None,
    duration_seconds: int = None,
    tags: List[Dict[str, str]] = None,
    transitive_tag_keys: List[str] = None,
    external_id: str = None,
    serial_number: str = None,
    token_code: str = None,
    source_identity: str = None,
) -> Dict[str, Any]:
    """
    Returns a set of temporary security credentials that you can use to access Amazon Web Services resources that you might not normally have access to.
    These temporary credentials consist of an access key ID, a secret access key, and a security token.
    Typically, you use AssumeRole within your account or for cross-account access.
    For a comparison of AssumeRole with other API operations that produce temporary credentials,
    see Requesting Temporary Security Credentials and Comparing the Amazon Web Services STS API operations in the IAM User Guide .

    Examples:

    Call from the CLI:

    .. code-block:: bash

        $ idem exec aws.sts.assume_role.credentials <role_arn> <role_session_name>

    Call from code:

    .. code-block:: python

        async def my_func(hub, ctx, role_arn:str, role_session_name:str):
            await hub.exec.aws.sts.assume_role.credentials(ctx, role_arn, role_session_name)
    """
    ret = dict(result=True, ret={}, comment="")
    hub.log.debug(f"Assume role configuration set for ARN {role_arn}")

    config = {"RoleArn": role_arn, "RoleSessionName": role_session_name}
    if external_id is not None:
        config["ExternalId"] = external_id
    if policy_arns is not None:
        config["PolicyArns"] = policy_arns
    if policy is not None:
        config["Policy"] = policy
    if tags is not None:
        config["Tags"] = tags
    if transitive_tag_keys is not None:
        config["TransitiveTagKeys"] = transitive_tag_keys
    if duration_seconds is not None:
        config["DurationSeconds"] = duration_seconds
    if serial_number is not None:
        config["SerialNumber"] = serial_number
    if token_code is not None:
        config["TokenCode"] = token_code
    if source_identity is not None:
        config["SourceIdentity"] = source_identity

    assumed_role_object = await hub.exec.boto3.client.sts.assume_role(ctx, **config)
    ret["result"] = assumed_role_object.result
    ret["comment"] = assumed_role_object.comment
    if assumed_role_object.result:
        ret["ret"] = assumed_role_object.ret["Credentials"]
    return ret
