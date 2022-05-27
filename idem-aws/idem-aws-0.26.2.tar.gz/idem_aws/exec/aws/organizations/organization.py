from typing import Any
from typing import Dict
from typing import List


async def update_tags(
    hub,
    ctx,
    resource_id: str,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
):
    """

    Args:
        resource_id: aws organizations resource id
        old_tags: List of existing tags
        new_tags: List of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """

    result = dict(comment=(), result=True, ret=None)

    old_tags_map = {tag.get("Key"): tag.get("Value") for tag in old_tags}
    new_tags_map = {tag.get("Key"): tag.get("Value") for tag in new_tags}

    if old_tags_map == new_tags_map:
        result["comment"] = result["comment"] + ("Tag update is not required",)
        return result

    tags_to_add = []
    tags_to_delete = []

    for key, value in new_tags_map.items():
        if (key in old_tags_map and old_tags_map.get(key) != new_tags_map.get(key)) or (
            key not in old_tags_map
        ):
            tags_to_add.append({"Key": key, "Value": value})

    for key in old_tags_map:
        if key not in new_tags_map:
            tags_to_delete.append(key)
    if not ctx.get("test", False):
        try:
            delete_tag_resp = await hub.exec.boto3.client.organizations.untag_resource(
                ctx, ResourceId=resource_id, TagKeys=tags_to_delete
            )

            if not delete_tag_resp["result"]:
                hub.log.debug(
                    f"Could not delete tags {tags_to_delete} on resource {resource_id} with error {delete_tag_resp['comment']}"
                )
                result["comment"] = result["comment"] + delete_tag_resp["comment"]
                result["result"] = delete_tag_resp["result"]
                return result

        except hub.tool.boto3.exception.ClientError as e:
            hub.log.debug(
                f"Could not delete tags {tags_to_delete} on resource {resource_id} with error {e}"
            )
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

        try:
            create_tag_resp = await hub.exec.boto3.client.organizations.tag_resource(
                ctx, ResourceId=resource_id, Tags=tags_to_add
            )
            if not create_tag_resp["result"]:
                hub.log.debug(
                    f"Could not create tags {tags_to_add} on resource {resource_id} with error {create_tag_resp['comment']}"
                )
                result["comment"] = result["comment"] + create_tag_resp["comment"]
                result["result"] = create_tag_resp["result"]
                return result

        except hub.tool.boto3.exception.ClientError as e:
            hub.log.debug(
                f"Error while creating tags {tags_to_add} on resource {resource_id} : {e}"
            )
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

    result["comment"] = result["comment"] + (f"Updated tags '{new_tags}'",)
    result["ret"] = new_tags
    return result
