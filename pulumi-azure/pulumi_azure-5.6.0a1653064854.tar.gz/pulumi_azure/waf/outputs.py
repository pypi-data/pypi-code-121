# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'PolicyCustomRule',
    'PolicyCustomRuleMatchCondition',
    'PolicyCustomRuleMatchConditionMatchVariable',
    'PolicyManagedRules',
    'PolicyManagedRulesExclusion',
    'PolicyManagedRulesManagedRuleSet',
    'PolicyManagedRulesManagedRuleSetRuleGroupOverride',
    'PolicyPolicySettings',
]

@pulumi.output_type
class PolicyCustomRule(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "matchConditions":
            suggest = "match_conditions"
        elif key == "ruleType":
            suggest = "rule_type"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyCustomRule. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyCustomRule.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyCustomRule.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 action: str,
                 match_conditions: Sequence['outputs.PolicyCustomRuleMatchCondition'],
                 priority: int,
                 rule_type: str,
                 name: Optional[str] = None):
        """
        :param str action: Type of action.
        :param Sequence['PolicyCustomRuleMatchConditionArgs'] match_conditions: One or more `match_conditions` blocks as defined below.
        :param int priority: Describes priority of the rule. Rules with a lower value will be evaluated before rules with a higher value.
        :param str rule_type: Describes the type of rule.
        :param str name: Gets name of the resource that is unique within a policy. This name can be used to access the resource.
        """
        pulumi.set(__self__, "action", action)
        pulumi.set(__self__, "match_conditions", match_conditions)
        pulumi.set(__self__, "priority", priority)
        pulumi.set(__self__, "rule_type", rule_type)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def action(self) -> str:
        """
        Type of action.
        """
        return pulumi.get(self, "action")

    @property
    @pulumi.getter(name="matchConditions")
    def match_conditions(self) -> Sequence['outputs.PolicyCustomRuleMatchCondition']:
        """
        One or more `match_conditions` blocks as defined below.
        """
        return pulumi.get(self, "match_conditions")

    @property
    @pulumi.getter
    def priority(self) -> int:
        """
        Describes priority of the rule. Rules with a lower value will be evaluated before rules with a higher value.
        """
        return pulumi.get(self, "priority")

    @property
    @pulumi.getter(name="ruleType")
    def rule_type(self) -> str:
        """
        Describes the type of rule.
        """
        return pulumi.get(self, "rule_type")

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        """
        Gets name of the resource that is unique within a policy. This name can be used to access the resource.
        """
        return pulumi.get(self, "name")


@pulumi.output_type
class PolicyCustomRuleMatchCondition(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "matchValues":
            suggest = "match_values"
        elif key == "matchVariables":
            suggest = "match_variables"
        elif key == "negationCondition":
            suggest = "negation_condition"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyCustomRuleMatchCondition. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyCustomRuleMatchCondition.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyCustomRuleMatchCondition.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 match_values: Sequence[str],
                 match_variables: Sequence['outputs.PolicyCustomRuleMatchConditionMatchVariable'],
                 operator: str,
                 negation_condition: Optional[bool] = None,
                 transforms: Optional[Sequence[str]] = None):
        """
        :param Sequence[str] match_values: A list of match values.
        :param Sequence['PolicyCustomRuleMatchConditionMatchVariableArgs'] match_variables: One or more `match_variables` blocks as defined below.
        :param str operator: Describes operator to be matched.
        :param bool negation_condition: Describes if this is negate condition or not
        :param Sequence[str] transforms: A list of transformations to do before the match is attempted.
        """
        pulumi.set(__self__, "match_values", match_values)
        pulumi.set(__self__, "match_variables", match_variables)
        pulumi.set(__self__, "operator", operator)
        if negation_condition is not None:
            pulumi.set(__self__, "negation_condition", negation_condition)
        if transforms is not None:
            pulumi.set(__self__, "transforms", transforms)

    @property
    @pulumi.getter(name="matchValues")
    def match_values(self) -> Sequence[str]:
        """
        A list of match values.
        """
        return pulumi.get(self, "match_values")

    @property
    @pulumi.getter(name="matchVariables")
    def match_variables(self) -> Sequence['outputs.PolicyCustomRuleMatchConditionMatchVariable']:
        """
        One or more `match_variables` blocks as defined below.
        """
        return pulumi.get(self, "match_variables")

    @property
    @pulumi.getter
    def operator(self) -> str:
        """
        Describes operator to be matched.
        """
        return pulumi.get(self, "operator")

    @property
    @pulumi.getter(name="negationCondition")
    def negation_condition(self) -> Optional[bool]:
        """
        Describes if this is negate condition or not
        """
        return pulumi.get(self, "negation_condition")

    @property
    @pulumi.getter
    def transforms(self) -> Optional[Sequence[str]]:
        """
        A list of transformations to do before the match is attempted.
        """
        return pulumi.get(self, "transforms")


