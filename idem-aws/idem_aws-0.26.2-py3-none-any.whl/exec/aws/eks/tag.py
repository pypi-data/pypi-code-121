import copy
from typing import Any
from typing import Dict


async def update_eks_tags(
    hub,
    ctx,
    resource_arn,
    old_tags: Dict[str, Any],
    new_tags: Dict[str, Any],
):
    """

    Args:
        hub:
        ctx:
        resource_arn: aws resource arn
        old_tags: Dict of old tags
        new_tags: Dict of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)

    tags_to_add = {}
    tags_to_remove = []
    tags_result = copy.deepcopy(old_tags)
    for key, value in new_tags.items():
        if (key in old_tags and old_tags.get(key) != new_tags.get(key)) or (
            key not in old_tags
        ):
            tags_to_add[key] = value

    for key in old_tags:
        if key not in new_tags:
            tags_to_remove.append(key)
    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.eks.untag_resource(
                ctx, resourceArn=resource_arn, tagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key.get("Key"), None) for key in tags_to_remove]
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.eks.tag_resource(
                ctx, resourceArn=resource_arn, tags=tags_to_add
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result

    result["ret"] = {"tags": {**tags_result, **tags_to_add}}
    result["comment"] = (f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",)
    return result
