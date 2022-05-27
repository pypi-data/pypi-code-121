import copy
from typing import Any
from typing import Dict
from typing import List


async def update_tags(
    hub,
    ctx,
    resource_id: str,
    resource_type: str,
    old_tags: List[Dict[str, Any]] = None,
    new_tags: List[Dict[str, Any]] = None,
):
    """
    Update tags of AWS route53 hosted zone resources
    Args:
        hub:
        ctx:
        resource_id (Text): route53 hosted_zone resource id
        resource_type (Text): type of resource,
        old_tags (List): list of old tags
        new_tags (List): list of new tags

    Returns:
        {"result": True|False, "comment": ("A message",), "ret": Dict}

    """
    tags_to_add = []
    tags_to_remove = []
    if old_tags is None:
        tags_to_remove = None
        tags_to_add = new_tags
        tags_result = {}
    else:
        old_tags_map = {tag.get("Key"): tag for tag in old_tags}
        tags_result = copy.deepcopy(old_tags_map)
        if new_tags is not None:
            for tag in new_tags:
                if tag.get("Key") in old_tags_map:
                    if tag.get("Value") == old_tags_map.get(tag.get("Key")).get(
                        "Value"
                    ):
                        del old_tags_map[tag.get("Key")]
                    else:
                        tags_to_add.append(tag)
                else:
                    tags_to_add.append(tag)
            tags_to_remove = [tag.get("Key") for tag in old_tags_map.values()]
    result = dict(comment=(), result=True, ret=None)

    if (not tags_to_remove) and (not tags_to_add):
        return result
    elif not tags_to_remove:
        tags_to_remove = None
    elif not tags_to_add:
        tags_to_add = None
    if not ctx.get("test", False):
        change_tag_resp = await hub.exec.boto3.client.route53.change_tags_for_resource(
            ctx,
            ResourceType=resource_type,
            ResourceId=resource_id,
            AddTags=tags_to_add,
            RemoveTagKeys=tags_to_remove,
        )
        if not change_tag_resp["result"]:
            response_message = change_tag_resp["comment"]
            hub.log.debug(
                f"Could not modify tags for {resource_id} with error {response_message}"
            )
            result["comment"] = (
                f"Could not modify tags for {resource_id} with error {response_message}",
            )
            result["result"] = False
            return result
        hub.log.debug(f"modified tags for {resource_id}")

    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    result["comment"] = (f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",)
    return result
