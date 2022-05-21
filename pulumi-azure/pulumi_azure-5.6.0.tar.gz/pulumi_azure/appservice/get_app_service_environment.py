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
    'GetAppServiceEnvironmentResult',
    'AwaitableGetAppServiceEnvironmentResult',
    'get_app_service_environment',
    'get_app_service_environment_output',
]

@pulumi.output_type
class GetAppServiceEnvironmentResult:
    """
    A collection of values returned by getAppServiceEnvironment.
    """
    def __init__(__self__, cluster_settings=None, front_end_scale_factor=None, id=None, internal_ip_address=None, location=None, name=None, outbound_ip_addresses=None, pricing_tier=None, resource_group_name=None, service_ip_address=None, tags=None):
        if cluster_settings and not isinstance(cluster_settings, list):
            raise TypeError("Expected argument 'cluster_settings' to be a list")
        pulumi.set(__self__, "cluster_settings", cluster_settings)
        if front_end_scale_factor and not isinstance(front_end_scale_factor, int):
            raise TypeError("Expected argument 'front_end_scale_factor' to be a int")
        pulumi.set(__self__, "front_end_scale_factor", front_end_scale_factor)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if internal_ip_address and not isinstance(internal_ip_address, str):
            raise TypeError("Expected argument 'internal_ip_address' to be a str")
        pulumi.set(__self__, "internal_ip_address", internal_ip_address)
        if location and not isinstance(location, str):
            raise TypeError("Expected argument 'location' to be a str")
        pulumi.set(__self__, "location", location)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if outbound_ip_addresses and not isinstance(outbound_ip_addresses, list):
            raise TypeError("Expected argument 'outbound_ip_addresses' to be a list")
        pulumi.set(__self__, "outbound_ip_addresses", outbound_ip_addresses)
        if pricing_tier and not isinstance(pricing_tier, str):
            raise TypeError("Expected argument 'pricing_tier' to be a str")
        pulumi.set(__self__, "pricing_tier", pricing_tier)
        if resource_group_name and not isinstance(resource_group_name, str):
            raise TypeError("Expected argument 'resource_group_name' to be a str")
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if service_ip_address and not isinstance(service_ip_address, str):
            raise TypeError("Expected argument 'service_ip_address' to be a str")
        pulumi.set(__self__, "service_ip_address", service_ip_address)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="clusterSettings")
    def cluster_settings(self) -> Sequence['outputs.GetAppServiceEnvironmentClusterSettingResult']:
        """
        Zero or more `cluster_setting` blocks as defined below.
        """
        return pulumi.get(self, "cluster_settings")

    @property
    @pulumi.getter(name="frontEndScaleFactor")
    def front_end_scale_factor(self) -> int:
        """
        The number of app instances per App Service Environment Front End.
        """
        return pulumi.get(self, "front_end_scale_factor")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="internalIpAddress")
    def internal_ip_address(self) -> str:
        """
        IP address of internal load balancer of the App Service Environment.
        """
        return pulumi.get(self, "internal_ip_address")

    @property
    @pulumi.getter
    def location(self) -> str:
        """
        The Azure Region where the App Service Environment exists.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the Cluster Setting.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="outboundIpAddresses")
    def outbound_ip_addresses(self) -> Sequence[str]:
        """
        List of outbound IP addresses of the App Service Environment.
        """
        return pulumi.get(self, "outbound_ip_addresses")

    @property
    @pulumi.getter(name="pricingTier")
    def pricing_tier(self) -> str:
        """
        The Pricing Tier (Isolated SKU) of the App Service Environment.
        """
        return pulumi.get(self, "pricing_tier")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> str:
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="serviceIpAddress")
    def service_ip_address(self) -> str:
        """
        IP address of service endpoint of the App Service Environment.
        """
        return pulumi.get(self, "service_ip_address")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        A mapping of tags assigned to the App Service Environment.
        """
        return pulumi.get(self, "tags")


class AwaitableGetAppServiceEnvironmentResult(GetAppServiceEnvironmentResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAppServiceEnvironmentResult(
            cluster_settings=self.cluster_settings,
            front_end_scale_factor=self.front_end_scale_factor,
            id=self.id,
            internal_ip_address=self.internal_ip_address,
            location=self.location,
            name=self.name,
            outbound_ip_addresses=self.outbound_ip_addresses,
            pricing_tier=self.pricing_tier,
            resource_group_name=self.resource_group_name,
            service_ip_address=self.service_ip_address,
            tags=self.tags)


def get_app_service_environment(name: Optional[str] = None,
                                resource_group_name: Optional[str] = None,
                                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAppServiceEnvironmentResult:
    """
    Use this data source to access information about an existing App Service Environment.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.appservice.get_app_service_environment(name="existing-ase",
        resource_group_name="existing-rg")
    pulumi.export("id", example.id)
    ```


    :param str name: The name of this App Service Environment.
    :param str resource_group_name: The name of the Resource Group where the App Service Environment exists.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:appservice/getAppServiceEnvironment:getAppServiceEnvironment', __args__, opts=opts, typ=GetAppServiceEnvironmentResult).value

    return AwaitableGetAppServiceEnvironmentResult(
        cluster_settings=__ret__.cluster_settings,
        front_end_scale_factor=__ret__.front_end_scale_factor,
        id=__ret__.id,
        internal_ip_address=__ret__.internal_ip_address,
        location=__ret__.location,
        name=__ret__.name,
        outbound_ip_addresses=__ret__.outbound_ip_addresses,
        pricing_tier=__ret__.pricing_tier,
        resource_group_name=__ret__.resource_group_name,
        service_ip_address=__ret__.service_ip_address,
        tags=__ret__.tags)


@_utilities.lift_output_func(get_app_service_environment)
def get_app_service_environment_output(name: Optional[pulumi.Input[str]] = None,
                                       resource_group_name: Optional[pulumi.Input[str]] = None,
                                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAppServiceEnvironmentResult]:
    """
    Use this data source to access information about an existing App Service Environment.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.appservice.get_app_service_environment(name="existing-ase",
        resource_group_name="existing-rg")
    pulumi.export("id", example.id)
    ```


    :param str name: The name of this App Service Environment.
    :param str resource_group_name: The name of the Resource Group where the App Service Environment exists.
    """
    ...
