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
    'GetBackendAddressPoolResult',
    'AwaitableGetBackendAddressPoolResult',
    'get_backend_address_pool',
    'get_backend_address_pool_output',
]

@pulumi.output_type
class GetBackendAddressPoolResult:
    """
    A collection of values returned by getBackendAddressPool.
    """
    def __init__(__self__, backend_addresses=None, backend_ip_configurations=None, id=None, load_balancing_rules=None, loadbalancer_id=None, name=None, outbound_rules=None):
        if backend_addresses and not isinstance(backend_addresses, list):
            raise TypeError("Expected argument 'backend_addresses' to be a list")
        pulumi.set(__self__, "backend_addresses", backend_addresses)
        if backend_ip_configurations and not isinstance(backend_ip_configurations, list):
            raise TypeError("Expected argument 'backend_ip_configurations' to be a list")
        pulumi.set(__self__, "backend_ip_configurations", backend_ip_configurations)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if load_balancing_rules and not isinstance(load_balancing_rules, list):
            raise TypeError("Expected argument 'load_balancing_rules' to be a list")
        pulumi.set(__self__, "load_balancing_rules", load_balancing_rules)
        if loadbalancer_id and not isinstance(loadbalancer_id, str):
            raise TypeError("Expected argument 'loadbalancer_id' to be a str")
        pulumi.set(__self__, "loadbalancer_id", loadbalancer_id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if outbound_rules and not isinstance(outbound_rules, list):
            raise TypeError("Expected argument 'outbound_rules' to be a list")
        pulumi.set(__self__, "outbound_rules", outbound_rules)

    @property
    @pulumi.getter(name="backendAddresses")
    def backend_addresses(self) -> Sequence['outputs.GetBackendAddressPoolBackendAddressResult']:
        """
        A list of `backend_address` block as defined below.
        """
        return pulumi.get(self, "backend_addresses")

    @property
    @pulumi.getter(name="backendIpConfigurations")
    def backend_ip_configurations(self) -> Sequence['outputs.GetBackendAddressPoolBackendIpConfigurationResult']:
        """
        A list of references to IP addresses defined in network interfaces.
        """
        return pulumi.get(self, "backend_ip_configurations")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="loadBalancingRules")
    def load_balancing_rules(self) -> Sequence[str]:
        """
        A list of the Load Balancing Rules associated with this Backend Address Pool.
        """
        return pulumi.get(self, "load_balancing_rules")

    @property
    @pulumi.getter(name="loadbalancerId")
    def loadbalancer_id(self) -> str:
        return pulumi.get(self, "loadbalancer_id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the Backend Address.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="outboundRules")
    def outbound_rules(self) -> Sequence[str]:
        """
        A list of the Load Balancing Outbound Rules associated with this Backend Address Pool.
        """
        return pulumi.get(self, "outbound_rules")


class AwaitableGetBackendAddressPoolResult(GetBackendAddressPoolResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetBackendAddressPoolResult(
            backend_addresses=self.backend_addresses,
            backend_ip_configurations=self.backend_ip_configurations,
            id=self.id,
            load_balancing_rules=self.load_balancing_rules,
            loadbalancer_id=self.loadbalancer_id,
            name=self.name,
            outbound_rules=self.outbound_rules)


def get_backend_address_pool(loadbalancer_id: Optional[str] = None,
                             name: Optional[str] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetBackendAddressPoolResult:
    """
    Use this data source to access information about an existing Load Balancer's Backend Address Pool.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example_lb = azure.lb.get_lb(name="example-lb",
        resource_group_name="example-resources")
    example_backend_address_pool = azure.lb.get_backend_address_pool(name="first",
        loadbalancer_id=example_lb.id)
    pulumi.export("backendAddressPoolId", example_backend_address_pool.id)
    pulumi.export("backendIpConfigurationIds", [__item["id"] for __item in data["azurerm_lb_backend_address_pool"]["beap"]["backend_ip_configurations"]])
    ```


    :param str loadbalancer_id: The ID of the Load Balancer in which the Backend Address Pool exists.
    :param str name: Specifies the name of the Backend Address Pool.
    """
    __args__ = dict()
    __args__['loadbalancerId'] = loadbalancer_id
    __args__['name'] = name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:lb/getBackendAddressPool:getBackendAddressPool', __args__, opts=opts, typ=GetBackendAddressPoolResult).value

    return AwaitableGetBackendAddressPoolResult(
        backend_addresses=__ret__.backend_addresses,
        backend_ip_configurations=__ret__.backend_ip_configurations,
        id=__ret__.id,
        load_balancing_rules=__ret__.load_balancing_rules,
        loadbalancer_id=__ret__.loadbalancer_id,
        name=__ret__.name,
        outbound_rules=__ret__.outbound_rules)


@_utilities.lift_output_func(get_backend_address_pool)
def get_backend_address_pool_output(loadbalancer_id: Optional[pulumi.Input[str]] = None,
                                    name: Optional[pulumi.Input[str]] = None,
                                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetBackendAddressPoolResult]:
    """
    Use this data source to access information about an existing Load Balancer's Backend Address Pool.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example_lb = azure.lb.get_lb(name="example-lb",
        resource_group_name="example-resources")
    example_backend_address_pool = azure.lb.get_backend_address_pool(name="first",
        loadbalancer_id=example_lb.id)
    pulumi.export("backendAddressPoolId", example_backend_address_pool.id)
    pulumi.export("backendIpConfigurationIds", [__item["id"] for __item in data["azurerm_lb_backend_address_pool"]["beap"]["backend_ip_configurations"]])
    ```


    :param str loadbalancer_id: The ID of the Load Balancer in which the Backend Address Pool exists.
    :param str name: Specifies the name of the Backend Address Pool.
    """
    ...
