from typing import Any
from typing import Dict


async def get_updated_payload_delivery_channel(
    hub,
    ctx,
    resource_id: str,
    before: Dict[str, Any],
    s3_bucket_name: str,
    s3_key_prefix: str,
    s3_kms_key_arn: str,
    sns_topic_arn: str,
    config_snapshot_delivery_properties: Dict[str, Any],
):
    """
    Get Updated payload of delivery channel of AWS Config

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        resource_id: AWS Delivery channel name
        before: Contains current configuration for the resource
        s3_bucket_name: String. Specified S3 Bucket name for delivery channel
        s3_key_prefix: String. The prefix for the specified Amazon S3 bucket.
        s3_kms_key_arn: String. ARN of the Key Management Service (KMS ) KMS key (KMS key) used to encrypt objects
        sns_topic_arn: String. Amazon SNS topic to which Config sends notifications about configuration changes.
        config_snapshot_delivery_properties: Dict.
            delivery_frequency: String. The frequency with which Config delivers configuration snapshots.

    Returns:
        {"result": True|False, "comment": Tuple, "ret": Dict}
    """
    result = dict(comment=(), result=True, ret=None)

    update_payload = {}
    delivery_props = {}

    if s3_bucket_name and before.get("s3_bucket_name") != s3_bucket_name:
        update_payload["s3BucketName"] = s3_bucket_name

    if s3_key_prefix and before.get("s3_key_prefix") != s3_key_prefix:
        update_payload["s3KeyPrefix"] = s3_key_prefix

    if s3_kms_key_arn and before.get("s3_kms_key_arn") != s3_kms_key_arn:
        update_payload["s3KmsKeyArn"] = s3_kms_key_arn

    if sns_topic_arn and before.get("sns_topic_arn") != sns_topic_arn:
        update_payload["snsTopicARN"] = sns_topic_arn

    if (
        config_snapshot_delivery_properties
        and not before.get("configSnapshotDeliveryProperties")
    ) or (
        config_snapshot_delivery_properties
        and before.get("configSnapshotDeliveryProperties")
        and before.get("configSnapshotDeliveryProperties").get("deliveryFrequency")
        != config_snapshot_delivery_properties.get("delivery_frequency")
    ):
        delivery_props["deliveryFrequency"] = config_snapshot_delivery_properties[
            "delivery_frequency"
        ]
        update_payload["configSnapshotDeliveryProperties"] = delivery_props

    update_payload["name"] = resource_id

    result["ret"] = update_payload
    result["result"] = True
    return result
