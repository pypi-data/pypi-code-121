import copy
from typing import Any
from typing import Dict


async def update_tags(
    hub,
    ctx,
    resource_arn: str,
    old_tags: Dict[str, Any],
    new_tags: Dict[str, Any],
):
    """
    Update tags of AWS Lambda resources

    Args:
        resource_arn: Identifies the Amazon Lambda Function resource to which tags should be added.
            This value is an Amazon Resource Name (ARN).
        old_tags: List of existing tags
        new_tags: List of new tags

    Returns:
        {"result": True|False, "comment": ("A message",) "ret": None}

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

    if (not tags_to_delete) and (not tags_to_add):
        return result

    if tags_to_delete:
        if not ctx.get("test", False):
            delete_tag_resp = await hub.exec.boto3.client["lambda"].untag_resource(
                ctx, Resource=resource_arn, TagKeys=tags_to_delete
            )
            if not delete_tag_resp:
                failure_message = (
                    f"Could not delete tags {tags_to_delete} for Lambda Function with ARN {resource_arn}."
                    f" Failed with error: {delete_tag_resp['comment']}"
                )
                hub.log.debug(failure_message)
                result["comment"] = (failure_message,)
                result["result"] = False
                return result
        [tags_result.pop(key, None) for key in tags_to_delete]

    if tags_to_add:
        if not ctx.get("test", False):
            create_tag_resp = await hub.exec.boto3.client["lambda"].tag_resource(
                ctx, Resource=resource_arn, Tags=tags_to_add
            )
            if not create_tag_resp:
                failure_message = (
                    f"Could not create tags {tags_to_add} for Lambda Function with ARN {resource_arn}."
                    f" Failed with error: {create_tag_resp['comment']}"
                )
                hub.log.debug(failure_message)
                result["comment"] = (failure_message,)
                result["result"] = False
                return result

    result["ret"] = {"tags": list(tags_result.values()) + list(tags_to_add)}
    result["comment"] = result["comment"] + (
        f"Update tags: Add [{tags_to_add}] Remove [{tags_to_delete}]",
    )
    return result
