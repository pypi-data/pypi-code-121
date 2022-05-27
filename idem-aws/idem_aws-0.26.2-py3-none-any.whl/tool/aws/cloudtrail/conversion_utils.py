from collections import OrderedDict
from typing import Any
from typing import Dict


async def convert_raw_cloudtrail_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str
) -> Dict[str, Any]:
    resource_id = raw_resource.get("Name")
    resource_parameters = OrderedDict(
        {
            "S3BucketName": "s3_bucket_name",
            "S3KeyPrefix": "s3_key_prefix",
            "SnsTopicName": "sns_topic_name",
            "IncludeGlobalServiceEvents": "include_global_service_events",
            "IsMultiRegionTrail": "is_multi_region_trail",
            "LogFileValidationEnabled": "enable_logfile_validation",
            "CloudWatchLogsLogGroupArn": "cloud_watch_logs_loggroup_arn",
            "CloudWatchLogsRoleArn": "cloud_watch_logs_role_arn",
            "KmsKeyId": "kms_key_id",
            "IsOrganizationTrail": "is_organization_trail",
            "TrailARN": "trail_arn",
            "Tags": "tags",
            "IsLogging": "is_logging",
            "EventSelectors": "event_selectors",
            "AdvancedEventSelectors": "advanced_event_selectors",
            "InsightSelectors": "insight_selectors",
        }
    )

    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}

    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    ret_tag = await hub.exec.boto3.client.cloudtrail.list_tags(
        ctx, ResourceIdList=[raw_resource.get("TrailARN")]
    )
    if ret_tag["result"]:
        resource_translated["tags"] = (
            ret_tag.get("ret").get("ResourceTagList")[0].get("TagsList")
        )

    ret_trail_status = await hub.exec.boto3.client.cloudtrail.get_trail_status(
        ctx, Name=raw_resource.get("TrailARN")
    )

    if ret_trail_status["result"]:
        resource_translated["is_logging"] = ret_trail_status.get("ret").get("IsLogging")

    ret_event_selectors = await hub.exec.boto3.client.cloudtrail.get_event_selectors(
        ctx, TrailName=raw_resource.get("TrailARN")
    )

    if ret_event_selectors["result"]:
        resource_translated["event_selectors"] = ret_event_selectors.get("ret").get(
            "EventSelectors"
        )
        resource_translated["advanced_event_selectors"] = ret_event_selectors.get(
            "ret"
        ).get("AdvancedEventSelectors")

    ret_insight_selectors = (
        await hub.exec.boto3.client.cloudtrail.get_insight_selectors(
            ctx, TrailName=raw_resource.get("TrailARN")
        )
    )

    if ret_insight_selectors["result"]:
        resource_translated["insight_selectors"] = ret_insight_selectors.get("ret").get(
            "InsightSelectors"
        )

    return resource_translated


def update_plan_state(
    hub, plan_state: Dict[str, Any], update_ret: Dict[str, Any]
) -> Dict[str, Any]:
    if update_ret:
        for key, value in update_ret["ret"].items():
            plan_state[key] = value
    return plan_state
