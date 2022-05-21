# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs
from ._inputs import *

__all__ = ['FactoryArgs', 'Factory']

@pulumi.input_type
class FactoryArgs:
    def __init__(__self__, *,
                 resource_group_name: pulumi.Input[str],
                 customer_managed_key_id: Optional[pulumi.Input[str]] = None,
                 customer_managed_key_identity_id: Optional[pulumi.Input[str]] = None,
                 github_configuration: Optional[pulumi.Input['FactoryGithubConfigurationArgs']] = None,
                 global_parameters: Optional[pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]]] = None,
                 identity: Optional[pulumi.Input['FactoryIdentityArgs']] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 managed_virtual_network_enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 public_network_enabled: Optional[pulumi.Input[bool]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vsts_configuration: Optional[pulumi.Input['FactoryVstsConfigurationArgs']] = None):
        """
        The set of arguments for constructing a Factory resource.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Data Factory.
        :param pulumi.Input[str] customer_managed_key_id: Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        :param pulumi.Input[str] customer_managed_key_identity_id: Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        :param pulumi.Input['FactoryGithubConfigurationArgs'] github_configuration: A `github_configuration` block as defined below.
        :param pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]] global_parameters: A list of `global_parameter` blocks as defined above.
        :param pulumi.Input['FactoryIdentityArgs'] identity: An `identity` block as defined below.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] managed_virtual_network_enabled: Is Managed Virtual Network enabled?
        :param pulumi.Input[str] name: Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[bool] public_network_enabled: Is the Data Factory visible to the public network? Defaults to `true`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input['FactoryVstsConfigurationArgs'] vsts_configuration: A `vsts_configuration` block as defined below.
        """
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if customer_managed_key_id is not None:
            pulumi.set(__self__, "customer_managed_key_id", customer_managed_key_id)
        if customer_managed_key_identity_id is not None:
            pulumi.set(__self__, "customer_managed_key_identity_id", customer_managed_key_identity_id)
        if github_configuration is not None:
            pulumi.set(__self__, "github_configuration", github_configuration)
        if global_parameters is not None:
            pulumi.set(__self__, "global_parameters", global_parameters)
        if identity is not None:
            pulumi.set(__self__, "identity", identity)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if managed_virtual_network_enabled is not None:
            pulumi.set(__self__, "managed_virtual_network_enabled", managed_virtual_network_enabled)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if public_network_enabled is not None:
            pulumi.set(__self__, "public_network_enabled", public_network_enabled)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if vsts_configuration is not None:
            pulumi.set(__self__, "vsts_configuration", vsts_configuration)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group in which to create the Data Factory.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="customerManagedKeyId")
    def customer_managed_key_id(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        """
        return pulumi.get(self, "customer_managed_key_id")

    @customer_managed_key_id.setter
    def customer_managed_key_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "customer_managed_key_id", value)

    @property
    @pulumi.getter(name="customerManagedKeyIdentityId")
    def customer_managed_key_identity_id(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        """
        return pulumi.get(self, "customer_managed_key_identity_id")

    @customer_managed_key_identity_id.setter
    def customer_managed_key_identity_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "customer_managed_key_identity_id", value)

    @property
    @pulumi.getter(name="githubConfiguration")
    def github_configuration(self) -> Optional[pulumi.Input['FactoryGithubConfigurationArgs']]:
        """
        A `github_configuration` block as defined below.
        """
        return pulumi.get(self, "github_configuration")

    @github_configuration.setter
    def github_configuration(self, value: Optional[pulumi.Input['FactoryGithubConfigurationArgs']]):
        pulumi.set(self, "github_configuration", value)

    @property
    @pulumi.getter(name="globalParameters")
    def global_parameters(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]]]:
        """
        A list of `global_parameter` blocks as defined above.
        """
        return pulumi.get(self, "global_parameters")

    @global_parameters.setter
    def global_parameters(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]]]):
        pulumi.set(self, "global_parameters", value)

    @property
    @pulumi.getter
    def identity(self) -> Optional[pulumi.Input['FactoryIdentityArgs']]:
        """
        An `identity` block as defined below.
        """
        return pulumi.get(self, "identity")

    @identity.setter
    def identity(self, value: Optional[pulumi.Input['FactoryIdentityArgs']]):
        pulumi.set(self, "identity", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="managedVirtualNetworkEnabled")
    def managed_virtual_network_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is Managed Virtual Network enabled?
        """
        return pulumi.get(self, "managed_virtual_network_enabled")

    @managed_virtual_network_enabled.setter
    def managed_virtual_network_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "managed_virtual_network_enabled", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="publicNetworkEnabled")
    def public_network_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the Data Factory visible to the public network? Defaults to `true`.
        """
        return pulumi.get(self, "public_network_enabled")

    @public_network_enabled.setter
    def public_network_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "public_network_enabled", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="vstsConfiguration")
    def vsts_configuration(self) -> Optional[pulumi.Input['FactoryVstsConfigurationArgs']]:
        """
        A `vsts_configuration` block as defined below.
        """
        return pulumi.get(self, "vsts_configuration")

    @vsts_configuration.setter
    def vsts_configuration(self, value: Optional[pulumi.Input['FactoryVstsConfigurationArgs']]):
        pulumi.set(self, "vsts_configuration", value)


