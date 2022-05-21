# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ManagementGroupArgs', 'ManagementGroup']

@pulumi.input_type
class ManagementGroupArgs:
    def __init__(__self__, *,
                 display_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parent_management_group_id: Optional[pulumi.Input[str]] = None,
                 subscription_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ManagementGroup resource.
        :param pulumi.Input[str] display_name: A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        :param pulumi.Input[str] name: The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        :param pulumi.Input[str] parent_management_group_id: The ID of the Parent Management Group. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subscription_ids: A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parent_management_group_id is not None:
            pulumi.set(__self__, "parent_management_group_id", parent_management_group_id)
        if subscription_ids is not None:
            pulumi.set(__self__, "subscription_ids", subscription_ids)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="parentManagementGroupId")
    def parent_management_group_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Parent Management Group. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "parent_management_group_id")

    @parent_management_group_id.setter
    def parent_management_group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "parent_management_group_id", value)

    @property
    @pulumi.getter(name="subscriptionIds")
    def subscription_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        return pulumi.get(self, "subscription_ids")

    @subscription_ids.setter
    def subscription_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "subscription_ids", value)


@pulumi.input_type
class _ManagementGroupState:
    def __init__(__self__, *,
                 display_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parent_management_group_id: Optional[pulumi.Input[str]] = None,
                 subscription_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering ManagementGroup resources.
        :param pulumi.Input[str] display_name: A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        :param pulumi.Input[str] name: The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        :param pulumi.Input[str] parent_management_group_id: The ID of the Parent Management Group. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subscription_ids: A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parent_management_group_id is not None:
            pulumi.set(__self__, "parent_management_group_id", parent_management_group_id)
        if subscription_ids is not None:
            pulumi.set(__self__, "subscription_ids", subscription_ids)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="parentManagementGroupId")
    def parent_management_group_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Parent Management Group. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "parent_management_group_id")

    @parent_management_group_id.setter
    def parent_management_group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "parent_management_group_id", value)

    @property
    @pulumi.getter(name="subscriptionIds")
    def subscription_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        return pulumi.get(self, "subscription_ids")

    @subscription_ids.setter
    def subscription_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "subscription_ids", value)


warnings.warn("""azure.managementgroups.ManagementGroup has been deprecated in favor of azure.management.Group""", DeprecationWarning)


class ManagementGroup(pulumi.CustomResource):
    warnings.warn("""azure.managementgroups.ManagementGroup has been deprecated in favor of azure.management.Group""", DeprecationWarning)

    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parent_management_group_id: Optional[pulumi.Input[str]] = None,
                 subscription_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Manages a Management Group.

        !> **Note:** Configuring `subscription_ids` is not supported when using the `management.GroupSubscriptionAssociation` resource, results will be unpredictable.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_subscription()
        example_parent = azure.management.Group("exampleParent",
            display_name="ParentGroup",
            subscription_ids=[current.subscription_id])
        example_child = azure.management.Group("exampleChild",
            display_name="ChildGroup",
            parent_management_group_id=example_parent.id,
            subscription_ids=[current.subscription_id])
        # other subscription IDs can go here
        ```

        ## Import

        Management Groups can be imported using the `management group resource id`, e.g.

        ```sh
         $ pulumi import azure:managementgroups/managementGroup:ManagementGroup example /providers/Microsoft.Management/managementGroups/group1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] display_name: A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        :param pulumi.Input[str] name: The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        :param pulumi.Input[str] parent_management_group_id: The ID of the Parent Management Group. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subscription_ids: A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[ManagementGroupArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Management Group.

        !> **Note:** Configuring `subscription_ids` is not supported when using the `management.GroupSubscriptionAssociation` resource, results will be unpredictable.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_subscription()
        example_parent = azure.management.Group("exampleParent",
            display_name="ParentGroup",
            subscription_ids=[current.subscription_id])
        example_child = azure.management.Group("exampleChild",
            display_name="ChildGroup",
            parent_management_group_id=example_parent.id,
            subscription_ids=[current.subscription_id])
        # other subscription IDs can go here
        ```

        ## Import

        Management Groups can be imported using the `management group resource id`, e.g.

        ```sh
         $ pulumi import azure:managementgroups/managementGroup:ManagementGroup example /providers/Microsoft.Management/managementGroups/group1
        ```

        :param str resource_name: The name of the resource.
        :param ManagementGroupArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ManagementGroupArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parent_management_group_id: Optional[pulumi.Input[str]] = None,
                 subscription_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        pulumi.log.warn("""ManagementGroup is deprecated: azure.managementgroups.ManagementGroup has been deprecated in favor of azure.management.Group""")
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ManagementGroupArgs.__new__(ManagementGroupArgs)

            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["name"] = name
            __props__.__dict__["parent_management_group_id"] = parent_management_group_id
            __props__.__dict__["subscription_ids"] = subscription_ids
        super(ManagementGroup, __self__).__init__(
            'azure:managementgroups/managementGroup:ManagementGroup',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            display_name: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            parent_management_group_id: Optional[pulumi.Input[str]] = None,
            subscription_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None) -> 'ManagementGroup':
        """
        Get an existing ManagementGroup resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] display_name: A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        :param pulumi.Input[str] name: The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        :param pulumi.Input[str] parent_management_group_id: The ID of the Parent Management Group. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subscription_ids: A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ManagementGroupState.__new__(_ManagementGroupState)

        __props__.__dict__["display_name"] = display_name
        __props__.__dict__["name"] = name
        __props__.__dict__["parent_management_group_id"] = parent_management_group_id
        __props__.__dict__["subscription_ids"] = subscription_ids
        return ManagementGroup(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        A friendly name for this Management Group. If not specified, this will be the same as the `name`.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name or UUID for this Management Group, which needs to be unique across your tenant. A new UUID will be generated if not provided. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="parentManagementGroupId")
    def parent_management_group_id(self) -> pulumi.Output[str]:
        """
        The ID of the Parent Management Group. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "parent_management_group_id")

    @property
    @pulumi.getter(name="subscriptionIds")
    def subscription_ids(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of Subscription GUIDs which should be assigned to the Management Group.
        """
        return pulumi.get(self, "subscription_ids")

