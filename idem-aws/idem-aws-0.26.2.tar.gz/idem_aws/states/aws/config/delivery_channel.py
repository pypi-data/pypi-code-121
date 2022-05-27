"""
hub.exec.boto3.client.config.put_delivery_channel
hub.exec.boto3.client.config.delete_delete_channel
hub.exec.boto3.client.config.describe_delivery_channels

"""
import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    s3_bucket_name: str,
    resource_id: str = None,
    s3_key_prefix: str = None,
    s3_kms_key_arn: str = None,
    sns_topic_arn: str = None,
    config_snapshot_delivery_properties: Dict = None,
) -> Dict[str, Any]:
    """
    Add or update the configuration delivery channel object that delivers the configuration information to an Amazon S3 bucket
    and to an Amazon SNS topic. For more information about delivery channel, please see AWS Config services
    Args:
        name(Text): An Idem name of the delivery channel.
        s3_bucket_name (Text): The name of the Amazon S3 bucket to which Config delivers configuration snapshots and configuration history files
        resource_id (Text, Optional): The resource Id of the delivery channel.
        s3_key_prefix (Text, Optional): The prefix for the specified Amazon S3 bucket.
        s3_kms_key_arn (Text, Optional): The Amazon Resource Name (ARN) of the Key Management Service (KMS ) KMS key (KMS key) used to encrypt objects delivered by Config.
        sns_topic_arn (Text, Optional): The Amazon Resource Name (ARN) of the Amazon SNS topic to which Config sends notifications about configuration changes.
        config_snapshot_delivery_properties (Dict, Optional):
            delivery_frequency (Text): The frequency with which Config delivers configuration snapshots.

    Request syntax:
        [aws-config-delivery_channel]:
          aws.config.delivery_channel.present:
          - name: 'string'
          - resource_id: 'string'
          - s3_bucket_name 'string'
          - s3_key_prefix: 'string'
          - s3_kms_key_arn: 'string'
          - sns_topic_arn: 'string'
          - config_snapshot_delivery_properties: dict
            delivery_frequency: 'string'

    Returns:
         Dict[str, Any]

    Examples:
        .. code-block:: sls
            aws-config-delivery_channel:
              aws.config.delivery_channel.present:
                - name: 'delivery-channel'
                - resource_id: 'delivery-channel'
                - s3_bucket_name 'Test-S3'
                - s3_key_prefix: 'S3-prefix'
                - s3_kms_key_arn: 'Test-Kms-Key'
                - sns_topic_arn: 'Test-Topic'
                - config_snapshot_delivery_properties:
                  delivery_frequency: 'One_Hour'
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False
    update_payload = {}
    update_config_snapshot_delivery_properties = None
    resource_id = resource_id if resource_id else name
    before = await hub.exec.boto3.client.config.describe_delivery_channels(
        ctx, DeliveryChannelNames=[resource_id]
    )
    if before:
        result[
            "old_state"
        ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_delivery_channel_to_present(
            ctx,
            raw_resource=before["ret"]["DeliveryChannels"][0],
            idem_resource_name=name,
        )
        plan_state = copy.deepcopy(result["old_state"])
        # updating config_snapshot_delivery_properties
        if config_snapshot_delivery_properties is not None:
            update_config_snapshot_delivery_properties = (
                config_snapshot_delivery_properties
            )
        update_payload = await hub.exec.aws.config.delivery_channel.get_updated_payload_delivery_channel(
            ctx,
            resource_id=resource_id,
            before=before["ret"]["DeliveryChannels"][0],
            s3_bucket_name=s3_bucket_name,
            s3_key_prefix=s3_key_prefix,
            s3_kms_key_arn=s3_kms_key_arn,
            sns_topic_arn=sns_topic_arn,
            config_snapshot_delivery_properties=update_config_snapshot_delivery_properties,
        )

        if update_payload["ret"]:
            resource_updated = True
            if not ctx.get("test", False):
                update_ret = await hub.exec.boto3.client.config.put_delivery_channel(
                    ctx=ctx, DeliveryChannel=update_payload["ret"]
                )
                if not update_ret["result"]:
                    result["comment"] = result["comment"] + update_ret["comment"]
                    result["result"] = False
                    return result

                result["comment"] = (f"Updated aws.config.delivery_channel '{name}'",)
                result["result"] = update_ret["result"]
            else:
                for key, value in update_payload["ret"].items():
                    plan_state[key] = value

        if not result["result"]:
            result["comment"] = result["comment"] + (f"{name} already exists",)
    else:
        delivery_props = {}
        dc_payload = {"name": name, "s3BucketName": s3_bucket_name}
        if sns_topic_arn:
            dc_payload["snsTopicARN"] = sns_topic_arn
        if s3_key_prefix:
            dc_payload["s3KeyPrefix"] = s3_key_prefix
        if s3_kms_key_arn:
            dc_payload["s3KmsKeyArn"] = s3_kms_key_arn
        if config_snapshot_delivery_properties:
            delivery_props["deliveryFrequency"] = config_snapshot_delivery_properties[
                "delivery_frequency"
            ]
            dc_payload["configSnapshotDeliveryProperties"] = delivery_props
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={}, desired_state=dc_payload
            )
            result["comment"] = (f"Would create aws.config.delivery_channel '{name}'",)
            return result

        ret = await hub.exec.boto3.client.config.put_delivery_channel(
            ctx, DeliveryChannel=dc_payload
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"] + ret["comment"]
            return result
            # resource_id = name
        result["comment"] = result["comment"] + (
            f"Created aws.config.delivery_channel '{name}'",
        )

    if ctx.get("test", False):
        result["new_state"] = plan_state
        if not resource_updated:
            result["comment"] = f"Would create aws.config.delivery_channel '{name}'"
        else:
            result["comment"] = (f"Would update aws.config.delivery_channel '{name}'",)
    elif (not before) or resource_updated:
        after = await hub.exec.boto3.client.config.describe_delivery_channels(
            ctx, DeliveryChannelNames=[resource_id]
        )
        result[
            "new_state"
        ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_delivery_channel_to_present(
            ctx,
            raw_resource=after["ret"]["DeliveryChannels"][0],
            idem_resource_name=name,
        )
    else:
        result["new_state"] = copy.deepcopy(result["old_state"])
    return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
) -> Dict[str, Any]:
    """
    Deletes the specified delivery channel Before you can delete the delivery channel, you must stop the configuration recorder
    by using the StopConfigurationRecorder action.

    Args:
        name(Text): An Idem name of the rule.
        resource_id(Text, optional): AWS Config delivery channel Name. Idem automatically considers this resource being absent
         if this field is not specified.

    Returns:
          Dict[str, Any]

    Examples:
          .. code-block:: sls

            ec2-instance-no-public-ip:
              aws.config.delivery_channel.absent:
              - name: ec2-instance-no-public-ip
              - resource_id: ec2-instance-no-public-ip

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    resource_id = resource_id if resource_id else name
    # if not resource_id:
    #     result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
    #         resource_type="aws.config.delivery_channel", name=name
    #     )
    #     return result
    before = await hub.exec.boto3.client.config.describe_delivery_channels(
        ctx, DeliveryChannelNames=[resource_id]
    )
    if not before:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.config.delivery_channel", name=name
        )
    elif ctx.get("test", False):
        result[
            "old_state"
        ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_delivery_channel_to_present(
            ctx,
            raw_resource=before["ret"]["DeliveryChannels"][0],
            idem_resource_name=resource_id,
        )
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.config.delivery_channel", name=resource_id
        )
        return result
    else:
        try:
            result[
                "old_state"
            ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_delivery_channel_to_present(
                ctx,
                raw_resource=before["ret"]["DeliveryChannels"][0],
                idem_resource_name=resource_id,
            )

            ret = await hub.exec.boto3.client.config.delete_delivery_channel(
                ctx, DeliveryChannelName=resource_id
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            result["comment"] = hub.tool.aws.comment_utils.delete_comment(
                resource_type="aws.config.delivery_channel", name=name
            )
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    """
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Return details about your delivery channel.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.config.delivery_channel
    """
    result = {}
    ret = await hub.exec.boto3.client.config.describe_delivery_channels(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe Delivery Channels {ret['comment']}")
        return {}

    for resource in ret["ret"]["DeliveryChannels"]:
        resource_id = resource.get("name")
        resource_translated = await hub.tool.aws.config.conversion_utils.convert_raw_config_delivery_channel_to_present(
            ctx, raw_resource=resource, idem_resource_name=resource_id
        )
        result[resource_id] = {
            "aws.config.delivery_channel.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }
    return result
