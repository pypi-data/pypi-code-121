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
    policy: str,
    resource_id: str = None,
) -> Dict[str, Any]:
    r"""

    Updates the topic's policy attribute. A topic can have a single policy, checks for changes in policy attribute and
    updates it if required.

    Args:
        hub:
        ctx:
        name(Text): The idem name for the topic_policy
        topic_arn(Text): The ARN of the topic for which the policy should be updated
        policy(Text): Topic policy, in json string format
        resource_id(Text, optional): Topic arn and 'policy' keyword separated with '-'



    Request Syntax:
        [topic-policy-name]:
          aws.sns.topic_policy.present:
          - name: 'string'
          - topic_arn: 'string'
          - policy: 'string'
          - resource_id: 'string'


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            topic-policy-name:
              aws.sns.topic_policy.present:
                - name: topic-policy-name
                - topic_arn: arn:aws:sns:eu-west-3:537227425989:test-topic
                - policy: '{"Version": "2012-10-17", "Id": "id-1", "Statement": [{"Sid":
                           "__default_statement_ID", "Effect": "Allow", "Principal": {"AWS": "*"}, "Action":
                           ["SNS:GetTopicAttributes", "SNS:SetTopicAttributes", "SNS:AddPermission", "SNS:RemovePermission",
                           "SNS:DeleteTopic", "SNS:Subscribe", "SNS:ListSubscriptionsByTopic", "SNS:Publish"],
                           "Resource": "arn:aws:sns:eu-west-3:537227425989:test-topic", "Condition": {"StringEquals":
                           {"AWS:SourceOwner": "537227425989"}}}]}'
                - resource_id: arn:aws:sns:eu-west-3:537227425989:test-topic-policy
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    resource_updated = False
    plan_state = None

    # Standardise JSON string format
    policy = hub.tool.aws.sns.conversion_utils.standardise_json(policy)

    before = await hub.exec.boto3.client.sns.get_topic_attributes(
        ctx, TopicArn=topic_arn
    )
    if before:
        result[
            "old_state"
        ] = hub.tool.aws.sns.conversion_utils.convert_raw_topic_policy_to_present(
            raw_resource=before, idem_resource_name=name
        )

        plan_state = copy.deepcopy(result["old_state"])
        old_policy = plan_state.get("policy")

        if policy is not None:
            # Update policy attribute in topic
            if not hub.tool.aws.state_comparison_utils.is_json_identical(
                old_policy, policy
            ):
                if ctx.get("test", False):
                    plan_state["policy"] = policy
                    result["comment"] = (
                        f"Would update policy attribute of aws.sns.topic '{topic_arn}'",
                    )
                else:
                    update_attributes_ret = (
                        await hub.exec.boto3.client.sns.set_topic_attributes(
                            ctx,
                            TopicArn=topic_arn,
                            AttributeName="Policy",
                            AttributeValue=policy,
                        )
                    )
                    if not update_attributes_ret["result"]:
                        result["comment"] = update_attributes_ret["comment"]
                        result["result"] = False
                        return result
                    resource_updated = True
                    result["comment"] = (
                        f"Updated policy attribute of aws.sns.topic '{topic_arn}'",
                    )

            else:
                result["comment"] = (
                    f"No changes required for aws.sns.topic_policy '{name}'",
                )

    else:
        result["comment"] = (f"aws.sns.topic with '{topic_arn}' ARN, does not exist",)
        result["result"] = False

    if ctx.get("test", False):
        result["new_state"] = plan_state
    elif resource_updated:
        after = await hub.exec.boto3.client.sns.get_topic_attributes(
            ctx, TopicArn=topic_arn
        )
        result[
            "new_state"
        ] = hub.tool.aws.sns.conversion_utils.convert_raw_topic_policy_to_present(
            raw_resource=after, idem_resource_name=name
        )
    else:
        result["new_state"] = copy.deepcopy(result["old_state"])
    return result


async def absent(hub, ctx, name: str, resource_id: str) -> Dict[str, Any]:
    r"""
    Deletes the current topic policy and replace with the default value. This action is idempotent, so deleting a topic's policy that does not exist
    does not result in an error.

    Args:
        name(Text): The idem name of the topic_policy.
        resource_id(Text): Topic arn and 'policy' keyword separated with '-'

    Request Syntax:
        [topic-policy-name]:
          aws.sns.topic_policy.absent:
          - name: 'string'
          - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            test-topic-policy:
              aws.sns.topic_policy.absent:
              - name: test-topic-policy
              - resource_id: arn:aws:sns:eu-west-3:537227425989:test-topic-policy
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    topic_arn = resource_id.split("-policy")[0]
    before = await hub.exec.boto3.client.sns.get_topic_attributes(
        ctx, TopicArn=topic_arn
    )

    if not before:
        result["comment"] = (f"aws.sns.topic with '{topic_arn}' ARN does not exist",)

    else:
        result[
            "old_state"
        ] = hub.tool.aws.sns.conversion_utils.convert_raw_topic_policy_to_present(
            raw_resource=before, idem_resource_name=name
        )
        plan_state = copy.deepcopy(result["old_state"])
        default_policy = hub.tool.aws.sns.sns_utils.get_default_topic_policy(topic_arn)
        if ctx.get("test", False):
            plan_state["policy"] = default_policy
            result["new_state"] = plan_state
            result["comment"] = (f"Would delete aws.sns.topic_policy '{name}'",)
            return result

        # Deleting topic policy is not possible so replacing it with the default policy
        ret = await hub.exec.boto3.client.sns.set_topic_attributes(
            ctx,
            TopicArn=topic_arn,
            AttributeName="Policy",
            AttributeValue=default_policy,
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            result["result"] = False
            return result

        after = await hub.exec.boto3.client.sns.get_topic_attributes(
            ctx, TopicArn=topic_arn
        )
        result[
            "new_state"
        ] = hub.tool.aws.sns.conversion_utils.convert_raw_topic_policy_to_present(
            raw_resource=after, idem_resource_name=name
        )
        result["comment"] = (
            f"Deleted aws.sns.topic_policy for aws.sns.topic '{topic_arn}'",
        )

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function
    Describes list of all the topic policy


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.sns.topic_policy
    """
    result = {}
    ret = await hub.exec.boto3.client.sns.list_topics(ctx)

    if not ret["result"]:
        hub.log.debug(f"Could not describe topic {ret['comment']}")
        return {}

    for topic in ret["ret"]["Topics"]:
        # Including fields to match the 'present' function parameters
        topic_arn = topic["TopicArn"]
        resource_id = topic_arn + "-policy"
        idem_resource_name = resource_id

        raw_resource = await hub.exec.boto3.client.sns.get_topic_attributes(
            ctx, TopicArn=topic_arn
        )

        resource_translated = (
            hub.tool.aws.sns.conversion_utils.convert_raw_topic_policy_to_present(
                raw_resource,
                idem_resource_name,
            )
        )
        result[resource_id] = {
            "aws.sns.topic_policy.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }

    return result
