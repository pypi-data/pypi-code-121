import copy
from typing import Any
from typing import Dict
from typing import List

__func_alias__ = {"list_": "list"}


async def update_user_tags(
    hub,
    ctx,
    user_name: str,
    old_tags: List[Dict[str, Any]],
    new_tags: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Update tags of AWS IAM user

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        user_name: AWS IAM username
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
            delete_ret = await hub.exec.boto3.client.iam.untag_user(
                ctx, UserName=user_name, TagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key) for key in tags_to_remove]
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.iam.tag_user(
                ctx, UserName=user_name, Tags=tags_to_add
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result
    result["ret"] = {"tags": list(tags_result.values()) + tags_to_add}
    result["comment"] = (f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",)
    return result


async def update_user(
    hub,
    ctx,
    before: Dict[str, Any],
    user_name: str = None,
    path: str = None,
):
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}
    if user_name and before.get("user_name") != user_name:
        update_payload["NewUserName"] = user_name
    if path and before.get("path") != path:
        update_payload["NewPath"] = path
    if update_payload:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.iam.update_user(
                ctx=ctx, UserName=before.get("resource_id"), **update_payload
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
        result["ret"] = {}
        if "NewUserName" in update_payload:
            result["ret"]["user_name"] = update_payload["NewUserName"]
            result["comment"] = result["comment"] + (
                f"Update user_name: {update_payload['NewUserName']} on user {before.get('user_name')}",
            )
        if "NewPath" in update_payload:
            result["ret"]["path"] = update_payload["NewPath"]
            result["comment"] = result["comment"] + (
                f"Update path: {update_payload['NewPath']} on user {before.get('user_name')}",
            )
    return result


async def list_(hub, ctx):
    ret = await hub.exec.boto3.client.iam.list_users(ctx)

    if not ret["result"]:
        return {
            "result": False,
            "ret": [],
            "comment": f"Can not list users: {ret['comment']}",
        }

    users = []
    for user_raw in ret["ret"]["Users"]:
        # we're using this function for the camel case to snake case
        user = hub.tool.aws.iam.conversion_utils.convert_raw_user_to_present(user_raw)
        users.append(user)

    return {"result": True, "ret": users}