@pulumi.output_type
class PolicyCustomRuleMatchConditionMatchVariable(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "variableName":
            suggest = "variable_name"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyCustomRuleMatchConditionMatchVariable. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyCustomRuleMatchConditionMatchVariable.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyCustomRuleMatchConditionMatchVariable.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 variable_name: str,
                 selector: Optional[str] = None):
        """
        :param str variable_name: The name of the Match Variable
        :param str selector: Describes field of the matchVariable collection
        """
        pulumi.set(__self__, "variable_name", variable_name)
        if selector is not None:
            pulumi.set(__self__, "selector", selector)

    @property
    @pulumi.getter(name="variableName")
    def variable_name(self) -> str:
        """
        The name of the Match Variable
        """
        return pulumi.get(self, "variable_name")

    @property
    @pulumi.getter
    def selector(self) -> Optional[str]:
        """
        Describes field of the matchVariable collection
        """
        return pulumi.get(self, "selector")


@pulumi.output_type
class PolicyManagedRules(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "managedRuleSets":
            suggest = "managed_rule_sets"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyManagedRules. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyManagedRules.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyManagedRules.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 managed_rule_sets: Sequence['outputs.PolicyManagedRulesManagedRuleSet'],
                 exclusions: Optional[Sequence['outputs.PolicyManagedRulesExclusion']] = None):
        """
        :param Sequence['PolicyManagedRulesManagedRuleSetArgs'] managed_rule_sets: One or more `managed_rule_set` block defined below.
        :param Sequence['PolicyManagedRulesExclusionArgs'] exclusions: One or more `exclusion` block defined below.
        """
        pulumi.set(__self__, "managed_rule_sets", managed_rule_sets)
        if exclusions is not None:
            pulumi.set(__self__, "exclusions", exclusions)

    @property
    @pulumi.getter(name="managedRuleSets")
    def managed_rule_sets(self) -> Sequence['outputs.PolicyManagedRulesManagedRuleSet']:
        """
        One or more `managed_rule_set` block defined below.
        """
        return pulumi.get(self, "managed_rule_sets")

    @property
    @pulumi.getter
    def exclusions(self) -> Optional[Sequence['outputs.PolicyManagedRulesExclusion']]:
        """
        One or more `exclusion` block defined below.
        """
        return pulumi.get(self, "exclusions")


@pulumi.output_type
class PolicyManagedRulesExclusion(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "matchVariable":
            suggest = "match_variable"
        elif key == "selectorMatchOperator":
            suggest = "selector_match_operator"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyManagedRulesExclusion. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyManagedRulesExclusion.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyManagedRulesExclusion.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 match_variable: str,
                 selector: str,
                 selector_match_operator: str):
        """
        :param str match_variable: The name of the Match Variable. Possible values: `RequestArgNames`, `RequestCookieNames`, `RequestHeaderNames`.
        :param str selector: Describes field of the matchVariable collection.
        :param str selector_match_operator: Describes operator to be matched. Possible values: `Contains`, `EndsWith`, `Equals`, `EqualsAny`, `StartsWith`.
        """
        pulumi.set(__self__, "match_variable", match_variable)
        pulumi.set(__self__, "selector", selector)
        pulumi.set(__self__, "selector_match_operator", selector_match_operator)

    @property
    @pulumi.getter(name="matchVariable")
    def match_variable(self) -> str:
        """
        The name of the Match Variable. Possible values: `RequestArgNames`, `RequestCookieNames`, `RequestHeaderNames`.
        """
        return pulumi.get(self, "match_variable")

    @property
    @pulumi.getter
    def selector(self) -> str:
        """
        Describes field of the matchVariable collection.
        """
        return pulumi.get(self, "selector")

    @property
    @pulumi.getter(name="selectorMatchOperator")
    def selector_match_operator(self) -> str:
        """
        Describes operator to be matched. Possible values: `Contains`, `EndsWith`, `Equals`, `EqualsAny`, `StartsWith`.
        """
        return pulumi.get(self, "selector_match_operator")


@pulumi.output_type
class PolicyManagedRulesManagedRuleSet(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "ruleGroupOverrides":
            suggest = "rule_group_overrides"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyManagedRulesManagedRuleSet. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyManagedRulesManagedRuleSet.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyManagedRulesManagedRuleSet.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 version: str,
                 rule_group_overrides: Optional[Sequence['outputs.PolicyManagedRulesManagedRuleSetRuleGroupOverride']] = None,
                 type: Optional[str] = None):
        """
        :param str version: The rule set version. Possible values: `0.1`, `1.0`, `2.2.9`, `3.0`, `3.1` and `3.2`.
        :param Sequence['PolicyManagedRulesManagedRuleSetRuleGroupOverrideArgs'] rule_group_overrides: One or more `rule_group_override` block defined below.
        :param str type: The rule set type. Possible values: `Microsoft_BotManagerRuleSet` and `OWASP`.
        """
        pulumi.set(__self__, "version", version)
        if rule_group_overrides is not None:
            pulumi.set(__self__, "rule_group_overrides", rule_group_overrides)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def version(self) -> str:
        """
        The rule set version. Possible values: `0.1`, `1.0`, `2.2.9`, `3.0`, `3.1` and `3.2`.
        """
        return pulumi.get(self, "version")

    @property
    @pulumi.getter(name="ruleGroupOverrides")
    def rule_group_overrides(self) -> Optional[Sequence['outputs.PolicyManagedRulesManagedRuleSetRuleGroupOverride']]:
        """
        One or more `rule_group_override` block defined below.
        """
        return pulumi.get(self, "rule_group_overrides")

    @property
    @pulumi.getter
    def type(self) -> Optional[str]:
        """
        The rule set type. Possible values: `Microsoft_BotManagerRuleSet` and `OWASP`.
        """
        return pulumi.get(self, "type")


