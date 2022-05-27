"""

hub.exec.boto3.client.events.delete_rule
hub.exec.boto3.client.events.describe_rule
hub.exec.boto3.client.events.disable_rule
hub.exec.boto3.client.events.enable_rule
hub.exec.boto3.client.events.list_rules
hub.exec.boto3.client.events.put_rule
"""
import copy
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    targets: List = None,
    schedule_expression: str = None,
    event_pattern: str = None,
    state: str = None,
    description: str = None,
    role_arn: str = None,
    event_bus_name: str = None,
    tags: List = None,
) -> Dict[str, Any]:
    r"""

    Enables the specified rule. If the rule does not exist, the operation fails. When you enable a rule, incoming
    events might not immediately start matching to a newly enabled rule. Allow a short period of time for changes to
    take effect.

    Args:
        hub:
        ctx:
        name(Text): A name, ID to identify the resource.
        resource_id(Text, Optional): The name of the AWS CloudWatch Events Rule.
        targets(List): The targets to update or add to the rule.
        schedule_expression (Text, Optional): Scheduling expression.
            For example, "cron(0 20 * * ? *)" or "rate(5 minutes)".
        event_pattern (Text, Optional): Rules use event patterns to select events and route them to targets. A pattern
            either matches an event or it doesn't. Event patterns are represented as JSON objects with a structure that
            is similar to that of events.
        state (Text, Optional): Indicates whether the rule is enabled or disabled.
        description (Text, Optional): A description of the rule.
        role_arn (Text, Optional): The Amazon Resource Name (ARN) of the IAM role associated with the rule.
            If you're setting an event bus in another account as the target and that account granted permission to your
            account through an organization instead of directly by the account ID, you must specify a RoleArn with proper
            permissions in the Target structure, instead of here in this parameter.
        event_bus_name (Text, Optional) : The name or ARN of the event bus to associate with this rule.
            If you omit this, the default event bus is used.
        tags(List, Optional): The list of key-value pairs to associate with the rule.
            * Key (string) [REQUIRED] : A string you can use to assign a value. The combination of tag keys and values
                can help you organize and categorize your resources.
            * Value (string) [REQUIRED] : The value for the specified tag key.

    Request Syntax:
        [cloudwatch-events-rule-id]:
          aws.events.rule.present:
            - name: event_rule
            - arn: arn:aws:events:us-west-1:000000000000:rule/qqqqqqq
            - state: ENABLED | DISABLED
            - schedule_expression: rate(5 minutes)
            - event_bus_name: default
            - tags:
              - Key: 'string'
                Value: 'string'


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            event_rule_id:
                aws.events.rule.present:
                  - name: event_rule
                  - arn: arn:aws:events:us-west-1:000000000000:rule/test
                  - state: ENABLED | DISABLED
                  - schedule_expression: rate(5 minutes)
                  - event_bus_name: default
                  - tags:
                    - Key: idem_test_event_rule1
                      Value: test value

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    are_tags_updated = False
    is_role_updated = False
    existing_tags = {}
    plan_state = {}
    rule_arn = None
    before = await hub.exec.boto3.client.events.describe_rule(ctx, Name=resource_id)
    if before["result"] and before["ret"]:
        result["comment"] = (f"'{name}' already exists",)
        rule_arn = before["ret"]["Arn"]
        tags_return = await hub.exec.boto3.client.events.list_tags_for_resource(
            ctx, ResourceARN=rule_arn
        )
        result["result"] = tags_return.get("result")
        if result["result"]:
            existing_tags = tags_return.get("ret").get("Tags")
        else:
            result["comment"] = result["comment"] + tags_return["comment"]
            return result

        resource_converted = await hub.tool.aws.events.conversion_utils.convert_raw_cloud_watch_rule_to_present(
            ctx,
            raw_resource=before["ret"],
            idem_resource_name=name,
            tags=existing_tags,
        )
        result["result"] = result["result"] and resource_converted["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + resource_converted["comment"]
        result["old_state"] = resource_converted["ret"]
        plan_state = copy.deepcopy(result["old_state"])

        update_return = await hub.exec.aws.events.rule.update_events_rule(
            ctx=ctx,
            old_targets=result["old_state"]["targets"],
            new_targets=targets,
            schedule_expression=schedule_expression,
            event_pattern=event_pattern,
            state=state,
            plan_state=plan_state,
            role_arn=role_arn,
            description=description,
            event_bus_name=event_bus_name,
            resource_id=resource_id,
        )
        result["result"] = result["result"] and update_return["result"]
        result["comment"] = result["comment"] + update_return["comment"]
        if result["result"]:
            is_role_updated = True

        if tags is not None:
            # Update tags
            update_tags_result = await hub.exec.aws.events.tag.update_tags(
                ctx=ctx,
                resource_id=rule_arn,
                old_tags=existing_tags,
                new_tags=tags,
            )
            result["comment"] = result["comment"] + update_tags_result["comment"]
            result["result"] = result["result"] and update_tags_result["result"]

            if not result["result"]:
                return result
            are_tags_updated = result["result"]

            if ctx.get("test", False) and (update_tags_result["ret"] is not None):
                plan_state["tags"] = update_tags_result["ret"].get("tags")
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "targets": targets,
                    "tags": tags,
                    "resource_id": name,
                    "schedule_expression": schedule_expression,
                    "event_pattern": event_pattern,
                    "description": description,
                    "event_bus_name": event_bus_name,
                    "role_arn": role_arn,
                    "state": state,
                },
            )
            result["comment"] = (f"Would create aws.events.rule '{name}'",)
            return result
        try:
            ret = await hub.exec.boto3.client.events.put_rule(
                ctx=ctx,
                Name=name,
                ScheduleExpression=schedule_expression,
                EventPattern=event_pattern,
                State=state,
                Description=description,
                RoleArn=role_arn,
                Tags=tags,
                EventBusName=event_bus_name,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + ret["comment"]
                return result
            if targets is not None:
                target_ret = await hub.exec.boto3.client.events.put_targets(
                    ctx=ctx,
                    Rule=name,
                    Targets=targets,
                    EventBusName=event_bus_name,
                )
                result["result"] = result["result"] and target_ret["result"]
                if not result["result"]:
                    result["comment"] = result["comment"] + ret["comment"]
                    return result
            resource_id = name
            rule_arn = ret["ret"]["RuleArn"]
            existing_tags = tags
            result["comment"] = (f"Created aws.events.rule '{name}'",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

    if ctx.get("test", False):
        result["new_state"] = plan_state
    elif not (before and before["result"]) or is_role_updated:
        after = await hub.exec.boto3.client.events.describe_rule(ctx, Name=resource_id)
        final_updated_tags = existing_tags
        if are_tags_updated:
            tags = await hub.exec.boto3.client.events.list_tags_for_resource(
                ctx, ResourceARN=rule_arn
            )
            if tags.get("result") and tags.get("ret"):
                final_updated_tags = tags.get("ret").get("Tags")
        resource_converted = await hub.tool.aws.events.conversion_utils.convert_raw_cloud_watch_rule_to_present(
            ctx,
            raw_resource=after["ret"],
            idem_resource_name=name,
            tags=final_updated_tags,
        )
        result["result"] = result["result"] and resource_converted["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + resource_converted["comment"]
        result["new_state"] = resource_converted["ret"]
    else:
        result["new_state"] = copy.deepcopy(result["old_state"])
    return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str,
    event_bus_name: str = None,
) -> Dict[str, Any]:
    r"""

    Deletes the specified rule. Before you can delete the rule, you must remove all targets, using RemoveTargets.
    When you delete a rule, incoming events might continue to match to the deleted rule. Allow a short period of
    time for changes to take effect. If you call delete rule multiple times for the same rule, all calls will
    succeed. When you call delete rule for a non-existent custom eventbus, ResourceNotFoundException is returned.
    Managed rules are rules created and managed by another Amazon Web Services service on your behalf. These rules
    are created by those other Amazon Web Services to support functionality in those services. You can
    delete these rules using the Force option, but you should do so only if you are sure the other service is not
    still using that rule.

    Args:
        ctx:
        hub:
        resource_id(Text): The name of the AWS CloudWatch Events Rule.
        name(Text): A name, ID to identify the resource.
        event_bus_name (Text, Optional) : The name or ARN of the event bus to associate with this rule.
            If you omit this, the default event bus is used.

    Request Syntax:
    [rule-id]:
      aws.events.rule.absent:
      - name: 'string'
      - resource_id: 'string'
      - event_bus_name: 'string'
      - qualifier: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.events.rule.absent:
                - name: value
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = await hub.exec.boto3.client.events.describe_rule(ctx, Name=resource_id)
    if not before["result"]:
        result["comment"] = (f"aws.events.rule '{name}' already absent",)
    else:
        tags = await hub.exec.boto3.client.events.list_tags_for_resource(
            ctx, ResourceARN=before["ret"].get("Arn")
        )
        result["result"] = tags.get("result")
        if result["result"]:
            existing_tags = tags.get("ret").get("Tags")
        else:
            result["comment"] = result["comment"] + tags["comment"]
            return result

        resource_converted = await hub.tool.aws.events.conversion_utils.convert_raw_cloud_watch_rule_to_present(
            ctx,
            raw_resource=before["ret"],
            idem_resource_name=before["ret"].get("Name"),
            tags=existing_tags,
        )
        result["result"] = result["result"] and resource_converted["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + resource_converted["comment"]
        result["old_state"] = resource_converted["ret"]
        if ctx.get("test", False):
            result["comment"] = result["comment"] + (
                f"Would delete aws.events.rule '{name}'",
            )
            return result
        else:
            try:
                targets = await hub.exec.boto3.client.events.list_targets_by_rule(
                    ctx, Rule=name
                )
                result["result"] = result["result"] and targets["result"]
                if result["result"] and targets["ret"]["Targets"]:
                    ids = []
                    for target in targets["ret"]["Targets"]:
                        ids.append(target.get("Id"))
                    remove_targets = await hub.exec.boto3.client.events.remove_targets(
                        ctx, Rule=name, Ids=ids
                    )
                    result["result"] = result["result"] and remove_targets["result"]
                    if not result["result"]:
                        result["comment"] = (
                            result["comment"] + remove_targets["comment"]
                        )
                        return result
                else:
                    result["comment"] = result["comment"] + targets["comment"]
                    return result
                ret = await hub.exec.boto3.client.events.delete_rule(
                    ctx, Name=name, EventBusName=event_bus_name
                )
                result["result"] = ret["result"] and result["result"]
                if not result["result"]:
                    result["comment"] = result["comment"] + ret["comment"]
                    return result
                result["comment"] = result["comment"] + (
                    f"Deleted aws.events.rule '{name}'",
                )
            except hub.tool.boto3.exception.ClientError as e:
                result["comment"] = result["comment"] + (
                    f"{e.__class__.__name__}: {e}",
                )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""

    Describe the resource in a way that can be recreated/managed with the corresponding "present" function


    Lists your Amazon EventBridge rules. You can either list all the rules or you can provide a prefix to match to
    the rule names. ListRules does not list the targets of a rule. To see the targets associated with a rule, use
    ListTargetsByRule.


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.events.rule
    """

    result = {}
    ret = await hub.exec.boto3.client.events.list_rules(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe aws.events.rule {ret['comment']}")
        return result
    for rule in ret["ret"]["Rules"]:
        tags = await hub.exec.boto3.client.events.list_tags_for_resource(
            ctx, ResourceARN=rule.get("Arn")
        )
        resource_converted = await hub.tool.aws.events.conversion_utils.convert_raw_cloud_watch_rule_to_present(
            ctx,
            raw_resource=rule,
            idem_resource_name=rule.get("Name"),
            tags=tags.get("ret").get("Tags") if tags.get("result") else None,
        )
        if not resource_converted["result"]:
            hub.log.warning(
                f"Could not describe aws.events.rule '{rule.get('Name')}' "
                f"with error {resource_converted['comment']}"
            )
        else:
            result[rule.get("Arn")] = {
                "aws.events.rule.present": [resource_converted["ret"]]
            }
    return result
