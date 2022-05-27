import copy
from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


async def update_web_acl(
    hub,
    ctx,
    name: str,
    raw_resource: Dict[str, Any],
    resource_parameters: Dict[str, None],
    scope: str,
    resource_id: str,
    lock_token: str,
):
    """

    Args:
        hub:
        ctx:
        name: Name of resource going to update.
        raw_resource: Old state of resource or existing resource details.
        resource_parameters: Parameters from sls file
        scope: Specifies whether this is for an Amazon CloudFront distribution or for a regional application.
        resource_id: The unique identifier for the web ACL.
        lock_token: A token used for optimistic locking.

    Returns:
        {"result": True|False, "comment": ("A tuple",), "ret": {}}
    """

    parameters = OrderedDict(
        {
            "Name": "name",
            "DefaultAction": "default_action",
            "VisibilityConfig": "visibility_config",
            "Description": "description",
            "Rules": "rules",
            "CustomResponseBodies": "custom_response_bodies",
            "CaptchaConfig": "captcha_config",
        }
    )
    parameters_to_update = {}
    result = dict(comment=(), result=True, ret=None)
    resource_parameters.pop("Tags", None)

    for key, value in resource_parameters.items():
        if value is None or value == raw_resource[key]:
            continue
        parameters_to_update[key] = resource_parameters[key]

    if parameters_to_update:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.wafv2.update_web_acl(
                ctx,
                Scope=scope,
                Id=resource_id,
                LockToken=lock_token,
                **resource_parameters,
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
            result["comment"] = result["comment"] + (f"Updated '{name}'",)

        result["ret"] = {}
        for parameter_raw, parameter_present in parameters.items():
            if parameter_raw in parameters_to_update:
                result["ret"][parameter_present] = parameters_to_update[parameter_raw]

    return result


async def update_web_acl_tags(
    hub,
    ctx,
    web_acl_arn,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
):
    """
    Update tags of Web ACL resources

    Args:
        hub:
        ctx:
        web_acl_arn: aws resource arn
        old_tags: list of old tags
        new_tags: list of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """

    tags_to_add = []
    tags_to_remove = []
    tags_keys_to_remove = []
    old_tags_map = {tag.get("Key"): tag for tag in old_tags}
    tags_result = copy.deepcopy(old_tags_map)

    if new_tags is not None:
        for tag in new_tags:
            if tag.get("Key") in old_tags_map:
                if tag.get("Value") == old_tags_map.get(tag.get("Key")).get("Value"):
                    del old_tags_map[tag.get("Key")]
                else:
                    tags_to_add.append(tag)
            else:
                tags_to_add.append(tag)
        tags_to_remove = [
            {"Key": tag.get("Key"), "value": tag.get("Value")}
            for tag in old_tags_map.values()
        ]
        tags_keys_to_remove = [tag.get("Key") for tag in old_tags_map.values()]

    result = dict(comment=(), result=True, ret=None)
    if (not tags_to_remove) and (not tags_to_add):
        return result

    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.wafv2.untag_resource(
                ctx, ResourceARN=web_acl_arn, TagKeys=tags_keys_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key.get("Key"), None) for key in tags_to_remove]

    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.wafv2.tag_resource(
                ctx, ResourceARN=web_acl_arn, Tags=tags_to_add
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result

    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    result["comment"] = (f"Updated tags: Add {tags_to_add} Remove {tags_to_remove}",)
    return result
