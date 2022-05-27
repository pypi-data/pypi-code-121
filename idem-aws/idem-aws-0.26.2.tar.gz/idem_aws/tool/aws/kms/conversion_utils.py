from collections import OrderedDict
from typing import Any
from typing import Dict


async def convert_raw_key_to_present(
    hub, ctx, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:
    describe_parameters = OrderedDict(
        {
            "KeyId": "resource_id",
            "KeyArn": "arn",
            "Arn": "arn",
            "KeyState": "key_state",
            "Description": "description",
            "KeyUsage": "key_usage",
            "KeySpec": "key_spec",
            "MultiRegion": "multi_region",
            "Policy": "policy",
            "BypassPolicyLockoutSafetyCheck": "bypass_policy_lockout_safety_check",
            "Tags": "tags",
        }
    )

    translated_resource = {}
    for parameter_raw, parameter_present in describe_parameters.items():
        if parameter_raw in raw_resource:
            translated_resource[parameter_present] = raw_resource.get(parameter_raw)

    # Get key tags
    # For tag operations key_id is used and not resource_i
    key_tags = await hub.exec.boto3.client.kms.list_resource_tags(
        ctx, KeyId=translated_resource["resource_id"]
    )
    if key_tags and key_tags["result"] is True:
        translated_resource["tags"] = key_tags["ret"].get("Tags", [])
    else:
        raise Exception(key_tags["comment"])

    # Get key policy
    key_policy = await hub.exec.boto3.client.kms.get_key_policy(
        ctx, KeyId=translated_resource["resource_id"], PolicyName="default"
    )
    if (
        key_policy
        and key_policy["result"] is True
        and key_policy["ret"].get("Policy", None)
    ):
        translated_resource[
            "policy"
        ] = hub.tool.aws.state_comparison_utils.standardise_json(
            key_policy["ret"].get("Policy")
        )
    else:
        raise Exception(key_policy["comment"])

    # Get key rotation value if key is Enabled (not if Disabled or PendingDeletion)
    if translated_resource["key_state"] == "Enabled":
        key_rotation = await hub.exec.boto3.client.kms.get_key_rotation_status(
            ctx, KeyId=translated_resource["resource_id"]
        )
        if key_rotation["result"] is True:
            translated_resource["enable_key_rotation"] = key_rotation["ret"].get(
                "KeyRotationEnabled", False
            )
        else:
            raise Exception(key_rotation["comment"])

    return translated_resource


def convert_raw_key_alias_to_present(
    hub, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:

    # Arn is not used for present but required for arg binding
    resource_parameters = OrderedDict(
        {
            "AliasArn": "arn",
            "TargetKeyId": "target_key_id",
        }
    )
    # AliasName is the unique identifier for KMS Alias, so it is set as resource_id
    translated_resource = {"resource_id": raw_resource.get("AliasName")}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            translated_resource[parameter_present] = raw_resource.get(parameter_raw)

    return translated_resource
