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
    'GetExpressRouteCircuitResult',
    'AwaitableGetExpressRouteCircuitResult',
    'get_express_route_circuit',
    'get_express_route_circuit_output',
]

@pulumi.output_type
class GetExpressRouteCircuitResult:
    """
    A collection of values returned by getExpressRouteCircuit.
    """
    def __init__(__self__, id=None, location=None, name=None, peerings=None, resource_group_name=None, service_key=None, service_provider_properties=None, service_provider_provisioning_state=None, sku=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if location and not isinstance(location, str):
            raise TypeError("Expected argument 'location' to be a str")
        pulumi.set(__self__, "location", location)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if peerings and not isinstance(peerings, list):
            raise TypeError("Expected argument 'peerings' to be a list")
        pulumi.set(__self__, "peerings", peerings)
        if resource_group_name and not isinstance(resource_group_name, str):
            raise TypeError("Expected argument 'resource_group_name' to be a str")
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if service_key and not isinstance(service_key, str):
            raise TypeError("Expected argument 'service_key' to be a str")
        pulumi.set(__self__, "service_key", service_key)
        if service_provider_properties and not isinstance(service_provider_properties, list):
            raise TypeError("Expected argument 'service_provider_properties' to be a list")
        pulumi.set(__self__, "service_provider_properties", service_provider_properties)
        if service_provider_provisioning_state and not isinstance(service_provider_provisioning_state, str):
            raise TypeError("Expected argument 'service_provider_provisioning_state' to be a str")
        pulumi.set(__self__, "service_provider_provisioning_state", service_provider_provisioning_state)
        if sku and not isinstance(sku, dict):
            raise TypeError("Expected argument 'sku' to be a dict")
        pulumi.set(__self__, "sku", sku)

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def location(self) -> str:
        """
        The Azure location where the ExpressRoute circuit exists
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> str:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def peerings(self) -> Sequence['outputs.GetExpressRouteCircuitPeeringResult']:
        """
        A `peerings` block for the ExpressRoute circuit as documented below
        """
        return pulumi.get(self, "peerings")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> str:
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="serviceKey")
    def service_key(self) -> str:
        """
        The string needed by the service provider to provision the ExpressRoute circuit.
        """
        return pulumi.get(self, "service_key")

    @property
    @pulumi.getter(name="serviceProviderProperties")
    def service_provider_properties(self) -> Sequence['outputs.GetExpressRouteCircuitServiceProviderPropertyResult']:
        """
        A `service_provider_properties` block for the ExpressRoute circuit as documented below
        """
        return pulumi.get(self, "service_provider_properties")

    @property
    @pulumi.getter(name="serviceProviderProvisioningState")
    def service_provider_provisioning_state(self) -> str:
        """
        The ExpressRoute circuit provisioning state from your chosen service provider. Possible values are "NotProvisioned", "Provisioning", "Provisioned", and "Deprovisioning".
        """
        return pulumi.get(self, "service_provider_provisioning_state")

    @property
    @pulumi.getter
    def sku(self) -> 'outputs.GetExpressRouteCircuitSkuResult':
        """
        A `sku` block for the ExpressRoute circuit as documented below.
        """
        return pulumi.get(self, "sku")


class AwaitableGetExpressRouteCircuitResult(GetExpressRouteCircuitResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetExpressRouteCircuitResult(
            id=self.id,
            location=self.location,
            name=self.name,
            peerings=self.peerings,
            resource_group_name=self.resource_group_name,
            service_key=self.service_key,
            service_provider_properties=self.service_provider_properties,
            service_provider_provisioning_state=self.service_provider_provisioning_state,
            sku=self.sku)


def get_express_route_circuit(name: Optional[str] = None,
                              resource_group_name: Optional[str] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetExpressRouteCircuitResult:
    """
    Use this data source to access information about an existing ExpressRoute circuit.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.network.get_express_route_circuit(resource_group_name=azurerm_resource_group["example"]["name"],
        name=azurerm_express_route_circuit["example"]["name"])
    pulumi.export("expressRouteCircuitId", example.id)
    pulumi.export("serviceKey", example.service_key)
    ```


    :param str name: The name of the ExpressRoute circuit.
    :param str resource_group_name: The Name of the Resource Group where the ExpressRoute circuit exists.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:network/getExpressRouteCircuit:getExpressRouteCircuit', __args__, opts=opts, typ=GetExpressRouteCircuitResult).value

    return AwaitableGetExpressRouteCircuitResult(
        id=__ret__.id,
        location=__ret__.location,
        name=__ret__.name,
        peerings=__ret__.peerings,
        resource_group_name=__ret__.resource_group_name,
        service_key=__ret__.service_key,
        service_provider_properties=__ret__.service_provider_properties,
        service_provider_provisioning_state=__ret__.service_provider_provisioning_state,
        sku=__ret__.sku)


@_utilities.lift_output_func(get_express_route_circuit)
def get_express_route_circuit_output(name: Optional[pulumi.Input[str]] = None,
                                     resource_group_name: Optional[pulumi.Input[str]] = None,
                                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetExpressRouteCircuitResult]:
    """
    Use this data source to access information about an existing ExpressRoute circuit.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.network.get_express_route_circuit(resource_group_name=azurerm_resource_group["example"]["name"],
        name=azurerm_express_route_circuit["example"]["name"])
    pulumi.export("expressRouteCircuitId", example.id)
    pulumi.export("serviceKey", example.service_key)
    ```


    :param str name: The name of the ExpressRoute circuit.
    :param str resource_group_name: The Name of the Resource Group where the ExpressRoute circuit exists.
    """
    ...
