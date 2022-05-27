import json
from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_web_acl_resource_association_to_present(
    hub,
    web_acl_arn: str,
    resource_arn: str,
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    """
    Util functions to convert raw resource state from Associate Web ACL to present input format.

    Args:
        hub:
        web_acl_arn: The Amazon Resource Name (ARN) of the web ACL that you want to associate with the resource.
        resource_arn: The Amazon Resource Name (ARN) of the resource to associate with the web ACL.
        idem_resource_name: The idem name for the resource.

    Returns:
        Dict[str, Any]
    """
    resource_id = resource_arn
    translated_resource = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "web_acl_arn": web_acl_arn,
        "resource_arn": resource_arn,
    }
    return translated_resource


async def convert_raw_web_acl_to_present(
    hub,
    ctx,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
    scope: str = None,
) -> Dict[str, Any]:
    """
    Util functions to convert raw resource state from Web ACL to present input format.

    Args:
        hub:
        ctx:
        raw_resource: Old state of resource or existing resource details.
        idem_resource_name: Resource name.
        scope: Specifies whether this is for an Amazon CloudFront distribution or for a regional application.

    Returns:
        Dict[str, Any]
    """

    result = dict(comment=(), result=True, ret=None)
    resource_id = raw_resource.get("Id")
    web_acl_arn = raw_resource.get("ARN")
    resource_parameters = OrderedDict(
        {
            "DefaultAction": "default_action",
            "Description": "description",
            "Rules": "rules",
            "VisibilityConfig": "visibility_config",
            "CustomResponseBodies": "custom_response_bodies",
            "CaptchaConfig": "captcha_config",
        }
    )
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "scope": scope,
        "web_acl_arn": web_acl_arn,
    }
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource and raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = json.loads(
                json.dumps(raw_resource.get(parameter_raw))
            )

    ret_tag = await hub.exec.boto3.client.wafv2.list_tags_for_resource(
        ctx, ResourceARN=web_acl_arn
    )
    result["result"] = ret_tag["result"]
    if not result["result"]:
        result["comment"] = result["comment"] + ret_tag["comment"]
        return result
    if (
        ret_tag["ret"]
        and ret_tag["ret"]["TagInfoForResource"]
        and ret_tag["ret"]["TagInfoForResource"].get("TagList")
    ):
        resource_translated["tags"] = ret_tag["ret"]["TagInfoForResource"].get(
            "TagList"
        )
    result["ret"] = resource_translated

    return result
