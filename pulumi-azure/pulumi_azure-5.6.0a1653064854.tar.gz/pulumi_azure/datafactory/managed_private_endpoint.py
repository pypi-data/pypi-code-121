# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ManagedPrivateEndpointArgs', 'ManagedPrivateEndpoint']

@pulumi.input_type
class ManagedPrivateEndpointArgs:
    def __init__(__self__, *,
                 data_factory_id: pulumi.Input[str],
                 target_resource_id: pulumi.Input[str],
                 fqdns: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 subresource_name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ManagedPrivateEndpoint resource.
        :param pulumi.Input[str] data_factory_id: The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[str] target_resource_id: The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] fqdns: Fully qualified domain names. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[str] subresource_name: Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        """
        pulumi.set(__self__, "data_factory_id", data_factory_id)
        pulumi.set(__self__, "target_resource_id", target_resource_id)
        if fqdns is not None:
            pulumi.set(__self__, "fqdns", fqdns)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if subresource_name is not None:
            pulumi.set(__self__, "subresource_name", subresource_name)

    @property
    @pulumi.getter(name="dataFactoryId")
    def data_factory_id(self) -> pulumi.Input[str]:
        """
        The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "data_factory_id")

    @data_factory_id.setter
    def data_factory_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "data_factory_id", value)

    @property
    @pulumi.getter(name="targetResourceId")
    def target_resource_id(self) -> pulumi.Input[str]:
        """
        The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "target_resource_id")

    @target_resource_id.setter
    def target_resource_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "target_resource_id", value)

    @property
    @pulumi.getter
    def fqdns(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Fully qualified domain names. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "fqdns")

    @fqdns.setter
    def fqdns(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "fqdns", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="subresourceName")
    def subresource_name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "subresource_name")

    @subresource_name.setter
    def subresource_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "subresource_name", value)


@pulumi.input_type
class _ManagedPrivateEndpointState:
    def __init__(__self__, *,
                 data_factory_id: Optional[pulumi.Input[str]] = None,
                 fqdns: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 subresource_name: Optional[pulumi.Input[str]] = None,
                 target_resource_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ManagedPrivateEndpoint resources.
        :param pulumi.Input[str] data_factory_id: The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] fqdns: Fully qualified domain names. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[str] subresource_name: Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        :param pulumi.Input[str] target_resource_id: The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        """
        if data_factory_id is not None:
            pulumi.set(__self__, "data_factory_id", data_factory_id)
        if fqdns is not None:
            pulumi.set(__self__, "fqdns", fqdns)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if subresource_name is not None:
            pulumi.set(__self__, "subresource_name", subresource_name)
        if target_resource_id is not None:
            pulumi.set(__self__, "target_resource_id", target_resource_id)

    @property
    @pulumi.getter(name="dataFactoryId")
    def data_factory_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "data_factory_id")

    @data_factory_id.setter
    def data_factory_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "data_factory_id", value)

    @property
    @pulumi.getter
    def fqdns(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Fully qualified domain names. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "fqdns")

    @fqdns.setter
    def fqdns(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "fqdns", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="subresourceName")
    def subresource_name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "subresource_name")

    @subresource_name.setter
    def subresource_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "subresource_name", value)

    @property
    @pulumi.getter(name="targetResourceId")
    def target_resource_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "target_resource_id")

    @target_resource_id.setter
    def target_resource_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "target_resource_id", value)


