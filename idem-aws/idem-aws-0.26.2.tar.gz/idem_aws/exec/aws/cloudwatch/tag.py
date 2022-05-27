import copy
from typing import Any
from typing import Dict


async def update_tags(
    hub,
    ctx,
    resource_name: str,
    old_tags: Dict[str, Any],
    new_tags: Dict[str, Any],
):
    """

    Args:
        hub:
        ctx:
        resource_name: aws cloudwatch resource name
        old_tags: Dict of existing tags
        new_tags: Dict of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """

    result = dict(comment=(), result=True, ret=None)
    tags_to_add = {}
    tags_to_delete = []
    tags_result = copy.deepcopy(old_tags)
    for key, value in new_tags.items():
        if (key in old_tags and old_tags.get(key) != new_tags.get(key)) or (
            key not in old_tags
        ):
            tags_to_add[key] = value

    for key in old_tags:
        if key not in new_tags:
            tags_to_delete.append(key)
    try:
        if not ctx.get("test", False) and tags_to_delete:
            delete_tag_resp = await hub.exec.boto3.client.logs.untag_log_group(
                ctx, logGroupName=resource_name, tags=tags_to_delete
            )
            if not delete_tag_resp["result"]:
                hub.log.debug(f"Could not delete tags {tags_to_delete}")
                result["comment"] = delete_tag_resp["comment"]
                result["result"] = False
                return result
            else:
                hub.log.debug(f"Deleted tags {tags_to_delete}")
        [tags_result.pop(key, None) for key in tags_to_delete]
    except hub.tool.boto3.exception.ClientError as e:
        hub.log.debug(
            f"Could not delete tags {tags_to_delete} for resource: {resource_name} due to the error: {delete_tag_resp['comment']}"
        )
        result["comment"] = (f"{e.__class__.__name__}: {e}",)
        result["result"] = False

    try:
        if not ctx.get("test", False) and tags_to_add:
            create_tag_resp = await hub.exec.boto3.client.logs.tag_log_group(
                ctx, logGroupName=resource_name, tags=tags_to_add
            )
            if not create_tag_resp["result"]:
                hub.log.debug(f"Could not create tags {tags_to_add}")
                result["comment"] = result["comment"] + create_tag_resp["comment"]
                result["result"] = False
                return result
            else:
                hub.log.debug(f"Created tags {tags_to_add}")
    except hub.tool.boto3.exception.ClientError as e:
        hub.log.debug(
            f"Could not create tags {tags_to_add} for resource: {resource_name} due to the error: {create_tag_resp['comment']}"
        )
        result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
        result["result"] = False
    result["ret"] = {"tags": list(tags_result.values()) + list(tags_to_add)}
    result["comment"] = result["comment"] + (
        f"Update tags: Add [{tags_to_add}] Remove [{tags_to_delete}]",
    )
    result["result"] = True
    return result
