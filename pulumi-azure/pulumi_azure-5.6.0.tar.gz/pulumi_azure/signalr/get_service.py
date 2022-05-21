# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetServiceResult',
    'AwaitableGetServiceResult',
    'get_service',
    'get_service_output',
]

@pulumi.output_type
class GetServiceResult:
    """
    A collection of values returned by getService.
    """
    def __init__(__self__, hostname=None, id=None, ip_address=None, location=None, name=None, primary_access_key=None, primary_connection_string=None, public_port=None, resource_group_name=None, secondary_access_key=None, secondary_connection_string=None, server_port=None, tags=None):
        if hostname and not isinstance(hostname, str):
            raise TypeError("Expected argument 'hostname' to be a str")
        pulumi.set(__self__, "hostname", hostname)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ip_address and not isinstance(ip_address, str):
            raise TypeError("Expected argument 'ip_address' to be a str")
        pulumi.set(__self__, "ip_address", ip_address)
        if location and not isinstance(location, str):
            raise TypeError("Expected argument 'location' to be a str")
        pulumi.set(__self__, "location", location)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if primary_access_key and not isinstance(primary_access_key, str):
            raise TypeError("Expected argument 'primary_access_key' to be a str")
        pulumi.set(__self__, "primary_access_key", primary_access_key)
        if primary_connection_string and not isinstance(primary_connection_string, str):
            raise TypeError("Expected argument 'primary_connection_string' to be a str")
        pulumi.set(__self__, "primary_connection_string", primary_connection_string)
        if public_port and not isinstance(public_port, int):
            raise TypeError("Expected argument 'public_port' to be a int")
        pulumi.set(__self__, "public_port", public_port)
        if resource_group_name and not isinstance(resource_group_name, str):
            raise TypeError("Expected argument 'resource_group_name' to be a str")
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if secondary_access_key and not isinstance(secondary_access_key, str):
            raise TypeError("Expected argument 'secondary_access_key' to be a str")
        pulumi.set(__self__, "secondary_access_key", secondary_access_key)
        if secondary_connection_string and not isinstance(secondary_connection_string, str):
            raise TypeError("Expected argument 'secondary_connection_string' to be a str")
        pulumi.set(__self__, "secondary_connection_string", secondary_connection_string)
        if server_port and not isinstance(server_port, int):
            raise TypeError("Expected argument 'server_port' to be a int")
        pulumi.set(__self__, "server_port", server_port)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def hostname(self) -> str:
        """
        The FQDN of the SignalR service.
        """
        return pulumi.get(self, "hostname")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="ipAddress")
    def ip_address(self) -> str:
        """
        The publicly accessible IP of the SignalR service.
        """
        return pulumi.get(self, "ip_address")

    @property
    @pulumi.getter
    def location(self) -> str:
        """
        Specifies the supported Azure location where the SignalR service exists.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> str:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="primaryAccessKey")
    def primary_access_key(self) -> str:
        """
        The primary access key of the SignalR service.
        """
        return pulumi.get(self, "primary_access_key")

    @property
    @pulumi.getter(name="primaryConnectionString")
    def primary_connection_string(self) -> str:
        """
        The primary connection string of the SignalR service.
        """
        return pulumi.get(self, "primary_connection_string")

    @property
    @pulumi.getter(name="publicPort")
    def public_port(self) -> int:
        """
        The publicly accessible port of the SignalR service which is designed for browser/client use.
        """
        return pulumi.get(self, "public_port")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> str:
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="secondaryAccessKey")
    def secondary_access_key(self) -> str:
        """
        The secondary access key of the SignalR service.
        """
        return pulumi.get(self, "secondary_access_key")

    @property
    @pulumi.getter(name="secondaryConnectionString")
    def secondary_connection_string(self) -> str:
        """
        The secondary connection string of the SignalR service.
        """
        return pulumi.get(self, "secondary_connection_string")

    @property
    @pulumi.getter(name="serverPort")
    def server_port(self) -> int:
        """
        The publicly accessible port of the SignalR service which is designed for customer server side use.
        """
        return pulumi.get(self, "server_port")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        return pulumi.get(self, "tags")


class AwaitableGetServiceResult(GetServiceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetServiceResult(
            hostname=self.hostname,
            id=self.id,
            ip_address=self.ip_address,
            location=self.location,
            name=self.name,
            primary_access_key=self.primary_access_key,
            primary_connection_string=self.primary_connection_string,
            public_port=self.public_port,
            resource_group_name=self.resource_group_name,
            secondary_access_key=self.secondary_access_key,
            secondary_connection_string=self.secondary_connection_string,
            server_port=self.server_port,
            tags=self.tags)


def get_service(name: Optional[str] = None,
                resource_group_name: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetServiceResult:
    """
    Use this data source to access information about an existing Azure SignalR service.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.signalr.get_service(name="test-signalr",
        resource_group_name="signalr-resource-group")
    ```


    :param str name: Specifies the name of the SignalR service.
    :param str resource_group_name: Specifies the name of the resource group the SignalR service is located in.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:signalr/getService:getService', __args__, opts=opts, typ=GetServiceResult).value

    return AwaitableGetServiceResult(
        hostname=__ret__.hostname,
        id=__ret__.id,
        ip_address=__ret__.ip_address,
        location=__ret__.location,
        name=__ret__.name,
        primary_access_key=__ret__.primary_access_key,
        primary_connection_string=__ret__.primary_connection_string,
        public_port=__ret__.public_port,
        resource_group_name=__ret__.resource_group_name,
        secondary_access_key=__ret__.secondary_access_key,
        secondary_connection_string=__ret__.secondary_connection_string,
        server_port=__ret__.server_port,
        tags=__ret__.tags)


@_utilities.lift_output_func(get_service)
def get_service_output(name: Optional[pulumi.Input[str]] = None,
                       resource_group_name: Optional[pulumi.Input[str]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetServiceResult]:
    """
    Use this data source to access information about an existing Azure SignalR service.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.signalr.get_service(name="test-signalr",
        resource_group_name="signalr-resource-group")
    ```


    :param str name: Specifies the name of the SignalR service.
    :param str resource_group_name: Specifies the name of the resource group the SignalR service is located in.
    """
    ...