@pulumi.input_type
class _FactoryState:
    def __init__(__self__, *,
                 customer_managed_key_id: Optional[pulumi.Input[str]] = None,
                 customer_managed_key_identity_id: Optional[pulumi.Input[str]] = None,
                 github_configuration: Optional[pulumi.Input['FactoryGithubConfigurationArgs']] = None,
                 global_parameters: Optional[pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]]] = None,
                 identity: Optional[pulumi.Input['FactoryIdentityArgs']] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 managed_virtual_network_enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 public_network_enabled: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vsts_configuration: Optional[pulumi.Input['FactoryVstsConfigurationArgs']] = None):
        """
        Input properties used for looking up and filtering Factory resources.
        :param pulumi.Input[str] customer_managed_key_id: Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        :param pulumi.Input[str] customer_managed_key_identity_id: Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        :param pulumi.Input['FactoryGithubConfigurationArgs'] github_configuration: A `github_configuration` block as defined below.
        :param pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]] global_parameters: A list of `global_parameter` blocks as defined above.
        :param pulumi.Input['FactoryIdentityArgs'] identity: An `identity` block as defined below.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] managed_virtual_network_enabled: Is Managed Virtual Network enabled?
        :param pulumi.Input[str] name: Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[bool] public_network_enabled: Is the Data Factory visible to the public network? Defaults to `true`.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Data Factory.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input['FactoryVstsConfigurationArgs'] vsts_configuration: A `vsts_configuration` block as defined below.
        """
        if customer_managed_key_id is not None:
            pulumi.set(__self__, "customer_managed_key_id", customer_managed_key_id)
        if customer_managed_key_identity_id is not None:
            pulumi.set(__self__, "customer_managed_key_identity_id", customer_managed_key_identity_id)
        if github_configuration is not None:
            pulumi.set(__self__, "github_configuration", github_configuration)
        if global_parameters is not None:
            pulumi.set(__self__, "global_parameters", global_parameters)
        if identity is not None:
            pulumi.set(__self__, "identity", identity)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if managed_virtual_network_enabled is not None:
            pulumi.set(__self__, "managed_virtual_network_enabled", managed_virtual_network_enabled)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if public_network_enabled is not None:
            pulumi.set(__self__, "public_network_enabled", public_network_enabled)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if vsts_configuration is not None:
            pulumi.set(__self__, "vsts_configuration", vsts_configuration)

    @property
    @pulumi.getter(name="customerManagedKeyId")
    def customer_managed_key_id(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        """
        return pulumi.get(self, "customer_managed_key_id")

    @customer_managed_key_id.setter
    def customer_managed_key_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "customer_managed_key_id", value)

    @property
    @pulumi.getter(name="customerManagedKeyIdentityId")
    def customer_managed_key_identity_id(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        """
        return pulumi.get(self, "customer_managed_key_identity_id")

    @customer_managed_key_identity_id.setter
    def customer_managed_key_identity_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "customer_managed_key_identity_id", value)

    @property
    @pulumi.getter(name="githubConfiguration")
    def github_configuration(self) -> Optional[pulumi.Input['FactoryGithubConfigurationArgs']]:
        """
        A `github_configuration` block as defined below.
        """
        return pulumi.get(self, "github_configuration")

    @github_configuration.setter
    def github_configuration(self, value: Optional[pulumi.Input['FactoryGithubConfigurationArgs']]):
        pulumi.set(self, "github_configuration", value)

    @property
    @pulumi.getter(name="globalParameters")
    def global_parameters(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]]]:
        """
        A list of `global_parameter` blocks as defined above.
        """
        return pulumi.get(self, "global_parameters")

    @global_parameters.setter
    def global_parameters(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FactoryGlobalParameterArgs']]]]):
        pulumi.set(self, "global_parameters", value)

    @property
    @pulumi.getter
    def identity(self) -> Optional[pulumi.Input['FactoryIdentityArgs']]:
        """
        An `identity` block as defined below.
        """
        return pulumi.get(self, "identity")

    @identity.setter
    def identity(self, value: Optional[pulumi.Input['FactoryIdentityArgs']]):
        pulumi.set(self, "identity", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="managedVirtualNetworkEnabled")
    def managed_virtual_network_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is Managed Virtual Network enabled?
        """
        return pulumi.get(self, "managed_virtual_network_enabled")

    @managed_virtual_network_enabled.setter
    def managed_virtual_network_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "managed_virtual_network_enabled", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="publicNetworkEnabled")
    def public_network_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the Data Factory visible to the public network? Defaults to `true`.
        """
        return pulumi.get(self, "public_network_enabled")

    @public_network_enabled.setter
    def public_network_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "public_network_enabled", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group in which to create the Data Factory.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="vstsConfiguration")
    def vsts_configuration(self) -> Optional[pulumi.Input['FactoryVstsConfigurationArgs']]:
        """
        A `vsts_configuration` block as defined below.
        """
        return pulumi.get(self, "vsts_configuration")

    @vsts_configuration.setter
    def vsts_configuration(self, value: Optional[pulumi.Input['FactoryVstsConfigurationArgs']]):
        pulumi.set(self, "vsts_configuration", value)


