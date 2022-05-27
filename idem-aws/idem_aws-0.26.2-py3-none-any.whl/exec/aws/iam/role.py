import copy
from typing import Any
from typing import Dict
from typing import List


async def update_role_tags(
    hub,
    ctx,
    role_name: str,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Update tags of AWS IAM Role

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        role_name: AWS IAM role name
        old_tags: list of old tags
        new_tags: list of new tags

    Returns:
        {"result": True|False, "comment": Tuple, "ret": Dict}
    """
    tags_to_add = []
    old_tags_map = {tag.get("Key"): tag for tag in old_tags}
    tags_result = copy.deepcopy(old_tags_map)
    for tag in new_tags:
        if tag.get("Key") in old_tags_map:
            if tag.get("Value") == old_tags_map.get(tag.get("Key")).get("Value"):
                del old_tags_map[tag.get("Key")]
            else:
                tags_to_add.append(tag)
        else:
            tags_to_add.append(tag)
    tags_to_remove = [tag.get("Key") for tag in old_tags_map.values()]
    result = dict(comment=(), result=True, ret=None)
    if (not tags_to_remove) and (not tags_to_add):
        return result
    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.iam.untag_role(
                ctx, RoleName=role_name, TagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key) for key in tags_to_remove]
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.iam.tag_role(
                ctx, RoleName=role_name, Tags=tags_to_add
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result
    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    result["comment"] = (f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",)
    return result


async def update_role(
    hub,
    ctx,
    old_state: Dict[str, Any],
    description: str = None,
    max_session_duration: int = None,
    timeout: Dict = None,
):
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}
    if (description is not None) and old_state.get("description") != description:
        update_payload["Description"] = description
    if (max_session_duration is not None) and old_state.get(
        "max_session_duration"
    ) != max_session_duration:
        update_payload["MaxSessionDuration"] = max_session_duration
    if update_payload:
        if not ctx.get("test", False):
            role_name = old_state.get("name")
            update_ret = await hub.exec.boto3.client.iam.update_role(
                ctx=ctx, RoleName=role_name, **update_payload
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result

            waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                default_delay=1,
                default_max_attempts=40,
                timeout_config=timeout.get("update") if timeout else None,
            )
            hub.log.debug(f"Waiting on updating aws.iam.role '{role_name}'")
            try:
                await hub.tool.boto3.client.wait(
                    ctx,
                    "iam",
                    "role_exists",
                    RoleName=role_name,
                    WaiterConfig=waiter_config,
                )
            except Exception as e:
                result["comment"] = result["comment"] + (str(e),)
                result["result"] = False
        result["ret"] = {}
        if "MaxSessionDuration" in update_payload:
            result["ret"]["max_session_duration"] = update_payload["MaxSessionDuration"]
            result["comment"] = result["comment"] + (
                f"Update max_session_duration: {update_payload['MaxSessionDuration']}",
            )
        if "Description" in update_payload:
            result["ret"]["description"] = update_payload["Description"]
            result["comment"] = result["comment"] + (
                f"Update description: {update_payload['Description']}",
            )
    return result


async def update_policy(
    hub,
    ctx,
    role_name: str,
    policy: str,
):
    # Update role's trust policy (the policy that is embedded within the role)
    result = dict(comment=(), result=True, ret=None)

    if not ctx.get("test", False):
        update_ret = await hub.exec.boto3.client.iam.update_assume_role_policy(
            ctx=ctx, RoleName=role_name, PolicyDocument=policy
        )
        if not update_ret["result"]:
            result["comment"] = update_ret["comment"]
            result["result"] = False
            return result

    if ctx.get("test", False):
        result["comment"] = (f"Would update aws.iam.role '{role_name}' policy",)
    else:
        result["comment"] = (f"Updated aws.iam.role '{role_name}' policy",)
    return result
