from typing import Dict

from dict_tools import differ


async def update_topic_attributes(
    hub,
    ctx,
    resource_arn: str,
    old_attributes: Dict[str, str],
    new_attributes: Dict[str, str],
):
    """
    Given old and new attributes of SNS topic the function updates the attributes.

    Args:
        hub:
        ctx:
        resource_arn(Text): AWS resource_arn of SNS topic
        old_attributes(Dict): old attribute of SNS topic
        new_attributes(Dict): new attribute of SNS topic

    """
    result = dict(comment=(), result=True, ret=None)
    attributes_diff = differ.deep_diff(old_attributes, new_attributes)
    attributes_to_update = attributes_diff.get("new")

    if ctx.get("test", False):
        result["ret"] = {"updated_attributes": attributes_to_update}
        result["comment"] = (f"Would Update attributes {attributes_to_update.keys()}",)
        return result

    else:
        if attributes_to_update:
            for key, value in attributes_to_update.items():
                ret = await hub.exec.boto3.client.sns.set_topic_attributes(
                    ctx, TopicArn=resource_arn, AttributeName=key, AttributeValue=value
                )
                if not ret["result"]:
                    result["comment"] = ret["comment"]
                    result["result"] = False
                    return result

            result["ret"] = {"updated_attributes": attributes_to_update}
            result["comment"] = (f"Updated attributes {attributes_to_update.keys()}",)
    return result


async def update_subscription_attributes(
    hub,
    ctx,
    resource_arn: str,
    old_attributes: Dict[str, str],
    new_attributes: Dict[str, str],
):
    """
    Given old and new attributes of SNS topic_subscription the function updates the attributes.

    Args:
        hub:
        ctx:
        resource_arn(Text): AWS resource_arn of SNS topic_subscription
        old_attributes(Dict): old attribute of SNS topic_subscription
        new_attributes(Dict): new attribute of SNS topic_subscription

    """
    result = dict(comment=(), result=True, ret=None)
    attributes_diff = differ.deep_diff(old_attributes, new_attributes)
    attributes_to_update = attributes_diff.get("new")

    if ctx.get("test", False):
        result["ret"] = {"updated_attributes": attributes_to_update}
        result["comment"] = (f"Would Update attributes {attributes_to_update.keys()}",)
        return result

    else:
        if attributes_to_update:
            for key, value in attributes_to_update.items():
                ret = await hub.exec.boto3.client.sns.set_subscription_attributes(
                    ctx,
                    SubscriptionArn=resource_arn,
                    AttributeName=key,
                    AttributeValue=value,
                )
                if not ret["result"]:
                    result["comment"] = ret["comment"]
                    result["result"] = False
                    return result

            result["ret"] = {"updated_attributes": attributes_to_update}
            result["comment"] = (f"Updated attributes {attributes_to_update.keys()}",)
    return result
