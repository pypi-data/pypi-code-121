import asyncio
import copy
from typing import Any
from typing import Dict
from typing import List


async def update_key_tags(
    hub,
    ctx,
    key_id: str,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
):
    """

    Args:
        hub:
        ctx:
        key_id: aws kms key id
        old_tags: list of old tags
        new_tags: list of new tags

    Returns:
        {"result": True|False, "comment": Tuple, "ret": "Tags after update"}

    """
    result = dict(comment=(), result=True, ret=None)

    tags_to_add = list()
    old_tags_map = {tag.get("TagKey"): tag for tag in old_tags}
    tags_result = copy.deepcopy(old_tags_map)
    for tag in new_tags:
        if tag.get("TagKey") in old_tags_map:
            # Make sure the key and value are the same before deleting
            if tag.get("TagValue") == old_tags_map.get(tag.get("TagKey")).get(
                "KeyValue"
            ):
                del old_tags_map[tag.get("TagKey")]
            else:
                tags_to_add.append(tag)
        else:
            tags_to_add.append(tag)
    tags_to_remove = [tag.get("TagKey") for tag in old_tags_map.values()]
    if tags_to_remove and not ctx.get("test", False):
        delete_ret = await hub.exec.boto3.client.kms.untag_resource(
            ctx, KeyId=key_id, TagKeys=tags_to_remove
        )
        if not delete_ret["result"]:
            result["comment"] = delete_ret["comment"]
            result["result"] = False
            return result
    if tags_to_add and not ctx.get("test", False):
        add_ret = await hub.exec.boto3.client.kms.tag_resource(
            ctx, KeyId=key_id, Tags=tags_to_add
        )
        if not add_ret["result"]:
            result["comment"] = add_ret["comment"]
            result["result"] = False
            return result
    for key in tags_to_remove:
        tags_result.pop(key)
    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    if ctx.get("test", False):
        result["comment"] = (
            f"Would update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",
        )
    else:
        result["comment"] = (
            f"Updated tags: Added [{tags_to_add}] Removed [{tags_to_remove}]",
        )
    return result


async def wait_for_updates(
    hub, ctx, timeout: Dict, resource_id: str, updates: Dict
) -> Dict[str, Any]:
    """
    Wait for key attribute updates.
    Possible attributes: description, state, policy, tags

    :param timeout: dictionary with 'delay in seconds and 'max_attempts'
    :param resource_id: key resource id
    :param updates: dictionary of key attribute and new value
    :return:
    """

    ret = dict(comment=(), result=True, ret=None)

    if updates is None or len(updates) == 0:
        hub.log.debug(f"No updates for KMS key '{resource_id}'")
        ret["comment"] = (f"No updates for KMS key '{resource_id}'",)
        return ret

    # sleep time seconds
    delay = timeout.get("delay", 2) if timeout else 2
    max_attempts = timeout.get("max_attempts", 120) if timeout else 120
    count = 1
    while count <= max_attempts and updates:
        hub.log.info(
            f"Waiting for key {resource_id} updates: '{updates.keys()}' for the {count} time"
        )
        await asyncio.sleep(delay)

        raw_key = await hub.exec.boto3.client.kms.describe_key(ctx, KeyId=resource_id)
        key = await hub.tool.aws.kms.conversion_utils.convert_raw_key_to_present(
            ctx, raw_resource=raw_key["ret"]["KeyMetadata"]
        )
        completed_updates = []
        for attr, value in updates.items():
            if key.get(attr) == value:
                hub.log.debug(f"aws.kms.key '{resource_id}' '{attr}' was updated.")
                completed_updates.append(attr)
        for updated_attr in completed_updates:
            updates.pop(updated_attr)
        count = count + 1

    ret["ret"] = key
    if updates:
        ret["result"] = False
        ret["comment"] = (
            f"Timed out waiting for aws.kms.key '{resource_id}' updates: {updates.keys()}",
        )
    return ret


async def set_key_rotation(hub, ctx, resource_id: str, enable_key_rotation: bool):
    """
    Enable or disable key rotation on the KMS key

    :param hub:
    :param ctx:
    :param resource_id: resource id for the key
    :param enable_key_rotation: True to enable key rotation, if not yet enabled and False to disable
    :return:
    """
    result = dict(comment=(), result=True, ret=None)

    if ctx.get("test", False):
        operation = "Would enable" if enable_key_rotation else "Would disable"
        result["comment"] = (
            f"{operation} key rotation for aws.kms.key '{resource_id}'",
        )
        return result

    if enable_key_rotation:
        ret = await hub.exec.boto3.client.kms.enable_key_rotation(
            ctx,
            KeyId=resource_id,
        )
    else:
        ret = await hub.exec.boto3.client.kms.disable_key_rotation(
            ctx,
            KeyId=resource_id,
        )

    if not ret["result"]:
        result["comment"] = ret["comment"]
        result["result"] = False
    else:
        operation = "Enabled" if enable_key_rotation else "Disabled"
        result["comment"] = (
            f"{operation} key rotation for aws.kms.key '{resource_id}'",
        )

    return result
