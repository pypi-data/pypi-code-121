import json
from typing import Any
from typing import Dict


def convert_raw_bucket_notification_to_present(
    hub, raw_resource: Dict[str, Any], bucket_name: str
) -> Dict[str, Any]:
    """
    Convert the s3 bucket notification configurations response to a common format

    Args:
        raw_resource: Dictionary of s3 bucket notification configurations
        bucket_name: Name of the bucket on which notification needs to be configured.

    Returns:
        A dictionary of s3 bucket notification configurations
    """
    translated_resource = {}
    raw_resource.pop("ResponseMetadata", None)

    if raw_resource:
        translated_resource["name"] = bucket_name
        translated_resource["resource_id"] = bucket_name + "-notifications"
        translated_resource["notifications"] = json.loads(json.dumps(raw_resource))
    return translated_resource


async def convert_raw_s3_to_present(
    hub, ctx, idem_resource_name: str = None
) -> Dict[str, Any]:
    """
    Convert the s3 bucket configurations response to a common format

    Args:
        idem_resource_name: Name of the bucket.

    Returns:
        Dict[str, Any]
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": idem_resource_name,
    }
    result = dict(comment=(), result=True, ret=None)
    ret = await hub.exec.boto3.client.s3.get_object_lock_configuration(
        ctx, Bucket=idem_resource_name
    )
    if not ret["result"]:
        result["comment"] = result["comment"] + ret["comment"]
    if ret["result"]:
        if ret["ret"]["ObjectLockConfiguration"]["ObjectLockEnabled"] == "Enabled":
            resource_translated["object_lock_enabled_for_bucket"] = True
        else:
            resource_translated["object_lock_enabled_for_bucket"] = False
    ret = await hub.exec.boto3.client.s3.get_bucket_location(
        ctx, Bucket=idem_resource_name
    )
    if not ret["result"]:
        result["comment"] = result["comment"] + ret["comment"]
    if ret["result"] and ret["ret"]["LocationConstraint"]:
        resource_translated["create_bucket_configuration"] = {
            "LocationConstraint": ret["ret"]["LocationConstraint"]
        }
    ret = await hub.exec.boto3.client.s3.get_bucket_ownership_controls(
        ctx, Bucket=idem_resource_name
    )
    if not ret["result"]:
        result["comment"] = result["comment"] + ret["comment"]
    if (
        ret["result"]
        and ret["ret"]["OwnershipControls"]
        and ret["ret"]["OwnershipControls"]["Rules"][0]["ObjectOwnership"]
    ):
        resource_translated["object_ownership"] = ret["ret"]["OwnershipControls"][
            "Rules"
        ][0]["ObjectOwnership"]
    ret = await hub.exec.boto3.client.s3.get_bucket_acl(ctx, Bucket=idem_resource_name)
    if not ret["result"]:
        result["comment"] = result["comment"] + ret["comment"]
    if ret["result"] and ret["ret"]["Grants"][0]["Permission"]:
        if ret["ret"]["Grants"][0]["Permission"] == "FULL_CONTROL":
            resource_translated["grant_full_control"] = "FULL_CONTROL"
        elif ret["ret"]["Grants"][0]["Permission"] == "READ":
            resource_translated["grant_read"] = "READ"
        elif ret["ret"]["Grants"][0]["Permission"] == "READ_ACP":
            resource_translated["grant_read_acp"] = "READ_ACP"
        elif ret["ret"]["Grants"][0]["Permission"] == "WRITE":
            resource_translated["grant_write"] = "WRITE"
        else:
            resource_translated["grant_write_acp"] = "WRITE_ACP"

    ret = await hub.exec.boto3.client.s3.get_bucket_tagging(
        ctx, Bucket=idem_resource_name
    )
    if not ret["result"]:
        result["comment"] = result["comment"] + ret["comment"]
    if ret["result"] and ret["ret"]["TagSet"]:
        resource_translated["tags"] = ret["ret"]["TagSet"]
    result["ret"] = resource_translated

    return result


def convert_raw_public_access_block_to_present(
    hub, bucket_name: str, public_access_block_configuration: Dict
) -> Dict[str, Any]:
    translated_resource = {
        "name": f"{bucket_name}-public-access-block",
        "bucket": bucket_name,
        "public_access_block_configuration": json.loads(
            json.dumps(public_access_block_configuration)
        ),
        "resource_id": bucket_name,
    }
    return translated_resource


def convert_raw_bucket_policy_to_present(
    hub, raw_resource: Dict[str, Any], bucket: str, name: str
) -> Dict[str, Any]:
    """
    Util function to convert the s3 bucket policy response to a common format

    Args:
        hub: required for functions in hub
        raw_resource: S3 bucket policy response
        bucket: Name of the bucket on which policy needs to be configured.

    Returns:
        A dictionary of s3 bucket notification configurations
    """
    translated_resource = {}
    raw_resource.pop("ResponseMetadata", None)

    if raw_resource:
        translated_resource["name"] = name
        translated_resource["resource_id"] = bucket + "-policy"
        translated_resource["bucket"] = bucket
        translated_resource["policy"] = raw_resource["Policy"]
    return translated_resource