class ManagedPrivateEndpoint(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 data_factory_id: Optional[pulumi.Input[str]] = None,
                 fqdns: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 subresource_name: Optional[pulumi.Input[str]] = None,
                 target_resource_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Data Factory Managed Private Endpoint.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_factory = azure.datafactory.Factory("exampleFactory",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            managed_virtual_network_enabled=True)
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_kind="BlobStorage",
            account_tier="Standard",
            account_replication_type="LRS")
        example_managed_private_endpoint = azure.datafactory.ManagedPrivateEndpoint("exampleManagedPrivateEndpoint",
            data_factory_id=example_factory.id,
            target_resource_id=example_account.id,
            subresource_name="blob")
        ```

        ## Import

        Data Factory Managed Private Endpoint can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:datafactory/managedPrivateEndpoint:ManagedPrivateEndpoint example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.DataFactory/factories/example/managedVirtualNetworks/default/managedPrivateEndpoints/endpoint1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] data_factory_id: The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] fqdns: Fully qualified domain names. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[str] subresource_name: Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        :param pulumi.Input[str] target_resource_id: The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ManagedPrivateEndpointArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Data Factory Managed Private Endpoint.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_factory = azure.datafactory.Factory("exampleFactory",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            managed_virtual_network_enabled=True)
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_kind="BlobStorage",
            account_tier="Standard",
            account_replication_type="LRS")
        example_managed_private_endpoint = azure.datafactory.ManagedPrivateEndpoint("exampleManagedPrivateEndpoint",
            data_factory_id=example_factory.id,
            target_resource_id=example_account.id,
            subresource_name="blob")
        ```

        ## Import

        Data Factory Managed Private Endpoint can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:datafactory/managedPrivateEndpoint:ManagedPrivateEndpoint example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.DataFactory/factories/example/managedVirtualNetworks/default/managedPrivateEndpoints/endpoint1
        ```

        :param str resource_name: The name of the resource.
        :param ManagedPrivateEndpointArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ManagedPrivateEndpointArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 data_factory_id: Optional[pulumi.Input[str]] = None,
                 fqdns: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 subresource_name: Optional[pulumi.Input[str]] = None,
                 target_resource_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = ManagedPrivateEndpointArgs.__new__(ManagedPrivateEndpointArgs)

            if data_factory_id is None and not opts.urn:
                raise TypeError("Missing required property 'data_factory_id'")
            __props__.__dict__["data_factory_id"] = data_factory_id
            __props__.__dict__["fqdns"] = fqdns
            __props__.__dict__["name"] = name
            __props__.__dict__["subresource_name"] = subresource_name
            if target_resource_id is None and not opts.urn:
                raise TypeError("Missing required property 'target_resource_id'")
            __props__.__dict__["target_resource_id"] = target_resource_id
        super(ManagedPrivateEndpoint, __self__).__init__(
            'azure:datafactory/managedPrivateEndpoint:ManagedPrivateEndpoint',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            data_factory_id: Optional[pulumi.Input[str]] = None,
            fqdns: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            name: Optional[pulumi.Input[str]] = None,
            subresource_name: Optional[pulumi.Input[str]] = None,
            target_resource_id: Optional[pulumi.Input[str]] = None) -> 'ManagedPrivateEndpoint':
        """
        Get an existing ManagedPrivateEndpoint resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] data_factory_id: The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] fqdns: Fully qualified domain names. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        :param pulumi.Input[str] subresource_name: Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        :param pulumi.Input[str] target_resource_id: The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ManagedPrivateEndpointState.__new__(_ManagedPrivateEndpointState)

        __props__.__dict__["data_factory_id"] = data_factory_id
        __props__.__dict__["fqdns"] = fqdns
        __props__.__dict__["name"] = name
        __props__.__dict__["subresource_name"] = subresource_name
        __props__.__dict__["target_resource_id"] = target_resource_id
        return ManagedPrivateEndpoint(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="dataFactoryId")
    def data_factory_id(self) -> pulumi.Output[str]:
        """
        The ID of the Data Factory on which to create the Managed Private Endpoint. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "data_factory_id")

    @property
    @pulumi.getter
    def fqdns(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Fully qualified domain names. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "fqdns")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="subresourceName")
    def subresource_name(self) -> pulumi.Output[Optional[str]]:
        """
        Specifies the sub resource name which the Data Factory Private Endpoint is able to connect to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "subresource_name")

    @property
    @pulumi.getter(name="targetResourceId")
    def target_resource_id(self) -> pulumi.Output[str]:
        """
        The ID of the Private Link Enabled Remote Resource which this Data Factory Private Endpoint should be connected to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "target_resource_id")

