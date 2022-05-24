"""
Type annotations for networkmanager service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmanager/type_defs/)

Usage::

    ```python
    from mypy_boto3_networkmanager.type_defs import AWSLocationTypeDef

    data: AWSLocationTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AttachmentStateType,
    AttachmentTypeType,
    ChangeActionType,
    ChangeSetStateType,
    ChangeTypeType,
    ConnectionStateType,
    ConnectionStatusType,
    ConnectionTypeType,
    ConnectPeerAssociationStateType,
    ConnectPeerStateType,
    CoreNetworkPolicyAliasType,
    CoreNetworkStateType,
    CustomerGatewayAssociationStateType,
    DeviceStateType,
    GlobalNetworkStateType,
    LinkAssociationStateType,
    LinkStateType,
    RouteAnalysisCompletionReasonCodeType,
    RouteAnalysisCompletionResultCodeType,
    RouteAnalysisStatusType,
    RouteStateType,
    RouteTableTypeType,
    RouteTypeType,
    SiteStateType,
    TransitGatewayConnectPeerAssociationStateType,
    TransitGatewayRegistrationStateType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AWSLocationTypeDef",
    "AcceptAttachmentRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AccountStatusTypeDef",
    "AssociateConnectPeerRequestRequestTypeDef",
    "ConnectPeerAssociationTypeDef",
    "AssociateCustomerGatewayRequestRequestTypeDef",
    "CustomerGatewayAssociationTypeDef",
    "AssociateLinkRequestRequestTypeDef",
    "LinkAssociationTypeDef",
    "AssociateTransitGatewayConnectPeerRequestRequestTypeDef",
    "TransitGatewayConnectPeerAssociationTypeDef",
    "TagTypeDef",
    "BandwidthTypeDef",
    "BgpOptionsTypeDef",
    "ConnectAttachmentOptionsTypeDef",
    "ConnectPeerBgpConfigurationTypeDef",
    "ConnectionHealthTypeDef",
    "CoreNetworkChangeValuesTypeDef",
    "CoreNetworkEdgeTypeDef",
    "CoreNetworkPolicyErrorTypeDef",
    "CoreNetworkPolicyVersionTypeDef",
    "CoreNetworkSegmentEdgeIdentifierTypeDef",
    "CoreNetworkSegmentTypeDef",
    "LocationTypeDef",
    "VpcOptionsTypeDef",
    "DeleteAttachmentRequestRequestTypeDef",
    "DeleteConnectPeerRequestRequestTypeDef",
    "DeleteConnectionRequestRequestTypeDef",
    "DeleteCoreNetworkPolicyVersionRequestRequestTypeDef",
    "DeleteCoreNetworkRequestRequestTypeDef",
    "DeleteDeviceRequestRequestTypeDef",
    "DeleteGlobalNetworkRequestRequestTypeDef",
    "DeleteLinkRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteSiteRequestRequestTypeDef",
    "DeregisterTransitGatewayRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeGlobalNetworksRequestRequestTypeDef",
    "DisassociateConnectPeerRequestRequestTypeDef",
    "DisassociateCustomerGatewayRequestRequestTypeDef",
    "DisassociateLinkRequestRequestTypeDef",
    "DisassociateTransitGatewayConnectPeerRequestRequestTypeDef",
    "ExecuteCoreNetworkChangeSetRequestRequestTypeDef",
    "GetConnectAttachmentRequestRequestTypeDef",
    "GetConnectPeerAssociationsRequestRequestTypeDef",
    "GetConnectPeerRequestRequestTypeDef",
    "GetConnectionsRequestRequestTypeDef",
    "GetCoreNetworkChangeSetRequestRequestTypeDef",
    "GetCoreNetworkPolicyRequestRequestTypeDef",
    "GetCoreNetworkRequestRequestTypeDef",
    "GetCustomerGatewayAssociationsRequestRequestTypeDef",
    "GetDevicesRequestRequestTypeDef",
    "GetLinkAssociationsRequestRequestTypeDef",
    "GetLinksRequestRequestTypeDef",
    "GetNetworkResourceCountsRequestRequestTypeDef",
    "NetworkResourceCountTypeDef",
    "GetNetworkResourceRelationshipsRequestRequestTypeDef",
    "RelationshipTypeDef",
    "GetNetworkResourcesRequestRequestTypeDef",
    "GetNetworkTelemetryRequestRequestTypeDef",
    "GetResourcePolicyRequestRequestTypeDef",
    "GetRouteAnalysisRequestRequestTypeDef",
    "GetSiteToSiteVpnAttachmentRequestRequestTypeDef",
    "GetSitesRequestRequestTypeDef",
    "GetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef",
    "GetTransitGatewayRegistrationsRequestRequestTypeDef",
    "GetVpcAttachmentRequestRequestTypeDef",
    "ListAttachmentsRequestRequestTypeDef",
    "ListConnectPeersRequestRequestTypeDef",
    "ListCoreNetworkPolicyVersionsRequestRequestTypeDef",
    "ListCoreNetworksRequestRequestTypeDef",
    "ListOrganizationServiceAccessStatusRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "NetworkResourceSummaryTypeDef",
    "NetworkRouteDestinationTypeDef",
    "PutCoreNetworkPolicyRequestRequestTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "RegisterTransitGatewayRequestRequestTypeDef",
    "RejectAttachmentRequestRequestTypeDef",
    "RestoreCoreNetworkPolicyVersionRequestRequestTypeDef",
    "RouteAnalysisCompletionTypeDef",
    "RouteAnalysisEndpointOptionsSpecificationTypeDef",
    "RouteAnalysisEndpointOptionsTypeDef",
    "StartOrganizationServiceAccessUpdateRequestRequestTypeDef",
    "TransitGatewayRegistrationStateReasonTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateConnectionRequestRequestTypeDef",
    "UpdateCoreNetworkRequestRequestTypeDef",
    "UpdateGlobalNetworkRequestRequestTypeDef",
    "UpdateNetworkResourceMetadataRequestRequestTypeDef",
    "GetResourcePolicyResponseTypeDef",
    "UpdateNetworkResourceMetadataResponseTypeDef",
    "OrganizationStatusTypeDef",
    "AssociateConnectPeerResponseTypeDef",
    "DisassociateConnectPeerResponseTypeDef",
    "GetConnectPeerAssociationsResponseTypeDef",
    "AssociateCustomerGatewayResponseTypeDef",
    "DisassociateCustomerGatewayResponseTypeDef",
    "GetCustomerGatewayAssociationsResponseTypeDef",
    "AssociateLinkResponseTypeDef",
    "DisassociateLinkResponseTypeDef",
    "GetLinkAssociationsResponseTypeDef",
    "AssociateTransitGatewayConnectPeerResponseTypeDef",
    "DisassociateTransitGatewayConnectPeerResponseTypeDef",
    "GetTransitGatewayConnectPeerAssociationsResponseTypeDef",
    "ConnectPeerSummaryTypeDef",
    "ConnectionTypeDef",
    "CoreNetworkSummaryTypeDef",
    "CreateConnectionRequestRequestTypeDef",
    "CreateCoreNetworkRequestRequestTypeDef",
    "CreateGlobalNetworkRequestRequestTypeDef",
    "CreateSiteToSiteVpnAttachmentRequestRequestTypeDef",
    "GlobalNetworkTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "NetworkResourceTypeDef",
    "ProposedSegmentChangeTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateLinkRequestRequestTypeDef",
    "LinkTypeDef",
    "UpdateLinkRequestRequestTypeDef",
    "CreateConnectPeerRequestRequestTypeDef",
    "CreateConnectAttachmentRequestRequestTypeDef",
    "ConnectPeerConfigurationTypeDef",
    "NetworkTelemetryTypeDef",
    "CoreNetworkChangeTypeDef",
    "CoreNetworkPolicyTypeDef",
    "ListCoreNetworkPolicyVersionsResponseTypeDef",
    "RouteTableIdentifierTypeDef",
    "CoreNetworkTypeDef",
    "CreateDeviceRequestRequestTypeDef",
    "CreateSiteRequestRequestTypeDef",
    "DeviceTypeDef",
    "SiteTypeDef",
    "UpdateDeviceRequestRequestTypeDef",
    "UpdateSiteRequestRequestTypeDef",
    "CreateVpcAttachmentRequestRequestTypeDef",
    "UpdateVpcAttachmentRequestRequestTypeDef",
    "DescribeGlobalNetworksRequestDescribeGlobalNetworksPaginateTypeDef",
    "GetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef",
    "GetConnectionsRequestGetConnectionsPaginateTypeDef",
    "GetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef",
    "GetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef",
    "GetDevicesRequestGetDevicesPaginateTypeDef",
    "GetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef",
    "GetLinksRequestGetLinksPaginateTypeDef",
    "GetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef",
    "GetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef",
    "GetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef",
    "GetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef",
    "GetSitesRequestGetSitesPaginateTypeDef",
    "GetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef",
    "GetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef",
    "ListAttachmentsRequestListAttachmentsPaginateTypeDef",
    "ListConnectPeersRequestListConnectPeersPaginateTypeDef",
    "ListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef",
    "ListCoreNetworksRequestListCoreNetworksPaginateTypeDef",
    "GetNetworkResourceCountsResponseTypeDef",
    "GetNetworkResourceRelationshipsResponseTypeDef",
    "PathComponentTypeDef",
    "NetworkRouteTypeDef",
    "StartRouteAnalysisRequestRequestTypeDef",
    "TransitGatewayRegistrationTypeDef",
    "ListOrganizationServiceAccessStatusResponseTypeDef",
    "StartOrganizationServiceAccessUpdateResponseTypeDef",
    "ListConnectPeersResponseTypeDef",
    "CreateConnectionResponseTypeDef",
    "DeleteConnectionResponseTypeDef",
    "GetConnectionsResponseTypeDef",
    "UpdateConnectionResponseTypeDef",
    "ListCoreNetworksResponseTypeDef",
    "CreateGlobalNetworkResponseTypeDef",
    "DeleteGlobalNetworkResponseTypeDef",
    "DescribeGlobalNetworksResponseTypeDef",
    "UpdateGlobalNetworkResponseTypeDef",
    "GetNetworkResourcesResponseTypeDef",
    "AttachmentTypeDef",
    "CreateLinkResponseTypeDef",
    "DeleteLinkResponseTypeDef",
    "GetLinksResponseTypeDef",
    "UpdateLinkResponseTypeDef",
    "ConnectPeerTypeDef",
    "GetNetworkTelemetryResponseTypeDef",
    "GetCoreNetworkChangeSetResponseTypeDef",
    "DeleteCoreNetworkPolicyVersionResponseTypeDef",
    "GetCoreNetworkPolicyResponseTypeDef",
    "PutCoreNetworkPolicyResponseTypeDef",
    "RestoreCoreNetworkPolicyVersionResponseTypeDef",
    "GetNetworkRoutesRequestRequestTypeDef",
    "CreateCoreNetworkResponseTypeDef",
    "DeleteCoreNetworkResponseTypeDef",
    "GetCoreNetworkResponseTypeDef",
    "UpdateCoreNetworkResponseTypeDef",
    "CreateDeviceResponseTypeDef",
    "DeleteDeviceResponseTypeDef",
    "GetDevicesResponseTypeDef",
    "UpdateDeviceResponseTypeDef",
    "CreateSiteResponseTypeDef",
    "DeleteSiteResponseTypeDef",
    "GetSitesResponseTypeDef",
    "UpdateSiteResponseTypeDef",
    "RouteAnalysisPathTypeDef",
    "GetNetworkRoutesResponseTypeDef",
    "DeregisterTransitGatewayResponseTypeDef",
    "GetTransitGatewayRegistrationsResponseTypeDef",
    "RegisterTransitGatewayResponseTypeDef",
    "AcceptAttachmentResponseTypeDef",
    "ConnectAttachmentTypeDef",
    "DeleteAttachmentResponseTypeDef",
    "ListAttachmentsResponseTypeDef",
    "RejectAttachmentResponseTypeDef",
    "SiteToSiteVpnAttachmentTypeDef",
    "VpcAttachmentTypeDef",
    "CreateConnectPeerResponseTypeDef",
    "DeleteConnectPeerResponseTypeDef",
    "GetConnectPeerResponseTypeDef",
    "RouteAnalysisTypeDef",
    "CreateConnectAttachmentResponseTypeDef",
    "GetConnectAttachmentResponseTypeDef",
    "CreateSiteToSiteVpnAttachmentResponseTypeDef",
    "GetSiteToSiteVpnAttachmentResponseTypeDef",
    "CreateVpcAttachmentResponseTypeDef",
    "GetVpcAttachmentResponseTypeDef",
    "UpdateVpcAttachmentResponseTypeDef",
    "GetRouteAnalysisResponseTypeDef",
    "StartRouteAnalysisResponseTypeDef",
)

AWSLocationTypeDef = TypedDict(
    "AWSLocationTypeDef",
    {
        "Zone": str,
        "SubnetArn": str,
    },
    total=False,
)

AcceptAttachmentRequestRequestTypeDef = TypedDict(
    "AcceptAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

AccountStatusTypeDef = TypedDict(
    "AccountStatusTypeDef",
    {
        "AccountId": str,
        "SLRDeploymentStatus": str,
    },
    total=False,
)

_RequiredAssociateConnectPeerRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateConnectPeerRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "ConnectPeerId": str,
        "DeviceId": str,
    },
)
_OptionalAssociateConnectPeerRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateConnectPeerRequestRequestTypeDef",
    {
        "LinkId": str,
    },
    total=False,
)


class AssociateConnectPeerRequestRequestTypeDef(
    _RequiredAssociateConnectPeerRequestRequestTypeDef,
    _OptionalAssociateConnectPeerRequestRequestTypeDef,
):
    pass


ConnectPeerAssociationTypeDef = TypedDict(
    "ConnectPeerAssociationTypeDef",
    {
        "ConnectPeerId": str,
        "GlobalNetworkId": str,
        "DeviceId": str,
        "LinkId": str,
        "State": ConnectPeerAssociationStateType,
    },
    total=False,
)

_RequiredAssociateCustomerGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateCustomerGatewayRequestRequestTypeDef",
    {
        "CustomerGatewayArn": str,
        "GlobalNetworkId": str,
        "DeviceId": str,
    },
)
_OptionalAssociateCustomerGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateCustomerGatewayRequestRequestTypeDef",
    {
        "LinkId": str,
    },
    total=False,
)


class AssociateCustomerGatewayRequestRequestTypeDef(
    _RequiredAssociateCustomerGatewayRequestRequestTypeDef,
    _OptionalAssociateCustomerGatewayRequestRequestTypeDef,
):
    pass


CustomerGatewayAssociationTypeDef = TypedDict(
    "CustomerGatewayAssociationTypeDef",
    {
        "CustomerGatewayArn": str,
        "GlobalNetworkId": str,
        "DeviceId": str,
        "LinkId": str,
        "State": CustomerGatewayAssociationStateType,
    },
    total=False,
)

AssociateLinkRequestRequestTypeDef = TypedDict(
    "AssociateLinkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "DeviceId": str,
        "LinkId": str,
    },
)

LinkAssociationTypeDef = TypedDict(
    "LinkAssociationTypeDef",
    {
        "GlobalNetworkId": str,
        "DeviceId": str,
        "LinkId": str,
        "LinkAssociationState": LinkAssociationStateType,
    },
    total=False,
)

_RequiredAssociateTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "TransitGatewayConnectPeerArn": str,
        "DeviceId": str,
    },
)
_OptionalAssociateTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "LinkId": str,
    },
    total=False,
)


class AssociateTransitGatewayConnectPeerRequestRequestTypeDef(
    _RequiredAssociateTransitGatewayConnectPeerRequestRequestTypeDef,
    _OptionalAssociateTransitGatewayConnectPeerRequestRequestTypeDef,
):
    pass


TransitGatewayConnectPeerAssociationTypeDef = TypedDict(
    "TransitGatewayConnectPeerAssociationTypeDef",
    {
        "TransitGatewayConnectPeerArn": str,
        "GlobalNetworkId": str,
        "DeviceId": str,
        "LinkId": str,
        "State": TransitGatewayConnectPeerAssociationStateType,
    },
    total=False,
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
    total=False,
)

BandwidthTypeDef = TypedDict(
    "BandwidthTypeDef",
    {
        "UploadSpeed": int,
        "DownloadSpeed": int,
    },
    total=False,
)

BgpOptionsTypeDef = TypedDict(
    "BgpOptionsTypeDef",
    {
        "PeerAsn": int,
    },
    total=False,
)

ConnectAttachmentOptionsTypeDef = TypedDict(
    "ConnectAttachmentOptionsTypeDef",
    {
        "Protocol": Literal["GRE"],
    },
    total=False,
)

ConnectPeerBgpConfigurationTypeDef = TypedDict(
    "ConnectPeerBgpConfigurationTypeDef",
    {
        "CoreNetworkAsn": int,
        "PeerAsn": int,
        "CoreNetworkAddress": str,
        "PeerAddress": str,
    },
    total=False,
)

ConnectionHealthTypeDef = TypedDict(
    "ConnectionHealthTypeDef",
    {
        "Type": ConnectionTypeType,
        "Status": ConnectionStatusType,
        "Timestamp": datetime,
    },
    total=False,
)

CoreNetworkChangeValuesTypeDef = TypedDict(
    "CoreNetworkChangeValuesTypeDef",
    {
        "SegmentName": str,
        "EdgeLocations": List[str],
        "Asn": int,
        "Cidr": str,
        "DestinationIdentifier": str,
        "InsideCidrBlocks": List[str],
        "SharedSegments": List[str],
    },
    total=False,
)

CoreNetworkEdgeTypeDef = TypedDict(
    "CoreNetworkEdgeTypeDef",
    {
        "EdgeLocation": str,
        "Asn": int,
        "InsideCidrBlocks": List[str],
    },
    total=False,
)

_RequiredCoreNetworkPolicyErrorTypeDef = TypedDict(
    "_RequiredCoreNetworkPolicyErrorTypeDef",
    {
        "ErrorCode": str,
        "Message": str,
    },
)
_OptionalCoreNetworkPolicyErrorTypeDef = TypedDict(
    "_OptionalCoreNetworkPolicyErrorTypeDef",
    {
        "Path": str,
    },
    total=False,
)


class CoreNetworkPolicyErrorTypeDef(
    _RequiredCoreNetworkPolicyErrorTypeDef, _OptionalCoreNetworkPolicyErrorTypeDef
):
    pass


CoreNetworkPolicyVersionTypeDef = TypedDict(
    "CoreNetworkPolicyVersionTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
        "Alias": CoreNetworkPolicyAliasType,
        "Description": str,
        "CreatedAt": datetime,
        "ChangeSetState": ChangeSetStateType,
    },
    total=False,
)

CoreNetworkSegmentEdgeIdentifierTypeDef = TypedDict(
    "CoreNetworkSegmentEdgeIdentifierTypeDef",
    {
        "CoreNetworkId": str,
        "SegmentName": str,
        "EdgeLocation": str,
    },
    total=False,
)

CoreNetworkSegmentTypeDef = TypedDict(
    "CoreNetworkSegmentTypeDef",
    {
        "Name": str,
        "EdgeLocations": List[str],
        "SharedSegments": List[str],
    },
    total=False,
)

LocationTypeDef = TypedDict(
    "LocationTypeDef",
    {
        "Address": str,
        "Latitude": str,
        "Longitude": str,
    },
    total=False,
)

VpcOptionsTypeDef = TypedDict(
    "VpcOptionsTypeDef",
    {
        "Ipv6Support": bool,
    },
    total=False,
)

DeleteAttachmentRequestRequestTypeDef = TypedDict(
    "DeleteAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)

DeleteConnectPeerRequestRequestTypeDef = TypedDict(
    "DeleteConnectPeerRequestRequestTypeDef",
    {
        "ConnectPeerId": str,
    },
)

DeleteConnectionRequestRequestTypeDef = TypedDict(
    "DeleteConnectionRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "ConnectionId": str,
    },
)

DeleteCoreNetworkPolicyVersionRequestRequestTypeDef = TypedDict(
    "DeleteCoreNetworkPolicyVersionRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
    },
)

DeleteCoreNetworkRequestRequestTypeDef = TypedDict(
    "DeleteCoreNetworkRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
    },
)

DeleteDeviceRequestRequestTypeDef = TypedDict(
    "DeleteDeviceRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "DeviceId": str,
    },
)

DeleteGlobalNetworkRequestRequestTypeDef = TypedDict(
    "DeleteGlobalNetworkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)

DeleteLinkRequestRequestTypeDef = TypedDict(
    "DeleteLinkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "LinkId": str,
    },
)

DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

DeleteSiteRequestRequestTypeDef = TypedDict(
    "DeleteSiteRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "SiteId": str,
    },
)

DeregisterTransitGatewayRequestRequestTypeDef = TypedDict(
    "DeregisterTransitGatewayRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "TransitGatewayArn": str,
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

DescribeGlobalNetworksRequestRequestTypeDef = TypedDict(
    "DescribeGlobalNetworksRequestRequestTypeDef",
    {
        "GlobalNetworkIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DisassociateConnectPeerRequestRequestTypeDef = TypedDict(
    "DisassociateConnectPeerRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "ConnectPeerId": str,
    },
)

DisassociateCustomerGatewayRequestRequestTypeDef = TypedDict(
    "DisassociateCustomerGatewayRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "CustomerGatewayArn": str,
    },
)

DisassociateLinkRequestRequestTypeDef = TypedDict(
    "DisassociateLinkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "DeviceId": str,
        "LinkId": str,
    },
)

DisassociateTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "DisassociateTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "TransitGatewayConnectPeerArn": str,
    },
)

ExecuteCoreNetworkChangeSetRequestRequestTypeDef = TypedDict(
    "ExecuteCoreNetworkChangeSetRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
    },
)

GetConnectAttachmentRequestRequestTypeDef = TypedDict(
    "GetConnectAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)

_RequiredGetConnectPeerAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetConnectPeerAssociationsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetConnectPeerAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetConnectPeerAssociationsRequestRequestTypeDef",
    {
        "ConnectPeerIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetConnectPeerAssociationsRequestRequestTypeDef(
    _RequiredGetConnectPeerAssociationsRequestRequestTypeDef,
    _OptionalGetConnectPeerAssociationsRequestRequestTypeDef,
):
    pass


GetConnectPeerRequestRequestTypeDef = TypedDict(
    "GetConnectPeerRequestRequestTypeDef",
    {
        "ConnectPeerId": str,
    },
)

_RequiredGetConnectionsRequestRequestTypeDef = TypedDict(
    "_RequiredGetConnectionsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetConnectionsRequestRequestTypeDef = TypedDict(
    "_OptionalGetConnectionsRequestRequestTypeDef",
    {
        "ConnectionIds": Sequence[str],
        "DeviceId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetConnectionsRequestRequestTypeDef(
    _RequiredGetConnectionsRequestRequestTypeDef, _OptionalGetConnectionsRequestRequestTypeDef
):
    pass


_RequiredGetCoreNetworkChangeSetRequestRequestTypeDef = TypedDict(
    "_RequiredGetCoreNetworkChangeSetRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
    },
)
_OptionalGetCoreNetworkChangeSetRequestRequestTypeDef = TypedDict(
    "_OptionalGetCoreNetworkChangeSetRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetCoreNetworkChangeSetRequestRequestTypeDef(
    _RequiredGetCoreNetworkChangeSetRequestRequestTypeDef,
    _OptionalGetCoreNetworkChangeSetRequestRequestTypeDef,
):
    pass


_RequiredGetCoreNetworkPolicyRequestRequestTypeDef = TypedDict(
    "_RequiredGetCoreNetworkPolicyRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
    },
)
_OptionalGetCoreNetworkPolicyRequestRequestTypeDef = TypedDict(
    "_OptionalGetCoreNetworkPolicyRequestRequestTypeDef",
    {
        "PolicyVersionId": int,
        "Alias": CoreNetworkPolicyAliasType,
    },
    total=False,
)


class GetCoreNetworkPolicyRequestRequestTypeDef(
    _RequiredGetCoreNetworkPolicyRequestRequestTypeDef,
    _OptionalGetCoreNetworkPolicyRequestRequestTypeDef,
):
    pass


GetCoreNetworkRequestRequestTypeDef = TypedDict(
    "GetCoreNetworkRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
    },
)

_RequiredGetCustomerGatewayAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetCustomerGatewayAssociationsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetCustomerGatewayAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetCustomerGatewayAssociationsRequestRequestTypeDef",
    {
        "CustomerGatewayArns": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetCustomerGatewayAssociationsRequestRequestTypeDef(
    _RequiredGetCustomerGatewayAssociationsRequestRequestTypeDef,
    _OptionalGetCustomerGatewayAssociationsRequestRequestTypeDef,
):
    pass


_RequiredGetDevicesRequestRequestTypeDef = TypedDict(
    "_RequiredGetDevicesRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetDevicesRequestRequestTypeDef = TypedDict(
    "_OptionalGetDevicesRequestRequestTypeDef",
    {
        "DeviceIds": Sequence[str],
        "SiteId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetDevicesRequestRequestTypeDef(
    _RequiredGetDevicesRequestRequestTypeDef, _OptionalGetDevicesRequestRequestTypeDef
):
    pass


_RequiredGetLinkAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetLinkAssociationsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetLinkAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetLinkAssociationsRequestRequestTypeDef",
    {
        "DeviceId": str,
        "LinkId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetLinkAssociationsRequestRequestTypeDef(
    _RequiredGetLinkAssociationsRequestRequestTypeDef,
    _OptionalGetLinkAssociationsRequestRequestTypeDef,
):
    pass


_RequiredGetLinksRequestRequestTypeDef = TypedDict(
    "_RequiredGetLinksRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetLinksRequestRequestTypeDef = TypedDict(
    "_OptionalGetLinksRequestRequestTypeDef",
    {
        "LinkIds": Sequence[str],
        "SiteId": str,
        "Type": str,
        "Provider": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetLinksRequestRequestTypeDef(
    _RequiredGetLinksRequestRequestTypeDef, _OptionalGetLinksRequestRequestTypeDef
):
    pass


_RequiredGetNetworkResourceCountsRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkResourceCountsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkResourceCountsRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkResourceCountsRequestRequestTypeDef",
    {
        "ResourceType": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetNetworkResourceCountsRequestRequestTypeDef(
    _RequiredGetNetworkResourceCountsRequestRequestTypeDef,
    _OptionalGetNetworkResourceCountsRequestRequestTypeDef,
):
    pass


NetworkResourceCountTypeDef = TypedDict(
    "NetworkResourceCountTypeDef",
    {
        "ResourceType": str,
        "Count": int,
    },
    total=False,
)

_RequiredGetNetworkResourceRelationshipsRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkResourceRelationshipsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkResourceRelationshipsRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkResourceRelationshipsRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "RegisteredGatewayArn": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceArn": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetNetworkResourceRelationshipsRequestRequestTypeDef(
    _RequiredGetNetworkResourceRelationshipsRequestRequestTypeDef,
    _OptionalGetNetworkResourceRelationshipsRequestRequestTypeDef,
):
    pass


RelationshipTypeDef = TypedDict(
    "RelationshipTypeDef",
    {
        "From": str,
        "To": str,
    },
    total=False,
)

_RequiredGetNetworkResourcesRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkResourcesRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkResourcesRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkResourcesRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "RegisteredGatewayArn": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceArn": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetNetworkResourcesRequestRequestTypeDef(
    _RequiredGetNetworkResourcesRequestRequestTypeDef,
    _OptionalGetNetworkResourcesRequestRequestTypeDef,
):
    pass


_RequiredGetNetworkTelemetryRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkTelemetryRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkTelemetryRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkTelemetryRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "RegisteredGatewayArn": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceArn": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetNetworkTelemetryRequestRequestTypeDef(
    _RequiredGetNetworkTelemetryRequestRequestTypeDef,
    _OptionalGetNetworkTelemetryRequestRequestTypeDef,
):
    pass


GetResourcePolicyRequestRequestTypeDef = TypedDict(
    "GetResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

GetRouteAnalysisRequestRequestTypeDef = TypedDict(
    "GetRouteAnalysisRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "RouteAnalysisId": str,
    },
)

GetSiteToSiteVpnAttachmentRequestRequestTypeDef = TypedDict(
    "GetSiteToSiteVpnAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)

_RequiredGetSitesRequestRequestTypeDef = TypedDict(
    "_RequiredGetSitesRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetSitesRequestRequestTypeDef = TypedDict(
    "_OptionalGetSitesRequestRequestTypeDef",
    {
        "SiteIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetSitesRequestRequestTypeDef(
    _RequiredGetSitesRequestRequestTypeDef, _OptionalGetSitesRequestRequestTypeDef
):
    pass


_RequiredGetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef",
    {
        "TransitGatewayConnectPeerArns": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef(
    _RequiredGetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef,
    _OptionalGetTransitGatewayConnectPeerAssociationsRequestRequestTypeDef,
):
    pass


_RequiredGetTransitGatewayRegistrationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetTransitGatewayRegistrationsRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetTransitGatewayRegistrationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetTransitGatewayRegistrationsRequestRequestTypeDef",
    {
        "TransitGatewayArns": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetTransitGatewayRegistrationsRequestRequestTypeDef(
    _RequiredGetTransitGatewayRegistrationsRequestRequestTypeDef,
    _OptionalGetTransitGatewayRegistrationsRequestRequestTypeDef,
):
    pass


GetVpcAttachmentRequestRequestTypeDef = TypedDict(
    "GetVpcAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)

ListAttachmentsRequestRequestTypeDef = TypedDict(
    "ListAttachmentsRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "AttachmentType": AttachmentTypeType,
        "EdgeLocation": str,
        "State": AttachmentStateType,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListConnectPeersRequestRequestTypeDef = TypedDict(
    "ListConnectPeersRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "ConnectAttachmentId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

_RequiredListCoreNetworkPolicyVersionsRequestRequestTypeDef = TypedDict(
    "_RequiredListCoreNetworkPolicyVersionsRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
    },
)
_OptionalListCoreNetworkPolicyVersionsRequestRequestTypeDef = TypedDict(
    "_OptionalListCoreNetworkPolicyVersionsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListCoreNetworkPolicyVersionsRequestRequestTypeDef(
    _RequiredListCoreNetworkPolicyVersionsRequestRequestTypeDef,
    _OptionalListCoreNetworkPolicyVersionsRequestRequestTypeDef,
):
    pass


ListCoreNetworksRequestRequestTypeDef = TypedDict(
    "ListCoreNetworksRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListOrganizationServiceAccessStatusRequestRequestTypeDef = TypedDict(
    "ListOrganizationServiceAccessStatusRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

NetworkResourceSummaryTypeDef = TypedDict(
    "NetworkResourceSummaryTypeDef",
    {
        "RegisteredGatewayArn": str,
        "ResourceArn": str,
        "ResourceType": str,
        "Definition": str,
        "NameTag": str,
        "IsMiddlebox": bool,
    },
    total=False,
)

NetworkRouteDestinationTypeDef = TypedDict(
    "NetworkRouteDestinationTypeDef",
    {
        "CoreNetworkAttachmentId": str,
        "TransitGatewayAttachmentId": str,
        "SegmentName": str,
        "EdgeLocation": str,
        "ResourceType": str,
        "ResourceId": str,
    },
    total=False,
)

_RequiredPutCoreNetworkPolicyRequestRequestTypeDef = TypedDict(
    "_RequiredPutCoreNetworkPolicyRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyDocument": str,
    },
)
_OptionalPutCoreNetworkPolicyRequestRequestTypeDef = TypedDict(
    "_OptionalPutCoreNetworkPolicyRequestRequestTypeDef",
    {
        "Description": str,
        "LatestVersionId": int,
        "ClientToken": str,
    },
    total=False,
)


class PutCoreNetworkPolicyRequestRequestTypeDef(
    _RequiredPutCoreNetworkPolicyRequestRequestTypeDef,
    _OptionalPutCoreNetworkPolicyRequestRequestTypeDef,
):
    pass


PutResourcePolicyRequestRequestTypeDef = TypedDict(
    "PutResourcePolicyRequestRequestTypeDef",
    {
        "PolicyDocument": str,
        "ResourceArn": str,
    },
)

RegisterTransitGatewayRequestRequestTypeDef = TypedDict(
    "RegisterTransitGatewayRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "TransitGatewayArn": str,
    },
)

RejectAttachmentRequestRequestTypeDef = TypedDict(
    "RejectAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)

RestoreCoreNetworkPolicyVersionRequestRequestTypeDef = TypedDict(
    "RestoreCoreNetworkPolicyVersionRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
    },
)

RouteAnalysisCompletionTypeDef = TypedDict(
    "RouteAnalysisCompletionTypeDef",
    {
        "ResultCode": RouteAnalysisCompletionResultCodeType,
        "ReasonCode": RouteAnalysisCompletionReasonCodeType,
        "ReasonContext": Dict[str, str],
    },
    total=False,
)

RouteAnalysisEndpointOptionsSpecificationTypeDef = TypedDict(
    "RouteAnalysisEndpointOptionsSpecificationTypeDef",
    {
        "TransitGatewayAttachmentArn": str,
        "IpAddress": str,
    },
    total=False,
)

RouteAnalysisEndpointOptionsTypeDef = TypedDict(
    "RouteAnalysisEndpointOptionsTypeDef",
    {
        "TransitGatewayAttachmentArn": str,
        "TransitGatewayArn": str,
        "IpAddress": str,
    },
    total=False,
)

StartOrganizationServiceAccessUpdateRequestRequestTypeDef = TypedDict(
    "StartOrganizationServiceAccessUpdateRequestRequestTypeDef",
    {
        "Action": str,
    },
)

TransitGatewayRegistrationStateReasonTypeDef = TypedDict(
    "TransitGatewayRegistrationStateReasonTypeDef",
    {
        "Code": TransitGatewayRegistrationStateType,
        "Message": str,
    },
    total=False,
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

_RequiredUpdateConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateConnectionRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "ConnectionId": str,
    },
)
_OptionalUpdateConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateConnectionRequestRequestTypeDef",
    {
        "LinkId": str,
        "ConnectedLinkId": str,
        "Description": str,
    },
    total=False,
)


class UpdateConnectionRequestRequestTypeDef(
    _RequiredUpdateConnectionRequestRequestTypeDef, _OptionalUpdateConnectionRequestRequestTypeDef
):
    pass


_RequiredUpdateCoreNetworkRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateCoreNetworkRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
    },
)
_OptionalUpdateCoreNetworkRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateCoreNetworkRequestRequestTypeDef",
    {
        "Description": str,
    },
    total=False,
)


class UpdateCoreNetworkRequestRequestTypeDef(
    _RequiredUpdateCoreNetworkRequestRequestTypeDef, _OptionalUpdateCoreNetworkRequestRequestTypeDef
):
    pass


_RequiredUpdateGlobalNetworkRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateGlobalNetworkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalUpdateGlobalNetworkRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateGlobalNetworkRequestRequestTypeDef",
    {
        "Description": str,
    },
    total=False,
)


class UpdateGlobalNetworkRequestRequestTypeDef(
    _RequiredUpdateGlobalNetworkRequestRequestTypeDef,
    _OptionalUpdateGlobalNetworkRequestRequestTypeDef,
):
    pass


UpdateNetworkResourceMetadataRequestRequestTypeDef = TypedDict(
    "UpdateNetworkResourceMetadataRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "ResourceArn": str,
        "Metadata": Mapping[str, str],
    },
)

GetResourcePolicyResponseTypeDef = TypedDict(
    "GetResourcePolicyResponseTypeDef",
    {
        "PolicyDocument": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateNetworkResourceMetadataResponseTypeDef = TypedDict(
    "UpdateNetworkResourceMetadataResponseTypeDef",
    {
        "ResourceArn": str,
        "Metadata": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

OrganizationStatusTypeDef = TypedDict(
    "OrganizationStatusTypeDef",
    {
        "OrganizationId": str,
        "OrganizationAwsServiceAccessStatus": str,
        "SLRDeploymentStatus": str,
        "AccountStatusList": List[AccountStatusTypeDef],
    },
    total=False,
)

AssociateConnectPeerResponseTypeDef = TypedDict(
    "AssociateConnectPeerResponseTypeDef",
    {
        "ConnectPeerAssociation": ConnectPeerAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateConnectPeerResponseTypeDef = TypedDict(
    "DisassociateConnectPeerResponseTypeDef",
    {
        "ConnectPeerAssociation": ConnectPeerAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetConnectPeerAssociationsResponseTypeDef = TypedDict(
    "GetConnectPeerAssociationsResponseTypeDef",
    {
        "ConnectPeerAssociations": List[ConnectPeerAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateCustomerGatewayResponseTypeDef = TypedDict(
    "AssociateCustomerGatewayResponseTypeDef",
    {
        "CustomerGatewayAssociation": CustomerGatewayAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateCustomerGatewayResponseTypeDef = TypedDict(
    "DisassociateCustomerGatewayResponseTypeDef",
    {
        "CustomerGatewayAssociation": CustomerGatewayAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCustomerGatewayAssociationsResponseTypeDef = TypedDict(
    "GetCustomerGatewayAssociationsResponseTypeDef",
    {
        "CustomerGatewayAssociations": List[CustomerGatewayAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateLinkResponseTypeDef = TypedDict(
    "AssociateLinkResponseTypeDef",
    {
        "LinkAssociation": LinkAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateLinkResponseTypeDef = TypedDict(
    "DisassociateLinkResponseTypeDef",
    {
        "LinkAssociation": LinkAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLinkAssociationsResponseTypeDef = TypedDict(
    "GetLinkAssociationsResponseTypeDef",
    {
        "LinkAssociations": List[LinkAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateTransitGatewayConnectPeerResponseTypeDef = TypedDict(
    "AssociateTransitGatewayConnectPeerResponseTypeDef",
    {
        "TransitGatewayConnectPeerAssociation": TransitGatewayConnectPeerAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateTransitGatewayConnectPeerResponseTypeDef = TypedDict(
    "DisassociateTransitGatewayConnectPeerResponseTypeDef",
    {
        "TransitGatewayConnectPeerAssociation": TransitGatewayConnectPeerAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayConnectPeerAssociationsResponseTypeDef = TypedDict(
    "GetTransitGatewayConnectPeerAssociationsResponseTypeDef",
    {
        "TransitGatewayConnectPeerAssociations": List[TransitGatewayConnectPeerAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ConnectPeerSummaryTypeDef = TypedDict(
    "ConnectPeerSummaryTypeDef",
    {
        "CoreNetworkId": str,
        "ConnectAttachmentId": str,
        "ConnectPeerId": str,
        "EdgeLocation": str,
        "ConnectPeerState": ConnectPeerStateType,
        "CreatedAt": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ConnectionTypeDef = TypedDict(
    "ConnectionTypeDef",
    {
        "ConnectionId": str,
        "ConnectionArn": str,
        "GlobalNetworkId": str,
        "DeviceId": str,
        "ConnectedDeviceId": str,
        "LinkId": str,
        "ConnectedLinkId": str,
        "Description": str,
        "CreatedAt": datetime,
        "State": ConnectionStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

CoreNetworkSummaryTypeDef = TypedDict(
    "CoreNetworkSummaryTypeDef",
    {
        "CoreNetworkId": str,
        "CoreNetworkArn": str,
        "GlobalNetworkId": str,
        "OwnerAccountId": str,
        "State": CoreNetworkStateType,
        "Description": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredCreateConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateConnectionRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "DeviceId": str,
        "ConnectedDeviceId": str,
    },
)
_OptionalCreateConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateConnectionRequestRequestTypeDef",
    {
        "LinkId": str,
        "ConnectedLinkId": str,
        "Description": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateConnectionRequestRequestTypeDef(
    _RequiredCreateConnectionRequestRequestTypeDef, _OptionalCreateConnectionRequestRequestTypeDef
):
    pass


_RequiredCreateCoreNetworkRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCoreNetworkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalCreateCoreNetworkRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCoreNetworkRequestRequestTypeDef",
    {
        "Description": str,
        "Tags": Sequence[TagTypeDef],
        "PolicyDocument": str,
        "ClientToken": str,
    },
    total=False,
)


class CreateCoreNetworkRequestRequestTypeDef(
    _RequiredCreateCoreNetworkRequestRequestTypeDef, _OptionalCreateCoreNetworkRequestRequestTypeDef
):
    pass


CreateGlobalNetworkRequestRequestTypeDef = TypedDict(
    "CreateGlobalNetworkRequestRequestTypeDef",
    {
        "Description": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)

_RequiredCreateSiteToSiteVpnAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSiteToSiteVpnAttachmentRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "VpnConnectionArn": str,
    },
)
_OptionalCreateSiteToSiteVpnAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSiteToSiteVpnAttachmentRequestRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateSiteToSiteVpnAttachmentRequestRequestTypeDef(
    _RequiredCreateSiteToSiteVpnAttachmentRequestRequestTypeDef,
    _OptionalCreateSiteToSiteVpnAttachmentRequestRequestTypeDef,
):
    pass


GlobalNetworkTypeDef = TypedDict(
    "GlobalNetworkTypeDef",
    {
        "GlobalNetworkId": str,
        "GlobalNetworkArn": str,
        "Description": str,
        "CreatedAt": datetime,
        "State": GlobalNetworkStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "TagList": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkResourceTypeDef = TypedDict(
    "NetworkResourceTypeDef",
    {
        "RegisteredGatewayArn": str,
        "CoreNetworkId": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceId": str,
        "ResourceArn": str,
        "Definition": str,
        "DefinitionTimestamp": datetime,
        "Tags": List[TagTypeDef],
        "Metadata": Dict[str, str],
    },
    total=False,
)

ProposedSegmentChangeTypeDef = TypedDict(
    "ProposedSegmentChangeTypeDef",
    {
        "Tags": List[TagTypeDef],
        "AttachmentPolicyRuleNumber": int,
        "SegmentName": str,
    },
    total=False,
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

_RequiredCreateLinkRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLinkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "Bandwidth": BandwidthTypeDef,
        "SiteId": str,
    },
)
_OptionalCreateLinkRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLinkRequestRequestTypeDef",
    {
        "Description": str,
        "Type": str,
        "Provider": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateLinkRequestRequestTypeDef(
    _RequiredCreateLinkRequestRequestTypeDef, _OptionalCreateLinkRequestRequestTypeDef
):
    pass


LinkTypeDef = TypedDict(
    "LinkTypeDef",
    {
        "LinkId": str,
        "LinkArn": str,
        "GlobalNetworkId": str,
        "SiteId": str,
        "Description": str,
        "Type": str,
        "Bandwidth": BandwidthTypeDef,
        "Provider": str,
        "CreatedAt": datetime,
        "State": LinkStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredUpdateLinkRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateLinkRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "LinkId": str,
    },
)
_OptionalUpdateLinkRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateLinkRequestRequestTypeDef",
    {
        "Description": str,
        "Type": str,
        "Bandwidth": BandwidthTypeDef,
        "Provider": str,
    },
    total=False,
)


class UpdateLinkRequestRequestTypeDef(
    _RequiredUpdateLinkRequestRequestTypeDef, _OptionalUpdateLinkRequestRequestTypeDef
):
    pass


_RequiredCreateConnectPeerRequestRequestTypeDef = TypedDict(
    "_RequiredCreateConnectPeerRequestRequestTypeDef",
    {
        "ConnectAttachmentId": str,
        "PeerAddress": str,
        "InsideCidrBlocks": Sequence[str],
    },
)
_OptionalCreateConnectPeerRequestRequestTypeDef = TypedDict(
    "_OptionalCreateConnectPeerRequestRequestTypeDef",
    {
        "CoreNetworkAddress": str,
        "BgpOptions": BgpOptionsTypeDef,
        "Tags": Sequence[TagTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateConnectPeerRequestRequestTypeDef(
    _RequiredCreateConnectPeerRequestRequestTypeDef, _OptionalCreateConnectPeerRequestRequestTypeDef
):
    pass


_RequiredCreateConnectAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateConnectAttachmentRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "EdgeLocation": str,
        "TransportAttachmentId": str,
        "Options": ConnectAttachmentOptionsTypeDef,
    },
)
_OptionalCreateConnectAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateConnectAttachmentRequestRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateConnectAttachmentRequestRequestTypeDef(
    _RequiredCreateConnectAttachmentRequestRequestTypeDef,
    _OptionalCreateConnectAttachmentRequestRequestTypeDef,
):
    pass


ConnectPeerConfigurationTypeDef = TypedDict(
    "ConnectPeerConfigurationTypeDef",
    {
        "CoreNetworkAddress": str,
        "PeerAddress": str,
        "InsideCidrBlocks": List[str],
        "Protocol": Literal["GRE"],
        "BgpConfigurations": List[ConnectPeerBgpConfigurationTypeDef],
    },
    total=False,
)

NetworkTelemetryTypeDef = TypedDict(
    "NetworkTelemetryTypeDef",
    {
        "RegisteredGatewayArn": str,
        "CoreNetworkId": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceId": str,
        "ResourceArn": str,
        "Address": str,
        "Health": ConnectionHealthTypeDef,
    },
    total=False,
)

CoreNetworkChangeTypeDef = TypedDict(
    "CoreNetworkChangeTypeDef",
    {
        "Type": ChangeTypeType,
        "Action": ChangeActionType,
        "Identifier": str,
        "PreviousValues": CoreNetworkChangeValuesTypeDef,
        "NewValues": CoreNetworkChangeValuesTypeDef,
    },
    total=False,
)

CoreNetworkPolicyTypeDef = TypedDict(
    "CoreNetworkPolicyTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
        "Alias": CoreNetworkPolicyAliasType,
        "Description": str,
        "CreatedAt": datetime,
        "ChangeSetState": ChangeSetStateType,
        "PolicyErrors": List[CoreNetworkPolicyErrorTypeDef],
        "PolicyDocument": str,
    },
    total=False,
)

ListCoreNetworkPolicyVersionsResponseTypeDef = TypedDict(
    "ListCoreNetworkPolicyVersionsResponseTypeDef",
    {
        "CoreNetworkPolicyVersions": List[CoreNetworkPolicyVersionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RouteTableIdentifierTypeDef = TypedDict(
    "RouteTableIdentifierTypeDef",
    {
        "TransitGatewayRouteTableArn": str,
        "CoreNetworkSegmentEdge": CoreNetworkSegmentEdgeIdentifierTypeDef,
    },
    total=False,
)

CoreNetworkTypeDef = TypedDict(
    "CoreNetworkTypeDef",
    {
        "GlobalNetworkId": str,
        "CoreNetworkId": str,
        "CoreNetworkArn": str,
        "Description": str,
        "CreatedAt": datetime,
        "State": CoreNetworkStateType,
        "Segments": List[CoreNetworkSegmentTypeDef],
        "Edges": List[CoreNetworkEdgeTypeDef],
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredCreateDeviceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDeviceRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalCreateDeviceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDeviceRequestRequestTypeDef",
    {
        "AWSLocation": AWSLocationTypeDef,
        "Description": str,
        "Type": str,
        "Vendor": str,
        "Model": str,
        "SerialNumber": str,
        "Location": LocationTypeDef,
        "SiteId": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDeviceRequestRequestTypeDef(
    _RequiredCreateDeviceRequestRequestTypeDef, _OptionalCreateDeviceRequestRequestTypeDef
):
    pass


_RequiredCreateSiteRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSiteRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalCreateSiteRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSiteRequestRequestTypeDef",
    {
        "Description": str,
        "Location": LocationTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateSiteRequestRequestTypeDef(
    _RequiredCreateSiteRequestRequestTypeDef, _OptionalCreateSiteRequestRequestTypeDef
):
    pass


DeviceTypeDef = TypedDict(
    "DeviceTypeDef",
    {
        "DeviceId": str,
        "DeviceArn": str,
        "GlobalNetworkId": str,
        "AWSLocation": AWSLocationTypeDef,
        "Description": str,
        "Type": str,
        "Vendor": str,
        "Model": str,
        "SerialNumber": str,
        "Location": LocationTypeDef,
        "SiteId": str,
        "CreatedAt": datetime,
        "State": DeviceStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

SiteTypeDef = TypedDict(
    "SiteTypeDef",
    {
        "SiteId": str,
        "SiteArn": str,
        "GlobalNetworkId": str,
        "Description": str,
        "Location": LocationTypeDef,
        "CreatedAt": datetime,
        "State": SiteStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredUpdateDeviceRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDeviceRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "DeviceId": str,
    },
)
_OptionalUpdateDeviceRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDeviceRequestRequestTypeDef",
    {
        "AWSLocation": AWSLocationTypeDef,
        "Description": str,
        "Type": str,
        "Vendor": str,
        "Model": str,
        "SerialNumber": str,
        "Location": LocationTypeDef,
        "SiteId": str,
    },
    total=False,
)


class UpdateDeviceRequestRequestTypeDef(
    _RequiredUpdateDeviceRequestRequestTypeDef, _OptionalUpdateDeviceRequestRequestTypeDef
):
    pass


_RequiredUpdateSiteRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateSiteRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "SiteId": str,
    },
)
_OptionalUpdateSiteRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateSiteRequestRequestTypeDef",
    {
        "Description": str,
        "Location": LocationTypeDef,
    },
    total=False,
)


class UpdateSiteRequestRequestTypeDef(
    _RequiredUpdateSiteRequestRequestTypeDef, _OptionalUpdateSiteRequestRequestTypeDef
):
    pass


_RequiredCreateVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpcAttachmentRequestRequestTypeDef",
    {
        "CoreNetworkId": str,
        "VpcArn": str,
        "SubnetArns": Sequence[str],
    },
)
_OptionalCreateVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpcAttachmentRequestRequestTypeDef",
    {
        "Options": VpcOptionsTypeDef,
        "Tags": Sequence[TagTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateVpcAttachmentRequestRequestTypeDef(
    _RequiredCreateVpcAttachmentRequestRequestTypeDef,
    _OptionalCreateVpcAttachmentRequestRequestTypeDef,
):
    pass


_RequiredUpdateVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateVpcAttachmentRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)
_OptionalUpdateVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateVpcAttachmentRequestRequestTypeDef",
    {
        "AddSubnetArns": Sequence[str],
        "RemoveSubnetArns": Sequence[str],
        "Options": VpcOptionsTypeDef,
    },
    total=False,
)


class UpdateVpcAttachmentRequestRequestTypeDef(
    _RequiredUpdateVpcAttachmentRequestRequestTypeDef,
    _OptionalUpdateVpcAttachmentRequestRequestTypeDef,
):
    pass


DescribeGlobalNetworksRequestDescribeGlobalNetworksPaginateTypeDef = TypedDict(
    "DescribeGlobalNetworksRequestDescribeGlobalNetworksPaginateTypeDef",
    {
        "GlobalNetworkIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredGetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef = TypedDict(
    "_RequiredGetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef = TypedDict(
    "_OptionalGetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef",
    {
        "ConnectPeerIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef(
    _RequiredGetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef,
    _OptionalGetConnectPeerAssociationsRequestGetConnectPeerAssociationsPaginateTypeDef,
):
    pass


_RequiredGetConnectionsRequestGetConnectionsPaginateTypeDef = TypedDict(
    "_RequiredGetConnectionsRequestGetConnectionsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetConnectionsRequestGetConnectionsPaginateTypeDef = TypedDict(
    "_OptionalGetConnectionsRequestGetConnectionsPaginateTypeDef",
    {
        "ConnectionIds": Sequence[str],
        "DeviceId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetConnectionsRequestGetConnectionsPaginateTypeDef(
    _RequiredGetConnectionsRequestGetConnectionsPaginateTypeDef,
    _OptionalGetConnectionsRequestGetConnectionsPaginateTypeDef,
):
    pass


_RequiredGetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef = TypedDict(
    "_RequiredGetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef",
    {
        "CoreNetworkId": str,
        "PolicyVersionId": int,
    },
)
_OptionalGetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef = TypedDict(
    "_OptionalGetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef(
    _RequiredGetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef,
    _OptionalGetCoreNetworkChangeSetRequestGetCoreNetworkChangeSetPaginateTypeDef,
):
    pass


_RequiredGetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef = TypedDict(
    "_RequiredGetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef = TypedDict(
    "_OptionalGetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef",
    {
        "CustomerGatewayArns": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef(
    _RequiredGetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef,
    _OptionalGetCustomerGatewayAssociationsRequestGetCustomerGatewayAssociationsPaginateTypeDef,
):
    pass


_RequiredGetDevicesRequestGetDevicesPaginateTypeDef = TypedDict(
    "_RequiredGetDevicesRequestGetDevicesPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetDevicesRequestGetDevicesPaginateTypeDef = TypedDict(
    "_OptionalGetDevicesRequestGetDevicesPaginateTypeDef",
    {
        "DeviceIds": Sequence[str],
        "SiteId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetDevicesRequestGetDevicesPaginateTypeDef(
    _RequiredGetDevicesRequestGetDevicesPaginateTypeDef,
    _OptionalGetDevicesRequestGetDevicesPaginateTypeDef,
):
    pass


_RequiredGetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef = TypedDict(
    "_RequiredGetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef = TypedDict(
    "_OptionalGetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef",
    {
        "DeviceId": str,
        "LinkId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef(
    _RequiredGetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef,
    _OptionalGetLinkAssociationsRequestGetLinkAssociationsPaginateTypeDef,
):
    pass


_RequiredGetLinksRequestGetLinksPaginateTypeDef = TypedDict(
    "_RequiredGetLinksRequestGetLinksPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetLinksRequestGetLinksPaginateTypeDef = TypedDict(
    "_OptionalGetLinksRequestGetLinksPaginateTypeDef",
    {
        "LinkIds": Sequence[str],
        "SiteId": str,
        "Type": str,
        "Provider": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetLinksRequestGetLinksPaginateTypeDef(
    _RequiredGetLinksRequestGetLinksPaginateTypeDef, _OptionalGetLinksRequestGetLinksPaginateTypeDef
):
    pass


_RequiredGetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef = TypedDict(
    "_RequiredGetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef = TypedDict(
    "_OptionalGetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef",
    {
        "ResourceType": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef(
    _RequiredGetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef,
    _OptionalGetNetworkResourceCountsRequestGetNetworkResourceCountsPaginateTypeDef,
):
    pass


_RequiredGetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef = TypedDict(
    "_RequiredGetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef = TypedDict(
    "_OptionalGetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef",
    {
        "CoreNetworkId": str,
        "RegisteredGatewayArn": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef(
    _RequiredGetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef,
    _OptionalGetNetworkResourceRelationshipsRequestGetNetworkResourceRelationshipsPaginateTypeDef,
):
    pass


_RequiredGetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef = TypedDict(
    "_RequiredGetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef = TypedDict(
    "_OptionalGetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef",
    {
        "CoreNetworkId": str,
        "RegisteredGatewayArn": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef(
    _RequiredGetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef,
    _OptionalGetNetworkResourcesRequestGetNetworkResourcesPaginateTypeDef,
):
    pass


_RequiredGetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef = TypedDict(
    "_RequiredGetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef = TypedDict(
    "_OptionalGetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef",
    {
        "CoreNetworkId": str,
        "RegisteredGatewayArn": str,
        "AwsRegion": str,
        "AccountId": str,
        "ResourceType": str,
        "ResourceArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef(
    _RequiredGetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef,
    _OptionalGetNetworkTelemetryRequestGetNetworkTelemetryPaginateTypeDef,
):
    pass


_RequiredGetSitesRequestGetSitesPaginateTypeDef = TypedDict(
    "_RequiredGetSitesRequestGetSitesPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetSitesRequestGetSitesPaginateTypeDef = TypedDict(
    "_OptionalGetSitesRequestGetSitesPaginateTypeDef",
    {
        "SiteIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetSitesRequestGetSitesPaginateTypeDef(
    _RequiredGetSitesRequestGetSitesPaginateTypeDef, _OptionalGetSitesRequestGetSitesPaginateTypeDef
):
    pass


_RequiredGetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef = TypedDict(
    "_RequiredGetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef = TypedDict(
    "_OptionalGetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef",
    {
        "TransitGatewayConnectPeerArns": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef(
    _RequiredGetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef,
    _OptionalGetTransitGatewayConnectPeerAssociationsRequestGetTransitGatewayConnectPeerAssociationsPaginateTypeDef,
):
    pass


_RequiredGetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef = TypedDict(
    "_RequiredGetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef",
    {
        "GlobalNetworkId": str,
    },
)
_OptionalGetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef = TypedDict(
    "_OptionalGetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef",
    {
        "TransitGatewayArns": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef(
    _RequiredGetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef,
    _OptionalGetTransitGatewayRegistrationsRequestGetTransitGatewayRegistrationsPaginateTypeDef,
):
    pass


ListAttachmentsRequestListAttachmentsPaginateTypeDef = TypedDict(
    "ListAttachmentsRequestListAttachmentsPaginateTypeDef",
    {
        "CoreNetworkId": str,
        "AttachmentType": AttachmentTypeType,
        "EdgeLocation": str,
        "State": AttachmentStateType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListConnectPeersRequestListConnectPeersPaginateTypeDef = TypedDict(
    "ListConnectPeersRequestListConnectPeersPaginateTypeDef",
    {
        "CoreNetworkId": str,
        "ConnectAttachmentId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef = (
    TypedDict(
        "_RequiredListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef",
        {
            "CoreNetworkId": str,
        },
    )
)
_OptionalListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef = (
    TypedDict(
        "_OptionalListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef",
        {
            "PaginationConfig": PaginatorConfigTypeDef,
        },
        total=False,
    )
)


class ListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef(
    _RequiredListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef,
    _OptionalListCoreNetworkPolicyVersionsRequestListCoreNetworkPolicyVersionsPaginateTypeDef,
):
    pass


ListCoreNetworksRequestListCoreNetworksPaginateTypeDef = TypedDict(
    "ListCoreNetworksRequestListCoreNetworksPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetNetworkResourceCountsResponseTypeDef = TypedDict(
    "GetNetworkResourceCountsResponseTypeDef",
    {
        "NetworkResourceCounts": List[NetworkResourceCountTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetNetworkResourceRelationshipsResponseTypeDef = TypedDict(
    "GetNetworkResourceRelationshipsResponseTypeDef",
    {
        "Relationships": List[RelationshipTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PathComponentTypeDef = TypedDict(
    "PathComponentTypeDef",
    {
        "Sequence": int,
        "Resource": NetworkResourceSummaryTypeDef,
        "DestinationCidrBlock": str,
    },
    total=False,
)

NetworkRouteTypeDef = TypedDict(
    "NetworkRouteTypeDef",
    {
        "DestinationCidrBlock": str,
        "Destinations": List[NetworkRouteDestinationTypeDef],
        "PrefixListId": str,
        "State": RouteStateType,
        "Type": RouteTypeType,
    },
    total=False,
)

_RequiredStartRouteAnalysisRequestRequestTypeDef = TypedDict(
    "_RequiredStartRouteAnalysisRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "Source": RouteAnalysisEndpointOptionsSpecificationTypeDef,
        "Destination": RouteAnalysisEndpointOptionsSpecificationTypeDef,
    },
)
_OptionalStartRouteAnalysisRequestRequestTypeDef = TypedDict(
    "_OptionalStartRouteAnalysisRequestRequestTypeDef",
    {
        "IncludeReturnPath": bool,
        "UseMiddleboxes": bool,
    },
    total=False,
)


class StartRouteAnalysisRequestRequestTypeDef(
    _RequiredStartRouteAnalysisRequestRequestTypeDef,
    _OptionalStartRouteAnalysisRequestRequestTypeDef,
):
    pass


TransitGatewayRegistrationTypeDef = TypedDict(
    "TransitGatewayRegistrationTypeDef",
    {
        "GlobalNetworkId": str,
        "TransitGatewayArn": str,
        "State": TransitGatewayRegistrationStateReasonTypeDef,
    },
    total=False,
)

ListOrganizationServiceAccessStatusResponseTypeDef = TypedDict(
    "ListOrganizationServiceAccessStatusResponseTypeDef",
    {
        "OrganizationStatus": OrganizationStatusTypeDef,
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartOrganizationServiceAccessUpdateResponseTypeDef = TypedDict(
    "StartOrganizationServiceAccessUpdateResponseTypeDef",
    {
        "OrganizationStatus": OrganizationStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListConnectPeersResponseTypeDef = TypedDict(
    "ListConnectPeersResponseTypeDef",
    {
        "ConnectPeers": List[ConnectPeerSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateConnectionResponseTypeDef = TypedDict(
    "CreateConnectionResponseTypeDef",
    {
        "Connection": ConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteConnectionResponseTypeDef = TypedDict(
    "DeleteConnectionResponseTypeDef",
    {
        "Connection": ConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetConnectionsResponseTypeDef = TypedDict(
    "GetConnectionsResponseTypeDef",
    {
        "Connections": List[ConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateConnectionResponseTypeDef = TypedDict(
    "UpdateConnectionResponseTypeDef",
    {
        "Connection": ConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListCoreNetworksResponseTypeDef = TypedDict(
    "ListCoreNetworksResponseTypeDef",
    {
        "CoreNetworks": List[CoreNetworkSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateGlobalNetworkResponseTypeDef = TypedDict(
    "CreateGlobalNetworkResponseTypeDef",
    {
        "GlobalNetwork": GlobalNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteGlobalNetworkResponseTypeDef = TypedDict(
    "DeleteGlobalNetworkResponseTypeDef",
    {
        "GlobalNetwork": GlobalNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeGlobalNetworksResponseTypeDef = TypedDict(
    "DescribeGlobalNetworksResponseTypeDef",
    {
        "GlobalNetworks": List[GlobalNetworkTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateGlobalNetworkResponseTypeDef = TypedDict(
    "UpdateGlobalNetworkResponseTypeDef",
    {
        "GlobalNetwork": GlobalNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetNetworkResourcesResponseTypeDef = TypedDict(
    "GetNetworkResourcesResponseTypeDef",
    {
        "NetworkResources": List[NetworkResourceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachmentTypeDef = TypedDict(
    "AttachmentTypeDef",
    {
        "CoreNetworkId": str,
        "CoreNetworkArn": str,
        "AttachmentId": str,
        "OwnerAccountId": str,
        "AttachmentType": AttachmentTypeType,
        "State": AttachmentStateType,
        "EdgeLocation": str,
        "ResourceArn": str,
        "AttachmentPolicyRuleNumber": int,
        "SegmentName": str,
        "Tags": List[TagTypeDef],
        "ProposedSegmentChange": ProposedSegmentChangeTypeDef,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
    },
    total=False,
)

CreateLinkResponseTypeDef = TypedDict(
    "CreateLinkResponseTypeDef",
    {
        "Link": LinkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLinkResponseTypeDef = TypedDict(
    "DeleteLinkResponseTypeDef",
    {
        "Link": LinkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLinksResponseTypeDef = TypedDict(
    "GetLinksResponseTypeDef",
    {
        "Links": List[LinkTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateLinkResponseTypeDef = TypedDict(
    "UpdateLinkResponseTypeDef",
    {
        "Link": LinkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ConnectPeerTypeDef = TypedDict(
    "ConnectPeerTypeDef",
    {
        "CoreNetworkId": str,
        "ConnectAttachmentId": str,
        "ConnectPeerId": str,
        "EdgeLocation": str,
        "State": ConnectPeerStateType,
        "CreatedAt": datetime,
        "Configuration": ConnectPeerConfigurationTypeDef,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

GetNetworkTelemetryResponseTypeDef = TypedDict(
    "GetNetworkTelemetryResponseTypeDef",
    {
        "NetworkTelemetry": List[NetworkTelemetryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCoreNetworkChangeSetResponseTypeDef = TypedDict(
    "GetCoreNetworkChangeSetResponseTypeDef",
    {
        "CoreNetworkChanges": List[CoreNetworkChangeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteCoreNetworkPolicyVersionResponseTypeDef = TypedDict(
    "DeleteCoreNetworkPolicyVersionResponseTypeDef",
    {
        "CoreNetworkPolicy": CoreNetworkPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCoreNetworkPolicyResponseTypeDef = TypedDict(
    "GetCoreNetworkPolicyResponseTypeDef",
    {
        "CoreNetworkPolicy": CoreNetworkPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutCoreNetworkPolicyResponseTypeDef = TypedDict(
    "PutCoreNetworkPolicyResponseTypeDef",
    {
        "CoreNetworkPolicy": CoreNetworkPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreCoreNetworkPolicyVersionResponseTypeDef = TypedDict(
    "RestoreCoreNetworkPolicyVersionResponseTypeDef",
    {
        "CoreNetworkPolicy": CoreNetworkPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredGetNetworkRoutesRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkRoutesRequestRequestTypeDef",
    {
        "GlobalNetworkId": str,
        "RouteTableIdentifier": RouteTableIdentifierTypeDef,
    },
)
_OptionalGetNetworkRoutesRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkRoutesRequestRequestTypeDef",
    {
        "ExactCidrMatches": Sequence[str],
        "LongestPrefixMatches": Sequence[str],
        "SubnetOfMatches": Sequence[str],
        "SupernetOfMatches": Sequence[str],
        "PrefixListIds": Sequence[str],
        "States": Sequence[RouteStateType],
        "Types": Sequence[RouteTypeType],
        "DestinationFilters": Mapping[str, Sequence[str]],
    },
    total=False,
)


class GetNetworkRoutesRequestRequestTypeDef(
    _RequiredGetNetworkRoutesRequestRequestTypeDef, _OptionalGetNetworkRoutesRequestRequestTypeDef
):
    pass


CreateCoreNetworkResponseTypeDef = TypedDict(
    "CreateCoreNetworkResponseTypeDef",
    {
        "CoreNetwork": CoreNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteCoreNetworkResponseTypeDef = TypedDict(
    "DeleteCoreNetworkResponseTypeDef",
    {
        "CoreNetwork": CoreNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCoreNetworkResponseTypeDef = TypedDict(
    "GetCoreNetworkResponseTypeDef",
    {
        "CoreNetwork": CoreNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateCoreNetworkResponseTypeDef = TypedDict(
    "UpdateCoreNetworkResponseTypeDef",
    {
        "CoreNetwork": CoreNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDeviceResponseTypeDef = TypedDict(
    "CreateDeviceResponseTypeDef",
    {
        "Device": DeviceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteDeviceResponseTypeDef = TypedDict(
    "DeleteDeviceResponseTypeDef",
    {
        "Device": DeviceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDevicesResponseTypeDef = TypedDict(
    "GetDevicesResponseTypeDef",
    {
        "Devices": List[DeviceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDeviceResponseTypeDef = TypedDict(
    "UpdateDeviceResponseTypeDef",
    {
        "Device": DeviceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSiteResponseTypeDef = TypedDict(
    "CreateSiteResponseTypeDef",
    {
        "Site": SiteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteSiteResponseTypeDef = TypedDict(
    "DeleteSiteResponseTypeDef",
    {
        "Site": SiteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSitesResponseTypeDef = TypedDict(
    "GetSitesResponseTypeDef",
    {
        "Sites": List[SiteTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateSiteResponseTypeDef = TypedDict(
    "UpdateSiteResponseTypeDef",
    {
        "Site": SiteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RouteAnalysisPathTypeDef = TypedDict(
    "RouteAnalysisPathTypeDef",
    {
        "CompletionStatus": RouteAnalysisCompletionTypeDef,
        "Path": List[PathComponentTypeDef],
    },
    total=False,
)

GetNetworkRoutesResponseTypeDef = TypedDict(
    "GetNetworkRoutesResponseTypeDef",
    {
        "RouteTableArn": str,
        "CoreNetworkSegmentEdge": CoreNetworkSegmentEdgeIdentifierTypeDef,
        "RouteTableType": RouteTableTypeType,
        "RouteTableTimestamp": datetime,
        "NetworkRoutes": List[NetworkRouteTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeregisterTransitGatewayResponseTypeDef = TypedDict(
    "DeregisterTransitGatewayResponseTypeDef",
    {
        "TransitGatewayRegistration": TransitGatewayRegistrationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayRegistrationsResponseTypeDef = TypedDict(
    "GetTransitGatewayRegistrationsResponseTypeDef",
    {
        "TransitGatewayRegistrations": List[TransitGatewayRegistrationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterTransitGatewayResponseTypeDef = TypedDict(
    "RegisterTransitGatewayResponseTypeDef",
    {
        "TransitGatewayRegistration": TransitGatewayRegistrationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AcceptAttachmentResponseTypeDef = TypedDict(
    "AcceptAttachmentResponseTypeDef",
    {
        "Attachment": AttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ConnectAttachmentTypeDef = TypedDict(
    "ConnectAttachmentTypeDef",
    {
        "Attachment": AttachmentTypeDef,
        "TransportAttachmentId": str,
        "Options": ConnectAttachmentOptionsTypeDef,
    },
    total=False,
)

DeleteAttachmentResponseTypeDef = TypedDict(
    "DeleteAttachmentResponseTypeDef",
    {
        "Attachment": AttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAttachmentsResponseTypeDef = TypedDict(
    "ListAttachmentsResponseTypeDef",
    {
        "Attachments": List[AttachmentTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RejectAttachmentResponseTypeDef = TypedDict(
    "RejectAttachmentResponseTypeDef",
    {
        "Attachment": AttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SiteToSiteVpnAttachmentTypeDef = TypedDict(
    "SiteToSiteVpnAttachmentTypeDef",
    {
        "Attachment": AttachmentTypeDef,
        "VpnConnectionArn": str,
    },
    total=False,
)

VpcAttachmentTypeDef = TypedDict(
    "VpcAttachmentTypeDef",
    {
        "Attachment": AttachmentTypeDef,
        "SubnetArns": List[str],
        "Options": VpcOptionsTypeDef,
    },
    total=False,
)

CreateConnectPeerResponseTypeDef = TypedDict(
    "CreateConnectPeerResponseTypeDef",
    {
        "ConnectPeer": ConnectPeerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteConnectPeerResponseTypeDef = TypedDict(
    "DeleteConnectPeerResponseTypeDef",
    {
        "ConnectPeer": ConnectPeerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetConnectPeerResponseTypeDef = TypedDict(
    "GetConnectPeerResponseTypeDef",
    {
        "ConnectPeer": ConnectPeerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RouteAnalysisTypeDef = TypedDict(
    "RouteAnalysisTypeDef",
    {
        "GlobalNetworkId": str,
        "OwnerAccountId": str,
        "RouteAnalysisId": str,
        "StartTimestamp": datetime,
        "Status": RouteAnalysisStatusType,
        "Source": RouteAnalysisEndpointOptionsTypeDef,
        "Destination": RouteAnalysisEndpointOptionsTypeDef,
        "IncludeReturnPath": bool,
        "UseMiddleboxes": bool,
        "ForwardPath": RouteAnalysisPathTypeDef,
        "ReturnPath": RouteAnalysisPathTypeDef,
    },
    total=False,
)

CreateConnectAttachmentResponseTypeDef = TypedDict(
    "CreateConnectAttachmentResponseTypeDef",
    {
        "ConnectAttachment": ConnectAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetConnectAttachmentResponseTypeDef = TypedDict(
    "GetConnectAttachmentResponseTypeDef",
    {
        "ConnectAttachment": ConnectAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSiteToSiteVpnAttachmentResponseTypeDef = TypedDict(
    "CreateSiteToSiteVpnAttachmentResponseTypeDef",
    {
        "SiteToSiteVpnAttachment": SiteToSiteVpnAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSiteToSiteVpnAttachmentResponseTypeDef = TypedDict(
    "GetSiteToSiteVpnAttachmentResponseTypeDef",
    {
        "SiteToSiteVpnAttachment": SiteToSiteVpnAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateVpcAttachmentResponseTypeDef = TypedDict(
    "CreateVpcAttachmentResponseTypeDef",
    {
        "VpcAttachment": VpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetVpcAttachmentResponseTypeDef = TypedDict(
    "GetVpcAttachmentResponseTypeDef",
    {
        "VpcAttachment": VpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateVpcAttachmentResponseTypeDef = TypedDict(
    "UpdateVpcAttachmentResponseTypeDef",
    {
        "VpcAttachment": VpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRouteAnalysisResponseTypeDef = TypedDict(
    "GetRouteAnalysisResponseTypeDef",
    {
        "RouteAnalysis": RouteAnalysisTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartRouteAnalysisResponseTypeDef = TypedDict(
    "StartRouteAnalysisResponseTypeDef",
    {
        "RouteAnalysis": RouteAnalysisTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