class Factory(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 customer_managed_key_id: Optional[pulumi.Input[str]] = None,
                 customer_managed_key_identity_id: Optional[pulumi.Input[str]] = None,
                 github_configuration: Optional[pulumi.Input[pulumi.InputType['FactoryGithubConfigurationArgs']]] = None,
                 global_parameters: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FactoryGlobalParameterArgs']]]]] = None,
                 identity: Optional[pulumi.Input[pulumi.InputType['FactoryIdentityArgs']]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 managed_virtual_network_enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 public_network_enabled: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vsts_configuration: Optional[pulumi.Input[pulumi.InputType['FactoryVstsConfigurationArgs']]] = None,
                 __props__=None):
        """
        Manages an Azure Data Factory (Version 2).

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_factory = azure.datafactory.Factory("exampleFactory",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name)
        ```

        ## Import

        Data Factory can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:datafactory/factory:Factory example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.DataFactory/factories/example
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] customer_managed_key_id: Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        :param pulumi.Input[str] customer_managed_key_identity_id: Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        :param pulumi.Input[pulumi.InputType['FactoryGithubConfigurationArgs']] github_configuration: A `github_configuration` block as defined below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FactoryGlobalParameterArgs']]]] global_parameters: A list of `global_parameter` blocks as defined above.
        :param pulumi.Input[pulumi.InputType['FactoryIdentityArgs']] identity: An `identity` block as defined below.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] managed_virtual_network_enabled: Is Managed Virtual Network enabled?
        :param pulumi.Input[str] name: Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[bool] public_network_enabled: Is the Data Factory visible to the public network? Defaults to `true`.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Data Factory.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[pulumi.InputType['FactoryVstsConfigurationArgs']] vsts_configuration: A `vsts_configuration` block as defined below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: FactoryArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an Azure Data Factory (Version 2).

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_factory = azure.datafactory.Factory("exampleFactory",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name)
        ```

        ## Import

        Data Factory can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:datafactory/factory:Factory example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.DataFactory/factories/example
        ```

        :param str resource_name: The name of the resource.
        :param FactoryArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(FactoryArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 customer_managed_key_id: Optional[pulumi.Input[str]] = None,
                 customer_managed_key_identity_id: Optional[pulumi.Input[str]] = None,
                 github_configuration: Optional[pulumi.Input[pulumi.InputType['FactoryGithubConfigurationArgs']]] = None,
                 global_parameters: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FactoryGlobalParameterArgs']]]]] = None,
                 identity: Optional[pulumi.Input[pulumi.InputType['FactoryIdentityArgs']]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 managed_virtual_network_enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 public_network_enabled: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vsts_configuration: Optional[pulumi.Input[pulumi.InputType['FactoryVstsConfigurationArgs']]] = None,
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
            __props__ = FactoryArgs.__new__(FactoryArgs)

            __props__.__dict__["customer_managed_key_id"] = customer_managed_key_id
            __props__.__dict__["customer_managed_key_identity_id"] = customer_managed_key_identity_id
            __props__.__dict__["github_configuration"] = github_configuration
            __props__.__dict__["global_parameters"] = global_parameters
            __props__.__dict__["identity"] = identity
            __props__.__dict__["location"] = location
            __props__.__dict__["managed_virtual_network_enabled"] = managed_virtual_network_enabled
            __props__.__dict__["name"] = name
            __props__.__dict__["public_network_enabled"] = public_network_enabled
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            __props__.__dict__["tags"] = tags
            __props__.__dict__["vsts_configuration"] = vsts_configuration
        super(Factory, __self__).__init__(
            'azure:datafactory/factory:Factory',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            customer_managed_key_id: Optional[pulumi.Input[str]] = None,
            customer_managed_key_identity_id: Optional[pulumi.Input[str]] = None,
            github_configuration: Optional[pulumi.Input[pulumi.InputType['FactoryGithubConfigurationArgs']]] = None,
            global_parameters: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FactoryGlobalParameterArgs']]]]] = None,
            identity: Optional[pulumi.Input[pulumi.InputType['FactoryIdentityArgs']]] = None,
            location: Optional[pulumi.Input[str]] = None,
            managed_virtual_network_enabled: Optional[pulumi.Input[bool]] = None,
            name: Optional[pulumi.Input[str]] = None,
            public_network_enabled: Optional[pulumi.Input[bool]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            vsts_configuration: Optional[pulumi.Input[pulumi.InputType['FactoryVstsConfigurationArgs']]] = None) -> 'Factory':
        """
        Get an existing Factory resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] customer_managed_key_id: Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        :param pulumi.Input[str] customer_managed_key_identity_id: Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        :param pulumi.Input[pulumi.InputType['FactoryGithubConfigurationArgs']] github_configuration: A `github_configuration` block as defined below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FactoryGlobalParameterArgs']]]] global_parameters: A list of `global_parameter` blocks as defined above.
        :param pulumi.Input[pulumi.InputType['FactoryIdentityArgs']] identity: An `identity` block as defined below.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] managed_virtual_network_enabled: Is Managed Virtual Network enabled?
        :param pulumi.Input[str] name: Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[bool] public_network_enabled: Is the Data Factory visible to the public network? Defaults to `true`.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Data Factory.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[pulumi.InputType['FactoryVstsConfigurationArgs']] vsts_configuration: A `vsts_configuration` block as defined below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _FactoryState.__new__(_FactoryState)

        __props__.__dict__["customer_managed_key_id"] = customer_managed_key_id
        __props__.__dict__["customer_managed_key_identity_id"] = customer_managed_key_identity_id
        __props__.__dict__["github_configuration"] = github_configuration
        __props__.__dict__["global_parameters"] = global_parameters
        __props__.__dict__["identity"] = identity
        __props__.__dict__["location"] = location
        __props__.__dict__["managed_virtual_network_enabled"] = managed_virtual_network_enabled
        __props__.__dict__["name"] = name
        __props__.__dict__["public_network_enabled"] = public_network_enabled
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["tags"] = tags
        __props__.__dict__["vsts_configuration"] = vsts_configuration
        return Factory(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="customerManagedKeyId")
    def customer_managed_key_id(self) -> pulumi.Output[Optional[str]]:
        """
        Specifies the Azure Key Vault Key ID to be used as the Customer Managed Key (CMK) for double encryption. Required with user assigned identity.
        """
        return pulumi.get(self, "customer_managed_key_id")

    @property
    @pulumi.getter(name="customerManagedKeyIdentityId")
    def customer_managed_key_identity_id(self) -> pulumi.Output[Optional[str]]:
        """
        Specifies the ID of the user assigned identity associated with the Customer Managed Key. Must be supplied if `customer_managed_key_id` is set.
        """
        return pulumi.get(self, "customer_managed_key_identity_id")

    @property
    @pulumi.getter(name="githubConfiguration")
    def github_configuration(self) -> pulumi.Output[Optional['outputs.FactoryGithubConfiguration']]:
        """
        A `github_configuration` block as defined below.
        """
        return pulumi.get(self, "github_configuration")

    @property
    @pulumi.getter(name="globalParameters")
    def global_parameters(self) -> pulumi.Output[Optional[Sequence['outputs.FactoryGlobalParameter']]]:
        """
        A list of `global_parameter` blocks as defined above.
        """
        return pulumi.get(self, "global_parameters")

    @property
    @pulumi.getter
    def identity(self) -> pulumi.Output[Optional['outputs.FactoryIdentity']]:
        """
        An `identity` block as defined below.
        """
        return pulumi.get(self, "identity")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter(name="managedVirtualNetworkEnabled")
    def managed_virtual_network_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Is Managed Virtual Network enabled?
        """
        return pulumi.get(self, "managed_virtual_network_enabled")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the Data Factory. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="publicNetworkEnabled")
    def public_network_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Is the Data Factory visible to the public network? Defaults to `true`.
        """
        return pulumi.get(self, "public_network_enabled")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group in which to create the Data Factory.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="vstsConfiguration")
    def vsts_configuration(self) -> pulumi.Output[Optional['outputs.FactoryVstsConfiguration']]:
        """
        A `vsts_configuration` block as defined below.
        """
        return pulumi.get(self, "vsts_configuration")

