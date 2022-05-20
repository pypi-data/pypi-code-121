# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['GroupPolicyRemediationArgs', 'GroupPolicyRemediation']

@pulumi.input_type
class GroupPolicyRemediationArgs:
    def __init__(__self__, *,
                 management_group_id: pulumi.Input[str],
                 policy_assignment_id: pulumi.Input[str],
                 location_filters: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy_definition_id: Optional[pulumi.Input[str]] = None,
                 resource_discovery_mode: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a GroupPolicyRemediation resource.
        """
        pulumi.set(__self__, "management_group_id", management_group_id)
        pulumi.set(__self__, "policy_assignment_id", policy_assignment_id)
        if location_filters is not None:
            pulumi.set(__self__, "location_filters", location_filters)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if policy_definition_id is not None:
            pulumi.set(__self__, "policy_definition_id", policy_definition_id)
        if resource_discovery_mode is not None:
            pulumi.set(__self__, "resource_discovery_mode", resource_discovery_mode)

    @property
    @pulumi.getter(name="managementGroupId")
    def management_group_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "management_group_id")

    @management_group_id.setter
    def management_group_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "management_group_id", value)

    @property
    @pulumi.getter(name="policyAssignmentId")
    def policy_assignment_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "policy_assignment_id")

    @policy_assignment_id.setter
    def policy_assignment_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "policy_assignment_id", value)

    @property
    @pulumi.getter(name="locationFilters")
    def location_filters(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "location_filters")

    @location_filters.setter
    def location_filters(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "location_filters", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="policyDefinitionId")
    def policy_definition_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "policy_definition_id")

    @policy_definition_id.setter
    def policy_definition_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_definition_id", value)

    @property
    @pulumi.getter(name="resourceDiscoveryMode")
    def resource_discovery_mode(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "resource_discovery_mode")

    @resource_discovery_mode.setter
    def resource_discovery_mode(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_discovery_mode", value)


@pulumi.input_type
class _GroupPolicyRemediationState:
    def __init__(__self__, *,
                 location_filters: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 management_group_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy_assignment_id: Optional[pulumi.Input[str]] = None,
                 policy_definition_id: Optional[pulumi.Input[str]] = None,
                 resource_discovery_mode: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering GroupPolicyRemediation resources.
        """
        if location_filters is not None:
            pulumi.set(__self__, "location_filters", location_filters)
        if management_group_id is not None:
            pulumi.set(__self__, "management_group_id", management_group_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if policy_assignment_id is not None:
            pulumi.set(__self__, "policy_assignment_id", policy_assignment_id)
        if policy_definition_id is not None:
            pulumi.set(__self__, "policy_definition_id", policy_definition_id)
        if resource_discovery_mode is not None:
            pulumi.set(__self__, "resource_discovery_mode", resource_discovery_mode)

    @property
    @pulumi.getter(name="locationFilters")
    def location_filters(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "location_filters")

    @location_filters.setter
    def location_filters(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "location_filters", value)

    @property
    @pulumi.getter(name="managementGroupId")
    def management_group_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "management_group_id")

    @management_group_id.setter
    def management_group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "management_group_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="policyAssignmentId")
    def policy_assignment_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "policy_assignment_id")

    @policy_assignment_id.setter
    def policy_assignment_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_assignment_id", value)

    @property
    @pulumi.getter(name="policyDefinitionId")
    def policy_definition_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "policy_definition_id")

    @policy_definition_id.setter
    def policy_definition_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_definition_id", value)

    @property
    @pulumi.getter(name="resourceDiscoveryMode")
    def resource_discovery_mode(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "resource_discovery_mode")

    @resource_discovery_mode.setter
    def resource_discovery_mode(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_discovery_mode", value)


class GroupPolicyRemediation(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 location_filters: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 management_group_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy_assignment_id: Optional[pulumi.Input[str]] = None,
                 policy_definition_id: Optional[pulumi.Input[str]] = None,
                 resource_discovery_mode: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Create a GroupPolicyRemediation resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: GroupPolicyRemediationArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Create a GroupPolicyRemediation resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param GroupPolicyRemediationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(GroupPolicyRemediationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 location_filters: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 management_group_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy_assignment_id: Optional[pulumi.Input[str]] = None,
                 policy_definition_id: Optional[pulumi.Input[str]] = None,
                 resource_discovery_mode: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = GroupPolicyRemediationArgs.__new__(GroupPolicyRemediationArgs)

            __props__.__dict__["location_filters"] = location_filters
            if management_group_id is None and not opts.urn:
                raise TypeError("Missing required property 'management_group_id'")
            __props__.__dict__["management_group_id"] = management_group_id
            __props__.__dict__["name"] = name
            if policy_assignment_id is None and not opts.urn:
                raise TypeError("Missing required property 'policy_assignment_id'")
            __props__.__dict__["policy_assignment_id"] = policy_assignment_id
            __props__.__dict__["policy_definition_id"] = policy_definition_id
            __props__.__dict__["resource_discovery_mode"] = resource_discovery_mode
        super(GroupPolicyRemediation, __self__).__init__(
            'azure:management/groupPolicyRemediation:GroupPolicyRemediation',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            location_filters: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            management_group_id: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            policy_assignment_id: Optional[pulumi.Input[str]] = None,
            policy_definition_id: Optional[pulumi.Input[str]] = None,
            resource_discovery_mode: Optional[pulumi.Input[str]] = None) -> 'GroupPolicyRemediation':
        """
        Get an existing GroupPolicyRemediation resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _GroupPolicyRemediationState.__new__(_GroupPolicyRemediationState)

        __props__.__dict__["location_filters"] = location_filters
        __props__.__dict__["management_group_id"] = management_group_id
        __props__.__dict__["name"] = name
        __props__.__dict__["policy_assignment_id"] = policy_assignment_id
        __props__.__dict__["policy_definition_id"] = policy_definition_id
        __props__.__dict__["resource_discovery_mode"] = resource_discovery_mode
        return GroupPolicyRemediation(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="locationFilters")
    def location_filters(self) -> pulumi.Output[Optional[Sequence[str]]]:
        return pulumi.get(self, "location_filters")

    @property
    @pulumi.getter(name="managementGroupId")
    def management_group_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "management_group_id")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="policyAssignmentId")
    def policy_assignment_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "policy_assignment_id")

    @property
    @pulumi.getter(name="policyDefinitionId")
    def policy_definition_id(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "policy_definition_id")

    @property
    @pulumi.getter(name="resourceDiscoveryMode")
    def resource_discovery_mode(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "resource_discovery_mode")

