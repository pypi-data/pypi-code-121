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
    'GetGatewayConnectionResult',
    'AwaitableGetGatewayConnectionResult',
    'get_gateway_connection',
    'get_gateway_connection_output',
]

@pulumi.output_type
class GetGatewayConnectionResult:
    """
    A collection of values returned by getGatewayConnection.
    """
    def __init__(__self__, authorization_key=None, connection_protocol=None, dpd_timeout_seconds=None, egress_bytes_transferred=None, enable_bgp=None, express_route_circuit_id=None, express_route_gateway_bypass=None, id=None, ingress_bytes_transferred=None, ipsec_policies=None, local_azure_ip_address_enabled=None, local_network_gateway_id=None, location=None, name=None, peer_virtual_network_gateway_id=None, resource_group_name=None, resource_guid=None, routing_weight=None, shared_key=None, tags=None, traffic_selector_policies=None, type=None, use_policy_based_traffic_selectors=None, virtual_network_gateway_id=None):
        if authorization_key and not isinstance(authorization_key, str):
            raise TypeError("Expected argument 'authorization_key' to be a str")
        pulumi.set(__self__, "authorization_key", authorization_key)
        if connection_protocol and not isinstance(connection_protocol, str):
            raise TypeError("Expected argument 'connection_protocol' to be a str")
        pulumi.set(__self__, "connection_protocol", connection_protocol)
        if dpd_timeout_seconds and not isinstance(dpd_timeout_seconds, int):
            raise TypeError("Expected argument 'dpd_timeout_seconds' to be a int")
        pulumi.set(__self__, "dpd_timeout_seconds", dpd_timeout_seconds)
        if egress_bytes_transferred and not isinstance(egress_bytes_transferred, int):
            raise TypeError("Expected argument 'egress_bytes_transferred' to be a int")
        pulumi.set(__self__, "egress_bytes_transferred", egress_bytes_transferred)
        if enable_bgp and not isinstance(enable_bgp, bool):
            raise TypeError("Expected argument 'enable_bgp' to be a bool")
        pulumi.set(__self__, "enable_bgp", enable_bgp)
        if express_route_circuit_id and not isinstance(express_route_circuit_id, str):
            raise TypeError("Expected argument 'express_route_circuit_id' to be a str")
        pulumi.set(__self__, "express_route_circuit_id", express_route_circuit_id)
        if express_route_gateway_bypass and not isinstance(express_route_gateway_bypass, bool):
            raise TypeError("Expected argument 'express_route_gateway_bypass' to be a bool")
        pulumi.set(__self__, "express_route_gateway_bypass", express_route_gateway_bypass)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ingress_bytes_transferred and not isinstance(ingress_bytes_transferred, int):
            raise TypeError("Expected argument 'ingress_bytes_transferred' to be a int")
        pulumi.set(__self__, "ingress_bytes_transferred", ingress_bytes_transferred)
        if ipsec_policies and not isinstance(ipsec_policies, list):
            raise TypeError("Expected argument 'ipsec_policies' to be a list")
        pulumi.set(__self__, "ipsec_policies", ipsec_policies)
        if local_azure_ip_address_enabled and not isinstance(local_azure_ip_address_enabled, bool):
            raise TypeError("Expected argument 'local_azure_ip_address_enabled' to be a bool")
        pulumi.set(__self__, "local_azure_ip_address_enabled", local_azure_ip_address_enabled)
        if local_network_gateway_id and not isinstance(local_network_gateway_id, str):
            raise TypeError("Expected argument 'local_network_gateway_id' to be a str")
        pulumi.set(__self__, "local_network_gateway_id", local_network_gateway_id)
        if location and not isinstance(location, str):
            raise TypeError("Expected argument 'location' to be a str")
        pulumi.set(__self__, "location", location)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if peer_virtual_network_gateway_id and not isinstance(peer_virtual_network_gateway_id, str):
            raise TypeError("Expected argument 'peer_virtual_network_gateway_id' to be a str")
        pulumi.set(__self__, "peer_virtual_network_gateway_id", peer_virtual_network_gateway_id)
        if resource_group_name and not isinstance(resource_group_name, str):
            raise TypeError("Expected argument 'resource_group_name' to be a str")
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if resource_guid and not isinstance(resource_guid, str):
            raise TypeError("Expected argument 'resource_guid' to be a str")
        pulumi.set(__self__, "resource_guid", resource_guid)
        if routing_weight and not isinstance(routing_weight, int):
            raise TypeError("Expected argument 'routing_weight' to be a int")
        pulumi.set(__self__, "routing_weight", routing_weight)
        if shared_key and not isinstance(shared_key, str):
            raise TypeError("Expected argument 'shared_key' to be a str")
        pulumi.set(__self__, "shared_key", shared_key)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if traffic_selector_policies and not isinstance(traffic_selector_policies, list):
            raise TypeError("Expected argument 'traffic_selector_policies' to be a list")
        pulumi.set(__self__, "traffic_selector_policies", traffic_selector_policies)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)
        if use_policy_based_traffic_selectors and not isinstance(use_policy_based_traffic_selectors, bool):
            raise TypeError("Expected argument 'use_policy_based_traffic_selectors' to be a bool")
        pulumi.set(__self__, "use_policy_based_traffic_selectors", use_policy_based_traffic_selectors)
        if virtual_network_gateway_id and not isinstance(virtual_network_gateway_id, str):
            raise TypeError("Expected argument 'virtual_network_gateway_id' to be a str")
        pulumi.set(__self__, "virtual_network_gateway_id", virtual_network_gateway_id)

    @property
    @pulumi.getter(name="authorizationKey")
    def authorization_key(self) -> str:
        """
        The authorization key associated with the
        Express Route Circuit. This field is present only if the type is an
        ExpressRoute connection.
        """
        return pulumi.get(self, "authorization_key")

    @property
    @pulumi.getter(name="connectionProtocol")
    def connection_protocol(self) -> str:
        return pulumi.get(self, "connection_protocol")

    @property
    @pulumi.getter(name="dpdTimeoutSeconds")
    def dpd_timeout_seconds(self) -> int:
        """
        The dead peer detection timeout of this connection in seconds.
        """
        return pulumi.get(self, "dpd_timeout_seconds")

    @property
    @pulumi.getter(name="egressBytesTransferred")
    def egress_bytes_transferred(self) -> int:
        return pulumi.get(self, "egress_bytes_transferred")

    @property
    @pulumi.getter(name="enableBgp")
    def enable_bgp(self) -> bool:
        """
        If `true`, BGP (Border Gateway Protocol) is enabled
        for this connection.
        """
        return pulumi.get(self, "enable_bgp")

    @property
    @pulumi.getter(name="expressRouteCircuitId")
    def express_route_circuit_id(self) -> str:
        """
        The ID of the Express Route Circuit
        (i.e. when `type` is `ExpressRoute`).
        """
        return pulumi.get(self, "express_route_circuit_id")

    @property
    @pulumi.getter(name="expressRouteGatewayBypass")
    def express_route_gateway_bypass(self) -> bool:
        """
        If `true`, data packets will bypass ExpressRoute Gateway for data forwarding. This is only valid for ExpressRoute connections.
        """
        return pulumi.get(self, "express_route_gateway_bypass")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="ingressBytesTransferred")
    def ingress_bytes_transferred(self) -> int:
        return pulumi.get(self, "ingress_bytes_transferred")

    @property
    @pulumi.getter(name="ipsecPolicies")
    def ipsec_policies(self) -> Sequence['outputs.GetGatewayConnectionIpsecPolicyResult']:
        return pulumi.get(self, "ipsec_policies")

    @property
    @pulumi.getter(name="localAzureIpAddressEnabled")
    def local_azure_ip_address_enabled(self) -> bool:
        """
        Use private local Azure IP for the connection.
        """
        return pulumi.get(self, "local_azure_ip_address_enabled")

    @property
    @pulumi.getter(name="localNetworkGatewayId")
    def local_network_gateway_id(self) -> str:
        """
        The ID of the local network gateway
        when a Site-to-Site connection (i.e. when `type` is `IPsec`).
        """
        return pulumi.get(self, "local_network_gateway_id")

    @property
    @pulumi.getter
    def location(self) -> str:
        """
        The location/region where the connection is
        located.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> str:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="peerVirtualNetworkGatewayId")
    def peer_virtual_network_gateway_id(self) -> str:
        """
        The ID of the peer virtual
        network gateway when a VNet-to-VNet connection (i.e. when `type`
        is `Vnet2Vnet`).
        """
        return pulumi.get(self, "peer_virtual_network_gateway_id")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> str:
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="resourceGuid")
    def resource_guid(self) -> str:
        return pulumi.get(self, "resource_guid")

    @property
    @pulumi.getter(name="routingWeight")
    def routing_weight(self) -> int:
        """
        The routing weight.
        """
        return pulumi.get(self, "routing_weight")

    @property
    @pulumi.getter(name="sharedKey")
    def shared_key(self) -> str:
        """
        The shared IPSec key.
        """
        return pulumi.get(self, "shared_key")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="trafficSelectorPolicies")
    def traffic_selector_policies(self) -> Sequence['outputs.GetGatewayConnectionTrafficSelectorPolicyResult']:
        return pulumi.get(self, "traffic_selector_policies")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of connection. Valid options are `IPsec`
        (Site-to-Site), `ExpressRoute` (ExpressRoute), and `Vnet2Vnet` (VNet-to-VNet).
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter(name="usePolicyBasedTrafficSelectors")
    def use_policy_based_traffic_selectors(self) -> bool:
        """
        If `true`, policy-based traffic
        selectors are enabled for this connection. Enabling policy-based traffic
        selectors requires an `ipsec_policy` block.
        """
        return pulumi.get(self, "use_policy_based_traffic_selectors")

    @property
    @pulumi.getter(name="virtualNetworkGatewayId")
    def virtual_network_gateway_id(self) -> str:
        """
        The ID of the Virtual Network Gateway
        in which the connection is created.
        """
        return pulumi.get(self, "virtual_network_gateway_id")


class AwaitableGetGatewayConnectionResult(GetGatewayConnectionResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetGatewayConnectionResult(
            authorization_key=self.authorization_key,
            connection_protocol=self.connection_protocol,
            dpd_timeout_seconds=self.dpd_timeout_seconds,
            egress_bytes_transferred=self.egress_bytes_transferred,
            enable_bgp=self.enable_bgp,
            express_route_circuit_id=self.express_route_circuit_id,
            express_route_gateway_bypass=self.express_route_gateway_bypass,
            id=self.id,
            ingress_bytes_transferred=self.ingress_bytes_transferred,
            ipsec_policies=self.ipsec_policies,
            local_azure_ip_address_enabled=self.local_azure_ip_address_enabled,
            local_network_gateway_id=self.local_network_gateway_id,
            location=self.location,
            name=self.name,
            peer_virtual_network_gateway_id=self.peer_virtual_network_gateway_id,
            resource_group_name=self.resource_group_name,
            resource_guid=self.resource_guid,
            routing_weight=self.routing_weight,
            shared_key=self.shared_key,
            tags=self.tags,
            traffic_selector_policies=self.traffic_selector_policies,
            type=self.type,
            use_policy_based_traffic_selectors=self.use_policy_based_traffic_selectors,
            virtual_network_gateway_id=self.virtual_network_gateway_id)


def get_gateway_connection(name: Optional[str] = None,
                           resource_group_name: Optional[str] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetGatewayConnectionResult:
    """
    Use this data source to access information about an existing Virtual Network Gateway Connection.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.network.get_gateway_connection(name="production",
        resource_group_name="networking")
    pulumi.export("virtualNetworkGatewayConnectionId", example.id)
    ```


    :param str name: Specifies the name of the Virtual Network Gateway Connection.
    :param str resource_group_name: Specifies the name of the resource group the Virtual Network Gateway Connection is located in.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:network/getGatewayConnection:getGatewayConnection', __args__, opts=opts, typ=GetGatewayConnectionResult).value

    return AwaitableGetGatewayConnectionResult(
        authorization_key=__ret__.authorization_key,
        connection_protocol=__ret__.connection_protocol,
        dpd_timeout_seconds=__ret__.dpd_timeout_seconds,
        egress_bytes_transferred=__ret__.egress_bytes_transferred,
        enable_bgp=__ret__.enable_bgp,
        express_route_circuit_id=__ret__.express_route_circuit_id,
        express_route_gateway_bypass=__ret__.express_route_gateway_bypass,
        id=__ret__.id,
        ingress_bytes_transferred=__ret__.ingress_bytes_transferred,
        ipsec_policies=__ret__.ipsec_policies,
        local_azure_ip_address_enabled=__ret__.local_azure_ip_address_enabled,
        local_network_gateway_id=__ret__.local_network_gateway_id,
        location=__ret__.location,
        name=__ret__.name,
        peer_virtual_network_gateway_id=__ret__.peer_virtual_network_gateway_id,
        resource_group_name=__ret__.resource_group_name,
        resource_guid=__ret__.resource_guid,
        routing_weight=__ret__.routing_weight,
        shared_key=__ret__.shared_key,
        tags=__ret__.tags,
        traffic_selector_policies=__ret__.traffic_selector_policies,
        type=__ret__.type,
        use_policy_based_traffic_selectors=__ret__.use_policy_based_traffic_selectors,
        virtual_network_gateway_id=__ret__.virtual_network_gateway_id)


@_utilities.lift_output_func(get_gateway_connection)
def get_gateway_connection_output(name: Optional[pulumi.Input[str]] = None,
                                  resource_group_name: Optional[pulumi.Input[str]] = None,
                                  opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetGatewayConnectionResult]:
    """
    Use this data source to access information about an existing Virtual Network Gateway Connection.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.network.get_gateway_connection(name="production",
        resource_group_name="networking")
    pulumi.export("virtualNetworkGatewayConnectionId", example.id)
    ```


    :param str name: Specifies the name of the Virtual Network Gateway Connection.
    :param str resource_group_name: Specifies the name of the resource group the Virtual Network Gateway Connection is located in.
    """
    ...