@pulumi.output_type
class PolicyManagedRulesManagedRuleSetRuleGroupOverride(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "ruleGroupName":
            suggest = "rule_group_name"
        elif key == "disabledRules":
            suggest = "disabled_rules"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyManagedRulesManagedRuleSetRuleGroupOverride. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyManagedRulesManagedRuleSetRuleGroupOverride.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyManagedRulesManagedRuleSetRuleGroupOverride.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 rule_group_name: str,
                 disabled_rules: Optional[Sequence[str]] = None):
        """
        :param str rule_group_name: The name of the Rule Group
        :param Sequence[str] disabled_rules: One or more Rule IDs
        """
        pulumi.set(__self__, "rule_group_name", rule_group_name)
        if disabled_rules is not None:
            pulumi.set(__self__, "disabled_rules", disabled_rules)

    @property
    @pulumi.getter(name="ruleGroupName")
    def rule_group_name(self) -> str:
        """
        The name of the Rule Group
        """
        return pulumi.get(self, "rule_group_name")

    @property
    @pulumi.getter(name="disabledRules")
    def disabled_rules(self) -> Optional[Sequence[str]]:
        """
        One or more Rule IDs
        """
        return pulumi.get(self, "disabled_rules")


@pulumi.output_type
class PolicyPolicySettings(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "fileUploadLimitInMb":
            suggest = "file_upload_limit_in_mb"
        elif key == "maxRequestBodySizeInKb":
            suggest = "max_request_body_size_in_kb"
        elif key == "requestBodyCheck":
            suggest = "request_body_check"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PolicyPolicySettings. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PolicyPolicySettings.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PolicyPolicySettings.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 enabled: Optional[bool] = None,
                 file_upload_limit_in_mb: Optional[int] = None,
                 max_request_body_size_in_kb: Optional[int] = None,
                 mode: Optional[str] = None,
                 request_body_check: Optional[bool] = None):
        """
        :param bool enabled: Describes if the policy is in enabled state or disabled state. Defaults to `true`.
        :param int file_upload_limit_in_mb: The File Upload Limit in MB. Accepted values are in the range `1` to `4000`. Defaults to `100`.
        :param int max_request_body_size_in_kb: The Maximum Request Body Size in KB.  Accepted values are in the range `8` to `2000`. Defaults to `128`.
        :param str mode: Describes if it is in detection mode or prevention mode at the policy level. Valid values are `Detection` and `Prevention`. Defaults to `Prevention`.
        :param bool request_body_check: Is Request Body Inspection enabled? Defaults to `true`.
        """
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if file_upload_limit_in_mb is not None:
            pulumi.set(__self__, "file_upload_limit_in_mb", file_upload_limit_in_mb)
        if max_request_body_size_in_kb is not None:
            pulumi.set(__self__, "max_request_body_size_in_kb", max_request_body_size_in_kb)
        if mode is not None:
            pulumi.set(__self__, "mode", mode)
        if request_body_check is not None:
            pulumi.set(__self__, "request_body_check", request_body_check)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[bool]:
        """
        Describes if the policy is in enabled state or disabled state. Defaults to `true`.
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter(name="fileUploadLimitInMb")
    def file_upload_limit_in_mb(self) -> Optional[int]:
        """
        The File Upload Limit in MB. Accepted values are in the range `1` to `4000`. Defaults to `100`.
        """
        return pulumi.get(self, "file_upload_limit_in_mb")

    @property
    @pulumi.getter(name="maxRequestBodySizeInKb")
    def max_request_body_size_in_kb(self) -> Optional[int]:
        """
        The Maximum Request Body Size in KB.  Accepted values are in the range `8` to `2000`. Defaults to `128`.
        """
        return pulumi.get(self, "max_request_body_size_in_kb")

    @property
    @pulumi.getter
    def mode(self) -> Optional[str]:
        """
        Describes if it is in detection mode or prevention mode at the policy level. Valid values are `Detection` and `Prevention`. Defaults to `Prevention`.
        """
        return pulumi.get(self, "mode")

    @property
    @pulumi.getter(name="requestBodyCheck")
    def request_body_check(self) -> Optional[bool]:
        """
        Is Request Body Inspection enabled? Defaults to `true`.
        """
        return pulumi.get(self, "request_body_check")


