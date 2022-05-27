import copy
from typing import Any
from typing import Dict
from typing import List


async def update_tags(
    hub,
    ctx,
    resource_arn: str,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
):
    """
    Update tags of AWS Dynamo DB resources

    Args:
        resource_arn: Identifies the Amazon DynamoDB resource to which tags should be added.
            This value is an Amazon Resource Name (ARN).
        old_tags: List of existing tags
        new_tags: List of new tags

    Returns:
        {"result": True|False, "comment": ("A tuple",), "ret": None}

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
        delete_error_message = f"Could not delete tags {tags_to_remove} for DynamoDB table with ARN {resource_arn}"
        if not ctx.get("test", False):
            delete_tag_resp = await hub.exec.boto3.client.dynamodb.untag_resource(
                ctx, ResourceArn=resource_arn, TagKeys=tags_to_remove
            )
            if not delete_tag_resp:
                hub.log.debug(delete_error_message)
                result["comment"] = (f"Could not delete tags {tags_to_remove}",)
                result["result"] = False
                return result
        [tags_result.pop(key) for key in tags_to_remove]
    if tags_to_add:
        add_error_message = f"Could not create tags {tags_to_remove} for DynamoDB table with ARN {resource_arn}"
        if not ctx.get("test", False):
            create_tag_resp = await hub.exec.boto3.client.dynamodb.tag_resource(
                ctx, ResourceArn=resource_arn, Tags=tags_to_add
            )
            if not create_tag_resp:
                hub.log.debug(add_error_message)
                result["comment"] = result["comment"] + (
                    f"Could not update tags {tags_to_add}",
                )
                result["result"] = False
                return result

    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    result["comment"] = result["comment"] + (
        f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",
    )
    return result
