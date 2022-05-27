import copy
from typing import Any
from typing import Dict
from typing import List


async def get_tags_for_resource(hub, ctx, resource_arn: str = None):
    """
    Gets the tags for a neptune resource

    Args:
        hub:
        ctx:
        resource_arn: aws resource arn

    Returns:
        {"result": True|False, "comment": "A message tuple", "ret": Dict['str', Any]|None}

    """
    result = dict(comment=(), result=False, ret=None)
    if not resource_arn:
        return result
    tags = await hub.exec.boto3.client.neptune.list_tags_for_resource(
        ctx, ResourceName=resource_arn
    )
    result["ret"] = tags.get("ret").get("TagList") if tags.get("result") else None
    result["result"] = tags.get("result")
    if not result["result"]:
        result["comment"] = (
            f"Getting tags for resource with resource_arn: '{resource_arn}' failed",
        )
    return result


async def update_tags(
    hub,
    ctx,
    resource_arn,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
):
    """
    Update tags of AWS Neptune resources

    Args:
        hub:
        ctx:
        resource_arn: aws resource arn
        old_tags: list of old tags
        new_tags: list of new tags

    Returns:
        {"result": True|False, "comment": "A message tuple", "ret": Dict['str', any]}

    """
    tags_to_add = []
    tags_to_remove = []
    old_tags_map = {tag.get("Key"): tag for tag in old_tags or []}
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
        tags_to_remove = list(old_tags_map.keys())
    result = dict(comment=(), result=True, ret=None)
    if (not tags_to_remove) and (not tags_to_add):
        return result
    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.neptune.remove_tags_from_resource(
                ctx, ResourceName=resource_arn, TagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key) for key in tags_to_remove]
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.neptune.add_tags_to_resource(
                ctx, ResourceName=resource_arn, Tags=tags_to_add
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result
    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    result["comment"] = result["comment"] + (
        f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",
    )
    return result
