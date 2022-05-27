"""
hub.exec.boto3.client.config.put_config_rule
hub.exec.boto3.client.config.delete_config_rule
hub.exec.boto3.client.config.describe_config_rules

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
    scope: Dict = None,
    source: Dict = True,
    tags: List = None,
    max_execution_frequency: str = None,
    input_parameters: str = None,
) -> Dict[str, Any]:
    """
    Adds or updates Config rule for evaluating whether your Amazon Web Services resources comply with your desired
    configurations. For more information about rules, please see AWS Config services
    Args:
        name(Text): An Idem name of the rule.
        resource_id(Text, Optional): AWS Config Rule Name.
        scope(Dict, Optional): Defines which resources can trigger an evaluation for the rule. The scope can include one or more
         resource types, a combination of one resource type and one resource ID, or a combination of a tag key and value
        source(Dict): Provides the rule owner, the rule identifier, and the
         notifications that cause the function to evaluate your Amazon Web Services resources,
        max_execution_frequency(Text, Optional): The maximum frequency with which Config runs evaluations for a rule. Default
         is 24 hours
        input_parameters(Text, Optional): A string, in JSON format, that is passed to the Config rule.
        tags(List, Optional): The tags for the resource. The metadata that you apply to a resource to help you categorize and
         organize them.

    Request syntax:
        [aws-config-rule]:
          aws.config.rule.present:
          - name: 'string'
          - resource_id: 'string'
          - scope: dict
            ComplianceResourceTypes: list
          - source: dict
            Owner: 'string'
            SourceIdentifier: 'string'

    Returns:
         None

    Examples:
        .. code-block:: sls

            ec2-instance-no-public-ip:
              aws.config.rule.present:
              - name: ec2-instance-no-public-ip
              - resource_id: ec2-instance-no-public-ip
              - tags:
                - Key: ENV
                  Value: Test
                - Key: Service
                  Value: TestService
              - config_rule_name: ec2-instance-no-public-ip
              - scope:
                  ComplianceResourceTypes:
                  - AWS::EC2::Instance
                  - AWS::EC2::Host
              - source:
                  Owner: AWS
                  SourceIdentifier: EC2_INSTANCE_NO_PUBLIC_IP
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False
    update_scope = None
    if resource_id:
        try:
            before = await hub.exec.boto3.client.config.describe_config_rules(
                ctx, ConfigRuleNames=[resource_id]
            )
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
            return result
    if before:
        try:
            result[
                "old_state"
            ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_rule_to_present(
                ctx,
                raw_resource=before["ret"]["ConfigRules"][0],
                idem_resource_name=name,
            )
            plan_state = copy.deepcopy(result["old_state"])
            # updating scope
            if scope is not None:
                update_scope = (
                    scope if scope is not None else result["old_state"]["scope"]
                )

            update_ret = await hub.exec.aws.config.rule.update_rule(
                ctx,
                resource_id=resource_id,
                before=before["ret"]["ConfigRules"][0],
                source=source,
                scope=update_scope,
                frequency=max_execution_frequency,
                input_parameters=input_parameters,
            )

            result["comment"] = result["comment"] + update_ret["comment"]
            result["result"] = update_ret["result"]
            resource_updated = resource_updated or bool(update_ret["ret"])
            if update_ret["ret"] and ctx.get("test", False):
                for key in ["max_execution_frequency", "scope", "input_parameters"]:
                    if key in update_ret["ret"]:
                        plan_state[key] = update_ret["ret"].get(key)

            if (tags is not None) and (
                not hub.tool.aws.state_comparison_utils.are_lists_identical(
                    tags, result["old_state"].get("tags", None)
                )
            ):
                update_tag_ret = await hub.exec.aws.config.tag.update_tags(
                    ctx,
                    result["old_state"]["config_rule_arn"],
                    result["old_state"]["tags"],
                    tags,
                )
                result["result"] = result["result"] and update_tag_ret["result"]
                result["comment"] = result["comment"] + update_tag_ret["comment"]
                resource_updated = resource_updated or bool(update_tag_ret["ret"])
                if ctx.get("test", False) and update_tag_ret["ret"] is not None:
                    plan_state["tags"] = update_tag_ret["ret"].get("tags")
            if not resource_updated:
                result["comment"] = result["comment"] + (f"{name} already exists",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    else:
        try:
            if ctx.get("test", False):
                desired_state_payload = {
                    "name": name,
                    "config_rule_name": name,
                    "source": source,
                    "tags": tags,
                }
                if scope:
                    desired_state_payload["scope"] = scope
                if input_parameters:
                    desired_state_payload["input_parameters"] = input_parameters
                if max_execution_frequency:
                    desired_state_payload[
                        "max_execution_frequency"
                    ] = max_execution_frequency
                result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                    enforced_state={}, desired_state=desired_state_payload
                )
                result["comment"] = (f"Would create aws.config.rule {name}",)
                return result
            config_rule_payload = {"ConfigRuleName": name, "Source": source}
            if scope:
                config_rule_payload["Scope"] = scope
            if max_execution_frequency:
                config_rule_payload[
                    "MaximumExecutionFrequency"
                ] = max_execution_frequency
            if input_parameters:
                config_rule_payload["InputParameters"] = input_parameters
            ret = await hub.exec.boto3.client.config.put_config_rule(
                ctx, ConfigRule=config_rule_payload, Tags=tags
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"] + ret["comment"]
                return result
            resource_id = name
            result["comment"] = result["comment"] + (f"Created '{name}'",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}")
            result["result"] = False
    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif (not before) or resource_updated:
            after = await hub.exec.boto3.client.config.describe_config_rules(
                ctx, ConfigRuleNames=[resource_id]
            )
            result[
                "new_state"
            ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_rule_to_present(
                ctx,
                raw_resource=after["ret"]["ConfigRules"][0],
                idem_resource_name=name,
            )
        else:
            result["new_state"] = copy.deepcopy(result["old_state"])
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
    return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
) -> Dict[str, Any]:
    """
    Deletes the specified Config rule and all of its evaluation results. Config sets the state of a rule to DELETING
    until the deletion is complete. You cannot update a rule while it is in this state. If you make a PutConfigRule or
    DeleteConfigRule request for the rule, you will receive a ResourceInUseException.

    Args:
        name(Text): An Idem name of the rule.
        resource_id(Text, optional): AWS Config Rule Name. Idem automatically considers this resource being absent
         if this field is not specified.

    Returns:
          Dict[str, Any]

    Examples:
          .. code-block:: sls

            ec2-instance-no-public-ip:
              aws.config.rule.absent:
              - name: ec2-instance-no-public-ip
              - resource_id: ec2-instance-no-public-ip

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.config.rule", name=name
        )
        return result
    before = await hub.exec.boto3.client.config.describe_config_rules(
        ctx, ConfigRuleNames=[resource_id]
    )
    if not before:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.config.rule", name=name
        )
    elif ctx.get("test", False):
        result[
            "old_state"
        ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_rule_to_present(
            ctx, raw_resource=before["ret"]["ConfigRules"][0], idem_resource_name=name
        )
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.config.rule", name=name
        )
        return result
    else:
        try:
            if before["ret"]["ConfigRules"][0]["ConfigRuleState"] == "DELETING":
                result["comment"] = (
                    f"aws.config.rule '{name}' is still in deleting state.",
                )
            else:
                result[
                    "old_state"
                ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_rule_to_present(
                    ctx,
                    raw_resource=before["ret"]["ConfigRules"][0],
                    idem_resource_name=name,
                )

                ret = await hub.exec.boto3.client.config.delete_config_rule(
                    ctx, ConfigRuleName=resource_id
                )
                result["result"] = ret["result"]
                if not result["result"]:
                    result["comment"] = ret["comment"]
                    result["result"] = False
                    return result
                result["comment"] = hub.tool.aws.comment_utils.delete_comment(
                    resource_type="aws.config.rule", name=name
                )
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    """
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Return details about your Config rules.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.config.rule
    """
    result = {}
    ret = await hub.exec.boto3.client.config.describe_config_rules(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe Rules {ret['comment']}")
        return {}

    for resource in ret["ret"]["ConfigRules"]:
        resource_id = resource.get("ConfigRuleName")
        resource_translated = await hub.tool.aws.config.conversion_utils.convert_raw_config_rule_to_present(
            ctx, raw_resource=resource, idem_resource_name=resource_id
        )
        result[resource_id] = {
            "aws.config.rule.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }
    return result
