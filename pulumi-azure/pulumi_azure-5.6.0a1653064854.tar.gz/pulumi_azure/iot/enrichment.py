# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['EnrichmentArgs', 'Enrichment']

@pulumi.input_type
class EnrichmentArgs:
    def __init__(__self__, *,
                 endpoint_names: pulumi.Input[Sequence[pulumi.Input[str]]],
                 iothub_name: pulumi.Input[str],
                 key: pulumi.Input[str],
                 resource_group_name: pulumi.Input[str],
                 value: pulumi.Input[str]):
        """
        The set of arguments for constructing a Enrichment resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] endpoint_names: The list of endpoints which will be enriched.
        :param pulumi.Input[str] key: The key of the enrichment.
        :param pulumi.Input[str] value: The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        pulumi.set(__self__, "endpoint_names", endpoint_names)
        pulumi.set(__self__, "iothub_name", iothub_name)
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter(name="endpointNames")
    def endpoint_names(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        The list of endpoints which will be enriched.
        """
        return pulumi.get(self, "endpoint_names")

    @endpoint_names.setter
    def endpoint_names(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "endpoint_names", value)

    @property
    @pulumi.getter(name="iothubName")
    def iothub_name(self) -> pulumi.Input[str]:
        return pulumi.get(self, "iothub_name")

    @iothub_name.setter
    def iothub_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "iothub_name", value)

    @property
    @pulumi.getter
    def key(self) -> pulumi.Input[str]:
        """
        The key of the enrichment.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: pulumi.Input[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        """
        The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class _EnrichmentState:
    def __init__(__self__, *,
                 endpoint_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 iothub_name: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering Enrichment resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] endpoint_names: The list of endpoints which will be enriched.
        :param pulumi.Input[str] key: The key of the enrichment.
        :param pulumi.Input[str] value: The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        if endpoint_names is not None:
            pulumi.set(__self__, "endpoint_names", endpoint_names)
        if iothub_name is not None:
            pulumi.set(__self__, "iothub_name", iothub_name)
        if key is not None:
            pulumi.set(__self__, "key", key)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter(name="endpointNames")
    def endpoint_names(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The list of endpoints which will be enriched.
        """
        return pulumi.get(self, "endpoint_names")

    @endpoint_names.setter
    def endpoint_names(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "endpoint_names", value)

    @property
    @pulumi.getter(name="iothubName")
    def iothub_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "iothub_name")

    @iothub_name.setter
    def iothub_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "iothub_name", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[pulumi.Input[str]]:
        """
        The key of the enrichment.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[pulumi.Input[str]]:
        """
        The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value", value)


class Enrichment(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 iothub_name: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages an IotHub Enrichment

        > **NOTE:** Enrichment can be defined either directly on the `iot.IoTHub` resource, or using the `iot.Enrichment` resources - but the two cannot be used together. If both are used against the same IoTHub, spurious changes will occur.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_tier="Standard",
            account_replication_type="LRS")
        example_container = azure.storage.Container("exampleContainer",
            storage_account_name=example_account.name,
            container_access_type="private")
        example_io_t_hub = azure.iot.IoTHub("exampleIoTHub",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            sku=azure.iot.IoTHubSkuArgs(
                name="S1",
                capacity=1,
            ),
            tags={
                "purpose": "testing",
            })
        example_endpoint_storage_container = azure.iot.EndpointStorageContainer("exampleEndpointStorageContainer",
            resource_group_name=example_resource_group.name,
            iothub_id=example_io_t_hub.id,
            connection_string=example_account.primary_blob_connection_string,
            batch_frequency_in_seconds=60,
            max_chunk_size_in_bytes=10485760,
            container_name=example_container.name,
            encoding="Avro",
            file_name_format="{iothub}/{partition}_{YYYY}_{MM}_{DD}_{HH}_{mm}")
        example_route = azure.iot.Route("exampleRoute",
            resource_group_name=example_resource_group.name,
            iothub_name=example_io_t_hub.name,
            source="DeviceMessages",
            condition="true",
            endpoint_names=[example_endpoint_storage_container.name],
            enabled=True)
        example_enrichment = azure.iot.Enrichment("exampleEnrichment",
            resource_group_name=example_resource_group.name,
            iothub_name=example_io_t_hub.name,
            key="example",
            value="my value",
            endpoint_names=[example_endpoint_storage_container.name])
        ```

        ## Import

        IoTHub Enrichment can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:iot/enrichment:Enrichment enrichment1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Devices/IotHubs/hub1/Enrichments/enrichment1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] endpoint_names: The list of endpoints which will be enriched.
        :param pulumi.Input[str] key: The key of the enrichment.
        :param pulumi.Input[str] value: The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EnrichmentArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an IotHub Enrichment

        > **NOTE:** Enrichment can be defined either directly on the `iot.IoTHub` resource, or using the `iot.Enrichment` resources - but the two cannot be used together. If both are used against the same IoTHub, spurious changes will occur.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_tier="Standard",
            account_replication_type="LRS")
        example_container = azure.storage.Container("exampleContainer",
            storage_account_name=example_account.name,
            container_access_type="private")
        example_io_t_hub = azure.iot.IoTHub("exampleIoTHub",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            sku=azure.iot.IoTHubSkuArgs(
                name="S1",
                capacity=1,
            ),
            tags={
                "purpose": "testing",
            })
        example_endpoint_storage_container = azure.iot.EndpointStorageContainer("exampleEndpointStorageContainer",
            resource_group_name=example_resource_group.name,
            iothub_id=example_io_t_hub.id,
            connection_string=example_account.primary_blob_connection_string,
            batch_frequency_in_seconds=60,
            max_chunk_size_in_bytes=10485760,
            container_name=example_container.name,
            encoding="Avro",
            file_name_format="{iothub}/{partition}_{YYYY}_{MM}_{DD}_{HH}_{mm}")
        example_route = azure.iot.Route("exampleRoute",
            resource_group_name=example_resource_group.name,
            iothub_name=example_io_t_hub.name,
            source="DeviceMessages",
            condition="true",
            endpoint_names=[example_endpoint_storage_container.name],
            enabled=True)
        example_enrichment = azure.iot.Enrichment("exampleEnrichment",
            resource_group_name=example_resource_group.name,
            iothub_name=example_io_t_hub.name,
            key="example",
            value="my value",
            endpoint_names=[example_endpoint_storage_container.name])
        ```

        ## Import

        IoTHub Enrichment can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:iot/enrichment:Enrichment enrichment1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Devices/IotHubs/hub1/Enrichments/enrichment1
        ```

        :param str resource_name: The name of the resource.
        :param EnrichmentArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EnrichmentArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 iothub_name: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None,
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
            __props__ = EnrichmentArgs.__new__(EnrichmentArgs)

            if endpoint_names is None and not opts.urn:
                raise TypeError("Missing required property 'endpoint_names'")
            __props__.__dict__["endpoint_names"] = endpoint_names
            if iothub_name is None and not opts.urn:
                raise TypeError("Missing required property 'iothub_name'")
            __props__.__dict__["iothub_name"] = iothub_name
            if key is None and not opts.urn:
                raise TypeError("Missing required property 'key'")
            __props__.__dict__["key"] = key
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            if value is None and not opts.urn:
                raise TypeError("Missing required property 'value'")
            __props__.__dict__["value"] = value
        super(Enrichment, __self__).__init__(
            'azure:iot/enrichment:Enrichment',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            endpoint_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            iothub_name: Optional[pulumi.Input[str]] = None,
            key: Optional[pulumi.Input[str]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            value: Optional[pulumi.Input[str]] = None) -> 'Enrichment':
        """
        Get an existing Enrichment resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] endpoint_names: The list of endpoints which will be enriched.
        :param pulumi.Input[str] key: The key of the enrichment.
        :param pulumi.Input[str] value: The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _EnrichmentState.__new__(_EnrichmentState)

        __props__.__dict__["endpoint_names"] = endpoint_names
        __props__.__dict__["iothub_name"] = iothub_name
        __props__.__dict__["key"] = key
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["value"] = value
        return Enrichment(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="endpointNames")
    def endpoint_names(self) -> pulumi.Output[Sequence[str]]:
        """
        The list of endpoints which will be enriched.
        """
        return pulumi.get(self, "endpoint_names")

    @property
    @pulumi.getter(name="iothubName")
    def iothub_name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "iothub_name")

    @property
    @pulumi.getter
    def key(self) -> pulumi.Output[str]:
        """
        The key of the enrichment.
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter
    def value(self) -> pulumi.Output[str]:
        """
        The value of the enrichment. Value can be any static string, the name of the IoT hub sending the message (use `$iothubname`) or information from the device twin (ex: `$twin.tags.latitude`)
        """
        return pulumi.get(self, "value")

