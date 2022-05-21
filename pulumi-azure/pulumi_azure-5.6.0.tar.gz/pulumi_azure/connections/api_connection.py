# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ApiConnectionArgs', 'ApiConnection']

@pulumi.input_type
class ApiConnectionArgs:
    def __init__(__self__, *,
                 managed_api_id: pulumi.Input[str],
                 resource_group_name: pulumi.Input[str],
                 display_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameter_values: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ApiConnection resource.
        :param pulumi.Input[str] managed_api_id: The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] display_name: A display name for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] name: The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameter_values: A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the API Connection.
        """
        pulumi.set(__self__, "managed_api_id", managed_api_id)
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parameter_values is not None:
            pulumi.set(__self__, "parameter_values", parameter_values)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="managedApiId")
    def managed_api_id(self) -> pulumi.Input[str]:
        """
        The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "managed_api_id")

    @managed_api_id.setter
    def managed_api_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "managed_api_id", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        A display name for this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="parameterValues")
    def parameter_values(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "parameter_values")

    @parameter_values.setter
    def parameter_values(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameter_values", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the API Connection.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _ApiConnectionState:
    def __init__(__self__, *,
                 display_name: Optional[pulumi.Input[str]] = None,
                 managed_api_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameter_values: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering ApiConnection resources.
        :param pulumi.Input[str] display_name: A display name for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] managed_api_id: The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] name: The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameter_values: A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the API Connection.
        """
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if managed_api_id is not None:
            pulumi.set(__self__, "managed_api_id", managed_api_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parameter_values is not None:
            pulumi.set(__self__, "parameter_values", parameter_values)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        A display name for this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter(name="managedApiId")
    def managed_api_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "managed_api_id")

    @managed_api_id.setter
    def managed_api_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "managed_api_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="parameterValues")
    def parameter_values(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "parameter_values")

    @parameter_values.setter
    def parameter_values(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameter_values", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the API Connection.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


class ApiConnection(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 managed_api_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameter_values: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Manages an API Connection.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_managed_api = azure.connections.get_managed_api_output(name="servicebus",
            location=example_resource_group.location)
        example_api_connection = azure.connections.ApiConnection("exampleApiConnection",
            resource_group_name=example_resource_group.name,
            managed_api_id=example_managed_api.id,
            display_name="Example 1",
            parameter_values={
                "connectionString": azurerm_servicebus_namespace["example"]["default_primary_connection_string"],
            },
            tags={
                "Hello": "World",
            })
        ```

        ## Import

        API Connections can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:connections/apiConnection:ApiConnection example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.Web/connections/example-connection
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] display_name: A display name for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] managed_api_id: The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] name: The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameter_values: A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the API Connection.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ApiConnectionArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an API Connection.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_managed_api = azure.connections.get_managed_api_output(name="servicebus",
            location=example_resource_group.location)
        example_api_connection = azure.connections.ApiConnection("exampleApiConnection",
            resource_group_name=example_resource_group.name,
            managed_api_id=example_managed_api.id,
            display_name="Example 1",
            parameter_values={
                "connectionString": azurerm_servicebus_namespace["example"]["default_primary_connection_string"],
            },
            tags={
                "Hello": "World",
            })
        ```

        ## Import

        API Connections can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:connections/apiConnection:ApiConnection example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.Web/connections/example-connection
        ```

        :param str resource_name: The name of the resource.
        :param ApiConnectionArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ApiConnectionArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 managed_api_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameter_values: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
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
            __props__ = ApiConnectionArgs.__new__(ApiConnectionArgs)

            __props__.__dict__["display_name"] = display_name
            if managed_api_id is None and not opts.urn:
                raise TypeError("Missing required property 'managed_api_id'")
            __props__.__dict__["managed_api_id"] = managed_api_id
            __props__.__dict__["name"] = name
            __props__.__dict__["parameter_values"] = parameter_values
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            __props__.__dict__["tags"] = tags
        super(ApiConnection, __self__).__init__(
            'azure:connections/apiConnection:ApiConnection',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            display_name: Optional[pulumi.Input[str]] = None,
            managed_api_id: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            parameter_values: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'ApiConnection':
        """
        Get an existing ApiConnection resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] display_name: A display name for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] managed_api_id: The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] name: The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameter_values: A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the API Connection.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ApiConnectionState.__new__(_ApiConnectionState)

        __props__.__dict__["display_name"] = display_name
        __props__.__dict__["managed_api_id"] = managed_api_id
        __props__.__dict__["name"] = name
        __props__.__dict__["parameter_values"] = parameter_values
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["tags"] = tags
        return ApiConnection(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        A display name for this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter(name="managedApiId")
    def managed_api_id(self) -> pulumi.Output[str]:
        """
        The ID of the Managed API which this API Connection is linked to. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "managed_api_id")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The Name which should be used for this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="parameterValues")
    def parameter_values(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of parameter values associated with this API Connection. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "parameter_values")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the Resource Group where this API Connection should exist. Changing this forces a new API Connection to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags which should be assigned to the API Connection.
        """
        return pulumi.get(self, "tags")

