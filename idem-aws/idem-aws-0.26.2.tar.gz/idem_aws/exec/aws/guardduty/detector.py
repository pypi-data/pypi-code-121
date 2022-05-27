import copy
from typing import Any
from typing import Dict


async def update_detector_tags(
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
        old_tags: dict of old tags
        new_tags: dict of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """

    tags_to_add = {}
    tags_to_remove = []
    tags_result = {}
    if old_tags:
        tags_result = copy.deepcopy(old_tags)
    if new_tags is not None:
        for key, value in new_tags.items():
            if (key in old_tags and old_tags.get(key) != new_tags.get(key)) or (
                key not in old_tags
            ):
                tags_to_add[key] = value
    if old_tags:
        for key in old_tags:
            if key not in new_tags:
                tags_to_remove.append(key)
    result = dict(comment=(), result=True, ret=None)
    if (not tags_to_remove) and (not tags_to_add):
        return result
    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.guardduty.untag_resource(
                ctx, ResourceArn=resource_arn, TagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
        [tags_result.pop(key, None) for key in tags_to_remove]
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.guardduty.tag_resource(
                ctx, ResourceArn=resource_arn, Tags=tags_to_add
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result
    tags_to_append = {**tags_result, **tags_to_add}
    result["ret"] = {"tags": tags_to_append}
    result["comment"] = (f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]",)
    return result


async def update_detector(
    hub,
    ctx,
    before: Dict[str, Any],
    detector_id: str = None,
    finding_publishing_frequency: str = None,
    data_sources: Dict[str, Any] = None,
):
    result = dict(comment=(), result=True, ret=None)
    compare_dict_result = False
    update_payload = {}
    if (finding_publishing_frequency is not None) and before["ret"].get(
        "FindingPublishingFrequency"
    ) != finding_publishing_frequency:
        update_payload["FindingPublishingFrequency"] = finding_publishing_frequency
    data_describe = before["ret"]
    data_sources_rendered = hub.tool.aws.guardduty.detector_utils.render_data_sources(
        data_describe
    )
    if data_sources:
        compare_dict_result = hub.tool.aws.guardduty.detector_utils.compare_dicts(
            data_sources, data_sources_rendered
        )
    if not compare_dict_result and data_sources is not None:
        update_payload["DataSources"] = data_sources
    if update_payload:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.guardduty.update_detector(
                ctx=ctx, DetectorId=detector_id, **update_payload
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
        result["ret"] = {}
        if "FindingPublishingFrequency" in update_payload:
            result["ret"]["finding_publishing_frequency"] = update_payload[
                "FindingPublishingFrequency"
            ]
            result["comment"] = result["comment"] + (
                f"Update finding_publishing_frequency: {update_payload['FindingPublishingFrequency']}",
            )
        if "DataSources" in update_payload:
            result["ret"]["data_sources"] = update_payload["DataSources"]
            result["comment"] = result["comment"] + (
                f"Update data_sources: {update_payload['DataSources']}",
            )
    return result
