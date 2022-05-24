"""
Type annotations for networkmanager service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_networkmanager.client import NetworkManagerClient
    from mypy_boto3_networkmanager.paginator import (
        DescribeGlobalNetworksPaginator,
        GetConnectPeerAssociationsPaginator,
        GetConnectionsPaginator,
        GetCoreNetworkChangeSetPaginator,
        GetCustomerGatewayAssociationsPaginator,
        GetDevicesPaginator,
        GetLinkAssociationsPaginator,
        GetLinksPaginator,
        GetNetworkResourceCountsPaginator,
        GetNetworkResourceRelationshipsPaginator,
        GetNetworkResourcesPaginator,
        GetNetworkTelemetryPaginator,
        GetSitesPaginator,
        GetTransitGatewayConnectPeerAssociationsPaginator,
        GetTransitGatewayRegistrationsPaginator,
        ListAttachmentsPaginator,
        ListConnectPeersPaginator,
        ListCoreNetworkPolicyVersionsPaginator,
        ListCoreNetworksPaginator,
    )

    session = Session()
    client: NetworkManagerClient = session.client("networkmanager")

    describe_global_networks_paginator: DescribeGlobalNetworksPaginator = client.get_paginator("describe_global_networks")
    get_connect_peer_associations_paginator: GetConnectPeerAssociationsPaginator = client.get_paginator("get_connect_peer_associations")
    get_connections_paginator: GetConnectionsPaginator = client.get_paginator("get_connections")
    get_core_network_change_set_paginator: GetCoreNetworkChangeSetPaginator = client.get_paginator("get_core_network_change_set")
    get_customer_gateway_associations_paginator: GetCustomerGatewayAssociationsPaginator = client.get_paginator("get_customer_gateway_associations")
    get_devices_paginator: GetDevicesPaginator = client.get_paginator("get_devices")
    get_link_associations_paginator: GetLinkAssociationsPaginator = client.get_paginator("get_link_associations")
    get_links_paginator: GetLinksPaginator = client.get_paginator("get_links")
    get_network_resource_counts_paginator: GetNetworkResourceCountsPaginator = client.get_paginator("get_network_resource_counts")
    get_network_resource_relationships_paginator: GetNetworkResourceRelationshipsPaginator = client.get_paginator("get_network_resource_relationships")
    get_network_resources_paginator: GetNetworkResourcesPaginator = client.get_paginator("get_network_resources")
    get_network_telemetry_paginator: GetNetworkTelemetryPaginator = client.get_paginator("get_network_telemetry")
    get_sites_paginator: GetSitesPaginator = client.get_paginator("get_sites")
    get_transit_gateway_connect_peer_associations_paginator: GetTransitGatewayConnectPeerAssociationsPaginator = client.get_paginator("get_transit_gateway_connect_peer_associations")
    get_transit_gateway_registrations_paginator: GetTransitGatewayRegistrationsPaginator = client.get_paginator("get_transit_gateway_registrations")
    list_attachments_paginator: ListAttachmentsPaginator = client.get_paginator("list_attachments")
    list_connect_peers_paginator: ListConnectPeersPaginator = client.get_paginator("list_connect_peers")
    list_core_network_policy_versions_paginator: ListCoreNetworkPolicyVersionsPaginator = client.get_paginator("list_core_network_policy_versions")
    list_core_networks_paginator: ListCoreNetworksPaginator = client.get_paginator("list_core_networks")
    ```
"""
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import AttachmentStateType, AttachmentTypeType
from .type_defs import (
    DescribeGlobalNetworksResponseTypeDef,
    GetConnectionsResponseTypeDef,
    GetConnectPeerAssociationsResponseTypeDef,
    GetCoreNetworkChangeSetResponseTypeDef,
    GetCustomerGatewayAssociationsResponseTypeDef,
    GetDevicesResponseTypeDef,
    GetLinkAssociationsResponseTypeDef,
    GetLinksResponseTypeDef,
    GetNetworkResourceCountsResponseTypeDef,
    GetNetworkResourceRelationshipsResponseTypeDef,
    GetNetworkResourcesResponseTypeDef,
    GetNetworkTelemetryResponseTypeDef,
    GetSitesResponseTypeDef,
    GetTransitGatewayConnectPeerAssociationsResponseTypeDef,
    GetTransitGatewayRegistrationsResponseTypeDef,
    ListAttachmentsResponseTypeDef,
    ListConnectPeersResponseTypeDef,
    ListCoreNetworkPolicyVersionsResponseTypeDef,
    ListCoreNetworksResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "DescribeGlobalNetworksPaginator",
    "GetConnectPeerAssociationsPaginator",
    "GetConnectionsPaginator",
    "GetCoreNetworkChangeSetPaginator",
    "GetCustomerGatewayAssociationsPaginator",
    "GetDevicesPaginator",
    "GetLinkAssociationsPaginator",
    "GetLinksPaginator",
    "GetNetworkResourceCountsPaginator",
    "GetNetworkResourceRelationshipsPaginator",
    "GetNetworkResourcesPaginator",
    "GetNetworkTelemetryPaginator",
    "GetSitesPaginator",
    "GetTransitGatewayConnectPeerAssociationsPaginator",
    "GetTransitGatewayRegistrationsPaginator",
    "ListAttachmentsPaginator",
    "ListConnectPeersPaginator",
    "ListCoreNetworkPolicyVersionsPaginator",
    "ListCoreNetworksPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeGlobalNetworksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.DescribeGlobalNetworks)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#describeglobalnetworkspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeGlobalNetworksResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.DescribeGlobalNetworks.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#describeglobalnetworkspaginator)
        """


class GetConnectPeerAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetConnectPeerAssociations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getconnectpeerassociationspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        ConnectPeerIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetConnectPeerAssociationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetConnectPeerAssociations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getconnectpeerassociationspaginator)
        """


class GetConnectionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetConnections)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getconnectionspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        ConnectionIds: Sequence[str] = ...,
        DeviceId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetConnectionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetConnections.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getconnectionspaginator)
        """


class GetCoreNetworkChangeSetPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetCoreNetworkChangeSet)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getcorenetworkchangesetpaginator)
    """

    def paginate(
        self,
        *,
        CoreNetworkId: str,
        PolicyVersionId: int,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetCoreNetworkChangeSetResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetCoreNetworkChangeSet.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getcorenetworkchangesetpaginator)
        """


class GetCustomerGatewayAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetCustomerGatewayAssociations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getcustomergatewayassociationspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        CustomerGatewayArns: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetCustomerGatewayAssociationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetCustomerGatewayAssociations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getcustomergatewayassociationspaginator)
        """


class GetDevicesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetDevices)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getdevicespaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        DeviceIds: Sequence[str] = ...,
        SiteId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetDevicesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetDevices.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getdevicespaginator)
        """


class GetLinkAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetLinkAssociations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getlinkassociationspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        DeviceId: str = ...,
        LinkId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetLinkAssociationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetLinkAssociations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getlinkassociationspaginator)
        """


class GetLinksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetLinks)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getlinkspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        LinkIds: Sequence[str] = ...,
        SiteId: str = ...,
        Type: str = ...,
        Provider: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetLinksResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetLinks.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getlinkspaginator)
        """


class GetNetworkResourceCountsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkResourceCounts)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworkresourcecountspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        ResourceType: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetNetworkResourceCountsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkResourceCounts.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworkresourcecountspaginator)
        """


class GetNetworkResourceRelationshipsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkResourceRelationships)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworkresourcerelationshipspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        CoreNetworkId: str = ...,
        RegisteredGatewayArn: str = ...,
        AwsRegion: str = ...,
        AccountId: str = ...,
        ResourceType: str = ...,
        ResourceArn: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetNetworkResourceRelationshipsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkResourceRelationships.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworkresourcerelationshipspaginator)
        """


class GetNetworkResourcesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkResources)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworkresourcespaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        CoreNetworkId: str = ...,
        RegisteredGatewayArn: str = ...,
        AwsRegion: str = ...,
        AccountId: str = ...,
        ResourceType: str = ...,
        ResourceArn: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetNetworkResourcesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkResources.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworkresourcespaginator)
        """


class GetNetworkTelemetryPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkTelemetry)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworktelemetrypaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        CoreNetworkId: str = ...,
        RegisteredGatewayArn: str = ...,
        AwsRegion: str = ...,
        AccountId: str = ...,
        ResourceType: str = ...,
        ResourceArn: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetNetworkTelemetryResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetNetworkTelemetry.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getnetworktelemetrypaginator)
        """


class GetSitesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetSites)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getsitespaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        SiteIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetSitesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetSites.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#getsitespaginator)
        """


class GetTransitGatewayConnectPeerAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetTransitGatewayConnectPeerAssociations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#gettransitgatewayconnectpeerassociationspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        TransitGatewayConnectPeerArns: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayConnectPeerAssociationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetTransitGatewayConnectPeerAssociations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#gettransitgatewayconnectpeerassociationspaginator)
        """


class GetTransitGatewayRegistrationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetTransitGatewayRegistrations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#gettransitgatewayregistrationspaginator)
    """

    def paginate(
        self,
        *,
        GlobalNetworkId: str,
        TransitGatewayArns: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetTransitGatewayRegistrationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.GetTransitGatewayRegistrations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#gettransitgatewayregistrationspaginator)
        """


class ListAttachmentsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListAttachments)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listattachmentspaginator)
    """

    def paginate(
        self,
        *,
        CoreNetworkId: str = ...,
        AttachmentType: AttachmentTypeType = ...,
        EdgeLocation: str = ...,
        State: AttachmentStateType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListAttachmentsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListAttachments.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listattachmentspaginator)
        """


class ListConnectPeersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListConnectPeers)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listconnectpeerspaginator)
    """

    def paginate(
        self,
        *,
        CoreNetworkId: str = ...,
        ConnectAttachmentId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListConnectPeersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListConnectPeers.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listconnectpeerspaginator)
        """


class ListCoreNetworkPolicyVersionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListCoreNetworkPolicyVersions)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listcorenetworkpolicyversionspaginator)
    """

    def paginate(
        self, *, CoreNetworkId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListCoreNetworkPolicyVersionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListCoreNetworkPolicyVersions.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listcorenetworkpolicyversionspaginator)
        """


class ListCoreNetworksPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListCoreNetworks)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listcorenetworkspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListCoreNetworksResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html#NetworkManager.Paginator.ListCoreNetworks.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/paginators/#listcorenetworkspaginator)
        """
