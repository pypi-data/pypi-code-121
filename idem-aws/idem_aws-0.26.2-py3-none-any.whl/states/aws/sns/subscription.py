import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]

TREQ = {
    "present": {
        "require": [
            "aws.sns.topic.present",
        ],
    },
}


async def present(
    hub,
    ctx,
    name: str,
    topic_arn: str,
    protocol: str,
    endpoint: str,
    resource_id: str = None,
    attributes: Dict = None,
    return_subscription_arn: bool = None,
) -> Dict[str, Any]:
    r"""

    Creates a new endpoint subscription to a topic.If the endpoint type is HTTP/S or email, or if the endpoint and
    the topic are not in the same Amazon Web Services account,For http and email protocols the endpoint owner must
    run the ConfirmSubscription action to confirm the subscription.

    Args:
        hub:
        ctx:
        name(Text): The idem name for the resource
        topic_arn(Text): The ARN of the topic to which the subscription should be added
        protocol(Text): The protocol that you want to use.Supported protocols are:http,https,email,email-json,
                                  sms,sqs,application,lambda,firehose
        endpoint(Text): The endpoint that you want to receive notifications.Endpoints vary by protocol
        resource_id(Text, optional): The AWS resource identifier, here it is resource arn
        attributes(Dict, optional): Attributes of the subscription
        return_subscription_arn(bool, optional): A bool value to specify if the subscription_arn should be return after
                                                creation.By default,it is false i.e. subscription_arn is not returned.


    Request Syntax:
        [subscription-name]:
          aws.sns.subscription.present:
          - topic_arn: 'string'
          - protocol: 'string'
          - endpoint: 'string'
          - resource_id: 'string'
          - attributes: 'dict'
          - return_subscription_arn: 'bool'


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            subscription-name:
              aws.sns.subscription.present:
                - topic_arn: arn:aws:sns:eu-west-3:537227425989:test-topic
                - protocol: sms
                - endpoint: "+911234567890"
                - attributes:
                    DeliveryPolicy: '{"healthyRetryPolicy": {"minDelayTarget": 10,"maxDelayTarget": 30,"numRetries": 10,"numMaxDelayRetries": 7,"numNoDelayRetries": 0,"numMinDelayRetries": 3,"backoffFunction": "linear"},"sicklyRetryPolicy": null,"throttlePolicy": null,"guaranteed": false}'
                    FilterPolicy: '{"pets": ["dog", "cat"]}'
                - return_subscription_arn: True
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False
    plan_state = None
    # Standardise JSON string format
    if attributes:
        for key, value in attributes.items():
            attributes[key] = hub.tool.aws.sns.conversion_utils.standardise_json(value)

    if resource_id:
        resource = hub.tool.boto3.resource.create(
            ctx, "sns", "Subscription", arn=resource_id
        )
        before = await hub.tool.boto3.resource.describe(resource)

    if before:
        try:
            result[
                "old_state"
            ] = hub.tool.aws.sns.conversion_utils.convert_raw_subscription_to_present(
                raw_resource=before, idem_resource_name=name
            )

            plan_state = copy.deepcopy(result["old_state"])
            old_attributes = plan_state.get("attributes")

            if attributes is not None:
                # Update Attributes
                update_attributes_ret = (
                    await hub.exec.aws.sns.attributes.update_subscription_attributes(
                        ctx=ctx,
                        resource_arn=resource_id,
                        old_attributes=old_attributes,
                        new_attributes=attributes,
                    )
                )
                if not update_attributes_ret["result"]:
                    result["comment"] = update_attributes_ret["comment"]
                    result["result"] = False
                    return result
                resource_updated = resource_updated or bool(
                    update_attributes_ret["ret"]
                )
                result["comment"] = result["comment"] + update_attributes_ret["comment"]

                if ctx.get("test", False) and update_attributes_ret["ret"]:
                    plan_state["attributes"] = update_attributes_ret["ret"].get(
                        "updated_attributes"
                    )

            else:
                result["comment"] = (f"aws.sns.subscription '{name}' already exists",)

        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "topic_arn": topic_arn,
                    "protocol": protocol,
                    "endpoint": endpoint,
                    "attributes": attributes,
                    "return_subscription_arn": return_subscription_arn,
                },
            )
            result["comment"] = (f"Would create aws.sns.subscription '{name}'",)
            return result
        try:
            ret = await hub.exec.boto3.client.sns.subscribe(
                ctx,
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint,
                Attributes=attributes,
                ReturnSubscriptionArn=True,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            resource_id = ret["ret"].get("SubscriptionArn")
            result["comment"] = (f"Created aws.sns.subscription '{name}'",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif (not before) or resource_updated:
            resource = hub.tool.boto3.resource.create(
                ctx, "sns", "Subscription", arn=resource_id
            )
            after = await hub.tool.boto3.resource.describe(resource)
            result[
                "new_state"
            ] = hub.tool.aws.sns.conversion_utils.convert_raw_subscription_to_present(
                raw_resource=after, idem_resource_name=name
            )
        else:
            result["new_state"] = copy.deepcopy(result["old_state"])
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
    return result


async def absent(hub, ctx, name: str, resource_id: str) -> Dict[str, Any]:
    r"""
    Deletes the specified subscription. This action is idempotent, so deleting a topic that does not exist
    does not result in an error.

    Args:
        name(Text): The name of the state.
        resource_id(Text): The AWS resource identifier i.e. resource arn

    Request Syntax:
        [subscription-name]:
          aws.sns.subscription.absent:
          - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            test-subscription:
              aws.sns.subscription.absent:
              - resource_id: arn:aws:sns:eu-west-3:537227425989:test-topic:9c0fd640-7fc6-4888-bc08-f0a497a6237f
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None

    # There is a delay with describe() call, to check if the resource is in list_subscriptions() before describe()
    ret = await hub.exec.boto3.client.sns.list_subscriptions(ctx)
    if not ret["result"]:
        result["result"] = False
        result["comment"] = ret["comment"]
        return result
    for subscription in ret["ret"]["Subscriptions"]:
        if subscription.get("SubscriptionArn") == resource_id:
            resource = hub.tool.boto3.resource.create(
                ctx, "sns", "Subscription", arn=resource_id
            )
            before = await hub.tool.boto3.resource.describe(resource)
            break

    if not before:
        result["comment"] = (f"aws.sns.subscription '{name}' already absent",)

    else:
        result[
            "old_state"
        ] = hub.tool.aws.sns.conversion_utils.convert_raw_subscription_to_present(
            raw_resource=before, idem_resource_name=name
        )
        if ctx.get("test", False):
            result["comment"] = (f"Would delete aws.sns.subscription '{name}'",)
            return result
        try:
            ret = await hub.exec.boto3.client.sns.unsubscribe(
                ctx, SubscriptionArn=resource_id
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
            result["comment"] = (f"Deleted aws.sns.subscription '{name}'",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function
    Describes list of all the subscriptions present in all topics


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.sns.subscription
    """

    result = {}
    ret = await hub.exec.boto3.client.sns.list_subscriptions(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe subscriptions {ret['comment']}")
        return {}

    for subscription in ret["ret"]["Subscriptions"]:
        # Including fields to match the 'present' function parameters
        resource_id = subscription.get("SubscriptionArn")
        # Few deleted subscriptions might take 2-3 days to be removed from the list.
        # And few subscriptions might not be confirmed by endpoint yet.
        if resource_id == "Deleted" or resource_id == "PendingConfirmation":
            continue
        # Attributes are not present in the return value of list_subscriptions
        resource = hub.tool.boto3.resource.create(
            ctx, "sns", "Subscription", arn=resource_id
        )
        raw_resource = await hub.tool.boto3.resource.describe(resource)
        resource_translated = (
            hub.tool.aws.sns.conversion_utils.convert_raw_subscription_to_present(
                raw_resource=raw_resource, idem_resource_name=resource_id
            )
        )
        result[resource_id] = {
            "aws.sns.subscription.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }
    return result
