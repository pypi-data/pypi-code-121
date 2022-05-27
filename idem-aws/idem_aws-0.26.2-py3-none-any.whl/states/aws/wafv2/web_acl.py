import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    scope: str,
    default_action: dict,
    visibility_config: dict,
    resource_id: str = None,
    description: str = None,
    rules: list = None,
    custom_response_bodies: dict = None,
    captcha_config: dict = None,
    tags: list = None,
):
    r"""

    A web ACL defines a collection of rules to use to inspect and control web requests. Each rule has an action defined
    (allow, block, or count) for requests that match the statement of the rule. In the web ACL, you assign a default
    action to take (allow, block) for any request that does not match any of the rules. The rules in a web ACL can be
    a combination of the types Rule , RuleGroup , and managed rule group. You can associate a web ACL with one or more
    Amazon Web Services resources to protect. The resources can be an Amazon CloudFront distribution, an Amazon API
    Gateway REST API, an Application Load Balancer, or an AppSync GraphQL API.

    Args:
        name(text): The name of the web ACL. You cannot change the name of a web ACL after you create it.
        scope(text): Specifies whether this is for an Amazon CloudFront distribution or for a regional application.
            A regional application can be an Application Load Balancer (ALB), an Amazon API Gateway REST API,
            or an AppSync GraphQL API.
            To work with CloudFront, you must also specify the Region US East (N. Virginia) as follows:
              * CLI -- Specify the Region when you use the CloudFront scope: --scope=CLOUDFRONT --region=us-east-1 .
              * API and SDKs -- For all calls, use the Region endpoint us-east-1.
        default_action(dict): The action to perform if none of the Rules contained in the WebACL match.
          * Block (dict) -- Specifies that WAF should block requests by default.
          * Allow (dict) -- Specifies that WAF should allow requests by default.
        visibility_config(dict): Defines and enables Amazon CloudWatch metrics and web request sample collection.
          * SampledRequestsEnabled (bool) -- A boolean indicating whether WAF should store a sampling of the web
              requests that match the rules. You can view the sampled requests through the WAF console.
          * CloudWatchMetricsEnabled (bool) -- A boolean indicating whether the associated resource sends metrics to
                Amazon CloudWatch. For the list of available metrics, see WAF Metrics.
          * MetricName (text) -- A name of the Amazon CloudWatch metric. The name can contain only the characters:
                A-Z, a-z, 0-9, - (hyphen), and _ (underscore). The name can be from one to 128 characters long.
                It can't contain whitespace or metric names reserved for WAF, for example "All" and "Default_Action."
        resource_id(text, optional): AWS WAF ID.
        description(text, optional): A description of the web ACL that helps with identification.
        rules(list, optional): The Rule statements used to identify the web requests that you want to allow, block, or
            count. Each rule includes one top-level statement that WAF uses to identify matching web requests, and
            parameters that govern how WAF handles them.
        custom_response_bodies(dict, optional): A map of custom response keys and content bodies. When you create a rule with a
            block action, you can send a custom response to the web request. You define these for the web ACL, and then
            use them in the rules and default actions that you define in the web ACL.
        captcha_config(dict, optional): Specifies how WAF should handle CAPTCHA evaluations for rules that don't have their own
            CaptchaConfig settings. If you don't specify this, WAF uses its default settings for CaptchaConfig.
              * ImmunityTimeProperty (dict) -- Determines how long a CAPTCHA token remains valid after the client
                    successfully solves a CAPTCHA puzzle.
                  * ImmunityTime(integer) -- The amount of time, in seconds, that a CAPTCHA token is valid. The default
                        setting is 300.
        tags(list, optional): A tag associated with an Amazon Web Services resource. Tags are key:value pairs that you can use to
            categorize and manage your resources, for purposes like billing or other management. Typically, the tag key
            represents a category, such as "environment", and the tag value represents a specific value within that
            category, such as "test," "development," or "production". Or you might set the tag key to "customer" and
            the value to the customer name or ID. You can specify one or more tags to add to each Amazon Web Services
            resource, up to 50 tags for a resource.
            * Key (Text) -- Part of the key:value pair that defines a tag. You can use a tag key to describe a category
                of information, such as "customer." Tag keys are case-sensitive.
            * Value (Text) -- Part of the key:value pair that defines a tag. You can use a tag value to describe a
                specific value within a category, such as "companyA" or "companyB." Tag values are case-sensitive.

    Request Syntax:
        [web-acl-name]::
            aws.wafv2.web_acl.present:
            - name: 'string'
            - scope: 'string'
            - default_action: 'dict'
            - description: 'string'
            - rules: ['string']
            - visibility_config: 'dict'
            - custom_response_bodies: 'dict'
            - captcha_config: 'dict'
            - tags:
              - Key: 'string'
                Value: 'string'

    Examples:

        .. code-block:: sls
        demo_waf:
            aws.wafv2.web_acl.present:
            - name: demo_waf.
            - scope: REGIONAL
            - default_action:
                Allow: {}
            - description: waf to support REGIONAL resources.
            - rules:
                - Name: AWS-AWSManagedRulesBotControlRuleSet
                  OverrideAction:
                  None: {}
                  Priority: 1
                  Statement:
                    ManagedRuleGroupStatement:
                    Name: AWSManagedRulesBotControlRuleSet
                    VendorName: AWS
                  VisibilityConfig:
                    CloudWatchMetricsEnabled: false
                    MetricName: AWS-AWSManagedRulesBotControlRuleSet
                    SampledRequestsEnabled: true
            - visibility_config:
                CloudWatchMetricsEnabled: false
                MetricName: test_metric_waf
                SampledRequestsEnabled: true
            - tags:
              - Key: type
                Value: REGIONAL

    Returns:
        Dict[str, Any]

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    lock_token: str = None
    resource_updated: bool = False
    resource_parameters = {
        "Name": name,
        "DefaultAction": default_action,
        "VisibilityConfig": visibility_config,
        "Description": description,
        "Rules": rules,
        "CustomResponseBodies": custom_response_bodies,
        "CaptchaConfig": captcha_config,
        "Tags": tags,
    }

    if resource_id:
        ret = await hub.exec.boto3.client.wafv2.get_web_acl(
            ctx, Name=name, Scope=scope, Id=resource_id
        )
        if ret["result"]:
            before = ret["ret"]["WebACL"]
            lock_token = ret["ret"]["LockToken"]

    if before:
        convert_ret = (
            await hub.tool.aws.wafv2.conversion_utils.convert_raw_web_acl_to_present(
                ctx, raw_resource=before, idem_resource_name=name, scope=scope
            )
        )
        result["result"] = convert_ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + convert_ret["comment"]
        result["old_state"] = convert_ret["ret"]
        plan_state = copy.deepcopy(result["old_state"])

        # Update web acl
        update_ret = await hub.exec.aws.wafv2.web_acl.update_web_acl(
            ctx,
            name=name,
            raw_resource=before,
            resource_parameters=resource_parameters,
            scope=scope,
            resource_id=resource_id,
            lock_token=lock_token,
        )
        result["comment"] = result["comment"] + update_ret["comment"]
        result["result"] = update_ret["result"]
        resource_updated = resource_updated or bool(update_ret["ret"])

        if update_ret["ret"] and ctx.get("test", False):
            for key in [
                "scope",
                "default_action",
                "visibility_config",
                "description",
                "rules",
                "custom_response_bodies",
                "captcha_config",
            ]:
                if key in update_ret["ret"]:
                    plan_state[key] = update_ret["ret"][key]

        if (tags is not None) and (
            not hub.tool.aws.state_comparison_utils.are_lists_identical(
                tags, result["old_state"].get("tags")
            )
        ):
            # Update tags
            update_tag_ret = await hub.exec.aws.wafv2.web_acl.update_web_acl_tags(
                ctx=ctx,
                web_acl_arn=before.get("ARN"),
                old_tags=result["old_state"].get("tags", []),
                new_tags=tags,
            )
            result["result"] = result["result"] and update_tag_ret["result"]
            result["comment"] = result["comment"] + update_tag_ret["comment"]
            resource_updated = resource_updated or bool(update_tag_ret["ret"])

            if ctx.get("test", False) and update_tag_ret["ret"] is not None:
                plan_state["tags"] = update_tag_ret["ret"].get("tags")

        if not resource_updated:
            result["comment"] = result["comment"] + (
                f"aws.wafv2.web_acl.present '{name}' has no property to update.",
            )

    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "scope": scope,
                    "default_action": default_action,
                    "visibility_config": visibility_config,
                    "description": description,
                    "rules": rules,
                    "custom_response_bodies": custom_response_bodies,
                    "captcha_config": captcha_config,
                    "tags": tags,
                },
            )
            result["comment"] = (f"Would create aws.wafv2.web_acl {name}",)
            return result

        # Create web acl
        ret = await hub.exec.boto3.client.wafv2.create_web_acl(
            ctx, Scope=scope, **resource_parameters
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + ret["comment"]
            return result
        result["comment"] = result["comment"] + (f"Created '{name}'",)
        resource_id = ret["ret"]["Summary"]["Id"]

    if ctx.get("test", False):
        result["new_state"] = plan_state

    elif (not before) or resource_updated:
        resource_ret = await hub.exec.boto3.client.wafv2.get_web_acl(
            ctx, Name=name, Scope=scope, Id=resource_id
        )
        if not result["result"]:
            result["comment"] = result["comment"] + ret["comment"]
            return result
        after = resource_ret["ret"]["WebACL"]

        convert_ret = (
            await hub.tool.aws.wafv2.conversion_utils.convert_raw_web_acl_to_present(
                ctx, raw_resource=after, idem_resource_name=name, scope=scope
            )
        )
        result["result"] = convert_ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + convert_ret["comment"]
        result["new_state"] = convert_ret["ret"]

    else:
        result["new_state"] = copy.deepcopy(result["old_state"])

    return result


async def absent(
    hub, ctx, name: str, scope: str, resource_id: str = None
) -> Dict[str, Any]:
    r"""
    Deletes the specified WebACL.
    You can only use this if ManagedByFirewallManager is false in the specified WebACL.

    Args:
        name(text): The name of the web ACL. You cannot change the name of a web ACL after you create it.
        resource_id(text): AWS WAF ID. Idem automatically considers this resource being absent if this field is not specified.
        scope(text): Specifies whether this is for an Amazon CloudFront distribution or for a regional application.
            A regional application can be an Application Load Balancer (ALB), an Amazon API Gateway REST API, or an
            AppSync GraphQL API.
            To work with CloudFront, you must also specify the Region US East (N. Virginia) as follows:
            * CLI -- Specify the Region when you use the CloudFront scope: --scope=CLOUDFRONT --region=us-east-1 .
            * API and SDKs -- For all calls, use the Region endpoint us-east-1.

    Request Syntax:
        [web-acl-name]::
            aws.wafv2.web_acl.absent:
            - name: 'string'
            - scope: 'string'

    Examples:

        .. code-block:: sls

            demo_waf::
               aws.wafv2.web_acl.absent:
                - name: demo_waf
                - scope: REGIONAL

    Returns:
        Dict[str, Any]

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    lock_token: str = None

    if resource_id:
        resource = await hub.exec.boto3.client.wafv2.get_web_acl(
            ctx, Name=name, Scope=scope, Id=resource_id
        )
        if resource["result"]:
            before = resource["ret"]["WebACL"]
            lock_token = resource["ret"]["LockToken"]

    if not before:
        result["comment"] = (f"aws.wafv2.web_acl '{name}' already absent",)

    elif ctx.get("test", False):
        convert_ret = (
            await hub.tool.aws.wafv2.conversion_utils.convert_raw_web_acl_to_present(
                ctx, raw_resource=before, idem_resource_name=name, scope=scope
            )
        )
        result["result"] = convert_ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + convert_ret["comment"]
            return result
        result["old_state"] = convert_ret["ret"]
        result["comment"] = (f"Would delete aws.wafv2.web_acl '{name}'",)
        return result

    else:
        convert_ret = (
            await hub.tool.aws.wafv2.conversion_utils.convert_raw_web_acl_to_present(
                ctx, raw_resource=before, idem_resource_name=name, scope=scope
            )
        )
        result["result"] = convert_ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + convert_ret["comment"]
            return result
        result["old_state"] = convert_ret["ret"]

        # Delete web acl
        ret = await hub.exec.boto3.client.wafv2.delete_web_acl(
            ctx, Name=name, Scope=scope, Id=resource_id, LockToken=lock_token
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result
        result["comment"] = (f"Deleted aws.wafv2.web_acl '{name}'",)

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""

    Retrieves an WebACLSummary objects for the web ACLs that you manage.

    Examples:

        .. code-block:: bash

            $ idem describe aws.wafv2.web_acl

    Returns:
        Dict[str, Any]

    """
    result = {}
    scope = ["CLOUDFRONT", "REGIONAL"]

    for web_acl_scope in scope:
        ret = await hub.exec.boto3.client.wafv2.list_web_acls(ctx, Scope=web_acl_scope)
        if not ret["result"]:
            hub.log.debug(f"Could not describe web acl {ret['comment']}")
            continue

        for resource in ret["ret"]["WebACLs"]:
            web_acl_name = resource["Name"]
            resource_id = resource["Id"]
            raw_resource = await hub.exec.boto3.client.wafv2.get_web_acl(
                ctx, Name=web_acl_name, Id=resource_id, Scope=web_acl_scope
            )
            if not raw_resource["result"]:
                hub.log.warning(
                    f"Could not get web acl '{web_acl_name}' with error {convert_ret['comment']}"
                )
                continue
            resource_ret = raw_resource["ret"]["WebACL"]
            convert_ret = await hub.tool.aws.wafv2.conversion_utils.convert_raw_web_acl_to_present(
                ctx,
                raw_resource=resource_ret,
                idem_resource_name=web_acl_name,
                scope=web_acl_scope,
            )
            if not convert_ret["result"]:
                hub.log.warning(
                    f"Could not describe web acl '{web_acl_name}' with error {convert_ret['comment']}"
                )
                continue
            translated_resource = convert_ret["ret"]
            result[translated_resource["resource_id"]] = {
                "aws.wafv2.web_acl.present": [
                    {parameter_key: parameter_value}
                    for parameter_key, parameter_value in translated_resource.items()
                ]
            }

    return result
