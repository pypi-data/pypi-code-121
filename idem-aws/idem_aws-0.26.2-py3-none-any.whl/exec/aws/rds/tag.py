import copy
from typing import Any
from typing import Dict
from typing import List


async def update_rds_tags(
    hub,
    ctx,
    resource_arn,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
):
    """
    Update tags of AWS RDS resources

    Args:
        hub:
        ctx:
        resource_arn: aws resource arn
        old_tags: list of old tags
        new_tags: list of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

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
            delete_ret = await hub.exec.boto3.client.rds.remove_tags_from_resource(
                ctx, ResourceName=resource_arn, TagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key) for key in tags_to_remove]
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.rds.add_tags_to_resource(
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
