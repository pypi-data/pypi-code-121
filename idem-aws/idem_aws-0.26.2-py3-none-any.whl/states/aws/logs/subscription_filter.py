import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    log_group_name: str,
    filter_pattern: str,
    destination_arn: str,
    resource_id: str = None,
    role_arn: str = None,
    distribution: str = None,
) -> Dict[str, Any]:
    r"""

    Creates or updates a subscription filter and associates it with the specified log group. Subscription filters
    allow you to subscribe to a real-time stream of log events ingested through PutLogEvents and have them delivered
    to a specific destination. When log events are sent to the receiving service, they are Base64 encoded and
    compressed with the gzip format. The following destinations are supported for subscription filters:   An Amazon
    Kinesis stream belonging to the same account as the subscription filter, for same-account delivery.   A logical
    destination that belongs to a different account, for cross-account delivery.   An Amazon Kinesis Firehose
    delivery stream that belongs to the same account as the subscription filter, for same-account delivery.   An
    Lambda function that belongs to the same account as the subscription filter, for same-account delivery.   Each
    log group can have up to two subscription filters associated with it. If you are updating an existing filter,
    you must specify the correct name in filterName.  To perform a PutSubscriptionFilter operation, you must also
    have the iam:PassRole permission.

    Args:
        name(Text): An Idem name of the resource.
        log_group_name(Text): The name of the log group.
        filter_pattern(Text): A filter pattern for subscribing to a filtered stream of log events.
        destination_arn(Text): The ARN of the destination to deliver matching log events to. Currently, the supported
            destinations are:   An Amazon Kinesis stream belonging to the same account as the subscription
            filter, for same-account delivery.   A logical destination (specified using an ARN) belonging to
            a different account, for cross-account delivery. If you are setting up a cross-account
            subscription, the destination must have an IAM policy associated with it that allows the sender
            to send logs to the destination. For more information, see PutDestinationPolicy.   An Amazon
            Kinesis Firehose delivery stream belonging to the same account as the subscription filter, for
            same-account delivery.   A Lambda function belonging to the same account as the subscription
            filter, for same-account delivery.
        resource_id(Text, optional): AWS logs Subscription filter name. Defaults to None.
        role_arn(Text, optional): The ARN of an IAM role that grants CloudWatch Logs permissions to deliver ingested log events to
            the destination stream. You don't need to provide the ARN when you are working with a logical
            destination for cross-account delivery. Defaults to None.
        distribution(Text, optional): The method used to distribute log data to the destination. By default, log data is grouped by
            log stream, but the grouping can be set to random for a more even distribution. This property is
            only applicable when the destination is an Amazon Kinesis stream. Defaults to None.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_present:
              aws.logs.subscription_filter.present:
                - name: value
                - log_group_name: value
                - filter_name: value
                - filter_pattern: value
                - role_arn: value
                - destination_arn: value
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    current_state = {}
    desired_state = {
        "name": name,
        "resource_id": resource_id,
        "log_group_name": log_group_name,
        "filter_pattern": filter_pattern,
        "destination_arn": destination_arn,
        "role_arn": role_arn,
        "distribution": distribution,
    }
    resource_updated = False
    if resource_id:
        ret = await hub.exec.boto3.client.logs.describe_subscription_filters(
            ctx, logGroupName=log_group_name, filterNamePrefix=resource_id
        )
        if not ret["result"]:
            result["result"] = False
            result["comment"] = ret["comment"]
            return result
        if ret["ret"]["subscriptionFilters"]:
            before = ret["ret"]["subscriptionFilters"][0]

    if before:
        current_state = hub.tool.aws.logs.subscription_filter_utils.convert_raw_subscription_filter_to_present(
            before, name
        )
        result["old_state"] = current_state

        resource_updated = (
            hub.tool.aws.logs.subscription_filter_utils.is_subscription_filter_updated(
                current_state, desired_state
            )
        )
        if not resource_updated:
            result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
                resource_type="aws.logs.subscription_filter", name=name
            )
            result["new_state"] = copy.deepcopy(result["old_state"])
            return result
    if (not before) or resource_updated:
        if not ctx.get("test", False):
            ret = await hub.exec.boto3.client.logs.put_subscription_filter(
                ctx,
                logGroupName=log_group_name,
                filterName=name,
                filterPattern=filter_pattern,
                destinationArn=destination_arn,
                roleArn=role_arn,
                distribution=distribution,
            )
            if not ret["result"]:
                result["result"] = ret["result"]
                result["comment"] = ret["comment"]
                return result
            if resource_updated:
                result["comment"] = hub.tool.aws.comment_utils.update_comment(
                    resource_type="aws.logs.subscription_filter", name=name
                )
            else:
                result["comment"] = hub.tool.aws.comment_utils.create_comment(
                    resource_type="aws.logs.subscription_filter", name=name
                )
        else:
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state=current_state,
                desired_state=desired_state,
            )
            if resource_updated:
                result["comment"] = hub.tool.aws.comment_utils.would_update_comment(
                    resource_type="aws.logs.subscription_filter", name=name
                )
            else:
                result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
                    resource_type="aws.logs.subscription_filter", name=name
                )
            return result

    if (not before) or resource_updated:
        resource_id = resource_id if resource_id else name
        ret = await hub.exec.boto3.client.logs.describe_subscription_filters(
            ctx, logGroupName=log_group_name, filterNamePrefix=resource_id
        )
        if not ret["result"]:
            result["result"] = False
            result["comment"] = ret["comment"]
            return result

        if ret["ret"]["subscriptionFilters"]:
            after = ret["ret"]["subscriptionFilters"][0]
        result[
            "new_state"
        ] = hub.tool.aws.logs.subscription_filter_utils.convert_raw_subscription_filter_to_present(
            after, name
        )

    return result


async def absent(
    hub,
    ctx,
    name: str,
    log_group_name: str,
    resource_id: str = None,
) -> Dict[str, Any]:
    r"""

    Deletes the specified subscription filter.

    Args:
        name(Text): An Idem name of the resource.
        log_group_name(Text): The name of the log group.
        resource_id(Text, optional): AWS logs Subscription filter name. Defaults to None.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.logs.subscription_filter.absent:
                - name: value
                - resource_id: value
                - log_group_name: value
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.logs.subscription_filter", name=name
        )
        return result
    ret = await hub.exec.boto3.client.logs.describe_subscription_filters(
        ctx, logGroupName=log_group_name, filterNamePrefix=resource_id
    )
    if not ret["result"]:
        result["result"] = False
        result["comment"] = ret["comment"]
        return result
    if ret["ret"]["subscriptionFilters"]:
        before = ret["ret"]["subscriptionFilters"][0]

    if not before:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.logs.subscription_filter", name=name
        )
    else:
        result[
            "old_state"
        ] = hub.tool.aws.logs.subscription_filter_utils.convert_raw_subscription_filter_to_present(
            raw_resource=before, idem_resource_name=name
        )
        if ctx.get("test", False):
            result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
                resource_type="aws.logs.subscription_filter", name=name
            )
            return result
        ret = await hub.exec.boto3.client.logs.delete_subscription_filter(
            ctx, logGroupName=log_group_name, filterName=resource_id
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result
        result["comment"] = hub.tool.aws.comment_utils.delete_comment(
            resource_type="aws.logs.subscription_filter", name=name
        )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""

    Describe the resource in a way that can be recreated/managed with the corresponding "present" function


    Lists the subscription filters for all the log groups.


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.logs.subscription_filter
    """

    result = {}
    log_group_ret = await hub.exec.boto3.client.logs.describe_log_groups(ctx)
    if not log_group_ret["result"]:
        hub.log.debug(f"Could not describe log groups {log_group_ret['comment']}")
        return {}

    for log_group in log_group_ret["ret"]["logGroups"]:
        ret = await hub.exec.boto3.client.logs.describe_subscription_filters(
            ctx, logGroupName=log_group["logGroupName"]
        )
        if not ret["result"]:
            hub.log.debug(
                f"Could not describe subscription_filters in log group {log_group['logGroupName']}.Will skip this log group {ret['comment']}"
            )
            continue
        for subscription_filter in ret["ret"]["subscriptionFilters"]:
            resource_id = subscription_filter.get("filterName")
            translated_resource = hub.tool.aws.logs.subscription_filter_utils.convert_raw_subscription_filter_to_present(
                subscription_filter, resource_id
            )
            result[resource_id] = {
                "aws.logs.subscription_filter.present": [
                    {parameter_key: parameter_value}
                    for parameter_key, parameter_value in translated_resource.items()
                ]
            }
    return result
