"""
Type annotations for ec2 service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ec2/type_defs/)

Usage::

    ```python
    from mypy_boto3_ec2.type_defs import AcceleratorCountRequestTypeDef

    data: AcceleratorCountRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Optional, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AcceleratorManufacturerType,
    AcceleratorNameType,
    AcceleratorTypeType,
    AccountAttributeNameType,
    ActivityStatusType,
    AddressFamilyType,
    AffinityType,
    AllocationStateType,
    AllocationStrategyType,
    AllowsMultipleInstanceTypesType,
    AnalysisStatusType,
    ApplianceModeSupportValueType,
    ArchitectureTypeType,
    ArchitectureValuesType,
    AssociationStatusCodeType,
    AttachmentStatusType,
    AutoAcceptSharedAssociationsValueType,
    AutoAcceptSharedAttachmentsValueType,
    AutoPlacementType,
    AvailabilityZoneOptInStatusType,
    AvailabilityZoneStateType,
    BareMetalType,
    BatchStateType,
    BgpStatusType,
    BootModeTypeType,
    BootModeValuesType,
    BundleTaskStateType,
    BurstablePerformanceType,
    ByoipCidrStateType,
    CancelBatchErrorCodeType,
    CancelSpotInstanceRequestStateType,
    CapacityReservationFleetStateType,
    CapacityReservationInstancePlatformType,
    CapacityReservationPreferenceType,
    CapacityReservationStateType,
    CapacityReservationTenancyType,
    CarrierGatewayStateType,
    ClientCertificateRevocationListStatusCodeType,
    ClientVpnAuthenticationTypeType,
    ClientVpnAuthorizationRuleStatusCodeType,
    ClientVpnConnectionStatusCodeType,
    ClientVpnEndpointAttributeStatusCodeType,
    ClientVpnEndpointStatusCodeType,
    ClientVpnRouteStatusCodeType,
    ConnectionNotificationStateType,
    ConnectivityTypeType,
    ConversionTaskStateType,
    CpuManufacturerType,
    DatafeedSubscriptionStateType,
    DefaultRouteTableAssociationValueType,
    DefaultRouteTablePropagationValueType,
    DefaultTargetCapacityTypeType,
    DeleteFleetErrorCodeType,
    DeleteQueuedReservedInstancesErrorCodeType,
    DestinationFileFormatType,
    DeviceTypeType,
    DiskImageFormatType,
    DiskTypeType,
    DnsNameStateType,
    DnsRecordIpTypeType,
    DnsSupportValueType,
    DomainTypeType,
    EbsEncryptionSupportType,
    EbsNvmeSupportType,
    EbsOptimizedSupportType,
    ElasticGpuStatusType,
    EnaSupportType,
    EndDateTypeType,
    EphemeralNvmeSupportType,
    EventCodeType,
    EventTypeType,
    ExcessCapacityTerminationPolicyType,
    ExportEnvironmentType,
    ExportTaskStateType,
    FastLaunchStateCodeType,
    FastSnapshotRestoreStateCodeType,
    FindingsFoundType,
    FleetActivityStatusType,
    FleetEventTypeType,
    FleetExcessCapacityTerminationPolicyType,
    FleetOnDemandAllocationStrategyType,
    FleetReplacementStrategyType,
    FleetStateCodeType,
    FleetTypeType,
    FlowLogsResourceTypeType,
    FpgaImageAttributeNameType,
    FpgaImageStateCodeType,
    GatewayAssociationStateType,
    HostnameTypeType,
    HostRecoveryType,
    HostTenancyType,
    HttpTokensStateType,
    HypervisorTypeType,
    IamInstanceProfileAssociationStateType,
    Igmpv2SupportValueType,
    ImageAttributeNameType,
    ImageStateType,
    ImageTypeValuesType,
    InstanceAttributeNameType,
    InstanceAutoRecoveryStateType,
    InstanceEventWindowStateType,
    InstanceGenerationType,
    InstanceHealthStatusType,
    InstanceInterruptionBehaviorType,
    InstanceLifecycleType,
    InstanceLifecycleTypeType,
    InstanceMatchCriteriaType,
    InstanceMetadataEndpointStateType,
    InstanceMetadataOptionsStateType,
    InstanceMetadataProtocolStateType,
    InstanceMetadataTagsStateType,
    InstanceStateNameType,
    InstanceStorageEncryptionSupportType,
    InstanceTypeHypervisorType,
    InstanceTypeType,
    InterfacePermissionTypeType,
    InterfaceProtocolTypeType,
    IpAddressTypeType,
    IpamAddressHistoryResourceTypeType,
    IpamComplianceStatusType,
    IpamManagementStateType,
    IpamOverlapStatusType,
    IpamPoolAllocationResourceTypeType,
    IpamPoolCidrStateType,
    IpamPoolStateType,
    IpamResourceTypeType,
    IpamScopeStateType,
    IpamScopeTypeType,
    IpamStateType,
    Ipv6SupportValueType,
    KeyFormatType,
    KeyTypeType,
    LaunchTemplateAutoRecoveryStateType,
    LaunchTemplateErrorCodeType,
    LaunchTemplateHttpTokensStateType,
    LaunchTemplateInstanceMetadataEndpointStateType,
    LaunchTemplateInstanceMetadataOptionsStateType,
    LaunchTemplateInstanceMetadataProtocolIpv6Type,
    LaunchTemplateInstanceMetadataTagsStateType,
    ListingStateType,
    ListingStatusType,
    LocalGatewayRouteStateType,
    LocalGatewayRouteTypeType,
    LocalStorageType,
    LocalStorageTypeType,
    LocationTypeType,
    LogDestinationTypeType,
    MembershipTypeType,
    ModifyAvailabilityZoneOptInStatusType,
    MonitoringStateType,
    MoveStatusType,
    MulticastSupportValueType,
    NatGatewayStateType,
    NetworkInterfaceAttributeType,
    NetworkInterfaceCreationTypeType,
    NetworkInterfacePermissionStateCodeType,
    NetworkInterfaceStatusType,
    NetworkInterfaceTypeType,
    OfferingClassTypeType,
    OfferingTypeValuesType,
    OnDemandAllocationStrategyType,
    OperationTypeType,
    PartitionLoadFrequencyType,
    PaymentOptionType,
    PlacementGroupStateType,
    PlacementGroupStrategyType,
    PlacementStrategyType,
    PrefixListStateType,
    PrincipalTypeType,
    ProductCodeValuesType,
    ProtocolType,
    ReplacementStrategyType,
    ReplaceRootVolumeTaskStateType,
    ReportInstanceReasonCodesType,
    ReportStatusTypeType,
    ReservationStateType,
    ReservedInstanceStateType,
    ResourceTypeType,
    RIProductDescriptionType,
    RootDeviceTypeType,
    RouteOriginType,
    RouteStateType,
    RouteTableAssociationStateCodeType,
    RuleActionType,
    SelfServicePortalType,
    ServiceConnectivityTypeType,
    ServiceStateType,
    ServiceTypeType,
    ShutdownBehaviorType,
    SnapshotAttributeNameType,
    SnapshotStateType,
    SpotAllocationStrategyType,
    SpotInstanceInterruptionBehaviorType,
    SpotInstanceStateType,
    SpotInstanceTypeType,
    StateType,
    StaticSourcesSupportValueType,
    StatusType,
    StatusTypeType,
    StorageTierType,
    SubnetCidrBlockStateCodeType,
    SubnetCidrReservationTypeType,
    SubnetStateType,
    SummaryStatusType,
    TargetCapacityUnitTypeType,
    TelemetryStatusType,
    TenancyType,
    TieringOperationStatusType,
    TrafficDirectionType,
    TrafficMirrorFilterRuleFieldType,
    TrafficMirrorRuleActionType,
    TrafficMirrorSessionFieldType,
    TrafficMirrorTargetTypeType,
    TrafficTypeType,
    TransitGatewayAssociationStateType,
    TransitGatewayAttachmentResourceTypeType,
    TransitGatewayAttachmentStateType,
    TransitGatewayConnectPeerStateType,
    TransitGatewayMulitcastDomainAssociationStateType,
    TransitGatewayMulticastDomainStateType,
    TransitGatewayPrefixListReferenceStateType,
    TransitGatewayPropagationStateType,
    TransitGatewayRouteStateType,
    TransitGatewayRouteTableStateType,
    TransitGatewayRouteTypeType,
    TransitGatewayStateType,
    TransportProtocolType,
    TunnelInsideIpVersionType,
    UnlimitedSupportedInstanceFamilyType,
    UnsuccessfulInstanceCreditSpecificationErrorCodeType,
    UsageClassTypeType,
    VirtualizationTypeType,
    VolumeAttachmentStateType,
    VolumeAttributeNameType,
    VolumeModificationStateType,
    VolumeStateType,
    VolumeStatusInfoStatusType,
    VolumeStatusNameType,
    VolumeTypeType,
    VpcAttributeNameType,
    VpcCidrBlockStateCodeType,
    VpcEndpointTypeType,
    VpcPeeringConnectionStateReasonCodeType,
    VpcStateType,
    VpnEcmpSupportValueType,
    VpnStateType,
    WeekDayType,
    scopeType,
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
    "AcceleratorCountRequestTypeDef",
    "AcceleratorCountTypeDef",
    "AcceleratorTotalMemoryMiBRequestTypeDef",
    "AcceleratorTotalMemoryMiBTypeDef",
    "TargetConfigurationRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AcceptTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef",
    "AcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    "AcceptTransitGatewayVpcAttachmentRequestRequestTypeDef",
    "AcceptVpcEndpointConnectionsRequestRequestTypeDef",
    "AcceptVpcPeeringConnectionRequestRequestTypeDef",
    "AcceptVpcPeeringConnectionRequestVpcPeeringConnectionAcceptTypeDef",
    "AccountAttributeValueTypeDef",
    "ActiveInstanceTypeDef",
    "AddIpamOperatingRegionTypeDef",
    "AddPrefixListEntryTypeDef",
    "AnalysisComponentTypeDef",
    "PtrUpdateStatusTypeDef",
    "TagTypeDef",
    "AdvertiseByoipCidrRequestRequestTypeDef",
    "ByoipCidrTypeDef",
    "AllocateIpamPoolCidrRequestRequestTypeDef",
    "IpamPoolAllocationTypeDef",
    "AllowedPrincipalTypeDef",
    "AlternatePathHintTypeDef",
    "PortRangeTypeDef",
    "AnalysisLoadBalancerListenerTypeDef",
    "AnalysisRouteTableRouteTypeDef",
    "ApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef",
    "AssignIpv6AddressesRequestRequestTypeDef",
    "AssignPrivateIpAddressesRequestNetworkInterfaceAssignPrivateIpAddressesTypeDef",
    "AssignPrivateIpAddressesRequestRequestTypeDef",
    "AssignedPrivateIpAddressTypeDef",
    "Ipv4PrefixSpecificationTypeDef",
    "AssociateAddressRequestClassicAddressAssociateTypeDef",
    "AssociateAddressRequestRequestTypeDef",
    "AssociateAddressRequestVpcAddressAssociateTypeDef",
    "AssociateClientVpnTargetNetworkRequestRequestTypeDef",
    "AssociationStatusTypeDef",
    "AssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef",
    "AssociateDhcpOptionsRequestRequestTypeDef",
    "AssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef",
    "AssociateEnclaveCertificateIamRoleRequestRequestTypeDef",
    "IamInstanceProfileSpecificationTypeDef",
    "AssociateRouteTableRequestRequestTypeDef",
    "AssociateRouteTableRequestRouteTableAssociateWithSubnetTypeDef",
    "RouteTableAssociationStateTypeDef",
    "AssociateSubnetCidrBlockRequestRequestTypeDef",
    "AssociateTransitGatewayMulticastDomainRequestRequestTypeDef",
    "AssociateTransitGatewayRouteTableRequestRequestTypeDef",
    "TransitGatewayAssociationTypeDef",
    "AssociateTrunkInterfaceRequestRequestTypeDef",
    "AssociateVpcCidrBlockRequestRequestTypeDef",
    "AssociatedRoleTypeDef",
    "AssociatedTargetNetworkTypeDef",
    "AthenaIntegrationTypeDef",
    "AttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef",
    "AttachClassicLinkVpcRequestRequestTypeDef",
    "AttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef",
    "AttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef",
    "AttachInternetGatewayRequestRequestTypeDef",
    "AttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef",
    "AttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef",
    "AttachNetworkInterfaceRequestRequestTypeDef",
    "AttachVolumeRequestInstanceAttachVolumeTypeDef",
    "AttachVolumeRequestRequestTypeDef",
    "AttachVolumeRequestVolumeAttachToInstanceTypeDef",
    "AttachVpnGatewayRequestRequestTypeDef",
    "VpcAttachmentTypeDef",
    "AttributeBooleanValueTypeDef",
    "AttributeValueTypeDef",
    "ClientVpnAuthorizationRuleStatusTypeDef",
    "AuthorizeClientVpnIngressRequestRequestTypeDef",
    "AvailabilityZoneMessageTypeDef",
    "InstanceCapacityTypeDef",
    "BaselineEbsBandwidthMbpsRequestTypeDef",
    "BaselineEbsBandwidthMbpsTypeDef",
    "BlobAttributeValueTypeDef",
    "EbsBlockDeviceTypeDef",
    "BundleTaskErrorTypeDef",
    "CancelBundleTaskRequestRequestTypeDef",
    "CancelCapacityReservationFleetErrorTypeDef",
    "CancelCapacityReservationFleetsRequestRequestTypeDef",
    "CapacityReservationFleetCancellationStateTypeDef",
    "CancelCapacityReservationRequestRequestTypeDef",
    "CancelConversionRequestRequestTypeDef",
    "CancelExportTaskRequestRequestTypeDef",
    "CancelImportTaskRequestRequestTypeDef",
    "CancelReservedInstancesListingRequestRequestTypeDef",
    "CancelSpotFleetRequestsErrorTypeDef",
    "CancelSpotFleetRequestsRequestRequestTypeDef",
    "CancelSpotFleetRequestsSuccessItemTypeDef",
    "CancelSpotInstanceRequestsRequestRequestTypeDef",
    "CancelledSpotInstanceRequestTypeDef",
    "FleetCapacityReservationTypeDef",
    "CapacityReservationGroupTypeDef",
    "CapacityReservationOptionsRequestTypeDef",
    "CapacityReservationOptionsTypeDef",
    "CapacityReservationTargetResponseTypeDef",
    "CapacityReservationTargetTypeDef",
    "CertificateAuthenticationRequestTypeDef",
    "CertificateAuthenticationTypeDef",
    "CidrAuthorizationContextTypeDef",
    "CidrBlockTypeDef",
    "ClassicLinkDnsSupportTypeDef",
    "GroupIdentifierTypeDef",
    "ClassicLoadBalancerTypeDef",
    "ClientCertificateRevocationListStatusTypeDef",
    "ClientConnectOptionsTypeDef",
    "ClientVpnEndpointAttributeStatusTypeDef",
    "ClientDataTypeDef",
    "ClientLoginBannerOptionsTypeDef",
    "ClientLoginBannerResponseOptionsTypeDef",
    "DirectoryServiceAuthenticationRequestTypeDef",
    "FederatedAuthenticationRequestTypeDef",
    "DirectoryServiceAuthenticationTypeDef",
    "FederatedAuthenticationTypeDef",
    "ClientVpnConnectionStatusTypeDef",
    "ClientVpnEndpointStatusTypeDef",
    "ConnectionLogResponseOptionsTypeDef",
    "ClientVpnRouteStatusTypeDef",
    "CoipAddressUsageTypeDef",
    "ConfirmProductInstanceRequestRequestTypeDef",
    "ConnectionLogOptionsTypeDef",
    "ConnectionNotificationTypeDef",
    "CopyFpgaImageRequestRequestTypeDef",
    "CopyImageRequestRequestTypeDef",
    "CpuOptionsRequestTypeDef",
    "CpuOptionsTypeDef",
    "ReservationFleetInstanceSpecificationTypeDef",
    "CreateClientVpnRouteRequestRequestTypeDef",
    "CreateDefaultSubnetRequestRequestTypeDef",
    "CreateDefaultVpcRequestRequestTypeDef",
    "NewDhcpConfigurationTypeDef",
    "TargetCapacitySpecificationRequestTypeDef",
    "DestinationOptionsRequestTypeDef",
    "StorageLocationTypeDef",
    "InstanceEventWindowTimeRangeRequestTypeDef",
    "ExportToS3TaskSpecificationTypeDef",
    "RequestIpamResourceTagTypeDef",
    "CreateLocalGatewayRouteRequestRequestTypeDef",
    "LocalGatewayRouteTypeDef",
    "IcmpTypeCodeTypeDef",
    "CreateNetworkInterfacePermissionRequestRequestTypeDef",
    "InstanceIpv6AddressTypeDef",
    "Ipv4PrefixSpecificationRequestTypeDef",
    "Ipv6PrefixSpecificationRequestTypeDef",
    "PrivateIpAddressSpecificationTypeDef",
    "PriceScheduleSpecificationTypeDef",
    "CreateRouteRequestRequestTypeDef",
    "CreateRouteRequestRouteTableCreateRouteTypeDef",
    "InstanceSpecificationTypeDef",
    "CreateSpotDatafeedSubscriptionRequestRequestTypeDef",
    "S3ObjectTagTypeDef",
    "TrafficMirrorPortRangeRequestTypeDef",
    "TransitGatewayConnectRequestBgpOptionsTypeDef",
    "CreateTransitGatewayConnectRequestOptionsTypeDef",
    "CreateTransitGatewayMulticastDomainRequestOptionsTypeDef",
    "CreateTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    "TransitGatewayRequestOptionsTypeDef",
    "CreateTransitGatewayRouteRequestRequestTypeDef",
    "CreateTransitGatewayVpcAttachmentRequestOptionsTypeDef",
    "CreateVolumePermissionTypeDef",
    "CreateVpcEndpointConnectionNotificationRequestRequestTypeDef",
    "DnsOptionsSpecificationTypeDef",
    "CreateVpnConnectionRouteRequestRequestTypeDef",
    "CreditSpecificationRequestTypeDef",
    "CreditSpecificationTypeDef",
    "DeleteCarrierGatewayRequestRequestTypeDef",
    "DeleteClientVpnEndpointRequestRequestTypeDef",
    "DeleteClientVpnRouteRequestRequestTypeDef",
    "DeleteCustomerGatewayRequestRequestTypeDef",
    "DeleteDhcpOptionsRequestDhcpOptionsDeleteTypeDef",
    "DeleteDhcpOptionsRequestRequestTypeDef",
    "DeleteEgressOnlyInternetGatewayRequestRequestTypeDef",
    "DeleteFleetErrorTypeDef",
    "DeleteFleetSuccessItemTypeDef",
    "DeleteFleetsRequestRequestTypeDef",
    "DeleteFlowLogsRequestRequestTypeDef",
    "DeleteFpgaImageRequestRequestTypeDef",
    "DeleteInstanceEventWindowRequestRequestTypeDef",
    "InstanceEventWindowStateChangeTypeDef",
    "DeleteInternetGatewayRequestInternetGatewayDeleteTypeDef",
    "DeleteInternetGatewayRequestRequestTypeDef",
    "DeleteIpamPoolRequestRequestTypeDef",
    "DeleteIpamRequestRequestTypeDef",
    "DeleteIpamScopeRequestRequestTypeDef",
    "DeleteKeyPairRequestKeyPairDeleteTypeDef",
    "DeleteKeyPairRequestKeyPairInfoDeleteTypeDef",
    "DeleteKeyPairRequestRequestTypeDef",
    "DeleteLaunchTemplateRequestRequestTypeDef",
    "DeleteLaunchTemplateVersionsRequestRequestTypeDef",
    "ResponseErrorTypeDef",
    "DeleteLaunchTemplateVersionsResponseSuccessItemTypeDef",
    "DeleteLocalGatewayRouteRequestRequestTypeDef",
    "DeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef",
    "DeleteManagedPrefixListRequestRequestTypeDef",
    "DeleteNatGatewayRequestRequestTypeDef",
    "DeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef",
    "DeleteNetworkAclEntryRequestRequestTypeDef",
    "DeleteNetworkAclRequestNetworkAclDeleteTypeDef",
    "DeleteNetworkAclRequestRequestTypeDef",
    "DeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef",
    "DeleteNetworkInsightsAccessScopeRequestRequestTypeDef",
    "DeleteNetworkInsightsAnalysisRequestRequestTypeDef",
    "DeleteNetworkInsightsPathRequestRequestTypeDef",
    "DeleteNetworkInterfacePermissionRequestRequestTypeDef",
    "DeleteNetworkInterfaceRequestNetworkInterfaceDeleteTypeDef",
    "DeleteNetworkInterfaceRequestRequestTypeDef",
    "DeletePlacementGroupRequestPlacementGroupDeleteTypeDef",
    "DeletePlacementGroupRequestRequestTypeDef",
    "DeletePublicIpv4PoolRequestRequestTypeDef",
    "DeleteQueuedReservedInstancesErrorTypeDef",
    "DeleteQueuedReservedInstancesRequestRequestTypeDef",
    "SuccessfulQueuedPurchaseDeletionTypeDef",
    "DeleteRouteRequestRequestTypeDef",
    "DeleteRouteRequestRouteDeleteTypeDef",
    "DeleteRouteTableRequestRequestTypeDef",
    "DeleteRouteTableRequestRouteTableDeleteTypeDef",
    "DeleteSecurityGroupRequestRequestTypeDef",
    "DeleteSecurityGroupRequestSecurityGroupDeleteTypeDef",
    "DeleteSnapshotRequestRequestTypeDef",
    "DeleteSnapshotRequestSnapshotDeleteTypeDef",
    "DeleteSpotDatafeedSubscriptionRequestRequestTypeDef",
    "DeleteSubnetCidrReservationRequestRequestTypeDef",
    "DeleteSubnetRequestRequestTypeDef",
    "DeleteSubnetRequestSubnetDeleteTypeDef",
    "DeleteTagsRequestTagDeleteTypeDef",
    "DeleteTrafficMirrorFilterRequestRequestTypeDef",
    "DeleteTrafficMirrorFilterRuleRequestRequestTypeDef",
    "DeleteTrafficMirrorSessionRequestRequestTypeDef",
    "DeleteTrafficMirrorTargetRequestRequestTypeDef",
    "DeleteTransitGatewayConnectPeerRequestRequestTypeDef",
    "DeleteTransitGatewayConnectRequestRequestTypeDef",
    "DeleteTransitGatewayMulticastDomainRequestRequestTypeDef",
    "DeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    "DeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    "DeleteTransitGatewayRequestRequestTypeDef",
    "DeleteTransitGatewayRouteRequestRequestTypeDef",
    "DeleteTransitGatewayRouteTableRequestRequestTypeDef",
    "DeleteTransitGatewayVpcAttachmentRequestRequestTypeDef",
    "DeleteVolumeRequestRequestTypeDef",
    "DeleteVolumeRequestVolumeDeleteTypeDef",
    "DeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef",
    "DeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef",
    "DeleteVpcEndpointsRequestRequestTypeDef",
    "DeleteVpcPeeringConnectionRequestRequestTypeDef",
    "DeleteVpcPeeringConnectionRequestVpcPeeringConnectionDeleteTypeDef",
    "DeleteVpcRequestRequestTypeDef",
    "DeleteVpcRequestVpcDeleteTypeDef",
    "DeleteVpnConnectionRequestRequestTypeDef",
    "DeleteVpnConnectionRouteRequestRequestTypeDef",
    "DeleteVpnGatewayRequestRequestTypeDef",
    "DeprovisionByoipCidrRequestRequestTypeDef",
    "DeprovisionIpamPoolCidrRequestRequestTypeDef",
    "DeprovisionPublicIpv4PoolCidrRequestRequestTypeDef",
    "DeregisterImageRequestImageDeregisterTypeDef",
    "DeregisterImageRequestRequestTypeDef",
    "DeregisterInstanceTagAttributeRequestTypeDef",
    "InstanceTagNotificationAttributeTypeDef",
    "DeregisterTransitGatewayMulticastGroupMembersRequestRequestTypeDef",
    "TransitGatewayMulticastDeregisteredGroupMembersTypeDef",
    "DeregisterTransitGatewayMulticastGroupSourcesRequestRequestTypeDef",
    "TransitGatewayMulticastDeregisteredGroupSourcesTypeDef",
    "DescribeAccountAttributesRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeAddressesAttributeRequestRequestTypeDef",
    "FilterTypeDef",
    "DescribeAggregateIdFormatRequestRequestTypeDef",
    "IdFormatTypeDef",
    "WaiterConfigTypeDef",
    "DescribeByoipCidrsRequestRequestTypeDef",
    "DescribeConversionTasksRequestRequestTypeDef",
    "FastLaunchLaunchTemplateSpecificationResponseTypeDef",
    "FastLaunchSnapshotConfigurationResponseTypeDef",
    "DescribeFastSnapshotRestoreSuccessItemTypeDef",
    "DescribeFleetHistoryRequestRequestTypeDef",
    "DescribeFpgaImageAttributeRequestRequestTypeDef",
    "HostOfferingTypeDef",
    "DescribeIdFormatRequestRequestTypeDef",
    "DescribeIdentityIdFormatRequestRequestTypeDef",
    "DescribeImageAttributeRequestImageDescribeAttributeTypeDef",
    "DescribeImageAttributeRequestRequestTypeDef",
    "DescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef",
    "DescribeInstanceAttributeRequestRequestTypeDef",
    "InstanceCreditSpecificationTypeDef",
    "DescribeInstanceEventNotificationAttributesRequestRequestTypeDef",
    "InstanceTypeOfferingTypeDef",
    "MovingAddressStatusTypeDef",
    "DescribeNetworkInterfaceAttributeRequestNetworkInterfaceDescribeAttributeTypeDef",
    "DescribeNetworkInterfaceAttributeRequestRequestTypeDef",
    "NetworkInterfaceAttachmentTypeDef",
    "PrefixListTypeDef",
    "DescribePrincipalIdFormatRequestRequestTypeDef",
    "RegionTypeDef",
    "ScheduledInstanceRecurrenceRequestTypeDef",
    "SlotDateTimeRangeRequestTypeDef",
    "SlotStartTimeRangeRequestTypeDef",
    "DescribeSecurityGroupReferencesRequestRequestTypeDef",
    "SecurityGroupReferenceTypeDef",
    "DescribeSnapshotAttributeRequestRequestTypeDef",
    "DescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef",
    "ProductCodeTypeDef",
    "DescribeSpotDatafeedSubscriptionRequestRequestTypeDef",
    "DescribeSpotFleetInstancesRequestRequestTypeDef",
    "DescribeSpotFleetRequestHistoryRequestRequestTypeDef",
    "DescribeSpotFleetRequestsRequestRequestTypeDef",
    "SpotPriceTypeDef",
    "DescribeStaleSecurityGroupsRequestRequestTypeDef",
    "StoreImageTaskResultTypeDef",
    "TagDescriptionTypeDef",
    "DescribeVolumeAttributeRequestRequestTypeDef",
    "DescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef",
    "VolumeModificationTypeDef",
    "DescribeVpcAttributeRequestRequestTypeDef",
    "DescribeVpcAttributeRequestVpcDescribeAttributeTypeDef",
    "DescribeVpcClassicLinkDnsSupportRequestRequestTypeDef",
    "DestinationOptionsResponseTypeDef",
    "DetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef",
    "DetachClassicLinkVpcRequestRequestTypeDef",
    "DetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef",
    "DetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef",
    "DetachInternetGatewayRequestRequestTypeDef",
    "DetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef",
    "DetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef",
    "DetachNetworkInterfaceRequestRequestTypeDef",
    "DetachVolumeRequestInstanceDetachVolumeTypeDef",
    "DetachVolumeRequestRequestTypeDef",
    "DetachVolumeRequestVolumeDetachFromInstanceTypeDef",
    "DetachVpnGatewayRequestRequestTypeDef",
    "DisableEbsEncryptionByDefaultRequestRequestTypeDef",
    "DisableFastLaunchRequestRequestTypeDef",
    "DisableFastSnapshotRestoreStateErrorTypeDef",
    "DisableFastSnapshotRestoreSuccessItemTypeDef",
    "DisableFastSnapshotRestoresRequestRequestTypeDef",
    "DisableImageDeprecationRequestRequestTypeDef",
    "DisableIpamOrganizationAdminAccountRequestRequestTypeDef",
    "DisableSerialConsoleAccessRequestRequestTypeDef",
    "DisableTransitGatewayRouteTablePropagationRequestRequestTypeDef",
    "TransitGatewayPropagationTypeDef",
    "DisableVgwRoutePropagationRequestRequestTypeDef",
    "DisableVpcClassicLinkDnsSupportRequestRequestTypeDef",
    "DisableVpcClassicLinkRequestRequestTypeDef",
    "DisableVpcClassicLinkRequestVpcDisableClassicLinkTypeDef",
    "DisassociateAddressRequestClassicAddressDisassociateTypeDef",
    "DisassociateAddressRequestNetworkInterfaceAssociationDeleteTypeDef",
    "DisassociateAddressRequestRequestTypeDef",
    "DisassociateClientVpnTargetNetworkRequestRequestTypeDef",
    "DisassociateEnclaveCertificateIamRoleRequestRequestTypeDef",
    "DisassociateIamInstanceProfileRequestRequestTypeDef",
    "DisassociateRouteTableRequestRequestTypeDef",
    "DisassociateRouteTableRequestRouteTableAssociationDeleteTypeDef",
    "DisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef",
    "DisassociateSubnetCidrBlockRequestRequestTypeDef",
    "DisassociateTransitGatewayMulticastDomainRequestRequestTypeDef",
    "DisassociateTransitGatewayRouteTableRequestRequestTypeDef",
    "DisassociateTrunkInterfaceRequestRequestTypeDef",
    "DisassociateVpcCidrBlockRequestRequestTypeDef",
    "DiskImageDescriptionTypeDef",
    "DiskImageDetailTypeDef",
    "VolumeDetailTypeDef",
    "DiskImageVolumeDescriptionTypeDef",
    "DiskInfoTypeDef",
    "DnsEntryTypeDef",
    "DnsOptionsTypeDef",
    "DnsServersOptionsModifyStructureTypeDef",
    "EbsOptimizedInfoTypeDef",
    "EbsInstanceBlockDeviceSpecificationTypeDef",
    "EbsInstanceBlockDeviceTypeDef",
    "EfaInfoTypeDef",
    "InternetGatewayAttachmentTypeDef",
    "ElasticGpuAssociationTypeDef",
    "ElasticGpuHealthTypeDef",
    "ElasticGpuSpecificationResponseTypeDef",
    "ElasticGpuSpecificationTypeDef",
    "ElasticInferenceAcceleratorAssociationTypeDef",
    "ElasticInferenceAcceleratorTypeDef",
    "EnableEbsEncryptionByDefaultRequestRequestTypeDef",
    "FastLaunchLaunchTemplateSpecificationRequestTypeDef",
    "FastLaunchSnapshotConfigurationRequestTypeDef",
    "EnableFastSnapshotRestoreStateErrorTypeDef",
    "EnableFastSnapshotRestoreSuccessItemTypeDef",
    "EnableFastSnapshotRestoresRequestRequestTypeDef",
    "EnableImageDeprecationRequestRequestTypeDef",
    "EnableIpamOrganizationAdminAccountRequestRequestTypeDef",
    "EnableSerialConsoleAccessRequestRequestTypeDef",
    "EnableTransitGatewayRouteTablePropagationRequestRequestTypeDef",
    "EnableVgwRoutePropagationRequestRequestTypeDef",
    "EnableVolumeIORequestRequestTypeDef",
    "EnableVolumeIORequestVolumeEnableIoTypeDef",
    "EnableVpcClassicLinkDnsSupportRequestRequestTypeDef",
    "EnableVpcClassicLinkRequestRequestTypeDef",
    "EnableVpcClassicLinkRequestVpcEnableClassicLinkTypeDef",
    "EnclaveOptionsRequestTypeDef",
    "EnclaveOptionsTypeDef",
    "EventInformationTypeDef",
    "TransitGatewayRouteTableRouteTypeDef",
    "ExportClientVpnClientCertificateRevocationListRequestRequestTypeDef",
    "ExportClientVpnClientConfigurationRequestRequestTypeDef",
    "ExportTaskS3LocationRequestTypeDef",
    "ExportTaskS3LocationTypeDef",
    "ExportToS3TaskTypeDef",
    "InstanceExportDetailsTypeDef",
    "TargetCapacitySpecificationTypeDef",
    "FleetLaunchTemplateSpecificationRequestTypeDef",
    "FleetLaunchTemplateSpecificationTypeDef",
    "PlacementTypeDef",
    "PlacementResponseTypeDef",
    "FleetSpotCapacityRebalanceRequestTypeDef",
    "FleetSpotCapacityRebalanceTypeDef",
    "FpgaDeviceMemoryInfoTypeDef",
    "LoadPermissionTypeDef",
    "FpgaImageStateTypeDef",
    "PciIdTypeDef",
    "GetAssociatedEnclaveCertificateIamRolesRequestRequestTypeDef",
    "GetAssociatedIpv6PoolCidrsRequestRequestTypeDef",
    "Ipv6CidrAssociationTypeDef",
    "GetCapacityReservationUsageRequestRequestTypeDef",
    "InstanceUsageTypeDef",
    "GetConsoleOutputRequestInstanceConsoleOutputTypeDef",
    "GetConsoleOutputRequestRequestTypeDef",
    "GetConsoleScreenshotRequestRequestTypeDef",
    "GetDefaultCreditSpecificationRequestRequestTypeDef",
    "InstanceFamilyCreditSpecificationTypeDef",
    "GetEbsDefaultKmsKeyIdRequestRequestTypeDef",
    "GetEbsEncryptionByDefaultRequestRequestTypeDef",
    "GetGroupsForCapacityReservationRequestRequestTypeDef",
    "GetHostReservationPurchasePreviewRequestRequestTypeDef",
    "PurchaseTypeDef",
    "InstanceTypeInfoFromInstanceRequirementsTypeDef",
    "GetInstanceUefiDataRequestRequestTypeDef",
    "GetIpamAddressHistoryRequestRequestTypeDef",
    "IpamAddressHistoryRecordTypeDef",
    "GetLaunchTemplateDataRequestRequestTypeDef",
    "GetManagedPrefixListAssociationsRequestRequestTypeDef",
    "PrefixListAssociationTypeDef",
    "GetManagedPrefixListEntriesRequestRequestTypeDef",
    "PrefixListEntryTypeDef",
    "GetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef",
    "GetNetworkInsightsAccessScopeContentRequestRequestTypeDef",
    "GetPasswordDataRequestInstancePasswordDataTypeDef",
    "GetPasswordDataRequestRequestTypeDef",
    "ReservationValueTypeDef",
    "GetSerialConsoleAccessStatusRequestRequestTypeDef",
    "SpotPlacementScoreTypeDef",
    "TransitGatewayAttachmentPropagationTypeDef",
    "TransitGatewayRouteTableAssociationTypeDef",
    "TransitGatewayRouteTablePropagationTypeDef",
    "GetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef",
    "GetVpnConnectionDeviceTypesRequestRequestTypeDef",
    "VpnConnectionDeviceTypeTypeDef",
    "GpuDeviceMemoryInfoTypeDef",
    "HibernationOptionsRequestTypeDef",
    "HibernationOptionsTypeDef",
    "HostInstanceTypeDef",
    "HostPropertiesTypeDef",
    "IKEVersionsListValueTypeDef",
    "IKEVersionsRequestListValueTypeDef",
    "IamInstanceProfileTypeDef",
    "LaunchPermissionTypeDef",
    "UserBucketTypeDef",
    "ImageRecycleBinInfoTypeDef",
    "StateReasonTypeDef",
    "ImportClientVpnClientCertificateRevocationListRequestRequestTypeDef",
    "ImportImageLicenseConfigurationRequestTypeDef",
    "ImportImageLicenseConfigurationResponseTypeDef",
    "UserDataTypeDef",
    "InferenceDeviceInfoTypeDef",
    "InstanceCountTypeDef",
    "InstanceCreditSpecificationRequestTypeDef",
    "InstanceEventWindowTimeRangeTypeDef",
    "InstanceIpv4PrefixTypeDef",
    "InstanceIpv6AddressRequestTypeDef",
    "InstanceIpv6PrefixTypeDef",
    "InstanceMaintenanceOptionsRequestTypeDef",
    "InstanceMaintenanceOptionsTypeDef",
    "SpotMarketOptionsTypeDef",
    "InstanceMetadataOptionsRequestTypeDef",
    "InstanceMetadataOptionsResponseTypeDef",
    "MonitoringTypeDef",
    "InstanceNetworkInterfaceAssociationTypeDef",
    "InstanceNetworkInterfaceAttachmentTypeDef",
    "MemoryGiBPerVCpuRequestTypeDef",
    "MemoryMiBRequestTypeDef",
    "NetworkInterfaceCountRequestTypeDef",
    "TotalLocalStorageGBRequestTypeDef",
    "VCpuCountRangeRequestTypeDef",
    "MemoryGiBPerVCpuTypeDef",
    "MemoryMiBTypeDef",
    "NetworkInterfaceCountTypeDef",
    "TotalLocalStorageGBTypeDef",
    "VCpuCountRangeTypeDef",
    "InstanceStateTypeDef",
    "InstanceStatusDetailsTypeDef",
    "InstanceStatusEventTypeDef",
    "LicenseConfigurationTypeDef",
    "PrivateDnsNameOptionsResponseTypeDef",
    "MemoryInfoTypeDef",
    "PlacementGroupInfoTypeDef",
    "ProcessorInfoTypeDef",
    "VCpuInfoTypeDef",
    "IpRangeTypeDef",
    "Ipv6RangeTypeDef",
    "PrefixListIdTypeDef",
    "UserIdGroupPairTypeDef",
    "IpamCidrAuthorizationContextTypeDef",
    "IpamOperatingRegionTypeDef",
    "IpamPoolCidrFailureReasonTypeDef",
    "IpamResourceTagTypeDef",
    "Ipv4PrefixSpecificationResponseTypeDef",
    "Ipv6CidrBlockTypeDef",
    "PoolCidrBlockTypeDef",
    "Ipv6PrefixSpecificationResponseTypeDef",
    "Ipv6PrefixSpecificationTypeDef",
    "LastErrorTypeDef",
    "RunInstancesMonitoringEnabledTypeDef",
    "SpotPlacementTypeDef",
    "LaunchTemplateEbsBlockDeviceRequestTypeDef",
    "LaunchTemplateEbsBlockDeviceTypeDef",
    "LaunchTemplateCpuOptionsRequestTypeDef",
    "LaunchTemplateCpuOptionsTypeDef",
    "LaunchTemplateElasticInferenceAcceleratorResponseTypeDef",
    "LaunchTemplateElasticInferenceAcceleratorTypeDef",
    "LaunchTemplateEnclaveOptionsRequestTypeDef",
    "LaunchTemplateEnclaveOptionsTypeDef",
    "LaunchTemplateHibernationOptionsRequestTypeDef",
    "LaunchTemplateHibernationOptionsTypeDef",
    "LaunchTemplateIamInstanceProfileSpecificationRequestTypeDef",
    "LaunchTemplateIamInstanceProfileSpecificationTypeDef",
    "LaunchTemplateInstanceMaintenanceOptionsRequestTypeDef",
    "LaunchTemplateInstanceMaintenanceOptionsTypeDef",
    "LaunchTemplateSpotMarketOptionsRequestTypeDef",
    "LaunchTemplateSpotMarketOptionsTypeDef",
    "LaunchTemplateInstanceMetadataOptionsRequestTypeDef",
    "LaunchTemplateInstanceMetadataOptionsTypeDef",
    "LaunchTemplateLicenseConfigurationRequestTypeDef",
    "LaunchTemplateLicenseConfigurationTypeDef",
    "LaunchTemplatePlacementRequestTypeDef",
    "LaunchTemplatePlacementTypeDef",
    "LaunchTemplatePrivateDnsNameOptionsRequestTypeDef",
    "LaunchTemplatePrivateDnsNameOptionsTypeDef",
    "LaunchTemplateSpecificationTypeDef",
    "LaunchTemplatesMonitoringRequestTypeDef",
    "LaunchTemplatesMonitoringTypeDef",
    "LicenseConfigurationRequestTypeDef",
    "ListImagesInRecycleBinRequestRequestTypeDef",
    "ListSnapshotsInRecycleBinRequestRequestTypeDef",
    "SnapshotRecycleBinInfoTypeDef",
    "LoadPermissionRequestTypeDef",
    "ModifyAddressAttributeRequestRequestTypeDef",
    "ModifyAvailabilityZoneGroupRequestRequestTypeDef",
    "ModifyCapacityReservationFleetRequestRequestTypeDef",
    "ModifyCapacityReservationRequestRequestTypeDef",
    "ModifyDefaultCreditSpecificationRequestRequestTypeDef",
    "ModifyEbsDefaultKmsKeyIdRequestRequestTypeDef",
    "ModifyHostsRequestRequestTypeDef",
    "ModifyIdFormatRequestRequestTypeDef",
    "ModifyIdentityIdFormatRequestRequestTypeDef",
    "SuccessfulInstanceCreditSpecificationItemTypeDef",
    "ModifyInstanceEventStartTimeRequestRequestTypeDef",
    "ModifyInstanceMaintenanceOptionsRequestRequestTypeDef",
    "ModifyInstanceMetadataOptionsRequestRequestTypeDef",
    "ModifyInstancePlacementRequestRequestTypeDef",
    "RemoveIpamOperatingRegionTypeDef",
    "ModifyIpamResourceCidrRequestRequestTypeDef",
    "ModifyIpamScopeRequestRequestTypeDef",
    "ModifyLaunchTemplateRequestRequestTypeDef",
    "RemovePrefixListEntryTypeDef",
    "NetworkInterfaceAttachmentChangesTypeDef",
    "ModifyPrivateDnsNameOptionsRequestRequestTypeDef",
    "ReservedInstancesConfigurationTypeDef",
    "ModifySnapshotTierRequestRequestTypeDef",
    "ModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef",
    "ModifyTrafficMirrorSessionRequestRequestTypeDef",
    "ModifyTransitGatewayOptionsTypeDef",
    "ModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    "ModifyTransitGatewayVpcAttachmentRequestOptionsTypeDef",
    "ModifyVolumeRequestRequestTypeDef",
    "ModifyVpcEndpointConnectionNotificationRequestRequestTypeDef",
    "ModifyVpcEndpointServiceConfigurationRequestRequestTypeDef",
    "ModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef",
    "ModifyVpcEndpointServicePermissionsRequestRequestTypeDef",
    "PeeringConnectionOptionsRequestTypeDef",
    "PeeringConnectionOptionsTypeDef",
    "ModifyVpcTenancyRequestRequestTypeDef",
    "ModifyVpnConnectionOptionsRequestRequestTypeDef",
    "ModifyVpnConnectionRequestRequestTypeDef",
    "ModifyVpnTunnelCertificateRequestRequestTypeDef",
    "Phase1DHGroupNumbersRequestListValueTypeDef",
    "Phase1EncryptionAlgorithmsRequestListValueTypeDef",
    "Phase1IntegrityAlgorithmsRequestListValueTypeDef",
    "Phase2DHGroupNumbersRequestListValueTypeDef",
    "Phase2EncryptionAlgorithmsRequestListValueTypeDef",
    "Phase2IntegrityAlgorithmsRequestListValueTypeDef",
    "MonitorInstancesRequestInstanceMonitorTypeDef",
    "MonitorInstancesRequestRequestTypeDef",
    "MoveAddressToVpcRequestRequestTypeDef",
    "MoveByoipCidrToIpamRequestRequestTypeDef",
    "NatGatewayAddressTypeDef",
    "ProvisionedBandwidthTypeDef",
    "NetworkAclAssociationTypeDef",
    "NetworkCardInfoTypeDef",
    "NetworkInterfaceAssociationTypeDef",
    "NetworkInterfaceIpv6AddressTypeDef",
    "NetworkInterfacePermissionStateTypeDef",
    "PacketHeaderStatementRequestTypeDef",
    "PacketHeaderStatementTypeDef",
    "ResourceStatementRequestTypeDef",
    "ResourceStatementTypeDef",
    "PeeringAttachmentStatusTypeDef",
    "PeeringTgwInfoTypeDef",
    "Phase1DHGroupNumbersListValueTypeDef",
    "Phase1EncryptionAlgorithmsListValueTypeDef",
    "Phase1IntegrityAlgorithmsListValueTypeDef",
    "Phase2DHGroupNumbersListValueTypeDef",
    "Phase2EncryptionAlgorithmsListValueTypeDef",
    "Phase2IntegrityAlgorithmsListValueTypeDef",
    "PriceScheduleTypeDef",
    "PricingDetailTypeDef",
    "PrivateDnsDetailsTypeDef",
    "PrivateDnsNameConfigurationTypeDef",
    "PrivateDnsNameOptionsOnLaunchTypeDef",
    "PrivateDnsNameOptionsRequestTypeDef",
    "PropagatingVgwTypeDef",
    "ProvisionPublicIpv4PoolCidrRequestRequestTypeDef",
    "PublicIpv4PoolRangeTypeDef",
    "PurchaseRequestTypeDef",
    "ReservedInstanceLimitPriceTypeDef",
    "RebootInstancesRequestInstanceRebootTypeDef",
    "RebootInstancesRequestRequestTypeDef",
    "RecurringChargeTypeDef",
    "ReferencedSecurityGroupTypeDef",
    "RegisterInstanceTagAttributeRequestTypeDef",
    "RegisterTransitGatewayMulticastGroupMembersRequestRequestTypeDef",
    "TransitGatewayMulticastRegisteredGroupMembersTypeDef",
    "RegisterTransitGatewayMulticastGroupSourcesRequestRequestTypeDef",
    "TransitGatewayMulticastRegisteredGroupSourcesTypeDef",
    "RejectTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef",
    "RejectTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    "RejectTransitGatewayVpcAttachmentRequestRequestTypeDef",
    "RejectVpcEndpointConnectionsRequestRequestTypeDef",
    "RejectVpcPeeringConnectionRequestRequestTypeDef",
    "RejectVpcPeeringConnectionRequestVpcPeeringConnectionRejectTypeDef",
    "ReleaseAddressRequestClassicAddressReleaseTypeDef",
    "ReleaseAddressRequestRequestTypeDef",
    "ReleaseAddressRequestVpcAddressReleaseTypeDef",
    "ReleaseHostsRequestRequestTypeDef",
    "ReleaseIpamPoolAllocationRequestRequestTypeDef",
    "ReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef",
    "ReplaceNetworkAclAssociationRequestRequestTypeDef",
    "ReplaceRouteRequestRequestTypeDef",
    "ReplaceRouteRequestRouteReplaceTypeDef",
    "ReplaceRouteTableAssociationRequestRequestTypeDef",
    "ReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef",
    "ReplaceTransitGatewayRouteRequestRequestTypeDef",
    "ReportInstanceStatusRequestInstanceReportStatusTypeDef",
    "ReportInstanceStatusRequestRequestTypeDef",
    "ReservedInstancesIdTypeDef",
    "ResetAddressAttributeRequestRequestTypeDef",
    "ResetEbsDefaultKmsKeyIdRequestRequestTypeDef",
    "ResetFpgaImageAttributeRequestRequestTypeDef",
    "ResetImageAttributeRequestImageResetAttributeTypeDef",
    "ResetImageAttributeRequestRequestTypeDef",
    "ResetInstanceAttributeRequestInstanceResetAttributeTypeDef",
    "ResetInstanceAttributeRequestInstanceResetKernelTypeDef",
    "ResetInstanceAttributeRequestInstanceResetRamdiskTypeDef",
    "ResetInstanceAttributeRequestInstanceResetSourceDestCheckTypeDef",
    "ResetInstanceAttributeRequestRequestTypeDef",
    "ResetNetworkInterfaceAttributeRequestNetworkInterfaceResetAttributeTypeDef",
    "ResetNetworkInterfaceAttributeRequestRequestTypeDef",
    "ResetSnapshotAttributeRequestRequestTypeDef",
    "ResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef",
    "RestoreAddressToClassicRequestRequestTypeDef",
    "RestoreImageFromRecycleBinRequestRequestTypeDef",
    "RestoreManagedPrefixListVersionRequestRequestTypeDef",
    "RestoreSnapshotFromRecycleBinRequestRequestTypeDef",
    "RestoreSnapshotTierRequestRequestTypeDef",
    "RevokeClientVpnIngressRequestRequestTypeDef",
    "RouteTypeDef",
    "S3StorageTypeDef",
    "ScheduledInstanceRecurrenceTypeDef",
    "ScheduledInstancesEbsTypeDef",
    "ScheduledInstancesIamInstanceProfileTypeDef",
    "ScheduledInstancesIpv6AddressTypeDef",
    "ScheduledInstancesMonitoringTypeDef",
    "ScheduledInstancesPlacementTypeDef",
    "ScheduledInstancesPrivateIpAddressConfigTypeDef",
    "TransitGatewayMulticastGroupTypeDef",
    "SecurityGroupIdentifierTypeDef",
    "SecurityGroupRuleDescriptionTypeDef",
    "SecurityGroupRuleRequestTypeDef",
    "SendDiagnosticInterruptRequestRequestTypeDef",
    "ServiceTypeDetailTypeDef",
    "ServiceResourceClassicAddressRequestTypeDef",
    "ServiceResourceDhcpOptionsRequestTypeDef",
    "ServiceResourceImageRequestTypeDef",
    "ServiceResourceInstanceRequestTypeDef",
    "ServiceResourceInternetGatewayRequestTypeDef",
    "ServiceResourceKeyPairRequestTypeDef",
    "ServiceResourceNetworkAclRequestTypeDef",
    "ServiceResourceNetworkInterfaceAssociationRequestTypeDef",
    "ServiceResourceNetworkInterfaceRequestTypeDef",
    "ServiceResourcePlacementGroupRequestTypeDef",
    "ServiceResourceRouteRequestTypeDef",
    "ServiceResourceRouteTableAssociationRequestTypeDef",
    "ServiceResourceRouteTableRequestTypeDef",
    "ServiceResourceSecurityGroupRequestTypeDef",
    "ServiceResourceSnapshotRequestTypeDef",
    "ServiceResourceSubnetRequestTypeDef",
    "ServiceResourceTagRequestTypeDef",
    "ServiceResourceVolumeRequestTypeDef",
    "ServiceResourceVpcAddressRequestTypeDef",
    "ServiceResourceVpcPeeringConnectionRequestTypeDef",
    "ServiceResourceVpcRequestTypeDef",
    "UserBucketDetailsTypeDef",
    "SpotCapacityRebalanceTypeDef",
    "SpotInstanceStateFaultTypeDef",
    "SpotFleetMonitoringTypeDef",
    "SpotInstanceStatusTypeDef",
    "StartInstancesRequestInstanceStartTypeDef",
    "StartInstancesRequestRequestTypeDef",
    "StartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef",
    "StopInstancesRequestInstanceStopTypeDef",
    "StopInstancesRequestRequestTypeDef",
    "SubnetAssociationTypeDef",
    "SubnetCidrBlockStateTypeDef",
    "TargetConfigurationTypeDef",
    "TargetGroupTypeDef",
    "TerminateClientVpnConnectionsRequestRequestTypeDef",
    "TerminateInstancesRequestInstanceTerminateTypeDef",
    "TerminateInstancesRequestRequestTypeDef",
    "TrafficMirrorPortRangeTypeDef",
    "TransitGatewayAttachmentAssociationTypeDef",
    "TransitGatewayAttachmentBgpConfigurationTypeDef",
    "TransitGatewayConnectOptionsTypeDef",
    "TransitGatewayMulticastDomainOptionsTypeDef",
    "TransitGatewayOptionsTypeDef",
    "TransitGatewayPrefixListAttachmentTypeDef",
    "TransitGatewayRouteAttachmentTypeDef",
    "TransitGatewayVpcAttachmentOptionsTypeDef",
    "UnassignIpv6AddressesRequestRequestTypeDef",
    "UnassignPrivateIpAddressesRequestNetworkInterfaceUnassignPrivateIpAddressesTypeDef",
    "UnassignPrivateIpAddressesRequestRequestTypeDef",
    "UnmonitorInstancesRequestInstanceUnmonitorTypeDef",
    "UnmonitorInstancesRequestRequestTypeDef",
    "UnsuccessfulInstanceCreditSpecificationItemErrorTypeDef",
    "UnsuccessfulItemErrorTypeDef",
    "ValidationErrorTypeDef",
    "VgwTelemetryTypeDef",
    "VolumeAttachmentTypeDef",
    "VolumeStatusActionTypeDef",
    "VolumeStatusAttachmentStatusTypeDef",
    "VolumeStatusDetailsTypeDef",
    "VolumeStatusEventTypeDef",
    "VpcCidrBlockStateTypeDef",
    "VpcPeeringConnectionOptionsDescriptionTypeDef",
    "VpcPeeringConnectionStateReasonTypeDef",
    "VpnStaticRouteTypeDef",
    "WithdrawByoipCidrRequestRequestTypeDef",
    "AcceptReservedInstancesExchangeQuoteRequestRequestTypeDef",
    "GetReservedInstancesExchangeQuoteRequestRequestTypeDef",
    "AcceptReservedInstancesExchangeQuoteResultTypeDef",
    "AllocateAddressResultTypeDef",
    "AllocateHostsResultTypeDef",
    "ApplySecurityGroupsToClientVpnTargetNetworkResultTypeDef",
    "AssignIpv6AddressesResultTypeDef",
    "AssociateAddressResultTypeDef",
    "AssociateEnclaveCertificateIamRoleResultTypeDef",
    "AttachClassicLinkVpcResultTypeDef",
    "AttachNetworkInterfaceResultTypeDef",
    "CancelCapacityReservationResultTypeDef",
    "CancelImportTaskResultTypeDef",
    "ConfirmProductInstanceResultTypeDef",
    "CopyFpgaImageResultTypeDef",
    "CopyImageResultTypeDef",
    "CpuOptionsResponseMetadataTypeDef",
    "CreateFpgaImageResultTypeDef",
    "CreateImageResultTypeDef",
    "CreatePublicIpv4PoolResultTypeDef",
    "CreateRestoreImageTaskResultTypeDef",
    "CreateRouteResultTypeDef",
    "CreateStoreImageTaskResultTypeDef",
    "DeleteEgressOnlyInternetGatewayResultTypeDef",
    "DeleteFpgaImageResultTypeDef",
    "DeleteNatGatewayResultTypeDef",
    "DeleteNetworkInsightsAccessScopeAnalysisResultTypeDef",
    "DeleteNetworkInsightsAccessScopeResultTypeDef",
    "DeleteNetworkInsightsAnalysisResultTypeDef",
    "DeleteNetworkInsightsPathResultTypeDef",
    "DeleteNetworkInterfacePermissionResultTypeDef",
    "DeletePublicIpv4PoolResultTypeDef",
    "DeleteTrafficMirrorFilterResultTypeDef",
    "DeleteTrafficMirrorFilterRuleResultTypeDef",
    "DeleteTrafficMirrorSessionResultTypeDef",
    "DeleteTrafficMirrorTargetResultTypeDef",
    "DeleteVpcPeeringConnectionResultTypeDef",
    "DeprovisionPublicIpv4PoolCidrResultTypeDef",
    "DetachClassicLinkVpcResultTypeDef",
    "DisableEbsEncryptionByDefaultResultTypeDef",
    "DisableImageDeprecationResultTypeDef",
    "DisableIpamOrganizationAdminAccountResultTypeDef",
    "DisableSerialConsoleAccessResultTypeDef",
    "DisableVpcClassicLinkDnsSupportResultTypeDef",
    "DisableVpcClassicLinkResultTypeDef",
    "DisassociateEnclaveCertificateIamRoleResultTypeDef",
    "DisassociateTrunkInterfaceResultTypeDef",
    "EnableEbsEncryptionByDefaultResultTypeDef",
    "EnableImageDeprecationResultTypeDef",
    "EnableIpamOrganizationAdminAccountResultTypeDef",
    "EnableSerialConsoleAccessResultTypeDef",
    "EnableVpcClassicLinkDnsSupportResultTypeDef",
    "EnableVpcClassicLinkResultTypeDef",
    "EnclaveOptionsResponseMetadataTypeDef",
    "ExportClientVpnClientConfigurationResultTypeDef",
    "ExportTransitGatewayRoutesResultTypeDef",
    "GetConsoleOutputResultTypeDef",
    "GetConsoleScreenshotResultTypeDef",
    "GetEbsDefaultKmsKeyIdResultTypeDef",
    "GetEbsEncryptionByDefaultResultTypeDef",
    "GetFlowLogsIntegrationTemplateResultTypeDef",
    "GetInstanceUefiDataResultTypeDef",
    "GetPasswordDataResultTypeDef",
    "GetSerialConsoleAccessStatusResultTypeDef",
    "GetVpnConnectionDeviceSampleConfigurationResultTypeDef",
    "HibernationOptionsResponseMetadataTypeDef",
    "IamInstanceProfileResponseMetadataTypeDef",
    "ImportClientVpnClientCertificateRevocationListResultTypeDef",
    "InstanceMaintenanceOptionsResponseMetadataTypeDef",
    "InstanceMetadataOptionsResponseResponseMetadataTypeDef",
    "InstanceStateResponseMetadataTypeDef",
    "ModifyAvailabilityZoneGroupResultTypeDef",
    "ModifyCapacityReservationFleetResultTypeDef",
    "ModifyCapacityReservationResultTypeDef",
    "ModifyClientVpnEndpointResultTypeDef",
    "ModifyEbsDefaultKmsKeyIdResultTypeDef",
    "ModifyFleetResultTypeDef",
    "ModifyInstanceCapacityReservationAttributesResultTypeDef",
    "ModifyInstanceMaintenanceOptionsResultTypeDef",
    "ModifyInstancePlacementResultTypeDef",
    "ModifyPrivateDnsNameOptionsResultTypeDef",
    "ModifyReservedInstancesResultTypeDef",
    "ModifySecurityGroupRulesResultTypeDef",
    "ModifySnapshotTierResultTypeDef",
    "ModifySpotFleetRequestResponseTypeDef",
    "ModifyVpcEndpointConnectionNotificationResultTypeDef",
    "ModifyVpcEndpointResultTypeDef",
    "ModifyVpcEndpointServiceConfigurationResultTypeDef",
    "ModifyVpcEndpointServicePayerResponsibilityResultTypeDef",
    "ModifyVpcEndpointServicePermissionsResultTypeDef",
    "ModifyVpcTenancyResultTypeDef",
    "MonitoringResponseMetadataTypeDef",
    "MoveAddressToVpcResultTypeDef",
    "NetworkInterfaceAssociationResponseMetadataTypeDef",
    "NetworkInterfaceAttachmentResponseMetadataTypeDef",
    "PlacementResponseMetadataTypeDef",
    "PrivateDnsNameOptionsOnLaunchResponseMetadataTypeDef",
    "PrivateDnsNameOptionsResponseResponseMetadataTypeDef",
    "PurchaseReservedInstancesOfferingResultTypeDef",
    "RegisterImageResultTypeDef",
    "RejectVpcPeeringConnectionResultTypeDef",
    "ReleaseIpamPoolAllocationResultTypeDef",
    "ReplaceNetworkAclAssociationResultTypeDef",
    "RequestSpotFleetResponseTypeDef",
    "ResetEbsDefaultKmsKeyIdResultTypeDef",
    "ResetFpgaImageAttributeResultTypeDef",
    "RestoreAddressToClassicResultTypeDef",
    "RestoreImageFromRecycleBinResultTypeDef",
    "RestoreSnapshotFromRecycleBinResultTypeDef",
    "RestoreSnapshotTierResultTypeDef",
    "RouteTableAssociationStateResponseMetadataTypeDef",
    "RunScheduledInstancesResultTypeDef",
    "StartVpcEndpointServicePrivateDnsVerificationResultTypeDef",
    "StateReasonResponseMetadataTypeDef",
    "UnassignIpv6AddressesResultTypeDef",
    "UpdateSecurityGroupRuleDescriptionsEgressResultTypeDef",
    "UpdateSecurityGroupRuleDescriptionsIngressResultTypeDef",
    "VolumeAttachmentResponseMetadataTypeDef",
    "VpcPeeringConnectionStateReasonResponseMetadataTypeDef",
    "AccountAttributeTypeDef",
    "DescribeFleetInstancesResultTypeDef",
    "DescribeSpotFleetInstancesResponseTypeDef",
    "AdditionalDetailTypeDef",
    "AnalysisLoadBalancerTargetTypeDef",
    "AddressAttributeTypeDef",
    "AddressTypeDef",
    "CapacityReservationTypeDef",
    "CarrierGatewayTypeDef",
    "CoipPoolTypeDef",
    "CopySnapshotResultTypeDef",
    "CreateSecurityGroupResultTypeDef",
    "CreateTagsRequestDhcpOptionsCreateTagsTypeDef",
    "CreateTagsRequestImageCreateTagsTypeDef",
    "CreateTagsRequestInstanceCreateTagsTypeDef",
    "CreateTagsRequestInternetGatewayCreateTagsTypeDef",
    "CreateTagsRequestNetworkAclCreateTagsTypeDef",
    "CreateTagsRequestNetworkInterfaceCreateTagsTypeDef",
    "CreateTagsRequestRequestTypeDef",
    "CreateTagsRequestRouteTableCreateTagsTypeDef",
    "CreateTagsRequestSecurityGroupCreateTagsTypeDef",
    "CreateTagsRequestServiceResourceCreateTagsTypeDef",
    "CreateTagsRequestSnapshotCreateTagsTypeDef",
    "CreateTagsRequestSubnetCreateTagsTypeDef",
    "CreateTagsRequestVolumeCreateTagsTypeDef",
    "CreateTagsRequestVpcCreateTagsTypeDef",
    "CustomerGatewayTypeDef",
    "DeleteTagsRequestRequestTypeDef",
    "HostReservationTypeDef",
    "ImportKeyPairResultTypeDef",
    "InstanceDeleteTagsRequestTypeDef",
    "InstanceEventWindowAssociationRequestTypeDef",
    "InstanceEventWindowAssociationTargetTypeDef",
    "InstanceEventWindowDisassociationRequestTypeDef",
    "IpamScopeTypeDef",
    "KeyPairInfoTypeDef",
    "KeyPairTypeDef",
    "LaunchTemplateTagSpecificationRequestTypeDef",
    "LaunchTemplateTagSpecificationTypeDef",
    "LaunchTemplateTypeDef",
    "LocalGatewayRouteTableTypeDef",
    "LocalGatewayRouteTableVirtualInterfaceGroupAssociationTypeDef",
    "LocalGatewayRouteTableVpcAssociationTypeDef",
    "LocalGatewayTypeDef",
    "LocalGatewayVirtualInterfaceGroupTypeDef",
    "LocalGatewayVirtualInterfaceTypeDef",
    "ManagedPrefixListTypeDef",
    "NetworkInsightsAccessScopeAnalysisTypeDef",
    "NetworkInsightsAccessScopeTypeDef",
    "NetworkInsightsPathTypeDef",
    "PlacementGroupTypeDef",
    "ReplaceRootVolumeTaskTypeDef",
    "SnapshotInfoTypeDef",
    "SnapshotResponseMetadataTypeDef",
    "SnapshotTierStatusTypeDef",
    "SnapshotTypeDef",
    "SpotFleetTagSpecificationTypeDef",
    "SubnetCidrReservationTypeDef",
    "TagSpecificationTypeDef",
    "TrafficMirrorSessionTypeDef",
    "TrafficMirrorTargetTypeDef",
    "TransitGatewayRouteTableTypeDef",
    "TrunkInterfaceAssociationTypeDef",
    "VpcClassicLinkTypeDef",
    "AdvertiseByoipCidrResultTypeDef",
    "DeprovisionByoipCidrResultTypeDef",
    "DescribeByoipCidrsResultTypeDef",
    "MoveByoipCidrToIpamResultTypeDef",
    "ProvisionByoipCidrResultTypeDef",
    "WithdrawByoipCidrResultTypeDef",
    "AllocateIpamPoolCidrResultTypeDef",
    "GetIpamPoolAllocationsResultTypeDef",
    "DescribeVpcEndpointServicePermissionsResultTypeDef",
    "AnalysisAclRuleTypeDef",
    "AnalysisPacketHeaderTypeDef",
    "AnalysisSecurityGroupRuleTypeDef",
    "AssignPrivateIpAddressesResultTypeDef",
    "AssociateClientVpnTargetNetworkResultTypeDef",
    "DisassociateClientVpnTargetNetworkResultTypeDef",
    "TargetNetworkTypeDef",
    "AssociateIamInstanceProfileRequestRequestTypeDef",
    "ReplaceIamInstanceProfileAssociationRequestRequestTypeDef",
    "AssociateRouteTableResultTypeDef",
    "ReplaceRouteTableAssociationResultTypeDef",
    "RouteTableAssociationTypeDef",
    "AssociateTransitGatewayRouteTableResultTypeDef",
    "DisassociateTransitGatewayRouteTableResultTypeDef",
    "GetAssociatedEnclaveCertificateIamRolesResultTypeDef",
    "IntegrateServicesTypeDef",
    "AttachVpnGatewayResultTypeDef",
    "VpnGatewayTypeDef",
    "DescribeVpcAttributeResultTypeDef",
    "ModifySubnetAttributeRequestRequestTypeDef",
    "ModifyVolumeAttributeRequestRequestTypeDef",
    "ModifyVolumeAttributeRequestVolumeModifyAttributeTypeDef",
    "ModifyVpcAttributeRequestRequestTypeDef",
    "ModifyVpcAttributeRequestVpcModifyAttributeTypeDef",
    "DhcpConfigurationTypeDef",
    "AuthorizationRuleTypeDef",
    "AuthorizeClientVpnIngressResultTypeDef",
    "RevokeClientVpnIngressResultTypeDef",
    "AvailabilityZoneTypeDef",
    "AvailableCapacityTypeDef",
    "BlockDeviceMappingTypeDef",
    "FailedCapacityReservationFleetCancellationResultTypeDef",
    "CancelSpotFleetRequestsErrorItemTypeDef",
    "CancelSpotInstanceRequestsResultTypeDef",
    "CapacityReservationFleetTypeDef",
    "CreateCapacityReservationFleetResultTypeDef",
    "GetGroupsForCapacityReservationResultTypeDef",
    "OnDemandOptionsRequestTypeDef",
    "OnDemandOptionsTypeDef",
    "CapacityReservationSpecificationResponseResponseMetadataTypeDef",
    "CapacityReservationSpecificationResponseTypeDef",
    "LaunchTemplateCapacityReservationSpecificationResponseTypeDef",
    "CapacityReservationSpecificationTypeDef",
    "LaunchTemplateCapacityReservationSpecificationRequestTypeDef",
    "DescribeVpcClassicLinkDnsSupportResultTypeDef",
    "ClassicLinkInstanceTypeDef",
    "ClassicLoadBalancersConfigTypeDef",
    "ExportClientVpnClientCertificateRevocationListResultTypeDef",
    "ClientConnectResponseOptionsTypeDef",
    "ClientVpnAuthenticationRequestTypeDef",
    "ClientVpnAuthenticationTypeDef",
    "ClientVpnConnectionTypeDef",
    "TerminateConnectionStatusTypeDef",
    "CreateClientVpnEndpointResultTypeDef",
    "DeleteClientVpnEndpointResultTypeDef",
    "ClientVpnRouteTypeDef",
    "CreateClientVpnRouteResultTypeDef",
    "DeleteClientVpnRouteResultTypeDef",
    "GetCoipPoolUsageResultTypeDef",
    "CreateVpcEndpointConnectionNotificationResultTypeDef",
    "DescribeVpcEndpointConnectionNotificationsResultTypeDef",
    "ModifyInstanceEventWindowRequestRequestTypeDef",
    "ModifyIpamPoolRequestRequestTypeDef",
    "CreateLocalGatewayRouteResultTypeDef",
    "DeleteLocalGatewayRouteResultTypeDef",
    "SearchLocalGatewayRoutesResultTypeDef",
    "CreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef",
    "CreateNetworkAclEntryRequestRequestTypeDef",
    "NetworkAclEntryTypeDef",
    "ReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef",
    "ReplaceNetworkAclEntryRequestRequestTypeDef",
    "InstanceNetworkInterfaceSpecificationTypeDef",
    "CreateReservedInstancesListingRequestRequestTypeDef",
    "CreateStoreImageTaskRequestRequestTypeDef",
    "CreateTrafficMirrorFilterRuleRequestRequestTypeDef",
    "ModifyTrafficMirrorFilterRuleRequestRequestTypeDef",
    "CreateVolumePermissionModificationsTypeDef",
    "ModifyVpcEndpointRequestRequestTypeDef",
    "DeleteFleetErrorItemTypeDef",
    "DeleteInstanceEventWindowResultTypeDef",
    "DeleteLaunchTemplateVersionsResponseErrorItemTypeDef",
    "FailedQueuedPurchaseDeletionTypeDef",
    "DeregisterInstanceEventNotificationAttributesRequestRequestTypeDef",
    "DeregisterInstanceEventNotificationAttributesResultTypeDef",
    "DescribeInstanceEventNotificationAttributesResultTypeDef",
    "RegisterInstanceEventNotificationAttributesResultTypeDef",
    "DeregisterTransitGatewayMulticastGroupMembersResultTypeDef",
    "DeregisterTransitGatewayMulticastGroupSourcesResultTypeDef",
    "DescribeAddressesAttributeRequestDescribeAddressesAttributePaginateTypeDef",
    "DescribeByoipCidrsRequestDescribeByoipCidrsPaginateTypeDef",
    "DescribePrincipalIdFormatRequestDescribePrincipalIdFormatPaginateTypeDef",
    "DescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef",
    "DescribeSpotFleetRequestsRequestDescribeSpotFleetRequestsPaginateTypeDef",
    "DescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef",
    "DescribeVpcClassicLinkDnsSupportRequestDescribeVpcClassicLinkDnsSupportPaginateTypeDef",
    "GetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef",
    "GetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef",
    "GetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef",
    "GetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef",
    "GetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef",
    "GetVpnConnectionDeviceTypesRequestGetVpnConnectionDeviceTypesPaginateTypeDef",
    "ListImagesInRecycleBinRequestListImagesInRecycleBinPaginateTypeDef",
    "ListSnapshotsInRecycleBinRequestListSnapshotsInRecycleBinPaginateTypeDef",
    "DescribeAddressesRequestRequestTypeDef",
    "DescribeAvailabilityZonesRequestRequestTypeDef",
    "DescribeBundleTasksRequestRequestTypeDef",
    "DescribeCapacityReservationFleetsRequestDescribeCapacityReservationFleetsPaginateTypeDef",
    "DescribeCapacityReservationFleetsRequestRequestTypeDef",
    "DescribeCapacityReservationsRequestDescribeCapacityReservationsPaginateTypeDef",
    "DescribeCapacityReservationsRequestRequestTypeDef",
    "DescribeCarrierGatewaysRequestDescribeCarrierGatewaysPaginateTypeDef",
    "DescribeCarrierGatewaysRequestRequestTypeDef",
    "DescribeClassicLinkInstancesRequestDescribeClassicLinkInstancesPaginateTypeDef",
    "DescribeClassicLinkInstancesRequestRequestTypeDef",
    "DescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef",
    "DescribeClientVpnAuthorizationRulesRequestRequestTypeDef",
    "DescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef",
    "DescribeClientVpnConnectionsRequestRequestTypeDef",
    "DescribeClientVpnEndpointsRequestDescribeClientVpnEndpointsPaginateTypeDef",
    "DescribeClientVpnEndpointsRequestRequestTypeDef",
    "DescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef",
    "DescribeClientVpnRoutesRequestRequestTypeDef",
    "DescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef",
    "DescribeClientVpnTargetNetworksRequestRequestTypeDef",
    "DescribeCoipPoolsRequestDescribeCoipPoolsPaginateTypeDef",
    "DescribeCoipPoolsRequestRequestTypeDef",
    "DescribeCustomerGatewaysRequestRequestTypeDef",
    "DescribeDhcpOptionsRequestDescribeDhcpOptionsPaginateTypeDef",
    "DescribeDhcpOptionsRequestRequestTypeDef",
    "DescribeEgressOnlyInternetGatewaysRequestDescribeEgressOnlyInternetGatewaysPaginateTypeDef",
    "DescribeEgressOnlyInternetGatewaysRequestRequestTypeDef",
    "DescribeElasticGpusRequestRequestTypeDef",
    "DescribeExportImageTasksRequestDescribeExportImageTasksPaginateTypeDef",
    "DescribeExportImageTasksRequestRequestTypeDef",
    "DescribeExportTasksRequestRequestTypeDef",
    "DescribeFastLaunchImagesRequestDescribeFastLaunchImagesPaginateTypeDef",
    "DescribeFastLaunchImagesRequestRequestTypeDef",
    "DescribeFastSnapshotRestoresRequestDescribeFastSnapshotRestoresPaginateTypeDef",
    "DescribeFastSnapshotRestoresRequestRequestTypeDef",
    "DescribeFleetInstancesRequestRequestTypeDef",
    "DescribeFleetsRequestDescribeFleetsPaginateTypeDef",
    "DescribeFleetsRequestRequestTypeDef",
    "DescribeFlowLogsRequestDescribeFlowLogsPaginateTypeDef",
    "DescribeFlowLogsRequestRequestTypeDef",
    "DescribeFpgaImagesRequestDescribeFpgaImagesPaginateTypeDef",
    "DescribeFpgaImagesRequestRequestTypeDef",
    "DescribeHostReservationOfferingsRequestDescribeHostReservationOfferingsPaginateTypeDef",
    "DescribeHostReservationOfferingsRequestRequestTypeDef",
    "DescribeHostReservationsRequestDescribeHostReservationsPaginateTypeDef",
    "DescribeHostReservationsRequestRequestTypeDef",
    "DescribeHostsRequestDescribeHostsPaginateTypeDef",
    "DescribeHostsRequestRequestTypeDef",
    "DescribeIamInstanceProfileAssociationsRequestDescribeIamInstanceProfileAssociationsPaginateTypeDef",
    "DescribeIamInstanceProfileAssociationsRequestRequestTypeDef",
    "DescribeImagesRequestRequestTypeDef",
    "DescribeImportImageTasksRequestDescribeImportImageTasksPaginateTypeDef",
    "DescribeImportImageTasksRequestRequestTypeDef",
    "DescribeImportSnapshotTasksRequestDescribeImportSnapshotTasksPaginateTypeDef",
    "DescribeImportSnapshotTasksRequestRequestTypeDef",
    "DescribeInstanceCreditSpecificationsRequestDescribeInstanceCreditSpecificationsPaginateTypeDef",
    "DescribeInstanceCreditSpecificationsRequestRequestTypeDef",
    "DescribeInstanceEventWindowsRequestDescribeInstanceEventWindowsPaginateTypeDef",
    "DescribeInstanceEventWindowsRequestRequestTypeDef",
    "DescribeInstanceStatusRequestDescribeInstanceStatusPaginateTypeDef",
    "DescribeInstanceStatusRequestRequestTypeDef",
    "DescribeInstanceTypeOfferingsRequestDescribeInstanceTypeOfferingsPaginateTypeDef",
    "DescribeInstanceTypeOfferingsRequestRequestTypeDef",
    "DescribeInstanceTypesRequestDescribeInstanceTypesPaginateTypeDef",
    "DescribeInstanceTypesRequestRequestTypeDef",
    "DescribeInstancesRequestDescribeInstancesPaginateTypeDef",
    "DescribeInstancesRequestRequestTypeDef",
    "DescribeInternetGatewaysRequestDescribeInternetGatewaysPaginateTypeDef",
    "DescribeInternetGatewaysRequestRequestTypeDef",
    "DescribeIpamPoolsRequestDescribeIpamPoolsPaginateTypeDef",
    "DescribeIpamPoolsRequestRequestTypeDef",
    "DescribeIpamScopesRequestDescribeIpamScopesPaginateTypeDef",
    "DescribeIpamScopesRequestRequestTypeDef",
    "DescribeIpamsRequestDescribeIpamsPaginateTypeDef",
    "DescribeIpamsRequestRequestTypeDef",
    "DescribeIpv6PoolsRequestDescribeIpv6PoolsPaginateTypeDef",
    "DescribeIpv6PoolsRequestRequestTypeDef",
    "DescribeKeyPairsRequestRequestTypeDef",
    "DescribeLaunchTemplateVersionsRequestDescribeLaunchTemplateVersionsPaginateTypeDef",
    "DescribeLaunchTemplateVersionsRequestRequestTypeDef",
    "DescribeLaunchTemplatesRequestDescribeLaunchTemplatesPaginateTypeDef",
    "DescribeLaunchTemplatesRequestRequestTypeDef",
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsRequestDescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginateTypeDef",
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsRequestRequestTypeDef",
    "DescribeLocalGatewayRouteTableVpcAssociationsRequestDescribeLocalGatewayRouteTableVpcAssociationsPaginateTypeDef",
    "DescribeLocalGatewayRouteTableVpcAssociationsRequestRequestTypeDef",
    "DescribeLocalGatewayRouteTablesRequestDescribeLocalGatewayRouteTablesPaginateTypeDef",
    "DescribeLocalGatewayRouteTablesRequestRequestTypeDef",
    "DescribeLocalGatewayVirtualInterfaceGroupsRequestDescribeLocalGatewayVirtualInterfaceGroupsPaginateTypeDef",
    "DescribeLocalGatewayVirtualInterfaceGroupsRequestRequestTypeDef",
    "DescribeLocalGatewayVirtualInterfacesRequestDescribeLocalGatewayVirtualInterfacesPaginateTypeDef",
    "DescribeLocalGatewayVirtualInterfacesRequestRequestTypeDef",
    "DescribeLocalGatewaysRequestDescribeLocalGatewaysPaginateTypeDef",
    "DescribeLocalGatewaysRequestRequestTypeDef",
    "DescribeManagedPrefixListsRequestDescribeManagedPrefixListsPaginateTypeDef",
    "DescribeManagedPrefixListsRequestRequestTypeDef",
    "DescribeMovingAddressesRequestDescribeMovingAddressesPaginateTypeDef",
    "DescribeMovingAddressesRequestRequestTypeDef",
    "DescribeNatGatewaysRequestDescribeNatGatewaysPaginateTypeDef",
    "DescribeNatGatewaysRequestRequestTypeDef",
    "DescribeNetworkAclsRequestDescribeNetworkAclsPaginateTypeDef",
    "DescribeNetworkAclsRequestRequestTypeDef",
    "DescribeNetworkInsightsAccessScopeAnalysesRequestDescribeNetworkInsightsAccessScopeAnalysesPaginateTypeDef",
    "DescribeNetworkInsightsAccessScopeAnalysesRequestRequestTypeDef",
    "DescribeNetworkInsightsAccessScopesRequestDescribeNetworkInsightsAccessScopesPaginateTypeDef",
    "DescribeNetworkInsightsAccessScopesRequestRequestTypeDef",
    "DescribeNetworkInsightsAnalysesRequestDescribeNetworkInsightsAnalysesPaginateTypeDef",
    "DescribeNetworkInsightsAnalysesRequestRequestTypeDef",
    "DescribeNetworkInsightsPathsRequestDescribeNetworkInsightsPathsPaginateTypeDef",
    "DescribeNetworkInsightsPathsRequestRequestTypeDef",
    "DescribeNetworkInterfacePermissionsRequestDescribeNetworkInterfacePermissionsPaginateTypeDef",
    "DescribeNetworkInterfacePermissionsRequestRequestTypeDef",
    "DescribeNetworkInterfacesRequestDescribeNetworkInterfacesPaginateTypeDef",
    "DescribeNetworkInterfacesRequestRequestTypeDef",
    "DescribePlacementGroupsRequestRequestTypeDef",
    "DescribePrefixListsRequestDescribePrefixListsPaginateTypeDef",
    "DescribePrefixListsRequestRequestTypeDef",
    "DescribePublicIpv4PoolsRequestDescribePublicIpv4PoolsPaginateTypeDef",
    "DescribePublicIpv4PoolsRequestRequestTypeDef",
    "DescribeRegionsRequestRequestTypeDef",
    "DescribeReplaceRootVolumeTasksRequestDescribeReplaceRootVolumeTasksPaginateTypeDef",
    "DescribeReplaceRootVolumeTasksRequestRequestTypeDef",
    "DescribeReservedInstancesListingsRequestRequestTypeDef",
    "DescribeReservedInstancesModificationsRequestDescribeReservedInstancesModificationsPaginateTypeDef",
    "DescribeReservedInstancesModificationsRequestRequestTypeDef",
    "DescribeReservedInstancesOfferingsRequestDescribeReservedInstancesOfferingsPaginateTypeDef",
    "DescribeReservedInstancesOfferingsRequestRequestTypeDef",
    "DescribeReservedInstancesRequestRequestTypeDef",
    "DescribeRouteTablesRequestDescribeRouteTablesPaginateTypeDef",
    "DescribeRouteTablesRequestRequestTypeDef",
    "DescribeSecurityGroupRulesRequestDescribeSecurityGroupRulesPaginateTypeDef",
    "DescribeSecurityGroupRulesRequestRequestTypeDef",
    "DescribeSecurityGroupsRequestDescribeSecurityGroupsPaginateTypeDef",
    "DescribeSecurityGroupsRequestRequestTypeDef",
    "DescribeSnapshotTierStatusRequestDescribeSnapshotTierStatusPaginateTypeDef",
    "DescribeSnapshotTierStatusRequestRequestTypeDef",
    "DescribeSnapshotsRequestDescribeSnapshotsPaginateTypeDef",
    "DescribeSnapshotsRequestRequestTypeDef",
    "DescribeSpotInstanceRequestsRequestDescribeSpotInstanceRequestsPaginateTypeDef",
    "DescribeSpotInstanceRequestsRequestRequestTypeDef",
    "DescribeSpotPriceHistoryRequestDescribeSpotPriceHistoryPaginateTypeDef",
    "DescribeSpotPriceHistoryRequestRequestTypeDef",
    "DescribeStoreImageTasksRequestDescribeStoreImageTasksPaginateTypeDef",
    "DescribeStoreImageTasksRequestRequestTypeDef",
    "DescribeSubnetsRequestDescribeSubnetsPaginateTypeDef",
    "DescribeSubnetsRequestRequestTypeDef",
    "DescribeTagsRequestDescribeTagsPaginateTypeDef",
    "DescribeTagsRequestRequestTypeDef",
    "DescribeTrafficMirrorFiltersRequestDescribeTrafficMirrorFiltersPaginateTypeDef",
    "DescribeTrafficMirrorFiltersRequestRequestTypeDef",
    "DescribeTrafficMirrorSessionsRequestDescribeTrafficMirrorSessionsPaginateTypeDef",
    "DescribeTrafficMirrorSessionsRequestRequestTypeDef",
    "DescribeTrafficMirrorTargetsRequestDescribeTrafficMirrorTargetsPaginateTypeDef",
    "DescribeTrafficMirrorTargetsRequestRequestTypeDef",
    "DescribeTransitGatewayAttachmentsRequestDescribeTransitGatewayAttachmentsPaginateTypeDef",
    "DescribeTransitGatewayAttachmentsRequestRequestTypeDef",
    "DescribeTransitGatewayConnectPeersRequestDescribeTransitGatewayConnectPeersPaginateTypeDef",
    "DescribeTransitGatewayConnectPeersRequestRequestTypeDef",
    "DescribeTransitGatewayConnectsRequestDescribeTransitGatewayConnectsPaginateTypeDef",
    "DescribeTransitGatewayConnectsRequestRequestTypeDef",
    "DescribeTransitGatewayMulticastDomainsRequestDescribeTransitGatewayMulticastDomainsPaginateTypeDef",
    "DescribeTransitGatewayMulticastDomainsRequestRequestTypeDef",
    "DescribeTransitGatewayPeeringAttachmentsRequestDescribeTransitGatewayPeeringAttachmentsPaginateTypeDef",
    "DescribeTransitGatewayPeeringAttachmentsRequestRequestTypeDef",
    "DescribeTransitGatewayRouteTablesRequestDescribeTransitGatewayRouteTablesPaginateTypeDef",
    "DescribeTransitGatewayRouteTablesRequestRequestTypeDef",
    "DescribeTransitGatewayVpcAttachmentsRequestDescribeTransitGatewayVpcAttachmentsPaginateTypeDef",
    "DescribeTransitGatewayVpcAttachmentsRequestRequestTypeDef",
    "DescribeTransitGatewaysRequestDescribeTransitGatewaysPaginateTypeDef",
    "DescribeTransitGatewaysRequestRequestTypeDef",
    "DescribeTrunkInterfaceAssociationsRequestDescribeTrunkInterfaceAssociationsPaginateTypeDef",
    "DescribeTrunkInterfaceAssociationsRequestRequestTypeDef",
    "DescribeVolumeStatusRequestDescribeVolumeStatusPaginateTypeDef",
    "DescribeVolumeStatusRequestRequestTypeDef",
    "DescribeVolumeStatusRequestVolumeDescribeStatusTypeDef",
    "DescribeVolumesModificationsRequestDescribeVolumesModificationsPaginateTypeDef",
    "DescribeVolumesModificationsRequestRequestTypeDef",
    "DescribeVolumesRequestDescribeVolumesPaginateTypeDef",
    "DescribeVolumesRequestRequestTypeDef",
    "DescribeVpcClassicLinkRequestRequestTypeDef",
    "DescribeVpcEndpointConnectionNotificationsRequestDescribeVpcEndpointConnectionNotificationsPaginateTypeDef",
    "DescribeVpcEndpointConnectionNotificationsRequestRequestTypeDef",
    "DescribeVpcEndpointConnectionsRequestDescribeVpcEndpointConnectionsPaginateTypeDef",
    "DescribeVpcEndpointConnectionsRequestRequestTypeDef",
    "DescribeVpcEndpointServiceConfigurationsRequestDescribeVpcEndpointServiceConfigurationsPaginateTypeDef",
    "DescribeVpcEndpointServiceConfigurationsRequestRequestTypeDef",
    "DescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef",
    "DescribeVpcEndpointServicePermissionsRequestRequestTypeDef",
    "DescribeVpcEndpointServicesRequestDescribeVpcEndpointServicesPaginateTypeDef",
    "DescribeVpcEndpointServicesRequestRequestTypeDef",
    "DescribeVpcEndpointsRequestDescribeVpcEndpointsPaginateTypeDef",
    "DescribeVpcEndpointsRequestRequestTypeDef",
    "DescribeVpcPeeringConnectionsRequestDescribeVpcPeeringConnectionsPaginateTypeDef",
    "DescribeVpcPeeringConnectionsRequestRequestTypeDef",
    "DescribeVpcsRequestDescribeVpcsPaginateTypeDef",
    "DescribeVpcsRequestRequestTypeDef",
    "DescribeVpnConnectionsRequestRequestTypeDef",
    "DescribeVpnGatewaysRequestRequestTypeDef",
    "ExportTransitGatewayRoutesRequestRequestTypeDef",
    "GetCoipPoolUsageRequestRequestTypeDef",
    "GetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef",
    "GetIpamPoolAllocationsRequestRequestTypeDef",
    "GetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef",
    "GetIpamPoolCidrsRequestRequestTypeDef",
    "GetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef",
    "GetIpamResourceCidrsRequestRequestTypeDef",
    "GetSubnetCidrReservationsRequestRequestTypeDef",
    "GetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef",
    "GetTransitGatewayAttachmentPropagationsRequestRequestTypeDef",
    "GetTransitGatewayMulticastDomainAssociationsRequestGetTransitGatewayMulticastDomainAssociationsPaginateTypeDef",
    "GetTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef",
    "GetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef",
    "GetTransitGatewayPrefixListReferencesRequestRequestTypeDef",
    "GetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef",
    "GetTransitGatewayRouteTableAssociationsRequestRequestTypeDef",
    "GetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef",
    "GetTransitGatewayRouteTablePropagationsRequestRequestTypeDef",
    "SearchLocalGatewayRoutesRequestRequestTypeDef",
    "SearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef",
    "SearchTransitGatewayMulticastGroupsRequestRequestTypeDef",
    "SearchTransitGatewayMulticastGroupsRequestSearchTransitGatewayMulticastGroupsPaginateTypeDef",
    "SearchTransitGatewayRoutesRequestRequestTypeDef",
    "DescribeAggregateIdFormatResultTypeDef",
    "DescribeIdFormatResultTypeDef",
    "DescribeIdentityIdFormatResultTypeDef",
    "PrincipalIdFormatTypeDef",
    "DescribeBundleTasksRequestBundleTaskCompleteWaitTypeDef",
    "DescribeConversionTasksRequestConversionTaskCancelledWaitTypeDef",
    "DescribeConversionTasksRequestConversionTaskCompletedWaitTypeDef",
    "DescribeConversionTasksRequestConversionTaskDeletedWaitTypeDef",
    "DescribeCustomerGatewaysRequestCustomerGatewayAvailableWaitTypeDef",
    "DescribeExportTasksRequestExportTaskCancelledWaitTypeDef",
    "DescribeExportTasksRequestExportTaskCompletedWaitTypeDef",
    "DescribeImagesRequestImageAvailableWaitTypeDef",
    "DescribeImagesRequestImageExistsWaitTypeDef",
    "DescribeInstanceStatusRequestInstanceStatusOkWaitTypeDef",
    "DescribeInstanceStatusRequestSystemStatusOkWaitTypeDef",
    "DescribeInstancesRequestInstanceExistsWaitTypeDef",
    "DescribeInstancesRequestInstanceRunningWaitTypeDef",
    "DescribeInstancesRequestInstanceStoppedWaitTypeDef",
    "DescribeInstancesRequestInstanceTerminatedWaitTypeDef",
    "DescribeInternetGatewaysRequestInternetGatewayExistsWaitTypeDef",
    "DescribeKeyPairsRequestKeyPairExistsWaitTypeDef",
    "DescribeNatGatewaysRequestNatGatewayAvailableWaitTypeDef",
    "DescribeNatGatewaysRequestNatGatewayDeletedWaitTypeDef",
    "DescribeNetworkInterfacesRequestNetworkInterfaceAvailableWaitTypeDef",
    "DescribeSecurityGroupsRequestSecurityGroupExistsWaitTypeDef",
    "DescribeSnapshotsRequestSnapshotCompletedWaitTypeDef",
    "DescribeSpotInstanceRequestsRequestSpotInstanceRequestFulfilledWaitTypeDef",
    "DescribeSubnetsRequestSubnetAvailableWaitTypeDef",
    "DescribeVolumesRequestVolumeAvailableWaitTypeDef",
    "DescribeVolumesRequestVolumeDeletedWaitTypeDef",
    "DescribeVolumesRequestVolumeInUseWaitTypeDef",
    "DescribeVpcPeeringConnectionsRequestVpcPeeringConnectionDeletedWaitTypeDef",
    "DescribeVpcPeeringConnectionsRequestVpcPeeringConnectionExistsWaitTypeDef",
    "DescribeVpcsRequestVpcAvailableWaitTypeDef",
    "DescribeVpcsRequestVpcExistsWaitTypeDef",
    "DescribeVpnConnectionsRequestVpnConnectionAvailableWaitTypeDef",
    "DescribeVpnConnectionsRequestVpnConnectionDeletedWaitTypeDef",
    "GetPasswordDataRequestPasswordDataAvailableWaitTypeDef",
    "DescribeFastLaunchImagesSuccessItemTypeDef",
    "DisableFastLaunchResultTypeDef",
    "EnableFastLaunchResultTypeDef",
    "DescribeFastSnapshotRestoresResultTypeDef",
    "DescribeHostReservationOfferingsResultTypeDef",
    "DescribeInstanceCreditSpecificationsResultTypeDef",
    "DescribeInstanceTypeOfferingsResultTypeDef",
    "DescribeMovingAddressesResultTypeDef",
    "DescribeNetworkInterfaceAttributeResultTypeDef",
    "DescribePrefixListsResultTypeDef",
    "DescribeRegionsResultTypeDef",
    "DescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef",
    "DescribeScheduledInstanceAvailabilityRequestRequestTypeDef",
    "DescribeScheduledInstancesRequestDescribeScheduledInstancesPaginateTypeDef",
    "DescribeScheduledInstancesRequestRequestTypeDef",
    "DescribeSecurityGroupReferencesResultTypeDef",
    "DescribeSnapshotAttributeResultTypeDef",
    "DescribeVolumeAttributeResultTypeDef",
    "DescribeSpotPriceHistoryResultTypeDef",
    "DescribeStoreImageTasksResultTypeDef",
    "DescribeTagsResultTypeDef",
    "DescribeVolumesModificationsResultTypeDef",
    "ModifyVolumeResultTypeDef",
    "FlowLogTypeDef",
    "DisableFastSnapshotRestoreStateErrorItemTypeDef",
    "DisableTransitGatewayRouteTablePropagationResultTypeDef",
    "EnableTransitGatewayRouteTablePropagationResultTypeDef",
    "DiskImageTypeDef",
    "ImportVolumeRequestRequestTypeDef",
    "ImportInstanceVolumeDetailItemTypeDef",
    "ImportVolumeTaskDetailsTypeDef",
    "InstanceStorageInfoTypeDef",
    "VpcEndpointConnectionTypeDef",
    "ModifyClientVpnEndpointRequestRequestTypeDef",
    "EbsInfoTypeDef",
    "InstanceBlockDeviceMappingSpecificationTypeDef",
    "InstanceBlockDeviceMappingTypeDef",
    "EgressOnlyInternetGatewayTypeDef",
    "InternetGatewayTypeDef",
    "ElasticGpusTypeDef",
    "EnableFastLaunchRequestRequestTypeDef",
    "EnableFastSnapshotRestoreStateErrorItemTypeDef",
    "HistoryRecordEntryTypeDef",
    "HistoryRecordTypeDef",
    "ExportImageResultTypeDef",
    "ExportImageTaskTypeDef",
    "ExportTaskTypeDef",
    "FleetSpotMaintenanceStrategiesRequestTypeDef",
    "FleetSpotMaintenanceStrategiesTypeDef",
    "FpgaDeviceInfoTypeDef",
    "FpgaImageAttributeTypeDef",
    "FpgaImageTypeDef",
    "GetAssociatedIpv6PoolCidrsResultTypeDef",
    "GetCapacityReservationUsageResultTypeDef",
    "GetDefaultCreditSpecificationResultTypeDef",
    "ModifyDefaultCreditSpecificationResultTypeDef",
    "GetHostReservationPurchasePreviewResultTypeDef",
    "PurchaseHostReservationResultTypeDef",
    "GetInstanceTypesFromInstanceRequirementsResultTypeDef",
    "GetIpamAddressHistoryResultTypeDef",
    "GetManagedPrefixListAssociationsResultTypeDef",
    "GetManagedPrefixListEntriesResultTypeDef",
    "ReservedInstanceReservationValueTypeDef",
    "GetSpotPlacementScoresResultTypeDef",
    "GetTransitGatewayAttachmentPropagationsResultTypeDef",
    "GetTransitGatewayRouteTableAssociationsResultTypeDef",
    "GetTransitGatewayRouteTablePropagationsResultTypeDef",
    "GetVpnConnectionDeviceTypesResultTypeDef",
    "GpuDeviceInfoTypeDef",
    "IamInstanceProfileAssociationTypeDef",
    "LaunchPermissionModificationsTypeDef",
    "ImageDiskContainerTypeDef",
    "SnapshotDiskContainerTypeDef",
    "ListImagesInRecycleBinResultTypeDef",
    "ImportInstanceLaunchSpecificationTypeDef",
    "InferenceAcceleratorInfoTypeDef",
    "ModifyInstanceCreditSpecificationRequestRequestTypeDef",
    "LaunchTemplateInstanceNetworkInterfaceSpecificationRequestTypeDef",
    "InstanceMarketOptionsRequestTypeDef",
    "ModifyInstanceMetadataOptionsResultTypeDef",
    "InstanceMonitoringTypeDef",
    "InstancePrivateIpAddressTypeDef",
    "InstanceRequirementsRequestTypeDef",
    "InstanceRequirementsTypeDef",
    "InstanceStateChangeTypeDef",
    "InstanceStatusSummaryTypeDef",
    "ModifyInstanceEventStartTimeResultTypeDef",
    "IpPermissionTypeDef",
    "StaleIpPermissionTypeDef",
    "ProvisionIpamPoolCidrRequestRequestTypeDef",
    "IpamTypeDef",
    "IpamPoolCidrTypeDef",
    "IpamPoolTypeDef",
    "IpamResourceCidrTypeDef",
    "Ipv6PoolTypeDef",
    "LaunchTemplateInstanceNetworkInterfaceSpecificationTypeDef",
    "LaunchTemplateBlockDeviceMappingRequestTypeDef",
    "LaunchTemplateBlockDeviceMappingTypeDef",
    "LaunchTemplateInstanceMarketOptionsRequestTypeDef",
    "LaunchTemplateInstanceMarketOptionsTypeDef",
    "ListSnapshotsInRecycleBinResultTypeDef",
    "LoadPermissionModificationsTypeDef",
    "ModifyIpamRequestRequestTypeDef",
    "ModifyManagedPrefixListRequestRequestTypeDef",
    "ModifyNetworkInterfaceAttributeRequestNetworkInterfaceModifyAttributeTypeDef",
    "ModifyNetworkInterfaceAttributeRequestRequestTypeDef",
    "ModifyReservedInstancesRequestRequestTypeDef",
    "ReservedInstancesModificationResultTypeDef",
    "ModifyTransitGatewayRequestRequestTypeDef",
    "ModifyTransitGatewayVpcAttachmentRequestRequestTypeDef",
    "ModifyVpcPeeringConnectionOptionsRequestRequestTypeDef",
    "ModifyVpcPeeringConnectionOptionsResultTypeDef",
    "ModifyVpnTunnelOptionsSpecificationTypeDef",
    "VpnTunnelOptionsSpecificationTypeDef",
    "NatGatewayTypeDef",
    "NetworkInfoTypeDef",
    "NetworkInterfacePrivateIpAddressTypeDef",
    "NetworkInterfacePermissionTypeDef",
    "PathStatementRequestTypeDef",
    "ThroughResourcesStatementRequestTypeDef",
    "PathStatementTypeDef",
    "ThroughResourcesStatementTypeDef",
    "TransitGatewayPeeringAttachmentTypeDef",
    "TunnelOptionTypeDef",
    "ReservedInstancesListingTypeDef",
    "ProvisionPublicIpv4PoolCidrResultTypeDef",
    "PublicIpv4PoolTypeDef",
    "PurchaseScheduledInstancesRequestRequestTypeDef",
    "PurchaseReservedInstancesOfferingRequestRequestTypeDef",
    "ReservedInstancesOfferingTypeDef",
    "ReservedInstancesTypeDef",
    "SecurityGroupRuleTypeDef",
    "RegisterInstanceEventNotificationAttributesRequestRequestTypeDef",
    "RegisterTransitGatewayMulticastGroupMembersResultTypeDef",
    "RegisterTransitGatewayMulticastGroupSourcesResultTypeDef",
    "StorageTypeDef",
    "ScheduledInstanceAvailabilityTypeDef",
    "ScheduledInstanceTypeDef",
    "ScheduledInstancesBlockDeviceMappingTypeDef",
    "ScheduledInstancesNetworkInterfaceTypeDef",
    "SearchTransitGatewayMulticastGroupsResultTypeDef",
    "VpcEndpointTypeDef",
    "SecurityGroupRuleUpdateTypeDef",
    "ServiceConfigurationTypeDef",
    "ServiceDetailTypeDef",
    "SnapshotDetailTypeDef",
    "SnapshotTaskDetailTypeDef",
    "SpotMaintenanceStrategiesTypeDef",
    "SpotDatafeedSubscriptionTypeDef",
    "TransitGatewayMulticastDomainAssociationTypeDef",
    "TransitGatewayMulticastDomainAssociationsTypeDef",
    "SubnetIpv6CidrBlockAssociationTypeDef",
    "TargetReservationValueTypeDef",
    "TargetGroupsConfigTypeDef",
    "TrafficMirrorFilterRuleTypeDef",
    "TransitGatewayAttachmentTypeDef",
    "TransitGatewayConnectPeerConfigurationTypeDef",
    "TransitGatewayConnectTypeDef",
    "TransitGatewayMulticastDomainTypeDef",
    "TransitGatewayTypeDef",
    "TransitGatewayPrefixListReferenceTypeDef",
    "TransitGatewayRouteTypeDef",
    "TransitGatewayVpcAttachmentTypeDef",
    "UnsuccessfulInstanceCreditSpecificationItemTypeDef",
    "UnsuccessfulItemTypeDef",
    "ValidationWarningTypeDef",
    "VolumeResponseMetadataTypeDef",
    "VolumeTypeDef",
    "VolumeStatusInfoTypeDef",
    "VpcCidrBlockAssociationTypeDef",
    "VpcIpv6CidrBlockAssociationTypeDef",
    "VpcPeeringConnectionVpcInfoResponseMetadataTypeDef",
    "VpcPeeringConnectionVpcInfoTypeDef",
    "DescribeAccountAttributesResultTypeDef",
    "DescribeAddressesAttributeResultTypeDef",
    "ModifyAddressAttributeResultTypeDef",
    "ResetAddressAttributeResultTypeDef",
    "DescribeAddressesResultTypeDef",
    "CreateCapacityReservationResultTypeDef",
    "DescribeCapacityReservationsResultTypeDef",
    "CreateCarrierGatewayResultTypeDef",
    "DeleteCarrierGatewayResultTypeDef",
    "DescribeCarrierGatewaysResultTypeDef",
    "DescribeCoipPoolsResultTypeDef",
    "CreateCustomerGatewayResultTypeDef",
    "DescribeCustomerGatewaysResultTypeDef",
    "DescribeHostReservationsResultTypeDef",
    "AssociateInstanceEventWindowRequestRequestTypeDef",
    "InstanceEventWindowTypeDef",
    "DisassociateInstanceEventWindowRequestRequestTypeDef",
    "CreateIpamScopeResultTypeDef",
    "DeleteIpamScopeResultTypeDef",
    "DescribeIpamScopesResultTypeDef",
    "ModifyIpamScopeResultTypeDef",
    "DescribeKeyPairsResultTypeDef",
    "DeleteLaunchTemplateResultTypeDef",
    "DescribeLaunchTemplatesResultTypeDef",
    "ModifyLaunchTemplateResultTypeDef",
    "DescribeLocalGatewayRouteTablesResultTypeDef",
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResultTypeDef",
    "CreateLocalGatewayRouteTableVpcAssociationResultTypeDef",
    "DeleteLocalGatewayRouteTableVpcAssociationResultTypeDef",
    "DescribeLocalGatewayRouteTableVpcAssociationsResultTypeDef",
    "DescribeLocalGatewaysResultTypeDef",
    "DescribeLocalGatewayVirtualInterfaceGroupsResultTypeDef",
    "DescribeLocalGatewayVirtualInterfacesResultTypeDef",
    "CreateManagedPrefixListResultTypeDef",
    "DeleteManagedPrefixListResultTypeDef",
    "DescribeManagedPrefixListsResultTypeDef",
    "ModifyManagedPrefixListResultTypeDef",
    "RestoreManagedPrefixListVersionResultTypeDef",
    "DescribeNetworkInsightsAccessScopeAnalysesResultTypeDef",
    "StartNetworkInsightsAccessScopeAnalysisResultTypeDef",
    "DescribeNetworkInsightsAccessScopesResultTypeDef",
    "CreateNetworkInsightsPathResultTypeDef",
    "DescribeNetworkInsightsPathsResultTypeDef",
    "CreatePlacementGroupResultTypeDef",
    "DescribePlacementGroupsResultTypeDef",
    "CreateReplaceRootVolumeTaskResultTypeDef",
    "DescribeReplaceRootVolumeTasksResultTypeDef",
    "CreateSnapshotsResultTypeDef",
    "DescribeSnapshotTierStatusResultTypeDef",
    "DescribeSnapshotsResultTypeDef",
    "CreateSubnetCidrReservationResultTypeDef",
    "DeleteSubnetCidrReservationResultTypeDef",
    "GetSubnetCidrReservationsResultTypeDef",
    "AllocateAddressRequestRequestTypeDef",
    "AllocateHostsRequestRequestTypeDef",
    "CopySnapshotRequestRequestTypeDef",
    "CopySnapshotRequestSnapshotCopyTypeDef",
    "CreateCapacityReservationFleetRequestRequestTypeDef",
    "CreateCapacityReservationRequestRequestTypeDef",
    "CreateCarrierGatewayRequestRequestTypeDef",
    "CreateCustomerGatewayRequestRequestTypeDef",
    "CreateDhcpOptionsRequestRequestTypeDef",
    "CreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef",
    "CreateEgressOnlyInternetGatewayRequestRequestTypeDef",
    "CreateFlowLogsRequestRequestTypeDef",
    "CreateFpgaImageRequestRequestTypeDef",
    "CreateInstanceEventWindowRequestRequestTypeDef",
    "CreateInstanceExportTaskRequestRequestTypeDef",
    "CreateInternetGatewayRequestRequestTypeDef",
    "CreateInternetGatewayRequestServiceResourceCreateInternetGatewayTypeDef",
    "CreateIpamPoolRequestRequestTypeDef",
    "CreateIpamRequestRequestTypeDef",
    "CreateIpamScopeRequestRequestTypeDef",
    "CreateKeyPairRequestRequestTypeDef",
    "CreateKeyPairRequestServiceResourceCreateKeyPairTypeDef",
    "CreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef",
    "CreateManagedPrefixListRequestRequestTypeDef",
    "CreateNatGatewayRequestRequestTypeDef",
    "CreateNetworkAclRequestRequestTypeDef",
    "CreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef",
    "CreateNetworkAclRequestVpcCreateNetworkAclTypeDef",
    "CreateNetworkInsightsPathRequestRequestTypeDef",
    "CreateNetworkInterfaceRequestRequestTypeDef",
    "CreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef",
    "CreateNetworkInterfaceRequestSubnetCreateNetworkInterfaceTypeDef",
    "CreatePlacementGroupRequestRequestTypeDef",
    "CreatePlacementGroupRequestServiceResourceCreatePlacementGroupTypeDef",
    "CreatePublicIpv4PoolRequestRequestTypeDef",
    "CreateReplaceRootVolumeTaskRequestRequestTypeDef",
    "CreateRestoreImageTaskRequestRequestTypeDef",
    "CreateRouteTableRequestRequestTypeDef",
    "CreateRouteTableRequestServiceResourceCreateRouteTableTypeDef",
    "CreateRouteTableRequestVpcCreateRouteTableTypeDef",
    "CreateSecurityGroupRequestRequestTypeDef",
    "CreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef",
    "CreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef",
    "CreateSnapshotRequestRequestTypeDef",
    "CreateSnapshotRequestServiceResourceCreateSnapshotTypeDef",
    "CreateSnapshotRequestVolumeCreateSnapshotTypeDef",
    "CreateSnapshotsRequestRequestTypeDef",
    "CreateSubnetCidrReservationRequestRequestTypeDef",
    "CreateSubnetRequestRequestTypeDef",
    "CreateSubnetRequestServiceResourceCreateSubnetTypeDef",
    "CreateSubnetRequestVpcCreateSubnetTypeDef",
    "CreateTrafficMirrorFilterRequestRequestTypeDef",
    "CreateTrafficMirrorSessionRequestRequestTypeDef",
    "CreateTrafficMirrorTargetRequestRequestTypeDef",
    "CreateTransitGatewayConnectPeerRequestRequestTypeDef",
    "CreateTransitGatewayConnectRequestRequestTypeDef",
    "CreateTransitGatewayMulticastDomainRequestRequestTypeDef",
    "CreateTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    "CreateTransitGatewayRequestRequestTypeDef",
    "CreateTransitGatewayRouteTableRequestRequestTypeDef",
    "CreateTransitGatewayVpcAttachmentRequestRequestTypeDef",
    "CreateVolumeRequestRequestTypeDef",
    "CreateVolumeRequestServiceResourceCreateVolumeTypeDef",
    "CreateVpcEndpointRequestRequestTypeDef",
    "CreateVpcEndpointServiceConfigurationRequestRequestTypeDef",
    "CreateVpcPeeringConnectionRequestRequestTypeDef",
    "CreateVpcPeeringConnectionRequestServiceResourceCreateVpcPeeringConnectionTypeDef",
    "CreateVpcPeeringConnectionRequestVpcRequestVpcPeeringConnectionTypeDef",
    "CreateVpcRequestRequestTypeDef",
    "CreateVpcRequestServiceResourceCreateVpcTypeDef",
    "CreateVpnGatewayRequestRequestTypeDef",
    "ExportImageRequestRequestTypeDef",
    "ImportKeyPairRequestRequestTypeDef",
    "ImportKeyPairRequestServiceResourceImportKeyPairTypeDef",
    "ProvisionByoipCidrRequestRequestTypeDef",
    "PurchaseHostReservationRequestRequestTypeDef",
    "StartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef",
    "StartNetworkInsightsAnalysisRequestRequestTypeDef",
    "CreateTrafficMirrorSessionResultTypeDef",
    "DescribeTrafficMirrorSessionsResultTypeDef",
    "ModifyTrafficMirrorSessionResultTypeDef",
    "CreateTrafficMirrorTargetResultTypeDef",
    "DescribeTrafficMirrorTargetsResultTypeDef",
    "CreateTransitGatewayRouteTableResultTypeDef",
    "DeleteTransitGatewayRouteTableResultTypeDef",
    "DescribeTransitGatewayRouteTablesResultTypeDef",
    "AssociateTrunkInterfaceResultTypeDef",
    "DescribeTrunkInterfaceAssociationsResultTypeDef",
    "DescribeVpcClassicLinkResultTypeDef",
    "ExplanationTypeDef",
    "PathComponentTypeDef",
    "DescribeClientVpnTargetNetworksResultTypeDef",
    "RouteTableTypeDef",
    "GetFlowLogsIntegrationTemplateRequestRequestTypeDef",
    "CreateVpnGatewayResultTypeDef",
    "DescribeVpnGatewaysResultTypeDef",
    "DhcpOptionsTypeDef",
    "DescribeClientVpnAuthorizationRulesResultTypeDef",
    "DescribeAvailabilityZonesResultTypeDef",
    "HostTypeDef",
    "CreateImageRequestInstanceCreateImageTypeDef",
    "CreateImageRequestRequestTypeDef",
    "ImageAttributeTypeDef",
    "ImageTypeDef",
    "RegisterImageRequestRequestTypeDef",
    "RegisterImageRequestServiceResourceRegisterImageTypeDef",
    "CancelCapacityReservationFleetsResultTypeDef",
    "CancelSpotFleetRequestsResponseTypeDef",
    "DescribeCapacityReservationFleetsResultTypeDef",
    "ModifyInstanceCapacityReservationAttributesRequestRequestTypeDef",
    "DescribeClassicLinkInstancesResultTypeDef",
    "CreateClientVpnEndpointRequestRequestTypeDef",
    "ClientVpnEndpointTypeDef",
    "DescribeClientVpnConnectionsResultTypeDef",
    "TerminateClientVpnConnectionsResultTypeDef",
    "DescribeClientVpnRoutesResultTypeDef",
    "NetworkAclTypeDef",
    "LaunchSpecificationTypeDef",
    "RequestSpotLaunchSpecificationTypeDef",
    "ModifySnapshotAttributeRequestRequestTypeDef",
    "ModifySnapshotAttributeRequestSnapshotModifyAttributeTypeDef",
    "DeleteFleetsResultTypeDef",
    "DeleteLaunchTemplateVersionsResultTypeDef",
    "DeleteQueuedReservedInstancesResultTypeDef",
    "DescribePrincipalIdFormatResultTypeDef",
    "DescribeFastLaunchImagesResultTypeDef",
    "DescribeFlowLogsResultTypeDef",
    "DisableFastSnapshotRestoreErrorItemTypeDef",
    "ImportInstanceTaskDetailsTypeDef",
    "DescribeVpcEndpointConnectionsResultTypeDef",
    "ModifyInstanceAttributeRequestInstanceModifyAttributeTypeDef",
    "ModifyInstanceAttributeRequestRequestTypeDef",
    "InstanceAttributeTypeDef",
    "CreateEgressOnlyInternetGatewayResultTypeDef",
    "DescribeEgressOnlyInternetGatewaysResultTypeDef",
    "CreateInternetGatewayResultTypeDef",
    "DescribeInternetGatewaysResultTypeDef",
    "DescribeElasticGpusResultTypeDef",
    "EnableFastSnapshotRestoreErrorItemTypeDef",
    "DescribeFleetHistoryResultTypeDef",
    "DescribeSpotFleetRequestHistoryResponseTypeDef",
    "DescribeExportImageTasksResultTypeDef",
    "CreateInstanceExportTaskResultTypeDef",
    "DescribeExportTasksResultTypeDef",
    "SpotOptionsRequestTypeDef",
    "SpotOptionsTypeDef",
    "FpgaInfoTypeDef",
    "DescribeFpgaImageAttributeResultTypeDef",
    "ModifyFpgaImageAttributeResultTypeDef",
    "DescribeFpgaImagesResultTypeDef",
    "GpuInfoTypeDef",
    "AssociateIamInstanceProfileResultTypeDef",
    "DescribeIamInstanceProfileAssociationsResultTypeDef",
    "DisassociateIamInstanceProfileResultTypeDef",
    "ReplaceIamInstanceProfileAssociationResultTypeDef",
    "ModifyImageAttributeRequestImageModifyAttributeTypeDef",
    "ModifyImageAttributeRequestRequestTypeDef",
    "ImportImageRequestRequestTypeDef",
    "ImportSnapshotRequestRequestTypeDef",
    "ImportInstanceRequestRequestTypeDef",
    "RunInstancesRequestRequestTypeDef",
    "RunInstancesRequestServiceResourceCreateInstancesTypeDef",
    "RunInstancesRequestSubnetCreateInstancesTypeDef",
    "MonitorInstancesResultTypeDef",
    "UnmonitorInstancesResultTypeDef",
    "InstanceNetworkInterfaceTypeDef",
    "FleetLaunchTemplateOverridesRequestTypeDef",
    "GetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef",
    "GetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef",
    "InstanceRequirementsWithMetadataRequestTypeDef",
    "FleetLaunchTemplateOverridesTypeDef",
    "LaunchTemplateOverridesTypeDef",
    "SpotFleetLaunchSpecificationTypeDef",
    "StartInstancesResultTypeDef",
    "StopInstancesResultTypeDef",
    "TerminateInstancesResultTypeDef",
    "InstanceStatusTypeDef",
    "AuthorizeSecurityGroupEgressRequestRequestTypeDef",
    "AuthorizeSecurityGroupEgressRequestSecurityGroupAuthorizeEgressTypeDef",
    "AuthorizeSecurityGroupIngressRequestRequestTypeDef",
    "AuthorizeSecurityGroupIngressRequestSecurityGroupAuthorizeIngressTypeDef",
    "RevokeSecurityGroupEgressRequestRequestTypeDef",
    "RevokeSecurityGroupEgressRequestSecurityGroupRevokeEgressTypeDef",
    "RevokeSecurityGroupEgressResultTypeDef",
    "RevokeSecurityGroupIngressRequestRequestTypeDef",
    "RevokeSecurityGroupIngressRequestSecurityGroupRevokeIngressTypeDef",
    "RevokeSecurityGroupIngressResultTypeDef",
    "SecurityGroupTypeDef",
    "UpdateSecurityGroupRuleDescriptionsEgressRequestRequestTypeDef",
    "UpdateSecurityGroupRuleDescriptionsIngressRequestRequestTypeDef",
    "StaleSecurityGroupTypeDef",
    "CreateIpamResultTypeDef",
    "DeleteIpamResultTypeDef",
    "DescribeIpamsResultTypeDef",
    "ModifyIpamResultTypeDef",
    "DeprovisionIpamPoolCidrResultTypeDef",
    "GetIpamPoolCidrsResultTypeDef",
    "ProvisionIpamPoolCidrResultTypeDef",
    "CreateIpamPoolResultTypeDef",
    "DeleteIpamPoolResultTypeDef",
    "DescribeIpamPoolsResultTypeDef",
    "ModifyIpamPoolResultTypeDef",
    "GetIpamResourceCidrsResultTypeDef",
    "ModifyIpamResourceCidrResultTypeDef",
    "DescribeIpv6PoolsResultTypeDef",
    "RequestLaunchTemplateDataTypeDef",
    "ResponseLaunchTemplateDataTypeDef",
    "ModifyFpgaImageAttributeRequestRequestTypeDef",
    "ReservedInstancesModificationTypeDef",
    "ModifyVpnTunnelOptionsRequestRequestTypeDef",
    "VpnConnectionOptionsSpecificationTypeDef",
    "CreateNatGatewayResultTypeDef",
    "DescribeNatGatewaysResultTypeDef",
    "NetworkInterfaceTypeDef",
    "CreateNetworkInterfacePermissionResultTypeDef",
    "DescribeNetworkInterfacePermissionsResultTypeDef",
    "AccessScopePathRequestTypeDef",
    "AccessScopePathTypeDef",
    "AcceptTransitGatewayPeeringAttachmentResultTypeDef",
    "CreateTransitGatewayPeeringAttachmentResultTypeDef",
    "DeleteTransitGatewayPeeringAttachmentResultTypeDef",
    "DescribeTransitGatewayPeeringAttachmentsResultTypeDef",
    "RejectTransitGatewayPeeringAttachmentResultTypeDef",
    "VpnConnectionOptionsTypeDef",
    "CancelReservedInstancesListingResultTypeDef",
    "CreateReservedInstancesListingResultTypeDef",
    "DescribeReservedInstancesListingsResultTypeDef",
    "DescribePublicIpv4PoolsResultTypeDef",
    "DescribeReservedInstancesOfferingsResultTypeDef",
    "DescribeReservedInstancesResultTypeDef",
    "AuthorizeSecurityGroupEgressResultTypeDef",
    "AuthorizeSecurityGroupIngressResultTypeDef",
    "DescribeSecurityGroupRulesResultTypeDef",
    "BundleInstanceRequestRequestTypeDef",
    "BundleTaskTypeDef",
    "DescribeScheduledInstanceAvailabilityResultTypeDef",
    "DescribeScheduledInstancesResultTypeDef",
    "PurchaseScheduledInstancesResultTypeDef",
    "ScheduledInstancesLaunchSpecificationTypeDef",
    "CreateVpcEndpointResultTypeDef",
    "DescribeVpcEndpointsResultTypeDef",
    "ModifySecurityGroupRulesRequestRequestTypeDef",
    "CreateVpcEndpointServiceConfigurationResultTypeDef",
    "DescribeVpcEndpointServiceConfigurationsResultTypeDef",
    "DescribeVpcEndpointServicesResultTypeDef",
    "ImportImageResultTypeDef",
    "ImportImageTaskTypeDef",
    "ImportSnapshotResultTypeDef",
    "ImportSnapshotTaskTypeDef",
    "CreateSpotDatafeedSubscriptionResultTypeDef",
    "DescribeSpotDatafeedSubscriptionResultTypeDef",
    "GetTransitGatewayMulticastDomainAssociationsResultTypeDef",
    "AcceptTransitGatewayMulticastDomainAssociationsResultTypeDef",
    "AssociateTransitGatewayMulticastDomainResultTypeDef",
    "DisassociateTransitGatewayMulticastDomainResultTypeDef",
    "RejectTransitGatewayMulticastDomainAssociationsResultTypeDef",
    "AssociateSubnetCidrBlockResultTypeDef",
    "DisassociateSubnetCidrBlockResultTypeDef",
    "SubnetTypeDef",
    "GetReservedInstancesExchangeQuoteResultTypeDef",
    "LoadBalancersConfigTypeDef",
    "CreateTrafficMirrorFilterRuleResultTypeDef",
    "ModifyTrafficMirrorFilterRuleResultTypeDef",
    "TrafficMirrorFilterTypeDef",
    "DescribeTransitGatewayAttachmentsResultTypeDef",
    "TransitGatewayConnectPeerTypeDef",
    "CreateTransitGatewayConnectResultTypeDef",
    "DeleteTransitGatewayConnectResultTypeDef",
    "DescribeTransitGatewayConnectsResultTypeDef",
    "CreateTransitGatewayMulticastDomainResultTypeDef",
    "DeleteTransitGatewayMulticastDomainResultTypeDef",
    "DescribeTransitGatewayMulticastDomainsResultTypeDef",
    "CreateTransitGatewayResultTypeDef",
    "DeleteTransitGatewayResultTypeDef",
    "DescribeTransitGatewaysResultTypeDef",
    "ModifyTransitGatewayResultTypeDef",
    "CreateTransitGatewayPrefixListReferenceResultTypeDef",
    "DeleteTransitGatewayPrefixListReferenceResultTypeDef",
    "GetTransitGatewayPrefixListReferencesResultTypeDef",
    "ModifyTransitGatewayPrefixListReferenceResultTypeDef",
    "CreateTransitGatewayRouteResultTypeDef",
    "DeleteTransitGatewayRouteResultTypeDef",
    "ReplaceTransitGatewayRouteResultTypeDef",
    "SearchTransitGatewayRoutesResultTypeDef",
    "AcceptTransitGatewayVpcAttachmentResultTypeDef",
    "CreateTransitGatewayVpcAttachmentResultTypeDef",
    "DeleteTransitGatewayVpcAttachmentResultTypeDef",
    "DescribeTransitGatewayVpcAttachmentsResultTypeDef",
    "ModifyTransitGatewayVpcAttachmentResultTypeDef",
    "RejectTransitGatewayVpcAttachmentResultTypeDef",
    "ModifyInstanceCreditSpecificationResultTypeDef",
    "AcceptVpcEndpointConnectionsResultTypeDef",
    "CreateFlowLogsResultTypeDef",
    "DeleteFlowLogsResultTypeDef",
    "DeleteVpcEndpointConnectionNotificationsResultTypeDef",
    "DeleteVpcEndpointServiceConfigurationsResultTypeDef",
    "DeleteVpcEndpointsResultTypeDef",
    "ModifyHostsResultTypeDef",
    "RejectVpcEndpointConnectionsResultTypeDef",
    "ReleaseHostsResultTypeDef",
    "CreateLaunchTemplateResultTypeDef",
    "DescribeVolumesResultTypeDef",
    "VolumeStatusItemTypeDef",
    "AssociateVpcCidrBlockResultTypeDef",
    "DisassociateVpcCidrBlockResultTypeDef",
    "VpcTypeDef",
    "VpcPeeringConnectionTypeDef",
    "AssociateInstanceEventWindowResultTypeDef",
    "CreateInstanceEventWindowResultTypeDef",
    "DescribeInstanceEventWindowsResultTypeDef",
    "DisassociateInstanceEventWindowResultTypeDef",
    "ModifyInstanceEventWindowResultTypeDef",
    "AccessScopeAnalysisFindingTypeDef",
    "NetworkInsightsAnalysisTypeDef",
    "CreateRouteTableResultTypeDef",
    "DescribeRouteTablesResultTypeDef",
    "CreateDhcpOptionsResultTypeDef",
    "DescribeDhcpOptionsResultTypeDef",
    "DescribeHostsResultTypeDef",
    "DescribeImagesResultTypeDef",
    "DescribeClientVpnEndpointsResultTypeDef",
    "CreateNetworkAclResultTypeDef",
    "DescribeNetworkAclsResultTypeDef",
    "SpotInstanceRequestTypeDef",
    "RequestSpotInstancesRequestRequestTypeDef",
    "DisableFastSnapshotRestoresResultTypeDef",
    "ConversionTaskTypeDef",
    "EnableFastSnapshotRestoresResultTypeDef",
    "InstanceTypeInfoTypeDef",
    "InstanceTypeDef",
    "FleetLaunchTemplateConfigRequestTypeDef",
    "GetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef",
    "GetSpotPlacementScoresRequestRequestTypeDef",
    "FleetLaunchTemplateConfigTypeDef",
    "LaunchTemplateAndOverridesResponseTypeDef",
    "LaunchTemplateConfigTypeDef",
    "DescribeInstanceStatusResultTypeDef",
    "DescribeSecurityGroupsResultTypeDef",
    "DescribeStaleSecurityGroupsResultTypeDef",
    "CreateLaunchTemplateRequestRequestTypeDef",
    "CreateLaunchTemplateVersionRequestRequestTypeDef",
    "GetLaunchTemplateDataResultTypeDef",
    "LaunchTemplateVersionTypeDef",
    "DescribeReservedInstancesModificationsResultTypeDef",
    "CreateVpnConnectionRequestRequestTypeDef",
    "CreateNetworkInterfaceResultTypeDef",
    "DescribeNetworkInterfacesResultTypeDef",
    "CreateNetworkInsightsAccessScopeRequestRequestTypeDef",
    "NetworkInsightsAccessScopeContentTypeDef",
    "VpnConnectionTypeDef",
    "BundleInstanceResultTypeDef",
    "CancelBundleTaskResultTypeDef",
    "DescribeBundleTasksResultTypeDef",
    "RunScheduledInstancesRequestRequestTypeDef",
    "DescribeImportImageTasksResultTypeDef",
    "DescribeImportSnapshotTasksResultTypeDef",
    "CreateDefaultSubnetResultTypeDef",
    "CreateSubnetResultTypeDef",
    "DescribeSubnetsResultTypeDef",
    "CreateTrafficMirrorFilterResultTypeDef",
    "DescribeTrafficMirrorFiltersResultTypeDef",
    "ModifyTrafficMirrorFilterNetworkServicesResultTypeDef",
    "CreateTransitGatewayConnectPeerResultTypeDef",
    "DeleteTransitGatewayConnectPeerResultTypeDef",
    "DescribeTransitGatewayConnectPeersResultTypeDef",
    "DescribeVolumeStatusResultTypeDef",
    "CreateDefaultVpcResultTypeDef",
    "CreateVpcResultTypeDef",
    "DescribeVpcsResultTypeDef",
    "AcceptVpcPeeringConnectionResultTypeDef",
    "CreateVpcPeeringConnectionResultTypeDef",
    "DescribeVpcPeeringConnectionsResultTypeDef",
    "GetNetworkInsightsAccessScopeAnalysisFindingsResultTypeDef",
    "DescribeNetworkInsightsAnalysesResultTypeDef",
    "StartNetworkInsightsAnalysisResultTypeDef",
    "DescribeSpotInstanceRequestsResultTypeDef",
    "RequestSpotInstancesResultTypeDef",
    "DescribeConversionTasksResultTypeDef",
    "ImportInstanceResultTypeDef",
    "ImportVolumeResultTypeDef",
    "DescribeInstanceTypesResultTypeDef",
    "ReservationResponseMetadataTypeDef",
    "ReservationTypeDef",
    "CreateFleetRequestRequestTypeDef",
    "ModifyFleetRequestRequestTypeDef",
    "CreateFleetErrorTypeDef",
    "CreateFleetInstanceTypeDef",
    "DescribeFleetErrorTypeDef",
    "DescribeFleetsInstancesTypeDef",
    "ModifySpotFleetRequestRequestRequestTypeDef",
    "SpotFleetRequestConfigDataTypeDef",
    "CreateLaunchTemplateVersionResultTypeDef",
    "DescribeLaunchTemplateVersionsResultTypeDef",
    "CreateNetworkInsightsAccessScopeResultTypeDef",
    "GetNetworkInsightsAccessScopeContentResultTypeDef",
    "CreateVpnConnectionResultTypeDef",
    "DescribeVpnConnectionsResultTypeDef",
    "ModifyVpnConnectionOptionsResultTypeDef",
    "ModifyVpnConnectionResultTypeDef",
    "ModifyVpnTunnelCertificateResultTypeDef",
    "ModifyVpnTunnelOptionsResultTypeDef",
    "DescribeInstancesResultTypeDef",
    "CreateFleetResultTypeDef",
    "FleetDataTypeDef",
    "RequestSpotFleetRequestRequestTypeDef",
    "SpotFleetRequestConfigTypeDef",
    "DescribeFleetsResultTypeDef",
    "DescribeSpotFleetRequestsResponseTypeDef",
)

AcceleratorCountRequestTypeDef = TypedDict(
    "AcceleratorCountRequestTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

AcceleratorCountTypeDef = TypedDict(
    "AcceleratorCountTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

AcceleratorTotalMemoryMiBRequestTypeDef = TypedDict(
    "AcceleratorTotalMemoryMiBRequestTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

AcceleratorTotalMemoryMiBTypeDef = TypedDict(
    "AcceleratorTotalMemoryMiBTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

_RequiredTargetConfigurationRequestTypeDef = TypedDict(
    "_RequiredTargetConfigurationRequestTypeDef",
    {
        "OfferingId": str,
    },
)
_OptionalTargetConfigurationRequestTypeDef = TypedDict(
    "_OptionalTargetConfigurationRequestTypeDef",
    {
        "InstanceCount": int,
    },
    total=False,
)


class TargetConfigurationRequestTypeDef(
    _RequiredTargetConfigurationRequestTypeDef, _OptionalTargetConfigurationRequestTypeDef
):
    pass


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

AcceptTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef = TypedDict(
    "AcceptTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "TransitGatewayAttachmentId": str,
        "SubnetIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

_RequiredAcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredAcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalAcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalAcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef(
    _RequiredAcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef,
    _OptionalAcceptTransitGatewayPeeringAttachmentRequestRequestTypeDef,
):
    pass


_RequiredAcceptTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredAcceptTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalAcceptTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalAcceptTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AcceptTransitGatewayVpcAttachmentRequestRequestTypeDef(
    _RequiredAcceptTransitGatewayVpcAttachmentRequestRequestTypeDef,
    _OptionalAcceptTransitGatewayVpcAttachmentRequestRequestTypeDef,
):
    pass


_RequiredAcceptVpcEndpointConnectionsRequestRequestTypeDef = TypedDict(
    "_RequiredAcceptVpcEndpointConnectionsRequestRequestTypeDef",
    {
        "ServiceId": str,
        "VpcEndpointIds": Sequence[str],
    },
)
_OptionalAcceptVpcEndpointConnectionsRequestRequestTypeDef = TypedDict(
    "_OptionalAcceptVpcEndpointConnectionsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AcceptVpcEndpointConnectionsRequestRequestTypeDef(
    _RequiredAcceptVpcEndpointConnectionsRequestRequestTypeDef,
    _OptionalAcceptVpcEndpointConnectionsRequestRequestTypeDef,
):
    pass


AcceptVpcPeeringConnectionRequestRequestTypeDef = TypedDict(
    "AcceptVpcPeeringConnectionRequestRequestTypeDef",
    {
        "DryRun": bool,
        "VpcPeeringConnectionId": str,
    },
    total=False,
)

AcceptVpcPeeringConnectionRequestVpcPeeringConnectionAcceptTypeDef = TypedDict(
    "AcceptVpcPeeringConnectionRequestVpcPeeringConnectionAcceptTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

AccountAttributeValueTypeDef = TypedDict(
    "AccountAttributeValueTypeDef",
    {
        "AttributeValue": str,
    },
    total=False,
)

ActiveInstanceTypeDef = TypedDict(
    "ActiveInstanceTypeDef",
    {
        "InstanceId": str,
        "InstanceType": str,
        "SpotInstanceRequestId": str,
        "InstanceHealth": InstanceHealthStatusType,
    },
    total=False,
)

AddIpamOperatingRegionTypeDef = TypedDict(
    "AddIpamOperatingRegionTypeDef",
    {
        "RegionName": str,
    },
    total=False,
)

_RequiredAddPrefixListEntryTypeDef = TypedDict(
    "_RequiredAddPrefixListEntryTypeDef",
    {
        "Cidr": str,
    },
)
_OptionalAddPrefixListEntryTypeDef = TypedDict(
    "_OptionalAddPrefixListEntryTypeDef",
    {
        "Description": str,
    },
    total=False,
)


class AddPrefixListEntryTypeDef(
    _RequiredAddPrefixListEntryTypeDef, _OptionalAddPrefixListEntryTypeDef
):
    pass


AnalysisComponentTypeDef = TypedDict(
    "AnalysisComponentTypeDef",
    {
        "Id": str,
        "Arn": str,
        "Name": str,
    },
    total=False,
)

PtrUpdateStatusTypeDef = TypedDict(
    "PtrUpdateStatusTypeDef",
    {
        "Value": str,
        "Status": str,
        "Reason": str,
    },
    total=False,
)

_RequiredTagTypeDef = TypedDict(
    "_RequiredTagTypeDef",
    {
        "Key": str,
    },
)
_OptionalTagTypeDef = TypedDict(
    "_OptionalTagTypeDef",
    {
        "Value": str,
    },
    total=False,
)


class TagTypeDef(_RequiredTagTypeDef, _OptionalTagTypeDef):
    pass


_RequiredAdvertiseByoipCidrRequestRequestTypeDef = TypedDict(
    "_RequiredAdvertiseByoipCidrRequestRequestTypeDef",
    {
        "Cidr": str,
    },
)
_OptionalAdvertiseByoipCidrRequestRequestTypeDef = TypedDict(
    "_OptionalAdvertiseByoipCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AdvertiseByoipCidrRequestRequestTypeDef(
    _RequiredAdvertiseByoipCidrRequestRequestTypeDef,
    _OptionalAdvertiseByoipCidrRequestRequestTypeDef,
):
    pass


ByoipCidrTypeDef = TypedDict(
    "ByoipCidrTypeDef",
    {
        "Cidr": str,
        "Description": str,
        "StatusMessage": str,
        "State": ByoipCidrStateType,
    },
    total=False,
)

_RequiredAllocateIpamPoolCidrRequestRequestTypeDef = TypedDict(
    "_RequiredAllocateIpamPoolCidrRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalAllocateIpamPoolCidrRequestRequestTypeDef = TypedDict(
    "_OptionalAllocateIpamPoolCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Cidr": str,
        "NetmaskLength": int,
        "ClientToken": str,
        "Description": str,
        "PreviewNextCidr": bool,
        "DisallowedCidrs": Sequence[str],
    },
    total=False,
)


class AllocateIpamPoolCidrRequestRequestTypeDef(
    _RequiredAllocateIpamPoolCidrRequestRequestTypeDef,
    _OptionalAllocateIpamPoolCidrRequestRequestTypeDef,
):
    pass


IpamPoolAllocationTypeDef = TypedDict(
    "IpamPoolAllocationTypeDef",
    {
        "Cidr": str,
        "IpamPoolAllocationId": str,
        "Description": str,
        "ResourceId": str,
        "ResourceType": IpamPoolAllocationResourceTypeType,
        "ResourceRegion": str,
        "ResourceOwner": str,
    },
    total=False,
)

AllowedPrincipalTypeDef = TypedDict(
    "AllowedPrincipalTypeDef",
    {
        "PrincipalType": PrincipalTypeType,
        "Principal": str,
    },
    total=False,
)

AlternatePathHintTypeDef = TypedDict(
    "AlternatePathHintTypeDef",
    {
        "ComponentId": str,
        "ComponentArn": str,
    },
    total=False,
)

PortRangeTypeDef = TypedDict(
    "PortRangeTypeDef",
    {
        "From": int,
        "To": int,
    },
    total=False,
)

AnalysisLoadBalancerListenerTypeDef = TypedDict(
    "AnalysisLoadBalancerListenerTypeDef",
    {
        "LoadBalancerPort": int,
        "InstancePort": int,
    },
    total=False,
)

AnalysisRouteTableRouteTypeDef = TypedDict(
    "AnalysisRouteTableRouteTypeDef",
    {
        "DestinationCidr": str,
        "DestinationPrefixListId": str,
        "EgressOnlyInternetGatewayId": str,
        "GatewayId": str,
        "InstanceId": str,
        "NatGatewayId": str,
        "NetworkInterfaceId": str,
        "Origin": str,
        "TransitGatewayId": str,
        "VpcPeeringConnectionId": str,
    },
    total=False,
)

_RequiredApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef = TypedDict(
    "_RequiredApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "VpcId": str,
        "SecurityGroupIds": Sequence[str],
    },
)
_OptionalApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef = TypedDict(
    "_OptionalApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef(
    _RequiredApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef,
    _OptionalApplySecurityGroupsToClientVpnTargetNetworkRequestRequestTypeDef,
):
    pass


_RequiredAssignIpv6AddressesRequestRequestTypeDef = TypedDict(
    "_RequiredAssignIpv6AddressesRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalAssignIpv6AddressesRequestRequestTypeDef = TypedDict(
    "_OptionalAssignIpv6AddressesRequestRequestTypeDef",
    {
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[str],
        "Ipv6PrefixCount": int,
        "Ipv6Prefixes": Sequence[str],
    },
    total=False,
)


class AssignIpv6AddressesRequestRequestTypeDef(
    _RequiredAssignIpv6AddressesRequestRequestTypeDef,
    _OptionalAssignIpv6AddressesRequestRequestTypeDef,
):
    pass


AssignPrivateIpAddressesRequestNetworkInterfaceAssignPrivateIpAddressesTypeDef = TypedDict(
    "AssignPrivateIpAddressesRequestNetworkInterfaceAssignPrivateIpAddressesTypeDef",
    {
        "AllowReassignment": bool,
        "PrivateIpAddresses": Sequence[str],
        "SecondaryPrivateIpAddressCount": int,
        "Ipv4Prefixes": Sequence[str],
        "Ipv4PrefixCount": int,
    },
    total=False,
)

_RequiredAssignPrivateIpAddressesRequestRequestTypeDef = TypedDict(
    "_RequiredAssignPrivateIpAddressesRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalAssignPrivateIpAddressesRequestRequestTypeDef = TypedDict(
    "_OptionalAssignPrivateIpAddressesRequestRequestTypeDef",
    {
        "AllowReassignment": bool,
        "PrivateIpAddresses": Sequence[str],
        "SecondaryPrivateIpAddressCount": int,
        "Ipv4Prefixes": Sequence[str],
        "Ipv4PrefixCount": int,
    },
    total=False,
)


class AssignPrivateIpAddressesRequestRequestTypeDef(
    _RequiredAssignPrivateIpAddressesRequestRequestTypeDef,
    _OptionalAssignPrivateIpAddressesRequestRequestTypeDef,
):
    pass


AssignedPrivateIpAddressTypeDef = TypedDict(
    "AssignedPrivateIpAddressTypeDef",
    {
        "PrivateIpAddress": str,
    },
    total=False,
)

Ipv4PrefixSpecificationTypeDef = TypedDict(
    "Ipv4PrefixSpecificationTypeDef",
    {
        "Ipv4Prefix": str,
    },
    total=False,
)

AssociateAddressRequestClassicAddressAssociateTypeDef = TypedDict(
    "AssociateAddressRequestClassicAddressAssociateTypeDef",
    {
        "AllocationId": str,
        "InstanceId": str,
        "AllowReassociation": bool,
        "DryRun": bool,
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
    },
    total=False,
)

AssociateAddressRequestRequestTypeDef = TypedDict(
    "AssociateAddressRequestRequestTypeDef",
    {
        "AllocationId": str,
        "InstanceId": str,
        "PublicIp": str,
        "AllowReassociation": bool,
        "DryRun": bool,
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
    },
    total=False,
)

AssociateAddressRequestVpcAddressAssociateTypeDef = TypedDict(
    "AssociateAddressRequestVpcAddressAssociateTypeDef",
    {
        "InstanceId": str,
        "PublicIp": str,
        "AllowReassociation": bool,
        "DryRun": bool,
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
    },
    total=False,
)

_RequiredAssociateClientVpnTargetNetworkRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateClientVpnTargetNetworkRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "SubnetId": str,
    },
)
_OptionalAssociateClientVpnTargetNetworkRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateClientVpnTargetNetworkRequestRequestTypeDef",
    {
        "ClientToken": str,
        "DryRun": bool,
    },
    total=False,
)


class AssociateClientVpnTargetNetworkRequestRequestTypeDef(
    _RequiredAssociateClientVpnTargetNetworkRequestRequestTypeDef,
    _OptionalAssociateClientVpnTargetNetworkRequestRequestTypeDef,
):
    pass


AssociationStatusTypeDef = TypedDict(
    "AssociationStatusTypeDef",
    {
        "Code": AssociationStatusCodeType,
        "Message": str,
    },
    total=False,
)

_RequiredAssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef = TypedDict(
    "_RequiredAssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalAssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef = TypedDict(
    "_OptionalAssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef(
    _RequiredAssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef,
    _OptionalAssociateDhcpOptionsRequestDhcpOptionsAssociateWithVpcTypeDef,
):
    pass


_RequiredAssociateDhcpOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateDhcpOptionsRequestRequestTypeDef",
    {
        "DhcpOptionsId": str,
        "VpcId": str,
    },
)
_OptionalAssociateDhcpOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateDhcpOptionsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AssociateDhcpOptionsRequestRequestTypeDef(
    _RequiredAssociateDhcpOptionsRequestRequestTypeDef,
    _OptionalAssociateDhcpOptionsRequestRequestTypeDef,
):
    pass


_RequiredAssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef = TypedDict(
    "_RequiredAssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef",
    {
        "DhcpOptionsId": str,
    },
)
_OptionalAssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef = TypedDict(
    "_OptionalAssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef(
    _RequiredAssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef,
    _OptionalAssociateDhcpOptionsRequestVpcAssociateDhcpOptionsTypeDef,
):
    pass


AssociateEnclaveCertificateIamRoleRequestRequestTypeDef = TypedDict(
    "AssociateEnclaveCertificateIamRoleRequestRequestTypeDef",
    {
        "CertificateArn": str,
        "RoleArn": str,
        "DryRun": bool,
    },
    total=False,
)

IamInstanceProfileSpecificationTypeDef = TypedDict(
    "IamInstanceProfileSpecificationTypeDef",
    {
        "Arn": str,
        "Name": str,
    },
    total=False,
)

_RequiredAssociateRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateRouteTableRequestRequestTypeDef",
    {
        "RouteTableId": str,
    },
)
_OptionalAssociateRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
        "SubnetId": str,
        "GatewayId": str,
    },
    total=False,
)


class AssociateRouteTableRequestRequestTypeDef(
    _RequiredAssociateRouteTableRequestRequestTypeDef,
    _OptionalAssociateRouteTableRequestRequestTypeDef,
):
    pass


AssociateRouteTableRequestRouteTableAssociateWithSubnetTypeDef = TypedDict(
    "AssociateRouteTableRequestRouteTableAssociateWithSubnetTypeDef",
    {
        "DryRun": bool,
        "SubnetId": str,
        "GatewayId": str,
    },
    total=False,
)

RouteTableAssociationStateTypeDef = TypedDict(
    "RouteTableAssociationStateTypeDef",
    {
        "State": RouteTableAssociationStateCodeType,
        "StatusMessage": str,
    },
    total=False,
)

AssociateSubnetCidrBlockRequestRequestTypeDef = TypedDict(
    "AssociateSubnetCidrBlockRequestRequestTypeDef",
    {
        "Ipv6CidrBlock": str,
        "SubnetId": str,
    },
)

AssociateTransitGatewayMulticastDomainRequestRequestTypeDef = TypedDict(
    "AssociateTransitGatewayMulticastDomainRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "TransitGatewayAttachmentId": str,
        "SubnetIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

_RequiredAssociateTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalAssociateTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AssociateTransitGatewayRouteTableRequestRequestTypeDef(
    _RequiredAssociateTransitGatewayRouteTableRequestRequestTypeDef,
    _OptionalAssociateTransitGatewayRouteTableRequestRequestTypeDef,
):
    pass


TransitGatewayAssociationTypeDef = TypedDict(
    "TransitGatewayAssociationTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "TransitGatewayAttachmentId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "State": TransitGatewayAssociationStateType,
    },
    total=False,
)

_RequiredAssociateTrunkInterfaceRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateTrunkInterfaceRequestRequestTypeDef",
    {
        "BranchInterfaceId": str,
        "TrunkInterfaceId": str,
    },
)
_OptionalAssociateTrunkInterfaceRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateTrunkInterfaceRequestRequestTypeDef",
    {
        "VlanId": int,
        "GreKey": int,
        "ClientToken": str,
        "DryRun": bool,
    },
    total=False,
)


class AssociateTrunkInterfaceRequestRequestTypeDef(
    _RequiredAssociateTrunkInterfaceRequestRequestTypeDef,
    _OptionalAssociateTrunkInterfaceRequestRequestTypeDef,
):
    pass


_RequiredAssociateVpcCidrBlockRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateVpcCidrBlockRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalAssociateVpcCidrBlockRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateVpcCidrBlockRequestRequestTypeDef",
    {
        "AmazonProvidedIpv6CidrBlock": bool,
        "CidrBlock": str,
        "Ipv6CidrBlockNetworkBorderGroup": str,
        "Ipv6Pool": str,
        "Ipv6CidrBlock": str,
        "Ipv4IpamPoolId": str,
        "Ipv4NetmaskLength": int,
        "Ipv6IpamPoolId": str,
        "Ipv6NetmaskLength": int,
    },
    total=False,
)


class AssociateVpcCidrBlockRequestRequestTypeDef(
    _RequiredAssociateVpcCidrBlockRequestRequestTypeDef,
    _OptionalAssociateVpcCidrBlockRequestRequestTypeDef,
):
    pass


AssociatedRoleTypeDef = TypedDict(
    "AssociatedRoleTypeDef",
    {
        "AssociatedRoleArn": str,
        "CertificateS3BucketName": str,
        "CertificateS3ObjectKey": str,
        "EncryptionKmsKeyId": str,
    },
    total=False,
)

AssociatedTargetNetworkTypeDef = TypedDict(
    "AssociatedTargetNetworkTypeDef",
    {
        "NetworkId": str,
        "NetworkType": Literal["vpc"],
    },
    total=False,
)

_RequiredAthenaIntegrationTypeDef = TypedDict(
    "_RequiredAthenaIntegrationTypeDef",
    {
        "IntegrationResultS3DestinationArn": str,
        "PartitionLoadFrequency": PartitionLoadFrequencyType,
    },
)
_OptionalAthenaIntegrationTypeDef = TypedDict(
    "_OptionalAthenaIntegrationTypeDef",
    {
        "PartitionStartDate": Union[datetime, str],
        "PartitionEndDate": Union[datetime, str],
    },
    total=False,
)


class AthenaIntegrationTypeDef(
    _RequiredAthenaIntegrationTypeDef, _OptionalAthenaIntegrationTypeDef
):
    pass


_RequiredAttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef = TypedDict(
    "_RequiredAttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef",
    {
        "Groups": Sequence[str],
        "VpcId": str,
    },
)
_OptionalAttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef = TypedDict(
    "_OptionalAttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef(
    _RequiredAttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef,
    _OptionalAttachClassicLinkVpcRequestInstanceAttachClassicLinkVpcTypeDef,
):
    pass


_RequiredAttachClassicLinkVpcRequestRequestTypeDef = TypedDict(
    "_RequiredAttachClassicLinkVpcRequestRequestTypeDef",
    {
        "Groups": Sequence[str],
        "InstanceId": str,
        "VpcId": str,
    },
)
_OptionalAttachClassicLinkVpcRequestRequestTypeDef = TypedDict(
    "_OptionalAttachClassicLinkVpcRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachClassicLinkVpcRequestRequestTypeDef(
    _RequiredAttachClassicLinkVpcRequestRequestTypeDef,
    _OptionalAttachClassicLinkVpcRequestRequestTypeDef,
):
    pass


_RequiredAttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef = TypedDict(
    "_RequiredAttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef",
    {
        "Groups": Sequence[str],
        "InstanceId": str,
    },
)
_OptionalAttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef = TypedDict(
    "_OptionalAttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef(
    _RequiredAttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef,
    _OptionalAttachClassicLinkVpcRequestVpcAttachClassicLinkInstanceTypeDef,
):
    pass


_RequiredAttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef = TypedDict(
    "_RequiredAttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalAttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef = TypedDict(
    "_OptionalAttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef(
    _RequiredAttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef,
    _OptionalAttachInternetGatewayRequestInternetGatewayAttachToVpcTypeDef,
):
    pass


_RequiredAttachInternetGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredAttachInternetGatewayRequestRequestTypeDef",
    {
        "InternetGatewayId": str,
        "VpcId": str,
    },
)
_OptionalAttachInternetGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalAttachInternetGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachInternetGatewayRequestRequestTypeDef(
    _RequiredAttachInternetGatewayRequestRequestTypeDef,
    _OptionalAttachInternetGatewayRequestRequestTypeDef,
):
    pass


_RequiredAttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef = TypedDict(
    "_RequiredAttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef",
    {
        "InternetGatewayId": str,
    },
)
_OptionalAttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef = TypedDict(
    "_OptionalAttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef(
    _RequiredAttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef,
    _OptionalAttachInternetGatewayRequestVpcAttachInternetGatewayTypeDef,
):
    pass


_RequiredAttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef = TypedDict(
    "_RequiredAttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef",
    {
        "DeviceIndex": int,
        "InstanceId": str,
    },
)
_OptionalAttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef = TypedDict(
    "_OptionalAttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef",
    {
        "DryRun": bool,
        "NetworkCardIndex": int,
    },
    total=False,
)


class AttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef(
    _RequiredAttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef,
    _OptionalAttachNetworkInterfaceRequestNetworkInterfaceAttachTypeDef,
):
    pass


_RequiredAttachNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_RequiredAttachNetworkInterfaceRequestRequestTypeDef",
    {
        "DeviceIndex": int,
        "InstanceId": str,
        "NetworkInterfaceId": str,
    },
)
_OptionalAttachNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_OptionalAttachNetworkInterfaceRequestRequestTypeDef",
    {
        "DryRun": bool,
        "NetworkCardIndex": int,
    },
    total=False,
)


class AttachNetworkInterfaceRequestRequestTypeDef(
    _RequiredAttachNetworkInterfaceRequestRequestTypeDef,
    _OptionalAttachNetworkInterfaceRequestRequestTypeDef,
):
    pass


_RequiredAttachVolumeRequestInstanceAttachVolumeTypeDef = TypedDict(
    "_RequiredAttachVolumeRequestInstanceAttachVolumeTypeDef",
    {
        "Device": str,
        "VolumeId": str,
    },
)
_OptionalAttachVolumeRequestInstanceAttachVolumeTypeDef = TypedDict(
    "_OptionalAttachVolumeRequestInstanceAttachVolumeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachVolumeRequestInstanceAttachVolumeTypeDef(
    _RequiredAttachVolumeRequestInstanceAttachVolumeTypeDef,
    _OptionalAttachVolumeRequestInstanceAttachVolumeTypeDef,
):
    pass


_RequiredAttachVolumeRequestRequestTypeDef = TypedDict(
    "_RequiredAttachVolumeRequestRequestTypeDef",
    {
        "Device": str,
        "InstanceId": str,
        "VolumeId": str,
    },
)
_OptionalAttachVolumeRequestRequestTypeDef = TypedDict(
    "_OptionalAttachVolumeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachVolumeRequestRequestTypeDef(
    _RequiredAttachVolumeRequestRequestTypeDef, _OptionalAttachVolumeRequestRequestTypeDef
):
    pass


_RequiredAttachVolumeRequestVolumeAttachToInstanceTypeDef = TypedDict(
    "_RequiredAttachVolumeRequestVolumeAttachToInstanceTypeDef",
    {
        "Device": str,
        "InstanceId": str,
    },
)
_OptionalAttachVolumeRequestVolumeAttachToInstanceTypeDef = TypedDict(
    "_OptionalAttachVolumeRequestVolumeAttachToInstanceTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachVolumeRequestVolumeAttachToInstanceTypeDef(
    _RequiredAttachVolumeRequestVolumeAttachToInstanceTypeDef,
    _OptionalAttachVolumeRequestVolumeAttachToInstanceTypeDef,
):
    pass


_RequiredAttachVpnGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredAttachVpnGatewayRequestRequestTypeDef",
    {
        "VpcId": str,
        "VpnGatewayId": str,
    },
)
_OptionalAttachVpnGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalAttachVpnGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AttachVpnGatewayRequestRequestTypeDef(
    _RequiredAttachVpnGatewayRequestRequestTypeDef, _OptionalAttachVpnGatewayRequestRequestTypeDef
):
    pass


VpcAttachmentTypeDef = TypedDict(
    "VpcAttachmentTypeDef",
    {
        "State": AttachmentStatusType,
        "VpcId": str,
    },
    total=False,
)

AttributeBooleanValueTypeDef = TypedDict(
    "AttributeBooleanValueTypeDef",
    {
        "Value": bool,
    },
    total=False,
)

AttributeValueTypeDef = TypedDict(
    "AttributeValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

ClientVpnAuthorizationRuleStatusTypeDef = TypedDict(
    "ClientVpnAuthorizationRuleStatusTypeDef",
    {
        "Code": ClientVpnAuthorizationRuleStatusCodeType,
        "Message": str,
    },
    total=False,
)

_RequiredAuthorizeClientVpnIngressRequestRequestTypeDef = TypedDict(
    "_RequiredAuthorizeClientVpnIngressRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "TargetNetworkCidr": str,
    },
)
_OptionalAuthorizeClientVpnIngressRequestRequestTypeDef = TypedDict(
    "_OptionalAuthorizeClientVpnIngressRequestRequestTypeDef",
    {
        "AccessGroupId": str,
        "AuthorizeAllGroups": bool,
        "Description": str,
        "ClientToken": str,
        "DryRun": bool,
    },
    total=False,
)


class AuthorizeClientVpnIngressRequestRequestTypeDef(
    _RequiredAuthorizeClientVpnIngressRequestRequestTypeDef,
    _OptionalAuthorizeClientVpnIngressRequestRequestTypeDef,
):
    pass


AvailabilityZoneMessageTypeDef = TypedDict(
    "AvailabilityZoneMessageTypeDef",
    {
        "Message": str,
    },
    total=False,
)

InstanceCapacityTypeDef = TypedDict(
    "InstanceCapacityTypeDef",
    {
        "AvailableCapacity": int,
        "InstanceType": str,
        "TotalCapacity": int,
    },
    total=False,
)

BaselineEbsBandwidthMbpsRequestTypeDef = TypedDict(
    "BaselineEbsBandwidthMbpsRequestTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

BaselineEbsBandwidthMbpsTypeDef = TypedDict(
    "BaselineEbsBandwidthMbpsTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

BlobAttributeValueTypeDef = TypedDict(
    "BlobAttributeValueTypeDef",
    {
        "Value": Union[str, bytes, IO[Any], StreamingBody],
    },
    total=False,
)

EbsBlockDeviceTypeDef = TypedDict(
    "EbsBlockDeviceTypeDef",
    {
        "DeleteOnTermination": bool,
        "Iops": int,
        "SnapshotId": str,
        "VolumeSize": int,
        "VolumeType": VolumeTypeType,
        "KmsKeyId": str,
        "Throughput": int,
        "OutpostArn": str,
        "Encrypted": bool,
    },
    total=False,
)

BundleTaskErrorTypeDef = TypedDict(
    "BundleTaskErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

_RequiredCancelBundleTaskRequestRequestTypeDef = TypedDict(
    "_RequiredCancelBundleTaskRequestRequestTypeDef",
    {
        "BundleId": str,
    },
)
_OptionalCancelBundleTaskRequestRequestTypeDef = TypedDict(
    "_OptionalCancelBundleTaskRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CancelBundleTaskRequestRequestTypeDef(
    _RequiredCancelBundleTaskRequestRequestTypeDef, _OptionalCancelBundleTaskRequestRequestTypeDef
):
    pass


CancelCapacityReservationFleetErrorTypeDef = TypedDict(
    "CancelCapacityReservationFleetErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

_RequiredCancelCapacityReservationFleetsRequestRequestTypeDef = TypedDict(
    "_RequiredCancelCapacityReservationFleetsRequestRequestTypeDef",
    {
        "CapacityReservationFleetIds": Sequence[str],
    },
)
_OptionalCancelCapacityReservationFleetsRequestRequestTypeDef = TypedDict(
    "_OptionalCancelCapacityReservationFleetsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CancelCapacityReservationFleetsRequestRequestTypeDef(
    _RequiredCancelCapacityReservationFleetsRequestRequestTypeDef,
    _OptionalCancelCapacityReservationFleetsRequestRequestTypeDef,
):
    pass


CapacityReservationFleetCancellationStateTypeDef = TypedDict(
    "CapacityReservationFleetCancellationStateTypeDef",
    {
        "CurrentFleetState": CapacityReservationFleetStateType,
        "PreviousFleetState": CapacityReservationFleetStateType,
        "CapacityReservationFleetId": str,
    },
    total=False,
)

_RequiredCancelCapacityReservationRequestRequestTypeDef = TypedDict(
    "_RequiredCancelCapacityReservationRequestRequestTypeDef",
    {
        "CapacityReservationId": str,
    },
)
_OptionalCancelCapacityReservationRequestRequestTypeDef = TypedDict(
    "_OptionalCancelCapacityReservationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CancelCapacityReservationRequestRequestTypeDef(
    _RequiredCancelCapacityReservationRequestRequestTypeDef,
    _OptionalCancelCapacityReservationRequestRequestTypeDef,
):
    pass


_RequiredCancelConversionRequestRequestTypeDef = TypedDict(
    "_RequiredCancelConversionRequestRequestTypeDef",
    {
        "ConversionTaskId": str,
    },
)
_OptionalCancelConversionRequestRequestTypeDef = TypedDict(
    "_OptionalCancelConversionRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ReasonMessage": str,
    },
    total=False,
)


class CancelConversionRequestRequestTypeDef(
    _RequiredCancelConversionRequestRequestTypeDef, _OptionalCancelConversionRequestRequestTypeDef
):
    pass


CancelExportTaskRequestRequestTypeDef = TypedDict(
    "CancelExportTaskRequestRequestTypeDef",
    {
        "ExportTaskId": str,
    },
)

CancelImportTaskRequestRequestTypeDef = TypedDict(
    "CancelImportTaskRequestRequestTypeDef",
    {
        "CancelReason": str,
        "DryRun": bool,
        "ImportTaskId": str,
    },
    total=False,
)

CancelReservedInstancesListingRequestRequestTypeDef = TypedDict(
    "CancelReservedInstancesListingRequestRequestTypeDef",
    {
        "ReservedInstancesListingId": str,
    },
)

CancelSpotFleetRequestsErrorTypeDef = TypedDict(
    "CancelSpotFleetRequestsErrorTypeDef",
    {
        "Code": CancelBatchErrorCodeType,
        "Message": str,
    },
    total=False,
)

_RequiredCancelSpotFleetRequestsRequestRequestTypeDef = TypedDict(
    "_RequiredCancelSpotFleetRequestsRequestRequestTypeDef",
    {
        "SpotFleetRequestIds": Sequence[str],
        "TerminateInstances": bool,
    },
)
_OptionalCancelSpotFleetRequestsRequestRequestTypeDef = TypedDict(
    "_OptionalCancelSpotFleetRequestsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CancelSpotFleetRequestsRequestRequestTypeDef(
    _RequiredCancelSpotFleetRequestsRequestRequestTypeDef,
    _OptionalCancelSpotFleetRequestsRequestRequestTypeDef,
):
    pass


CancelSpotFleetRequestsSuccessItemTypeDef = TypedDict(
    "CancelSpotFleetRequestsSuccessItemTypeDef",
    {
        "CurrentSpotFleetRequestState": BatchStateType,
        "PreviousSpotFleetRequestState": BatchStateType,
        "SpotFleetRequestId": str,
    },
    total=False,
)

_RequiredCancelSpotInstanceRequestsRequestRequestTypeDef = TypedDict(
    "_RequiredCancelSpotInstanceRequestsRequestRequestTypeDef",
    {
        "SpotInstanceRequestIds": Sequence[str],
    },
)
_OptionalCancelSpotInstanceRequestsRequestRequestTypeDef = TypedDict(
    "_OptionalCancelSpotInstanceRequestsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CancelSpotInstanceRequestsRequestRequestTypeDef(
    _RequiredCancelSpotInstanceRequestsRequestRequestTypeDef,
    _OptionalCancelSpotInstanceRequestsRequestRequestTypeDef,
):
    pass


CancelledSpotInstanceRequestTypeDef = TypedDict(
    "CancelledSpotInstanceRequestTypeDef",
    {
        "SpotInstanceRequestId": str,
        "State": CancelSpotInstanceRequestStateType,
    },
    total=False,
)

FleetCapacityReservationTypeDef = TypedDict(
    "FleetCapacityReservationTypeDef",
    {
        "CapacityReservationId": str,
        "AvailabilityZoneId": str,
        "InstanceType": InstanceTypeType,
        "InstancePlatform": CapacityReservationInstancePlatformType,
        "AvailabilityZone": str,
        "TotalInstanceCount": int,
        "FulfilledCapacity": float,
        "EbsOptimized": bool,
        "CreateDate": datetime,
        "Weight": float,
        "Priority": int,
    },
    total=False,
)

CapacityReservationGroupTypeDef = TypedDict(
    "CapacityReservationGroupTypeDef",
    {
        "GroupArn": str,
        "OwnerId": str,
    },
    total=False,
)

CapacityReservationOptionsRequestTypeDef = TypedDict(
    "CapacityReservationOptionsRequestTypeDef",
    {
        "UsageStrategy": Literal["use-capacity-reservations-first"],
    },
    total=False,
)

CapacityReservationOptionsTypeDef = TypedDict(
    "CapacityReservationOptionsTypeDef",
    {
        "UsageStrategy": Literal["use-capacity-reservations-first"],
    },
    total=False,
)

CapacityReservationTargetResponseTypeDef = TypedDict(
    "CapacityReservationTargetResponseTypeDef",
    {
        "CapacityReservationId": str,
        "CapacityReservationResourceGroupArn": str,
    },
    total=False,
)

CapacityReservationTargetTypeDef = TypedDict(
    "CapacityReservationTargetTypeDef",
    {
        "CapacityReservationId": str,
        "CapacityReservationResourceGroupArn": str,
    },
    total=False,
)

CertificateAuthenticationRequestTypeDef = TypedDict(
    "CertificateAuthenticationRequestTypeDef",
    {
        "ClientRootCertificateChainArn": str,
    },
    total=False,
)

CertificateAuthenticationTypeDef = TypedDict(
    "CertificateAuthenticationTypeDef",
    {
        "ClientRootCertificateChain": str,
    },
    total=False,
)

CidrAuthorizationContextTypeDef = TypedDict(
    "CidrAuthorizationContextTypeDef",
    {
        "Message": str,
        "Signature": str,
    },
)

CidrBlockTypeDef = TypedDict(
    "CidrBlockTypeDef",
    {
        "CidrBlock": str,
    },
    total=False,
)

ClassicLinkDnsSupportTypeDef = TypedDict(
    "ClassicLinkDnsSupportTypeDef",
    {
        "ClassicLinkDnsSupported": bool,
        "VpcId": str,
    },
    total=False,
)

GroupIdentifierTypeDef = TypedDict(
    "GroupIdentifierTypeDef",
    {
        "GroupName": str,
        "GroupId": str,
    },
    total=False,
)

ClassicLoadBalancerTypeDef = TypedDict(
    "ClassicLoadBalancerTypeDef",
    {
        "Name": str,
    },
    total=False,
)

ClientCertificateRevocationListStatusTypeDef = TypedDict(
    "ClientCertificateRevocationListStatusTypeDef",
    {
        "Code": ClientCertificateRevocationListStatusCodeType,
        "Message": str,
    },
    total=False,
)

ClientConnectOptionsTypeDef = TypedDict(
    "ClientConnectOptionsTypeDef",
    {
        "Enabled": bool,
        "LambdaFunctionArn": str,
    },
    total=False,
)

ClientVpnEndpointAttributeStatusTypeDef = TypedDict(
    "ClientVpnEndpointAttributeStatusTypeDef",
    {
        "Code": ClientVpnEndpointAttributeStatusCodeType,
        "Message": str,
    },
    total=False,
)

ClientDataTypeDef = TypedDict(
    "ClientDataTypeDef",
    {
        "Comment": str,
        "UploadEnd": Union[datetime, str],
        "UploadSize": float,
        "UploadStart": Union[datetime, str],
    },
    total=False,
)

ClientLoginBannerOptionsTypeDef = TypedDict(
    "ClientLoginBannerOptionsTypeDef",
    {
        "Enabled": bool,
        "BannerText": str,
    },
    total=False,
)

ClientLoginBannerResponseOptionsTypeDef = TypedDict(
    "ClientLoginBannerResponseOptionsTypeDef",
    {
        "Enabled": bool,
        "BannerText": str,
    },
    total=False,
)

DirectoryServiceAuthenticationRequestTypeDef = TypedDict(
    "DirectoryServiceAuthenticationRequestTypeDef",
    {
        "DirectoryId": str,
    },
    total=False,
)

FederatedAuthenticationRequestTypeDef = TypedDict(
    "FederatedAuthenticationRequestTypeDef",
    {
        "SAMLProviderArn": str,
        "SelfServiceSAMLProviderArn": str,
    },
    total=False,
)

DirectoryServiceAuthenticationTypeDef = TypedDict(
    "DirectoryServiceAuthenticationTypeDef",
    {
        "DirectoryId": str,
    },
    total=False,
)

FederatedAuthenticationTypeDef = TypedDict(
    "FederatedAuthenticationTypeDef",
    {
        "SamlProviderArn": str,
        "SelfServiceSamlProviderArn": str,
    },
    total=False,
)

ClientVpnConnectionStatusTypeDef = TypedDict(
    "ClientVpnConnectionStatusTypeDef",
    {
        "Code": ClientVpnConnectionStatusCodeType,
        "Message": str,
    },
    total=False,
)

ClientVpnEndpointStatusTypeDef = TypedDict(
    "ClientVpnEndpointStatusTypeDef",
    {
        "Code": ClientVpnEndpointStatusCodeType,
        "Message": str,
    },
    total=False,
)

ConnectionLogResponseOptionsTypeDef = TypedDict(
    "ConnectionLogResponseOptionsTypeDef",
    {
        "Enabled": bool,
        "CloudwatchLogGroup": str,
        "CloudwatchLogStream": str,
    },
    total=False,
)

ClientVpnRouteStatusTypeDef = TypedDict(
    "ClientVpnRouteStatusTypeDef",
    {
        "Code": ClientVpnRouteStatusCodeType,
        "Message": str,
    },
    total=False,
)

CoipAddressUsageTypeDef = TypedDict(
    "CoipAddressUsageTypeDef",
    {
        "AllocationId": str,
        "AwsAccountId": str,
        "AwsService": str,
        "CoIp": str,
    },
    total=False,
)

_RequiredConfirmProductInstanceRequestRequestTypeDef = TypedDict(
    "_RequiredConfirmProductInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ProductCode": str,
    },
)
_OptionalConfirmProductInstanceRequestRequestTypeDef = TypedDict(
    "_OptionalConfirmProductInstanceRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ConfirmProductInstanceRequestRequestTypeDef(
    _RequiredConfirmProductInstanceRequestRequestTypeDef,
    _OptionalConfirmProductInstanceRequestRequestTypeDef,
):
    pass


ConnectionLogOptionsTypeDef = TypedDict(
    "ConnectionLogOptionsTypeDef",
    {
        "Enabled": bool,
        "CloudwatchLogGroup": str,
        "CloudwatchLogStream": str,
    },
    total=False,
)

ConnectionNotificationTypeDef = TypedDict(
    "ConnectionNotificationTypeDef",
    {
        "ConnectionNotificationId": str,
        "ServiceId": str,
        "VpcEndpointId": str,
        "ConnectionNotificationType": Literal["Topic"],
        "ConnectionNotificationArn": str,
        "ConnectionEvents": List[str],
        "ConnectionNotificationState": ConnectionNotificationStateType,
    },
    total=False,
)

_RequiredCopyFpgaImageRequestRequestTypeDef = TypedDict(
    "_RequiredCopyFpgaImageRequestRequestTypeDef",
    {
        "SourceFpgaImageId": str,
        "SourceRegion": str,
    },
)
_OptionalCopyFpgaImageRequestRequestTypeDef = TypedDict(
    "_OptionalCopyFpgaImageRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Description": str,
        "Name": str,
        "ClientToken": str,
    },
    total=False,
)


class CopyFpgaImageRequestRequestTypeDef(
    _RequiredCopyFpgaImageRequestRequestTypeDef, _OptionalCopyFpgaImageRequestRequestTypeDef
):
    pass


_RequiredCopyImageRequestRequestTypeDef = TypedDict(
    "_RequiredCopyImageRequestRequestTypeDef",
    {
        "Name": str,
        "SourceImageId": str,
        "SourceRegion": str,
    },
)
_OptionalCopyImageRequestRequestTypeDef = TypedDict(
    "_OptionalCopyImageRequestRequestTypeDef",
    {
        "ClientToken": str,
        "Description": str,
        "Encrypted": bool,
        "KmsKeyId": str,
        "DestinationOutpostArn": str,
        "DryRun": bool,
    },
    total=False,
)


class CopyImageRequestRequestTypeDef(
    _RequiredCopyImageRequestRequestTypeDef, _OptionalCopyImageRequestRequestTypeDef
):
    pass


CpuOptionsRequestTypeDef = TypedDict(
    "CpuOptionsRequestTypeDef",
    {
        "CoreCount": int,
        "ThreadsPerCore": int,
    },
    total=False,
)

CpuOptionsTypeDef = TypedDict(
    "CpuOptionsTypeDef",
    {
        "CoreCount": int,
        "ThreadsPerCore": int,
    },
    total=False,
)

ReservationFleetInstanceSpecificationTypeDef = TypedDict(
    "ReservationFleetInstanceSpecificationTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "InstancePlatform": CapacityReservationInstancePlatformType,
        "Weight": float,
        "AvailabilityZone": str,
        "AvailabilityZoneId": str,
        "EbsOptimized": bool,
        "Priority": int,
    },
    total=False,
)

_RequiredCreateClientVpnRouteRequestRequestTypeDef = TypedDict(
    "_RequiredCreateClientVpnRouteRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "DestinationCidrBlock": str,
        "TargetVpcSubnetId": str,
    },
)
_OptionalCreateClientVpnRouteRequestRequestTypeDef = TypedDict(
    "_OptionalCreateClientVpnRouteRequestRequestTypeDef",
    {
        "Description": str,
        "ClientToken": str,
        "DryRun": bool,
    },
    total=False,
)


class CreateClientVpnRouteRequestRequestTypeDef(
    _RequiredCreateClientVpnRouteRequestRequestTypeDef,
    _OptionalCreateClientVpnRouteRequestRequestTypeDef,
):
    pass


_RequiredCreateDefaultSubnetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDefaultSubnetRequestRequestTypeDef",
    {
        "AvailabilityZone": str,
    },
)
_OptionalCreateDefaultSubnetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDefaultSubnetRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Ipv6Native": bool,
    },
    total=False,
)


class CreateDefaultSubnetRequestRequestTypeDef(
    _RequiredCreateDefaultSubnetRequestRequestTypeDef,
    _OptionalCreateDefaultSubnetRequestRequestTypeDef,
):
    pass


CreateDefaultVpcRequestRequestTypeDef = TypedDict(
    "CreateDefaultVpcRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

NewDhcpConfigurationTypeDef = TypedDict(
    "NewDhcpConfigurationTypeDef",
    {
        "Key": str,
        "Values": Sequence[str],
    },
    total=False,
)

_RequiredTargetCapacitySpecificationRequestTypeDef = TypedDict(
    "_RequiredTargetCapacitySpecificationRequestTypeDef",
    {
        "TotalTargetCapacity": int,
    },
)
_OptionalTargetCapacitySpecificationRequestTypeDef = TypedDict(
    "_OptionalTargetCapacitySpecificationRequestTypeDef",
    {
        "OnDemandTargetCapacity": int,
        "SpotTargetCapacity": int,
        "DefaultTargetCapacityType": DefaultTargetCapacityTypeType,
        "TargetCapacityUnitType": TargetCapacityUnitTypeType,
    },
    total=False,
)


class TargetCapacitySpecificationRequestTypeDef(
    _RequiredTargetCapacitySpecificationRequestTypeDef,
    _OptionalTargetCapacitySpecificationRequestTypeDef,
):
    pass


DestinationOptionsRequestTypeDef = TypedDict(
    "DestinationOptionsRequestTypeDef",
    {
        "FileFormat": DestinationFileFormatType,
        "HiveCompatiblePartitions": bool,
        "PerHourPartition": bool,
    },
    total=False,
)

StorageLocationTypeDef = TypedDict(
    "StorageLocationTypeDef",
    {
        "Bucket": str,
        "Key": str,
    },
    total=False,
)

InstanceEventWindowTimeRangeRequestTypeDef = TypedDict(
    "InstanceEventWindowTimeRangeRequestTypeDef",
    {
        "StartWeekDay": WeekDayType,
        "StartHour": int,
        "EndWeekDay": WeekDayType,
        "EndHour": int,
    },
    total=False,
)

ExportToS3TaskSpecificationTypeDef = TypedDict(
    "ExportToS3TaskSpecificationTypeDef",
    {
        "ContainerFormat": Literal["ova"],
        "DiskImageFormat": DiskImageFormatType,
        "S3Bucket": str,
        "S3Prefix": str,
    },
    total=False,
)

RequestIpamResourceTagTypeDef = TypedDict(
    "RequestIpamResourceTagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
    total=False,
)

_RequiredCreateLocalGatewayRouteRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLocalGatewayRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "LocalGatewayRouteTableId": str,
        "LocalGatewayVirtualInterfaceGroupId": str,
    },
)
_OptionalCreateLocalGatewayRouteRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLocalGatewayRouteRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateLocalGatewayRouteRequestRequestTypeDef(
    _RequiredCreateLocalGatewayRouteRequestRequestTypeDef,
    _OptionalCreateLocalGatewayRouteRequestRequestTypeDef,
):
    pass


LocalGatewayRouteTypeDef = TypedDict(
    "LocalGatewayRouteTypeDef",
    {
        "DestinationCidrBlock": str,
        "LocalGatewayVirtualInterfaceGroupId": str,
        "Type": LocalGatewayRouteTypeType,
        "State": LocalGatewayRouteStateType,
        "LocalGatewayRouteTableId": str,
        "LocalGatewayRouteTableArn": str,
        "OwnerId": str,
    },
    total=False,
)

IcmpTypeCodeTypeDef = TypedDict(
    "IcmpTypeCodeTypeDef",
    {
        "Code": int,
        "Type": int,
    },
    total=False,
)

_RequiredCreateNetworkInterfacePermissionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNetworkInterfacePermissionRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
        "Permission": InterfacePermissionTypeType,
    },
)
_OptionalCreateNetworkInterfacePermissionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNetworkInterfacePermissionRequestRequestTypeDef",
    {
        "AwsAccountId": str,
        "AwsService": str,
        "DryRun": bool,
    },
    total=False,
)


class CreateNetworkInterfacePermissionRequestRequestTypeDef(
    _RequiredCreateNetworkInterfacePermissionRequestRequestTypeDef,
    _OptionalCreateNetworkInterfacePermissionRequestRequestTypeDef,
):
    pass


InstanceIpv6AddressTypeDef = TypedDict(
    "InstanceIpv6AddressTypeDef",
    {
        "Ipv6Address": str,
    },
    total=False,
)

Ipv4PrefixSpecificationRequestTypeDef = TypedDict(
    "Ipv4PrefixSpecificationRequestTypeDef",
    {
        "Ipv4Prefix": str,
    },
    total=False,
)

Ipv6PrefixSpecificationRequestTypeDef = TypedDict(
    "Ipv6PrefixSpecificationRequestTypeDef",
    {
        "Ipv6Prefix": str,
    },
    total=False,
)

PrivateIpAddressSpecificationTypeDef = TypedDict(
    "PrivateIpAddressSpecificationTypeDef",
    {
        "Primary": bool,
        "PrivateIpAddress": str,
    },
    total=False,
)

PriceScheduleSpecificationTypeDef = TypedDict(
    "PriceScheduleSpecificationTypeDef",
    {
        "CurrencyCode": Literal["USD"],
        "Price": float,
        "Term": int,
    },
    total=False,
)

_RequiredCreateRouteRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRouteRequestRequestTypeDef",
    {
        "RouteTableId": str,
    },
)
_OptionalCreateRouteRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "DryRun": bool,
        "VpcEndpointId": str,
        "EgressOnlyInternetGatewayId": str,
        "GatewayId": str,
        "InstanceId": str,
        "NatGatewayId": str,
        "TransitGatewayId": str,
        "LocalGatewayId": str,
        "CarrierGatewayId": str,
        "NetworkInterfaceId": str,
        "VpcPeeringConnectionId": str,
        "CoreNetworkArn": str,
    },
    total=False,
)


class CreateRouteRequestRequestTypeDef(
    _RequiredCreateRouteRequestRequestTypeDef, _OptionalCreateRouteRequestRequestTypeDef
):
    pass


CreateRouteRequestRouteTableCreateRouteTypeDef = TypedDict(
    "CreateRouteRequestRouteTableCreateRouteTypeDef",
    {
        "DestinationCidrBlock": str,
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "DryRun": bool,
        "VpcEndpointId": str,
        "EgressOnlyInternetGatewayId": str,
        "GatewayId": str,
        "InstanceId": str,
        "NatGatewayId": str,
        "TransitGatewayId": str,
        "LocalGatewayId": str,
        "CarrierGatewayId": str,
        "NetworkInterfaceId": str,
        "VpcPeeringConnectionId": str,
        "CoreNetworkArn": str,
    },
    total=False,
)

InstanceSpecificationTypeDef = TypedDict(
    "InstanceSpecificationTypeDef",
    {
        "InstanceId": str,
        "ExcludeBootVolume": bool,
    },
    total=False,
)

_RequiredCreateSpotDatafeedSubscriptionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSpotDatafeedSubscriptionRequestRequestTypeDef",
    {
        "Bucket": str,
    },
)
_OptionalCreateSpotDatafeedSubscriptionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSpotDatafeedSubscriptionRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Prefix": str,
    },
    total=False,
)


class CreateSpotDatafeedSubscriptionRequestRequestTypeDef(
    _RequiredCreateSpotDatafeedSubscriptionRequestRequestTypeDef,
    _OptionalCreateSpotDatafeedSubscriptionRequestRequestTypeDef,
):
    pass


S3ObjectTagTypeDef = TypedDict(
    "S3ObjectTagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
    total=False,
)

TrafficMirrorPortRangeRequestTypeDef = TypedDict(
    "TrafficMirrorPortRangeRequestTypeDef",
    {
        "FromPort": int,
        "ToPort": int,
    },
    total=False,
)

TransitGatewayConnectRequestBgpOptionsTypeDef = TypedDict(
    "TransitGatewayConnectRequestBgpOptionsTypeDef",
    {
        "PeerAsn": int,
    },
    total=False,
)

CreateTransitGatewayConnectRequestOptionsTypeDef = TypedDict(
    "CreateTransitGatewayConnectRequestOptionsTypeDef",
    {
        "Protocol": Literal["gre"],
    },
)

CreateTransitGatewayMulticastDomainRequestOptionsTypeDef = TypedDict(
    "CreateTransitGatewayMulticastDomainRequestOptionsTypeDef",
    {
        "Igmpv2Support": Igmpv2SupportValueType,
        "StaticSourcesSupport": StaticSourcesSupportValueType,
        "AutoAcceptSharedAssociations": AutoAcceptSharedAssociationsValueType,
    },
    total=False,
)

_RequiredCreateTransitGatewayPrefixListReferenceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "PrefixListId": str,
    },
)
_OptionalCreateTransitGatewayPrefixListReferenceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "Blackhole": bool,
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayPrefixListReferenceRequestRequestTypeDef(
    _RequiredCreateTransitGatewayPrefixListReferenceRequestRequestTypeDef,
    _OptionalCreateTransitGatewayPrefixListReferenceRequestRequestTypeDef,
):
    pass


TransitGatewayRequestOptionsTypeDef = TypedDict(
    "TransitGatewayRequestOptionsTypeDef",
    {
        "AmazonSideAsn": int,
        "AutoAcceptSharedAttachments": AutoAcceptSharedAttachmentsValueType,
        "DefaultRouteTableAssociation": DefaultRouteTableAssociationValueType,
        "DefaultRouteTablePropagation": DefaultRouteTablePropagationValueType,
        "VpnEcmpSupport": VpnEcmpSupportValueType,
        "DnsSupport": DnsSupportValueType,
        "MulticastSupport": MulticastSupportValueType,
        "TransitGatewayCidrBlocks": Sequence[str],
    },
    total=False,
)

_RequiredCreateTransitGatewayRouteRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalCreateTransitGatewayRouteRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayRouteRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "Blackhole": bool,
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayRouteRequestRequestTypeDef(
    _RequiredCreateTransitGatewayRouteRequestRequestTypeDef,
    _OptionalCreateTransitGatewayRouteRequestRequestTypeDef,
):
    pass


CreateTransitGatewayVpcAttachmentRequestOptionsTypeDef = TypedDict(
    "CreateTransitGatewayVpcAttachmentRequestOptionsTypeDef",
    {
        "DnsSupport": DnsSupportValueType,
        "Ipv6Support": Ipv6SupportValueType,
        "ApplianceModeSupport": ApplianceModeSupportValueType,
    },
    total=False,
)

CreateVolumePermissionTypeDef = TypedDict(
    "CreateVolumePermissionTypeDef",
    {
        "Group": Literal["all"],
        "UserId": str,
    },
    total=False,
)

_RequiredCreateVpcEndpointConnectionNotificationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpcEndpointConnectionNotificationRequestRequestTypeDef",
    {
        "ConnectionNotificationArn": str,
        "ConnectionEvents": Sequence[str],
    },
)
_OptionalCreateVpcEndpointConnectionNotificationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpcEndpointConnectionNotificationRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ServiceId": str,
        "VpcEndpointId": str,
        "ClientToken": str,
    },
    total=False,
)


class CreateVpcEndpointConnectionNotificationRequestRequestTypeDef(
    _RequiredCreateVpcEndpointConnectionNotificationRequestRequestTypeDef,
    _OptionalCreateVpcEndpointConnectionNotificationRequestRequestTypeDef,
):
    pass


DnsOptionsSpecificationTypeDef = TypedDict(
    "DnsOptionsSpecificationTypeDef",
    {
        "DnsRecordIpType": DnsRecordIpTypeType,
    },
    total=False,
)

CreateVpnConnectionRouteRequestRequestTypeDef = TypedDict(
    "CreateVpnConnectionRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "VpnConnectionId": str,
    },
)

CreditSpecificationRequestTypeDef = TypedDict(
    "CreditSpecificationRequestTypeDef",
    {
        "CpuCredits": str,
    },
)

CreditSpecificationTypeDef = TypedDict(
    "CreditSpecificationTypeDef",
    {
        "CpuCredits": str,
    },
    total=False,
)

_RequiredDeleteCarrierGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteCarrierGatewayRequestRequestTypeDef",
    {
        "CarrierGatewayId": str,
    },
)
_OptionalDeleteCarrierGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteCarrierGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteCarrierGatewayRequestRequestTypeDef(
    _RequiredDeleteCarrierGatewayRequestRequestTypeDef,
    _OptionalDeleteCarrierGatewayRequestRequestTypeDef,
):
    pass


_RequiredDeleteClientVpnEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteClientVpnEndpointRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDeleteClientVpnEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteClientVpnEndpointRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteClientVpnEndpointRequestRequestTypeDef(
    _RequiredDeleteClientVpnEndpointRequestRequestTypeDef,
    _OptionalDeleteClientVpnEndpointRequestRequestTypeDef,
):
    pass


_RequiredDeleteClientVpnRouteRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteClientVpnRouteRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "DestinationCidrBlock": str,
    },
)
_OptionalDeleteClientVpnRouteRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteClientVpnRouteRequestRequestTypeDef",
    {
        "TargetVpcSubnetId": str,
        "DryRun": bool,
    },
    total=False,
)


class DeleteClientVpnRouteRequestRequestTypeDef(
    _RequiredDeleteClientVpnRouteRequestRequestTypeDef,
    _OptionalDeleteClientVpnRouteRequestRequestTypeDef,
):
    pass


_RequiredDeleteCustomerGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteCustomerGatewayRequestRequestTypeDef",
    {
        "CustomerGatewayId": str,
    },
)
_OptionalDeleteCustomerGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteCustomerGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteCustomerGatewayRequestRequestTypeDef(
    _RequiredDeleteCustomerGatewayRequestRequestTypeDef,
    _OptionalDeleteCustomerGatewayRequestRequestTypeDef,
):
    pass


DeleteDhcpOptionsRequestDhcpOptionsDeleteTypeDef = TypedDict(
    "DeleteDhcpOptionsRequestDhcpOptionsDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteDhcpOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteDhcpOptionsRequestRequestTypeDef",
    {
        "DhcpOptionsId": str,
    },
)
_OptionalDeleteDhcpOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteDhcpOptionsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteDhcpOptionsRequestRequestTypeDef(
    _RequiredDeleteDhcpOptionsRequestRequestTypeDef, _OptionalDeleteDhcpOptionsRequestRequestTypeDef
):
    pass


_RequiredDeleteEgressOnlyInternetGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteEgressOnlyInternetGatewayRequestRequestTypeDef",
    {
        "EgressOnlyInternetGatewayId": str,
    },
)
_OptionalDeleteEgressOnlyInternetGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteEgressOnlyInternetGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteEgressOnlyInternetGatewayRequestRequestTypeDef(
    _RequiredDeleteEgressOnlyInternetGatewayRequestRequestTypeDef,
    _OptionalDeleteEgressOnlyInternetGatewayRequestRequestTypeDef,
):
    pass


DeleteFleetErrorTypeDef = TypedDict(
    "DeleteFleetErrorTypeDef",
    {
        "Code": DeleteFleetErrorCodeType,
        "Message": str,
    },
    total=False,
)

DeleteFleetSuccessItemTypeDef = TypedDict(
    "DeleteFleetSuccessItemTypeDef",
    {
        "CurrentFleetState": FleetStateCodeType,
        "PreviousFleetState": FleetStateCodeType,
        "FleetId": str,
    },
    total=False,
)

_RequiredDeleteFleetsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteFleetsRequestRequestTypeDef",
    {
        "FleetIds": Sequence[str],
        "TerminateInstances": bool,
    },
)
_OptionalDeleteFleetsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteFleetsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteFleetsRequestRequestTypeDef(
    _RequiredDeleteFleetsRequestRequestTypeDef, _OptionalDeleteFleetsRequestRequestTypeDef
):
    pass


_RequiredDeleteFlowLogsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteFlowLogsRequestRequestTypeDef",
    {
        "FlowLogIds": Sequence[str],
    },
)
_OptionalDeleteFlowLogsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteFlowLogsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteFlowLogsRequestRequestTypeDef(
    _RequiredDeleteFlowLogsRequestRequestTypeDef, _OptionalDeleteFlowLogsRequestRequestTypeDef
):
    pass


_RequiredDeleteFpgaImageRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteFpgaImageRequestRequestTypeDef",
    {
        "FpgaImageId": str,
    },
)
_OptionalDeleteFpgaImageRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteFpgaImageRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteFpgaImageRequestRequestTypeDef(
    _RequiredDeleteFpgaImageRequestRequestTypeDef, _OptionalDeleteFpgaImageRequestRequestTypeDef
):
    pass


_RequiredDeleteInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteInstanceEventWindowRequestRequestTypeDef",
    {
        "InstanceEventWindowId": str,
    },
)
_OptionalDeleteInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteInstanceEventWindowRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ForceDelete": bool,
    },
    total=False,
)


class DeleteInstanceEventWindowRequestRequestTypeDef(
    _RequiredDeleteInstanceEventWindowRequestRequestTypeDef,
    _OptionalDeleteInstanceEventWindowRequestRequestTypeDef,
):
    pass


InstanceEventWindowStateChangeTypeDef = TypedDict(
    "InstanceEventWindowStateChangeTypeDef",
    {
        "InstanceEventWindowId": str,
        "State": InstanceEventWindowStateType,
    },
    total=False,
)

DeleteInternetGatewayRequestInternetGatewayDeleteTypeDef = TypedDict(
    "DeleteInternetGatewayRequestInternetGatewayDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteInternetGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteInternetGatewayRequestRequestTypeDef",
    {
        "InternetGatewayId": str,
    },
)
_OptionalDeleteInternetGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteInternetGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteInternetGatewayRequestRequestTypeDef(
    _RequiredDeleteInternetGatewayRequestRequestTypeDef,
    _OptionalDeleteInternetGatewayRequestRequestTypeDef,
):
    pass


_RequiredDeleteIpamPoolRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteIpamPoolRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalDeleteIpamPoolRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteIpamPoolRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteIpamPoolRequestRequestTypeDef(
    _RequiredDeleteIpamPoolRequestRequestTypeDef, _OptionalDeleteIpamPoolRequestRequestTypeDef
):
    pass


_RequiredDeleteIpamRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteIpamRequestRequestTypeDef",
    {
        "IpamId": str,
    },
)
_OptionalDeleteIpamRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteIpamRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Cascade": bool,
    },
    total=False,
)


class DeleteIpamRequestRequestTypeDef(
    _RequiredDeleteIpamRequestRequestTypeDef, _OptionalDeleteIpamRequestRequestTypeDef
):
    pass


_RequiredDeleteIpamScopeRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteIpamScopeRequestRequestTypeDef",
    {
        "IpamScopeId": str,
    },
)
_OptionalDeleteIpamScopeRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteIpamScopeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteIpamScopeRequestRequestTypeDef(
    _RequiredDeleteIpamScopeRequestRequestTypeDef, _OptionalDeleteIpamScopeRequestRequestTypeDef
):
    pass


DeleteKeyPairRequestKeyPairDeleteTypeDef = TypedDict(
    "DeleteKeyPairRequestKeyPairDeleteTypeDef",
    {
        "KeyPairId": str,
        "DryRun": bool,
    },
    total=False,
)

DeleteKeyPairRequestKeyPairInfoDeleteTypeDef = TypedDict(
    "DeleteKeyPairRequestKeyPairInfoDeleteTypeDef",
    {
        "KeyPairId": str,
        "DryRun": bool,
    },
    total=False,
)

DeleteKeyPairRequestRequestTypeDef = TypedDict(
    "DeleteKeyPairRequestRequestTypeDef",
    {
        "KeyName": str,
        "KeyPairId": str,
        "DryRun": bool,
    },
    total=False,
)

DeleteLaunchTemplateRequestRequestTypeDef = TypedDict(
    "DeleteLaunchTemplateRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
    },
    total=False,
)

_RequiredDeleteLaunchTemplateVersionsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteLaunchTemplateVersionsRequestRequestTypeDef",
    {
        "Versions": Sequence[str],
    },
)
_OptionalDeleteLaunchTemplateVersionsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteLaunchTemplateVersionsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
    },
    total=False,
)


class DeleteLaunchTemplateVersionsRequestRequestTypeDef(
    _RequiredDeleteLaunchTemplateVersionsRequestRequestTypeDef,
    _OptionalDeleteLaunchTemplateVersionsRequestRequestTypeDef,
):
    pass


ResponseErrorTypeDef = TypedDict(
    "ResponseErrorTypeDef",
    {
        "Code": LaunchTemplateErrorCodeType,
        "Message": str,
    },
    total=False,
)

DeleteLaunchTemplateVersionsResponseSuccessItemTypeDef = TypedDict(
    "DeleteLaunchTemplateVersionsResponseSuccessItemTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "VersionNumber": int,
    },
    total=False,
)

_RequiredDeleteLocalGatewayRouteRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteLocalGatewayRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "LocalGatewayRouteTableId": str,
    },
)
_OptionalDeleteLocalGatewayRouteRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteLocalGatewayRouteRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteLocalGatewayRouteRequestRequestTypeDef(
    _RequiredDeleteLocalGatewayRouteRequestRequestTypeDef,
    _OptionalDeleteLocalGatewayRouteRequestRequestTypeDef,
):
    pass


_RequiredDeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociationId": str,
    },
)
_OptionalDeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef(
    _RequiredDeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef,
    _OptionalDeleteLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef,
):
    pass


_RequiredDeleteManagedPrefixListRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteManagedPrefixListRequestRequestTypeDef",
    {
        "PrefixListId": str,
    },
)
_OptionalDeleteManagedPrefixListRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteManagedPrefixListRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteManagedPrefixListRequestRequestTypeDef(
    _RequiredDeleteManagedPrefixListRequestRequestTypeDef,
    _OptionalDeleteManagedPrefixListRequestRequestTypeDef,
):
    pass


_RequiredDeleteNatGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNatGatewayRequestRequestTypeDef",
    {
        "NatGatewayId": str,
    },
)
_OptionalDeleteNatGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNatGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNatGatewayRequestRequestTypeDef(
    _RequiredDeleteNatGatewayRequestRequestTypeDef, _OptionalDeleteNatGatewayRequestRequestTypeDef
):
    pass


_RequiredDeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef = TypedDict(
    "_RequiredDeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef",
    {
        "Egress": bool,
        "RuleNumber": int,
    },
)
_OptionalDeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef = TypedDict(
    "_OptionalDeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef(
    _RequiredDeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef,
    _OptionalDeleteNetworkAclEntryRequestNetworkAclDeleteEntryTypeDef,
):
    pass


_RequiredDeleteNetworkAclEntryRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkAclEntryRequestRequestTypeDef",
    {
        "Egress": bool,
        "NetworkAclId": str,
        "RuleNumber": int,
    },
)
_OptionalDeleteNetworkAclEntryRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkAclEntryRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkAclEntryRequestRequestTypeDef(
    _RequiredDeleteNetworkAclEntryRequestRequestTypeDef,
    _OptionalDeleteNetworkAclEntryRequestRequestTypeDef,
):
    pass


DeleteNetworkAclRequestNetworkAclDeleteTypeDef = TypedDict(
    "DeleteNetworkAclRequestNetworkAclDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteNetworkAclRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkAclRequestRequestTypeDef",
    {
        "NetworkAclId": str,
    },
)
_OptionalDeleteNetworkAclRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkAclRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkAclRequestRequestTypeDef(
    _RequiredDeleteNetworkAclRequestRequestTypeDef, _OptionalDeleteNetworkAclRequestRequestTypeDef
):
    pass


_RequiredDeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisId": str,
    },
)
_OptionalDeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef(
    _RequiredDeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef,
    _OptionalDeleteNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef,
):
    pass


_RequiredDeleteNetworkInsightsAccessScopeRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkInsightsAccessScopeRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeId": str,
    },
)
_OptionalDeleteNetworkInsightsAccessScopeRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkInsightsAccessScopeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkInsightsAccessScopeRequestRequestTypeDef(
    _RequiredDeleteNetworkInsightsAccessScopeRequestRequestTypeDef,
    _OptionalDeleteNetworkInsightsAccessScopeRequestRequestTypeDef,
):
    pass


_RequiredDeleteNetworkInsightsAnalysisRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkInsightsAnalysisRequestRequestTypeDef",
    {
        "NetworkInsightsAnalysisId": str,
    },
)
_OptionalDeleteNetworkInsightsAnalysisRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkInsightsAnalysisRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkInsightsAnalysisRequestRequestTypeDef(
    _RequiredDeleteNetworkInsightsAnalysisRequestRequestTypeDef,
    _OptionalDeleteNetworkInsightsAnalysisRequestRequestTypeDef,
):
    pass


_RequiredDeleteNetworkInsightsPathRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkInsightsPathRequestRequestTypeDef",
    {
        "NetworkInsightsPathId": str,
    },
)
_OptionalDeleteNetworkInsightsPathRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkInsightsPathRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkInsightsPathRequestRequestTypeDef(
    _RequiredDeleteNetworkInsightsPathRequestRequestTypeDef,
    _OptionalDeleteNetworkInsightsPathRequestRequestTypeDef,
):
    pass


_RequiredDeleteNetworkInterfacePermissionRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkInterfacePermissionRequestRequestTypeDef",
    {
        "NetworkInterfacePermissionId": str,
    },
)
_OptionalDeleteNetworkInterfacePermissionRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkInterfacePermissionRequestRequestTypeDef",
    {
        "Force": bool,
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkInterfacePermissionRequestRequestTypeDef(
    _RequiredDeleteNetworkInterfacePermissionRequestRequestTypeDef,
    _OptionalDeleteNetworkInterfacePermissionRequestRequestTypeDef,
):
    pass


DeleteNetworkInterfaceRequestNetworkInterfaceDeleteTypeDef = TypedDict(
    "DeleteNetworkInterfaceRequestNetworkInterfaceDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNetworkInterfaceRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalDeleteNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNetworkInterfaceRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteNetworkInterfaceRequestRequestTypeDef(
    _RequiredDeleteNetworkInterfaceRequestRequestTypeDef,
    _OptionalDeleteNetworkInterfaceRequestRequestTypeDef,
):
    pass


DeletePlacementGroupRequestPlacementGroupDeleteTypeDef = TypedDict(
    "DeletePlacementGroupRequestPlacementGroupDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeletePlacementGroupRequestRequestTypeDef = TypedDict(
    "_RequiredDeletePlacementGroupRequestRequestTypeDef",
    {
        "GroupName": str,
    },
)
_OptionalDeletePlacementGroupRequestRequestTypeDef = TypedDict(
    "_OptionalDeletePlacementGroupRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeletePlacementGroupRequestRequestTypeDef(
    _RequiredDeletePlacementGroupRequestRequestTypeDef,
    _OptionalDeletePlacementGroupRequestRequestTypeDef,
):
    pass


_RequiredDeletePublicIpv4PoolRequestRequestTypeDef = TypedDict(
    "_RequiredDeletePublicIpv4PoolRequestRequestTypeDef",
    {
        "PoolId": str,
    },
)
_OptionalDeletePublicIpv4PoolRequestRequestTypeDef = TypedDict(
    "_OptionalDeletePublicIpv4PoolRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeletePublicIpv4PoolRequestRequestTypeDef(
    _RequiredDeletePublicIpv4PoolRequestRequestTypeDef,
    _OptionalDeletePublicIpv4PoolRequestRequestTypeDef,
):
    pass


DeleteQueuedReservedInstancesErrorTypeDef = TypedDict(
    "DeleteQueuedReservedInstancesErrorTypeDef",
    {
        "Code": DeleteQueuedReservedInstancesErrorCodeType,
        "Message": str,
    },
    total=False,
)

_RequiredDeleteQueuedReservedInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteQueuedReservedInstancesRequestRequestTypeDef",
    {
        "ReservedInstancesIds": Sequence[str],
    },
)
_OptionalDeleteQueuedReservedInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteQueuedReservedInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteQueuedReservedInstancesRequestRequestTypeDef(
    _RequiredDeleteQueuedReservedInstancesRequestRequestTypeDef,
    _OptionalDeleteQueuedReservedInstancesRequestRequestTypeDef,
):
    pass


SuccessfulQueuedPurchaseDeletionTypeDef = TypedDict(
    "SuccessfulQueuedPurchaseDeletionTypeDef",
    {
        "ReservedInstancesId": str,
    },
    total=False,
)

_RequiredDeleteRouteRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteRouteRequestRequestTypeDef",
    {
        "RouteTableId": str,
    },
)
_OptionalDeleteRouteRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "DryRun": bool,
    },
    total=False,
)


class DeleteRouteRequestRequestTypeDef(
    _RequiredDeleteRouteRequestRequestTypeDef, _OptionalDeleteRouteRequestRequestTypeDef
):
    pass


DeleteRouteRequestRouteDeleteTypeDef = TypedDict(
    "DeleteRouteRequestRouteDeleteTypeDef",
    {
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteRouteTableRequestRequestTypeDef",
    {
        "RouteTableId": str,
    },
)
_OptionalDeleteRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteRouteTableRequestRequestTypeDef(
    _RequiredDeleteRouteTableRequestRequestTypeDef, _OptionalDeleteRouteTableRequestRequestTypeDef
):
    pass


DeleteRouteTableRequestRouteTableDeleteTypeDef = TypedDict(
    "DeleteRouteTableRequestRouteTableDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

DeleteSecurityGroupRequestRequestTypeDef = TypedDict(
    "DeleteSecurityGroupRequestRequestTypeDef",
    {
        "GroupId": str,
        "GroupName": str,
        "DryRun": bool,
    },
    total=False,
)

DeleteSecurityGroupRequestSecurityGroupDeleteTypeDef = TypedDict(
    "DeleteSecurityGroupRequestSecurityGroupDeleteTypeDef",
    {
        "GroupName": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteSnapshotRequestRequestTypeDef",
    {
        "SnapshotId": str,
    },
)
_OptionalDeleteSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteSnapshotRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteSnapshotRequestRequestTypeDef(
    _RequiredDeleteSnapshotRequestRequestTypeDef, _OptionalDeleteSnapshotRequestRequestTypeDef
):
    pass


DeleteSnapshotRequestSnapshotDeleteTypeDef = TypedDict(
    "DeleteSnapshotRequestSnapshotDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

DeleteSpotDatafeedSubscriptionRequestRequestTypeDef = TypedDict(
    "DeleteSpotDatafeedSubscriptionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteSubnetCidrReservationRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteSubnetCidrReservationRequestRequestTypeDef",
    {
        "SubnetCidrReservationId": str,
    },
)
_OptionalDeleteSubnetCidrReservationRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteSubnetCidrReservationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteSubnetCidrReservationRequestRequestTypeDef(
    _RequiredDeleteSubnetCidrReservationRequestRequestTypeDef,
    _OptionalDeleteSubnetCidrReservationRequestRequestTypeDef,
):
    pass


_RequiredDeleteSubnetRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteSubnetRequestRequestTypeDef",
    {
        "SubnetId": str,
    },
)
_OptionalDeleteSubnetRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteSubnetRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteSubnetRequestRequestTypeDef(
    _RequiredDeleteSubnetRequestRequestTypeDef, _OptionalDeleteSubnetRequestRequestTypeDef
):
    pass


DeleteSubnetRequestSubnetDeleteTypeDef = TypedDict(
    "DeleteSubnetRequestSubnetDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

DeleteTagsRequestTagDeleteTypeDef = TypedDict(
    "DeleteTagsRequestTagDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteTrafficMirrorFilterRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTrafficMirrorFilterRequestRequestTypeDef",
    {
        "TrafficMirrorFilterId": str,
    },
)
_OptionalDeleteTrafficMirrorFilterRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTrafficMirrorFilterRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTrafficMirrorFilterRequestRequestTypeDef(
    _RequiredDeleteTrafficMirrorFilterRequestRequestTypeDef,
    _OptionalDeleteTrafficMirrorFilterRequestRequestTypeDef,
):
    pass


_RequiredDeleteTrafficMirrorFilterRuleRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTrafficMirrorFilterRuleRequestRequestTypeDef",
    {
        "TrafficMirrorFilterRuleId": str,
    },
)
_OptionalDeleteTrafficMirrorFilterRuleRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTrafficMirrorFilterRuleRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTrafficMirrorFilterRuleRequestRequestTypeDef(
    _RequiredDeleteTrafficMirrorFilterRuleRequestRequestTypeDef,
    _OptionalDeleteTrafficMirrorFilterRuleRequestRequestTypeDef,
):
    pass


_RequiredDeleteTrafficMirrorSessionRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTrafficMirrorSessionRequestRequestTypeDef",
    {
        "TrafficMirrorSessionId": str,
    },
)
_OptionalDeleteTrafficMirrorSessionRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTrafficMirrorSessionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTrafficMirrorSessionRequestRequestTypeDef(
    _RequiredDeleteTrafficMirrorSessionRequestRequestTypeDef,
    _OptionalDeleteTrafficMirrorSessionRequestRequestTypeDef,
):
    pass


_RequiredDeleteTrafficMirrorTargetRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTrafficMirrorTargetRequestRequestTypeDef",
    {
        "TrafficMirrorTargetId": str,
    },
)
_OptionalDeleteTrafficMirrorTargetRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTrafficMirrorTargetRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTrafficMirrorTargetRequestRequestTypeDef(
    _RequiredDeleteTrafficMirrorTargetRequestRequestTypeDef,
    _OptionalDeleteTrafficMirrorTargetRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "TransitGatewayConnectPeerId": str,
    },
)
_OptionalDeleteTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayConnectPeerRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayConnectPeerRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayConnectPeerRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayConnectRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayConnectRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalDeleteTransitGatewayConnectRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayConnectRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayConnectRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayConnectRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayConnectRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayMulticastDomainRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayMulticastDomainRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
    },
)
_OptionalDeleteTransitGatewayMulticastDomainRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayMulticastDomainRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayMulticastDomainRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayMulticastDomainRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayMulticastDomainRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalDeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayPeeringAttachmentRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "PrefixListId": str,
    },
)
_OptionalDeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayPrefixListReferenceRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
    },
)
_OptionalDeleteTransitGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayRouteRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayRouteRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "DestinationCidrBlock": str,
    },
)
_OptionalDeleteTransitGatewayRouteRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayRouteRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayRouteRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayRouteRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayRouteRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalDeleteTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayRouteTableRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayRouteTableRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayRouteTableRequestRequestTypeDef,
):
    pass


_RequiredDeleteTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalDeleteTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteTransitGatewayVpcAttachmentRequestRequestTypeDef(
    _RequiredDeleteTransitGatewayVpcAttachmentRequestRequestTypeDef,
    _OptionalDeleteTransitGatewayVpcAttachmentRequestRequestTypeDef,
):
    pass


_RequiredDeleteVolumeRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVolumeRequestRequestTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalDeleteVolumeRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVolumeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVolumeRequestRequestTypeDef(
    _RequiredDeleteVolumeRequestRequestTypeDef, _OptionalDeleteVolumeRequestRequestTypeDef
):
    pass


DeleteVolumeRequestVolumeDeleteTypeDef = TypedDict(
    "DeleteVolumeRequestVolumeDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef",
    {
        "ConnectionNotificationIds": Sequence[str],
    },
)
_OptionalDeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef(
    _RequiredDeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef,
    _OptionalDeleteVpcEndpointConnectionNotificationsRequestRequestTypeDef,
):
    pass


_RequiredDeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef",
    {
        "ServiceIds": Sequence[str],
    },
)
_OptionalDeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef(
    _RequiredDeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef,
    _OptionalDeleteVpcEndpointServiceConfigurationsRequestRequestTypeDef,
):
    pass


_RequiredDeleteVpcEndpointsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpcEndpointsRequestRequestTypeDef",
    {
        "VpcEndpointIds": Sequence[str],
    },
)
_OptionalDeleteVpcEndpointsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpcEndpointsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpcEndpointsRequestRequestTypeDef(
    _RequiredDeleteVpcEndpointsRequestRequestTypeDef,
    _OptionalDeleteVpcEndpointsRequestRequestTypeDef,
):
    pass


_RequiredDeleteVpcPeeringConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpcPeeringConnectionRequestRequestTypeDef",
    {
        "VpcPeeringConnectionId": str,
    },
)
_OptionalDeleteVpcPeeringConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpcPeeringConnectionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpcPeeringConnectionRequestRequestTypeDef(
    _RequiredDeleteVpcPeeringConnectionRequestRequestTypeDef,
    _OptionalDeleteVpcPeeringConnectionRequestRequestTypeDef,
):
    pass


DeleteVpcPeeringConnectionRequestVpcPeeringConnectionDeleteTypeDef = TypedDict(
    "DeleteVpcPeeringConnectionRequestVpcPeeringConnectionDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteVpcRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpcRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalDeleteVpcRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpcRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpcRequestRequestTypeDef(
    _RequiredDeleteVpcRequestRequestTypeDef, _OptionalDeleteVpcRequestRequestTypeDef
):
    pass


DeleteVpcRequestVpcDeleteTypeDef = TypedDict(
    "DeleteVpcRequestVpcDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeleteVpnConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpnConnectionRequestRequestTypeDef",
    {
        "VpnConnectionId": str,
    },
)
_OptionalDeleteVpnConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpnConnectionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpnConnectionRequestRequestTypeDef(
    _RequiredDeleteVpnConnectionRequestRequestTypeDef,
    _OptionalDeleteVpnConnectionRequestRequestTypeDef,
):
    pass


DeleteVpnConnectionRouteRequestRequestTypeDef = TypedDict(
    "DeleteVpnConnectionRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "VpnConnectionId": str,
    },
)

_RequiredDeleteVpnGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVpnGatewayRequestRequestTypeDef",
    {
        "VpnGatewayId": str,
    },
)
_OptionalDeleteVpnGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVpnGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeleteVpnGatewayRequestRequestTypeDef(
    _RequiredDeleteVpnGatewayRequestRequestTypeDef, _OptionalDeleteVpnGatewayRequestRequestTypeDef
):
    pass


_RequiredDeprovisionByoipCidrRequestRequestTypeDef = TypedDict(
    "_RequiredDeprovisionByoipCidrRequestRequestTypeDef",
    {
        "Cidr": str,
    },
)
_OptionalDeprovisionByoipCidrRequestRequestTypeDef = TypedDict(
    "_OptionalDeprovisionByoipCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeprovisionByoipCidrRequestRequestTypeDef(
    _RequiredDeprovisionByoipCidrRequestRequestTypeDef,
    _OptionalDeprovisionByoipCidrRequestRequestTypeDef,
):
    pass


_RequiredDeprovisionIpamPoolCidrRequestRequestTypeDef = TypedDict(
    "_RequiredDeprovisionIpamPoolCidrRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalDeprovisionIpamPoolCidrRequestRequestTypeDef = TypedDict(
    "_OptionalDeprovisionIpamPoolCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Cidr": str,
    },
    total=False,
)


class DeprovisionIpamPoolCidrRequestRequestTypeDef(
    _RequiredDeprovisionIpamPoolCidrRequestRequestTypeDef,
    _OptionalDeprovisionIpamPoolCidrRequestRequestTypeDef,
):
    pass


_RequiredDeprovisionPublicIpv4PoolCidrRequestRequestTypeDef = TypedDict(
    "_RequiredDeprovisionPublicIpv4PoolCidrRequestRequestTypeDef",
    {
        "PoolId": str,
        "Cidr": str,
    },
)
_OptionalDeprovisionPublicIpv4PoolCidrRequestRequestTypeDef = TypedDict(
    "_OptionalDeprovisionPublicIpv4PoolCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeprovisionPublicIpv4PoolCidrRequestRequestTypeDef(
    _RequiredDeprovisionPublicIpv4PoolCidrRequestRequestTypeDef,
    _OptionalDeprovisionPublicIpv4PoolCidrRequestRequestTypeDef,
):
    pass


DeregisterImageRequestImageDeregisterTypeDef = TypedDict(
    "DeregisterImageRequestImageDeregisterTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDeregisterImageRequestRequestTypeDef = TypedDict(
    "_RequiredDeregisterImageRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalDeregisterImageRequestRequestTypeDef = TypedDict(
    "_OptionalDeregisterImageRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DeregisterImageRequestRequestTypeDef(
    _RequiredDeregisterImageRequestRequestTypeDef, _OptionalDeregisterImageRequestRequestTypeDef
):
    pass


DeregisterInstanceTagAttributeRequestTypeDef = TypedDict(
    "DeregisterInstanceTagAttributeRequestTypeDef",
    {
        "IncludeAllTagsOfInstance": bool,
        "InstanceTagKeys": Sequence[str],
    },
    total=False,
)

InstanceTagNotificationAttributeTypeDef = TypedDict(
    "InstanceTagNotificationAttributeTypeDef",
    {
        "InstanceTagKeys": List[str],
        "IncludeAllTagsOfInstance": bool,
    },
    total=False,
)

DeregisterTransitGatewayMulticastGroupMembersRequestRequestTypeDef = TypedDict(
    "DeregisterTransitGatewayMulticastGroupMembersRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "GroupIpAddress": str,
        "NetworkInterfaceIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

TransitGatewayMulticastDeregisteredGroupMembersTypeDef = TypedDict(
    "TransitGatewayMulticastDeregisteredGroupMembersTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "DeregisteredNetworkInterfaceIds": List[str],
        "GroupIpAddress": str,
    },
    total=False,
)

DeregisterTransitGatewayMulticastGroupSourcesRequestRequestTypeDef = TypedDict(
    "DeregisterTransitGatewayMulticastGroupSourcesRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "GroupIpAddress": str,
        "NetworkInterfaceIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

TransitGatewayMulticastDeregisteredGroupSourcesTypeDef = TypedDict(
    "TransitGatewayMulticastDeregisteredGroupSourcesTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "DeregisteredNetworkInterfaceIds": List[str],
        "GroupIpAddress": str,
    },
    total=False,
)

DescribeAccountAttributesRequestRequestTypeDef = TypedDict(
    "DescribeAccountAttributesRequestRequestTypeDef",
    {
        "AttributeNames": Sequence[AccountAttributeNameType],
        "DryRun": bool,
    },
    total=False,
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

DescribeAddressesAttributeRequestRequestTypeDef = TypedDict(
    "DescribeAddressesAttributeRequestRequestTypeDef",
    {
        "AllocationIds": Sequence[str],
        "Attribute": Literal["domain-name"],
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)

FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": str,
        "Values": Sequence[str],
    },
    total=False,
)

DescribeAggregateIdFormatRequestRequestTypeDef = TypedDict(
    "DescribeAggregateIdFormatRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

IdFormatTypeDef = TypedDict(
    "IdFormatTypeDef",
    {
        "Deadline": datetime,
        "Resource": str,
        "UseLongIds": bool,
    },
    total=False,
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": int,
        "MaxAttempts": int,
    },
    total=False,
)

_RequiredDescribeByoipCidrsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeByoipCidrsRequestRequestTypeDef",
    {
        "MaxResults": int,
    },
)
_OptionalDescribeByoipCidrsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeByoipCidrsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "NextToken": str,
    },
    total=False,
)


class DescribeByoipCidrsRequestRequestTypeDef(
    _RequiredDescribeByoipCidrsRequestRequestTypeDef,
    _OptionalDescribeByoipCidrsRequestRequestTypeDef,
):
    pass


DescribeConversionTasksRequestRequestTypeDef = TypedDict(
    "DescribeConversionTasksRequestRequestTypeDef",
    {
        "ConversionTaskIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

FastLaunchLaunchTemplateSpecificationResponseTypeDef = TypedDict(
    "FastLaunchLaunchTemplateSpecificationResponseTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "Version": str,
    },
    total=False,
)

FastLaunchSnapshotConfigurationResponseTypeDef = TypedDict(
    "FastLaunchSnapshotConfigurationResponseTypeDef",
    {
        "TargetResourceCount": int,
    },
    total=False,
)

DescribeFastSnapshotRestoreSuccessItemTypeDef = TypedDict(
    "DescribeFastSnapshotRestoreSuccessItemTypeDef",
    {
        "SnapshotId": str,
        "AvailabilityZone": str,
        "State": FastSnapshotRestoreStateCodeType,
        "StateTransitionReason": str,
        "OwnerId": str,
        "OwnerAlias": str,
        "EnablingTime": datetime,
        "OptimizingTime": datetime,
        "EnabledTime": datetime,
        "DisablingTime": datetime,
        "DisabledTime": datetime,
    },
    total=False,
)

_RequiredDescribeFleetHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeFleetHistoryRequestRequestTypeDef",
    {
        "FleetId": str,
        "StartTime": Union[datetime, str],
    },
)
_OptionalDescribeFleetHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeFleetHistoryRequestRequestTypeDef",
    {
        "DryRun": bool,
        "EventType": FleetEventTypeType,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeFleetHistoryRequestRequestTypeDef(
    _RequiredDescribeFleetHistoryRequestRequestTypeDef,
    _OptionalDescribeFleetHistoryRequestRequestTypeDef,
):
    pass


_RequiredDescribeFpgaImageAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeFpgaImageAttributeRequestRequestTypeDef",
    {
        "FpgaImageId": str,
        "Attribute": FpgaImageAttributeNameType,
    },
)
_OptionalDescribeFpgaImageAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeFpgaImageAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeFpgaImageAttributeRequestRequestTypeDef(
    _RequiredDescribeFpgaImageAttributeRequestRequestTypeDef,
    _OptionalDescribeFpgaImageAttributeRequestRequestTypeDef,
):
    pass


HostOfferingTypeDef = TypedDict(
    "HostOfferingTypeDef",
    {
        "CurrencyCode": Literal["USD"],
        "Duration": int,
        "HourlyPrice": str,
        "InstanceFamily": str,
        "OfferingId": str,
        "PaymentOption": PaymentOptionType,
        "UpfrontPrice": str,
    },
    total=False,
)

DescribeIdFormatRequestRequestTypeDef = TypedDict(
    "DescribeIdFormatRequestRequestTypeDef",
    {
        "Resource": str,
    },
    total=False,
)

_RequiredDescribeIdentityIdFormatRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeIdentityIdFormatRequestRequestTypeDef",
    {
        "PrincipalArn": str,
    },
)
_OptionalDescribeIdentityIdFormatRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeIdentityIdFormatRequestRequestTypeDef",
    {
        "Resource": str,
    },
    total=False,
)


class DescribeIdentityIdFormatRequestRequestTypeDef(
    _RequiredDescribeIdentityIdFormatRequestRequestTypeDef,
    _OptionalDescribeIdentityIdFormatRequestRequestTypeDef,
):
    pass


_RequiredDescribeImageAttributeRequestImageDescribeAttributeTypeDef = TypedDict(
    "_RequiredDescribeImageAttributeRequestImageDescribeAttributeTypeDef",
    {
        "Attribute": ImageAttributeNameType,
    },
)
_OptionalDescribeImageAttributeRequestImageDescribeAttributeTypeDef = TypedDict(
    "_OptionalDescribeImageAttributeRequestImageDescribeAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeImageAttributeRequestImageDescribeAttributeTypeDef(
    _RequiredDescribeImageAttributeRequestImageDescribeAttributeTypeDef,
    _OptionalDescribeImageAttributeRequestImageDescribeAttributeTypeDef,
):
    pass


_RequiredDescribeImageAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeImageAttributeRequestRequestTypeDef",
    {
        "Attribute": ImageAttributeNameType,
        "ImageId": str,
    },
)
_OptionalDescribeImageAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeImageAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeImageAttributeRequestRequestTypeDef(
    _RequiredDescribeImageAttributeRequestRequestTypeDef,
    _OptionalDescribeImageAttributeRequestRequestTypeDef,
):
    pass


_RequiredDescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef = TypedDict(
    "_RequiredDescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
    },
)
_OptionalDescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef = TypedDict(
    "_OptionalDescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef(
    _RequiredDescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef,
    _OptionalDescribeInstanceAttributeRequestInstanceDescribeAttributeTypeDef,
):
    pass


_RequiredDescribeInstanceAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeInstanceAttributeRequestRequestTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
        "InstanceId": str,
    },
)
_OptionalDescribeInstanceAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeInstanceAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeInstanceAttributeRequestRequestTypeDef(
    _RequiredDescribeInstanceAttributeRequestRequestTypeDef,
    _OptionalDescribeInstanceAttributeRequestRequestTypeDef,
):
    pass


InstanceCreditSpecificationTypeDef = TypedDict(
    "InstanceCreditSpecificationTypeDef",
    {
        "InstanceId": str,
        "CpuCredits": str,
    },
    total=False,
)

DescribeInstanceEventNotificationAttributesRequestRequestTypeDef = TypedDict(
    "DescribeInstanceEventNotificationAttributesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

InstanceTypeOfferingTypeDef = TypedDict(
    "InstanceTypeOfferingTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "LocationType": LocationTypeType,
        "Location": str,
    },
    total=False,
)

MovingAddressStatusTypeDef = TypedDict(
    "MovingAddressStatusTypeDef",
    {
        "MoveStatus": MoveStatusType,
        "PublicIp": str,
    },
    total=False,
)

DescribeNetworkInterfaceAttributeRequestNetworkInterfaceDescribeAttributeTypeDef = TypedDict(
    "DescribeNetworkInterfaceAttributeRequestNetworkInterfaceDescribeAttributeTypeDef",
    {
        "Attribute": NetworkInterfaceAttributeType,
        "DryRun": bool,
    },
    total=False,
)

_RequiredDescribeNetworkInterfaceAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeNetworkInterfaceAttributeRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalDescribeNetworkInterfaceAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeNetworkInterfaceAttributeRequestRequestTypeDef",
    {
        "Attribute": NetworkInterfaceAttributeType,
        "DryRun": bool,
    },
    total=False,
)


class DescribeNetworkInterfaceAttributeRequestRequestTypeDef(
    _RequiredDescribeNetworkInterfaceAttributeRequestRequestTypeDef,
    _OptionalDescribeNetworkInterfaceAttributeRequestRequestTypeDef,
):
    pass


NetworkInterfaceAttachmentTypeDef = TypedDict(
    "NetworkInterfaceAttachmentTypeDef",
    {
        "AttachTime": datetime,
        "AttachmentId": str,
        "DeleteOnTermination": bool,
        "DeviceIndex": int,
        "NetworkCardIndex": int,
        "InstanceId": str,
        "InstanceOwnerId": str,
        "Status": AttachmentStatusType,
    },
    total=False,
)

PrefixListTypeDef = TypedDict(
    "PrefixListTypeDef",
    {
        "Cidrs": List[str],
        "PrefixListId": str,
        "PrefixListName": str,
    },
    total=False,
)

DescribePrincipalIdFormatRequestRequestTypeDef = TypedDict(
    "DescribePrincipalIdFormatRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Resources": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

RegionTypeDef = TypedDict(
    "RegionTypeDef",
    {
        "Endpoint": str,
        "RegionName": str,
        "OptInStatus": str,
    },
    total=False,
)

ScheduledInstanceRecurrenceRequestTypeDef = TypedDict(
    "ScheduledInstanceRecurrenceRequestTypeDef",
    {
        "Frequency": str,
        "Interval": int,
        "OccurrenceDays": Sequence[int],
        "OccurrenceRelativeToEnd": bool,
        "OccurrenceUnit": str,
    },
    total=False,
)

SlotDateTimeRangeRequestTypeDef = TypedDict(
    "SlotDateTimeRangeRequestTypeDef",
    {
        "EarliestTime": Union[datetime, str],
        "LatestTime": Union[datetime, str],
    },
)

SlotStartTimeRangeRequestTypeDef = TypedDict(
    "SlotStartTimeRangeRequestTypeDef",
    {
        "EarliestTime": Union[datetime, str],
        "LatestTime": Union[datetime, str],
    },
    total=False,
)

_RequiredDescribeSecurityGroupReferencesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeSecurityGroupReferencesRequestRequestTypeDef",
    {
        "GroupId": Sequence[str],
    },
)
_OptionalDescribeSecurityGroupReferencesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeSecurityGroupReferencesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeSecurityGroupReferencesRequestRequestTypeDef(
    _RequiredDescribeSecurityGroupReferencesRequestRequestTypeDef,
    _OptionalDescribeSecurityGroupReferencesRequestRequestTypeDef,
):
    pass


SecurityGroupReferenceTypeDef = TypedDict(
    "SecurityGroupReferenceTypeDef",
    {
        "GroupId": str,
        "ReferencingVpcId": str,
        "VpcPeeringConnectionId": str,
    },
    total=False,
)

_RequiredDescribeSnapshotAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeSnapshotAttributeRequestRequestTypeDef",
    {
        "Attribute": SnapshotAttributeNameType,
        "SnapshotId": str,
    },
)
_OptionalDescribeSnapshotAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeSnapshotAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeSnapshotAttributeRequestRequestTypeDef(
    _RequiredDescribeSnapshotAttributeRequestRequestTypeDef,
    _OptionalDescribeSnapshotAttributeRequestRequestTypeDef,
):
    pass


_RequiredDescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef = TypedDict(
    "_RequiredDescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef",
    {
        "Attribute": SnapshotAttributeNameType,
    },
)
_OptionalDescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef = TypedDict(
    "_OptionalDescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef(
    _RequiredDescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef,
    _OptionalDescribeSnapshotAttributeRequestSnapshotDescribeAttributeTypeDef,
):
    pass


ProductCodeTypeDef = TypedDict(
    "ProductCodeTypeDef",
    {
        "ProductCodeId": str,
        "ProductCodeType": ProductCodeValuesType,
    },
    total=False,
)

DescribeSpotDatafeedSubscriptionRequestRequestTypeDef = TypedDict(
    "DescribeSpotDatafeedSubscriptionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDescribeSpotFleetInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeSpotFleetInstancesRequestRequestTypeDef",
    {
        "SpotFleetRequestId": str,
    },
)
_OptionalDescribeSpotFleetInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeSpotFleetInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeSpotFleetInstancesRequestRequestTypeDef(
    _RequiredDescribeSpotFleetInstancesRequestRequestTypeDef,
    _OptionalDescribeSpotFleetInstancesRequestRequestTypeDef,
):
    pass


_RequiredDescribeSpotFleetRequestHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeSpotFleetRequestHistoryRequestRequestTypeDef",
    {
        "SpotFleetRequestId": str,
        "StartTime": Union[datetime, str],
    },
)
_OptionalDescribeSpotFleetRequestHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeSpotFleetRequestHistoryRequestRequestTypeDef",
    {
        "DryRun": bool,
        "EventType": EventTypeType,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeSpotFleetRequestHistoryRequestRequestTypeDef(
    _RequiredDescribeSpotFleetRequestHistoryRequestRequestTypeDef,
    _OptionalDescribeSpotFleetRequestHistoryRequestRequestTypeDef,
):
    pass


DescribeSpotFleetRequestsRequestRequestTypeDef = TypedDict(
    "DescribeSpotFleetRequestsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "SpotFleetRequestIds": Sequence[str],
    },
    total=False,
)

SpotPriceTypeDef = TypedDict(
    "SpotPriceTypeDef",
    {
        "AvailabilityZone": str,
        "InstanceType": InstanceTypeType,
        "ProductDescription": RIProductDescriptionType,
        "SpotPrice": str,
        "Timestamp": datetime,
    },
    total=False,
)

_RequiredDescribeStaleSecurityGroupsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeStaleSecurityGroupsRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalDescribeStaleSecurityGroupsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeStaleSecurityGroupsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeStaleSecurityGroupsRequestRequestTypeDef(
    _RequiredDescribeStaleSecurityGroupsRequestRequestTypeDef,
    _OptionalDescribeStaleSecurityGroupsRequestRequestTypeDef,
):
    pass


StoreImageTaskResultTypeDef = TypedDict(
    "StoreImageTaskResultTypeDef",
    {
        "AmiId": str,
        "TaskStartTime": datetime,
        "Bucket": str,
        "S3objectKey": str,
        "ProgressPercentage": int,
        "StoreTaskState": str,
        "StoreTaskFailureReason": str,
    },
    total=False,
)

TagDescriptionTypeDef = TypedDict(
    "TagDescriptionTypeDef",
    {
        "Key": str,
        "ResourceId": str,
        "ResourceType": ResourceTypeType,
        "Value": str,
    },
    total=False,
)

_RequiredDescribeVolumeAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeVolumeAttributeRequestRequestTypeDef",
    {
        "Attribute": VolumeAttributeNameType,
        "VolumeId": str,
    },
)
_OptionalDescribeVolumeAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeVolumeAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeVolumeAttributeRequestRequestTypeDef(
    _RequiredDescribeVolumeAttributeRequestRequestTypeDef,
    _OptionalDescribeVolumeAttributeRequestRequestTypeDef,
):
    pass


_RequiredDescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef = TypedDict(
    "_RequiredDescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef",
    {
        "Attribute": VolumeAttributeNameType,
    },
)
_OptionalDescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef = TypedDict(
    "_OptionalDescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef(
    _RequiredDescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef,
    _OptionalDescribeVolumeAttributeRequestVolumeDescribeAttributeTypeDef,
):
    pass


VolumeModificationTypeDef = TypedDict(
    "VolumeModificationTypeDef",
    {
        "VolumeId": str,
        "ModificationState": VolumeModificationStateType,
        "StatusMessage": str,
        "TargetSize": int,
        "TargetIops": int,
        "TargetVolumeType": VolumeTypeType,
        "TargetThroughput": int,
        "TargetMultiAttachEnabled": bool,
        "OriginalSize": int,
        "OriginalIops": int,
        "OriginalVolumeType": VolumeTypeType,
        "OriginalThroughput": int,
        "OriginalMultiAttachEnabled": bool,
        "Progress": int,
        "StartTime": datetime,
        "EndTime": datetime,
    },
    total=False,
)

_RequiredDescribeVpcAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeVpcAttributeRequestRequestTypeDef",
    {
        "Attribute": VpcAttributeNameType,
        "VpcId": str,
    },
)
_OptionalDescribeVpcAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeVpcAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeVpcAttributeRequestRequestTypeDef(
    _RequiredDescribeVpcAttributeRequestRequestTypeDef,
    _OptionalDescribeVpcAttributeRequestRequestTypeDef,
):
    pass


_RequiredDescribeVpcAttributeRequestVpcDescribeAttributeTypeDef = TypedDict(
    "_RequiredDescribeVpcAttributeRequestVpcDescribeAttributeTypeDef",
    {
        "Attribute": VpcAttributeNameType,
    },
)
_OptionalDescribeVpcAttributeRequestVpcDescribeAttributeTypeDef = TypedDict(
    "_OptionalDescribeVpcAttributeRequestVpcDescribeAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DescribeVpcAttributeRequestVpcDescribeAttributeTypeDef(
    _RequiredDescribeVpcAttributeRequestVpcDescribeAttributeTypeDef,
    _OptionalDescribeVpcAttributeRequestVpcDescribeAttributeTypeDef,
):
    pass


DescribeVpcClassicLinkDnsSupportRequestRequestTypeDef = TypedDict(
    "DescribeVpcClassicLinkDnsSupportRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "VpcIds": Sequence[str],
    },
    total=False,
)

DestinationOptionsResponseTypeDef = TypedDict(
    "DestinationOptionsResponseTypeDef",
    {
        "FileFormat": DestinationFileFormatType,
        "HiveCompatiblePartitions": bool,
        "PerHourPartition": bool,
    },
    total=False,
)

_RequiredDetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef = TypedDict(
    "_RequiredDetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalDetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef = TypedDict(
    "_OptionalDetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef(
    _RequiredDetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef,
    _OptionalDetachClassicLinkVpcRequestInstanceDetachClassicLinkVpcTypeDef,
):
    pass


_RequiredDetachClassicLinkVpcRequestRequestTypeDef = TypedDict(
    "_RequiredDetachClassicLinkVpcRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VpcId": str,
    },
)
_OptionalDetachClassicLinkVpcRequestRequestTypeDef = TypedDict(
    "_OptionalDetachClassicLinkVpcRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachClassicLinkVpcRequestRequestTypeDef(
    _RequiredDetachClassicLinkVpcRequestRequestTypeDef,
    _OptionalDetachClassicLinkVpcRequestRequestTypeDef,
):
    pass


_RequiredDetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef = TypedDict(
    "_RequiredDetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalDetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef = TypedDict(
    "_OptionalDetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef(
    _RequiredDetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef,
    _OptionalDetachClassicLinkVpcRequestVpcDetachClassicLinkInstanceTypeDef,
):
    pass


_RequiredDetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef = TypedDict(
    "_RequiredDetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalDetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef = TypedDict(
    "_OptionalDetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef(
    _RequiredDetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef,
    _OptionalDetachInternetGatewayRequestInternetGatewayDetachFromVpcTypeDef,
):
    pass


_RequiredDetachInternetGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDetachInternetGatewayRequestRequestTypeDef",
    {
        "InternetGatewayId": str,
        "VpcId": str,
    },
)
_OptionalDetachInternetGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDetachInternetGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachInternetGatewayRequestRequestTypeDef(
    _RequiredDetachInternetGatewayRequestRequestTypeDef,
    _OptionalDetachInternetGatewayRequestRequestTypeDef,
):
    pass


_RequiredDetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef = TypedDict(
    "_RequiredDetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef",
    {
        "InternetGatewayId": str,
    },
)
_OptionalDetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef = TypedDict(
    "_OptionalDetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef(
    _RequiredDetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef,
    _OptionalDetachInternetGatewayRequestVpcDetachInternetGatewayTypeDef,
):
    pass


_RequiredDetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef = TypedDict(
    "_RequiredDetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef",
    {
        "AttachmentId": str,
    },
)
_OptionalDetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef = TypedDict(
    "_OptionalDetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef",
    {
        "DryRun": bool,
        "Force": bool,
    },
    total=False,
)


class DetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef(
    _RequiredDetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef,
    _OptionalDetachNetworkInterfaceRequestNetworkInterfaceDetachTypeDef,
):
    pass


_RequiredDetachNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_RequiredDetachNetworkInterfaceRequestRequestTypeDef",
    {
        "AttachmentId": str,
    },
)
_OptionalDetachNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_OptionalDetachNetworkInterfaceRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Force": bool,
    },
    total=False,
)


class DetachNetworkInterfaceRequestRequestTypeDef(
    _RequiredDetachNetworkInterfaceRequestRequestTypeDef,
    _OptionalDetachNetworkInterfaceRequestRequestTypeDef,
):
    pass


_RequiredDetachVolumeRequestInstanceDetachVolumeTypeDef = TypedDict(
    "_RequiredDetachVolumeRequestInstanceDetachVolumeTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalDetachVolumeRequestInstanceDetachVolumeTypeDef = TypedDict(
    "_OptionalDetachVolumeRequestInstanceDetachVolumeTypeDef",
    {
        "Device": str,
        "Force": bool,
        "DryRun": bool,
    },
    total=False,
)


class DetachVolumeRequestInstanceDetachVolumeTypeDef(
    _RequiredDetachVolumeRequestInstanceDetachVolumeTypeDef,
    _OptionalDetachVolumeRequestInstanceDetachVolumeTypeDef,
):
    pass


_RequiredDetachVolumeRequestRequestTypeDef = TypedDict(
    "_RequiredDetachVolumeRequestRequestTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalDetachVolumeRequestRequestTypeDef = TypedDict(
    "_OptionalDetachVolumeRequestRequestTypeDef",
    {
        "Device": str,
        "Force": bool,
        "InstanceId": str,
        "DryRun": bool,
    },
    total=False,
)


class DetachVolumeRequestRequestTypeDef(
    _RequiredDetachVolumeRequestRequestTypeDef, _OptionalDetachVolumeRequestRequestTypeDef
):
    pass


DetachVolumeRequestVolumeDetachFromInstanceTypeDef = TypedDict(
    "DetachVolumeRequestVolumeDetachFromInstanceTypeDef",
    {
        "Device": str,
        "Force": bool,
        "InstanceId": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredDetachVpnGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredDetachVpnGatewayRequestRequestTypeDef",
    {
        "VpcId": str,
        "VpnGatewayId": str,
    },
)
_OptionalDetachVpnGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalDetachVpnGatewayRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DetachVpnGatewayRequestRequestTypeDef(
    _RequiredDetachVpnGatewayRequestRequestTypeDef, _OptionalDetachVpnGatewayRequestRequestTypeDef
):
    pass


DisableEbsEncryptionByDefaultRequestRequestTypeDef = TypedDict(
    "DisableEbsEncryptionByDefaultRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDisableFastLaunchRequestRequestTypeDef = TypedDict(
    "_RequiredDisableFastLaunchRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalDisableFastLaunchRequestRequestTypeDef = TypedDict(
    "_OptionalDisableFastLaunchRequestRequestTypeDef",
    {
        "Force": bool,
        "DryRun": bool,
    },
    total=False,
)


class DisableFastLaunchRequestRequestTypeDef(
    _RequiredDisableFastLaunchRequestRequestTypeDef, _OptionalDisableFastLaunchRequestRequestTypeDef
):
    pass


DisableFastSnapshotRestoreStateErrorTypeDef = TypedDict(
    "DisableFastSnapshotRestoreStateErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

DisableFastSnapshotRestoreSuccessItemTypeDef = TypedDict(
    "DisableFastSnapshotRestoreSuccessItemTypeDef",
    {
        "SnapshotId": str,
        "AvailabilityZone": str,
        "State": FastSnapshotRestoreStateCodeType,
        "StateTransitionReason": str,
        "OwnerId": str,
        "OwnerAlias": str,
        "EnablingTime": datetime,
        "OptimizingTime": datetime,
        "EnabledTime": datetime,
        "DisablingTime": datetime,
        "DisabledTime": datetime,
    },
    total=False,
)

_RequiredDisableFastSnapshotRestoresRequestRequestTypeDef = TypedDict(
    "_RequiredDisableFastSnapshotRestoresRequestRequestTypeDef",
    {
        "AvailabilityZones": Sequence[str],
        "SourceSnapshotIds": Sequence[str],
    },
)
_OptionalDisableFastSnapshotRestoresRequestRequestTypeDef = TypedDict(
    "_OptionalDisableFastSnapshotRestoresRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisableFastSnapshotRestoresRequestRequestTypeDef(
    _RequiredDisableFastSnapshotRestoresRequestRequestTypeDef,
    _OptionalDisableFastSnapshotRestoresRequestRequestTypeDef,
):
    pass


_RequiredDisableImageDeprecationRequestRequestTypeDef = TypedDict(
    "_RequiredDisableImageDeprecationRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalDisableImageDeprecationRequestRequestTypeDef = TypedDict(
    "_OptionalDisableImageDeprecationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisableImageDeprecationRequestRequestTypeDef(
    _RequiredDisableImageDeprecationRequestRequestTypeDef,
    _OptionalDisableImageDeprecationRequestRequestTypeDef,
):
    pass


_RequiredDisableIpamOrganizationAdminAccountRequestRequestTypeDef = TypedDict(
    "_RequiredDisableIpamOrganizationAdminAccountRequestRequestTypeDef",
    {
        "DelegatedAdminAccountId": str,
    },
)
_OptionalDisableIpamOrganizationAdminAccountRequestRequestTypeDef = TypedDict(
    "_OptionalDisableIpamOrganizationAdminAccountRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisableIpamOrganizationAdminAccountRequestRequestTypeDef(
    _RequiredDisableIpamOrganizationAdminAccountRequestRequestTypeDef,
    _OptionalDisableIpamOrganizationAdminAccountRequestRequestTypeDef,
):
    pass


DisableSerialConsoleAccessRequestRequestTypeDef = TypedDict(
    "DisableSerialConsoleAccessRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDisableTransitGatewayRouteTablePropagationRequestRequestTypeDef = TypedDict(
    "_RequiredDisableTransitGatewayRouteTablePropagationRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalDisableTransitGatewayRouteTablePropagationRequestRequestTypeDef = TypedDict(
    "_OptionalDisableTransitGatewayRouteTablePropagationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisableTransitGatewayRouteTablePropagationRequestRequestTypeDef(
    _RequiredDisableTransitGatewayRouteTablePropagationRequestRequestTypeDef,
    _OptionalDisableTransitGatewayRouteTablePropagationRequestRequestTypeDef,
):
    pass


TransitGatewayPropagationTypeDef = TypedDict(
    "TransitGatewayPropagationTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "TransitGatewayRouteTableId": str,
        "State": TransitGatewayPropagationStateType,
    },
    total=False,
)

_RequiredDisableVgwRoutePropagationRequestRequestTypeDef = TypedDict(
    "_RequiredDisableVgwRoutePropagationRequestRequestTypeDef",
    {
        "GatewayId": str,
        "RouteTableId": str,
    },
)
_OptionalDisableVgwRoutePropagationRequestRequestTypeDef = TypedDict(
    "_OptionalDisableVgwRoutePropagationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisableVgwRoutePropagationRequestRequestTypeDef(
    _RequiredDisableVgwRoutePropagationRequestRequestTypeDef,
    _OptionalDisableVgwRoutePropagationRequestRequestTypeDef,
):
    pass


DisableVpcClassicLinkDnsSupportRequestRequestTypeDef = TypedDict(
    "DisableVpcClassicLinkDnsSupportRequestRequestTypeDef",
    {
        "VpcId": str,
    },
    total=False,
)

_RequiredDisableVpcClassicLinkRequestRequestTypeDef = TypedDict(
    "_RequiredDisableVpcClassicLinkRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalDisableVpcClassicLinkRequestRequestTypeDef = TypedDict(
    "_OptionalDisableVpcClassicLinkRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisableVpcClassicLinkRequestRequestTypeDef(
    _RequiredDisableVpcClassicLinkRequestRequestTypeDef,
    _OptionalDisableVpcClassicLinkRequestRequestTypeDef,
):
    pass


DisableVpcClassicLinkRequestVpcDisableClassicLinkTypeDef = TypedDict(
    "DisableVpcClassicLinkRequestVpcDisableClassicLinkTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

DisassociateAddressRequestClassicAddressDisassociateTypeDef = TypedDict(
    "DisassociateAddressRequestClassicAddressDisassociateTypeDef",
    {
        "AssociationId": str,
        "PublicIp": str,
        "DryRun": bool,
    },
    total=False,
)

DisassociateAddressRequestNetworkInterfaceAssociationDeleteTypeDef = TypedDict(
    "DisassociateAddressRequestNetworkInterfaceAssociationDeleteTypeDef",
    {
        "PublicIp": str,
        "DryRun": bool,
    },
    total=False,
)

DisassociateAddressRequestRequestTypeDef = TypedDict(
    "DisassociateAddressRequestRequestTypeDef",
    {
        "AssociationId": str,
        "PublicIp": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredDisassociateClientVpnTargetNetworkRequestRequestTypeDef = TypedDict(
    "_RequiredDisassociateClientVpnTargetNetworkRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "AssociationId": str,
    },
)
_OptionalDisassociateClientVpnTargetNetworkRequestRequestTypeDef = TypedDict(
    "_OptionalDisassociateClientVpnTargetNetworkRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisassociateClientVpnTargetNetworkRequestRequestTypeDef(
    _RequiredDisassociateClientVpnTargetNetworkRequestRequestTypeDef,
    _OptionalDisassociateClientVpnTargetNetworkRequestRequestTypeDef,
):
    pass


DisassociateEnclaveCertificateIamRoleRequestRequestTypeDef = TypedDict(
    "DisassociateEnclaveCertificateIamRoleRequestRequestTypeDef",
    {
        "CertificateArn": str,
        "RoleArn": str,
        "DryRun": bool,
    },
    total=False,
)

DisassociateIamInstanceProfileRequestRequestTypeDef = TypedDict(
    "DisassociateIamInstanceProfileRequestRequestTypeDef",
    {
        "AssociationId": str,
    },
)

_RequiredDisassociateRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredDisassociateRouteTableRequestRequestTypeDef",
    {
        "AssociationId": str,
    },
)
_OptionalDisassociateRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalDisassociateRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisassociateRouteTableRequestRequestTypeDef(
    _RequiredDisassociateRouteTableRequestRequestTypeDef,
    _OptionalDisassociateRouteTableRequestRequestTypeDef,
):
    pass


DisassociateRouteTableRequestRouteTableAssociationDeleteTypeDef = TypedDict(
    "DisassociateRouteTableRequestRouteTableAssociationDeleteTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredDisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef = TypedDict(
    "_RequiredDisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef",
    {
        "AssociationId": str,
    },
)
_OptionalDisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef = TypedDict(
    "_OptionalDisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef(
    _RequiredDisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef,
    _OptionalDisassociateRouteTableRequestServiceResourceDisassociateRouteTableTypeDef,
):
    pass


DisassociateSubnetCidrBlockRequestRequestTypeDef = TypedDict(
    "DisassociateSubnetCidrBlockRequestRequestTypeDef",
    {
        "AssociationId": str,
    },
)

DisassociateTransitGatewayMulticastDomainRequestRequestTypeDef = TypedDict(
    "DisassociateTransitGatewayMulticastDomainRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "TransitGatewayAttachmentId": str,
        "SubnetIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

_RequiredDisassociateTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredDisassociateTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalDisassociateTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalDisassociateTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisassociateTransitGatewayRouteTableRequestRequestTypeDef(
    _RequiredDisassociateTransitGatewayRouteTableRequestRequestTypeDef,
    _OptionalDisassociateTransitGatewayRouteTableRequestRequestTypeDef,
):
    pass


_RequiredDisassociateTrunkInterfaceRequestRequestTypeDef = TypedDict(
    "_RequiredDisassociateTrunkInterfaceRequestRequestTypeDef",
    {
        "AssociationId": str,
    },
)
_OptionalDisassociateTrunkInterfaceRequestRequestTypeDef = TypedDict(
    "_OptionalDisassociateTrunkInterfaceRequestRequestTypeDef",
    {
        "ClientToken": str,
        "DryRun": bool,
    },
    total=False,
)


class DisassociateTrunkInterfaceRequestRequestTypeDef(
    _RequiredDisassociateTrunkInterfaceRequestRequestTypeDef,
    _OptionalDisassociateTrunkInterfaceRequestRequestTypeDef,
):
    pass


DisassociateVpcCidrBlockRequestRequestTypeDef = TypedDict(
    "DisassociateVpcCidrBlockRequestRequestTypeDef",
    {
        "AssociationId": str,
    },
)

DiskImageDescriptionTypeDef = TypedDict(
    "DiskImageDescriptionTypeDef",
    {
        "Checksum": str,
        "Format": DiskImageFormatType,
        "ImportManifestUrl": str,
        "Size": int,
    },
    total=False,
)

DiskImageDetailTypeDef = TypedDict(
    "DiskImageDetailTypeDef",
    {
        "Bytes": int,
        "Format": DiskImageFormatType,
        "ImportManifestUrl": str,
    },
)

VolumeDetailTypeDef = TypedDict(
    "VolumeDetailTypeDef",
    {
        "Size": int,
    },
)

DiskImageVolumeDescriptionTypeDef = TypedDict(
    "DiskImageVolumeDescriptionTypeDef",
    {
        "Id": str,
        "Size": int,
    },
    total=False,
)

DiskInfoTypeDef = TypedDict(
    "DiskInfoTypeDef",
    {
        "SizeInGB": int,
        "Count": int,
        "Type": DiskTypeType,
    },
    total=False,
)

DnsEntryTypeDef = TypedDict(
    "DnsEntryTypeDef",
    {
        "DnsName": str,
        "HostedZoneId": str,
    },
    total=False,
)

DnsOptionsTypeDef = TypedDict(
    "DnsOptionsTypeDef",
    {
        "DnsRecordIpType": DnsRecordIpTypeType,
    },
    total=False,
)

DnsServersOptionsModifyStructureTypeDef = TypedDict(
    "DnsServersOptionsModifyStructureTypeDef",
    {
        "CustomDnsServers": Sequence[str],
        "Enabled": bool,
    },
    total=False,
)

EbsOptimizedInfoTypeDef = TypedDict(
    "EbsOptimizedInfoTypeDef",
    {
        "BaselineBandwidthInMbps": int,
        "BaselineThroughputInMBps": float,
        "BaselineIops": int,
        "MaximumBandwidthInMbps": int,
        "MaximumThroughputInMBps": float,
        "MaximumIops": int,
    },
    total=False,
)

EbsInstanceBlockDeviceSpecificationTypeDef = TypedDict(
    "EbsInstanceBlockDeviceSpecificationTypeDef",
    {
        "DeleteOnTermination": bool,
        "VolumeId": str,
    },
    total=False,
)

EbsInstanceBlockDeviceTypeDef = TypedDict(
    "EbsInstanceBlockDeviceTypeDef",
    {
        "AttachTime": datetime,
        "DeleteOnTermination": bool,
        "Status": AttachmentStatusType,
        "VolumeId": str,
    },
    total=False,
)

EfaInfoTypeDef = TypedDict(
    "EfaInfoTypeDef",
    {
        "MaximumEfaInterfaces": int,
    },
    total=False,
)

InternetGatewayAttachmentTypeDef = TypedDict(
    "InternetGatewayAttachmentTypeDef",
    {
        "State": AttachmentStatusType,
        "VpcId": str,
    },
    total=False,
)

ElasticGpuAssociationTypeDef = TypedDict(
    "ElasticGpuAssociationTypeDef",
    {
        "ElasticGpuId": str,
        "ElasticGpuAssociationId": str,
        "ElasticGpuAssociationState": str,
        "ElasticGpuAssociationTime": str,
    },
    total=False,
)

ElasticGpuHealthTypeDef = TypedDict(
    "ElasticGpuHealthTypeDef",
    {
        "Status": ElasticGpuStatusType,
    },
    total=False,
)

ElasticGpuSpecificationResponseTypeDef = TypedDict(
    "ElasticGpuSpecificationResponseTypeDef",
    {
        "Type": str,
    },
    total=False,
)

ElasticGpuSpecificationTypeDef = TypedDict(
    "ElasticGpuSpecificationTypeDef",
    {
        "Type": str,
    },
)

ElasticInferenceAcceleratorAssociationTypeDef = TypedDict(
    "ElasticInferenceAcceleratorAssociationTypeDef",
    {
        "ElasticInferenceAcceleratorArn": str,
        "ElasticInferenceAcceleratorAssociationId": str,
        "ElasticInferenceAcceleratorAssociationState": str,
        "ElasticInferenceAcceleratorAssociationTime": datetime,
    },
    total=False,
)

_RequiredElasticInferenceAcceleratorTypeDef = TypedDict(
    "_RequiredElasticInferenceAcceleratorTypeDef",
    {
        "Type": str,
    },
)
_OptionalElasticInferenceAcceleratorTypeDef = TypedDict(
    "_OptionalElasticInferenceAcceleratorTypeDef",
    {
        "Count": int,
    },
    total=False,
)


class ElasticInferenceAcceleratorTypeDef(
    _RequiredElasticInferenceAcceleratorTypeDef, _OptionalElasticInferenceAcceleratorTypeDef
):
    pass


EnableEbsEncryptionByDefaultRequestRequestTypeDef = TypedDict(
    "EnableEbsEncryptionByDefaultRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredFastLaunchLaunchTemplateSpecificationRequestTypeDef = TypedDict(
    "_RequiredFastLaunchLaunchTemplateSpecificationRequestTypeDef",
    {
        "Version": str,
    },
)
_OptionalFastLaunchLaunchTemplateSpecificationRequestTypeDef = TypedDict(
    "_OptionalFastLaunchLaunchTemplateSpecificationRequestTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
    },
    total=False,
)


class FastLaunchLaunchTemplateSpecificationRequestTypeDef(
    _RequiredFastLaunchLaunchTemplateSpecificationRequestTypeDef,
    _OptionalFastLaunchLaunchTemplateSpecificationRequestTypeDef,
):
    pass


FastLaunchSnapshotConfigurationRequestTypeDef = TypedDict(
    "FastLaunchSnapshotConfigurationRequestTypeDef",
    {
        "TargetResourceCount": int,
    },
    total=False,
)

EnableFastSnapshotRestoreStateErrorTypeDef = TypedDict(
    "EnableFastSnapshotRestoreStateErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

EnableFastSnapshotRestoreSuccessItemTypeDef = TypedDict(
    "EnableFastSnapshotRestoreSuccessItemTypeDef",
    {
        "SnapshotId": str,
        "AvailabilityZone": str,
        "State": FastSnapshotRestoreStateCodeType,
        "StateTransitionReason": str,
        "OwnerId": str,
        "OwnerAlias": str,
        "EnablingTime": datetime,
        "OptimizingTime": datetime,
        "EnabledTime": datetime,
        "DisablingTime": datetime,
        "DisabledTime": datetime,
    },
    total=False,
)

_RequiredEnableFastSnapshotRestoresRequestRequestTypeDef = TypedDict(
    "_RequiredEnableFastSnapshotRestoresRequestRequestTypeDef",
    {
        "AvailabilityZones": Sequence[str],
        "SourceSnapshotIds": Sequence[str],
    },
)
_OptionalEnableFastSnapshotRestoresRequestRequestTypeDef = TypedDict(
    "_OptionalEnableFastSnapshotRestoresRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableFastSnapshotRestoresRequestRequestTypeDef(
    _RequiredEnableFastSnapshotRestoresRequestRequestTypeDef,
    _OptionalEnableFastSnapshotRestoresRequestRequestTypeDef,
):
    pass


_RequiredEnableImageDeprecationRequestRequestTypeDef = TypedDict(
    "_RequiredEnableImageDeprecationRequestRequestTypeDef",
    {
        "ImageId": str,
        "DeprecateAt": Union[datetime, str],
    },
)
_OptionalEnableImageDeprecationRequestRequestTypeDef = TypedDict(
    "_OptionalEnableImageDeprecationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableImageDeprecationRequestRequestTypeDef(
    _RequiredEnableImageDeprecationRequestRequestTypeDef,
    _OptionalEnableImageDeprecationRequestRequestTypeDef,
):
    pass


_RequiredEnableIpamOrganizationAdminAccountRequestRequestTypeDef = TypedDict(
    "_RequiredEnableIpamOrganizationAdminAccountRequestRequestTypeDef",
    {
        "DelegatedAdminAccountId": str,
    },
)
_OptionalEnableIpamOrganizationAdminAccountRequestRequestTypeDef = TypedDict(
    "_OptionalEnableIpamOrganizationAdminAccountRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableIpamOrganizationAdminAccountRequestRequestTypeDef(
    _RequiredEnableIpamOrganizationAdminAccountRequestRequestTypeDef,
    _OptionalEnableIpamOrganizationAdminAccountRequestRequestTypeDef,
):
    pass


EnableSerialConsoleAccessRequestRequestTypeDef = TypedDict(
    "EnableSerialConsoleAccessRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredEnableTransitGatewayRouteTablePropagationRequestRequestTypeDef = TypedDict(
    "_RequiredEnableTransitGatewayRouteTablePropagationRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalEnableTransitGatewayRouteTablePropagationRequestRequestTypeDef = TypedDict(
    "_OptionalEnableTransitGatewayRouteTablePropagationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableTransitGatewayRouteTablePropagationRequestRequestTypeDef(
    _RequiredEnableTransitGatewayRouteTablePropagationRequestRequestTypeDef,
    _OptionalEnableTransitGatewayRouteTablePropagationRequestRequestTypeDef,
):
    pass


_RequiredEnableVgwRoutePropagationRequestRequestTypeDef = TypedDict(
    "_RequiredEnableVgwRoutePropagationRequestRequestTypeDef",
    {
        "GatewayId": str,
        "RouteTableId": str,
    },
)
_OptionalEnableVgwRoutePropagationRequestRequestTypeDef = TypedDict(
    "_OptionalEnableVgwRoutePropagationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableVgwRoutePropagationRequestRequestTypeDef(
    _RequiredEnableVgwRoutePropagationRequestRequestTypeDef,
    _OptionalEnableVgwRoutePropagationRequestRequestTypeDef,
):
    pass


_RequiredEnableVolumeIORequestRequestTypeDef = TypedDict(
    "_RequiredEnableVolumeIORequestRequestTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalEnableVolumeIORequestRequestTypeDef = TypedDict(
    "_OptionalEnableVolumeIORequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableVolumeIORequestRequestTypeDef(
    _RequiredEnableVolumeIORequestRequestTypeDef, _OptionalEnableVolumeIORequestRequestTypeDef
):
    pass


EnableVolumeIORequestVolumeEnableIoTypeDef = TypedDict(
    "EnableVolumeIORequestVolumeEnableIoTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

EnableVpcClassicLinkDnsSupportRequestRequestTypeDef = TypedDict(
    "EnableVpcClassicLinkDnsSupportRequestRequestTypeDef",
    {
        "VpcId": str,
    },
    total=False,
)

_RequiredEnableVpcClassicLinkRequestRequestTypeDef = TypedDict(
    "_RequiredEnableVpcClassicLinkRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalEnableVpcClassicLinkRequestRequestTypeDef = TypedDict(
    "_OptionalEnableVpcClassicLinkRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class EnableVpcClassicLinkRequestRequestTypeDef(
    _RequiredEnableVpcClassicLinkRequestRequestTypeDef,
    _OptionalEnableVpcClassicLinkRequestRequestTypeDef,
):
    pass


EnableVpcClassicLinkRequestVpcEnableClassicLinkTypeDef = TypedDict(
    "EnableVpcClassicLinkRequestVpcEnableClassicLinkTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

EnclaveOptionsRequestTypeDef = TypedDict(
    "EnclaveOptionsRequestTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

EnclaveOptionsTypeDef = TypedDict(
    "EnclaveOptionsTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

EventInformationTypeDef = TypedDict(
    "EventInformationTypeDef",
    {
        "EventDescription": str,
        "EventSubType": str,
        "InstanceId": str,
    },
    total=False,
)

TransitGatewayRouteTableRouteTypeDef = TypedDict(
    "TransitGatewayRouteTableRouteTypeDef",
    {
        "DestinationCidr": str,
        "State": str,
        "RouteOrigin": str,
        "PrefixListId": str,
        "AttachmentId": str,
        "ResourceId": str,
        "ResourceType": str,
    },
    total=False,
)

_RequiredExportClientVpnClientCertificateRevocationListRequestRequestTypeDef = TypedDict(
    "_RequiredExportClientVpnClientCertificateRevocationListRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalExportClientVpnClientCertificateRevocationListRequestRequestTypeDef = TypedDict(
    "_OptionalExportClientVpnClientCertificateRevocationListRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ExportClientVpnClientCertificateRevocationListRequestRequestTypeDef(
    _RequiredExportClientVpnClientCertificateRevocationListRequestRequestTypeDef,
    _OptionalExportClientVpnClientCertificateRevocationListRequestRequestTypeDef,
):
    pass


_RequiredExportClientVpnClientConfigurationRequestRequestTypeDef = TypedDict(
    "_RequiredExportClientVpnClientConfigurationRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalExportClientVpnClientConfigurationRequestRequestTypeDef = TypedDict(
    "_OptionalExportClientVpnClientConfigurationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ExportClientVpnClientConfigurationRequestRequestTypeDef(
    _RequiredExportClientVpnClientConfigurationRequestRequestTypeDef,
    _OptionalExportClientVpnClientConfigurationRequestRequestTypeDef,
):
    pass


_RequiredExportTaskS3LocationRequestTypeDef = TypedDict(
    "_RequiredExportTaskS3LocationRequestTypeDef",
    {
        "S3Bucket": str,
    },
)
_OptionalExportTaskS3LocationRequestTypeDef = TypedDict(
    "_OptionalExportTaskS3LocationRequestTypeDef",
    {
        "S3Prefix": str,
    },
    total=False,
)


class ExportTaskS3LocationRequestTypeDef(
    _RequiredExportTaskS3LocationRequestTypeDef, _OptionalExportTaskS3LocationRequestTypeDef
):
    pass


ExportTaskS3LocationTypeDef = TypedDict(
    "ExportTaskS3LocationTypeDef",
    {
        "S3Bucket": str,
        "S3Prefix": str,
    },
    total=False,
)

ExportToS3TaskTypeDef = TypedDict(
    "ExportToS3TaskTypeDef",
    {
        "ContainerFormat": Literal["ova"],
        "DiskImageFormat": DiskImageFormatType,
        "S3Bucket": str,
        "S3Key": str,
    },
    total=False,
)

InstanceExportDetailsTypeDef = TypedDict(
    "InstanceExportDetailsTypeDef",
    {
        "InstanceId": str,
        "TargetEnvironment": ExportEnvironmentType,
    },
    total=False,
)

TargetCapacitySpecificationTypeDef = TypedDict(
    "TargetCapacitySpecificationTypeDef",
    {
        "TotalTargetCapacity": int,
        "OnDemandTargetCapacity": int,
        "SpotTargetCapacity": int,
        "DefaultTargetCapacityType": DefaultTargetCapacityTypeType,
        "TargetCapacityUnitType": TargetCapacityUnitTypeType,
    },
    total=False,
)

FleetLaunchTemplateSpecificationRequestTypeDef = TypedDict(
    "FleetLaunchTemplateSpecificationRequestTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "Version": str,
    },
    total=False,
)

FleetLaunchTemplateSpecificationTypeDef = TypedDict(
    "FleetLaunchTemplateSpecificationTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "Version": str,
    },
    total=False,
)

PlacementTypeDef = TypedDict(
    "PlacementTypeDef",
    {
        "AvailabilityZone": str,
        "Affinity": str,
        "GroupName": str,
        "PartitionNumber": int,
        "HostId": str,
        "Tenancy": TenancyType,
        "SpreadDomain": str,
        "HostResourceGroupArn": str,
    },
    total=False,
)

PlacementResponseTypeDef = TypedDict(
    "PlacementResponseTypeDef",
    {
        "GroupName": str,
    },
    total=False,
)

FleetSpotCapacityRebalanceRequestTypeDef = TypedDict(
    "FleetSpotCapacityRebalanceRequestTypeDef",
    {
        "ReplacementStrategy": FleetReplacementStrategyType,
        "TerminationDelay": int,
    },
    total=False,
)

FleetSpotCapacityRebalanceTypeDef = TypedDict(
    "FleetSpotCapacityRebalanceTypeDef",
    {
        "ReplacementStrategy": FleetReplacementStrategyType,
        "TerminationDelay": int,
    },
    total=False,
)

FpgaDeviceMemoryInfoTypeDef = TypedDict(
    "FpgaDeviceMemoryInfoTypeDef",
    {
        "SizeInMiB": int,
    },
    total=False,
)

LoadPermissionTypeDef = TypedDict(
    "LoadPermissionTypeDef",
    {
        "UserId": str,
        "Group": Literal["all"],
    },
    total=False,
)

FpgaImageStateTypeDef = TypedDict(
    "FpgaImageStateTypeDef",
    {
        "Code": FpgaImageStateCodeType,
        "Message": str,
    },
    total=False,
)

PciIdTypeDef = TypedDict(
    "PciIdTypeDef",
    {
        "DeviceId": str,
        "VendorId": str,
        "SubsystemId": str,
        "SubsystemVendorId": str,
    },
    total=False,
)

GetAssociatedEnclaveCertificateIamRolesRequestRequestTypeDef = TypedDict(
    "GetAssociatedEnclaveCertificateIamRolesRequestRequestTypeDef",
    {
        "CertificateArn": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredGetAssociatedIpv6PoolCidrsRequestRequestTypeDef = TypedDict(
    "_RequiredGetAssociatedIpv6PoolCidrsRequestRequestTypeDef",
    {
        "PoolId": str,
    },
)
_OptionalGetAssociatedIpv6PoolCidrsRequestRequestTypeDef = TypedDict(
    "_OptionalGetAssociatedIpv6PoolCidrsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)


class GetAssociatedIpv6PoolCidrsRequestRequestTypeDef(
    _RequiredGetAssociatedIpv6PoolCidrsRequestRequestTypeDef,
    _OptionalGetAssociatedIpv6PoolCidrsRequestRequestTypeDef,
):
    pass


Ipv6CidrAssociationTypeDef = TypedDict(
    "Ipv6CidrAssociationTypeDef",
    {
        "Ipv6Cidr": str,
        "AssociatedResource": str,
    },
    total=False,
)

_RequiredGetCapacityReservationUsageRequestRequestTypeDef = TypedDict(
    "_RequiredGetCapacityReservationUsageRequestRequestTypeDef",
    {
        "CapacityReservationId": str,
    },
)
_OptionalGetCapacityReservationUsageRequestRequestTypeDef = TypedDict(
    "_OptionalGetCapacityReservationUsageRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)


class GetCapacityReservationUsageRequestRequestTypeDef(
    _RequiredGetCapacityReservationUsageRequestRequestTypeDef,
    _OptionalGetCapacityReservationUsageRequestRequestTypeDef,
):
    pass


InstanceUsageTypeDef = TypedDict(
    "InstanceUsageTypeDef",
    {
        "AccountId": str,
        "UsedInstanceCount": int,
    },
    total=False,
)

GetConsoleOutputRequestInstanceConsoleOutputTypeDef = TypedDict(
    "GetConsoleOutputRequestInstanceConsoleOutputTypeDef",
    {
        "DryRun": bool,
        "Latest": bool,
    },
    total=False,
)

_RequiredGetConsoleOutputRequestRequestTypeDef = TypedDict(
    "_RequiredGetConsoleOutputRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalGetConsoleOutputRequestRequestTypeDef = TypedDict(
    "_OptionalGetConsoleOutputRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Latest": bool,
    },
    total=False,
)


class GetConsoleOutputRequestRequestTypeDef(
    _RequiredGetConsoleOutputRequestRequestTypeDef, _OptionalGetConsoleOutputRequestRequestTypeDef
):
    pass


_RequiredGetConsoleScreenshotRequestRequestTypeDef = TypedDict(
    "_RequiredGetConsoleScreenshotRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalGetConsoleScreenshotRequestRequestTypeDef = TypedDict(
    "_OptionalGetConsoleScreenshotRequestRequestTypeDef",
    {
        "DryRun": bool,
        "WakeUp": bool,
    },
    total=False,
)


class GetConsoleScreenshotRequestRequestTypeDef(
    _RequiredGetConsoleScreenshotRequestRequestTypeDef,
    _OptionalGetConsoleScreenshotRequestRequestTypeDef,
):
    pass


_RequiredGetDefaultCreditSpecificationRequestRequestTypeDef = TypedDict(
    "_RequiredGetDefaultCreditSpecificationRequestRequestTypeDef",
    {
        "InstanceFamily": UnlimitedSupportedInstanceFamilyType,
    },
)
_OptionalGetDefaultCreditSpecificationRequestRequestTypeDef = TypedDict(
    "_OptionalGetDefaultCreditSpecificationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class GetDefaultCreditSpecificationRequestRequestTypeDef(
    _RequiredGetDefaultCreditSpecificationRequestRequestTypeDef,
    _OptionalGetDefaultCreditSpecificationRequestRequestTypeDef,
):
    pass


InstanceFamilyCreditSpecificationTypeDef = TypedDict(
    "InstanceFamilyCreditSpecificationTypeDef",
    {
        "InstanceFamily": UnlimitedSupportedInstanceFamilyType,
        "CpuCredits": str,
    },
    total=False,
)

GetEbsDefaultKmsKeyIdRequestRequestTypeDef = TypedDict(
    "GetEbsDefaultKmsKeyIdRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

GetEbsEncryptionByDefaultRequestRequestTypeDef = TypedDict(
    "GetEbsEncryptionByDefaultRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredGetGroupsForCapacityReservationRequestRequestTypeDef = TypedDict(
    "_RequiredGetGroupsForCapacityReservationRequestRequestTypeDef",
    {
        "CapacityReservationId": str,
    },
)
_OptionalGetGroupsForCapacityReservationRequestRequestTypeDef = TypedDict(
    "_OptionalGetGroupsForCapacityReservationRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)


class GetGroupsForCapacityReservationRequestRequestTypeDef(
    _RequiredGetGroupsForCapacityReservationRequestRequestTypeDef,
    _OptionalGetGroupsForCapacityReservationRequestRequestTypeDef,
):
    pass


GetHostReservationPurchasePreviewRequestRequestTypeDef = TypedDict(
    "GetHostReservationPurchasePreviewRequestRequestTypeDef",
    {
        "HostIdSet": Sequence[str],
        "OfferingId": str,
    },
)

PurchaseTypeDef = TypedDict(
    "PurchaseTypeDef",
    {
        "CurrencyCode": Literal["USD"],
        "Duration": int,
        "HostIdSet": List[str],
        "HostReservationId": str,
        "HourlyPrice": str,
        "InstanceFamily": str,
        "PaymentOption": PaymentOptionType,
        "UpfrontPrice": str,
    },
    total=False,
)

InstanceTypeInfoFromInstanceRequirementsTypeDef = TypedDict(
    "InstanceTypeInfoFromInstanceRequirementsTypeDef",
    {
        "InstanceType": str,
    },
    total=False,
)

_RequiredGetInstanceUefiDataRequestRequestTypeDef = TypedDict(
    "_RequiredGetInstanceUefiDataRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalGetInstanceUefiDataRequestRequestTypeDef = TypedDict(
    "_OptionalGetInstanceUefiDataRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class GetInstanceUefiDataRequestRequestTypeDef(
    _RequiredGetInstanceUefiDataRequestRequestTypeDef,
    _OptionalGetInstanceUefiDataRequestRequestTypeDef,
):
    pass


_RequiredGetIpamAddressHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredGetIpamAddressHistoryRequestRequestTypeDef",
    {
        "Cidr": str,
        "IpamScopeId": str,
    },
)
_OptionalGetIpamAddressHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalGetIpamAddressHistoryRequestRequestTypeDef",
    {
        "DryRun": bool,
        "VpcId": str,
        "StartTime": Union[datetime, str],
        "EndTime": Union[datetime, str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetIpamAddressHistoryRequestRequestTypeDef(
    _RequiredGetIpamAddressHistoryRequestRequestTypeDef,
    _OptionalGetIpamAddressHistoryRequestRequestTypeDef,
):
    pass


IpamAddressHistoryRecordTypeDef = TypedDict(
    "IpamAddressHistoryRecordTypeDef",
    {
        "ResourceOwnerId": str,
        "ResourceRegion": str,
        "ResourceType": IpamAddressHistoryResourceTypeType,
        "ResourceId": str,
        "ResourceCidr": str,
        "ResourceName": str,
        "ResourceComplianceStatus": IpamComplianceStatusType,
        "ResourceOverlapStatus": IpamOverlapStatusType,
        "VpcId": str,
        "SampledStartTime": datetime,
        "SampledEndTime": datetime,
    },
    total=False,
)

_RequiredGetLaunchTemplateDataRequestRequestTypeDef = TypedDict(
    "_RequiredGetLaunchTemplateDataRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalGetLaunchTemplateDataRequestRequestTypeDef = TypedDict(
    "_OptionalGetLaunchTemplateDataRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class GetLaunchTemplateDataRequestRequestTypeDef(
    _RequiredGetLaunchTemplateDataRequestRequestTypeDef,
    _OptionalGetLaunchTemplateDataRequestRequestTypeDef,
):
    pass


_RequiredGetManagedPrefixListAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetManagedPrefixListAssociationsRequestRequestTypeDef",
    {
        "PrefixListId": str,
    },
)
_OptionalGetManagedPrefixListAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetManagedPrefixListAssociationsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetManagedPrefixListAssociationsRequestRequestTypeDef(
    _RequiredGetManagedPrefixListAssociationsRequestRequestTypeDef,
    _OptionalGetManagedPrefixListAssociationsRequestRequestTypeDef,
):
    pass


PrefixListAssociationTypeDef = TypedDict(
    "PrefixListAssociationTypeDef",
    {
        "ResourceId": str,
        "ResourceOwner": str,
    },
    total=False,
)

_RequiredGetManagedPrefixListEntriesRequestRequestTypeDef = TypedDict(
    "_RequiredGetManagedPrefixListEntriesRequestRequestTypeDef",
    {
        "PrefixListId": str,
    },
)
_OptionalGetManagedPrefixListEntriesRequestRequestTypeDef = TypedDict(
    "_OptionalGetManagedPrefixListEntriesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TargetVersion": int,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetManagedPrefixListEntriesRequestRequestTypeDef(
    _RequiredGetManagedPrefixListEntriesRequestRequestTypeDef,
    _OptionalGetManagedPrefixListEntriesRequestRequestTypeDef,
):
    pass


PrefixListEntryTypeDef = TypedDict(
    "PrefixListEntryTypeDef",
    {
        "Cidr": str,
        "Description": str,
    },
    total=False,
)

_RequiredGetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisId": str,
    },
)
_OptionalGetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class GetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef(
    _RequiredGetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef,
    _OptionalGetNetworkInsightsAccessScopeAnalysisFindingsRequestRequestTypeDef,
):
    pass


_RequiredGetNetworkInsightsAccessScopeContentRequestRequestTypeDef = TypedDict(
    "_RequiredGetNetworkInsightsAccessScopeContentRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeId": str,
    },
)
_OptionalGetNetworkInsightsAccessScopeContentRequestRequestTypeDef = TypedDict(
    "_OptionalGetNetworkInsightsAccessScopeContentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class GetNetworkInsightsAccessScopeContentRequestRequestTypeDef(
    _RequiredGetNetworkInsightsAccessScopeContentRequestRequestTypeDef,
    _OptionalGetNetworkInsightsAccessScopeContentRequestRequestTypeDef,
):
    pass


GetPasswordDataRequestInstancePasswordDataTypeDef = TypedDict(
    "GetPasswordDataRequestInstancePasswordDataTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredGetPasswordDataRequestRequestTypeDef = TypedDict(
    "_RequiredGetPasswordDataRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalGetPasswordDataRequestRequestTypeDef = TypedDict(
    "_OptionalGetPasswordDataRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class GetPasswordDataRequestRequestTypeDef(
    _RequiredGetPasswordDataRequestRequestTypeDef, _OptionalGetPasswordDataRequestRequestTypeDef
):
    pass


ReservationValueTypeDef = TypedDict(
    "ReservationValueTypeDef",
    {
        "HourlyPrice": str,
        "RemainingTotalValue": str,
        "RemainingUpfrontValue": str,
    },
    total=False,
)

GetSerialConsoleAccessStatusRequestRequestTypeDef = TypedDict(
    "GetSerialConsoleAccessStatusRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

SpotPlacementScoreTypeDef = TypedDict(
    "SpotPlacementScoreTypeDef",
    {
        "Region": str,
        "AvailabilityZoneId": str,
        "Score": int,
    },
    total=False,
)

TransitGatewayAttachmentPropagationTypeDef = TypedDict(
    "TransitGatewayAttachmentPropagationTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "State": TransitGatewayPropagationStateType,
    },
    total=False,
)

TransitGatewayRouteTableAssociationTypeDef = TypedDict(
    "TransitGatewayRouteTableAssociationTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "State": TransitGatewayAssociationStateType,
    },
    total=False,
)

TransitGatewayRouteTablePropagationTypeDef = TypedDict(
    "TransitGatewayRouteTablePropagationTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "State": TransitGatewayPropagationStateType,
    },
    total=False,
)

_RequiredGetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef = TypedDict(
    "_RequiredGetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef",
    {
        "VpnConnectionId": str,
        "VpnConnectionDeviceTypeId": str,
    },
)
_OptionalGetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef = TypedDict(
    "_OptionalGetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef",
    {
        "InternetKeyExchangeVersion": str,
        "DryRun": bool,
    },
    total=False,
)


class GetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef(
    _RequiredGetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef,
    _OptionalGetVpnConnectionDeviceSampleConfigurationRequestRequestTypeDef,
):
    pass


GetVpnConnectionDeviceTypesRequestRequestTypeDef = TypedDict(
    "GetVpnConnectionDeviceTypesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

VpnConnectionDeviceTypeTypeDef = TypedDict(
    "VpnConnectionDeviceTypeTypeDef",
    {
        "VpnConnectionDeviceTypeId": str,
        "Vendor": str,
        "Platform": str,
        "Software": str,
    },
    total=False,
)

GpuDeviceMemoryInfoTypeDef = TypedDict(
    "GpuDeviceMemoryInfoTypeDef",
    {
        "SizeInMiB": int,
    },
    total=False,
)

HibernationOptionsRequestTypeDef = TypedDict(
    "HibernationOptionsRequestTypeDef",
    {
        "Configured": bool,
    },
    total=False,
)

HibernationOptionsTypeDef = TypedDict(
    "HibernationOptionsTypeDef",
    {
        "Configured": bool,
    },
    total=False,
)

HostInstanceTypeDef = TypedDict(
    "HostInstanceTypeDef",
    {
        "InstanceId": str,
        "InstanceType": str,
        "OwnerId": str,
    },
    total=False,
)

HostPropertiesTypeDef = TypedDict(
    "HostPropertiesTypeDef",
    {
        "Cores": int,
        "InstanceType": str,
        "InstanceFamily": str,
        "Sockets": int,
        "TotalVCpus": int,
    },
    total=False,
)

IKEVersionsListValueTypeDef = TypedDict(
    "IKEVersionsListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

IKEVersionsRequestListValueTypeDef = TypedDict(
    "IKEVersionsRequestListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

IamInstanceProfileTypeDef = TypedDict(
    "IamInstanceProfileTypeDef",
    {
        "Arn": str,
        "Id": str,
    },
    total=False,
)

LaunchPermissionTypeDef = TypedDict(
    "LaunchPermissionTypeDef",
    {
        "Group": Literal["all"],
        "UserId": str,
        "OrganizationArn": str,
        "OrganizationalUnitArn": str,
    },
    total=False,
)

UserBucketTypeDef = TypedDict(
    "UserBucketTypeDef",
    {
        "S3Bucket": str,
        "S3Key": str,
    },
    total=False,
)

ImageRecycleBinInfoTypeDef = TypedDict(
    "ImageRecycleBinInfoTypeDef",
    {
        "ImageId": str,
        "Name": str,
        "Description": str,
        "RecycleBinEnterTime": datetime,
        "RecycleBinExitTime": datetime,
    },
    total=False,
)

StateReasonTypeDef = TypedDict(
    "StateReasonTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

_RequiredImportClientVpnClientCertificateRevocationListRequestRequestTypeDef = TypedDict(
    "_RequiredImportClientVpnClientCertificateRevocationListRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "CertificateRevocationList": str,
    },
)
_OptionalImportClientVpnClientCertificateRevocationListRequestRequestTypeDef = TypedDict(
    "_OptionalImportClientVpnClientCertificateRevocationListRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ImportClientVpnClientCertificateRevocationListRequestRequestTypeDef(
    _RequiredImportClientVpnClientCertificateRevocationListRequestRequestTypeDef,
    _OptionalImportClientVpnClientCertificateRevocationListRequestRequestTypeDef,
):
    pass


ImportImageLicenseConfigurationRequestTypeDef = TypedDict(
    "ImportImageLicenseConfigurationRequestTypeDef",
    {
        "LicenseConfigurationArn": str,
    },
    total=False,
)

ImportImageLicenseConfigurationResponseTypeDef = TypedDict(
    "ImportImageLicenseConfigurationResponseTypeDef",
    {
        "LicenseConfigurationArn": str,
    },
    total=False,
)

UserDataTypeDef = TypedDict(
    "UserDataTypeDef",
    {
        "Data": str,
    },
    total=False,
)

InferenceDeviceInfoTypeDef = TypedDict(
    "InferenceDeviceInfoTypeDef",
    {
        "Count": int,
        "Name": str,
        "Manufacturer": str,
    },
    total=False,
)

InstanceCountTypeDef = TypedDict(
    "InstanceCountTypeDef",
    {
        "InstanceCount": int,
        "State": ListingStateType,
    },
    total=False,
)

InstanceCreditSpecificationRequestTypeDef = TypedDict(
    "InstanceCreditSpecificationRequestTypeDef",
    {
        "InstanceId": str,
        "CpuCredits": str,
    },
    total=False,
)

InstanceEventWindowTimeRangeTypeDef = TypedDict(
    "InstanceEventWindowTimeRangeTypeDef",
    {
        "StartWeekDay": WeekDayType,
        "StartHour": int,
        "EndWeekDay": WeekDayType,
        "EndHour": int,
    },
    total=False,
)

InstanceIpv4PrefixTypeDef = TypedDict(
    "InstanceIpv4PrefixTypeDef",
    {
        "Ipv4Prefix": str,
    },
    total=False,
)

InstanceIpv6AddressRequestTypeDef = TypedDict(
    "InstanceIpv6AddressRequestTypeDef",
    {
        "Ipv6Address": str,
    },
    total=False,
)

InstanceIpv6PrefixTypeDef = TypedDict(
    "InstanceIpv6PrefixTypeDef",
    {
        "Ipv6Prefix": str,
    },
    total=False,
)

InstanceMaintenanceOptionsRequestTypeDef = TypedDict(
    "InstanceMaintenanceOptionsRequestTypeDef",
    {
        "AutoRecovery": InstanceAutoRecoveryStateType,
    },
    total=False,
)

InstanceMaintenanceOptionsTypeDef = TypedDict(
    "InstanceMaintenanceOptionsTypeDef",
    {
        "AutoRecovery": InstanceAutoRecoveryStateType,
    },
    total=False,
)

SpotMarketOptionsTypeDef = TypedDict(
    "SpotMarketOptionsTypeDef",
    {
        "MaxPrice": str,
        "SpotInstanceType": SpotInstanceTypeType,
        "BlockDurationMinutes": int,
        "ValidUntil": Union[datetime, str],
        "InstanceInterruptionBehavior": InstanceInterruptionBehaviorType,
    },
    total=False,
)

InstanceMetadataOptionsRequestTypeDef = TypedDict(
    "InstanceMetadataOptionsRequestTypeDef",
    {
        "HttpTokens": HttpTokensStateType,
        "HttpPutResponseHopLimit": int,
        "HttpEndpoint": InstanceMetadataEndpointStateType,
        "HttpProtocolIpv6": InstanceMetadataProtocolStateType,
        "InstanceMetadataTags": InstanceMetadataTagsStateType,
    },
    total=False,
)

InstanceMetadataOptionsResponseTypeDef = TypedDict(
    "InstanceMetadataOptionsResponseTypeDef",
    {
        "State": InstanceMetadataOptionsStateType,
        "HttpTokens": HttpTokensStateType,
        "HttpPutResponseHopLimit": int,
        "HttpEndpoint": InstanceMetadataEndpointStateType,
        "HttpProtocolIpv6": InstanceMetadataProtocolStateType,
        "InstanceMetadataTags": InstanceMetadataTagsStateType,
    },
    total=False,
)

MonitoringTypeDef = TypedDict(
    "MonitoringTypeDef",
    {
        "State": MonitoringStateType,
    },
    total=False,
)

InstanceNetworkInterfaceAssociationTypeDef = TypedDict(
    "InstanceNetworkInterfaceAssociationTypeDef",
    {
        "CarrierIp": str,
        "CustomerOwnedIp": str,
        "IpOwnerId": str,
        "PublicDnsName": str,
        "PublicIp": str,
    },
    total=False,
)

InstanceNetworkInterfaceAttachmentTypeDef = TypedDict(
    "InstanceNetworkInterfaceAttachmentTypeDef",
    {
        "AttachTime": datetime,
        "AttachmentId": str,
        "DeleteOnTermination": bool,
        "DeviceIndex": int,
        "Status": AttachmentStatusType,
        "NetworkCardIndex": int,
    },
    total=False,
)

MemoryGiBPerVCpuRequestTypeDef = TypedDict(
    "MemoryGiBPerVCpuRequestTypeDef",
    {
        "Min": float,
        "Max": float,
    },
    total=False,
)

_RequiredMemoryMiBRequestTypeDef = TypedDict(
    "_RequiredMemoryMiBRequestTypeDef",
    {
        "Min": int,
    },
)
_OptionalMemoryMiBRequestTypeDef = TypedDict(
    "_OptionalMemoryMiBRequestTypeDef",
    {
        "Max": int,
    },
    total=False,
)


class MemoryMiBRequestTypeDef(_RequiredMemoryMiBRequestTypeDef, _OptionalMemoryMiBRequestTypeDef):
    pass


NetworkInterfaceCountRequestTypeDef = TypedDict(
    "NetworkInterfaceCountRequestTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

TotalLocalStorageGBRequestTypeDef = TypedDict(
    "TotalLocalStorageGBRequestTypeDef",
    {
        "Min": float,
        "Max": float,
    },
    total=False,
)

_RequiredVCpuCountRangeRequestTypeDef = TypedDict(
    "_RequiredVCpuCountRangeRequestTypeDef",
    {
        "Min": int,
    },
)
_OptionalVCpuCountRangeRequestTypeDef = TypedDict(
    "_OptionalVCpuCountRangeRequestTypeDef",
    {
        "Max": int,
    },
    total=False,
)


class VCpuCountRangeRequestTypeDef(
    _RequiredVCpuCountRangeRequestTypeDef, _OptionalVCpuCountRangeRequestTypeDef
):
    pass


MemoryGiBPerVCpuTypeDef = TypedDict(
    "MemoryGiBPerVCpuTypeDef",
    {
        "Min": float,
        "Max": float,
    },
    total=False,
)

MemoryMiBTypeDef = TypedDict(
    "MemoryMiBTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

NetworkInterfaceCountTypeDef = TypedDict(
    "NetworkInterfaceCountTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

TotalLocalStorageGBTypeDef = TypedDict(
    "TotalLocalStorageGBTypeDef",
    {
        "Min": float,
        "Max": float,
    },
    total=False,
)

VCpuCountRangeTypeDef = TypedDict(
    "VCpuCountRangeTypeDef",
    {
        "Min": int,
        "Max": int,
    },
    total=False,
)

InstanceStateTypeDef = TypedDict(
    "InstanceStateTypeDef",
    {
        "Code": int,
        "Name": InstanceStateNameType,
    },
    total=False,
)

InstanceStatusDetailsTypeDef = TypedDict(
    "InstanceStatusDetailsTypeDef",
    {
        "ImpairedSince": datetime,
        "Name": Literal["reachability"],
        "Status": StatusTypeType,
    },
    total=False,
)

InstanceStatusEventTypeDef = TypedDict(
    "InstanceStatusEventTypeDef",
    {
        "InstanceEventId": str,
        "Code": EventCodeType,
        "Description": str,
        "NotAfter": datetime,
        "NotBefore": datetime,
        "NotBeforeDeadline": datetime,
    },
    total=False,
)

LicenseConfigurationTypeDef = TypedDict(
    "LicenseConfigurationTypeDef",
    {
        "LicenseConfigurationArn": str,
    },
    total=False,
)

PrivateDnsNameOptionsResponseTypeDef = TypedDict(
    "PrivateDnsNameOptionsResponseTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
    },
    total=False,
)

MemoryInfoTypeDef = TypedDict(
    "MemoryInfoTypeDef",
    {
        "SizeInMiB": int,
    },
    total=False,
)

PlacementGroupInfoTypeDef = TypedDict(
    "PlacementGroupInfoTypeDef",
    {
        "SupportedStrategies": List[PlacementGroupStrategyType],
    },
    total=False,
)

ProcessorInfoTypeDef = TypedDict(
    "ProcessorInfoTypeDef",
    {
        "SupportedArchitectures": List[ArchitectureTypeType],
        "SustainedClockSpeedInGhz": float,
    },
    total=False,
)

VCpuInfoTypeDef = TypedDict(
    "VCpuInfoTypeDef",
    {
        "DefaultVCpus": int,
        "DefaultCores": int,
        "DefaultThreadsPerCore": int,
        "ValidCores": List[int],
        "ValidThreadsPerCore": List[int],
    },
    total=False,
)

IpRangeTypeDef = TypedDict(
    "IpRangeTypeDef",
    {
        "CidrIp": str,
        "Description": str,
    },
    total=False,
)

Ipv6RangeTypeDef = TypedDict(
    "Ipv6RangeTypeDef",
    {
        "CidrIpv6": str,
        "Description": str,
    },
    total=False,
)

PrefixListIdTypeDef = TypedDict(
    "PrefixListIdTypeDef",
    {
        "Description": str,
        "PrefixListId": str,
    },
    total=False,
)

UserIdGroupPairTypeDef = TypedDict(
    "UserIdGroupPairTypeDef",
    {
        "Description": str,
        "GroupId": str,
        "GroupName": str,
        "PeeringStatus": str,
        "UserId": str,
        "VpcId": str,
        "VpcPeeringConnectionId": str,
    },
    total=False,
)

IpamCidrAuthorizationContextTypeDef = TypedDict(
    "IpamCidrAuthorizationContextTypeDef",
    {
        "Message": str,
        "Signature": str,
    },
    total=False,
)

IpamOperatingRegionTypeDef = TypedDict(
    "IpamOperatingRegionTypeDef",
    {
        "RegionName": str,
    },
    total=False,
)

IpamPoolCidrFailureReasonTypeDef = TypedDict(
    "IpamPoolCidrFailureReasonTypeDef",
    {
        "Code": Literal["cidr-not-available"],
        "Message": str,
    },
    total=False,
)

IpamResourceTagTypeDef = TypedDict(
    "IpamResourceTagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
    total=False,
)

Ipv4PrefixSpecificationResponseTypeDef = TypedDict(
    "Ipv4PrefixSpecificationResponseTypeDef",
    {
        "Ipv4Prefix": str,
    },
    total=False,
)

Ipv6CidrBlockTypeDef = TypedDict(
    "Ipv6CidrBlockTypeDef",
    {
        "Ipv6CidrBlock": str,
    },
    total=False,
)

PoolCidrBlockTypeDef = TypedDict(
    "PoolCidrBlockTypeDef",
    {
        "Cidr": str,
    },
    total=False,
)

Ipv6PrefixSpecificationResponseTypeDef = TypedDict(
    "Ipv6PrefixSpecificationResponseTypeDef",
    {
        "Ipv6Prefix": str,
    },
    total=False,
)

Ipv6PrefixSpecificationTypeDef = TypedDict(
    "Ipv6PrefixSpecificationTypeDef",
    {
        "Ipv6Prefix": str,
    },
    total=False,
)

LastErrorTypeDef = TypedDict(
    "LastErrorTypeDef",
    {
        "Message": str,
        "Code": str,
    },
    total=False,
)

RunInstancesMonitoringEnabledTypeDef = TypedDict(
    "RunInstancesMonitoringEnabledTypeDef",
    {
        "Enabled": bool,
    },
)

SpotPlacementTypeDef = TypedDict(
    "SpotPlacementTypeDef",
    {
        "AvailabilityZone": str,
        "GroupName": str,
        "Tenancy": TenancyType,
    },
    total=False,
)

LaunchTemplateEbsBlockDeviceRequestTypeDef = TypedDict(
    "LaunchTemplateEbsBlockDeviceRequestTypeDef",
    {
        "Encrypted": bool,
        "DeleteOnTermination": bool,
        "Iops": int,
        "KmsKeyId": str,
        "SnapshotId": str,
        "VolumeSize": int,
        "VolumeType": VolumeTypeType,
        "Throughput": int,
    },
    total=False,
)

LaunchTemplateEbsBlockDeviceTypeDef = TypedDict(
    "LaunchTemplateEbsBlockDeviceTypeDef",
    {
        "Encrypted": bool,
        "DeleteOnTermination": bool,
        "Iops": int,
        "KmsKeyId": str,
        "SnapshotId": str,
        "VolumeSize": int,
        "VolumeType": VolumeTypeType,
        "Throughput": int,
    },
    total=False,
)

LaunchTemplateCpuOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateCpuOptionsRequestTypeDef",
    {
        "CoreCount": int,
        "ThreadsPerCore": int,
    },
    total=False,
)

LaunchTemplateCpuOptionsTypeDef = TypedDict(
    "LaunchTemplateCpuOptionsTypeDef",
    {
        "CoreCount": int,
        "ThreadsPerCore": int,
    },
    total=False,
)

LaunchTemplateElasticInferenceAcceleratorResponseTypeDef = TypedDict(
    "LaunchTemplateElasticInferenceAcceleratorResponseTypeDef",
    {
        "Type": str,
        "Count": int,
    },
    total=False,
)

_RequiredLaunchTemplateElasticInferenceAcceleratorTypeDef = TypedDict(
    "_RequiredLaunchTemplateElasticInferenceAcceleratorTypeDef",
    {
        "Type": str,
    },
)
_OptionalLaunchTemplateElasticInferenceAcceleratorTypeDef = TypedDict(
    "_OptionalLaunchTemplateElasticInferenceAcceleratorTypeDef",
    {
        "Count": int,
    },
    total=False,
)


class LaunchTemplateElasticInferenceAcceleratorTypeDef(
    _RequiredLaunchTemplateElasticInferenceAcceleratorTypeDef,
    _OptionalLaunchTemplateElasticInferenceAcceleratorTypeDef,
):
    pass


LaunchTemplateEnclaveOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateEnclaveOptionsRequestTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

LaunchTemplateEnclaveOptionsTypeDef = TypedDict(
    "LaunchTemplateEnclaveOptionsTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

LaunchTemplateHibernationOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateHibernationOptionsRequestTypeDef",
    {
        "Configured": bool,
    },
    total=False,
)

LaunchTemplateHibernationOptionsTypeDef = TypedDict(
    "LaunchTemplateHibernationOptionsTypeDef",
    {
        "Configured": bool,
    },
    total=False,
)

LaunchTemplateIamInstanceProfileSpecificationRequestTypeDef = TypedDict(
    "LaunchTemplateIamInstanceProfileSpecificationRequestTypeDef",
    {
        "Arn": str,
        "Name": str,
    },
    total=False,
)

LaunchTemplateIamInstanceProfileSpecificationTypeDef = TypedDict(
    "LaunchTemplateIamInstanceProfileSpecificationTypeDef",
    {
        "Arn": str,
        "Name": str,
    },
    total=False,
)

LaunchTemplateInstanceMaintenanceOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateInstanceMaintenanceOptionsRequestTypeDef",
    {
        "AutoRecovery": LaunchTemplateAutoRecoveryStateType,
    },
    total=False,
)

LaunchTemplateInstanceMaintenanceOptionsTypeDef = TypedDict(
    "LaunchTemplateInstanceMaintenanceOptionsTypeDef",
    {
        "AutoRecovery": LaunchTemplateAutoRecoveryStateType,
    },
    total=False,
)

LaunchTemplateSpotMarketOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateSpotMarketOptionsRequestTypeDef",
    {
        "MaxPrice": str,
        "SpotInstanceType": SpotInstanceTypeType,
        "BlockDurationMinutes": int,
        "ValidUntil": Union[datetime, str],
        "InstanceInterruptionBehavior": InstanceInterruptionBehaviorType,
    },
    total=False,
)

LaunchTemplateSpotMarketOptionsTypeDef = TypedDict(
    "LaunchTemplateSpotMarketOptionsTypeDef",
    {
        "MaxPrice": str,
        "SpotInstanceType": SpotInstanceTypeType,
        "BlockDurationMinutes": int,
        "ValidUntil": datetime,
        "InstanceInterruptionBehavior": InstanceInterruptionBehaviorType,
    },
    total=False,
)

LaunchTemplateInstanceMetadataOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateInstanceMetadataOptionsRequestTypeDef",
    {
        "HttpTokens": LaunchTemplateHttpTokensStateType,
        "HttpPutResponseHopLimit": int,
        "HttpEndpoint": LaunchTemplateInstanceMetadataEndpointStateType,
        "HttpProtocolIpv6": LaunchTemplateInstanceMetadataProtocolIpv6Type,
        "InstanceMetadataTags": LaunchTemplateInstanceMetadataTagsStateType,
    },
    total=False,
)

LaunchTemplateInstanceMetadataOptionsTypeDef = TypedDict(
    "LaunchTemplateInstanceMetadataOptionsTypeDef",
    {
        "State": LaunchTemplateInstanceMetadataOptionsStateType,
        "HttpTokens": LaunchTemplateHttpTokensStateType,
        "HttpPutResponseHopLimit": int,
        "HttpEndpoint": LaunchTemplateInstanceMetadataEndpointStateType,
        "HttpProtocolIpv6": LaunchTemplateInstanceMetadataProtocolIpv6Type,
        "InstanceMetadataTags": LaunchTemplateInstanceMetadataTagsStateType,
    },
    total=False,
)

LaunchTemplateLicenseConfigurationRequestTypeDef = TypedDict(
    "LaunchTemplateLicenseConfigurationRequestTypeDef",
    {
        "LicenseConfigurationArn": str,
    },
    total=False,
)

LaunchTemplateLicenseConfigurationTypeDef = TypedDict(
    "LaunchTemplateLicenseConfigurationTypeDef",
    {
        "LicenseConfigurationArn": str,
    },
    total=False,
)

LaunchTemplatePlacementRequestTypeDef = TypedDict(
    "LaunchTemplatePlacementRequestTypeDef",
    {
        "AvailabilityZone": str,
        "Affinity": str,
        "GroupName": str,
        "HostId": str,
        "Tenancy": TenancyType,
        "SpreadDomain": str,
        "HostResourceGroupArn": str,
        "PartitionNumber": int,
    },
    total=False,
)

LaunchTemplatePlacementTypeDef = TypedDict(
    "LaunchTemplatePlacementTypeDef",
    {
        "AvailabilityZone": str,
        "Affinity": str,
        "GroupName": str,
        "HostId": str,
        "Tenancy": TenancyType,
        "SpreadDomain": str,
        "HostResourceGroupArn": str,
        "PartitionNumber": int,
    },
    total=False,
)

LaunchTemplatePrivateDnsNameOptionsRequestTypeDef = TypedDict(
    "LaunchTemplatePrivateDnsNameOptionsRequestTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
    },
    total=False,
)

LaunchTemplatePrivateDnsNameOptionsTypeDef = TypedDict(
    "LaunchTemplatePrivateDnsNameOptionsTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
    },
    total=False,
)

LaunchTemplateSpecificationTypeDef = TypedDict(
    "LaunchTemplateSpecificationTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "Version": str,
    },
    total=False,
)

LaunchTemplatesMonitoringRequestTypeDef = TypedDict(
    "LaunchTemplatesMonitoringRequestTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

LaunchTemplatesMonitoringTypeDef = TypedDict(
    "LaunchTemplatesMonitoringTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

LicenseConfigurationRequestTypeDef = TypedDict(
    "LicenseConfigurationRequestTypeDef",
    {
        "LicenseConfigurationArn": str,
    },
    total=False,
)

ListImagesInRecycleBinRequestRequestTypeDef = TypedDict(
    "ListImagesInRecycleBinRequestRequestTypeDef",
    {
        "ImageIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)

ListSnapshotsInRecycleBinRequestRequestTypeDef = TypedDict(
    "ListSnapshotsInRecycleBinRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "SnapshotIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

SnapshotRecycleBinInfoTypeDef = TypedDict(
    "SnapshotRecycleBinInfoTypeDef",
    {
        "SnapshotId": str,
        "RecycleBinEnterTime": datetime,
        "RecycleBinExitTime": datetime,
        "Description": str,
        "VolumeId": str,
    },
    total=False,
)

LoadPermissionRequestTypeDef = TypedDict(
    "LoadPermissionRequestTypeDef",
    {
        "Group": Literal["all"],
        "UserId": str,
    },
    total=False,
)

_RequiredModifyAddressAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyAddressAttributeRequestRequestTypeDef",
    {
        "AllocationId": str,
    },
)
_OptionalModifyAddressAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyAddressAttributeRequestRequestTypeDef",
    {
        "DomainName": str,
        "DryRun": bool,
    },
    total=False,
)


class ModifyAddressAttributeRequestRequestTypeDef(
    _RequiredModifyAddressAttributeRequestRequestTypeDef,
    _OptionalModifyAddressAttributeRequestRequestTypeDef,
):
    pass


_RequiredModifyAvailabilityZoneGroupRequestRequestTypeDef = TypedDict(
    "_RequiredModifyAvailabilityZoneGroupRequestRequestTypeDef",
    {
        "GroupName": str,
        "OptInStatus": ModifyAvailabilityZoneOptInStatusType,
    },
)
_OptionalModifyAvailabilityZoneGroupRequestRequestTypeDef = TypedDict(
    "_OptionalModifyAvailabilityZoneGroupRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyAvailabilityZoneGroupRequestRequestTypeDef(
    _RequiredModifyAvailabilityZoneGroupRequestRequestTypeDef,
    _OptionalModifyAvailabilityZoneGroupRequestRequestTypeDef,
):
    pass


_RequiredModifyCapacityReservationFleetRequestRequestTypeDef = TypedDict(
    "_RequiredModifyCapacityReservationFleetRequestRequestTypeDef",
    {
        "CapacityReservationFleetId": str,
    },
)
_OptionalModifyCapacityReservationFleetRequestRequestTypeDef = TypedDict(
    "_OptionalModifyCapacityReservationFleetRequestRequestTypeDef",
    {
        "TotalTargetCapacity": int,
        "EndDate": Union[datetime, str],
        "DryRun": bool,
        "RemoveEndDate": bool,
    },
    total=False,
)


class ModifyCapacityReservationFleetRequestRequestTypeDef(
    _RequiredModifyCapacityReservationFleetRequestRequestTypeDef,
    _OptionalModifyCapacityReservationFleetRequestRequestTypeDef,
):
    pass


_RequiredModifyCapacityReservationRequestRequestTypeDef = TypedDict(
    "_RequiredModifyCapacityReservationRequestRequestTypeDef",
    {
        "CapacityReservationId": str,
    },
)
_OptionalModifyCapacityReservationRequestRequestTypeDef = TypedDict(
    "_OptionalModifyCapacityReservationRequestRequestTypeDef",
    {
        "InstanceCount": int,
        "EndDate": Union[datetime, str],
        "EndDateType": EndDateTypeType,
        "Accept": bool,
        "DryRun": bool,
        "AdditionalInfo": str,
    },
    total=False,
)


class ModifyCapacityReservationRequestRequestTypeDef(
    _RequiredModifyCapacityReservationRequestRequestTypeDef,
    _OptionalModifyCapacityReservationRequestRequestTypeDef,
):
    pass


_RequiredModifyDefaultCreditSpecificationRequestRequestTypeDef = TypedDict(
    "_RequiredModifyDefaultCreditSpecificationRequestRequestTypeDef",
    {
        "InstanceFamily": UnlimitedSupportedInstanceFamilyType,
        "CpuCredits": str,
    },
)
_OptionalModifyDefaultCreditSpecificationRequestRequestTypeDef = TypedDict(
    "_OptionalModifyDefaultCreditSpecificationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyDefaultCreditSpecificationRequestRequestTypeDef(
    _RequiredModifyDefaultCreditSpecificationRequestRequestTypeDef,
    _OptionalModifyDefaultCreditSpecificationRequestRequestTypeDef,
):
    pass


_RequiredModifyEbsDefaultKmsKeyIdRequestRequestTypeDef = TypedDict(
    "_RequiredModifyEbsDefaultKmsKeyIdRequestRequestTypeDef",
    {
        "KmsKeyId": str,
    },
)
_OptionalModifyEbsDefaultKmsKeyIdRequestRequestTypeDef = TypedDict(
    "_OptionalModifyEbsDefaultKmsKeyIdRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyEbsDefaultKmsKeyIdRequestRequestTypeDef(
    _RequiredModifyEbsDefaultKmsKeyIdRequestRequestTypeDef,
    _OptionalModifyEbsDefaultKmsKeyIdRequestRequestTypeDef,
):
    pass


_RequiredModifyHostsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyHostsRequestRequestTypeDef",
    {
        "HostIds": Sequence[str],
    },
)
_OptionalModifyHostsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyHostsRequestRequestTypeDef",
    {
        "AutoPlacement": AutoPlacementType,
        "HostRecovery": HostRecoveryType,
        "InstanceType": str,
        "InstanceFamily": str,
    },
    total=False,
)


class ModifyHostsRequestRequestTypeDef(
    _RequiredModifyHostsRequestRequestTypeDef, _OptionalModifyHostsRequestRequestTypeDef
):
    pass


ModifyIdFormatRequestRequestTypeDef = TypedDict(
    "ModifyIdFormatRequestRequestTypeDef",
    {
        "Resource": str,
        "UseLongIds": bool,
    },
)

ModifyIdentityIdFormatRequestRequestTypeDef = TypedDict(
    "ModifyIdentityIdFormatRequestRequestTypeDef",
    {
        "PrincipalArn": str,
        "Resource": str,
        "UseLongIds": bool,
    },
)

SuccessfulInstanceCreditSpecificationItemTypeDef = TypedDict(
    "SuccessfulInstanceCreditSpecificationItemTypeDef",
    {
        "InstanceId": str,
    },
    total=False,
)

_RequiredModifyInstanceEventStartTimeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceEventStartTimeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "InstanceEventId": str,
        "NotBefore": Union[datetime, str],
    },
)
_OptionalModifyInstanceEventStartTimeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceEventStartTimeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyInstanceEventStartTimeRequestRequestTypeDef(
    _RequiredModifyInstanceEventStartTimeRequestRequestTypeDef,
    _OptionalModifyInstanceEventStartTimeRequestRequestTypeDef,
):
    pass


_RequiredModifyInstanceMaintenanceOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceMaintenanceOptionsRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalModifyInstanceMaintenanceOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceMaintenanceOptionsRequestRequestTypeDef",
    {
        "AutoRecovery": InstanceAutoRecoveryStateType,
        "DryRun": bool,
    },
    total=False,
)


class ModifyInstanceMaintenanceOptionsRequestRequestTypeDef(
    _RequiredModifyInstanceMaintenanceOptionsRequestRequestTypeDef,
    _OptionalModifyInstanceMaintenanceOptionsRequestRequestTypeDef,
):
    pass


_RequiredModifyInstanceMetadataOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceMetadataOptionsRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalModifyInstanceMetadataOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceMetadataOptionsRequestRequestTypeDef",
    {
        "HttpTokens": HttpTokensStateType,
        "HttpPutResponseHopLimit": int,
        "HttpEndpoint": InstanceMetadataEndpointStateType,
        "DryRun": bool,
        "HttpProtocolIpv6": InstanceMetadataProtocolStateType,
        "InstanceMetadataTags": InstanceMetadataTagsStateType,
    },
    total=False,
)


class ModifyInstanceMetadataOptionsRequestRequestTypeDef(
    _RequiredModifyInstanceMetadataOptionsRequestRequestTypeDef,
    _OptionalModifyInstanceMetadataOptionsRequestRequestTypeDef,
):
    pass


_RequiredModifyInstancePlacementRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstancePlacementRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalModifyInstancePlacementRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstancePlacementRequestRequestTypeDef",
    {
        "Affinity": AffinityType,
        "GroupName": str,
        "HostId": str,
        "Tenancy": HostTenancyType,
        "PartitionNumber": int,
        "HostResourceGroupArn": str,
    },
    total=False,
)


class ModifyInstancePlacementRequestRequestTypeDef(
    _RequiredModifyInstancePlacementRequestRequestTypeDef,
    _OptionalModifyInstancePlacementRequestRequestTypeDef,
):
    pass


RemoveIpamOperatingRegionTypeDef = TypedDict(
    "RemoveIpamOperatingRegionTypeDef",
    {
        "RegionName": str,
    },
    total=False,
)

_RequiredModifyIpamResourceCidrRequestRequestTypeDef = TypedDict(
    "_RequiredModifyIpamResourceCidrRequestRequestTypeDef",
    {
        "ResourceId": str,
        "ResourceCidr": str,
        "ResourceRegion": str,
        "CurrentIpamScopeId": str,
        "Monitored": bool,
    },
)
_OptionalModifyIpamResourceCidrRequestRequestTypeDef = TypedDict(
    "_OptionalModifyIpamResourceCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
        "DestinationIpamScopeId": str,
    },
    total=False,
)


class ModifyIpamResourceCidrRequestRequestTypeDef(
    _RequiredModifyIpamResourceCidrRequestRequestTypeDef,
    _OptionalModifyIpamResourceCidrRequestRequestTypeDef,
):
    pass


_RequiredModifyIpamScopeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyIpamScopeRequestRequestTypeDef",
    {
        "IpamScopeId": str,
    },
)
_OptionalModifyIpamScopeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyIpamScopeRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Description": str,
    },
    total=False,
)


class ModifyIpamScopeRequestRequestTypeDef(
    _RequiredModifyIpamScopeRequestRequestTypeDef, _OptionalModifyIpamScopeRequestRequestTypeDef
):
    pass


ModifyLaunchTemplateRequestRequestTypeDef = TypedDict(
    "ModifyLaunchTemplateRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ClientToken": str,
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "DefaultVersion": str,
    },
    total=False,
)

RemovePrefixListEntryTypeDef = TypedDict(
    "RemovePrefixListEntryTypeDef",
    {
        "Cidr": str,
    },
)

NetworkInterfaceAttachmentChangesTypeDef = TypedDict(
    "NetworkInterfaceAttachmentChangesTypeDef",
    {
        "AttachmentId": str,
        "DeleteOnTermination": bool,
    },
    total=False,
)

ModifyPrivateDnsNameOptionsRequestRequestTypeDef = TypedDict(
    "ModifyPrivateDnsNameOptionsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "InstanceId": str,
        "PrivateDnsHostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
    },
    total=False,
)

ReservedInstancesConfigurationTypeDef = TypedDict(
    "ReservedInstancesConfigurationTypeDef",
    {
        "AvailabilityZone": str,
        "InstanceCount": int,
        "InstanceType": InstanceTypeType,
        "Platform": str,
        "Scope": scopeType,
    },
    total=False,
)

_RequiredModifySnapshotTierRequestRequestTypeDef = TypedDict(
    "_RequiredModifySnapshotTierRequestRequestTypeDef",
    {
        "SnapshotId": str,
    },
)
_OptionalModifySnapshotTierRequestRequestTypeDef = TypedDict(
    "_OptionalModifySnapshotTierRequestRequestTypeDef",
    {
        "StorageTier": Literal["archive"],
        "DryRun": bool,
    },
    total=False,
)


class ModifySnapshotTierRequestRequestTypeDef(
    _RequiredModifySnapshotTierRequestRequestTypeDef,
    _OptionalModifySnapshotTierRequestRequestTypeDef,
):
    pass


_RequiredModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef = TypedDict(
    "_RequiredModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef",
    {
        "TrafficMirrorFilterId": str,
    },
)
_OptionalModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef = TypedDict(
    "_OptionalModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef",
    {
        "AddNetworkServices": Sequence[Literal["amazon-dns"]],
        "RemoveNetworkServices": Sequence[Literal["amazon-dns"]],
        "DryRun": bool,
    },
    total=False,
)


class ModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef(
    _RequiredModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef,
    _OptionalModifyTrafficMirrorFilterNetworkServicesRequestRequestTypeDef,
):
    pass


_RequiredModifyTrafficMirrorSessionRequestRequestTypeDef = TypedDict(
    "_RequiredModifyTrafficMirrorSessionRequestRequestTypeDef",
    {
        "TrafficMirrorSessionId": str,
    },
)
_OptionalModifyTrafficMirrorSessionRequestRequestTypeDef = TypedDict(
    "_OptionalModifyTrafficMirrorSessionRequestRequestTypeDef",
    {
        "TrafficMirrorTargetId": str,
        "TrafficMirrorFilterId": str,
        "PacketLength": int,
        "SessionNumber": int,
        "VirtualNetworkId": int,
        "Description": str,
        "RemoveFields": Sequence[TrafficMirrorSessionFieldType],
        "DryRun": bool,
    },
    total=False,
)


class ModifyTrafficMirrorSessionRequestRequestTypeDef(
    _RequiredModifyTrafficMirrorSessionRequestRequestTypeDef,
    _OptionalModifyTrafficMirrorSessionRequestRequestTypeDef,
):
    pass


ModifyTransitGatewayOptionsTypeDef = TypedDict(
    "ModifyTransitGatewayOptionsTypeDef",
    {
        "AddTransitGatewayCidrBlocks": Sequence[str],
        "RemoveTransitGatewayCidrBlocks": Sequence[str],
        "VpnEcmpSupport": VpnEcmpSupportValueType,
        "DnsSupport": DnsSupportValueType,
        "AutoAcceptSharedAttachments": AutoAcceptSharedAttachmentsValueType,
        "DefaultRouteTableAssociation": DefaultRouteTableAssociationValueType,
        "AssociationDefaultRouteTableId": str,
        "DefaultRouteTablePropagation": DefaultRouteTablePropagationValueType,
        "PropagationDefaultRouteTableId": str,
    },
    total=False,
)

_RequiredModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef = TypedDict(
    "_RequiredModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "PrefixListId": str,
    },
)
_OptionalModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef = TypedDict(
    "_OptionalModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "Blackhole": bool,
        "DryRun": bool,
    },
    total=False,
)


class ModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef(
    _RequiredModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef,
    _OptionalModifyTransitGatewayPrefixListReferenceRequestRequestTypeDef,
):
    pass


ModifyTransitGatewayVpcAttachmentRequestOptionsTypeDef = TypedDict(
    "ModifyTransitGatewayVpcAttachmentRequestOptionsTypeDef",
    {
        "DnsSupport": DnsSupportValueType,
        "Ipv6Support": Ipv6SupportValueType,
        "ApplianceModeSupport": ApplianceModeSupportValueType,
    },
    total=False,
)

_RequiredModifyVolumeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVolumeRequestRequestTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalModifyVolumeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVolumeRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Size": int,
        "VolumeType": VolumeTypeType,
        "Iops": int,
        "Throughput": int,
        "MultiAttachEnabled": bool,
    },
    total=False,
)


class ModifyVolumeRequestRequestTypeDef(
    _RequiredModifyVolumeRequestRequestTypeDef, _OptionalModifyVolumeRequestRequestTypeDef
):
    pass


_RequiredModifyVpcEndpointConnectionNotificationRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcEndpointConnectionNotificationRequestRequestTypeDef",
    {
        "ConnectionNotificationId": str,
    },
)
_OptionalModifyVpcEndpointConnectionNotificationRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcEndpointConnectionNotificationRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ConnectionNotificationArn": str,
        "ConnectionEvents": Sequence[str],
    },
    total=False,
)


class ModifyVpcEndpointConnectionNotificationRequestRequestTypeDef(
    _RequiredModifyVpcEndpointConnectionNotificationRequestRequestTypeDef,
    _OptionalModifyVpcEndpointConnectionNotificationRequestRequestTypeDef,
):
    pass


_RequiredModifyVpcEndpointServiceConfigurationRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcEndpointServiceConfigurationRequestRequestTypeDef",
    {
        "ServiceId": str,
    },
)
_OptionalModifyVpcEndpointServiceConfigurationRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcEndpointServiceConfigurationRequestRequestTypeDef",
    {
        "DryRun": bool,
        "PrivateDnsName": str,
        "RemovePrivateDnsName": bool,
        "AcceptanceRequired": bool,
        "AddNetworkLoadBalancerArns": Sequence[str],
        "RemoveNetworkLoadBalancerArns": Sequence[str],
        "AddGatewayLoadBalancerArns": Sequence[str],
        "RemoveGatewayLoadBalancerArns": Sequence[str],
        "AddSupportedIpAddressTypes": Sequence[str],
        "RemoveSupportedIpAddressTypes": Sequence[str],
    },
    total=False,
)


class ModifyVpcEndpointServiceConfigurationRequestRequestTypeDef(
    _RequiredModifyVpcEndpointServiceConfigurationRequestRequestTypeDef,
    _OptionalModifyVpcEndpointServiceConfigurationRequestRequestTypeDef,
):
    pass


_RequiredModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef",
    {
        "ServiceId": str,
        "PayerResponsibility": Literal["ServiceOwner"],
    },
)
_OptionalModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef(
    _RequiredModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef,
    _OptionalModifyVpcEndpointServicePayerResponsibilityRequestRequestTypeDef,
):
    pass


_RequiredModifyVpcEndpointServicePermissionsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcEndpointServicePermissionsRequestRequestTypeDef",
    {
        "ServiceId": str,
    },
)
_OptionalModifyVpcEndpointServicePermissionsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcEndpointServicePermissionsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "AddAllowedPrincipals": Sequence[str],
        "RemoveAllowedPrincipals": Sequence[str],
    },
    total=False,
)


class ModifyVpcEndpointServicePermissionsRequestRequestTypeDef(
    _RequiredModifyVpcEndpointServicePermissionsRequestRequestTypeDef,
    _OptionalModifyVpcEndpointServicePermissionsRequestRequestTypeDef,
):
    pass


PeeringConnectionOptionsRequestTypeDef = TypedDict(
    "PeeringConnectionOptionsRequestTypeDef",
    {
        "AllowDnsResolutionFromRemoteVpc": bool,
        "AllowEgressFromLocalClassicLinkToRemoteVpc": bool,
        "AllowEgressFromLocalVpcToRemoteClassicLink": bool,
    },
    total=False,
)

PeeringConnectionOptionsTypeDef = TypedDict(
    "PeeringConnectionOptionsTypeDef",
    {
        "AllowDnsResolutionFromRemoteVpc": bool,
        "AllowEgressFromLocalClassicLinkToRemoteVpc": bool,
        "AllowEgressFromLocalVpcToRemoteClassicLink": bool,
    },
    total=False,
)

_RequiredModifyVpcTenancyRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcTenancyRequestRequestTypeDef",
    {
        "VpcId": str,
        "InstanceTenancy": Literal["default"],
    },
)
_OptionalModifyVpcTenancyRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcTenancyRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyVpcTenancyRequestRequestTypeDef(
    _RequiredModifyVpcTenancyRequestRequestTypeDef, _OptionalModifyVpcTenancyRequestRequestTypeDef
):
    pass


_RequiredModifyVpnConnectionOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpnConnectionOptionsRequestRequestTypeDef",
    {
        "VpnConnectionId": str,
    },
)
_OptionalModifyVpnConnectionOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpnConnectionOptionsRequestRequestTypeDef",
    {
        "LocalIpv4NetworkCidr": str,
        "RemoteIpv4NetworkCidr": str,
        "LocalIpv6NetworkCidr": str,
        "RemoteIpv6NetworkCidr": str,
        "DryRun": bool,
    },
    total=False,
)


class ModifyVpnConnectionOptionsRequestRequestTypeDef(
    _RequiredModifyVpnConnectionOptionsRequestRequestTypeDef,
    _OptionalModifyVpnConnectionOptionsRequestRequestTypeDef,
):
    pass


_RequiredModifyVpnConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpnConnectionRequestRequestTypeDef",
    {
        "VpnConnectionId": str,
    },
)
_OptionalModifyVpnConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpnConnectionRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
        "CustomerGatewayId": str,
        "VpnGatewayId": str,
        "DryRun": bool,
    },
    total=False,
)


class ModifyVpnConnectionRequestRequestTypeDef(
    _RequiredModifyVpnConnectionRequestRequestTypeDef,
    _OptionalModifyVpnConnectionRequestRequestTypeDef,
):
    pass


_RequiredModifyVpnTunnelCertificateRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpnTunnelCertificateRequestRequestTypeDef",
    {
        "VpnConnectionId": str,
        "VpnTunnelOutsideIpAddress": str,
    },
)
_OptionalModifyVpnTunnelCertificateRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpnTunnelCertificateRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyVpnTunnelCertificateRequestRequestTypeDef(
    _RequiredModifyVpnTunnelCertificateRequestRequestTypeDef,
    _OptionalModifyVpnTunnelCertificateRequestRequestTypeDef,
):
    pass


Phase1DHGroupNumbersRequestListValueTypeDef = TypedDict(
    "Phase1DHGroupNumbersRequestListValueTypeDef",
    {
        "Value": int,
    },
    total=False,
)

Phase1EncryptionAlgorithmsRequestListValueTypeDef = TypedDict(
    "Phase1EncryptionAlgorithmsRequestListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

Phase1IntegrityAlgorithmsRequestListValueTypeDef = TypedDict(
    "Phase1IntegrityAlgorithmsRequestListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

Phase2DHGroupNumbersRequestListValueTypeDef = TypedDict(
    "Phase2DHGroupNumbersRequestListValueTypeDef",
    {
        "Value": int,
    },
    total=False,
)

Phase2EncryptionAlgorithmsRequestListValueTypeDef = TypedDict(
    "Phase2EncryptionAlgorithmsRequestListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

Phase2IntegrityAlgorithmsRequestListValueTypeDef = TypedDict(
    "Phase2IntegrityAlgorithmsRequestListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

MonitorInstancesRequestInstanceMonitorTypeDef = TypedDict(
    "MonitorInstancesRequestInstanceMonitorTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredMonitorInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredMonitorInstancesRequestRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
    },
)
_OptionalMonitorInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalMonitorInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class MonitorInstancesRequestRequestTypeDef(
    _RequiredMonitorInstancesRequestRequestTypeDef, _OptionalMonitorInstancesRequestRequestTypeDef
):
    pass


_RequiredMoveAddressToVpcRequestRequestTypeDef = TypedDict(
    "_RequiredMoveAddressToVpcRequestRequestTypeDef",
    {
        "PublicIp": str,
    },
)
_OptionalMoveAddressToVpcRequestRequestTypeDef = TypedDict(
    "_OptionalMoveAddressToVpcRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class MoveAddressToVpcRequestRequestTypeDef(
    _RequiredMoveAddressToVpcRequestRequestTypeDef, _OptionalMoveAddressToVpcRequestRequestTypeDef
):
    pass


_RequiredMoveByoipCidrToIpamRequestRequestTypeDef = TypedDict(
    "_RequiredMoveByoipCidrToIpamRequestRequestTypeDef",
    {
        "Cidr": str,
        "IpamPoolId": str,
        "IpamPoolOwner": str,
    },
)
_OptionalMoveByoipCidrToIpamRequestRequestTypeDef = TypedDict(
    "_OptionalMoveByoipCidrToIpamRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class MoveByoipCidrToIpamRequestRequestTypeDef(
    _RequiredMoveByoipCidrToIpamRequestRequestTypeDef,
    _OptionalMoveByoipCidrToIpamRequestRequestTypeDef,
):
    pass


NatGatewayAddressTypeDef = TypedDict(
    "NatGatewayAddressTypeDef",
    {
        "AllocationId": str,
        "NetworkInterfaceId": str,
        "PrivateIp": str,
        "PublicIp": str,
    },
    total=False,
)

ProvisionedBandwidthTypeDef = TypedDict(
    "ProvisionedBandwidthTypeDef",
    {
        "ProvisionTime": datetime,
        "Provisioned": str,
        "RequestTime": datetime,
        "Requested": str,
        "Status": str,
    },
    total=False,
)

NetworkAclAssociationTypeDef = TypedDict(
    "NetworkAclAssociationTypeDef",
    {
        "NetworkAclAssociationId": str,
        "NetworkAclId": str,
        "SubnetId": str,
    },
    total=False,
)

NetworkCardInfoTypeDef = TypedDict(
    "NetworkCardInfoTypeDef",
    {
        "NetworkCardIndex": int,
        "NetworkPerformance": str,
        "MaximumNetworkInterfaces": int,
    },
    total=False,
)

NetworkInterfaceAssociationTypeDef = TypedDict(
    "NetworkInterfaceAssociationTypeDef",
    {
        "AllocationId": str,
        "AssociationId": str,
        "IpOwnerId": str,
        "PublicDnsName": str,
        "PublicIp": str,
        "CustomerOwnedIp": str,
        "CarrierIp": str,
    },
    total=False,
)

NetworkInterfaceIpv6AddressTypeDef = TypedDict(
    "NetworkInterfaceIpv6AddressTypeDef",
    {
        "Ipv6Address": str,
    },
    total=False,
)

NetworkInterfacePermissionStateTypeDef = TypedDict(
    "NetworkInterfacePermissionStateTypeDef",
    {
        "State": NetworkInterfacePermissionStateCodeType,
        "StatusMessage": str,
    },
    total=False,
)

PacketHeaderStatementRequestTypeDef = TypedDict(
    "PacketHeaderStatementRequestTypeDef",
    {
        "SourceAddresses": Sequence[str],
        "DestinationAddresses": Sequence[str],
        "SourcePorts": Sequence[str],
        "DestinationPorts": Sequence[str],
        "SourcePrefixLists": Sequence[str],
        "DestinationPrefixLists": Sequence[str],
        "Protocols": Sequence[ProtocolType],
    },
    total=False,
)

PacketHeaderStatementTypeDef = TypedDict(
    "PacketHeaderStatementTypeDef",
    {
        "SourceAddresses": List[str],
        "DestinationAddresses": List[str],
        "SourcePorts": List[str],
        "DestinationPorts": List[str],
        "SourcePrefixLists": List[str],
        "DestinationPrefixLists": List[str],
        "Protocols": List[ProtocolType],
    },
    total=False,
)

ResourceStatementRequestTypeDef = TypedDict(
    "ResourceStatementRequestTypeDef",
    {
        "Resources": Sequence[str],
        "ResourceTypes": Sequence[str],
    },
    total=False,
)

ResourceStatementTypeDef = TypedDict(
    "ResourceStatementTypeDef",
    {
        "Resources": List[str],
        "ResourceTypes": List[str],
    },
    total=False,
)

PeeringAttachmentStatusTypeDef = TypedDict(
    "PeeringAttachmentStatusTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

PeeringTgwInfoTypeDef = TypedDict(
    "PeeringTgwInfoTypeDef",
    {
        "TransitGatewayId": str,
        "OwnerId": str,
        "Region": str,
    },
    total=False,
)

Phase1DHGroupNumbersListValueTypeDef = TypedDict(
    "Phase1DHGroupNumbersListValueTypeDef",
    {
        "Value": int,
    },
    total=False,
)

Phase1EncryptionAlgorithmsListValueTypeDef = TypedDict(
    "Phase1EncryptionAlgorithmsListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

Phase1IntegrityAlgorithmsListValueTypeDef = TypedDict(
    "Phase1IntegrityAlgorithmsListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

Phase2DHGroupNumbersListValueTypeDef = TypedDict(
    "Phase2DHGroupNumbersListValueTypeDef",
    {
        "Value": int,
    },
    total=False,
)

Phase2EncryptionAlgorithmsListValueTypeDef = TypedDict(
    "Phase2EncryptionAlgorithmsListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

Phase2IntegrityAlgorithmsListValueTypeDef = TypedDict(
    "Phase2IntegrityAlgorithmsListValueTypeDef",
    {
        "Value": str,
    },
    total=False,
)

PriceScheduleTypeDef = TypedDict(
    "PriceScheduleTypeDef",
    {
        "Active": bool,
        "CurrencyCode": Literal["USD"],
        "Price": float,
        "Term": int,
    },
    total=False,
)

PricingDetailTypeDef = TypedDict(
    "PricingDetailTypeDef",
    {
        "Count": int,
        "Price": float,
    },
    total=False,
)

PrivateDnsDetailsTypeDef = TypedDict(
    "PrivateDnsDetailsTypeDef",
    {
        "PrivateDnsName": str,
    },
    total=False,
)

PrivateDnsNameConfigurationTypeDef = TypedDict(
    "PrivateDnsNameConfigurationTypeDef",
    {
        "State": DnsNameStateType,
        "Type": str,
        "Value": str,
        "Name": str,
    },
    total=False,
)

PrivateDnsNameOptionsOnLaunchTypeDef = TypedDict(
    "PrivateDnsNameOptionsOnLaunchTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
    },
    total=False,
)

PrivateDnsNameOptionsRequestTypeDef = TypedDict(
    "PrivateDnsNameOptionsRequestTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
    },
    total=False,
)

PropagatingVgwTypeDef = TypedDict(
    "PropagatingVgwTypeDef",
    {
        "GatewayId": str,
    },
    total=False,
)

_RequiredProvisionPublicIpv4PoolCidrRequestRequestTypeDef = TypedDict(
    "_RequiredProvisionPublicIpv4PoolCidrRequestRequestTypeDef",
    {
        "IpamPoolId": str,
        "PoolId": str,
        "NetmaskLength": int,
    },
)
_OptionalProvisionPublicIpv4PoolCidrRequestRequestTypeDef = TypedDict(
    "_OptionalProvisionPublicIpv4PoolCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ProvisionPublicIpv4PoolCidrRequestRequestTypeDef(
    _RequiredProvisionPublicIpv4PoolCidrRequestRequestTypeDef,
    _OptionalProvisionPublicIpv4PoolCidrRequestRequestTypeDef,
):
    pass


PublicIpv4PoolRangeTypeDef = TypedDict(
    "PublicIpv4PoolRangeTypeDef",
    {
        "FirstAddress": str,
        "LastAddress": str,
        "AddressCount": int,
        "AvailableAddressCount": int,
    },
    total=False,
)

PurchaseRequestTypeDef = TypedDict(
    "PurchaseRequestTypeDef",
    {
        "InstanceCount": int,
        "PurchaseToken": str,
    },
)

ReservedInstanceLimitPriceTypeDef = TypedDict(
    "ReservedInstanceLimitPriceTypeDef",
    {
        "Amount": float,
        "CurrencyCode": Literal["USD"],
    },
    total=False,
)

RebootInstancesRequestInstanceRebootTypeDef = TypedDict(
    "RebootInstancesRequestInstanceRebootTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredRebootInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredRebootInstancesRequestRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
    },
)
_OptionalRebootInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalRebootInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RebootInstancesRequestRequestTypeDef(
    _RequiredRebootInstancesRequestRequestTypeDef, _OptionalRebootInstancesRequestRequestTypeDef
):
    pass


RecurringChargeTypeDef = TypedDict(
    "RecurringChargeTypeDef",
    {
        "Amount": float,
        "Frequency": Literal["Hourly"],
    },
    total=False,
)

ReferencedSecurityGroupTypeDef = TypedDict(
    "ReferencedSecurityGroupTypeDef",
    {
        "GroupId": str,
        "PeeringStatus": str,
        "UserId": str,
        "VpcId": str,
        "VpcPeeringConnectionId": str,
    },
    total=False,
)

RegisterInstanceTagAttributeRequestTypeDef = TypedDict(
    "RegisterInstanceTagAttributeRequestTypeDef",
    {
        "IncludeAllTagsOfInstance": bool,
        "InstanceTagKeys": Sequence[str],
    },
    total=False,
)

RegisterTransitGatewayMulticastGroupMembersRequestRequestTypeDef = TypedDict(
    "RegisterTransitGatewayMulticastGroupMembersRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "GroupIpAddress": str,
        "NetworkInterfaceIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

TransitGatewayMulticastRegisteredGroupMembersTypeDef = TypedDict(
    "TransitGatewayMulticastRegisteredGroupMembersTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "RegisteredNetworkInterfaceIds": List[str],
        "GroupIpAddress": str,
    },
    total=False,
)

RegisterTransitGatewayMulticastGroupSourcesRequestRequestTypeDef = TypedDict(
    "RegisterTransitGatewayMulticastGroupSourcesRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "GroupIpAddress": str,
        "NetworkInterfaceIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

TransitGatewayMulticastRegisteredGroupSourcesTypeDef = TypedDict(
    "TransitGatewayMulticastRegisteredGroupSourcesTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "RegisteredNetworkInterfaceIds": List[str],
        "GroupIpAddress": str,
    },
    total=False,
)

RejectTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef = TypedDict(
    "RejectTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "TransitGatewayAttachmentId": str,
        "SubnetIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

_RequiredRejectTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredRejectTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalRejectTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalRejectTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RejectTransitGatewayPeeringAttachmentRequestRequestTypeDef(
    _RequiredRejectTransitGatewayPeeringAttachmentRequestRequestTypeDef,
    _OptionalRejectTransitGatewayPeeringAttachmentRequestRequestTypeDef,
):
    pass


_RequiredRejectTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredRejectTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalRejectTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalRejectTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RejectTransitGatewayVpcAttachmentRequestRequestTypeDef(
    _RequiredRejectTransitGatewayVpcAttachmentRequestRequestTypeDef,
    _OptionalRejectTransitGatewayVpcAttachmentRequestRequestTypeDef,
):
    pass


_RequiredRejectVpcEndpointConnectionsRequestRequestTypeDef = TypedDict(
    "_RequiredRejectVpcEndpointConnectionsRequestRequestTypeDef",
    {
        "ServiceId": str,
        "VpcEndpointIds": Sequence[str],
    },
)
_OptionalRejectVpcEndpointConnectionsRequestRequestTypeDef = TypedDict(
    "_OptionalRejectVpcEndpointConnectionsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RejectVpcEndpointConnectionsRequestRequestTypeDef(
    _RequiredRejectVpcEndpointConnectionsRequestRequestTypeDef,
    _OptionalRejectVpcEndpointConnectionsRequestRequestTypeDef,
):
    pass


_RequiredRejectVpcPeeringConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredRejectVpcPeeringConnectionRequestRequestTypeDef",
    {
        "VpcPeeringConnectionId": str,
    },
)
_OptionalRejectVpcPeeringConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalRejectVpcPeeringConnectionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RejectVpcPeeringConnectionRequestRequestTypeDef(
    _RequiredRejectVpcPeeringConnectionRequestRequestTypeDef,
    _OptionalRejectVpcPeeringConnectionRequestRequestTypeDef,
):
    pass


RejectVpcPeeringConnectionRequestVpcPeeringConnectionRejectTypeDef = TypedDict(
    "RejectVpcPeeringConnectionRequestVpcPeeringConnectionRejectTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

ReleaseAddressRequestClassicAddressReleaseTypeDef = TypedDict(
    "ReleaseAddressRequestClassicAddressReleaseTypeDef",
    {
        "AllocationId": str,
        "PublicIp": str,
        "NetworkBorderGroup": str,
        "DryRun": bool,
    },
    total=False,
)

ReleaseAddressRequestRequestTypeDef = TypedDict(
    "ReleaseAddressRequestRequestTypeDef",
    {
        "AllocationId": str,
        "PublicIp": str,
        "NetworkBorderGroup": str,
        "DryRun": bool,
    },
    total=False,
)

ReleaseAddressRequestVpcAddressReleaseTypeDef = TypedDict(
    "ReleaseAddressRequestVpcAddressReleaseTypeDef",
    {
        "AllocationId": str,
        "PublicIp": str,
        "NetworkBorderGroup": str,
        "DryRun": bool,
    },
    total=False,
)

ReleaseHostsRequestRequestTypeDef = TypedDict(
    "ReleaseHostsRequestRequestTypeDef",
    {
        "HostIds": Sequence[str],
    },
)

_RequiredReleaseIpamPoolAllocationRequestRequestTypeDef = TypedDict(
    "_RequiredReleaseIpamPoolAllocationRequestRequestTypeDef",
    {
        "IpamPoolId": str,
        "Cidr": str,
        "IpamPoolAllocationId": str,
    },
)
_OptionalReleaseIpamPoolAllocationRequestRequestTypeDef = TypedDict(
    "_OptionalReleaseIpamPoolAllocationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ReleaseIpamPoolAllocationRequestRequestTypeDef(
    _RequiredReleaseIpamPoolAllocationRequestRequestTypeDef,
    _OptionalReleaseIpamPoolAllocationRequestRequestTypeDef,
):
    pass


_RequiredReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef = TypedDict(
    "_RequiredReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef",
    {
        "AssociationId": str,
    },
)
_OptionalReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef = TypedDict(
    "_OptionalReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef(
    _RequiredReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef,
    _OptionalReplaceNetworkAclAssociationRequestNetworkAclReplaceAssociationTypeDef,
):
    pass


_RequiredReplaceNetworkAclAssociationRequestRequestTypeDef = TypedDict(
    "_RequiredReplaceNetworkAclAssociationRequestRequestTypeDef",
    {
        "AssociationId": str,
        "NetworkAclId": str,
    },
)
_OptionalReplaceNetworkAclAssociationRequestRequestTypeDef = TypedDict(
    "_OptionalReplaceNetworkAclAssociationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ReplaceNetworkAclAssociationRequestRequestTypeDef(
    _RequiredReplaceNetworkAclAssociationRequestRequestTypeDef,
    _OptionalReplaceNetworkAclAssociationRequestRequestTypeDef,
):
    pass


_RequiredReplaceRouteRequestRequestTypeDef = TypedDict(
    "_RequiredReplaceRouteRequestRequestTypeDef",
    {
        "RouteTableId": str,
    },
)
_OptionalReplaceRouteRequestRequestTypeDef = TypedDict(
    "_OptionalReplaceRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "DryRun": bool,
        "VpcEndpointId": str,
        "EgressOnlyInternetGatewayId": str,
        "GatewayId": str,
        "InstanceId": str,
        "LocalTarget": bool,
        "NatGatewayId": str,
        "TransitGatewayId": str,
        "LocalGatewayId": str,
        "CarrierGatewayId": str,
        "NetworkInterfaceId": str,
        "VpcPeeringConnectionId": str,
        "CoreNetworkArn": str,
    },
    total=False,
)


class ReplaceRouteRequestRequestTypeDef(
    _RequiredReplaceRouteRequestRequestTypeDef, _OptionalReplaceRouteRequestRequestTypeDef
):
    pass


ReplaceRouteRequestRouteReplaceTypeDef = TypedDict(
    "ReplaceRouteRequestRouteReplaceTypeDef",
    {
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "DryRun": bool,
        "VpcEndpointId": str,
        "EgressOnlyInternetGatewayId": str,
        "GatewayId": str,
        "InstanceId": str,
        "LocalTarget": bool,
        "NatGatewayId": str,
        "TransitGatewayId": str,
        "LocalGatewayId": str,
        "CarrierGatewayId": str,
        "NetworkInterfaceId": str,
        "VpcPeeringConnectionId": str,
        "CoreNetworkArn": str,
    },
    total=False,
)

_RequiredReplaceRouteTableAssociationRequestRequestTypeDef = TypedDict(
    "_RequiredReplaceRouteTableAssociationRequestRequestTypeDef",
    {
        "AssociationId": str,
        "RouteTableId": str,
    },
)
_OptionalReplaceRouteTableAssociationRequestRequestTypeDef = TypedDict(
    "_OptionalReplaceRouteTableAssociationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ReplaceRouteTableAssociationRequestRequestTypeDef(
    _RequiredReplaceRouteTableAssociationRequestRequestTypeDef,
    _OptionalReplaceRouteTableAssociationRequestRequestTypeDef,
):
    pass


_RequiredReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef = TypedDict(
    "_RequiredReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef",
    {
        "RouteTableId": str,
    },
)
_OptionalReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef = TypedDict(
    "_OptionalReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef(
    _RequiredReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef,
    _OptionalReplaceRouteTableAssociationRequestRouteTableAssociationReplaceSubnetTypeDef,
):
    pass


_RequiredReplaceTransitGatewayRouteRequestRequestTypeDef = TypedDict(
    "_RequiredReplaceTransitGatewayRouteRequestRequestTypeDef",
    {
        "DestinationCidrBlock": str,
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalReplaceTransitGatewayRouteRequestRequestTypeDef = TypedDict(
    "_OptionalReplaceTransitGatewayRouteRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "Blackhole": bool,
        "DryRun": bool,
    },
    total=False,
)


class ReplaceTransitGatewayRouteRequestRequestTypeDef(
    _RequiredReplaceTransitGatewayRouteRequestRequestTypeDef,
    _OptionalReplaceTransitGatewayRouteRequestRequestTypeDef,
):
    pass


_RequiredReportInstanceStatusRequestInstanceReportStatusTypeDef = TypedDict(
    "_RequiredReportInstanceStatusRequestInstanceReportStatusTypeDef",
    {
        "ReasonCodes": Sequence[ReportInstanceReasonCodesType],
        "Status": ReportStatusTypeType,
    },
)
_OptionalReportInstanceStatusRequestInstanceReportStatusTypeDef = TypedDict(
    "_OptionalReportInstanceStatusRequestInstanceReportStatusTypeDef",
    {
        "Description": str,
        "DryRun": bool,
        "EndTime": Union[datetime, str],
        "StartTime": Union[datetime, str],
    },
    total=False,
)


class ReportInstanceStatusRequestInstanceReportStatusTypeDef(
    _RequiredReportInstanceStatusRequestInstanceReportStatusTypeDef,
    _OptionalReportInstanceStatusRequestInstanceReportStatusTypeDef,
):
    pass


_RequiredReportInstanceStatusRequestRequestTypeDef = TypedDict(
    "_RequiredReportInstanceStatusRequestRequestTypeDef",
    {
        "Instances": Sequence[str],
        "ReasonCodes": Sequence[ReportInstanceReasonCodesType],
        "Status": ReportStatusTypeType,
    },
)
_OptionalReportInstanceStatusRequestRequestTypeDef = TypedDict(
    "_OptionalReportInstanceStatusRequestRequestTypeDef",
    {
        "Description": str,
        "DryRun": bool,
        "EndTime": Union[datetime, str],
        "StartTime": Union[datetime, str],
    },
    total=False,
)


class ReportInstanceStatusRequestRequestTypeDef(
    _RequiredReportInstanceStatusRequestRequestTypeDef,
    _OptionalReportInstanceStatusRequestRequestTypeDef,
):
    pass


ReservedInstancesIdTypeDef = TypedDict(
    "ReservedInstancesIdTypeDef",
    {
        "ReservedInstancesId": str,
    },
    total=False,
)

_RequiredResetAddressAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredResetAddressAttributeRequestRequestTypeDef",
    {
        "AllocationId": str,
        "Attribute": Literal["domain-name"],
    },
)
_OptionalResetAddressAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalResetAddressAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetAddressAttributeRequestRequestTypeDef(
    _RequiredResetAddressAttributeRequestRequestTypeDef,
    _OptionalResetAddressAttributeRequestRequestTypeDef,
):
    pass


ResetEbsDefaultKmsKeyIdRequestRequestTypeDef = TypedDict(
    "ResetEbsDefaultKmsKeyIdRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredResetFpgaImageAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredResetFpgaImageAttributeRequestRequestTypeDef",
    {
        "FpgaImageId": str,
    },
)
_OptionalResetFpgaImageAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalResetFpgaImageAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Attribute": Literal["loadPermission"],
    },
    total=False,
)


class ResetFpgaImageAttributeRequestRequestTypeDef(
    _RequiredResetFpgaImageAttributeRequestRequestTypeDef,
    _OptionalResetFpgaImageAttributeRequestRequestTypeDef,
):
    pass


_RequiredResetImageAttributeRequestImageResetAttributeTypeDef = TypedDict(
    "_RequiredResetImageAttributeRequestImageResetAttributeTypeDef",
    {
        "Attribute": Literal["launchPermission"],
    },
)
_OptionalResetImageAttributeRequestImageResetAttributeTypeDef = TypedDict(
    "_OptionalResetImageAttributeRequestImageResetAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetImageAttributeRequestImageResetAttributeTypeDef(
    _RequiredResetImageAttributeRequestImageResetAttributeTypeDef,
    _OptionalResetImageAttributeRequestImageResetAttributeTypeDef,
):
    pass


_RequiredResetImageAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredResetImageAttributeRequestRequestTypeDef",
    {
        "Attribute": Literal["launchPermission"],
        "ImageId": str,
    },
)
_OptionalResetImageAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalResetImageAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetImageAttributeRequestRequestTypeDef(
    _RequiredResetImageAttributeRequestRequestTypeDef,
    _OptionalResetImageAttributeRequestRequestTypeDef,
):
    pass


_RequiredResetInstanceAttributeRequestInstanceResetAttributeTypeDef = TypedDict(
    "_RequiredResetInstanceAttributeRequestInstanceResetAttributeTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
    },
)
_OptionalResetInstanceAttributeRequestInstanceResetAttributeTypeDef = TypedDict(
    "_OptionalResetInstanceAttributeRequestInstanceResetAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetInstanceAttributeRequestInstanceResetAttributeTypeDef(
    _RequiredResetInstanceAttributeRequestInstanceResetAttributeTypeDef,
    _OptionalResetInstanceAttributeRequestInstanceResetAttributeTypeDef,
):
    pass


ResetInstanceAttributeRequestInstanceResetKernelTypeDef = TypedDict(
    "ResetInstanceAttributeRequestInstanceResetKernelTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
        "DryRun": bool,
    },
    total=False,
)

ResetInstanceAttributeRequestInstanceResetRamdiskTypeDef = TypedDict(
    "ResetInstanceAttributeRequestInstanceResetRamdiskTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
        "DryRun": bool,
    },
    total=False,
)

ResetInstanceAttributeRequestInstanceResetSourceDestCheckTypeDef = TypedDict(
    "ResetInstanceAttributeRequestInstanceResetSourceDestCheckTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
        "DryRun": bool,
    },
    total=False,
)

_RequiredResetInstanceAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredResetInstanceAttributeRequestRequestTypeDef",
    {
        "Attribute": InstanceAttributeNameType,
        "InstanceId": str,
    },
)
_OptionalResetInstanceAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalResetInstanceAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetInstanceAttributeRequestRequestTypeDef(
    _RequiredResetInstanceAttributeRequestRequestTypeDef,
    _OptionalResetInstanceAttributeRequestRequestTypeDef,
):
    pass


ResetNetworkInterfaceAttributeRequestNetworkInterfaceResetAttributeTypeDef = TypedDict(
    "ResetNetworkInterfaceAttributeRequestNetworkInterfaceResetAttributeTypeDef",
    {
        "DryRun": bool,
        "SourceDestCheck": str,
    },
    total=False,
)

_RequiredResetNetworkInterfaceAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredResetNetworkInterfaceAttributeRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalResetNetworkInterfaceAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalResetNetworkInterfaceAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
        "SourceDestCheck": str,
    },
    total=False,
)


class ResetNetworkInterfaceAttributeRequestRequestTypeDef(
    _RequiredResetNetworkInterfaceAttributeRequestRequestTypeDef,
    _OptionalResetNetworkInterfaceAttributeRequestRequestTypeDef,
):
    pass


_RequiredResetSnapshotAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredResetSnapshotAttributeRequestRequestTypeDef",
    {
        "Attribute": SnapshotAttributeNameType,
        "SnapshotId": str,
    },
)
_OptionalResetSnapshotAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalResetSnapshotAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetSnapshotAttributeRequestRequestTypeDef(
    _RequiredResetSnapshotAttributeRequestRequestTypeDef,
    _OptionalResetSnapshotAttributeRequestRequestTypeDef,
):
    pass


_RequiredResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef = TypedDict(
    "_RequiredResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef",
    {
        "Attribute": SnapshotAttributeNameType,
    },
)
_OptionalResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef = TypedDict(
    "_OptionalResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef(
    _RequiredResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef,
    _OptionalResetSnapshotAttributeRequestSnapshotResetAttributeTypeDef,
):
    pass


_RequiredRestoreAddressToClassicRequestRequestTypeDef = TypedDict(
    "_RequiredRestoreAddressToClassicRequestRequestTypeDef",
    {
        "PublicIp": str,
    },
)
_OptionalRestoreAddressToClassicRequestRequestTypeDef = TypedDict(
    "_OptionalRestoreAddressToClassicRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RestoreAddressToClassicRequestRequestTypeDef(
    _RequiredRestoreAddressToClassicRequestRequestTypeDef,
    _OptionalRestoreAddressToClassicRequestRequestTypeDef,
):
    pass


_RequiredRestoreImageFromRecycleBinRequestRequestTypeDef = TypedDict(
    "_RequiredRestoreImageFromRecycleBinRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalRestoreImageFromRecycleBinRequestRequestTypeDef = TypedDict(
    "_OptionalRestoreImageFromRecycleBinRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RestoreImageFromRecycleBinRequestRequestTypeDef(
    _RequiredRestoreImageFromRecycleBinRequestRequestTypeDef,
    _OptionalRestoreImageFromRecycleBinRequestRequestTypeDef,
):
    pass


_RequiredRestoreManagedPrefixListVersionRequestRequestTypeDef = TypedDict(
    "_RequiredRestoreManagedPrefixListVersionRequestRequestTypeDef",
    {
        "PrefixListId": str,
        "PreviousVersion": int,
        "CurrentVersion": int,
    },
)
_OptionalRestoreManagedPrefixListVersionRequestRequestTypeDef = TypedDict(
    "_OptionalRestoreManagedPrefixListVersionRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RestoreManagedPrefixListVersionRequestRequestTypeDef(
    _RequiredRestoreManagedPrefixListVersionRequestRequestTypeDef,
    _OptionalRestoreManagedPrefixListVersionRequestRequestTypeDef,
):
    pass


_RequiredRestoreSnapshotFromRecycleBinRequestRequestTypeDef = TypedDict(
    "_RequiredRestoreSnapshotFromRecycleBinRequestRequestTypeDef",
    {
        "SnapshotId": str,
    },
)
_OptionalRestoreSnapshotFromRecycleBinRequestRequestTypeDef = TypedDict(
    "_OptionalRestoreSnapshotFromRecycleBinRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RestoreSnapshotFromRecycleBinRequestRequestTypeDef(
    _RequiredRestoreSnapshotFromRecycleBinRequestRequestTypeDef,
    _OptionalRestoreSnapshotFromRecycleBinRequestRequestTypeDef,
):
    pass


_RequiredRestoreSnapshotTierRequestRequestTypeDef = TypedDict(
    "_RequiredRestoreSnapshotTierRequestRequestTypeDef",
    {
        "SnapshotId": str,
    },
)
_OptionalRestoreSnapshotTierRequestRequestTypeDef = TypedDict(
    "_OptionalRestoreSnapshotTierRequestRequestTypeDef",
    {
        "TemporaryRestoreDays": int,
        "PermanentRestore": bool,
        "DryRun": bool,
    },
    total=False,
)


class RestoreSnapshotTierRequestRequestTypeDef(
    _RequiredRestoreSnapshotTierRequestRequestTypeDef,
    _OptionalRestoreSnapshotTierRequestRequestTypeDef,
):
    pass


_RequiredRevokeClientVpnIngressRequestRequestTypeDef = TypedDict(
    "_RequiredRevokeClientVpnIngressRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
        "TargetNetworkCidr": str,
    },
)
_OptionalRevokeClientVpnIngressRequestRequestTypeDef = TypedDict(
    "_OptionalRevokeClientVpnIngressRequestRequestTypeDef",
    {
        "AccessGroupId": str,
        "RevokeAllGroups": bool,
        "DryRun": bool,
    },
    total=False,
)


class RevokeClientVpnIngressRequestRequestTypeDef(
    _RequiredRevokeClientVpnIngressRequestRequestTypeDef,
    _OptionalRevokeClientVpnIngressRequestRequestTypeDef,
):
    pass


RouteTypeDef = TypedDict(
    "RouteTypeDef",
    {
        "DestinationCidrBlock": str,
        "DestinationIpv6CidrBlock": str,
        "DestinationPrefixListId": str,
        "EgressOnlyInternetGatewayId": str,
        "GatewayId": str,
        "InstanceId": str,
        "InstanceOwnerId": str,
        "NatGatewayId": str,
        "TransitGatewayId": str,
        "LocalGatewayId": str,
        "CarrierGatewayId": str,
        "NetworkInterfaceId": str,
        "Origin": RouteOriginType,
        "State": RouteStateType,
        "VpcPeeringConnectionId": str,
        "CoreNetworkArn": str,
    },
    total=False,
)

S3StorageTypeDef = TypedDict(
    "S3StorageTypeDef",
    {
        "AWSAccessKeyId": str,
        "Bucket": str,
        "Prefix": str,
        "UploadPolicy": Union[str, bytes, IO[Any], StreamingBody],
        "UploadPolicySignature": str,
    },
    total=False,
)

ScheduledInstanceRecurrenceTypeDef = TypedDict(
    "ScheduledInstanceRecurrenceTypeDef",
    {
        "Frequency": str,
        "Interval": int,
        "OccurrenceDaySet": List[int],
        "OccurrenceRelativeToEnd": bool,
        "OccurrenceUnit": str,
    },
    total=False,
)

ScheduledInstancesEbsTypeDef = TypedDict(
    "ScheduledInstancesEbsTypeDef",
    {
        "DeleteOnTermination": bool,
        "Encrypted": bool,
        "Iops": int,
        "SnapshotId": str,
        "VolumeSize": int,
        "VolumeType": str,
    },
    total=False,
)

ScheduledInstancesIamInstanceProfileTypeDef = TypedDict(
    "ScheduledInstancesIamInstanceProfileTypeDef",
    {
        "Arn": str,
        "Name": str,
    },
    total=False,
)

ScheduledInstancesIpv6AddressTypeDef = TypedDict(
    "ScheduledInstancesIpv6AddressTypeDef",
    {
        "Ipv6Address": str,
    },
    total=False,
)

ScheduledInstancesMonitoringTypeDef = TypedDict(
    "ScheduledInstancesMonitoringTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

ScheduledInstancesPlacementTypeDef = TypedDict(
    "ScheduledInstancesPlacementTypeDef",
    {
        "AvailabilityZone": str,
        "GroupName": str,
    },
    total=False,
)

ScheduledInstancesPrivateIpAddressConfigTypeDef = TypedDict(
    "ScheduledInstancesPrivateIpAddressConfigTypeDef",
    {
        "Primary": bool,
        "PrivateIpAddress": str,
    },
    total=False,
)

TransitGatewayMulticastGroupTypeDef = TypedDict(
    "TransitGatewayMulticastGroupTypeDef",
    {
        "GroupIpAddress": str,
        "TransitGatewayAttachmentId": str,
        "SubnetId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "ResourceOwnerId": str,
        "NetworkInterfaceId": str,
        "GroupMember": bool,
        "GroupSource": bool,
        "MemberType": MembershipTypeType,
        "SourceType": MembershipTypeType,
    },
    total=False,
)

SecurityGroupIdentifierTypeDef = TypedDict(
    "SecurityGroupIdentifierTypeDef",
    {
        "GroupId": str,
        "GroupName": str,
    },
    total=False,
)

SecurityGroupRuleDescriptionTypeDef = TypedDict(
    "SecurityGroupRuleDescriptionTypeDef",
    {
        "SecurityGroupRuleId": str,
        "Description": str,
    },
    total=False,
)

SecurityGroupRuleRequestTypeDef = TypedDict(
    "SecurityGroupRuleRequestTypeDef",
    {
        "IpProtocol": str,
        "FromPort": int,
        "ToPort": int,
        "CidrIpv4": str,
        "CidrIpv6": str,
        "PrefixListId": str,
        "ReferencedGroupId": str,
        "Description": str,
    },
    total=False,
)

_RequiredSendDiagnosticInterruptRequestRequestTypeDef = TypedDict(
    "_RequiredSendDiagnosticInterruptRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalSendDiagnosticInterruptRequestRequestTypeDef = TypedDict(
    "_OptionalSendDiagnosticInterruptRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class SendDiagnosticInterruptRequestRequestTypeDef(
    _RequiredSendDiagnosticInterruptRequestRequestTypeDef,
    _OptionalSendDiagnosticInterruptRequestRequestTypeDef,
):
    pass


ServiceTypeDetailTypeDef = TypedDict(
    "ServiceTypeDetailTypeDef",
    {
        "ServiceType": ServiceTypeType,
    },
    total=False,
)

ServiceResourceClassicAddressRequestTypeDef = TypedDict(
    "ServiceResourceClassicAddressRequestTypeDef",
    {
        "public_ip": str,
    },
)

ServiceResourceDhcpOptionsRequestTypeDef = TypedDict(
    "ServiceResourceDhcpOptionsRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceImageRequestTypeDef = TypedDict(
    "ServiceResourceImageRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceInstanceRequestTypeDef = TypedDict(
    "ServiceResourceInstanceRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceInternetGatewayRequestTypeDef = TypedDict(
    "ServiceResourceInternetGatewayRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceKeyPairRequestTypeDef = TypedDict(
    "ServiceResourceKeyPairRequestTypeDef",
    {
        "name": str,
    },
)

ServiceResourceNetworkAclRequestTypeDef = TypedDict(
    "ServiceResourceNetworkAclRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceNetworkInterfaceAssociationRequestTypeDef = TypedDict(
    "ServiceResourceNetworkInterfaceAssociationRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceNetworkInterfaceRequestTypeDef = TypedDict(
    "ServiceResourceNetworkInterfaceRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourcePlacementGroupRequestTypeDef = TypedDict(
    "ServiceResourcePlacementGroupRequestTypeDef",
    {
        "name": str,
    },
)

ServiceResourceRouteRequestTypeDef = TypedDict(
    "ServiceResourceRouteRequestTypeDef",
    {
        "route_table_id": str,
        "destination_cidr_block": str,
    },
)

ServiceResourceRouteTableAssociationRequestTypeDef = TypedDict(
    "ServiceResourceRouteTableAssociationRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceRouteTableRequestTypeDef = TypedDict(
    "ServiceResourceRouteTableRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceSecurityGroupRequestTypeDef = TypedDict(
    "ServiceResourceSecurityGroupRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceSnapshotRequestTypeDef = TypedDict(
    "ServiceResourceSnapshotRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceSubnetRequestTypeDef = TypedDict(
    "ServiceResourceSubnetRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceTagRequestTypeDef = TypedDict(
    "ServiceResourceTagRequestTypeDef",
    {
        "resource_id": str,
        "key": str,
        "value": str,
    },
)

ServiceResourceVolumeRequestTypeDef = TypedDict(
    "ServiceResourceVolumeRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceVpcAddressRequestTypeDef = TypedDict(
    "ServiceResourceVpcAddressRequestTypeDef",
    {
        "allocation_id": str,
    },
)

ServiceResourceVpcPeeringConnectionRequestTypeDef = TypedDict(
    "ServiceResourceVpcPeeringConnectionRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceVpcRequestTypeDef = TypedDict(
    "ServiceResourceVpcRequestTypeDef",
    {
        "id": str,
    },
)

UserBucketDetailsTypeDef = TypedDict(
    "UserBucketDetailsTypeDef",
    {
        "S3Bucket": str,
        "S3Key": str,
    },
    total=False,
)

SpotCapacityRebalanceTypeDef = TypedDict(
    "SpotCapacityRebalanceTypeDef",
    {
        "ReplacementStrategy": ReplacementStrategyType,
        "TerminationDelay": int,
    },
    total=False,
)

SpotInstanceStateFaultTypeDef = TypedDict(
    "SpotInstanceStateFaultTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

SpotFleetMonitoringTypeDef = TypedDict(
    "SpotFleetMonitoringTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

SpotInstanceStatusTypeDef = TypedDict(
    "SpotInstanceStatusTypeDef",
    {
        "Code": str,
        "Message": str,
        "UpdateTime": datetime,
    },
    total=False,
)

StartInstancesRequestInstanceStartTypeDef = TypedDict(
    "StartInstancesRequestInstanceStartTypeDef",
    {
        "AdditionalInfo": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredStartInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredStartInstancesRequestRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
    },
)
_OptionalStartInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalStartInstancesRequestRequestTypeDef",
    {
        "AdditionalInfo": str,
        "DryRun": bool,
    },
    total=False,
)


class StartInstancesRequestRequestTypeDef(
    _RequiredStartInstancesRequestRequestTypeDef, _OptionalStartInstancesRequestRequestTypeDef
):
    pass


_RequiredStartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef = TypedDict(
    "_RequiredStartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef",
    {
        "ServiceId": str,
    },
)
_OptionalStartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef = TypedDict(
    "_OptionalStartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class StartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef(
    _RequiredStartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef,
    _OptionalStartVpcEndpointServicePrivateDnsVerificationRequestRequestTypeDef,
):
    pass


StopInstancesRequestInstanceStopTypeDef = TypedDict(
    "StopInstancesRequestInstanceStopTypeDef",
    {
        "Hibernate": bool,
        "DryRun": bool,
        "Force": bool,
    },
    total=False,
)

_RequiredStopInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredStopInstancesRequestRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
    },
)
_OptionalStopInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalStopInstancesRequestRequestTypeDef",
    {
        "Hibernate": bool,
        "DryRun": bool,
        "Force": bool,
    },
    total=False,
)


class StopInstancesRequestRequestTypeDef(
    _RequiredStopInstancesRequestRequestTypeDef, _OptionalStopInstancesRequestRequestTypeDef
):
    pass


SubnetAssociationTypeDef = TypedDict(
    "SubnetAssociationTypeDef",
    {
        "SubnetId": str,
        "State": TransitGatewayMulitcastDomainAssociationStateType,
    },
    total=False,
)

SubnetCidrBlockStateTypeDef = TypedDict(
    "SubnetCidrBlockStateTypeDef",
    {
        "State": SubnetCidrBlockStateCodeType,
        "StatusMessage": str,
    },
    total=False,
)

TargetConfigurationTypeDef = TypedDict(
    "TargetConfigurationTypeDef",
    {
        "InstanceCount": int,
        "OfferingId": str,
    },
    total=False,
)

TargetGroupTypeDef = TypedDict(
    "TargetGroupTypeDef",
    {
        "Arn": str,
    },
    total=False,
)

_RequiredTerminateClientVpnConnectionsRequestRequestTypeDef = TypedDict(
    "_RequiredTerminateClientVpnConnectionsRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalTerminateClientVpnConnectionsRequestRequestTypeDef = TypedDict(
    "_OptionalTerminateClientVpnConnectionsRequestRequestTypeDef",
    {
        "ConnectionId": str,
        "Username": str,
        "DryRun": bool,
    },
    total=False,
)


class TerminateClientVpnConnectionsRequestRequestTypeDef(
    _RequiredTerminateClientVpnConnectionsRequestRequestTypeDef,
    _OptionalTerminateClientVpnConnectionsRequestRequestTypeDef,
):
    pass


TerminateInstancesRequestInstanceTerminateTypeDef = TypedDict(
    "TerminateInstancesRequestInstanceTerminateTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredTerminateInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredTerminateInstancesRequestRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
    },
)
_OptionalTerminateInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalTerminateInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class TerminateInstancesRequestRequestTypeDef(
    _RequiredTerminateInstancesRequestRequestTypeDef,
    _OptionalTerminateInstancesRequestRequestTypeDef,
):
    pass


TrafficMirrorPortRangeTypeDef = TypedDict(
    "TrafficMirrorPortRangeTypeDef",
    {
        "FromPort": int,
        "ToPort": int,
    },
    total=False,
)

TransitGatewayAttachmentAssociationTypeDef = TypedDict(
    "TransitGatewayAttachmentAssociationTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "State": TransitGatewayAssociationStateType,
    },
    total=False,
)

TransitGatewayAttachmentBgpConfigurationTypeDef = TypedDict(
    "TransitGatewayAttachmentBgpConfigurationTypeDef",
    {
        "TransitGatewayAsn": int,
        "PeerAsn": int,
        "TransitGatewayAddress": str,
        "PeerAddress": str,
        "BgpStatus": BgpStatusType,
    },
    total=False,
)

TransitGatewayConnectOptionsTypeDef = TypedDict(
    "TransitGatewayConnectOptionsTypeDef",
    {
        "Protocol": Literal["gre"],
    },
    total=False,
)

TransitGatewayMulticastDomainOptionsTypeDef = TypedDict(
    "TransitGatewayMulticastDomainOptionsTypeDef",
    {
        "Igmpv2Support": Igmpv2SupportValueType,
        "StaticSourcesSupport": StaticSourcesSupportValueType,
        "AutoAcceptSharedAssociations": AutoAcceptSharedAssociationsValueType,
    },
    total=False,
)

TransitGatewayOptionsTypeDef = TypedDict(
    "TransitGatewayOptionsTypeDef",
    {
        "AmazonSideAsn": int,
        "TransitGatewayCidrBlocks": List[str],
        "AutoAcceptSharedAttachments": AutoAcceptSharedAttachmentsValueType,
        "DefaultRouteTableAssociation": DefaultRouteTableAssociationValueType,
        "AssociationDefaultRouteTableId": str,
        "DefaultRouteTablePropagation": DefaultRouteTablePropagationValueType,
        "PropagationDefaultRouteTableId": str,
        "VpnEcmpSupport": VpnEcmpSupportValueType,
        "DnsSupport": DnsSupportValueType,
        "MulticastSupport": MulticastSupportValueType,
    },
    total=False,
)

TransitGatewayPrefixListAttachmentTypeDef = TypedDict(
    "TransitGatewayPrefixListAttachmentTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "ResourceId": str,
    },
    total=False,
)

TransitGatewayRouteAttachmentTypeDef = TypedDict(
    "TransitGatewayRouteAttachmentTypeDef",
    {
        "ResourceId": str,
        "TransitGatewayAttachmentId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
    },
    total=False,
)

TransitGatewayVpcAttachmentOptionsTypeDef = TypedDict(
    "TransitGatewayVpcAttachmentOptionsTypeDef",
    {
        "DnsSupport": DnsSupportValueType,
        "Ipv6Support": Ipv6SupportValueType,
        "ApplianceModeSupport": ApplianceModeSupportValueType,
    },
    total=False,
)

_RequiredUnassignIpv6AddressesRequestRequestTypeDef = TypedDict(
    "_RequiredUnassignIpv6AddressesRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalUnassignIpv6AddressesRequestRequestTypeDef = TypedDict(
    "_OptionalUnassignIpv6AddressesRequestRequestTypeDef",
    {
        "Ipv6Addresses": Sequence[str],
        "Ipv6Prefixes": Sequence[str],
    },
    total=False,
)


class UnassignIpv6AddressesRequestRequestTypeDef(
    _RequiredUnassignIpv6AddressesRequestRequestTypeDef,
    _OptionalUnassignIpv6AddressesRequestRequestTypeDef,
):
    pass


UnassignPrivateIpAddressesRequestNetworkInterfaceUnassignPrivateIpAddressesTypeDef = TypedDict(
    "UnassignPrivateIpAddressesRequestNetworkInterfaceUnassignPrivateIpAddressesTypeDef",
    {
        "PrivateIpAddresses": Sequence[str],
        "Ipv4Prefixes": Sequence[str],
    },
    total=False,
)

_RequiredUnassignPrivateIpAddressesRequestRequestTypeDef = TypedDict(
    "_RequiredUnassignPrivateIpAddressesRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalUnassignPrivateIpAddressesRequestRequestTypeDef = TypedDict(
    "_OptionalUnassignPrivateIpAddressesRequestRequestTypeDef",
    {
        "PrivateIpAddresses": Sequence[str],
        "Ipv4Prefixes": Sequence[str],
    },
    total=False,
)


class UnassignPrivateIpAddressesRequestRequestTypeDef(
    _RequiredUnassignPrivateIpAddressesRequestRequestTypeDef,
    _OptionalUnassignPrivateIpAddressesRequestRequestTypeDef,
):
    pass


UnmonitorInstancesRequestInstanceUnmonitorTypeDef = TypedDict(
    "UnmonitorInstancesRequestInstanceUnmonitorTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)

_RequiredUnmonitorInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredUnmonitorInstancesRequestRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
    },
)
_OptionalUnmonitorInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalUnmonitorInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class UnmonitorInstancesRequestRequestTypeDef(
    _RequiredUnmonitorInstancesRequestRequestTypeDef,
    _OptionalUnmonitorInstancesRequestRequestTypeDef,
):
    pass


UnsuccessfulInstanceCreditSpecificationItemErrorTypeDef = TypedDict(
    "UnsuccessfulInstanceCreditSpecificationItemErrorTypeDef",
    {
        "Code": UnsuccessfulInstanceCreditSpecificationErrorCodeType,
        "Message": str,
    },
    total=False,
)

UnsuccessfulItemErrorTypeDef = TypedDict(
    "UnsuccessfulItemErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

ValidationErrorTypeDef = TypedDict(
    "ValidationErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

VgwTelemetryTypeDef = TypedDict(
    "VgwTelemetryTypeDef",
    {
        "AcceptedRouteCount": int,
        "LastStatusChange": datetime,
        "OutsideIpAddress": str,
        "Status": TelemetryStatusType,
        "StatusMessage": str,
        "CertificateArn": str,
    },
    total=False,
)

VolumeAttachmentTypeDef = TypedDict(
    "VolumeAttachmentTypeDef",
    {
        "AttachTime": datetime,
        "Device": str,
        "InstanceId": str,
        "State": VolumeAttachmentStateType,
        "VolumeId": str,
        "DeleteOnTermination": bool,
    },
    total=False,
)

VolumeStatusActionTypeDef = TypedDict(
    "VolumeStatusActionTypeDef",
    {
        "Code": str,
        "Description": str,
        "EventId": str,
        "EventType": str,
    },
    total=False,
)

VolumeStatusAttachmentStatusTypeDef = TypedDict(
    "VolumeStatusAttachmentStatusTypeDef",
    {
        "IoPerformance": str,
        "InstanceId": str,
    },
    total=False,
)

VolumeStatusDetailsTypeDef = TypedDict(
    "VolumeStatusDetailsTypeDef",
    {
        "Name": VolumeStatusNameType,
        "Status": str,
    },
    total=False,
)

VolumeStatusEventTypeDef = TypedDict(
    "VolumeStatusEventTypeDef",
    {
        "Description": str,
        "EventId": str,
        "EventType": str,
        "NotAfter": datetime,
        "NotBefore": datetime,
        "InstanceId": str,
    },
    total=False,
)

VpcCidrBlockStateTypeDef = TypedDict(
    "VpcCidrBlockStateTypeDef",
    {
        "State": VpcCidrBlockStateCodeType,
        "StatusMessage": str,
    },
    total=False,
)

VpcPeeringConnectionOptionsDescriptionTypeDef = TypedDict(
    "VpcPeeringConnectionOptionsDescriptionTypeDef",
    {
        "AllowDnsResolutionFromRemoteVpc": bool,
        "AllowEgressFromLocalClassicLinkToRemoteVpc": bool,
        "AllowEgressFromLocalVpcToRemoteClassicLink": bool,
    },
    total=False,
)

VpcPeeringConnectionStateReasonTypeDef = TypedDict(
    "VpcPeeringConnectionStateReasonTypeDef",
    {
        "Code": VpcPeeringConnectionStateReasonCodeType,
        "Message": str,
    },
    total=False,
)

VpnStaticRouteTypeDef = TypedDict(
    "VpnStaticRouteTypeDef",
    {
        "DestinationCidrBlock": str,
        "Source": Literal["Static"],
        "State": VpnStateType,
    },
    total=False,
)

_RequiredWithdrawByoipCidrRequestRequestTypeDef = TypedDict(
    "_RequiredWithdrawByoipCidrRequestRequestTypeDef",
    {
        "Cidr": str,
    },
)
_OptionalWithdrawByoipCidrRequestRequestTypeDef = TypedDict(
    "_OptionalWithdrawByoipCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class WithdrawByoipCidrRequestRequestTypeDef(
    _RequiredWithdrawByoipCidrRequestRequestTypeDef, _OptionalWithdrawByoipCidrRequestRequestTypeDef
):
    pass


_RequiredAcceptReservedInstancesExchangeQuoteRequestRequestTypeDef = TypedDict(
    "_RequiredAcceptReservedInstancesExchangeQuoteRequestRequestTypeDef",
    {
        "ReservedInstanceIds": Sequence[str],
    },
)
_OptionalAcceptReservedInstancesExchangeQuoteRequestRequestTypeDef = TypedDict(
    "_OptionalAcceptReservedInstancesExchangeQuoteRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TargetConfigurations": Sequence[TargetConfigurationRequestTypeDef],
    },
    total=False,
)


class AcceptReservedInstancesExchangeQuoteRequestRequestTypeDef(
    _RequiredAcceptReservedInstancesExchangeQuoteRequestRequestTypeDef,
    _OptionalAcceptReservedInstancesExchangeQuoteRequestRequestTypeDef,
):
    pass


_RequiredGetReservedInstancesExchangeQuoteRequestRequestTypeDef = TypedDict(
    "_RequiredGetReservedInstancesExchangeQuoteRequestRequestTypeDef",
    {
        "ReservedInstanceIds": Sequence[str],
    },
)
_OptionalGetReservedInstancesExchangeQuoteRequestRequestTypeDef = TypedDict(
    "_OptionalGetReservedInstancesExchangeQuoteRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TargetConfigurations": Sequence[TargetConfigurationRequestTypeDef],
    },
    total=False,
)


class GetReservedInstancesExchangeQuoteRequestRequestTypeDef(
    _RequiredGetReservedInstancesExchangeQuoteRequestRequestTypeDef,
    _OptionalGetReservedInstancesExchangeQuoteRequestRequestTypeDef,
):
    pass


AcceptReservedInstancesExchangeQuoteResultTypeDef = TypedDict(
    "AcceptReservedInstancesExchangeQuoteResultTypeDef",
    {
        "ExchangeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AllocateAddressResultTypeDef = TypedDict(
    "AllocateAddressResultTypeDef",
    {
        "PublicIp": str,
        "AllocationId": str,
        "PublicIpv4Pool": str,
        "NetworkBorderGroup": str,
        "Domain": DomainTypeType,
        "CustomerOwnedIp": str,
        "CustomerOwnedIpv4Pool": str,
        "CarrierIp": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AllocateHostsResultTypeDef = TypedDict(
    "AllocateHostsResultTypeDef",
    {
        "HostIds": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ApplySecurityGroupsToClientVpnTargetNetworkResultTypeDef = TypedDict(
    "ApplySecurityGroupsToClientVpnTargetNetworkResultTypeDef",
    {
        "SecurityGroupIds": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssignIpv6AddressesResultTypeDef = TypedDict(
    "AssignIpv6AddressesResultTypeDef",
    {
        "AssignedIpv6Addresses": List[str],
        "AssignedIpv6Prefixes": List[str],
        "NetworkInterfaceId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateAddressResultTypeDef = TypedDict(
    "AssociateAddressResultTypeDef",
    {
        "AssociationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateEnclaveCertificateIamRoleResultTypeDef = TypedDict(
    "AssociateEnclaveCertificateIamRoleResultTypeDef",
    {
        "CertificateS3BucketName": str,
        "CertificateS3ObjectKey": str,
        "EncryptionKmsKeyId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachClassicLinkVpcResultTypeDef = TypedDict(
    "AttachClassicLinkVpcResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachNetworkInterfaceResultTypeDef = TypedDict(
    "AttachNetworkInterfaceResultTypeDef",
    {
        "AttachmentId": str,
        "NetworkCardIndex": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CancelCapacityReservationResultTypeDef = TypedDict(
    "CancelCapacityReservationResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CancelImportTaskResultTypeDef = TypedDict(
    "CancelImportTaskResultTypeDef",
    {
        "ImportTaskId": str,
        "PreviousState": str,
        "State": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ConfirmProductInstanceResultTypeDef = TypedDict(
    "ConfirmProductInstanceResultTypeDef",
    {
        "OwnerId": str,
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CopyFpgaImageResultTypeDef = TypedDict(
    "CopyFpgaImageResultTypeDef",
    {
        "FpgaImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CopyImageResultTypeDef = TypedDict(
    "CopyImageResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CpuOptionsResponseMetadataTypeDef = TypedDict(
    "CpuOptionsResponseMetadataTypeDef",
    {
        "CoreCount": int,
        "ThreadsPerCore": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFpgaImageResultTypeDef = TypedDict(
    "CreateFpgaImageResultTypeDef",
    {
        "FpgaImageId": str,
        "FpgaImageGlobalId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateImageResultTypeDef = TypedDict(
    "CreateImageResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePublicIpv4PoolResultTypeDef = TypedDict(
    "CreatePublicIpv4PoolResultTypeDef",
    {
        "PoolId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRestoreImageTaskResultTypeDef = TypedDict(
    "CreateRestoreImageTaskResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRouteResultTypeDef = TypedDict(
    "CreateRouteResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStoreImageTaskResultTypeDef = TypedDict(
    "CreateStoreImageTaskResultTypeDef",
    {
        "ObjectKey": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteEgressOnlyInternetGatewayResultTypeDef = TypedDict(
    "DeleteEgressOnlyInternetGatewayResultTypeDef",
    {
        "ReturnCode": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteFpgaImageResultTypeDef = TypedDict(
    "DeleteFpgaImageResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNatGatewayResultTypeDef = TypedDict(
    "DeleteNatGatewayResultTypeDef",
    {
        "NatGatewayId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNetworkInsightsAccessScopeAnalysisResultTypeDef = TypedDict(
    "DeleteNetworkInsightsAccessScopeAnalysisResultTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNetworkInsightsAccessScopeResultTypeDef = TypedDict(
    "DeleteNetworkInsightsAccessScopeResultTypeDef",
    {
        "NetworkInsightsAccessScopeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNetworkInsightsAnalysisResultTypeDef = TypedDict(
    "DeleteNetworkInsightsAnalysisResultTypeDef",
    {
        "NetworkInsightsAnalysisId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNetworkInsightsPathResultTypeDef = TypedDict(
    "DeleteNetworkInsightsPathResultTypeDef",
    {
        "NetworkInsightsPathId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNetworkInterfacePermissionResultTypeDef = TypedDict(
    "DeleteNetworkInterfacePermissionResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeletePublicIpv4PoolResultTypeDef = TypedDict(
    "DeletePublicIpv4PoolResultTypeDef",
    {
        "ReturnValue": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTrafficMirrorFilterResultTypeDef = TypedDict(
    "DeleteTrafficMirrorFilterResultTypeDef",
    {
        "TrafficMirrorFilterId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTrafficMirrorFilterRuleResultTypeDef = TypedDict(
    "DeleteTrafficMirrorFilterRuleResultTypeDef",
    {
        "TrafficMirrorFilterRuleId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTrafficMirrorSessionResultTypeDef = TypedDict(
    "DeleteTrafficMirrorSessionResultTypeDef",
    {
        "TrafficMirrorSessionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTrafficMirrorTargetResultTypeDef = TypedDict(
    "DeleteTrafficMirrorTargetResultTypeDef",
    {
        "TrafficMirrorTargetId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteVpcPeeringConnectionResultTypeDef = TypedDict(
    "DeleteVpcPeeringConnectionResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeprovisionPublicIpv4PoolCidrResultTypeDef = TypedDict(
    "DeprovisionPublicIpv4PoolCidrResultTypeDef",
    {
        "PoolId": str,
        "DeprovisionedAddresses": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetachClassicLinkVpcResultTypeDef = TypedDict(
    "DetachClassicLinkVpcResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableEbsEncryptionByDefaultResultTypeDef = TypedDict(
    "DisableEbsEncryptionByDefaultResultTypeDef",
    {
        "EbsEncryptionByDefault": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableImageDeprecationResultTypeDef = TypedDict(
    "DisableImageDeprecationResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableIpamOrganizationAdminAccountResultTypeDef = TypedDict(
    "DisableIpamOrganizationAdminAccountResultTypeDef",
    {
        "Success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableSerialConsoleAccessResultTypeDef = TypedDict(
    "DisableSerialConsoleAccessResultTypeDef",
    {
        "SerialConsoleAccessEnabled": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableVpcClassicLinkDnsSupportResultTypeDef = TypedDict(
    "DisableVpcClassicLinkDnsSupportResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableVpcClassicLinkResultTypeDef = TypedDict(
    "DisableVpcClassicLinkResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateEnclaveCertificateIamRoleResultTypeDef = TypedDict(
    "DisassociateEnclaveCertificateIamRoleResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateTrunkInterfaceResultTypeDef = TypedDict(
    "DisassociateTrunkInterfaceResultTypeDef",
    {
        "Return": bool,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableEbsEncryptionByDefaultResultTypeDef = TypedDict(
    "EnableEbsEncryptionByDefaultResultTypeDef",
    {
        "EbsEncryptionByDefault": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableImageDeprecationResultTypeDef = TypedDict(
    "EnableImageDeprecationResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableIpamOrganizationAdminAccountResultTypeDef = TypedDict(
    "EnableIpamOrganizationAdminAccountResultTypeDef",
    {
        "Success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableSerialConsoleAccessResultTypeDef = TypedDict(
    "EnableSerialConsoleAccessResultTypeDef",
    {
        "SerialConsoleAccessEnabled": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableVpcClassicLinkDnsSupportResultTypeDef = TypedDict(
    "EnableVpcClassicLinkDnsSupportResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableVpcClassicLinkResultTypeDef = TypedDict(
    "EnableVpcClassicLinkResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnclaveOptionsResponseMetadataTypeDef = TypedDict(
    "EnclaveOptionsResponseMetadataTypeDef",
    {
        "Enabled": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportClientVpnClientConfigurationResultTypeDef = TypedDict(
    "ExportClientVpnClientConfigurationResultTypeDef",
    {
        "ClientConfiguration": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportTransitGatewayRoutesResultTypeDef = TypedDict(
    "ExportTransitGatewayRoutesResultTypeDef",
    {
        "S3Location": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetConsoleOutputResultTypeDef = TypedDict(
    "GetConsoleOutputResultTypeDef",
    {
        "InstanceId": str,
        "Output": str,
        "Timestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetConsoleScreenshotResultTypeDef = TypedDict(
    "GetConsoleScreenshotResultTypeDef",
    {
        "ImageData": str,
        "InstanceId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetEbsDefaultKmsKeyIdResultTypeDef = TypedDict(
    "GetEbsDefaultKmsKeyIdResultTypeDef",
    {
        "KmsKeyId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetEbsEncryptionByDefaultResultTypeDef = TypedDict(
    "GetEbsEncryptionByDefaultResultTypeDef",
    {
        "EbsEncryptionByDefault": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetFlowLogsIntegrationTemplateResultTypeDef = TypedDict(
    "GetFlowLogsIntegrationTemplateResultTypeDef",
    {
        "Result": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstanceUefiDataResultTypeDef = TypedDict(
    "GetInstanceUefiDataResultTypeDef",
    {
        "InstanceId": str,
        "UefiData": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetPasswordDataResultTypeDef = TypedDict(
    "GetPasswordDataResultTypeDef",
    {
        "InstanceId": str,
        "PasswordData": str,
        "Timestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSerialConsoleAccessStatusResultTypeDef = TypedDict(
    "GetSerialConsoleAccessStatusResultTypeDef",
    {
        "SerialConsoleAccessEnabled": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetVpnConnectionDeviceSampleConfigurationResultTypeDef = TypedDict(
    "GetVpnConnectionDeviceSampleConfigurationResultTypeDef",
    {
        "VpnConnectionDeviceSampleConfiguration": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HibernationOptionsResponseMetadataTypeDef = TypedDict(
    "HibernationOptionsResponseMetadataTypeDef",
    {
        "Configured": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IamInstanceProfileResponseMetadataTypeDef = TypedDict(
    "IamInstanceProfileResponseMetadataTypeDef",
    {
        "Arn": str,
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportClientVpnClientCertificateRevocationListResultTypeDef = TypedDict(
    "ImportClientVpnClientCertificateRevocationListResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceMaintenanceOptionsResponseMetadataTypeDef = TypedDict(
    "InstanceMaintenanceOptionsResponseMetadataTypeDef",
    {
        "AutoRecovery": InstanceAutoRecoveryStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceMetadataOptionsResponseResponseMetadataTypeDef = TypedDict(
    "InstanceMetadataOptionsResponseResponseMetadataTypeDef",
    {
        "State": InstanceMetadataOptionsStateType,
        "HttpTokens": HttpTokensStateType,
        "HttpPutResponseHopLimit": int,
        "HttpEndpoint": InstanceMetadataEndpointStateType,
        "HttpProtocolIpv6": InstanceMetadataProtocolStateType,
        "InstanceMetadataTags": InstanceMetadataTagsStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceStateResponseMetadataTypeDef = TypedDict(
    "InstanceStateResponseMetadataTypeDef",
    {
        "Code": int,
        "Name": InstanceStateNameType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyAvailabilityZoneGroupResultTypeDef = TypedDict(
    "ModifyAvailabilityZoneGroupResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyCapacityReservationFleetResultTypeDef = TypedDict(
    "ModifyCapacityReservationFleetResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyCapacityReservationResultTypeDef = TypedDict(
    "ModifyCapacityReservationResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyClientVpnEndpointResultTypeDef = TypedDict(
    "ModifyClientVpnEndpointResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyEbsDefaultKmsKeyIdResultTypeDef = TypedDict(
    "ModifyEbsDefaultKmsKeyIdResultTypeDef",
    {
        "KmsKeyId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyFleetResultTypeDef = TypedDict(
    "ModifyFleetResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyInstanceCapacityReservationAttributesResultTypeDef = TypedDict(
    "ModifyInstanceCapacityReservationAttributesResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyInstanceMaintenanceOptionsResultTypeDef = TypedDict(
    "ModifyInstanceMaintenanceOptionsResultTypeDef",
    {
        "InstanceId": str,
        "AutoRecovery": InstanceAutoRecoveryStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyInstancePlacementResultTypeDef = TypedDict(
    "ModifyInstancePlacementResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyPrivateDnsNameOptionsResultTypeDef = TypedDict(
    "ModifyPrivateDnsNameOptionsResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyReservedInstancesResultTypeDef = TypedDict(
    "ModifyReservedInstancesResultTypeDef",
    {
        "ReservedInstancesModificationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifySecurityGroupRulesResultTypeDef = TypedDict(
    "ModifySecurityGroupRulesResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifySnapshotTierResultTypeDef = TypedDict(
    "ModifySnapshotTierResultTypeDef",
    {
        "SnapshotId": str,
        "TieringStartTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifySpotFleetRequestResponseTypeDef = TypedDict(
    "ModifySpotFleetRequestResponseTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpcEndpointConnectionNotificationResultTypeDef = TypedDict(
    "ModifyVpcEndpointConnectionNotificationResultTypeDef",
    {
        "ReturnValue": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpcEndpointResultTypeDef = TypedDict(
    "ModifyVpcEndpointResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpcEndpointServiceConfigurationResultTypeDef = TypedDict(
    "ModifyVpcEndpointServiceConfigurationResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpcEndpointServicePayerResponsibilityResultTypeDef = TypedDict(
    "ModifyVpcEndpointServicePayerResponsibilityResultTypeDef",
    {
        "ReturnValue": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpcEndpointServicePermissionsResultTypeDef = TypedDict(
    "ModifyVpcEndpointServicePermissionsResultTypeDef",
    {
        "ReturnValue": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpcTenancyResultTypeDef = TypedDict(
    "ModifyVpcTenancyResultTypeDef",
    {
        "ReturnValue": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MonitoringResponseMetadataTypeDef = TypedDict(
    "MonitoringResponseMetadataTypeDef",
    {
        "State": MonitoringStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MoveAddressToVpcResultTypeDef = TypedDict(
    "MoveAddressToVpcResultTypeDef",
    {
        "AllocationId": str,
        "Status": StatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkInterfaceAssociationResponseMetadataTypeDef = TypedDict(
    "NetworkInterfaceAssociationResponseMetadataTypeDef",
    {
        "AllocationId": str,
        "AssociationId": str,
        "IpOwnerId": str,
        "PublicDnsName": str,
        "PublicIp": str,
        "CustomerOwnedIp": str,
        "CarrierIp": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkInterfaceAttachmentResponseMetadataTypeDef = TypedDict(
    "NetworkInterfaceAttachmentResponseMetadataTypeDef",
    {
        "AttachTime": datetime,
        "AttachmentId": str,
        "DeleteOnTermination": bool,
        "DeviceIndex": int,
        "NetworkCardIndex": int,
        "InstanceId": str,
        "InstanceOwnerId": str,
        "Status": AttachmentStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PlacementResponseMetadataTypeDef = TypedDict(
    "PlacementResponseMetadataTypeDef",
    {
        "AvailabilityZone": str,
        "Affinity": str,
        "GroupName": str,
        "PartitionNumber": int,
        "HostId": str,
        "Tenancy": TenancyType,
        "SpreadDomain": str,
        "HostResourceGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PrivateDnsNameOptionsOnLaunchResponseMetadataTypeDef = TypedDict(
    "PrivateDnsNameOptionsOnLaunchResponseMetadataTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PrivateDnsNameOptionsResponseResponseMetadataTypeDef = TypedDict(
    "PrivateDnsNameOptionsResponseResponseMetadataTypeDef",
    {
        "HostnameType": HostnameTypeType,
        "EnableResourceNameDnsARecord": bool,
        "EnableResourceNameDnsAAAARecord": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PurchaseReservedInstancesOfferingResultTypeDef = TypedDict(
    "PurchaseReservedInstancesOfferingResultTypeDef",
    {
        "ReservedInstancesId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterImageResultTypeDef = TypedDict(
    "RegisterImageResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RejectVpcPeeringConnectionResultTypeDef = TypedDict(
    "RejectVpcPeeringConnectionResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReleaseIpamPoolAllocationResultTypeDef = TypedDict(
    "ReleaseIpamPoolAllocationResultTypeDef",
    {
        "Success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplaceNetworkAclAssociationResultTypeDef = TypedDict(
    "ReplaceNetworkAclAssociationResultTypeDef",
    {
        "NewAssociationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RequestSpotFleetResponseTypeDef = TypedDict(
    "RequestSpotFleetResponseTypeDef",
    {
        "SpotFleetRequestId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResetEbsDefaultKmsKeyIdResultTypeDef = TypedDict(
    "ResetEbsDefaultKmsKeyIdResultTypeDef",
    {
        "KmsKeyId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResetFpgaImageAttributeResultTypeDef = TypedDict(
    "ResetFpgaImageAttributeResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreAddressToClassicResultTypeDef = TypedDict(
    "RestoreAddressToClassicResultTypeDef",
    {
        "PublicIp": str,
        "Status": StatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreImageFromRecycleBinResultTypeDef = TypedDict(
    "RestoreImageFromRecycleBinResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreSnapshotFromRecycleBinResultTypeDef = TypedDict(
    "RestoreSnapshotFromRecycleBinResultTypeDef",
    {
        "SnapshotId": str,
        "OutpostArn": str,
        "Description": str,
        "Encrypted": bool,
        "OwnerId": str,
        "Progress": str,
        "StartTime": datetime,
        "State": SnapshotStateType,
        "VolumeId": str,
        "VolumeSize": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreSnapshotTierResultTypeDef = TypedDict(
    "RestoreSnapshotTierResultTypeDef",
    {
        "SnapshotId": str,
        "RestoreStartTime": datetime,
        "RestoreDuration": int,
        "IsPermanentRestore": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RouteTableAssociationStateResponseMetadataTypeDef = TypedDict(
    "RouteTableAssociationStateResponseMetadataTypeDef",
    {
        "State": RouteTableAssociationStateCodeType,
        "StatusMessage": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RunScheduledInstancesResultTypeDef = TypedDict(
    "RunScheduledInstancesResultTypeDef",
    {
        "InstanceIdSet": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartVpcEndpointServicePrivateDnsVerificationResultTypeDef = TypedDict(
    "StartVpcEndpointServicePrivateDnsVerificationResultTypeDef",
    {
        "ReturnValue": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StateReasonResponseMetadataTypeDef = TypedDict(
    "StateReasonResponseMetadataTypeDef",
    {
        "Code": str,
        "Message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UnassignIpv6AddressesResultTypeDef = TypedDict(
    "UnassignIpv6AddressesResultTypeDef",
    {
        "NetworkInterfaceId": str,
        "UnassignedIpv6Addresses": List[str],
        "UnassignedIpv6Prefixes": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateSecurityGroupRuleDescriptionsEgressResultTypeDef = TypedDict(
    "UpdateSecurityGroupRuleDescriptionsEgressResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateSecurityGroupRuleDescriptionsIngressResultTypeDef = TypedDict(
    "UpdateSecurityGroupRuleDescriptionsIngressResultTypeDef",
    {
        "Return": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VolumeAttachmentResponseMetadataTypeDef = TypedDict(
    "VolumeAttachmentResponseMetadataTypeDef",
    {
        "AttachTime": datetime,
        "Device": str,
        "InstanceId": str,
        "State": VolumeAttachmentStateType,
        "VolumeId": str,
        "DeleteOnTermination": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VpcPeeringConnectionStateReasonResponseMetadataTypeDef = TypedDict(
    "VpcPeeringConnectionStateReasonResponseMetadataTypeDef",
    {
        "Code": VpcPeeringConnectionStateReasonCodeType,
        "Message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AccountAttributeTypeDef = TypedDict(
    "AccountAttributeTypeDef",
    {
        "AttributeName": str,
        "AttributeValues": List[AccountAttributeValueTypeDef],
    },
    total=False,
)

DescribeFleetInstancesResultTypeDef = TypedDict(
    "DescribeFleetInstancesResultTypeDef",
    {
        "ActiveInstances": List[ActiveInstanceTypeDef],
        "NextToken": str,
        "FleetId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpotFleetInstancesResponseTypeDef = TypedDict(
    "DescribeSpotFleetInstancesResponseTypeDef",
    {
        "ActiveInstances": List[ActiveInstanceTypeDef],
        "NextToken": str,
        "SpotFleetRequestId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AdditionalDetailTypeDef = TypedDict(
    "AdditionalDetailTypeDef",
    {
        "AdditionalDetailType": str,
        "Component": AnalysisComponentTypeDef,
    },
    total=False,
)

AnalysisLoadBalancerTargetTypeDef = TypedDict(
    "AnalysisLoadBalancerTargetTypeDef",
    {
        "Address": str,
        "AvailabilityZone": str,
        "Instance": AnalysisComponentTypeDef,
        "Port": int,
    },
    total=False,
)

AddressAttributeTypeDef = TypedDict(
    "AddressAttributeTypeDef",
    {
        "PublicIp": str,
        "AllocationId": str,
        "PtrRecord": str,
        "PtrRecordUpdate": PtrUpdateStatusTypeDef,
    },
    total=False,
)

AddressTypeDef = TypedDict(
    "AddressTypeDef",
    {
        "InstanceId": str,
        "PublicIp": str,
        "AllocationId": str,
        "AssociationId": str,
        "Domain": DomainTypeType,
        "NetworkInterfaceId": str,
        "NetworkInterfaceOwnerId": str,
        "PrivateIpAddress": str,
        "Tags": List[TagTypeDef],
        "PublicIpv4Pool": str,
        "NetworkBorderGroup": str,
        "CustomerOwnedIp": str,
        "CustomerOwnedIpv4Pool": str,
        "CarrierIp": str,
    },
    total=False,
)

CapacityReservationTypeDef = TypedDict(
    "CapacityReservationTypeDef",
    {
        "CapacityReservationId": str,
        "OwnerId": str,
        "CapacityReservationArn": str,
        "AvailabilityZoneId": str,
        "InstanceType": str,
        "InstancePlatform": CapacityReservationInstancePlatformType,
        "AvailabilityZone": str,
        "Tenancy": CapacityReservationTenancyType,
        "TotalInstanceCount": int,
        "AvailableInstanceCount": int,
        "EbsOptimized": bool,
        "EphemeralStorage": bool,
        "State": CapacityReservationStateType,
        "StartDate": datetime,
        "EndDate": datetime,
        "EndDateType": EndDateTypeType,
        "InstanceMatchCriteria": InstanceMatchCriteriaType,
        "CreateDate": datetime,
        "Tags": List[TagTypeDef],
        "OutpostArn": str,
        "CapacityReservationFleetId": str,
        "PlacementGroupArn": str,
    },
    total=False,
)

CarrierGatewayTypeDef = TypedDict(
    "CarrierGatewayTypeDef",
    {
        "CarrierGatewayId": str,
        "VpcId": str,
        "State": CarrierGatewayStateType,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

CoipPoolTypeDef = TypedDict(
    "CoipPoolTypeDef",
    {
        "PoolId": str,
        "PoolCidrs": List[str],
        "LocalGatewayRouteTableId": str,
        "Tags": List[TagTypeDef],
        "PoolArn": str,
    },
    total=False,
)

CopySnapshotResultTypeDef = TypedDict(
    "CopySnapshotResultTypeDef",
    {
        "SnapshotId": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSecurityGroupResultTypeDef = TypedDict(
    "CreateSecurityGroupResultTypeDef",
    {
        "GroupId": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateTagsRequestDhcpOptionsCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestDhcpOptionsCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestDhcpOptionsCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestDhcpOptionsCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestDhcpOptionsCreateTagsTypeDef(
    _RequiredCreateTagsRequestDhcpOptionsCreateTagsTypeDef,
    _OptionalCreateTagsRequestDhcpOptionsCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestImageCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestImageCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestImageCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestImageCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestImageCreateTagsTypeDef(
    _RequiredCreateTagsRequestImageCreateTagsTypeDef,
    _OptionalCreateTagsRequestImageCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestInstanceCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestInstanceCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestInstanceCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestInstanceCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestInstanceCreateTagsTypeDef(
    _RequiredCreateTagsRequestInstanceCreateTagsTypeDef,
    _OptionalCreateTagsRequestInstanceCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestInternetGatewayCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestInternetGatewayCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestInternetGatewayCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestInternetGatewayCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestInternetGatewayCreateTagsTypeDef(
    _RequiredCreateTagsRequestInternetGatewayCreateTagsTypeDef,
    _OptionalCreateTagsRequestInternetGatewayCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestNetworkAclCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestNetworkAclCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestNetworkAclCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestNetworkAclCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestNetworkAclCreateTagsTypeDef(
    _RequiredCreateTagsRequestNetworkAclCreateTagsTypeDef,
    _OptionalCreateTagsRequestNetworkAclCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestNetworkInterfaceCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestNetworkInterfaceCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestNetworkInterfaceCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestNetworkInterfaceCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestNetworkInterfaceCreateTagsTypeDef(
    _RequiredCreateTagsRequestNetworkInterfaceCreateTagsTypeDef,
    _OptionalCreateTagsRequestNetworkInterfaceCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTagsRequestRequestTypeDef",
    {
        "Resources": Sequence[Any],
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTagsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestRequestTypeDef(
    _RequiredCreateTagsRequestRequestTypeDef, _OptionalCreateTagsRequestRequestTypeDef
):
    pass


_RequiredCreateTagsRequestRouteTableCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestRouteTableCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestRouteTableCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestRouteTableCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestRouteTableCreateTagsTypeDef(
    _RequiredCreateTagsRequestRouteTableCreateTagsTypeDef,
    _OptionalCreateTagsRequestRouteTableCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestSecurityGroupCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestSecurityGroupCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestSecurityGroupCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestSecurityGroupCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestSecurityGroupCreateTagsTypeDef(
    _RequiredCreateTagsRequestSecurityGroupCreateTagsTypeDef,
    _OptionalCreateTagsRequestSecurityGroupCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestServiceResourceCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestServiceResourceCreateTagsTypeDef",
    {
        "Resources": Sequence[str],
        "Tags": Sequence[TagTypeDef],
    },
)
_OptionalCreateTagsRequestServiceResourceCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestServiceResourceCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestServiceResourceCreateTagsTypeDef(
    _RequiredCreateTagsRequestServiceResourceCreateTagsTypeDef,
    _OptionalCreateTagsRequestServiceResourceCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestSnapshotCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestSnapshotCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestSnapshotCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestSnapshotCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestSnapshotCreateTagsTypeDef(
    _RequiredCreateTagsRequestSnapshotCreateTagsTypeDef,
    _OptionalCreateTagsRequestSnapshotCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestSubnetCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestSubnetCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestSubnetCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestSubnetCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestSubnetCreateTagsTypeDef(
    _RequiredCreateTagsRequestSubnetCreateTagsTypeDef,
    _OptionalCreateTagsRequestSubnetCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestVolumeCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestVolumeCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestVolumeCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestVolumeCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestVolumeCreateTagsTypeDef(
    _RequiredCreateTagsRequestVolumeCreateTagsTypeDef,
    _OptionalCreateTagsRequestVolumeCreateTagsTypeDef,
):
    pass


_RequiredCreateTagsRequestVpcCreateTagsTypeDef = TypedDict(
    "_RequiredCreateTagsRequestVpcCreateTagsTypeDef",
    {
        "Tags": Optional[Sequence[TagTypeDef]],
    },
)
_OptionalCreateTagsRequestVpcCreateTagsTypeDef = TypedDict(
    "_OptionalCreateTagsRequestVpcCreateTagsTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class CreateTagsRequestVpcCreateTagsTypeDef(
    _RequiredCreateTagsRequestVpcCreateTagsTypeDef, _OptionalCreateTagsRequestVpcCreateTagsTypeDef
):
    pass


CustomerGatewayTypeDef = TypedDict(
    "CustomerGatewayTypeDef",
    {
        "BgpAsn": str,
        "CustomerGatewayId": str,
        "IpAddress": str,
        "CertificateArn": str,
        "State": str,
        "Type": str,
        "DeviceName": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredDeleteTagsRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteTagsRequestRequestTypeDef",
    {
        "Resources": Sequence[Any],
    },
)
_OptionalDeleteTagsRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteTagsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Tags": Optional[Sequence[TagTypeDef]],
    },
    total=False,
)


class DeleteTagsRequestRequestTypeDef(
    _RequiredDeleteTagsRequestRequestTypeDef, _OptionalDeleteTagsRequestRequestTypeDef
):
    pass


HostReservationTypeDef = TypedDict(
    "HostReservationTypeDef",
    {
        "Count": int,
        "CurrencyCode": Literal["USD"],
        "Duration": int,
        "End": datetime,
        "HostIdSet": List[str],
        "HostReservationId": str,
        "HourlyPrice": str,
        "InstanceFamily": str,
        "OfferingId": str,
        "PaymentOption": PaymentOptionType,
        "Start": datetime,
        "State": ReservationStateType,
        "UpfrontPrice": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ImportKeyPairResultTypeDef = TypedDict(
    "ImportKeyPairResultTypeDef",
    {
        "KeyFingerprint": str,
        "KeyName": str,
        "KeyPairId": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceDeleteTagsRequestTypeDef = TypedDict(
    "InstanceDeleteTagsRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
        "DryRun": bool,
    },
    total=False,
)

InstanceEventWindowAssociationRequestTypeDef = TypedDict(
    "InstanceEventWindowAssociationRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
        "InstanceTags": Sequence[TagTypeDef],
        "DedicatedHostIds": Sequence[str],
    },
    total=False,
)

InstanceEventWindowAssociationTargetTypeDef = TypedDict(
    "InstanceEventWindowAssociationTargetTypeDef",
    {
        "InstanceIds": List[str],
        "Tags": List[TagTypeDef],
        "DedicatedHostIds": List[str],
    },
    total=False,
)

InstanceEventWindowDisassociationRequestTypeDef = TypedDict(
    "InstanceEventWindowDisassociationRequestTypeDef",
    {
        "InstanceIds": Sequence[str],
        "InstanceTags": Sequence[TagTypeDef],
        "DedicatedHostIds": Sequence[str],
    },
    total=False,
)

IpamScopeTypeDef = TypedDict(
    "IpamScopeTypeDef",
    {
        "OwnerId": str,
        "IpamScopeId": str,
        "IpamScopeArn": str,
        "IpamArn": str,
        "IpamRegion": str,
        "IpamScopeType": IpamScopeTypeType,
        "IsDefault": bool,
        "Description": str,
        "PoolCount": int,
        "State": IpamScopeStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

KeyPairInfoTypeDef = TypedDict(
    "KeyPairInfoTypeDef",
    {
        "KeyPairId": str,
        "KeyFingerprint": str,
        "KeyName": str,
        "KeyType": KeyTypeType,
        "Tags": List[TagTypeDef],
        "PublicKey": str,
        "CreateTime": datetime,
    },
    total=False,
)

KeyPairTypeDef = TypedDict(
    "KeyPairTypeDef",
    {
        "KeyFingerprint": str,
        "KeyMaterial": str,
        "KeyName": str,
        "KeyPairId": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LaunchTemplateTagSpecificationRequestTypeDef = TypedDict(
    "LaunchTemplateTagSpecificationRequestTypeDef",
    {
        "ResourceType": ResourceTypeType,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)

LaunchTemplateTagSpecificationTypeDef = TypedDict(
    "LaunchTemplateTagSpecificationTypeDef",
    {
        "ResourceType": ResourceTypeType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LaunchTemplateTypeDef = TypedDict(
    "LaunchTemplateTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "CreateTime": datetime,
        "CreatedBy": str,
        "DefaultVersionNumber": int,
        "LatestVersionNumber": int,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LocalGatewayRouteTableTypeDef = TypedDict(
    "LocalGatewayRouteTableTypeDef",
    {
        "LocalGatewayRouteTableId": str,
        "LocalGatewayRouteTableArn": str,
        "LocalGatewayId": str,
        "OutpostArn": str,
        "OwnerId": str,
        "State": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LocalGatewayRouteTableVirtualInterfaceGroupAssociationTypeDef = TypedDict(
    "LocalGatewayRouteTableVirtualInterfaceGroupAssociationTypeDef",
    {
        "LocalGatewayRouteTableVirtualInterfaceGroupAssociationId": str,
        "LocalGatewayVirtualInterfaceGroupId": str,
        "LocalGatewayId": str,
        "LocalGatewayRouteTableId": str,
        "LocalGatewayRouteTableArn": str,
        "OwnerId": str,
        "State": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LocalGatewayRouteTableVpcAssociationTypeDef = TypedDict(
    "LocalGatewayRouteTableVpcAssociationTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociationId": str,
        "LocalGatewayRouteTableId": str,
        "LocalGatewayRouteTableArn": str,
        "LocalGatewayId": str,
        "VpcId": str,
        "OwnerId": str,
        "State": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LocalGatewayTypeDef = TypedDict(
    "LocalGatewayTypeDef",
    {
        "LocalGatewayId": str,
        "OutpostArn": str,
        "OwnerId": str,
        "State": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LocalGatewayVirtualInterfaceGroupTypeDef = TypedDict(
    "LocalGatewayVirtualInterfaceGroupTypeDef",
    {
        "LocalGatewayVirtualInterfaceGroupId": str,
        "LocalGatewayVirtualInterfaceIds": List[str],
        "LocalGatewayId": str,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LocalGatewayVirtualInterfaceTypeDef = TypedDict(
    "LocalGatewayVirtualInterfaceTypeDef",
    {
        "LocalGatewayVirtualInterfaceId": str,
        "LocalGatewayId": str,
        "Vlan": int,
        "LocalAddress": str,
        "PeerAddress": str,
        "LocalBgpAsn": int,
        "PeerBgpAsn": int,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ManagedPrefixListTypeDef = TypedDict(
    "ManagedPrefixListTypeDef",
    {
        "PrefixListId": str,
        "AddressFamily": str,
        "State": PrefixListStateType,
        "StateMessage": str,
        "PrefixListArn": str,
        "PrefixListName": str,
        "MaxEntries": int,
        "Version": int,
        "Tags": List[TagTypeDef],
        "OwnerId": str,
    },
    total=False,
)

NetworkInsightsAccessScopeAnalysisTypeDef = TypedDict(
    "NetworkInsightsAccessScopeAnalysisTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisId": str,
        "NetworkInsightsAccessScopeAnalysisArn": str,
        "NetworkInsightsAccessScopeId": str,
        "Status": AnalysisStatusType,
        "StatusMessage": str,
        "WarningMessage": str,
        "StartDate": datetime,
        "EndDate": datetime,
        "FindingsFound": FindingsFoundType,
        "AnalyzedEniCount": int,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

NetworkInsightsAccessScopeTypeDef = TypedDict(
    "NetworkInsightsAccessScopeTypeDef",
    {
        "NetworkInsightsAccessScopeId": str,
        "NetworkInsightsAccessScopeArn": str,
        "CreatedDate": datetime,
        "UpdatedDate": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

NetworkInsightsPathTypeDef = TypedDict(
    "NetworkInsightsPathTypeDef",
    {
        "NetworkInsightsPathId": str,
        "NetworkInsightsPathArn": str,
        "CreatedDate": datetime,
        "Source": str,
        "Destination": str,
        "SourceIp": str,
        "DestinationIp": str,
        "Protocol": ProtocolType,
        "DestinationPort": int,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

PlacementGroupTypeDef = TypedDict(
    "PlacementGroupTypeDef",
    {
        "GroupName": str,
        "State": PlacementGroupStateType,
        "Strategy": PlacementStrategyType,
        "PartitionCount": int,
        "GroupId": str,
        "Tags": List[TagTypeDef],
        "GroupArn": str,
    },
    total=False,
)

ReplaceRootVolumeTaskTypeDef = TypedDict(
    "ReplaceRootVolumeTaskTypeDef",
    {
        "ReplaceRootVolumeTaskId": str,
        "InstanceId": str,
        "TaskState": ReplaceRootVolumeTaskStateType,
        "StartTime": str,
        "CompleteTime": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

SnapshotInfoTypeDef = TypedDict(
    "SnapshotInfoTypeDef",
    {
        "Description": str,
        "Tags": List[TagTypeDef],
        "Encrypted": bool,
        "VolumeId": str,
        "State": SnapshotStateType,
        "VolumeSize": int,
        "StartTime": datetime,
        "Progress": str,
        "OwnerId": str,
        "SnapshotId": str,
        "OutpostArn": str,
    },
    total=False,
)

SnapshotResponseMetadataTypeDef = TypedDict(
    "SnapshotResponseMetadataTypeDef",
    {
        "DataEncryptionKeyId": str,
        "Description": str,
        "Encrypted": bool,
        "KmsKeyId": str,
        "OwnerId": str,
        "Progress": str,
        "SnapshotId": str,
        "StartTime": datetime,
        "State": SnapshotStateType,
        "StateMessage": str,
        "VolumeId": str,
        "VolumeSize": int,
        "OwnerAlias": str,
        "OutpostArn": str,
        "Tags": List[TagTypeDef],
        "StorageTier": StorageTierType,
        "RestoreExpiryTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SnapshotTierStatusTypeDef = TypedDict(
    "SnapshotTierStatusTypeDef",
    {
        "SnapshotId": str,
        "VolumeId": str,
        "Status": SnapshotStateType,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
        "StorageTier": StorageTierType,
        "LastTieringStartTime": datetime,
        "LastTieringProgress": int,
        "LastTieringOperationStatus": TieringOperationStatusType,
        "LastTieringOperationStatusDetail": str,
        "ArchivalCompleteTime": datetime,
        "RestoreExpiryTime": datetime,
    },
    total=False,
)

SnapshotTypeDef = TypedDict(
    "SnapshotTypeDef",
    {
        "DataEncryptionKeyId": str,
        "Description": str,
        "Encrypted": bool,
        "KmsKeyId": str,
        "OwnerId": str,
        "Progress": str,
        "SnapshotId": str,
        "StartTime": datetime,
        "State": SnapshotStateType,
        "StateMessage": str,
        "VolumeId": str,
        "VolumeSize": int,
        "OwnerAlias": str,
        "OutpostArn": str,
        "Tags": List[TagTypeDef],
        "StorageTier": StorageTierType,
        "RestoreExpiryTime": datetime,
    },
    total=False,
)

SpotFleetTagSpecificationTypeDef = TypedDict(
    "SpotFleetTagSpecificationTypeDef",
    {
        "ResourceType": ResourceTypeType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

SubnetCidrReservationTypeDef = TypedDict(
    "SubnetCidrReservationTypeDef",
    {
        "SubnetCidrReservationId": str,
        "SubnetId": str,
        "Cidr": str,
        "ReservationType": SubnetCidrReservationTypeType,
        "OwnerId": str,
        "Description": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TagSpecificationTypeDef = TypedDict(
    "TagSpecificationTypeDef",
    {
        "ResourceType": ResourceTypeType,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)

TrafficMirrorSessionTypeDef = TypedDict(
    "TrafficMirrorSessionTypeDef",
    {
        "TrafficMirrorSessionId": str,
        "TrafficMirrorTargetId": str,
        "TrafficMirrorFilterId": str,
        "NetworkInterfaceId": str,
        "OwnerId": str,
        "PacketLength": int,
        "SessionNumber": int,
        "VirtualNetworkId": int,
        "Description": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TrafficMirrorTargetTypeDef = TypedDict(
    "TrafficMirrorTargetTypeDef",
    {
        "TrafficMirrorTargetId": str,
        "NetworkInterfaceId": str,
        "NetworkLoadBalancerArn": str,
        "Type": TrafficMirrorTargetTypeType,
        "Description": str,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
        "GatewayLoadBalancerEndpointId": str,
    },
    total=False,
)

TransitGatewayRouteTableTypeDef = TypedDict(
    "TransitGatewayRouteTableTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "TransitGatewayId": str,
        "State": TransitGatewayRouteTableStateType,
        "DefaultAssociationRouteTable": bool,
        "DefaultPropagationRouteTable": bool,
        "CreationTime": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TrunkInterfaceAssociationTypeDef = TypedDict(
    "TrunkInterfaceAssociationTypeDef",
    {
        "AssociationId": str,
        "BranchInterfaceId": str,
        "TrunkInterfaceId": str,
        "InterfaceProtocol": InterfaceProtocolTypeType,
        "VlanId": int,
        "GreKey": int,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

VpcClassicLinkTypeDef = TypedDict(
    "VpcClassicLinkTypeDef",
    {
        "ClassicLinkEnabled": bool,
        "Tags": List[TagTypeDef],
        "VpcId": str,
    },
    total=False,
)

AdvertiseByoipCidrResultTypeDef = TypedDict(
    "AdvertiseByoipCidrResultTypeDef",
    {
        "ByoipCidr": ByoipCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeprovisionByoipCidrResultTypeDef = TypedDict(
    "DeprovisionByoipCidrResultTypeDef",
    {
        "ByoipCidr": ByoipCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeByoipCidrsResultTypeDef = TypedDict(
    "DescribeByoipCidrsResultTypeDef",
    {
        "ByoipCidrs": List[ByoipCidrTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MoveByoipCidrToIpamResultTypeDef = TypedDict(
    "MoveByoipCidrToIpamResultTypeDef",
    {
        "ByoipCidr": ByoipCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ProvisionByoipCidrResultTypeDef = TypedDict(
    "ProvisionByoipCidrResultTypeDef",
    {
        "ByoipCidr": ByoipCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

WithdrawByoipCidrResultTypeDef = TypedDict(
    "WithdrawByoipCidrResultTypeDef",
    {
        "ByoipCidr": ByoipCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AllocateIpamPoolCidrResultTypeDef = TypedDict(
    "AllocateIpamPoolCidrResultTypeDef",
    {
        "IpamPoolAllocation": IpamPoolAllocationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetIpamPoolAllocationsResultTypeDef = TypedDict(
    "GetIpamPoolAllocationsResultTypeDef",
    {
        "IpamPoolAllocations": List[IpamPoolAllocationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcEndpointServicePermissionsResultTypeDef = TypedDict(
    "DescribeVpcEndpointServicePermissionsResultTypeDef",
    {
        "AllowedPrincipals": List[AllowedPrincipalTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AnalysisAclRuleTypeDef = TypedDict(
    "AnalysisAclRuleTypeDef",
    {
        "Cidr": str,
        "Egress": bool,
        "PortRange": PortRangeTypeDef,
        "Protocol": str,
        "RuleAction": str,
        "RuleNumber": int,
    },
    total=False,
)

AnalysisPacketHeaderTypeDef = TypedDict(
    "AnalysisPacketHeaderTypeDef",
    {
        "DestinationAddresses": List[str],
        "DestinationPortRanges": List[PortRangeTypeDef],
        "Protocol": str,
        "SourceAddresses": List[str],
        "SourcePortRanges": List[PortRangeTypeDef],
    },
    total=False,
)

AnalysisSecurityGroupRuleTypeDef = TypedDict(
    "AnalysisSecurityGroupRuleTypeDef",
    {
        "Cidr": str,
        "Direction": str,
        "SecurityGroupId": str,
        "PortRange": PortRangeTypeDef,
        "PrefixListId": str,
        "Protocol": str,
    },
    total=False,
)

AssignPrivateIpAddressesResultTypeDef = TypedDict(
    "AssignPrivateIpAddressesResultTypeDef",
    {
        "NetworkInterfaceId": str,
        "AssignedPrivateIpAddresses": List[AssignedPrivateIpAddressTypeDef],
        "AssignedIpv4Prefixes": List[Ipv4PrefixSpecificationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateClientVpnTargetNetworkResultTypeDef = TypedDict(
    "AssociateClientVpnTargetNetworkResultTypeDef",
    {
        "AssociationId": str,
        "Status": AssociationStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateClientVpnTargetNetworkResultTypeDef = TypedDict(
    "DisassociateClientVpnTargetNetworkResultTypeDef",
    {
        "AssociationId": str,
        "Status": AssociationStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TargetNetworkTypeDef = TypedDict(
    "TargetNetworkTypeDef",
    {
        "AssociationId": str,
        "VpcId": str,
        "TargetNetworkId": str,
        "ClientVpnEndpointId": str,
        "Status": AssociationStatusTypeDef,
        "SecurityGroups": List[str],
    },
    total=False,
)

AssociateIamInstanceProfileRequestRequestTypeDef = TypedDict(
    "AssociateIamInstanceProfileRequestRequestTypeDef",
    {
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "InstanceId": str,
    },
)

ReplaceIamInstanceProfileAssociationRequestRequestTypeDef = TypedDict(
    "ReplaceIamInstanceProfileAssociationRequestRequestTypeDef",
    {
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "AssociationId": str,
    },
)

AssociateRouteTableResultTypeDef = TypedDict(
    "AssociateRouteTableResultTypeDef",
    {
        "AssociationId": str,
        "AssociationState": RouteTableAssociationStateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplaceRouteTableAssociationResultTypeDef = TypedDict(
    "ReplaceRouteTableAssociationResultTypeDef",
    {
        "NewAssociationId": str,
        "AssociationState": RouteTableAssociationStateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RouteTableAssociationTypeDef = TypedDict(
    "RouteTableAssociationTypeDef",
    {
        "Main": bool,
        "RouteTableAssociationId": str,
        "RouteTableId": str,
        "SubnetId": str,
        "GatewayId": str,
        "AssociationState": RouteTableAssociationStateTypeDef,
    },
    total=False,
)

AssociateTransitGatewayRouteTableResultTypeDef = TypedDict(
    "AssociateTransitGatewayRouteTableResultTypeDef",
    {
        "Association": TransitGatewayAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateTransitGatewayRouteTableResultTypeDef = TypedDict(
    "DisassociateTransitGatewayRouteTableResultTypeDef",
    {
        "Association": TransitGatewayAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetAssociatedEnclaveCertificateIamRolesResultTypeDef = TypedDict(
    "GetAssociatedEnclaveCertificateIamRolesResultTypeDef",
    {
        "AssociatedRoles": List[AssociatedRoleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IntegrateServicesTypeDef = TypedDict(
    "IntegrateServicesTypeDef",
    {
        "AthenaIntegrations": Sequence[AthenaIntegrationTypeDef],
    },
    total=False,
)

AttachVpnGatewayResultTypeDef = TypedDict(
    "AttachVpnGatewayResultTypeDef",
    {
        "VpcAttachment": VpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VpnGatewayTypeDef = TypedDict(
    "VpnGatewayTypeDef",
    {
        "AvailabilityZone": str,
        "State": VpnStateType,
        "Type": Literal["ipsec.1"],
        "VpcAttachments": List[VpcAttachmentTypeDef],
        "VpnGatewayId": str,
        "AmazonSideAsn": int,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

DescribeVpcAttributeResultTypeDef = TypedDict(
    "DescribeVpcAttributeResultTypeDef",
    {
        "VpcId": str,
        "EnableDnsHostnames": AttributeBooleanValueTypeDef,
        "EnableDnsSupport": AttributeBooleanValueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredModifySubnetAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifySubnetAttributeRequestRequestTypeDef",
    {
        "SubnetId": str,
    },
)
_OptionalModifySubnetAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifySubnetAttributeRequestRequestTypeDef",
    {
        "AssignIpv6AddressOnCreation": AttributeBooleanValueTypeDef,
        "MapPublicIpOnLaunch": AttributeBooleanValueTypeDef,
        "MapCustomerOwnedIpOnLaunch": AttributeBooleanValueTypeDef,
        "CustomerOwnedIpv4Pool": str,
        "EnableDns64": AttributeBooleanValueTypeDef,
        "PrivateDnsHostnameTypeOnLaunch": HostnameTypeType,
        "EnableResourceNameDnsARecordOnLaunch": AttributeBooleanValueTypeDef,
        "EnableResourceNameDnsAAAARecordOnLaunch": AttributeBooleanValueTypeDef,
        "EnableLniAtDeviceIndex": int,
        "DisableLniAtDeviceIndex": AttributeBooleanValueTypeDef,
    },
    total=False,
)


class ModifySubnetAttributeRequestRequestTypeDef(
    _RequiredModifySubnetAttributeRequestRequestTypeDef,
    _OptionalModifySubnetAttributeRequestRequestTypeDef,
):
    pass


_RequiredModifyVolumeAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVolumeAttributeRequestRequestTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalModifyVolumeAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVolumeAttributeRequestRequestTypeDef",
    {
        "AutoEnableIO": AttributeBooleanValueTypeDef,
        "DryRun": bool,
    },
    total=False,
)


class ModifyVolumeAttributeRequestRequestTypeDef(
    _RequiredModifyVolumeAttributeRequestRequestTypeDef,
    _OptionalModifyVolumeAttributeRequestRequestTypeDef,
):
    pass


ModifyVolumeAttributeRequestVolumeModifyAttributeTypeDef = TypedDict(
    "ModifyVolumeAttributeRequestVolumeModifyAttributeTypeDef",
    {
        "AutoEnableIO": AttributeBooleanValueTypeDef,
        "DryRun": bool,
    },
    total=False,
)

_RequiredModifyVpcAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcAttributeRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalModifyVpcAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcAttributeRequestRequestTypeDef",
    {
        "EnableDnsHostnames": AttributeBooleanValueTypeDef,
        "EnableDnsSupport": AttributeBooleanValueTypeDef,
    },
    total=False,
)


class ModifyVpcAttributeRequestRequestTypeDef(
    _RequiredModifyVpcAttributeRequestRequestTypeDef,
    _OptionalModifyVpcAttributeRequestRequestTypeDef,
):
    pass


ModifyVpcAttributeRequestVpcModifyAttributeTypeDef = TypedDict(
    "ModifyVpcAttributeRequestVpcModifyAttributeTypeDef",
    {
        "EnableDnsHostnames": AttributeBooleanValueTypeDef,
        "EnableDnsSupport": AttributeBooleanValueTypeDef,
    },
    total=False,
)

DhcpConfigurationTypeDef = TypedDict(
    "DhcpConfigurationTypeDef",
    {
        "Key": str,
        "Values": List[AttributeValueTypeDef],
    },
    total=False,
)

AuthorizationRuleTypeDef = TypedDict(
    "AuthorizationRuleTypeDef",
    {
        "ClientVpnEndpointId": str,
        "Description": str,
        "GroupId": str,
        "AccessAll": bool,
        "DestinationCidr": str,
        "Status": ClientVpnAuthorizationRuleStatusTypeDef,
    },
    total=False,
)

AuthorizeClientVpnIngressResultTypeDef = TypedDict(
    "AuthorizeClientVpnIngressResultTypeDef",
    {
        "Status": ClientVpnAuthorizationRuleStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RevokeClientVpnIngressResultTypeDef = TypedDict(
    "RevokeClientVpnIngressResultTypeDef",
    {
        "Status": ClientVpnAuthorizationRuleStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AvailabilityZoneTypeDef = TypedDict(
    "AvailabilityZoneTypeDef",
    {
        "State": AvailabilityZoneStateType,
        "OptInStatus": AvailabilityZoneOptInStatusType,
        "Messages": List[AvailabilityZoneMessageTypeDef],
        "RegionName": str,
        "ZoneName": str,
        "ZoneId": str,
        "GroupName": str,
        "NetworkBorderGroup": str,
        "ZoneType": str,
        "ParentZoneName": str,
        "ParentZoneId": str,
    },
    total=False,
)

AvailableCapacityTypeDef = TypedDict(
    "AvailableCapacityTypeDef",
    {
        "AvailableInstanceCapacity": List[InstanceCapacityTypeDef],
        "AvailableVCpus": int,
    },
    total=False,
)

BlockDeviceMappingTypeDef = TypedDict(
    "BlockDeviceMappingTypeDef",
    {
        "DeviceName": str,
        "VirtualName": str,
        "Ebs": EbsBlockDeviceTypeDef,
        "NoDevice": str,
    },
    total=False,
)

FailedCapacityReservationFleetCancellationResultTypeDef = TypedDict(
    "FailedCapacityReservationFleetCancellationResultTypeDef",
    {
        "CapacityReservationFleetId": str,
        "CancelCapacityReservationFleetError": CancelCapacityReservationFleetErrorTypeDef,
    },
    total=False,
)

CancelSpotFleetRequestsErrorItemTypeDef = TypedDict(
    "CancelSpotFleetRequestsErrorItemTypeDef",
    {
        "Error": CancelSpotFleetRequestsErrorTypeDef,
        "SpotFleetRequestId": str,
    },
    total=False,
)

CancelSpotInstanceRequestsResultTypeDef = TypedDict(
    "CancelSpotInstanceRequestsResultTypeDef",
    {
        "CancelledSpotInstanceRequests": List[CancelledSpotInstanceRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CapacityReservationFleetTypeDef = TypedDict(
    "CapacityReservationFleetTypeDef",
    {
        "CapacityReservationFleetId": str,
        "CapacityReservationFleetArn": str,
        "State": CapacityReservationFleetStateType,
        "TotalTargetCapacity": int,
        "TotalFulfilledCapacity": float,
        "Tenancy": Literal["default"],
        "EndDate": datetime,
        "CreateTime": datetime,
        "InstanceMatchCriteria": Literal["open"],
        "AllocationStrategy": str,
        "InstanceTypeSpecifications": List[FleetCapacityReservationTypeDef],
        "Tags": List[TagTypeDef],
    },
    total=False,
)

CreateCapacityReservationFleetResultTypeDef = TypedDict(
    "CreateCapacityReservationFleetResultTypeDef",
    {
        "CapacityReservationFleetId": str,
        "State": CapacityReservationFleetStateType,
        "TotalTargetCapacity": int,
        "TotalFulfilledCapacity": float,
        "InstanceMatchCriteria": Literal["open"],
        "AllocationStrategy": str,
        "CreateTime": datetime,
        "EndDate": datetime,
        "Tenancy": Literal["default"],
        "FleetCapacityReservations": List[FleetCapacityReservationTypeDef],
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetGroupsForCapacityReservationResultTypeDef = TypedDict(
    "GetGroupsForCapacityReservationResultTypeDef",
    {
        "NextToken": str,
        "CapacityReservationGroups": List[CapacityReservationGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

OnDemandOptionsRequestTypeDef = TypedDict(
    "OnDemandOptionsRequestTypeDef",
    {
        "AllocationStrategy": FleetOnDemandAllocationStrategyType,
        "CapacityReservationOptions": CapacityReservationOptionsRequestTypeDef,
        "SingleInstanceType": bool,
        "SingleAvailabilityZone": bool,
        "MinTargetCapacity": int,
        "MaxTotalPrice": str,
    },
    total=False,
)

OnDemandOptionsTypeDef = TypedDict(
    "OnDemandOptionsTypeDef",
    {
        "AllocationStrategy": FleetOnDemandAllocationStrategyType,
        "CapacityReservationOptions": CapacityReservationOptionsTypeDef,
        "SingleInstanceType": bool,
        "SingleAvailabilityZone": bool,
        "MinTargetCapacity": int,
        "MaxTotalPrice": str,
    },
    total=False,
)

CapacityReservationSpecificationResponseResponseMetadataTypeDef = TypedDict(
    "CapacityReservationSpecificationResponseResponseMetadataTypeDef",
    {
        "CapacityReservationPreference": CapacityReservationPreferenceType,
        "CapacityReservationTarget": CapacityReservationTargetResponseTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CapacityReservationSpecificationResponseTypeDef = TypedDict(
    "CapacityReservationSpecificationResponseTypeDef",
    {
        "CapacityReservationPreference": CapacityReservationPreferenceType,
        "CapacityReservationTarget": CapacityReservationTargetResponseTypeDef,
    },
    total=False,
)

LaunchTemplateCapacityReservationSpecificationResponseTypeDef = TypedDict(
    "LaunchTemplateCapacityReservationSpecificationResponseTypeDef",
    {
        "CapacityReservationPreference": CapacityReservationPreferenceType,
        "CapacityReservationTarget": CapacityReservationTargetResponseTypeDef,
    },
    total=False,
)

CapacityReservationSpecificationTypeDef = TypedDict(
    "CapacityReservationSpecificationTypeDef",
    {
        "CapacityReservationPreference": CapacityReservationPreferenceType,
        "CapacityReservationTarget": CapacityReservationTargetTypeDef,
    },
    total=False,
)

LaunchTemplateCapacityReservationSpecificationRequestTypeDef = TypedDict(
    "LaunchTemplateCapacityReservationSpecificationRequestTypeDef",
    {
        "CapacityReservationPreference": CapacityReservationPreferenceType,
        "CapacityReservationTarget": CapacityReservationTargetTypeDef,
    },
    total=False,
)

DescribeVpcClassicLinkDnsSupportResultTypeDef = TypedDict(
    "DescribeVpcClassicLinkDnsSupportResultTypeDef",
    {
        "NextToken": str,
        "Vpcs": List[ClassicLinkDnsSupportTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ClassicLinkInstanceTypeDef = TypedDict(
    "ClassicLinkInstanceTypeDef",
    {
        "Groups": List[GroupIdentifierTypeDef],
        "InstanceId": str,
        "Tags": List[TagTypeDef],
        "VpcId": str,
    },
    total=False,
)

ClassicLoadBalancersConfigTypeDef = TypedDict(
    "ClassicLoadBalancersConfigTypeDef",
    {
        "ClassicLoadBalancers": List[ClassicLoadBalancerTypeDef],
    },
    total=False,
)

ExportClientVpnClientCertificateRevocationListResultTypeDef = TypedDict(
    "ExportClientVpnClientCertificateRevocationListResultTypeDef",
    {
        "CertificateRevocationList": str,
        "Status": ClientCertificateRevocationListStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ClientConnectResponseOptionsTypeDef = TypedDict(
    "ClientConnectResponseOptionsTypeDef",
    {
        "Enabled": bool,
        "LambdaFunctionArn": str,
        "Status": ClientVpnEndpointAttributeStatusTypeDef,
    },
    total=False,
)

ClientVpnAuthenticationRequestTypeDef = TypedDict(
    "ClientVpnAuthenticationRequestTypeDef",
    {
        "Type": ClientVpnAuthenticationTypeType,
        "ActiveDirectory": DirectoryServiceAuthenticationRequestTypeDef,
        "MutualAuthentication": CertificateAuthenticationRequestTypeDef,
        "FederatedAuthentication": FederatedAuthenticationRequestTypeDef,
    },
    total=False,
)

ClientVpnAuthenticationTypeDef = TypedDict(
    "ClientVpnAuthenticationTypeDef",
    {
        "Type": ClientVpnAuthenticationTypeType,
        "ActiveDirectory": DirectoryServiceAuthenticationTypeDef,
        "MutualAuthentication": CertificateAuthenticationTypeDef,
        "FederatedAuthentication": FederatedAuthenticationTypeDef,
    },
    total=False,
)

ClientVpnConnectionTypeDef = TypedDict(
    "ClientVpnConnectionTypeDef",
    {
        "ClientVpnEndpointId": str,
        "Timestamp": str,
        "ConnectionId": str,
        "Username": str,
        "ConnectionEstablishedTime": str,
        "IngressBytes": str,
        "EgressBytes": str,
        "IngressPackets": str,
        "EgressPackets": str,
        "ClientIp": str,
        "CommonName": str,
        "Status": ClientVpnConnectionStatusTypeDef,
        "ConnectionEndTime": str,
        "PostureComplianceStatuses": List[str],
    },
    total=False,
)

TerminateConnectionStatusTypeDef = TypedDict(
    "TerminateConnectionStatusTypeDef",
    {
        "ConnectionId": str,
        "PreviousStatus": ClientVpnConnectionStatusTypeDef,
        "CurrentStatus": ClientVpnConnectionStatusTypeDef,
    },
    total=False,
)

CreateClientVpnEndpointResultTypeDef = TypedDict(
    "CreateClientVpnEndpointResultTypeDef",
    {
        "ClientVpnEndpointId": str,
        "Status": ClientVpnEndpointStatusTypeDef,
        "DnsName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteClientVpnEndpointResultTypeDef = TypedDict(
    "DeleteClientVpnEndpointResultTypeDef",
    {
        "Status": ClientVpnEndpointStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ClientVpnRouteTypeDef = TypedDict(
    "ClientVpnRouteTypeDef",
    {
        "ClientVpnEndpointId": str,
        "DestinationCidr": str,
        "TargetSubnet": str,
        "Type": str,
        "Origin": str,
        "Status": ClientVpnRouteStatusTypeDef,
        "Description": str,
    },
    total=False,
)

CreateClientVpnRouteResultTypeDef = TypedDict(
    "CreateClientVpnRouteResultTypeDef",
    {
        "Status": ClientVpnRouteStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteClientVpnRouteResultTypeDef = TypedDict(
    "DeleteClientVpnRouteResultTypeDef",
    {
        "Status": ClientVpnRouteStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCoipPoolUsageResultTypeDef = TypedDict(
    "GetCoipPoolUsageResultTypeDef",
    {
        "CoipPoolId": str,
        "CoipAddressUsages": List[CoipAddressUsageTypeDef],
        "LocalGatewayRouteTableId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateVpcEndpointConnectionNotificationResultTypeDef = TypedDict(
    "CreateVpcEndpointConnectionNotificationResultTypeDef",
    {
        "ConnectionNotification": ConnectionNotificationTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcEndpointConnectionNotificationsResultTypeDef = TypedDict(
    "DescribeVpcEndpointConnectionNotificationsResultTypeDef",
    {
        "ConnectionNotificationSet": List[ConnectionNotificationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredModifyInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceEventWindowRequestRequestTypeDef",
    {
        "InstanceEventWindowId": str,
    },
)
_OptionalModifyInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceEventWindowRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Name": str,
        "TimeRanges": Sequence[InstanceEventWindowTimeRangeRequestTypeDef],
        "CronExpression": str,
    },
    total=False,
)


class ModifyInstanceEventWindowRequestRequestTypeDef(
    _RequiredModifyInstanceEventWindowRequestRequestTypeDef,
    _OptionalModifyInstanceEventWindowRequestRequestTypeDef,
):
    pass


_RequiredModifyIpamPoolRequestRequestTypeDef = TypedDict(
    "_RequiredModifyIpamPoolRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalModifyIpamPoolRequestRequestTypeDef = TypedDict(
    "_OptionalModifyIpamPoolRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Description": str,
        "AutoImport": bool,
        "AllocationMinNetmaskLength": int,
        "AllocationMaxNetmaskLength": int,
        "AllocationDefaultNetmaskLength": int,
        "ClearAllocationDefaultNetmaskLength": bool,
        "AddAllocationResourceTags": Sequence[RequestIpamResourceTagTypeDef],
        "RemoveAllocationResourceTags": Sequence[RequestIpamResourceTagTypeDef],
    },
    total=False,
)


class ModifyIpamPoolRequestRequestTypeDef(
    _RequiredModifyIpamPoolRequestRequestTypeDef, _OptionalModifyIpamPoolRequestRequestTypeDef
):
    pass


CreateLocalGatewayRouteResultTypeDef = TypedDict(
    "CreateLocalGatewayRouteResultTypeDef",
    {
        "Route": LocalGatewayRouteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLocalGatewayRouteResultTypeDef = TypedDict(
    "DeleteLocalGatewayRouteResultTypeDef",
    {
        "Route": LocalGatewayRouteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchLocalGatewayRoutesResultTypeDef = TypedDict(
    "SearchLocalGatewayRoutesResultTypeDef",
    {
        "Routes": List[LocalGatewayRouteTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef = TypedDict(
    "_RequiredCreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef",
    {
        "Egress": bool,
        "Protocol": str,
        "RuleAction": RuleActionType,
        "RuleNumber": int,
    },
)
_OptionalCreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef = TypedDict(
    "_OptionalCreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef",
    {
        "CidrBlock": str,
        "DryRun": bool,
        "IcmpTypeCode": IcmpTypeCodeTypeDef,
        "Ipv6CidrBlock": str,
        "PortRange": PortRangeTypeDef,
    },
    total=False,
)


class CreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef(
    _RequiredCreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef,
    _OptionalCreateNetworkAclEntryRequestNetworkAclCreateEntryTypeDef,
):
    pass


_RequiredCreateNetworkAclEntryRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNetworkAclEntryRequestRequestTypeDef",
    {
        "Egress": bool,
        "NetworkAclId": str,
        "Protocol": str,
        "RuleAction": RuleActionType,
        "RuleNumber": int,
    },
)
_OptionalCreateNetworkAclEntryRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNetworkAclEntryRequestRequestTypeDef",
    {
        "CidrBlock": str,
        "DryRun": bool,
        "IcmpTypeCode": IcmpTypeCodeTypeDef,
        "Ipv6CidrBlock": str,
        "PortRange": PortRangeTypeDef,
    },
    total=False,
)


class CreateNetworkAclEntryRequestRequestTypeDef(
    _RequiredCreateNetworkAclEntryRequestRequestTypeDef,
    _OptionalCreateNetworkAclEntryRequestRequestTypeDef,
):
    pass


NetworkAclEntryTypeDef = TypedDict(
    "NetworkAclEntryTypeDef",
    {
        "CidrBlock": str,
        "Egress": bool,
        "IcmpTypeCode": IcmpTypeCodeTypeDef,
        "Ipv6CidrBlock": str,
        "PortRange": PortRangeTypeDef,
        "Protocol": str,
        "RuleAction": RuleActionType,
        "RuleNumber": int,
    },
    total=False,
)

_RequiredReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef = TypedDict(
    "_RequiredReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef",
    {
        "Egress": bool,
        "Protocol": str,
        "RuleAction": RuleActionType,
        "RuleNumber": int,
    },
)
_OptionalReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef = TypedDict(
    "_OptionalReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef",
    {
        "CidrBlock": str,
        "DryRun": bool,
        "IcmpTypeCode": IcmpTypeCodeTypeDef,
        "Ipv6CidrBlock": str,
        "PortRange": PortRangeTypeDef,
    },
    total=False,
)


class ReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef(
    _RequiredReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef,
    _OptionalReplaceNetworkAclEntryRequestNetworkAclReplaceEntryTypeDef,
):
    pass


_RequiredReplaceNetworkAclEntryRequestRequestTypeDef = TypedDict(
    "_RequiredReplaceNetworkAclEntryRequestRequestTypeDef",
    {
        "Egress": bool,
        "NetworkAclId": str,
        "Protocol": str,
        "RuleAction": RuleActionType,
        "RuleNumber": int,
    },
)
_OptionalReplaceNetworkAclEntryRequestRequestTypeDef = TypedDict(
    "_OptionalReplaceNetworkAclEntryRequestRequestTypeDef",
    {
        "CidrBlock": str,
        "DryRun": bool,
        "IcmpTypeCode": IcmpTypeCodeTypeDef,
        "Ipv6CidrBlock": str,
        "PortRange": PortRangeTypeDef,
    },
    total=False,
)


class ReplaceNetworkAclEntryRequestRequestTypeDef(
    _RequiredReplaceNetworkAclEntryRequestRequestTypeDef,
    _OptionalReplaceNetworkAclEntryRequestRequestTypeDef,
):
    pass


InstanceNetworkInterfaceSpecificationTypeDef = TypedDict(
    "InstanceNetworkInterfaceSpecificationTypeDef",
    {
        "AssociatePublicIpAddress": bool,
        "DeleteOnTermination": bool,
        "Description": str,
        "DeviceIndex": int,
        "Groups": List[str],
        "Ipv6AddressCount": int,
        "Ipv6Addresses": List[InstanceIpv6AddressTypeDef],
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
        "PrivateIpAddresses": List[PrivateIpAddressSpecificationTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "SubnetId": str,
        "AssociateCarrierIpAddress": bool,
        "InterfaceType": str,
        "NetworkCardIndex": int,
        "Ipv4Prefixes": List[Ipv4PrefixSpecificationRequestTypeDef],
        "Ipv4PrefixCount": int,
        "Ipv6Prefixes": List[Ipv6PrefixSpecificationRequestTypeDef],
        "Ipv6PrefixCount": int,
    },
    total=False,
)

CreateReservedInstancesListingRequestRequestTypeDef = TypedDict(
    "CreateReservedInstancesListingRequestRequestTypeDef",
    {
        "ClientToken": str,
        "InstanceCount": int,
        "PriceSchedules": Sequence[PriceScheduleSpecificationTypeDef],
        "ReservedInstancesId": str,
    },
)

_RequiredCreateStoreImageTaskRequestRequestTypeDef = TypedDict(
    "_RequiredCreateStoreImageTaskRequestRequestTypeDef",
    {
        "ImageId": str,
        "Bucket": str,
    },
)
_OptionalCreateStoreImageTaskRequestRequestTypeDef = TypedDict(
    "_OptionalCreateStoreImageTaskRequestRequestTypeDef",
    {
        "S3ObjectTags": Sequence[S3ObjectTagTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateStoreImageTaskRequestRequestTypeDef(
    _RequiredCreateStoreImageTaskRequestRequestTypeDef,
    _OptionalCreateStoreImageTaskRequestRequestTypeDef,
):
    pass


_RequiredCreateTrafficMirrorFilterRuleRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTrafficMirrorFilterRuleRequestRequestTypeDef",
    {
        "TrafficMirrorFilterId": str,
        "TrafficDirection": TrafficDirectionType,
        "RuleNumber": int,
        "RuleAction": TrafficMirrorRuleActionType,
        "DestinationCidrBlock": str,
        "SourceCidrBlock": str,
    },
)
_OptionalCreateTrafficMirrorFilterRuleRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTrafficMirrorFilterRuleRequestRequestTypeDef",
    {
        "DestinationPortRange": TrafficMirrorPortRangeRequestTypeDef,
        "SourcePortRange": TrafficMirrorPortRangeRequestTypeDef,
        "Protocol": int,
        "Description": str,
        "DryRun": bool,
        "ClientToken": str,
    },
    total=False,
)


class CreateTrafficMirrorFilterRuleRequestRequestTypeDef(
    _RequiredCreateTrafficMirrorFilterRuleRequestRequestTypeDef,
    _OptionalCreateTrafficMirrorFilterRuleRequestRequestTypeDef,
):
    pass


_RequiredModifyTrafficMirrorFilterRuleRequestRequestTypeDef = TypedDict(
    "_RequiredModifyTrafficMirrorFilterRuleRequestRequestTypeDef",
    {
        "TrafficMirrorFilterRuleId": str,
    },
)
_OptionalModifyTrafficMirrorFilterRuleRequestRequestTypeDef = TypedDict(
    "_OptionalModifyTrafficMirrorFilterRuleRequestRequestTypeDef",
    {
        "TrafficDirection": TrafficDirectionType,
        "RuleNumber": int,
        "RuleAction": TrafficMirrorRuleActionType,
        "DestinationPortRange": TrafficMirrorPortRangeRequestTypeDef,
        "SourcePortRange": TrafficMirrorPortRangeRequestTypeDef,
        "Protocol": int,
        "DestinationCidrBlock": str,
        "SourceCidrBlock": str,
        "Description": str,
        "RemoveFields": Sequence[TrafficMirrorFilterRuleFieldType],
        "DryRun": bool,
    },
    total=False,
)


class ModifyTrafficMirrorFilterRuleRequestRequestTypeDef(
    _RequiredModifyTrafficMirrorFilterRuleRequestRequestTypeDef,
    _OptionalModifyTrafficMirrorFilterRuleRequestRequestTypeDef,
):
    pass


CreateVolumePermissionModificationsTypeDef = TypedDict(
    "CreateVolumePermissionModificationsTypeDef",
    {
        "Add": Sequence[CreateVolumePermissionTypeDef],
        "Remove": Sequence[CreateVolumePermissionTypeDef],
    },
    total=False,
)

_RequiredModifyVpcEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcEndpointRequestRequestTypeDef",
    {
        "VpcEndpointId": str,
    },
)
_OptionalModifyVpcEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcEndpointRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ResetPolicy": bool,
        "PolicyDocument": str,
        "AddRouteTableIds": Sequence[str],
        "RemoveRouteTableIds": Sequence[str],
        "AddSubnetIds": Sequence[str],
        "RemoveSubnetIds": Sequence[str],
        "AddSecurityGroupIds": Sequence[str],
        "RemoveSecurityGroupIds": Sequence[str],
        "IpAddressType": IpAddressTypeType,
        "DnsOptions": DnsOptionsSpecificationTypeDef,
        "PrivateDnsEnabled": bool,
    },
    total=False,
)


class ModifyVpcEndpointRequestRequestTypeDef(
    _RequiredModifyVpcEndpointRequestRequestTypeDef, _OptionalModifyVpcEndpointRequestRequestTypeDef
):
    pass


DeleteFleetErrorItemTypeDef = TypedDict(
    "DeleteFleetErrorItemTypeDef",
    {
        "Error": DeleteFleetErrorTypeDef,
        "FleetId": str,
    },
    total=False,
)

DeleteInstanceEventWindowResultTypeDef = TypedDict(
    "DeleteInstanceEventWindowResultTypeDef",
    {
        "InstanceEventWindowState": InstanceEventWindowStateChangeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLaunchTemplateVersionsResponseErrorItemTypeDef = TypedDict(
    "DeleteLaunchTemplateVersionsResponseErrorItemTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "VersionNumber": int,
        "ResponseError": ResponseErrorTypeDef,
    },
    total=False,
)

FailedQueuedPurchaseDeletionTypeDef = TypedDict(
    "FailedQueuedPurchaseDeletionTypeDef",
    {
        "Error": DeleteQueuedReservedInstancesErrorTypeDef,
        "ReservedInstancesId": str,
    },
    total=False,
)

DeregisterInstanceEventNotificationAttributesRequestRequestTypeDef = TypedDict(
    "DeregisterInstanceEventNotificationAttributesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "InstanceTagAttribute": DeregisterInstanceTagAttributeRequestTypeDef,
    },
    total=False,
)

DeregisterInstanceEventNotificationAttributesResultTypeDef = TypedDict(
    "DeregisterInstanceEventNotificationAttributesResultTypeDef",
    {
        "InstanceTagAttribute": InstanceTagNotificationAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInstanceEventNotificationAttributesResultTypeDef = TypedDict(
    "DescribeInstanceEventNotificationAttributesResultTypeDef",
    {
        "InstanceTagAttribute": InstanceTagNotificationAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterInstanceEventNotificationAttributesResultTypeDef = TypedDict(
    "RegisterInstanceEventNotificationAttributesResultTypeDef",
    {
        "InstanceTagAttribute": InstanceTagNotificationAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeregisterTransitGatewayMulticastGroupMembersResultTypeDef = TypedDict(
    "DeregisterTransitGatewayMulticastGroupMembersResultTypeDef",
    {
        "DeregisteredMulticastGroupMembers": TransitGatewayMulticastDeregisteredGroupMembersTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeregisterTransitGatewayMulticastGroupSourcesResultTypeDef = TypedDict(
    "DeregisterTransitGatewayMulticastGroupSourcesResultTypeDef",
    {
        "DeregisteredMulticastGroupSources": TransitGatewayMulticastDeregisteredGroupSourcesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAddressesAttributeRequestDescribeAddressesAttributePaginateTypeDef = TypedDict(
    "DescribeAddressesAttributeRequestDescribeAddressesAttributePaginateTypeDef",
    {
        "AllocationIds": Sequence[str],
        "Attribute": Literal["domain-name"],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeByoipCidrsRequestDescribeByoipCidrsPaginateTypeDef = TypedDict(
    "DescribeByoipCidrsRequestDescribeByoipCidrsPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribePrincipalIdFormatRequestDescribePrincipalIdFormatPaginateTypeDef = TypedDict(
    "DescribePrincipalIdFormatRequestDescribePrincipalIdFormatPaginateTypeDef",
    {
        "DryRun": bool,
        "Resources": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef = TypedDict(
    "_RequiredDescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef",
    {
        "SpotFleetRequestId": str,
    },
)
_OptionalDescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef = TypedDict(
    "_OptionalDescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef(
    _RequiredDescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef,
    _OptionalDescribeSpotFleetInstancesRequestDescribeSpotFleetInstancesPaginateTypeDef,
):
    pass


DescribeSpotFleetRequestsRequestDescribeSpotFleetRequestsPaginateTypeDef = TypedDict(
    "DescribeSpotFleetRequestsRequestDescribeSpotFleetRequestsPaginateTypeDef",
    {
        "DryRun": bool,
        "SpotFleetRequestIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef = TypedDict(
    "_RequiredDescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalDescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef = TypedDict(
    "_OptionalDescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef(
    _RequiredDescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef,
    _OptionalDescribeStaleSecurityGroupsRequestDescribeStaleSecurityGroupsPaginateTypeDef,
):
    pass


DescribeVpcClassicLinkDnsSupportRequestDescribeVpcClassicLinkDnsSupportPaginateTypeDef = TypedDict(
    "DescribeVpcClassicLinkDnsSupportRequestDescribeVpcClassicLinkDnsSupportPaginateTypeDef",
    {
        "VpcIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredGetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef = TypedDict(
    "_RequiredGetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef",
    {
        "PoolId": str,
    },
)
_OptionalGetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef = TypedDict(
    "_OptionalGetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef(
    _RequiredGetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef,
    _OptionalGetAssociatedIpv6PoolCidrsRequestGetAssociatedIpv6PoolCidrsPaginateTypeDef,
):
    pass


_RequiredGetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef = TypedDict(
    "_RequiredGetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef",
    {
        "CapacityReservationId": str,
    },
)
_OptionalGetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef = TypedDict(
    "_OptionalGetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef(
    _RequiredGetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef,
    _OptionalGetGroupsForCapacityReservationRequestGetGroupsForCapacityReservationPaginateTypeDef,
):
    pass


_RequiredGetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef = TypedDict(
    "_RequiredGetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef",
    {
        "Cidr": str,
        "IpamScopeId": str,
    },
)
_OptionalGetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef = TypedDict(
    "_OptionalGetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef",
    {
        "DryRun": bool,
        "VpcId": str,
        "StartTime": Union[datetime, str],
        "EndTime": Union[datetime, str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef(
    _RequiredGetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef,
    _OptionalGetIpamAddressHistoryRequestGetIpamAddressHistoryPaginateTypeDef,
):
    pass


_RequiredGetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef = TypedDict(
    "_RequiredGetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef",
    {
        "PrefixListId": str,
    },
)
_OptionalGetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef = TypedDict(
    "_OptionalGetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef(
    _RequiredGetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef,
    _OptionalGetManagedPrefixListAssociationsRequestGetManagedPrefixListAssociationsPaginateTypeDef,
):
    pass


_RequiredGetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef = TypedDict(
    "_RequiredGetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef",
    {
        "PrefixListId": str,
    },
)
_OptionalGetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef = TypedDict(
    "_OptionalGetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef",
    {
        "DryRun": bool,
        "TargetVersion": int,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef(
    _RequiredGetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef,
    _OptionalGetManagedPrefixListEntriesRequestGetManagedPrefixListEntriesPaginateTypeDef,
):
    pass


GetVpnConnectionDeviceTypesRequestGetVpnConnectionDeviceTypesPaginateTypeDef = TypedDict(
    "GetVpnConnectionDeviceTypesRequestGetVpnConnectionDeviceTypesPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListImagesInRecycleBinRequestListImagesInRecycleBinPaginateTypeDef = TypedDict(
    "ListImagesInRecycleBinRequestListImagesInRecycleBinPaginateTypeDef",
    {
        "ImageIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSnapshotsInRecycleBinRequestListSnapshotsInRecycleBinPaginateTypeDef = TypedDict(
    "ListSnapshotsInRecycleBinRequestListSnapshotsInRecycleBinPaginateTypeDef",
    {
        "SnapshotIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeAddressesRequestRequestTypeDef = TypedDict(
    "DescribeAddressesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "PublicIps": Sequence[str],
        "AllocationIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

DescribeAvailabilityZonesRequestRequestTypeDef = TypedDict(
    "DescribeAvailabilityZonesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "ZoneNames": Sequence[str],
        "ZoneIds": Sequence[str],
        "AllAvailabilityZones": bool,
        "DryRun": bool,
    },
    total=False,
)

DescribeBundleTasksRequestRequestTypeDef = TypedDict(
    "DescribeBundleTasksRequestRequestTypeDef",
    {
        "BundleIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)

DescribeCapacityReservationFleetsRequestDescribeCapacityReservationFleetsPaginateTypeDef = (
    TypedDict(
        "DescribeCapacityReservationFleetsRequestDescribeCapacityReservationFleetsPaginateTypeDef",
        {
            "CapacityReservationFleetIds": Sequence[str],
            "Filters": Sequence[FilterTypeDef],
            "DryRun": bool,
            "PaginationConfig": PaginatorConfigTypeDef,
        },
        total=False,
    )
)

DescribeCapacityReservationFleetsRequestRequestTypeDef = TypedDict(
    "DescribeCapacityReservationFleetsRequestRequestTypeDef",
    {
        "CapacityReservationFleetIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)

DescribeCapacityReservationsRequestDescribeCapacityReservationsPaginateTypeDef = TypedDict(
    "DescribeCapacityReservationsRequestDescribeCapacityReservationsPaginateTypeDef",
    {
        "CapacityReservationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeCapacityReservationsRequestRequestTypeDef = TypedDict(
    "DescribeCapacityReservationsRequestRequestTypeDef",
    {
        "CapacityReservationIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)

DescribeCarrierGatewaysRequestDescribeCarrierGatewaysPaginateTypeDef = TypedDict(
    "DescribeCarrierGatewaysRequestDescribeCarrierGatewaysPaginateTypeDef",
    {
        "CarrierGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeCarrierGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeCarrierGatewaysRequestRequestTypeDef",
    {
        "CarrierGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeClassicLinkInstancesRequestDescribeClassicLinkInstancesPaginateTypeDef = TypedDict(
    "DescribeClassicLinkInstancesRequestDescribeClassicLinkInstancesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "InstanceIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeClassicLinkInstancesRequestRequestTypeDef = TypedDict(
    "DescribeClassicLinkInstancesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "InstanceIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

_RequiredDescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef = TypedDict(
    "_RequiredDescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef = TypedDict(
    "_OptionalDescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef(
    _RequiredDescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef,
    _OptionalDescribeClientVpnAuthorizationRulesRequestDescribeClientVpnAuthorizationRulesPaginateTypeDef,
):
    pass


_RequiredDescribeClientVpnAuthorizationRulesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeClientVpnAuthorizationRulesRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnAuthorizationRulesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeClientVpnAuthorizationRulesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "NextToken": str,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
    },
    total=False,
)


class DescribeClientVpnAuthorizationRulesRequestRequestTypeDef(
    _RequiredDescribeClientVpnAuthorizationRulesRequestRequestTypeDef,
    _OptionalDescribeClientVpnAuthorizationRulesRequestRequestTypeDef,
):
    pass


_RequiredDescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef = TypedDict(
    "_RequiredDescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef = TypedDict(
    "_OptionalDescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef(
    _RequiredDescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef,
    _OptionalDescribeClientVpnConnectionsRequestDescribeClientVpnConnectionsPaginateTypeDef,
):
    pass


_RequiredDescribeClientVpnConnectionsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeClientVpnConnectionsRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnConnectionsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeClientVpnConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)


class DescribeClientVpnConnectionsRequestRequestTypeDef(
    _RequiredDescribeClientVpnConnectionsRequestRequestTypeDef,
    _OptionalDescribeClientVpnConnectionsRequestRequestTypeDef,
):
    pass


DescribeClientVpnEndpointsRequestDescribeClientVpnEndpointsPaginateTypeDef = TypedDict(
    "DescribeClientVpnEndpointsRequestDescribeClientVpnEndpointsPaginateTypeDef",
    {
        "ClientVpnEndpointIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeClientVpnEndpointsRequestRequestTypeDef = TypedDict(
    "DescribeClientVpnEndpointsRequestRequestTypeDef",
    {
        "ClientVpnEndpointIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)

_RequiredDescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef = TypedDict(
    "_RequiredDescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef = TypedDict(
    "_OptionalDescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef(
    _RequiredDescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef,
    _OptionalDescribeClientVpnRoutesRequestDescribeClientVpnRoutesPaginateTypeDef,
):
    pass


_RequiredDescribeClientVpnRoutesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeClientVpnRoutesRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnRoutesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeClientVpnRoutesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class DescribeClientVpnRoutesRequestRequestTypeDef(
    _RequiredDescribeClientVpnRoutesRequestRequestTypeDef,
    _OptionalDescribeClientVpnRoutesRequestRequestTypeDef,
):
    pass


_RequiredDescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef = TypedDict(
    "_RequiredDescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef = TypedDict(
    "_OptionalDescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef",
    {
        "AssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef(
    _RequiredDescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef,
    _OptionalDescribeClientVpnTargetNetworksRequestDescribeClientVpnTargetNetworksPaginateTypeDef,
):
    pass


_RequiredDescribeClientVpnTargetNetworksRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeClientVpnTargetNetworksRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalDescribeClientVpnTargetNetworksRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeClientVpnTargetNetworksRequestRequestTypeDef",
    {
        "AssociationIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class DescribeClientVpnTargetNetworksRequestRequestTypeDef(
    _RequiredDescribeClientVpnTargetNetworksRequestRequestTypeDef,
    _OptionalDescribeClientVpnTargetNetworksRequestRequestTypeDef,
):
    pass


DescribeCoipPoolsRequestDescribeCoipPoolsPaginateTypeDef = TypedDict(
    "DescribeCoipPoolsRequestDescribeCoipPoolsPaginateTypeDef",
    {
        "PoolIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeCoipPoolsRequestRequestTypeDef = TypedDict(
    "DescribeCoipPoolsRequestRequestTypeDef",
    {
        "PoolIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeCustomerGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeCustomerGatewaysRequestRequestTypeDef",
    {
        "CustomerGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)

DescribeDhcpOptionsRequestDescribeDhcpOptionsPaginateTypeDef = TypedDict(
    "DescribeDhcpOptionsRequestDescribeDhcpOptionsPaginateTypeDef",
    {
        "DhcpOptionsIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeDhcpOptionsRequestRequestTypeDef = TypedDict(
    "DescribeDhcpOptionsRequestRequestTypeDef",
    {
        "DhcpOptionsIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeEgressOnlyInternetGatewaysRequestDescribeEgressOnlyInternetGatewaysPaginateTypeDef = TypedDict(
    "DescribeEgressOnlyInternetGatewaysRequestDescribeEgressOnlyInternetGatewaysPaginateTypeDef",
    {
        "DryRun": bool,
        "EgressOnlyInternetGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeEgressOnlyInternetGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeEgressOnlyInternetGatewaysRequestRequestTypeDef",
    {
        "DryRun": bool,
        "EgressOnlyInternetGatewayIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)

DescribeElasticGpusRequestRequestTypeDef = TypedDict(
    "DescribeElasticGpusRequestRequestTypeDef",
    {
        "ElasticGpuIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeExportImageTasksRequestDescribeExportImageTasksPaginateTypeDef = TypedDict(
    "DescribeExportImageTasksRequestDescribeExportImageTasksPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ExportImageTaskIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeExportImageTasksRequestRequestTypeDef = TypedDict(
    "DescribeExportImageTasksRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ExportImageTaskIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeExportTasksRequestRequestTypeDef = TypedDict(
    "DescribeExportTasksRequestRequestTypeDef",
    {
        "ExportTaskIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)

DescribeFastLaunchImagesRequestDescribeFastLaunchImagesPaginateTypeDef = TypedDict(
    "DescribeFastLaunchImagesRequestDescribeFastLaunchImagesPaginateTypeDef",
    {
        "ImageIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeFastLaunchImagesRequestRequestTypeDef = TypedDict(
    "DescribeFastLaunchImagesRequestRequestTypeDef",
    {
        "ImageIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeFastSnapshotRestoresRequestDescribeFastSnapshotRestoresPaginateTypeDef = TypedDict(
    "DescribeFastSnapshotRestoresRequestDescribeFastSnapshotRestoresPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeFastSnapshotRestoresRequestRequestTypeDef = TypedDict(
    "DescribeFastSnapshotRestoresRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredDescribeFleetInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeFleetInstancesRequestRequestTypeDef",
    {
        "FleetId": str,
    },
)
_OptionalDescribeFleetInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeFleetInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)


class DescribeFleetInstancesRequestRequestTypeDef(
    _RequiredDescribeFleetInstancesRequestRequestTypeDef,
    _OptionalDescribeFleetInstancesRequestRequestTypeDef,
):
    pass


DescribeFleetsRequestDescribeFleetsPaginateTypeDef = TypedDict(
    "DescribeFleetsRequestDescribeFleetsPaginateTypeDef",
    {
        "DryRun": bool,
        "FleetIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeFleetsRequestRequestTypeDef = TypedDict(
    "DescribeFleetsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "FleetIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)

DescribeFlowLogsRequestDescribeFlowLogsPaginateTypeDef = TypedDict(
    "DescribeFlowLogsRequestDescribeFlowLogsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "FlowLogIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeFlowLogsRequestRequestTypeDef = TypedDict(
    "DescribeFlowLogsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "FlowLogIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeFpgaImagesRequestDescribeFpgaImagesPaginateTypeDef = TypedDict(
    "DescribeFpgaImagesRequestDescribeFpgaImagesPaginateTypeDef",
    {
        "DryRun": bool,
        "FpgaImageIds": Sequence[str],
        "Owners": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeFpgaImagesRequestRequestTypeDef = TypedDict(
    "DescribeFpgaImagesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "FpgaImageIds": Sequence[str],
        "Owners": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeHostReservationOfferingsRequestDescribeHostReservationOfferingsPaginateTypeDef = TypedDict(
    "DescribeHostReservationOfferingsRequestDescribeHostReservationOfferingsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxDuration": int,
        "MinDuration": int,
        "OfferingId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeHostReservationOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeHostReservationOfferingsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxDuration": int,
        "MaxResults": int,
        "MinDuration": int,
        "NextToken": str,
        "OfferingId": str,
    },
    total=False,
)

DescribeHostReservationsRequestDescribeHostReservationsPaginateTypeDef = TypedDict(
    "DescribeHostReservationsRequestDescribeHostReservationsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "HostReservationIdSet": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeHostReservationsRequestRequestTypeDef = TypedDict(
    "DescribeHostReservationsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "HostReservationIdSet": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeHostsRequestDescribeHostsPaginateTypeDef = TypedDict(
    "DescribeHostsRequestDescribeHostsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "HostIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeHostsRequestRequestTypeDef = TypedDict(
    "DescribeHostsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "HostIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeIamInstanceProfileAssociationsRequestDescribeIamInstanceProfileAssociationsPaginateTypeDef = TypedDict(
    "DescribeIamInstanceProfileAssociationsRequestDescribeIamInstanceProfileAssociationsPaginateTypeDef",
    {
        "AssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeIamInstanceProfileAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeIamInstanceProfileAssociationsRequestRequestTypeDef",
    {
        "AssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeImagesRequestRequestTypeDef = TypedDict(
    "DescribeImagesRequestRequestTypeDef",
    {
        "ExecutableUsers": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "ImageIds": Sequence[str],
        "Owners": Sequence[str],
        "IncludeDeprecated": bool,
        "DryRun": bool,
    },
    total=False,
)

DescribeImportImageTasksRequestDescribeImportImageTasksPaginateTypeDef = TypedDict(
    "DescribeImportImageTasksRequestDescribeImportImageTasksPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ImportTaskIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeImportImageTasksRequestRequestTypeDef = TypedDict(
    "DescribeImportImageTasksRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ImportTaskIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeImportSnapshotTasksRequestDescribeImportSnapshotTasksPaginateTypeDef = TypedDict(
    "DescribeImportSnapshotTasksRequestDescribeImportSnapshotTasksPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ImportTaskIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeImportSnapshotTasksRequestRequestTypeDef = TypedDict(
    "DescribeImportSnapshotTasksRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ImportTaskIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInstanceCreditSpecificationsRequestDescribeInstanceCreditSpecificationsPaginateTypeDef = TypedDict(
    "DescribeInstanceCreditSpecificationsRequestDescribeInstanceCreditSpecificationsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInstanceCreditSpecificationsRequestRequestTypeDef = TypedDict(
    "DescribeInstanceCreditSpecificationsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInstanceEventWindowsRequestDescribeInstanceEventWindowsPaginateTypeDef = TypedDict(
    "DescribeInstanceEventWindowsRequestDescribeInstanceEventWindowsPaginateTypeDef",
    {
        "DryRun": bool,
        "InstanceEventWindowIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInstanceEventWindowsRequestRequestTypeDef = TypedDict(
    "DescribeInstanceEventWindowsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "InstanceEventWindowIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInstanceStatusRequestDescribeInstanceStatusPaginateTypeDef = TypedDict(
    "DescribeInstanceStatusRequestDescribeInstanceStatusPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "IncludeAllInstances": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInstanceStatusRequestRequestTypeDef = TypedDict(
    "DescribeInstanceStatusRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
        "IncludeAllInstances": bool,
    },
    total=False,
)

DescribeInstanceTypeOfferingsRequestDescribeInstanceTypeOfferingsPaginateTypeDef = TypedDict(
    "DescribeInstanceTypeOfferingsRequestDescribeInstanceTypeOfferingsPaginateTypeDef",
    {
        "DryRun": bool,
        "LocationType": LocationTypeType,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInstanceTypeOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeInstanceTypeOfferingsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LocationType": LocationTypeType,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInstanceTypesRequestDescribeInstanceTypesPaginateTypeDef = TypedDict(
    "DescribeInstanceTypesRequestDescribeInstanceTypesPaginateTypeDef",
    {
        "DryRun": bool,
        "InstanceTypes": Sequence[InstanceTypeType],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInstanceTypesRequestRequestTypeDef = TypedDict(
    "DescribeInstanceTypesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "InstanceTypes": Sequence[InstanceTypeType],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInstancesRequestDescribeInstancesPaginateTypeDef = TypedDict(
    "DescribeInstancesRequestDescribeInstancesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInstancesRequestRequestTypeDef = TypedDict(
    "DescribeInstancesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInternetGatewaysRequestDescribeInternetGatewaysPaginateTypeDef = TypedDict(
    "DescribeInternetGatewaysRequestDescribeInternetGatewaysPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "InternetGatewayIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeInternetGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeInternetGatewaysRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "InternetGatewayIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeIpamPoolsRequestDescribeIpamPoolsPaginateTypeDef = TypedDict(
    "DescribeIpamPoolsRequestDescribeIpamPoolsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "IpamPoolIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeIpamPoolsRequestRequestTypeDef = TypedDict(
    "DescribeIpamPoolsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "IpamPoolIds": Sequence[str],
    },
    total=False,
)

DescribeIpamScopesRequestDescribeIpamScopesPaginateTypeDef = TypedDict(
    "DescribeIpamScopesRequestDescribeIpamScopesPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "IpamScopeIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeIpamScopesRequestRequestTypeDef = TypedDict(
    "DescribeIpamScopesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "IpamScopeIds": Sequence[str],
    },
    total=False,
)

DescribeIpamsRequestDescribeIpamsPaginateTypeDef = TypedDict(
    "DescribeIpamsRequestDescribeIpamsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "IpamIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeIpamsRequestRequestTypeDef = TypedDict(
    "DescribeIpamsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "IpamIds": Sequence[str],
    },
    total=False,
)

DescribeIpv6PoolsRequestDescribeIpv6PoolsPaginateTypeDef = TypedDict(
    "DescribeIpv6PoolsRequestDescribeIpv6PoolsPaginateTypeDef",
    {
        "PoolIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeIpv6PoolsRequestRequestTypeDef = TypedDict(
    "DescribeIpv6PoolsRequestRequestTypeDef",
    {
        "PoolIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)

DescribeKeyPairsRequestRequestTypeDef = TypedDict(
    "DescribeKeyPairsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "KeyNames": Sequence[str],
        "KeyPairIds": Sequence[str],
        "DryRun": bool,
        "IncludePublicKey": bool,
    },
    total=False,
)

DescribeLaunchTemplateVersionsRequestDescribeLaunchTemplateVersionsPaginateTypeDef = TypedDict(
    "DescribeLaunchTemplateVersionsRequestDescribeLaunchTemplateVersionsPaginateTypeDef",
    {
        "DryRun": bool,
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "Versions": Sequence[str],
        "MinVersion": str,
        "MaxVersion": str,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLaunchTemplateVersionsRequestRequestTypeDef = TypedDict(
    "DescribeLaunchTemplateVersionsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "Versions": Sequence[str],
        "MinVersion": str,
        "MaxVersion": str,
        "NextToken": str,
        "MaxResults": int,
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)

DescribeLaunchTemplatesRequestDescribeLaunchTemplatesPaginateTypeDef = TypedDict(
    "DescribeLaunchTemplatesRequestDescribeLaunchTemplatesPaginateTypeDef",
    {
        "DryRun": bool,
        "LaunchTemplateIds": Sequence[str],
        "LaunchTemplateNames": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLaunchTemplatesRequestRequestTypeDef = TypedDict(
    "DescribeLaunchTemplatesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LaunchTemplateIds": Sequence[str],
        "LaunchTemplateNames": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsRequestDescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginateTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsRequestDescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsPaginateTypeDef",
    {
        "LocalGatewayRouteTableVirtualInterfaceGroupAssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsRequestRequestTypeDef",
    {
        "LocalGatewayRouteTableVirtualInterfaceGroupAssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeLocalGatewayRouteTableVpcAssociationsRequestDescribeLocalGatewayRouteTableVpcAssociationsPaginateTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTableVpcAssociationsRequestDescribeLocalGatewayRouteTableVpcAssociationsPaginateTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLocalGatewayRouteTableVpcAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTableVpcAssociationsRequestRequestTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociationIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeLocalGatewayRouteTablesRequestDescribeLocalGatewayRouteTablesPaginateTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTablesRequestDescribeLocalGatewayRouteTablesPaginateTypeDef",
    {
        "LocalGatewayRouteTableIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLocalGatewayRouteTablesRequestRequestTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTablesRequestRequestTypeDef",
    {
        "LocalGatewayRouteTableIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeLocalGatewayVirtualInterfaceGroupsRequestDescribeLocalGatewayVirtualInterfaceGroupsPaginateTypeDef = TypedDict(
    "DescribeLocalGatewayVirtualInterfaceGroupsRequestDescribeLocalGatewayVirtualInterfaceGroupsPaginateTypeDef",
    {
        "LocalGatewayVirtualInterfaceGroupIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLocalGatewayVirtualInterfaceGroupsRequestRequestTypeDef = TypedDict(
    "DescribeLocalGatewayVirtualInterfaceGroupsRequestRequestTypeDef",
    {
        "LocalGatewayVirtualInterfaceGroupIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeLocalGatewayVirtualInterfacesRequestDescribeLocalGatewayVirtualInterfacesPaginateTypeDef = TypedDict(
    "DescribeLocalGatewayVirtualInterfacesRequestDescribeLocalGatewayVirtualInterfacesPaginateTypeDef",
    {
        "LocalGatewayVirtualInterfaceIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLocalGatewayVirtualInterfacesRequestRequestTypeDef = TypedDict(
    "DescribeLocalGatewayVirtualInterfacesRequestRequestTypeDef",
    {
        "LocalGatewayVirtualInterfaceIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeLocalGatewaysRequestDescribeLocalGatewaysPaginateTypeDef = TypedDict(
    "DescribeLocalGatewaysRequestDescribeLocalGatewaysPaginateTypeDef",
    {
        "LocalGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLocalGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeLocalGatewaysRequestRequestTypeDef",
    {
        "LocalGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeManagedPrefixListsRequestDescribeManagedPrefixListsPaginateTypeDef = TypedDict(
    "DescribeManagedPrefixListsRequestDescribeManagedPrefixListsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PrefixListIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeManagedPrefixListsRequestRequestTypeDef = TypedDict(
    "DescribeManagedPrefixListsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "PrefixListIds": Sequence[str],
    },
    total=False,
)

DescribeMovingAddressesRequestDescribeMovingAddressesPaginateTypeDef = TypedDict(
    "DescribeMovingAddressesRequestDescribeMovingAddressesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PublicIps": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeMovingAddressesRequestRequestTypeDef = TypedDict(
    "DescribeMovingAddressesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "PublicIps": Sequence[str],
    },
    total=False,
)

DescribeNatGatewaysRequestDescribeNatGatewaysPaginateTypeDef = TypedDict(
    "DescribeNatGatewaysRequestDescribeNatGatewaysPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "NatGatewayIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNatGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeNatGatewaysRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NatGatewayIds": Sequence[str],
        "NextToken": str,
    },
    total=False,
)

DescribeNetworkAclsRequestDescribeNetworkAclsPaginateTypeDef = TypedDict(
    "DescribeNetworkAclsRequestDescribeNetworkAclsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NetworkAclIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkAclsRequestRequestTypeDef = TypedDict(
    "DescribeNetworkAclsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NetworkAclIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeNetworkInsightsAccessScopeAnalysesRequestDescribeNetworkInsightsAccessScopeAnalysesPaginateTypeDef = TypedDict(
    "DescribeNetworkInsightsAccessScopeAnalysesRequestDescribeNetworkInsightsAccessScopeAnalysesPaginateTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisIds": Sequence[str],
        "NetworkInsightsAccessScopeId": str,
        "AnalysisStartTimeBegin": Union[datetime, str],
        "AnalysisStartTimeEnd": Union[datetime, str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInsightsAccessScopeAnalysesRequestRequestTypeDef = TypedDict(
    "DescribeNetworkInsightsAccessScopeAnalysesRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisIds": Sequence[str],
        "NetworkInsightsAccessScopeId": str,
        "AnalysisStartTimeBegin": Union[datetime, str],
        "AnalysisStartTimeEnd": Union[datetime, str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "DryRun": bool,
        "NextToken": str,
    },
    total=False,
)

DescribeNetworkInsightsAccessScopesRequestDescribeNetworkInsightsAccessScopesPaginateTypeDef = TypedDict(
    "DescribeNetworkInsightsAccessScopesRequestDescribeNetworkInsightsAccessScopesPaginateTypeDef",
    {
        "NetworkInsightsAccessScopeIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInsightsAccessScopesRequestRequestTypeDef = TypedDict(
    "DescribeNetworkInsightsAccessScopesRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "DryRun": bool,
        "NextToken": str,
    },
    total=False,
)

DescribeNetworkInsightsAnalysesRequestDescribeNetworkInsightsAnalysesPaginateTypeDef = TypedDict(
    "DescribeNetworkInsightsAnalysesRequestDescribeNetworkInsightsAnalysesPaginateTypeDef",
    {
        "NetworkInsightsAnalysisIds": Sequence[str],
        "NetworkInsightsPathId": str,
        "AnalysisStartTime": Union[datetime, str],
        "AnalysisEndTime": Union[datetime, str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInsightsAnalysesRequestRequestTypeDef = TypedDict(
    "DescribeNetworkInsightsAnalysesRequestRequestTypeDef",
    {
        "NetworkInsightsAnalysisIds": Sequence[str],
        "NetworkInsightsPathId": str,
        "AnalysisStartTime": Union[datetime, str],
        "AnalysisEndTime": Union[datetime, str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "DryRun": bool,
        "NextToken": str,
    },
    total=False,
)

DescribeNetworkInsightsPathsRequestDescribeNetworkInsightsPathsPaginateTypeDef = TypedDict(
    "DescribeNetworkInsightsPathsRequestDescribeNetworkInsightsPathsPaginateTypeDef",
    {
        "NetworkInsightsPathIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInsightsPathsRequestRequestTypeDef = TypedDict(
    "DescribeNetworkInsightsPathsRequestRequestTypeDef",
    {
        "NetworkInsightsPathIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "DryRun": bool,
        "NextToken": str,
    },
    total=False,
)

DescribeNetworkInterfacePermissionsRequestDescribeNetworkInterfacePermissionsPaginateTypeDef = TypedDict(
    "DescribeNetworkInterfacePermissionsRequestDescribeNetworkInterfacePermissionsPaginateTypeDef",
    {
        "NetworkInterfacePermissionIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInterfacePermissionsRequestRequestTypeDef = TypedDict(
    "DescribeNetworkInterfacePermissionsRequestRequestTypeDef",
    {
        "NetworkInterfacePermissionIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeNetworkInterfacesRequestDescribeNetworkInterfacesPaginateTypeDef = TypedDict(
    "DescribeNetworkInterfacesRequestDescribeNetworkInterfacesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NetworkInterfaceIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInterfacesRequestRequestTypeDef = TypedDict(
    "DescribeNetworkInterfacesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NetworkInterfaceIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribePlacementGroupsRequestRequestTypeDef = TypedDict(
    "DescribePlacementGroupsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "GroupNames": Sequence[str],
        "GroupIds": Sequence[str],
    },
    total=False,
)

DescribePrefixListsRequestDescribePrefixListsPaginateTypeDef = TypedDict(
    "DescribePrefixListsRequestDescribePrefixListsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PrefixListIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribePrefixListsRequestRequestTypeDef = TypedDict(
    "DescribePrefixListsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "PrefixListIds": Sequence[str],
    },
    total=False,
)

DescribePublicIpv4PoolsRequestDescribePublicIpv4PoolsPaginateTypeDef = TypedDict(
    "DescribePublicIpv4PoolsRequestDescribePublicIpv4PoolsPaginateTypeDef",
    {
        "PoolIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribePublicIpv4PoolsRequestRequestTypeDef = TypedDict(
    "DescribePublicIpv4PoolsRequestRequestTypeDef",
    {
        "PoolIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "Filters": Sequence[FilterTypeDef],
    },
    total=False,
)

DescribeRegionsRequestRequestTypeDef = TypedDict(
    "DescribeRegionsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "RegionNames": Sequence[str],
        "DryRun": bool,
        "AllRegions": bool,
    },
    total=False,
)

DescribeReplaceRootVolumeTasksRequestDescribeReplaceRootVolumeTasksPaginateTypeDef = TypedDict(
    "DescribeReplaceRootVolumeTasksRequestDescribeReplaceRootVolumeTasksPaginateTypeDef",
    {
        "ReplaceRootVolumeTaskIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeReplaceRootVolumeTasksRequestRequestTypeDef = TypedDict(
    "DescribeReplaceRootVolumeTasksRequestRequestTypeDef",
    {
        "ReplaceRootVolumeTaskIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeReservedInstancesListingsRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesListingsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "ReservedInstancesId": str,
        "ReservedInstancesListingId": str,
    },
    total=False,
)

DescribeReservedInstancesModificationsRequestDescribeReservedInstancesModificationsPaginateTypeDef = TypedDict(
    "DescribeReservedInstancesModificationsRequestDescribeReservedInstancesModificationsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "ReservedInstancesModificationIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeReservedInstancesModificationsRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesModificationsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "ReservedInstancesModificationIds": Sequence[str],
        "NextToken": str,
    },
    total=False,
)

DescribeReservedInstancesOfferingsRequestDescribeReservedInstancesOfferingsPaginateTypeDef = TypedDict(
    "DescribeReservedInstancesOfferingsRequestDescribeReservedInstancesOfferingsPaginateTypeDef",
    {
        "AvailabilityZone": str,
        "Filters": Sequence[FilterTypeDef],
        "IncludeMarketplace": bool,
        "InstanceType": InstanceTypeType,
        "MaxDuration": int,
        "MaxInstanceCount": int,
        "MinDuration": int,
        "OfferingClass": OfferingClassTypeType,
        "ProductDescription": RIProductDescriptionType,
        "ReservedInstancesOfferingIds": Sequence[str],
        "DryRun": bool,
        "InstanceTenancy": TenancyType,
        "OfferingType": OfferingTypeValuesType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeReservedInstancesOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesOfferingsRequestRequestTypeDef",
    {
        "AvailabilityZone": str,
        "Filters": Sequence[FilterTypeDef],
        "IncludeMarketplace": bool,
        "InstanceType": InstanceTypeType,
        "MaxDuration": int,
        "MaxInstanceCount": int,
        "MinDuration": int,
        "OfferingClass": OfferingClassTypeType,
        "ProductDescription": RIProductDescriptionType,
        "ReservedInstancesOfferingIds": Sequence[str],
        "DryRun": bool,
        "InstanceTenancy": TenancyType,
        "MaxResults": int,
        "NextToken": str,
        "OfferingType": OfferingTypeValuesType,
    },
    total=False,
)

DescribeReservedInstancesRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "OfferingClass": OfferingClassTypeType,
        "ReservedInstancesIds": Sequence[str],
        "DryRun": bool,
        "OfferingType": OfferingTypeValuesType,
    },
    total=False,
)

DescribeRouteTablesRequestDescribeRouteTablesPaginateTypeDef = TypedDict(
    "DescribeRouteTablesRequestDescribeRouteTablesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "RouteTableIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeRouteTablesRequestRequestTypeDef = TypedDict(
    "DescribeRouteTablesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "RouteTableIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeSecurityGroupRulesRequestDescribeSecurityGroupRulesPaginateTypeDef = TypedDict(
    "DescribeSecurityGroupRulesRequestDescribeSecurityGroupRulesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "SecurityGroupRuleIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSecurityGroupRulesRequestRequestTypeDef = TypedDict(
    "DescribeSecurityGroupRulesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "SecurityGroupRuleIds": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeSecurityGroupsRequestDescribeSecurityGroupsPaginateTypeDef = TypedDict(
    "DescribeSecurityGroupsRequestDescribeSecurityGroupsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "GroupIds": Sequence[str],
        "GroupNames": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSecurityGroupsRequestRequestTypeDef = TypedDict(
    "DescribeSecurityGroupsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "GroupIds": Sequence[str],
        "GroupNames": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeSnapshotTierStatusRequestDescribeSnapshotTierStatusPaginateTypeDef = TypedDict(
    "DescribeSnapshotTierStatusRequestDescribeSnapshotTierStatusPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSnapshotTierStatusRequestRequestTypeDef = TypedDict(
    "DescribeSnapshotTierStatusRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeSnapshotsRequestDescribeSnapshotsPaginateTypeDef = TypedDict(
    "DescribeSnapshotsRequestDescribeSnapshotsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "OwnerIds": Sequence[str],
        "RestorableByUserIds": Sequence[str],
        "SnapshotIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSnapshotsRequestRequestTypeDef = TypedDict(
    "DescribeSnapshotsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "OwnerIds": Sequence[str],
        "RestorableByUserIds": Sequence[str],
        "SnapshotIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

DescribeSpotInstanceRequestsRequestDescribeSpotInstanceRequestsPaginateTypeDef = TypedDict(
    "DescribeSpotInstanceRequestsRequestDescribeSpotInstanceRequestsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "SpotInstanceRequestIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSpotInstanceRequestsRequestRequestTypeDef = TypedDict(
    "DescribeSpotInstanceRequestsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "SpotInstanceRequestIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeSpotPriceHistoryRequestDescribeSpotPriceHistoryPaginateTypeDef = TypedDict(
    "DescribeSpotPriceHistoryRequestDescribeSpotPriceHistoryPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "AvailabilityZone": str,
        "DryRun": bool,
        "EndTime": Union[datetime, str],
        "InstanceTypes": Sequence[InstanceTypeType],
        "ProductDescriptions": Sequence[str],
        "StartTime": Union[datetime, str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSpotPriceHistoryRequestRequestTypeDef = TypedDict(
    "DescribeSpotPriceHistoryRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "AvailabilityZone": str,
        "DryRun": bool,
        "EndTime": Union[datetime, str],
        "InstanceTypes": Sequence[InstanceTypeType],
        "MaxResults": int,
        "NextToken": str,
        "ProductDescriptions": Sequence[str],
        "StartTime": Union[datetime, str],
    },
    total=False,
)

DescribeStoreImageTasksRequestDescribeStoreImageTasksPaginateTypeDef = TypedDict(
    "DescribeStoreImageTasksRequestDescribeStoreImageTasksPaginateTypeDef",
    {
        "ImageIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeStoreImageTasksRequestRequestTypeDef = TypedDict(
    "DescribeStoreImageTasksRequestRequestTypeDef",
    {
        "ImageIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeSubnetsRequestDescribeSubnetsPaginateTypeDef = TypedDict(
    "DescribeSubnetsRequestDescribeSubnetsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "SubnetIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSubnetsRequestRequestTypeDef = TypedDict(
    "DescribeSubnetsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "SubnetIds": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeTagsRequestDescribeTagsPaginateTypeDef = TypedDict(
    "DescribeTagsRequestDescribeTagsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTagsRequestRequestTypeDef = TypedDict(
    "DescribeTagsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeTrafficMirrorFiltersRequestDescribeTrafficMirrorFiltersPaginateTypeDef = TypedDict(
    "DescribeTrafficMirrorFiltersRequestDescribeTrafficMirrorFiltersPaginateTypeDef",
    {
        "TrafficMirrorFilterIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTrafficMirrorFiltersRequestRequestTypeDef = TypedDict(
    "DescribeTrafficMirrorFiltersRequestRequestTypeDef",
    {
        "TrafficMirrorFilterIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeTrafficMirrorSessionsRequestDescribeTrafficMirrorSessionsPaginateTypeDef = TypedDict(
    "DescribeTrafficMirrorSessionsRequestDescribeTrafficMirrorSessionsPaginateTypeDef",
    {
        "TrafficMirrorSessionIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTrafficMirrorSessionsRequestRequestTypeDef = TypedDict(
    "DescribeTrafficMirrorSessionsRequestRequestTypeDef",
    {
        "TrafficMirrorSessionIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeTrafficMirrorTargetsRequestDescribeTrafficMirrorTargetsPaginateTypeDef = TypedDict(
    "DescribeTrafficMirrorTargetsRequestDescribeTrafficMirrorTargetsPaginateTypeDef",
    {
        "TrafficMirrorTargetIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTrafficMirrorTargetsRequestRequestTypeDef = TypedDict(
    "DescribeTrafficMirrorTargetsRequestRequestTypeDef",
    {
        "TrafficMirrorTargetIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeTransitGatewayAttachmentsRequestDescribeTransitGatewayAttachmentsPaginateTypeDef = (
    TypedDict(
        "DescribeTransitGatewayAttachmentsRequestDescribeTransitGatewayAttachmentsPaginateTypeDef",
        {
            "TransitGatewayAttachmentIds": Sequence[str],
            "Filters": Sequence[FilterTypeDef],
            "DryRun": bool,
            "PaginationConfig": PaginatorConfigTypeDef,
        },
        total=False,
    )
)

DescribeTransitGatewayAttachmentsRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayAttachmentsRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewayConnectPeersRequestDescribeTransitGatewayConnectPeersPaginateTypeDef = TypedDict(
    "DescribeTransitGatewayConnectPeersRequestDescribeTransitGatewayConnectPeersPaginateTypeDef",
    {
        "TransitGatewayConnectPeerIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTransitGatewayConnectPeersRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayConnectPeersRequestRequestTypeDef",
    {
        "TransitGatewayConnectPeerIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewayConnectsRequestDescribeTransitGatewayConnectsPaginateTypeDef = TypedDict(
    "DescribeTransitGatewayConnectsRequestDescribeTransitGatewayConnectsPaginateTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTransitGatewayConnectsRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayConnectsRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewayMulticastDomainsRequestDescribeTransitGatewayMulticastDomainsPaginateTypeDef = TypedDict(
    "DescribeTransitGatewayMulticastDomainsRequestDescribeTransitGatewayMulticastDomainsPaginateTypeDef",
    {
        "TransitGatewayMulticastDomainIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTransitGatewayMulticastDomainsRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayMulticastDomainsRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewayPeeringAttachmentsRequestDescribeTransitGatewayPeeringAttachmentsPaginateTypeDef = TypedDict(
    "DescribeTransitGatewayPeeringAttachmentsRequestDescribeTransitGatewayPeeringAttachmentsPaginateTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTransitGatewayPeeringAttachmentsRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayPeeringAttachmentsRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewayRouteTablesRequestDescribeTransitGatewayRouteTablesPaginateTypeDef = (
    TypedDict(
        "DescribeTransitGatewayRouteTablesRequestDescribeTransitGatewayRouteTablesPaginateTypeDef",
        {
            "TransitGatewayRouteTableIds": Sequence[str],
            "Filters": Sequence[FilterTypeDef],
            "DryRun": bool,
            "PaginationConfig": PaginatorConfigTypeDef,
        },
        total=False,
    )
)

DescribeTransitGatewayRouteTablesRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayRouteTablesRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewayVpcAttachmentsRequestDescribeTransitGatewayVpcAttachmentsPaginateTypeDef = TypedDict(
    "DescribeTransitGatewayVpcAttachmentsRequestDescribeTransitGatewayVpcAttachmentsPaginateTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTransitGatewayVpcAttachmentsRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewayVpcAttachmentsRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTransitGatewaysRequestDescribeTransitGatewaysPaginateTypeDef = TypedDict(
    "DescribeTransitGatewaysRequestDescribeTransitGatewaysPaginateTypeDef",
    {
        "TransitGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTransitGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeTransitGatewaysRequestRequestTypeDef",
    {
        "TransitGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeTrunkInterfaceAssociationsRequestDescribeTrunkInterfaceAssociationsPaginateTypeDef = TypedDict(
    "DescribeTrunkInterfaceAssociationsRequestDescribeTrunkInterfaceAssociationsPaginateTypeDef",
    {
        "AssociationIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeTrunkInterfaceAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeTrunkInterfaceAssociationsRequestRequestTypeDef",
    {
        "AssociationIds": Sequence[str],
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeVolumeStatusRequestDescribeVolumeStatusPaginateTypeDef = TypedDict(
    "DescribeVolumeStatusRequestDescribeVolumeStatusPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VolumeIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVolumeStatusRequestRequestTypeDef = TypedDict(
    "DescribeVolumeStatusRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "VolumeIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

DescribeVolumeStatusRequestVolumeDescribeStatusTypeDef = TypedDict(
    "DescribeVolumeStatusRequestVolumeDescribeStatusTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

DescribeVolumesModificationsRequestDescribeVolumesModificationsPaginateTypeDef = TypedDict(
    "DescribeVolumesModificationsRequestDescribeVolumesModificationsPaginateTypeDef",
    {
        "DryRun": bool,
        "VolumeIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVolumesModificationsRequestRequestTypeDef = TypedDict(
    "DescribeVolumesModificationsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "VolumeIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeVolumesRequestDescribeVolumesPaginateTypeDef = TypedDict(
    "DescribeVolumesRequestDescribeVolumesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VolumeIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVolumesRequestRequestTypeDef = TypedDict(
    "DescribeVolumesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VolumeIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeVpcClassicLinkRequestRequestTypeDef = TypedDict(
    "DescribeVpcClassicLinkRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "VpcIds": Sequence[str],
    },
    total=False,
)

DescribeVpcEndpointConnectionNotificationsRequestDescribeVpcEndpointConnectionNotificationsPaginateTypeDef = TypedDict(
    "DescribeVpcEndpointConnectionNotificationsRequestDescribeVpcEndpointConnectionNotificationsPaginateTypeDef",
    {
        "DryRun": bool,
        "ConnectionNotificationId": str,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcEndpointConnectionNotificationsRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointConnectionNotificationsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ConnectionNotificationId": str,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeVpcEndpointConnectionsRequestDescribeVpcEndpointConnectionsPaginateTypeDef = TypedDict(
    "DescribeVpcEndpointConnectionsRequestDescribeVpcEndpointConnectionsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcEndpointConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointConnectionsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeVpcEndpointServiceConfigurationsRequestDescribeVpcEndpointServiceConfigurationsPaginateTypeDef = TypedDict(
    "DescribeVpcEndpointServiceConfigurationsRequestDescribeVpcEndpointServiceConfigurationsPaginateTypeDef",
    {
        "DryRun": bool,
        "ServiceIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcEndpointServiceConfigurationsRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointServiceConfigurationsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ServiceIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

_RequiredDescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef = TypedDict(
    "_RequiredDescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef",
    {
        "ServiceId": str,
    },
)
_OptionalDescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef = TypedDict(
    "_OptionalDescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef(
    _RequiredDescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef,
    _OptionalDescribeVpcEndpointServicePermissionsRequestDescribeVpcEndpointServicePermissionsPaginateTypeDef,
):
    pass


_RequiredDescribeVpcEndpointServicePermissionsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeVpcEndpointServicePermissionsRequestRequestTypeDef",
    {
        "ServiceId": str,
    },
)
_OptionalDescribeVpcEndpointServicePermissionsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeVpcEndpointServicePermissionsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeVpcEndpointServicePermissionsRequestRequestTypeDef(
    _RequiredDescribeVpcEndpointServicePermissionsRequestRequestTypeDef,
    _OptionalDescribeVpcEndpointServicePermissionsRequestRequestTypeDef,
):
    pass


DescribeVpcEndpointServicesRequestDescribeVpcEndpointServicesPaginateTypeDef = TypedDict(
    "DescribeVpcEndpointServicesRequestDescribeVpcEndpointServicesPaginateTypeDef",
    {
        "DryRun": bool,
        "ServiceNames": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcEndpointServicesRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointServicesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ServiceNames": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeVpcEndpointsRequestDescribeVpcEndpointsPaginateTypeDef = TypedDict(
    "DescribeVpcEndpointsRequestDescribeVpcEndpointsPaginateTypeDef",
    {
        "DryRun": bool,
        "VpcEndpointIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcEndpointsRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "VpcEndpointIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeVpcPeeringConnectionsRequestDescribeVpcPeeringConnectionsPaginateTypeDef = TypedDict(
    "DescribeVpcPeeringConnectionsRequestDescribeVpcPeeringConnectionsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "VpcPeeringConnectionIds": Sequence[str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcPeeringConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeVpcPeeringConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "VpcPeeringConnectionIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeVpcsRequestDescribeVpcsPaginateTypeDef = TypedDict(
    "DescribeVpcsRequestDescribeVpcsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpcIds": Sequence[str],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeVpcsRequestRequestTypeDef = TypedDict(
    "DescribeVpcsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpcIds": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeVpnConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeVpnConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpnConnectionIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

DescribeVpnGatewaysRequestRequestTypeDef = TypedDict(
    "DescribeVpnGatewaysRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpnGatewayIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

_RequiredExportTransitGatewayRoutesRequestRequestTypeDef = TypedDict(
    "_RequiredExportTransitGatewayRoutesRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "S3Bucket": str,
    },
)
_OptionalExportTransitGatewayRoutesRequestRequestTypeDef = TypedDict(
    "_OptionalExportTransitGatewayRoutesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class ExportTransitGatewayRoutesRequestRequestTypeDef(
    _RequiredExportTransitGatewayRoutesRequestRequestTypeDef,
    _OptionalExportTransitGatewayRoutesRequestRequestTypeDef,
):
    pass


_RequiredGetCoipPoolUsageRequestRequestTypeDef = TypedDict(
    "_RequiredGetCoipPoolUsageRequestRequestTypeDef",
    {
        "PoolId": str,
    },
)
_OptionalGetCoipPoolUsageRequestRequestTypeDef = TypedDict(
    "_OptionalGetCoipPoolUsageRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class GetCoipPoolUsageRequestRequestTypeDef(
    _RequiredGetCoipPoolUsageRequestRequestTypeDef, _OptionalGetCoipPoolUsageRequestRequestTypeDef
):
    pass


_RequiredGetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef = TypedDict(
    "_RequiredGetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalGetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef = TypedDict(
    "_OptionalGetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef",
    {
        "DryRun": bool,
        "IpamPoolAllocationId": str,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef(
    _RequiredGetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef,
    _OptionalGetIpamPoolAllocationsRequestGetIpamPoolAllocationsPaginateTypeDef,
):
    pass


_RequiredGetIpamPoolAllocationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetIpamPoolAllocationsRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalGetIpamPoolAllocationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetIpamPoolAllocationsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "IpamPoolAllocationId": str,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetIpamPoolAllocationsRequestRequestTypeDef(
    _RequiredGetIpamPoolAllocationsRequestRequestTypeDef,
    _OptionalGetIpamPoolAllocationsRequestRequestTypeDef,
):
    pass


_RequiredGetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef = TypedDict(
    "_RequiredGetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalGetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef = TypedDict(
    "_OptionalGetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef(
    _RequiredGetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef,
    _OptionalGetIpamPoolCidrsRequestGetIpamPoolCidrsPaginateTypeDef,
):
    pass


_RequiredGetIpamPoolCidrsRequestRequestTypeDef = TypedDict(
    "_RequiredGetIpamPoolCidrsRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalGetIpamPoolCidrsRequestRequestTypeDef = TypedDict(
    "_OptionalGetIpamPoolCidrsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetIpamPoolCidrsRequestRequestTypeDef(
    _RequiredGetIpamPoolCidrsRequestRequestTypeDef, _OptionalGetIpamPoolCidrsRequestRequestTypeDef
):
    pass


_RequiredGetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef = TypedDict(
    "_RequiredGetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef",
    {
        "IpamScopeId": str,
    },
)
_OptionalGetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef = TypedDict(
    "_OptionalGetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "IpamPoolId": str,
        "ResourceId": str,
        "ResourceType": IpamResourceTypeType,
        "ResourceTag": RequestIpamResourceTagTypeDef,
        "ResourceOwner": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef(
    _RequiredGetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef,
    _OptionalGetIpamResourceCidrsRequestGetIpamResourceCidrsPaginateTypeDef,
):
    pass


_RequiredGetIpamResourceCidrsRequestRequestTypeDef = TypedDict(
    "_RequiredGetIpamResourceCidrsRequestRequestTypeDef",
    {
        "IpamScopeId": str,
    },
)
_OptionalGetIpamResourceCidrsRequestRequestTypeDef = TypedDict(
    "_OptionalGetIpamResourceCidrsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "IpamPoolId": str,
        "ResourceId": str,
        "ResourceType": IpamResourceTypeType,
        "ResourceTag": RequestIpamResourceTagTypeDef,
        "ResourceOwner": str,
    },
    total=False,
)


class GetIpamResourceCidrsRequestRequestTypeDef(
    _RequiredGetIpamResourceCidrsRequestRequestTypeDef,
    _OptionalGetIpamResourceCidrsRequestRequestTypeDef,
):
    pass


_RequiredGetSubnetCidrReservationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetSubnetCidrReservationsRequestRequestTypeDef",
    {
        "SubnetId": str,
    },
)
_OptionalGetSubnetCidrReservationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetSubnetCidrReservationsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class GetSubnetCidrReservationsRequestRequestTypeDef(
    _RequiredGetSubnetCidrReservationsRequestRequestTypeDef,
    _OptionalGetSubnetCidrReservationsRequestRequestTypeDef,
):
    pass


_RequiredGetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef = TypedDict(
    "_RequiredGetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalGetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef = TypedDict(
    "_OptionalGetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef(
    _RequiredGetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef,
    _OptionalGetTransitGatewayAttachmentPropagationsRequestGetTransitGatewayAttachmentPropagationsPaginateTypeDef,
):
    pass


_RequiredGetTransitGatewayAttachmentPropagationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetTransitGatewayAttachmentPropagationsRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalGetTransitGatewayAttachmentPropagationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetTransitGatewayAttachmentPropagationsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class GetTransitGatewayAttachmentPropagationsRequestRequestTypeDef(
    _RequiredGetTransitGatewayAttachmentPropagationsRequestRequestTypeDef,
    _OptionalGetTransitGatewayAttachmentPropagationsRequestRequestTypeDef,
):
    pass


GetTransitGatewayMulticastDomainAssociationsRequestGetTransitGatewayMulticastDomainAssociationsPaginateTypeDef = TypedDict(
    "GetTransitGatewayMulticastDomainAssociationsRequestGetTransitGatewayMulticastDomainAssociationsPaginateTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef = TypedDict(
    "GetTransitGatewayMulticastDomainAssociationsRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

_RequiredGetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef = TypedDict(
    "_RequiredGetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalGetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef = TypedDict(
    "_OptionalGetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef(
    _RequiredGetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef,
    _OptionalGetTransitGatewayPrefixListReferencesRequestGetTransitGatewayPrefixListReferencesPaginateTypeDef,
):
    pass


_RequiredGetTransitGatewayPrefixListReferencesRequestRequestTypeDef = TypedDict(
    "_RequiredGetTransitGatewayPrefixListReferencesRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalGetTransitGatewayPrefixListReferencesRequestRequestTypeDef = TypedDict(
    "_OptionalGetTransitGatewayPrefixListReferencesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class GetTransitGatewayPrefixListReferencesRequestRequestTypeDef(
    _RequiredGetTransitGatewayPrefixListReferencesRequestRequestTypeDef,
    _OptionalGetTransitGatewayPrefixListReferencesRequestRequestTypeDef,
):
    pass


_RequiredGetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef = TypedDict(
    "_RequiredGetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalGetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef = TypedDict(
    "_OptionalGetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef(
    _RequiredGetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef,
    _OptionalGetTransitGatewayRouteTableAssociationsRequestGetTransitGatewayRouteTableAssociationsPaginateTypeDef,
):
    pass


_RequiredGetTransitGatewayRouteTableAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetTransitGatewayRouteTableAssociationsRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalGetTransitGatewayRouteTableAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetTransitGatewayRouteTableAssociationsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class GetTransitGatewayRouteTableAssociationsRequestRequestTypeDef(
    _RequiredGetTransitGatewayRouteTableAssociationsRequestRequestTypeDef,
    _OptionalGetTransitGatewayRouteTableAssociationsRequestRequestTypeDef,
):
    pass


_RequiredGetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef = TypedDict(
    "_RequiredGetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalGetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef = TypedDict(
    "_OptionalGetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef(
    _RequiredGetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef,
    _OptionalGetTransitGatewayRouteTablePropagationsRequestGetTransitGatewayRouteTablePropagationsPaginateTypeDef,
):
    pass


_RequiredGetTransitGatewayRouteTablePropagationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetTransitGatewayRouteTablePropagationsRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
    },
)
_OptionalGetTransitGatewayRouteTablePropagationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetTransitGatewayRouteTablePropagationsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class GetTransitGatewayRouteTablePropagationsRequestRequestTypeDef(
    _RequiredGetTransitGatewayRouteTablePropagationsRequestRequestTypeDef,
    _OptionalGetTransitGatewayRouteTablePropagationsRequestRequestTypeDef,
):
    pass


_RequiredSearchLocalGatewayRoutesRequestRequestTypeDef = TypedDict(
    "_RequiredSearchLocalGatewayRoutesRequestRequestTypeDef",
    {
        "LocalGatewayRouteTableId": str,
    },
)
_OptionalSearchLocalGatewayRoutesRequestRequestTypeDef = TypedDict(
    "_OptionalSearchLocalGatewayRoutesRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)


class SearchLocalGatewayRoutesRequestRequestTypeDef(
    _RequiredSearchLocalGatewayRoutesRequestRequestTypeDef,
    _OptionalSearchLocalGatewayRoutesRequestRequestTypeDef,
):
    pass


_RequiredSearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef = TypedDict(
    "_RequiredSearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef",
    {
        "LocalGatewayRouteTableId": str,
    },
)
_OptionalSearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef = TypedDict(
    "_OptionalSearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class SearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef(
    _RequiredSearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef,
    _OptionalSearchLocalGatewayRoutesRequestSearchLocalGatewayRoutesPaginateTypeDef,
):
    pass


SearchTransitGatewayMulticastGroupsRequestRequestTypeDef = TypedDict(
    "SearchTransitGatewayMulticastGroupsRequestRequestTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
    },
    total=False,
)

SearchTransitGatewayMulticastGroupsRequestSearchTransitGatewayMulticastGroupsPaginateTypeDef = TypedDict(
    "SearchTransitGatewayMulticastGroupsRequestSearchTransitGatewayMulticastGroupsPaginateTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredSearchTransitGatewayRoutesRequestRequestTypeDef = TypedDict(
    "_RequiredSearchTransitGatewayRoutesRequestRequestTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "Filters": Sequence[FilterTypeDef],
    },
)
_OptionalSearchTransitGatewayRoutesRequestRequestTypeDef = TypedDict(
    "_OptionalSearchTransitGatewayRoutesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "DryRun": bool,
    },
    total=False,
)


class SearchTransitGatewayRoutesRequestRequestTypeDef(
    _RequiredSearchTransitGatewayRoutesRequestRequestTypeDef,
    _OptionalSearchTransitGatewayRoutesRequestRequestTypeDef,
):
    pass


DescribeAggregateIdFormatResultTypeDef = TypedDict(
    "DescribeAggregateIdFormatResultTypeDef",
    {
        "UseLongIdsAggregated": bool,
        "Statuses": List[IdFormatTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIdFormatResultTypeDef = TypedDict(
    "DescribeIdFormatResultTypeDef",
    {
        "Statuses": List[IdFormatTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIdentityIdFormatResultTypeDef = TypedDict(
    "DescribeIdentityIdFormatResultTypeDef",
    {
        "Statuses": List[IdFormatTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PrincipalIdFormatTypeDef = TypedDict(
    "PrincipalIdFormatTypeDef",
    {
        "Arn": str,
        "Statuses": List[IdFormatTypeDef],
    },
    total=False,
)

DescribeBundleTasksRequestBundleTaskCompleteWaitTypeDef = TypedDict(
    "DescribeBundleTasksRequestBundleTaskCompleteWaitTypeDef",
    {
        "BundleIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeConversionTasksRequestConversionTaskCancelledWaitTypeDef = TypedDict(
    "DescribeConversionTasksRequestConversionTaskCancelledWaitTypeDef",
    {
        "ConversionTaskIds": Sequence[str],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeConversionTasksRequestConversionTaskCompletedWaitTypeDef = TypedDict(
    "DescribeConversionTasksRequestConversionTaskCompletedWaitTypeDef",
    {
        "ConversionTaskIds": Sequence[str],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeConversionTasksRequestConversionTaskDeletedWaitTypeDef = TypedDict(
    "DescribeConversionTasksRequestConversionTaskDeletedWaitTypeDef",
    {
        "ConversionTaskIds": Sequence[str],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeCustomerGatewaysRequestCustomerGatewayAvailableWaitTypeDef = TypedDict(
    "DescribeCustomerGatewaysRequestCustomerGatewayAvailableWaitTypeDef",
    {
        "CustomerGatewayIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeExportTasksRequestExportTaskCancelledWaitTypeDef = TypedDict(
    "DescribeExportTasksRequestExportTaskCancelledWaitTypeDef",
    {
        "ExportTaskIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeExportTasksRequestExportTaskCompletedWaitTypeDef = TypedDict(
    "DescribeExportTasksRequestExportTaskCompletedWaitTypeDef",
    {
        "ExportTaskIds": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeImagesRequestImageAvailableWaitTypeDef = TypedDict(
    "DescribeImagesRequestImageAvailableWaitTypeDef",
    {
        "ExecutableUsers": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "ImageIds": Sequence[str],
        "Owners": Sequence[str],
        "IncludeDeprecated": bool,
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeImagesRequestImageExistsWaitTypeDef = TypedDict(
    "DescribeImagesRequestImageExistsWaitTypeDef",
    {
        "ExecutableUsers": Sequence[str],
        "Filters": Sequence[FilterTypeDef],
        "ImageIds": Sequence[str],
        "Owners": Sequence[str],
        "IncludeDeprecated": bool,
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInstanceStatusRequestInstanceStatusOkWaitTypeDef = TypedDict(
    "DescribeInstanceStatusRequestInstanceStatusOkWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
        "IncludeAllInstances": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInstanceStatusRequestSystemStatusOkWaitTypeDef = TypedDict(
    "DescribeInstanceStatusRequestSystemStatusOkWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
        "DryRun": bool,
        "IncludeAllInstances": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInstancesRequestInstanceExistsWaitTypeDef = TypedDict(
    "DescribeInstancesRequestInstanceExistsWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInstancesRequestInstanceRunningWaitTypeDef = TypedDict(
    "DescribeInstancesRequestInstanceRunningWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInstancesRequestInstanceStoppedWaitTypeDef = TypedDict(
    "DescribeInstancesRequestInstanceStoppedWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInstancesRequestInstanceTerminatedWaitTypeDef = TypedDict(
    "DescribeInstancesRequestInstanceTerminatedWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "InstanceIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeInternetGatewaysRequestInternetGatewayExistsWaitTypeDef = TypedDict(
    "DescribeInternetGatewaysRequestInternetGatewayExistsWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "InternetGatewayIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeKeyPairsRequestKeyPairExistsWaitTypeDef = TypedDict(
    "DescribeKeyPairsRequestKeyPairExistsWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "KeyNames": Sequence[str],
        "KeyPairIds": Sequence[str],
        "DryRun": bool,
        "IncludePublicKey": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeNatGatewaysRequestNatGatewayAvailableWaitTypeDef = TypedDict(
    "DescribeNatGatewaysRequestNatGatewayAvailableWaitTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NatGatewayIds": Sequence[str],
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeNatGatewaysRequestNatGatewayDeletedWaitTypeDef = TypedDict(
    "DescribeNatGatewaysRequestNatGatewayDeletedWaitTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NatGatewayIds": Sequence[str],
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeNetworkInterfacesRequestNetworkInterfaceAvailableWaitTypeDef = TypedDict(
    "DescribeNetworkInterfacesRequestNetworkInterfaceAvailableWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "NetworkInterfaceIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeSecurityGroupsRequestSecurityGroupExistsWaitTypeDef = TypedDict(
    "DescribeSecurityGroupsRequestSecurityGroupExistsWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "GroupIds": Sequence[str],
        "GroupNames": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeSnapshotsRequestSnapshotCompletedWaitTypeDef = TypedDict(
    "DescribeSnapshotsRequestSnapshotCompletedWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "OwnerIds": Sequence[str],
        "RestorableByUserIds": Sequence[str],
        "SnapshotIds": Sequence[str],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeSpotInstanceRequestsRequestSpotInstanceRequestFulfilledWaitTypeDef = TypedDict(
    "DescribeSpotInstanceRequestsRequestSpotInstanceRequestFulfilledWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "SpotInstanceRequestIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeSubnetsRequestSubnetAvailableWaitTypeDef = TypedDict(
    "DescribeSubnetsRequestSubnetAvailableWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "SubnetIds": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVolumesRequestVolumeAvailableWaitTypeDef = TypedDict(
    "DescribeVolumesRequestVolumeAvailableWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VolumeIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVolumesRequestVolumeDeletedWaitTypeDef = TypedDict(
    "DescribeVolumesRequestVolumeDeletedWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VolumeIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVolumesRequestVolumeInUseWaitTypeDef = TypedDict(
    "DescribeVolumesRequestVolumeInUseWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VolumeIds": Sequence[str],
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVpcPeeringConnectionsRequestVpcPeeringConnectionDeletedWaitTypeDef = TypedDict(
    "DescribeVpcPeeringConnectionsRequestVpcPeeringConnectionDeletedWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "VpcPeeringConnectionIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVpcPeeringConnectionsRequestVpcPeeringConnectionExistsWaitTypeDef = TypedDict(
    "DescribeVpcPeeringConnectionsRequestVpcPeeringConnectionExistsWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "DryRun": bool,
        "VpcPeeringConnectionIds": Sequence[str],
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVpcsRequestVpcAvailableWaitTypeDef = TypedDict(
    "DescribeVpcsRequestVpcAvailableWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpcIds": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVpcsRequestVpcExistsWaitTypeDef = TypedDict(
    "DescribeVpcsRequestVpcExistsWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpcIds": Sequence[str],
        "DryRun": bool,
        "NextToken": str,
        "MaxResults": int,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVpnConnectionsRequestVpnConnectionAvailableWaitTypeDef = TypedDict(
    "DescribeVpnConnectionsRequestVpnConnectionAvailableWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpnConnectionIds": Sequence[str],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeVpnConnectionsRequestVpnConnectionDeletedWaitTypeDef = TypedDict(
    "DescribeVpnConnectionsRequestVpnConnectionDeletedWaitTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "VpnConnectionIds": Sequence[str],
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

_RequiredGetPasswordDataRequestPasswordDataAvailableWaitTypeDef = TypedDict(
    "_RequiredGetPasswordDataRequestPasswordDataAvailableWaitTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalGetPasswordDataRequestPasswordDataAvailableWaitTypeDef = TypedDict(
    "_OptionalGetPasswordDataRequestPasswordDataAvailableWaitTypeDef",
    {
        "DryRun": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)


class GetPasswordDataRequestPasswordDataAvailableWaitTypeDef(
    _RequiredGetPasswordDataRequestPasswordDataAvailableWaitTypeDef,
    _OptionalGetPasswordDataRequestPasswordDataAvailableWaitTypeDef,
):
    pass


DescribeFastLaunchImagesSuccessItemTypeDef = TypedDict(
    "DescribeFastLaunchImagesSuccessItemTypeDef",
    {
        "ImageId": str,
        "ResourceType": Literal["snapshot"],
        "SnapshotConfiguration": FastLaunchSnapshotConfigurationResponseTypeDef,
        "LaunchTemplate": FastLaunchLaunchTemplateSpecificationResponseTypeDef,
        "MaxParallelLaunches": int,
        "OwnerId": str,
        "State": FastLaunchStateCodeType,
        "StateTransitionReason": str,
        "StateTransitionTime": datetime,
    },
    total=False,
)

DisableFastLaunchResultTypeDef = TypedDict(
    "DisableFastLaunchResultTypeDef",
    {
        "ImageId": str,
        "ResourceType": Literal["snapshot"],
        "SnapshotConfiguration": FastLaunchSnapshotConfigurationResponseTypeDef,
        "LaunchTemplate": FastLaunchLaunchTemplateSpecificationResponseTypeDef,
        "MaxParallelLaunches": int,
        "OwnerId": str,
        "State": FastLaunchStateCodeType,
        "StateTransitionReason": str,
        "StateTransitionTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableFastLaunchResultTypeDef = TypedDict(
    "EnableFastLaunchResultTypeDef",
    {
        "ImageId": str,
        "ResourceType": Literal["snapshot"],
        "SnapshotConfiguration": FastLaunchSnapshotConfigurationResponseTypeDef,
        "LaunchTemplate": FastLaunchLaunchTemplateSpecificationResponseTypeDef,
        "MaxParallelLaunches": int,
        "OwnerId": str,
        "State": FastLaunchStateCodeType,
        "StateTransitionReason": str,
        "StateTransitionTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFastSnapshotRestoresResultTypeDef = TypedDict(
    "DescribeFastSnapshotRestoresResultTypeDef",
    {
        "FastSnapshotRestores": List[DescribeFastSnapshotRestoreSuccessItemTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeHostReservationOfferingsResultTypeDef = TypedDict(
    "DescribeHostReservationOfferingsResultTypeDef",
    {
        "NextToken": str,
        "OfferingSet": List[HostOfferingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInstanceCreditSpecificationsResultTypeDef = TypedDict(
    "DescribeInstanceCreditSpecificationsResultTypeDef",
    {
        "InstanceCreditSpecifications": List[InstanceCreditSpecificationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInstanceTypeOfferingsResultTypeDef = TypedDict(
    "DescribeInstanceTypeOfferingsResultTypeDef",
    {
        "InstanceTypeOfferings": List[InstanceTypeOfferingTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeMovingAddressesResultTypeDef = TypedDict(
    "DescribeMovingAddressesResultTypeDef",
    {
        "MovingAddressStatuses": List[MovingAddressStatusTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInterfaceAttributeResultTypeDef = TypedDict(
    "DescribeNetworkInterfaceAttributeResultTypeDef",
    {
        "Attachment": NetworkInterfaceAttachmentTypeDef,
        "Description": AttributeValueTypeDef,
        "Groups": List[GroupIdentifierTypeDef],
        "NetworkInterfaceId": str,
        "SourceDestCheck": AttributeBooleanValueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePrefixListsResultTypeDef = TypedDict(
    "DescribePrefixListsResultTypeDef",
    {
        "NextToken": str,
        "PrefixLists": List[PrefixListTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRegionsResultTypeDef = TypedDict(
    "DescribeRegionsResultTypeDef",
    {
        "Regions": List[RegionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredDescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef = TypedDict(
    "_RequiredDescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef",
    {
        "FirstSlotStartTimeRange": SlotDateTimeRangeRequestTypeDef,
        "Recurrence": ScheduledInstanceRecurrenceRequestTypeDef,
    },
)
_OptionalDescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef = TypedDict(
    "_OptionalDescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxSlotDurationInHours": int,
        "MinSlotDurationInHours": int,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef(
    _RequiredDescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef,
    _OptionalDescribeScheduledInstanceAvailabilityRequestDescribeScheduledInstanceAvailabilityPaginateTypeDef,
):
    pass


_RequiredDescribeScheduledInstanceAvailabilityRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeScheduledInstanceAvailabilityRequestRequestTypeDef",
    {
        "FirstSlotStartTimeRange": SlotDateTimeRangeRequestTypeDef,
        "Recurrence": ScheduledInstanceRecurrenceRequestTypeDef,
    },
)
_OptionalDescribeScheduledInstanceAvailabilityRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeScheduledInstanceAvailabilityRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "MaxSlotDurationInHours": int,
        "MinSlotDurationInHours": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeScheduledInstanceAvailabilityRequestRequestTypeDef(
    _RequiredDescribeScheduledInstanceAvailabilityRequestRequestTypeDef,
    _OptionalDescribeScheduledInstanceAvailabilityRequestRequestTypeDef,
):
    pass


DescribeScheduledInstancesRequestDescribeScheduledInstancesPaginateTypeDef = TypedDict(
    "DescribeScheduledInstancesRequestDescribeScheduledInstancesPaginateTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "ScheduledInstanceIds": Sequence[str],
        "SlotStartTimeRange": SlotStartTimeRangeRequestTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeScheduledInstancesRequestRequestTypeDef = TypedDict(
    "DescribeScheduledInstancesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "ScheduledInstanceIds": Sequence[str],
        "SlotStartTimeRange": SlotStartTimeRangeRequestTypeDef,
    },
    total=False,
)

DescribeSecurityGroupReferencesResultTypeDef = TypedDict(
    "DescribeSecurityGroupReferencesResultTypeDef",
    {
        "SecurityGroupReferenceSet": List[SecurityGroupReferenceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSnapshotAttributeResultTypeDef = TypedDict(
    "DescribeSnapshotAttributeResultTypeDef",
    {
        "CreateVolumePermissions": List[CreateVolumePermissionTypeDef],
        "ProductCodes": List[ProductCodeTypeDef],
        "SnapshotId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVolumeAttributeResultTypeDef = TypedDict(
    "DescribeVolumeAttributeResultTypeDef",
    {
        "AutoEnableIO": AttributeBooleanValueTypeDef,
        "ProductCodes": List[ProductCodeTypeDef],
        "VolumeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpotPriceHistoryResultTypeDef = TypedDict(
    "DescribeSpotPriceHistoryResultTypeDef",
    {
        "NextToken": str,
        "SpotPriceHistory": List[SpotPriceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStoreImageTasksResultTypeDef = TypedDict(
    "DescribeStoreImageTasksResultTypeDef",
    {
        "StoreImageTaskResults": List[StoreImageTaskResultTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTagsResultTypeDef = TypedDict(
    "DescribeTagsResultTypeDef",
    {
        "NextToken": str,
        "Tags": List[TagDescriptionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVolumesModificationsResultTypeDef = TypedDict(
    "DescribeVolumesModificationsResultTypeDef",
    {
        "VolumesModifications": List[VolumeModificationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVolumeResultTypeDef = TypedDict(
    "ModifyVolumeResultTypeDef",
    {
        "VolumeModification": VolumeModificationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FlowLogTypeDef = TypedDict(
    "FlowLogTypeDef",
    {
        "CreationTime": datetime,
        "DeliverLogsErrorMessage": str,
        "DeliverLogsPermissionArn": str,
        "DeliverLogsStatus": str,
        "FlowLogId": str,
        "FlowLogStatus": str,
        "LogGroupName": str,
        "ResourceId": str,
        "TrafficType": TrafficTypeType,
        "LogDestinationType": LogDestinationTypeType,
        "LogDestination": str,
        "LogFormat": str,
        "Tags": List[TagTypeDef],
        "MaxAggregationInterval": int,
        "DestinationOptions": DestinationOptionsResponseTypeDef,
    },
    total=False,
)

DisableFastSnapshotRestoreStateErrorItemTypeDef = TypedDict(
    "DisableFastSnapshotRestoreStateErrorItemTypeDef",
    {
        "AvailabilityZone": str,
        "Error": DisableFastSnapshotRestoreStateErrorTypeDef,
    },
    total=False,
)

DisableTransitGatewayRouteTablePropagationResultTypeDef = TypedDict(
    "DisableTransitGatewayRouteTablePropagationResultTypeDef",
    {
        "Propagation": TransitGatewayPropagationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableTransitGatewayRouteTablePropagationResultTypeDef = TypedDict(
    "EnableTransitGatewayRouteTablePropagationResultTypeDef",
    {
        "Propagation": TransitGatewayPropagationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DiskImageTypeDef = TypedDict(
    "DiskImageTypeDef",
    {
        "Description": str,
        "Image": DiskImageDetailTypeDef,
        "Volume": VolumeDetailTypeDef,
    },
    total=False,
)

_RequiredImportVolumeRequestRequestTypeDef = TypedDict(
    "_RequiredImportVolumeRequestRequestTypeDef",
    {
        "AvailabilityZone": str,
        "Image": DiskImageDetailTypeDef,
        "Volume": VolumeDetailTypeDef,
    },
)
_OptionalImportVolumeRequestRequestTypeDef = TypedDict(
    "_OptionalImportVolumeRequestRequestTypeDef",
    {
        "Description": str,
        "DryRun": bool,
    },
    total=False,
)


class ImportVolumeRequestRequestTypeDef(
    _RequiredImportVolumeRequestRequestTypeDef, _OptionalImportVolumeRequestRequestTypeDef
):
    pass


ImportInstanceVolumeDetailItemTypeDef = TypedDict(
    "ImportInstanceVolumeDetailItemTypeDef",
    {
        "AvailabilityZone": str,
        "BytesConverted": int,
        "Description": str,
        "Image": DiskImageDescriptionTypeDef,
        "Status": str,
        "StatusMessage": str,
        "Volume": DiskImageVolumeDescriptionTypeDef,
    },
    total=False,
)

ImportVolumeTaskDetailsTypeDef = TypedDict(
    "ImportVolumeTaskDetailsTypeDef",
    {
        "AvailabilityZone": str,
        "BytesConverted": int,
        "Description": str,
        "Image": DiskImageDescriptionTypeDef,
        "Volume": DiskImageVolumeDescriptionTypeDef,
    },
    total=False,
)

InstanceStorageInfoTypeDef = TypedDict(
    "InstanceStorageInfoTypeDef",
    {
        "TotalSizeInGB": int,
        "Disks": List[DiskInfoTypeDef],
        "NvmeSupport": EphemeralNvmeSupportType,
        "EncryptionSupport": InstanceStorageEncryptionSupportType,
    },
    total=False,
)

VpcEndpointConnectionTypeDef = TypedDict(
    "VpcEndpointConnectionTypeDef",
    {
        "ServiceId": str,
        "VpcEndpointId": str,
        "VpcEndpointOwner": str,
        "VpcEndpointState": StateType,
        "CreationTimestamp": datetime,
        "DnsEntries": List[DnsEntryTypeDef],
        "NetworkLoadBalancerArns": List[str],
        "GatewayLoadBalancerArns": List[str],
        "IpAddressType": IpAddressTypeType,
    },
    total=False,
)

_RequiredModifyClientVpnEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredModifyClientVpnEndpointRequestRequestTypeDef",
    {
        "ClientVpnEndpointId": str,
    },
)
_OptionalModifyClientVpnEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalModifyClientVpnEndpointRequestRequestTypeDef",
    {
        "ServerCertificateArn": str,
        "ConnectionLogOptions": ConnectionLogOptionsTypeDef,
        "DnsServers": DnsServersOptionsModifyStructureTypeDef,
        "VpnPort": int,
        "Description": str,
        "SplitTunnel": bool,
        "DryRun": bool,
        "SecurityGroupIds": Sequence[str],
        "VpcId": str,
        "SelfServicePortal": SelfServicePortalType,
        "ClientConnectOptions": ClientConnectOptionsTypeDef,
        "SessionTimeoutHours": int,
        "ClientLoginBannerOptions": ClientLoginBannerOptionsTypeDef,
    },
    total=False,
)


class ModifyClientVpnEndpointRequestRequestTypeDef(
    _RequiredModifyClientVpnEndpointRequestRequestTypeDef,
    _OptionalModifyClientVpnEndpointRequestRequestTypeDef,
):
    pass


EbsInfoTypeDef = TypedDict(
    "EbsInfoTypeDef",
    {
        "EbsOptimizedSupport": EbsOptimizedSupportType,
        "EncryptionSupport": EbsEncryptionSupportType,
        "EbsOptimizedInfo": EbsOptimizedInfoTypeDef,
        "NvmeSupport": EbsNvmeSupportType,
    },
    total=False,
)

InstanceBlockDeviceMappingSpecificationTypeDef = TypedDict(
    "InstanceBlockDeviceMappingSpecificationTypeDef",
    {
        "DeviceName": str,
        "Ebs": EbsInstanceBlockDeviceSpecificationTypeDef,
        "NoDevice": str,
        "VirtualName": str,
    },
    total=False,
)

InstanceBlockDeviceMappingTypeDef = TypedDict(
    "InstanceBlockDeviceMappingTypeDef",
    {
        "DeviceName": str,
        "Ebs": EbsInstanceBlockDeviceTypeDef,
    },
    total=False,
)

EgressOnlyInternetGatewayTypeDef = TypedDict(
    "EgressOnlyInternetGatewayTypeDef",
    {
        "Attachments": List[InternetGatewayAttachmentTypeDef],
        "EgressOnlyInternetGatewayId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

InternetGatewayTypeDef = TypedDict(
    "InternetGatewayTypeDef",
    {
        "Attachments": List[InternetGatewayAttachmentTypeDef],
        "InternetGatewayId": str,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ElasticGpusTypeDef = TypedDict(
    "ElasticGpusTypeDef",
    {
        "ElasticGpuId": str,
        "AvailabilityZone": str,
        "ElasticGpuType": str,
        "ElasticGpuHealth": ElasticGpuHealthTypeDef,
        "ElasticGpuState": Literal["ATTACHED"],
        "InstanceId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredEnableFastLaunchRequestRequestTypeDef = TypedDict(
    "_RequiredEnableFastLaunchRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalEnableFastLaunchRequestRequestTypeDef = TypedDict(
    "_OptionalEnableFastLaunchRequestRequestTypeDef",
    {
        "ResourceType": str,
        "SnapshotConfiguration": FastLaunchSnapshotConfigurationRequestTypeDef,
        "LaunchTemplate": FastLaunchLaunchTemplateSpecificationRequestTypeDef,
        "MaxParallelLaunches": int,
        "DryRun": bool,
    },
    total=False,
)


class EnableFastLaunchRequestRequestTypeDef(
    _RequiredEnableFastLaunchRequestRequestTypeDef, _OptionalEnableFastLaunchRequestRequestTypeDef
):
    pass


EnableFastSnapshotRestoreStateErrorItemTypeDef = TypedDict(
    "EnableFastSnapshotRestoreStateErrorItemTypeDef",
    {
        "AvailabilityZone": str,
        "Error": EnableFastSnapshotRestoreStateErrorTypeDef,
    },
    total=False,
)

HistoryRecordEntryTypeDef = TypedDict(
    "HistoryRecordEntryTypeDef",
    {
        "EventInformation": EventInformationTypeDef,
        "EventType": FleetEventTypeType,
        "Timestamp": datetime,
    },
    total=False,
)

HistoryRecordTypeDef = TypedDict(
    "HistoryRecordTypeDef",
    {
        "EventInformation": EventInformationTypeDef,
        "EventType": EventTypeType,
        "Timestamp": datetime,
    },
    total=False,
)

ExportImageResultTypeDef = TypedDict(
    "ExportImageResultTypeDef",
    {
        "Description": str,
        "DiskImageFormat": DiskImageFormatType,
        "ExportImageTaskId": str,
        "ImageId": str,
        "RoleName": str,
        "Progress": str,
        "S3ExportLocation": ExportTaskS3LocationTypeDef,
        "Status": str,
        "StatusMessage": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportImageTaskTypeDef = TypedDict(
    "ExportImageTaskTypeDef",
    {
        "Description": str,
        "ExportImageTaskId": str,
        "ImageId": str,
        "Progress": str,
        "S3ExportLocation": ExportTaskS3LocationTypeDef,
        "Status": str,
        "StatusMessage": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ExportTaskTypeDef = TypedDict(
    "ExportTaskTypeDef",
    {
        "Description": str,
        "ExportTaskId": str,
        "ExportToS3Task": ExportToS3TaskTypeDef,
        "InstanceExportDetails": InstanceExportDetailsTypeDef,
        "State": ExportTaskStateType,
        "StatusMessage": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

FleetSpotMaintenanceStrategiesRequestTypeDef = TypedDict(
    "FleetSpotMaintenanceStrategiesRequestTypeDef",
    {
        "CapacityRebalance": FleetSpotCapacityRebalanceRequestTypeDef,
    },
    total=False,
)

FleetSpotMaintenanceStrategiesTypeDef = TypedDict(
    "FleetSpotMaintenanceStrategiesTypeDef",
    {
        "CapacityRebalance": FleetSpotCapacityRebalanceTypeDef,
    },
    total=False,
)

FpgaDeviceInfoTypeDef = TypedDict(
    "FpgaDeviceInfoTypeDef",
    {
        "Name": str,
        "Manufacturer": str,
        "Count": int,
        "MemoryInfo": FpgaDeviceMemoryInfoTypeDef,
    },
    total=False,
)

FpgaImageAttributeTypeDef = TypedDict(
    "FpgaImageAttributeTypeDef",
    {
        "FpgaImageId": str,
        "Name": str,
        "Description": str,
        "LoadPermissions": List[LoadPermissionTypeDef],
        "ProductCodes": List[ProductCodeTypeDef],
    },
    total=False,
)

FpgaImageTypeDef = TypedDict(
    "FpgaImageTypeDef",
    {
        "FpgaImageId": str,
        "FpgaImageGlobalId": str,
        "Name": str,
        "Description": str,
        "ShellVersion": str,
        "PciId": PciIdTypeDef,
        "State": FpgaImageStateTypeDef,
        "CreateTime": datetime,
        "UpdateTime": datetime,
        "OwnerId": str,
        "OwnerAlias": str,
        "ProductCodes": List[ProductCodeTypeDef],
        "Tags": List[TagTypeDef],
        "Public": bool,
        "DataRetentionSupport": bool,
    },
    total=False,
)

GetAssociatedIpv6PoolCidrsResultTypeDef = TypedDict(
    "GetAssociatedIpv6PoolCidrsResultTypeDef",
    {
        "Ipv6CidrAssociations": List[Ipv6CidrAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCapacityReservationUsageResultTypeDef = TypedDict(
    "GetCapacityReservationUsageResultTypeDef",
    {
        "NextToken": str,
        "CapacityReservationId": str,
        "InstanceType": str,
        "TotalInstanceCount": int,
        "AvailableInstanceCount": int,
        "State": CapacityReservationStateType,
        "InstanceUsages": List[InstanceUsageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDefaultCreditSpecificationResultTypeDef = TypedDict(
    "GetDefaultCreditSpecificationResultTypeDef",
    {
        "InstanceFamilyCreditSpecification": InstanceFamilyCreditSpecificationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyDefaultCreditSpecificationResultTypeDef = TypedDict(
    "ModifyDefaultCreditSpecificationResultTypeDef",
    {
        "InstanceFamilyCreditSpecification": InstanceFamilyCreditSpecificationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetHostReservationPurchasePreviewResultTypeDef = TypedDict(
    "GetHostReservationPurchasePreviewResultTypeDef",
    {
        "CurrencyCode": Literal["USD"],
        "Purchase": List[PurchaseTypeDef],
        "TotalHourlyPrice": str,
        "TotalUpfrontPrice": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PurchaseHostReservationResultTypeDef = TypedDict(
    "PurchaseHostReservationResultTypeDef",
    {
        "ClientToken": str,
        "CurrencyCode": Literal["USD"],
        "Purchase": List[PurchaseTypeDef],
        "TotalHourlyPrice": str,
        "TotalUpfrontPrice": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstanceTypesFromInstanceRequirementsResultTypeDef = TypedDict(
    "GetInstanceTypesFromInstanceRequirementsResultTypeDef",
    {
        "InstanceTypes": List[InstanceTypeInfoFromInstanceRequirementsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetIpamAddressHistoryResultTypeDef = TypedDict(
    "GetIpamAddressHistoryResultTypeDef",
    {
        "HistoryRecords": List[IpamAddressHistoryRecordTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetManagedPrefixListAssociationsResultTypeDef = TypedDict(
    "GetManagedPrefixListAssociationsResultTypeDef",
    {
        "PrefixListAssociations": List[PrefixListAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetManagedPrefixListEntriesResultTypeDef = TypedDict(
    "GetManagedPrefixListEntriesResultTypeDef",
    {
        "Entries": List[PrefixListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReservedInstanceReservationValueTypeDef = TypedDict(
    "ReservedInstanceReservationValueTypeDef",
    {
        "ReservationValue": ReservationValueTypeDef,
        "ReservedInstanceId": str,
    },
    total=False,
)

GetSpotPlacementScoresResultTypeDef = TypedDict(
    "GetSpotPlacementScoresResultTypeDef",
    {
        "SpotPlacementScores": List[SpotPlacementScoreTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayAttachmentPropagationsResultTypeDef = TypedDict(
    "GetTransitGatewayAttachmentPropagationsResultTypeDef",
    {
        "TransitGatewayAttachmentPropagations": List[TransitGatewayAttachmentPropagationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayRouteTableAssociationsResultTypeDef = TypedDict(
    "GetTransitGatewayRouteTableAssociationsResultTypeDef",
    {
        "Associations": List[TransitGatewayRouteTableAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayRouteTablePropagationsResultTypeDef = TypedDict(
    "GetTransitGatewayRouteTablePropagationsResultTypeDef",
    {
        "TransitGatewayRouteTablePropagations": List[TransitGatewayRouteTablePropagationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetVpnConnectionDeviceTypesResultTypeDef = TypedDict(
    "GetVpnConnectionDeviceTypesResultTypeDef",
    {
        "VpnConnectionDeviceTypes": List[VpnConnectionDeviceTypeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GpuDeviceInfoTypeDef = TypedDict(
    "GpuDeviceInfoTypeDef",
    {
        "Name": str,
        "Manufacturer": str,
        "Count": int,
        "MemoryInfo": GpuDeviceMemoryInfoTypeDef,
    },
    total=False,
)

IamInstanceProfileAssociationTypeDef = TypedDict(
    "IamInstanceProfileAssociationTypeDef",
    {
        "AssociationId": str,
        "InstanceId": str,
        "IamInstanceProfile": IamInstanceProfileTypeDef,
        "State": IamInstanceProfileAssociationStateType,
        "Timestamp": datetime,
    },
    total=False,
)

LaunchPermissionModificationsTypeDef = TypedDict(
    "LaunchPermissionModificationsTypeDef",
    {
        "Add": Sequence[LaunchPermissionTypeDef],
        "Remove": Sequence[LaunchPermissionTypeDef],
    },
    total=False,
)

ImageDiskContainerTypeDef = TypedDict(
    "ImageDiskContainerTypeDef",
    {
        "Description": str,
        "DeviceName": str,
        "Format": str,
        "SnapshotId": str,
        "Url": str,
        "UserBucket": UserBucketTypeDef,
    },
    total=False,
)

SnapshotDiskContainerTypeDef = TypedDict(
    "SnapshotDiskContainerTypeDef",
    {
        "Description": str,
        "Format": str,
        "Url": str,
        "UserBucket": UserBucketTypeDef,
    },
    total=False,
)

ListImagesInRecycleBinResultTypeDef = TypedDict(
    "ListImagesInRecycleBinResultTypeDef",
    {
        "Images": List[ImageRecycleBinInfoTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportInstanceLaunchSpecificationTypeDef = TypedDict(
    "ImportInstanceLaunchSpecificationTypeDef",
    {
        "AdditionalInfo": str,
        "Architecture": ArchitectureValuesType,
        "GroupIds": Sequence[str],
        "GroupNames": Sequence[str],
        "InstanceInitiatedShutdownBehavior": ShutdownBehaviorType,
        "InstanceType": InstanceTypeType,
        "Monitoring": bool,
        "Placement": PlacementTypeDef,
        "PrivateIpAddress": str,
        "SubnetId": str,
        "UserData": UserDataTypeDef,
    },
    total=False,
)

InferenceAcceleratorInfoTypeDef = TypedDict(
    "InferenceAcceleratorInfoTypeDef",
    {
        "Accelerators": List[InferenceDeviceInfoTypeDef],
    },
    total=False,
)

_RequiredModifyInstanceCreditSpecificationRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceCreditSpecificationRequestRequestTypeDef",
    {
        "InstanceCreditSpecifications": Sequence[InstanceCreditSpecificationRequestTypeDef],
    },
)
_OptionalModifyInstanceCreditSpecificationRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceCreditSpecificationRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ClientToken": str,
    },
    total=False,
)


class ModifyInstanceCreditSpecificationRequestRequestTypeDef(
    _RequiredModifyInstanceCreditSpecificationRequestRequestTypeDef,
    _OptionalModifyInstanceCreditSpecificationRequestRequestTypeDef,
):
    pass


LaunchTemplateInstanceNetworkInterfaceSpecificationRequestTypeDef = TypedDict(
    "LaunchTemplateInstanceNetworkInterfaceSpecificationRequestTypeDef",
    {
        "AssociateCarrierIpAddress": bool,
        "AssociatePublicIpAddress": bool,
        "DeleteOnTermination": bool,
        "Description": str,
        "DeviceIndex": int,
        "Groups": Sequence[str],
        "InterfaceType": str,
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressRequestTypeDef],
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
        "PrivateIpAddresses": Sequence[PrivateIpAddressSpecificationTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "SubnetId": str,
        "NetworkCardIndex": int,
        "Ipv4Prefixes": Sequence[Ipv4PrefixSpecificationRequestTypeDef],
        "Ipv4PrefixCount": int,
        "Ipv6Prefixes": Sequence[Ipv6PrefixSpecificationRequestTypeDef],
        "Ipv6PrefixCount": int,
    },
    total=False,
)

InstanceMarketOptionsRequestTypeDef = TypedDict(
    "InstanceMarketOptionsRequestTypeDef",
    {
        "MarketType": Literal["spot"],
        "SpotOptions": SpotMarketOptionsTypeDef,
    },
    total=False,
)

ModifyInstanceMetadataOptionsResultTypeDef = TypedDict(
    "ModifyInstanceMetadataOptionsResultTypeDef",
    {
        "InstanceId": str,
        "InstanceMetadataOptions": InstanceMetadataOptionsResponseTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceMonitoringTypeDef = TypedDict(
    "InstanceMonitoringTypeDef",
    {
        "InstanceId": str,
        "Monitoring": MonitoringTypeDef,
    },
    total=False,
)

InstancePrivateIpAddressTypeDef = TypedDict(
    "InstancePrivateIpAddressTypeDef",
    {
        "Association": InstanceNetworkInterfaceAssociationTypeDef,
        "Primary": bool,
        "PrivateDnsName": str,
        "PrivateIpAddress": str,
    },
    total=False,
)

_RequiredInstanceRequirementsRequestTypeDef = TypedDict(
    "_RequiredInstanceRequirementsRequestTypeDef",
    {
        "VCpuCount": VCpuCountRangeRequestTypeDef,
        "MemoryMiB": MemoryMiBRequestTypeDef,
    },
)
_OptionalInstanceRequirementsRequestTypeDef = TypedDict(
    "_OptionalInstanceRequirementsRequestTypeDef",
    {
        "CpuManufacturers": Sequence[CpuManufacturerType],
        "MemoryGiBPerVCpu": MemoryGiBPerVCpuRequestTypeDef,
        "ExcludedInstanceTypes": Sequence[str],
        "InstanceGenerations": Sequence[InstanceGenerationType],
        "SpotMaxPricePercentageOverLowestPrice": int,
        "OnDemandMaxPricePercentageOverLowestPrice": int,
        "BareMetal": BareMetalType,
        "BurstablePerformance": BurstablePerformanceType,
        "RequireHibernateSupport": bool,
        "NetworkInterfaceCount": NetworkInterfaceCountRequestTypeDef,
        "LocalStorage": LocalStorageType,
        "LocalStorageTypes": Sequence[LocalStorageTypeType],
        "TotalLocalStorageGB": TotalLocalStorageGBRequestTypeDef,
        "BaselineEbsBandwidthMbps": BaselineEbsBandwidthMbpsRequestTypeDef,
        "AcceleratorTypes": Sequence[AcceleratorTypeType],
        "AcceleratorCount": AcceleratorCountRequestTypeDef,
        "AcceleratorManufacturers": Sequence[AcceleratorManufacturerType],
        "AcceleratorNames": Sequence[AcceleratorNameType],
        "AcceleratorTotalMemoryMiB": AcceleratorTotalMemoryMiBRequestTypeDef,
    },
    total=False,
)


class InstanceRequirementsRequestTypeDef(
    _RequiredInstanceRequirementsRequestTypeDef, _OptionalInstanceRequirementsRequestTypeDef
):
    pass


InstanceRequirementsTypeDef = TypedDict(
    "InstanceRequirementsTypeDef",
    {
        "VCpuCount": VCpuCountRangeTypeDef,
        "MemoryMiB": MemoryMiBTypeDef,
        "CpuManufacturers": List[CpuManufacturerType],
        "MemoryGiBPerVCpu": MemoryGiBPerVCpuTypeDef,
        "ExcludedInstanceTypes": List[str],
        "InstanceGenerations": List[InstanceGenerationType],
        "SpotMaxPricePercentageOverLowestPrice": int,
        "OnDemandMaxPricePercentageOverLowestPrice": int,
        "BareMetal": BareMetalType,
        "BurstablePerformance": BurstablePerformanceType,
        "RequireHibernateSupport": bool,
        "NetworkInterfaceCount": NetworkInterfaceCountTypeDef,
        "LocalStorage": LocalStorageType,
        "LocalStorageTypes": List[LocalStorageTypeType],
        "TotalLocalStorageGB": TotalLocalStorageGBTypeDef,
        "BaselineEbsBandwidthMbps": BaselineEbsBandwidthMbpsTypeDef,
        "AcceleratorTypes": List[AcceleratorTypeType],
        "AcceleratorCount": AcceleratorCountTypeDef,
        "AcceleratorManufacturers": List[AcceleratorManufacturerType],
        "AcceleratorNames": List[AcceleratorNameType],
        "AcceleratorTotalMemoryMiB": AcceleratorTotalMemoryMiBTypeDef,
    },
    total=False,
)

InstanceStateChangeTypeDef = TypedDict(
    "InstanceStateChangeTypeDef",
    {
        "CurrentState": InstanceStateTypeDef,
        "InstanceId": str,
        "PreviousState": InstanceStateTypeDef,
    },
    total=False,
)

InstanceStatusSummaryTypeDef = TypedDict(
    "InstanceStatusSummaryTypeDef",
    {
        "Details": List[InstanceStatusDetailsTypeDef],
        "Status": SummaryStatusType,
    },
    total=False,
)

ModifyInstanceEventStartTimeResultTypeDef = TypedDict(
    "ModifyInstanceEventStartTimeResultTypeDef",
    {
        "Event": InstanceStatusEventTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IpPermissionTypeDef = TypedDict(
    "IpPermissionTypeDef",
    {
        "FromPort": int,
        "IpProtocol": str,
        "IpRanges": Sequence[IpRangeTypeDef],
        "Ipv6Ranges": Sequence[Ipv6RangeTypeDef],
        "PrefixListIds": Sequence[PrefixListIdTypeDef],
        "ToPort": int,
        "UserIdGroupPairs": Sequence[UserIdGroupPairTypeDef],
    },
    total=False,
)

StaleIpPermissionTypeDef = TypedDict(
    "StaleIpPermissionTypeDef",
    {
        "FromPort": int,
        "IpProtocol": str,
        "IpRanges": List[str],
        "PrefixListIds": List[str],
        "ToPort": int,
        "UserIdGroupPairs": List[UserIdGroupPairTypeDef],
    },
    total=False,
)

_RequiredProvisionIpamPoolCidrRequestRequestTypeDef = TypedDict(
    "_RequiredProvisionIpamPoolCidrRequestRequestTypeDef",
    {
        "IpamPoolId": str,
    },
)
_OptionalProvisionIpamPoolCidrRequestRequestTypeDef = TypedDict(
    "_OptionalProvisionIpamPoolCidrRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Cidr": str,
        "CidrAuthorizationContext": IpamCidrAuthorizationContextTypeDef,
    },
    total=False,
)


class ProvisionIpamPoolCidrRequestRequestTypeDef(
    _RequiredProvisionIpamPoolCidrRequestRequestTypeDef,
    _OptionalProvisionIpamPoolCidrRequestRequestTypeDef,
):
    pass


IpamTypeDef = TypedDict(
    "IpamTypeDef",
    {
        "OwnerId": str,
        "IpamId": str,
        "IpamArn": str,
        "IpamRegion": str,
        "PublicDefaultScopeId": str,
        "PrivateDefaultScopeId": str,
        "ScopeCount": int,
        "Description": str,
        "OperatingRegions": List[IpamOperatingRegionTypeDef],
        "State": IpamStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

IpamPoolCidrTypeDef = TypedDict(
    "IpamPoolCidrTypeDef",
    {
        "Cidr": str,
        "State": IpamPoolCidrStateType,
        "FailureReason": IpamPoolCidrFailureReasonTypeDef,
    },
    total=False,
)

IpamPoolTypeDef = TypedDict(
    "IpamPoolTypeDef",
    {
        "OwnerId": str,
        "IpamPoolId": str,
        "SourceIpamPoolId": str,
        "IpamPoolArn": str,
        "IpamScopeArn": str,
        "IpamScopeType": IpamScopeTypeType,
        "IpamArn": str,
        "IpamRegion": str,
        "Locale": str,
        "PoolDepth": int,
        "State": IpamPoolStateType,
        "StateMessage": str,
        "Description": str,
        "AutoImport": bool,
        "PubliclyAdvertisable": bool,
        "AddressFamily": AddressFamilyType,
        "AllocationMinNetmaskLength": int,
        "AllocationMaxNetmaskLength": int,
        "AllocationDefaultNetmaskLength": int,
        "AllocationResourceTags": List[IpamResourceTagTypeDef],
        "Tags": List[TagTypeDef],
        "AwsService": Literal["ec2"],
    },
    total=False,
)

IpamResourceCidrTypeDef = TypedDict(
    "IpamResourceCidrTypeDef",
    {
        "IpamId": str,
        "IpamScopeId": str,
        "IpamPoolId": str,
        "ResourceRegion": str,
        "ResourceOwnerId": str,
        "ResourceId": str,
        "ResourceName": str,
        "ResourceCidr": str,
        "ResourceType": IpamResourceTypeType,
        "ResourceTags": List[IpamResourceTagTypeDef],
        "IpUsage": float,
        "ComplianceStatus": IpamComplianceStatusType,
        "ManagementState": IpamManagementStateType,
        "OverlapStatus": IpamOverlapStatusType,
        "VpcId": str,
    },
    total=False,
)

Ipv6PoolTypeDef = TypedDict(
    "Ipv6PoolTypeDef",
    {
        "PoolId": str,
        "Description": str,
        "PoolCidrBlocks": List[PoolCidrBlockTypeDef],
        "Tags": List[TagTypeDef],
    },
    total=False,
)

LaunchTemplateInstanceNetworkInterfaceSpecificationTypeDef = TypedDict(
    "LaunchTemplateInstanceNetworkInterfaceSpecificationTypeDef",
    {
        "AssociateCarrierIpAddress": bool,
        "AssociatePublicIpAddress": bool,
        "DeleteOnTermination": bool,
        "Description": str,
        "DeviceIndex": int,
        "Groups": List[str],
        "InterfaceType": str,
        "Ipv6AddressCount": int,
        "Ipv6Addresses": List[InstanceIpv6AddressTypeDef],
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
        "PrivateIpAddresses": List[PrivateIpAddressSpecificationTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "SubnetId": str,
        "NetworkCardIndex": int,
        "Ipv4Prefixes": List[Ipv4PrefixSpecificationResponseTypeDef],
        "Ipv4PrefixCount": int,
        "Ipv6Prefixes": List[Ipv6PrefixSpecificationResponseTypeDef],
        "Ipv6PrefixCount": int,
    },
    total=False,
)

LaunchTemplateBlockDeviceMappingRequestTypeDef = TypedDict(
    "LaunchTemplateBlockDeviceMappingRequestTypeDef",
    {
        "DeviceName": str,
        "VirtualName": str,
        "Ebs": LaunchTemplateEbsBlockDeviceRequestTypeDef,
        "NoDevice": str,
    },
    total=False,
)

LaunchTemplateBlockDeviceMappingTypeDef = TypedDict(
    "LaunchTemplateBlockDeviceMappingTypeDef",
    {
        "DeviceName": str,
        "VirtualName": str,
        "Ebs": LaunchTemplateEbsBlockDeviceTypeDef,
        "NoDevice": str,
    },
    total=False,
)

LaunchTemplateInstanceMarketOptionsRequestTypeDef = TypedDict(
    "LaunchTemplateInstanceMarketOptionsRequestTypeDef",
    {
        "MarketType": Literal["spot"],
        "SpotOptions": LaunchTemplateSpotMarketOptionsRequestTypeDef,
    },
    total=False,
)

LaunchTemplateInstanceMarketOptionsTypeDef = TypedDict(
    "LaunchTemplateInstanceMarketOptionsTypeDef",
    {
        "MarketType": Literal["spot"],
        "SpotOptions": LaunchTemplateSpotMarketOptionsTypeDef,
    },
    total=False,
)

ListSnapshotsInRecycleBinResultTypeDef = TypedDict(
    "ListSnapshotsInRecycleBinResultTypeDef",
    {
        "Snapshots": List[SnapshotRecycleBinInfoTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LoadPermissionModificationsTypeDef = TypedDict(
    "LoadPermissionModificationsTypeDef",
    {
        "Add": Sequence[LoadPermissionRequestTypeDef],
        "Remove": Sequence[LoadPermissionRequestTypeDef],
    },
    total=False,
)

_RequiredModifyIpamRequestRequestTypeDef = TypedDict(
    "_RequiredModifyIpamRequestRequestTypeDef",
    {
        "IpamId": str,
    },
)
_OptionalModifyIpamRequestRequestTypeDef = TypedDict(
    "_OptionalModifyIpamRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Description": str,
        "AddOperatingRegions": Sequence[AddIpamOperatingRegionTypeDef],
        "RemoveOperatingRegions": Sequence[RemoveIpamOperatingRegionTypeDef],
    },
    total=False,
)


class ModifyIpamRequestRequestTypeDef(
    _RequiredModifyIpamRequestRequestTypeDef, _OptionalModifyIpamRequestRequestTypeDef
):
    pass


_RequiredModifyManagedPrefixListRequestRequestTypeDef = TypedDict(
    "_RequiredModifyManagedPrefixListRequestRequestTypeDef",
    {
        "PrefixListId": str,
    },
)
_OptionalModifyManagedPrefixListRequestRequestTypeDef = TypedDict(
    "_OptionalModifyManagedPrefixListRequestRequestTypeDef",
    {
        "DryRun": bool,
        "CurrentVersion": int,
        "PrefixListName": str,
        "AddEntries": Sequence[AddPrefixListEntryTypeDef],
        "RemoveEntries": Sequence[RemovePrefixListEntryTypeDef],
        "MaxEntries": int,
    },
    total=False,
)


class ModifyManagedPrefixListRequestRequestTypeDef(
    _RequiredModifyManagedPrefixListRequestRequestTypeDef,
    _OptionalModifyManagedPrefixListRequestRequestTypeDef,
):
    pass


ModifyNetworkInterfaceAttributeRequestNetworkInterfaceModifyAttributeTypeDef = TypedDict(
    "ModifyNetworkInterfaceAttributeRequestNetworkInterfaceModifyAttributeTypeDef",
    {
        "Attachment": NetworkInterfaceAttachmentChangesTypeDef,
        "Description": AttributeValueTypeDef,
        "DryRun": bool,
        "Groups": Sequence[str],
        "SourceDestCheck": AttributeBooleanValueTypeDef,
    },
    total=False,
)

_RequiredModifyNetworkInterfaceAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyNetworkInterfaceAttributeRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
    },
)
_OptionalModifyNetworkInterfaceAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyNetworkInterfaceAttributeRequestRequestTypeDef",
    {
        "Attachment": NetworkInterfaceAttachmentChangesTypeDef,
        "Description": AttributeValueTypeDef,
        "DryRun": bool,
        "Groups": Sequence[str],
        "SourceDestCheck": AttributeBooleanValueTypeDef,
    },
    total=False,
)


class ModifyNetworkInterfaceAttributeRequestRequestTypeDef(
    _RequiredModifyNetworkInterfaceAttributeRequestRequestTypeDef,
    _OptionalModifyNetworkInterfaceAttributeRequestRequestTypeDef,
):
    pass


_RequiredModifyReservedInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredModifyReservedInstancesRequestRequestTypeDef",
    {
        "ReservedInstancesIds": Sequence[str],
        "TargetConfigurations": Sequence[ReservedInstancesConfigurationTypeDef],
    },
)
_OptionalModifyReservedInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalModifyReservedInstancesRequestRequestTypeDef",
    {
        "ClientToken": str,
    },
    total=False,
)


class ModifyReservedInstancesRequestRequestTypeDef(
    _RequiredModifyReservedInstancesRequestRequestTypeDef,
    _OptionalModifyReservedInstancesRequestRequestTypeDef,
):
    pass


ReservedInstancesModificationResultTypeDef = TypedDict(
    "ReservedInstancesModificationResultTypeDef",
    {
        "ReservedInstancesId": str,
        "TargetConfiguration": ReservedInstancesConfigurationTypeDef,
    },
    total=False,
)

_RequiredModifyTransitGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredModifyTransitGatewayRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
    },
)
_OptionalModifyTransitGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalModifyTransitGatewayRequestRequestTypeDef",
    {
        "Description": str,
        "Options": ModifyTransitGatewayOptionsTypeDef,
        "DryRun": bool,
    },
    total=False,
)


class ModifyTransitGatewayRequestRequestTypeDef(
    _RequiredModifyTransitGatewayRequestRequestTypeDef,
    _OptionalModifyTransitGatewayRequestRequestTypeDef,
):
    pass


_RequiredModifyTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredModifyTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
    },
)
_OptionalModifyTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalModifyTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "AddSubnetIds": Sequence[str],
        "RemoveSubnetIds": Sequence[str],
        "Options": ModifyTransitGatewayVpcAttachmentRequestOptionsTypeDef,
        "DryRun": bool,
    },
    total=False,
)


class ModifyTransitGatewayVpcAttachmentRequestRequestTypeDef(
    _RequiredModifyTransitGatewayVpcAttachmentRequestRequestTypeDef,
    _OptionalModifyTransitGatewayVpcAttachmentRequestRequestTypeDef,
):
    pass


_RequiredModifyVpcPeeringConnectionOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpcPeeringConnectionOptionsRequestRequestTypeDef",
    {
        "VpcPeeringConnectionId": str,
    },
)
_OptionalModifyVpcPeeringConnectionOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpcPeeringConnectionOptionsRequestRequestTypeDef",
    {
        "AccepterPeeringConnectionOptions": PeeringConnectionOptionsRequestTypeDef,
        "DryRun": bool,
        "RequesterPeeringConnectionOptions": PeeringConnectionOptionsRequestTypeDef,
    },
    total=False,
)


class ModifyVpcPeeringConnectionOptionsRequestRequestTypeDef(
    _RequiredModifyVpcPeeringConnectionOptionsRequestRequestTypeDef,
    _OptionalModifyVpcPeeringConnectionOptionsRequestRequestTypeDef,
):
    pass


ModifyVpcPeeringConnectionOptionsResultTypeDef = TypedDict(
    "ModifyVpcPeeringConnectionOptionsResultTypeDef",
    {
        "AccepterPeeringConnectionOptions": PeeringConnectionOptionsTypeDef,
        "RequesterPeeringConnectionOptions": PeeringConnectionOptionsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpnTunnelOptionsSpecificationTypeDef = TypedDict(
    "ModifyVpnTunnelOptionsSpecificationTypeDef",
    {
        "TunnelInsideCidr": str,
        "TunnelInsideIpv6Cidr": str,
        "PreSharedKey": str,
        "Phase1LifetimeSeconds": int,
        "Phase2LifetimeSeconds": int,
        "RekeyMarginTimeSeconds": int,
        "RekeyFuzzPercentage": int,
        "ReplayWindowSize": int,
        "DPDTimeoutSeconds": int,
        "DPDTimeoutAction": str,
        "Phase1EncryptionAlgorithms": Sequence[Phase1EncryptionAlgorithmsRequestListValueTypeDef],
        "Phase2EncryptionAlgorithms": Sequence[Phase2EncryptionAlgorithmsRequestListValueTypeDef],
        "Phase1IntegrityAlgorithms": Sequence[Phase1IntegrityAlgorithmsRequestListValueTypeDef],
        "Phase2IntegrityAlgorithms": Sequence[Phase2IntegrityAlgorithmsRequestListValueTypeDef],
        "Phase1DHGroupNumbers": Sequence[Phase1DHGroupNumbersRequestListValueTypeDef],
        "Phase2DHGroupNumbers": Sequence[Phase2DHGroupNumbersRequestListValueTypeDef],
        "IKEVersions": Sequence[IKEVersionsRequestListValueTypeDef],
        "StartupAction": str,
    },
    total=False,
)

VpnTunnelOptionsSpecificationTypeDef = TypedDict(
    "VpnTunnelOptionsSpecificationTypeDef",
    {
        "TunnelInsideCidr": str,
        "TunnelInsideIpv6Cidr": str,
        "PreSharedKey": str,
        "Phase1LifetimeSeconds": int,
        "Phase2LifetimeSeconds": int,
        "RekeyMarginTimeSeconds": int,
        "RekeyFuzzPercentage": int,
        "ReplayWindowSize": int,
        "DPDTimeoutSeconds": int,
        "DPDTimeoutAction": str,
        "Phase1EncryptionAlgorithms": Sequence[Phase1EncryptionAlgorithmsRequestListValueTypeDef],
        "Phase2EncryptionAlgorithms": Sequence[Phase2EncryptionAlgorithmsRequestListValueTypeDef],
        "Phase1IntegrityAlgorithms": Sequence[Phase1IntegrityAlgorithmsRequestListValueTypeDef],
        "Phase2IntegrityAlgorithms": Sequence[Phase2IntegrityAlgorithmsRequestListValueTypeDef],
        "Phase1DHGroupNumbers": Sequence[Phase1DHGroupNumbersRequestListValueTypeDef],
        "Phase2DHGroupNumbers": Sequence[Phase2DHGroupNumbersRequestListValueTypeDef],
        "IKEVersions": Sequence[IKEVersionsRequestListValueTypeDef],
        "StartupAction": str,
    },
    total=False,
)

NatGatewayTypeDef = TypedDict(
    "NatGatewayTypeDef",
    {
        "CreateTime": datetime,
        "DeleteTime": datetime,
        "FailureCode": str,
        "FailureMessage": str,
        "NatGatewayAddresses": List[NatGatewayAddressTypeDef],
        "NatGatewayId": str,
        "ProvisionedBandwidth": ProvisionedBandwidthTypeDef,
        "State": NatGatewayStateType,
        "SubnetId": str,
        "VpcId": str,
        "Tags": List[TagTypeDef],
        "ConnectivityType": ConnectivityTypeType,
    },
    total=False,
)

NetworkInfoTypeDef = TypedDict(
    "NetworkInfoTypeDef",
    {
        "NetworkPerformance": str,
        "MaximumNetworkInterfaces": int,
        "MaximumNetworkCards": int,
        "DefaultNetworkCardIndex": int,
        "NetworkCards": List[NetworkCardInfoTypeDef],
        "Ipv4AddressesPerInterface": int,
        "Ipv6AddressesPerInterface": int,
        "Ipv6Supported": bool,
        "EnaSupport": EnaSupportType,
        "EfaSupported": bool,
        "EfaInfo": EfaInfoTypeDef,
        "EncryptionInTransitSupported": bool,
    },
    total=False,
)

NetworkInterfacePrivateIpAddressTypeDef = TypedDict(
    "NetworkInterfacePrivateIpAddressTypeDef",
    {
        "Association": NetworkInterfaceAssociationTypeDef,
        "Primary": bool,
        "PrivateDnsName": str,
        "PrivateIpAddress": str,
    },
    total=False,
)

NetworkInterfacePermissionTypeDef = TypedDict(
    "NetworkInterfacePermissionTypeDef",
    {
        "NetworkInterfacePermissionId": str,
        "NetworkInterfaceId": str,
        "AwsAccountId": str,
        "AwsService": str,
        "Permission": InterfacePermissionTypeType,
        "PermissionState": NetworkInterfacePermissionStateTypeDef,
    },
    total=False,
)

PathStatementRequestTypeDef = TypedDict(
    "PathStatementRequestTypeDef",
    {
        "PacketHeaderStatement": PacketHeaderStatementRequestTypeDef,
        "ResourceStatement": ResourceStatementRequestTypeDef,
    },
    total=False,
)

ThroughResourcesStatementRequestTypeDef = TypedDict(
    "ThroughResourcesStatementRequestTypeDef",
    {
        "ResourceStatement": ResourceStatementRequestTypeDef,
    },
    total=False,
)

PathStatementTypeDef = TypedDict(
    "PathStatementTypeDef",
    {
        "PacketHeaderStatement": PacketHeaderStatementTypeDef,
        "ResourceStatement": ResourceStatementTypeDef,
    },
    total=False,
)

ThroughResourcesStatementTypeDef = TypedDict(
    "ThroughResourcesStatementTypeDef",
    {
        "ResourceStatement": ResourceStatementTypeDef,
    },
    total=False,
)

TransitGatewayPeeringAttachmentTypeDef = TypedDict(
    "TransitGatewayPeeringAttachmentTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "RequesterTgwInfo": PeeringTgwInfoTypeDef,
        "AccepterTgwInfo": PeeringTgwInfoTypeDef,
        "Status": PeeringAttachmentStatusTypeDef,
        "State": TransitGatewayAttachmentStateType,
        "CreationTime": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TunnelOptionTypeDef = TypedDict(
    "TunnelOptionTypeDef",
    {
        "OutsideIpAddress": str,
        "TunnelInsideCidr": str,
        "TunnelInsideIpv6Cidr": str,
        "PreSharedKey": str,
        "Phase1LifetimeSeconds": int,
        "Phase2LifetimeSeconds": int,
        "RekeyMarginTimeSeconds": int,
        "RekeyFuzzPercentage": int,
        "ReplayWindowSize": int,
        "DpdTimeoutSeconds": int,
        "DpdTimeoutAction": str,
        "Phase1EncryptionAlgorithms": List[Phase1EncryptionAlgorithmsListValueTypeDef],
        "Phase2EncryptionAlgorithms": List[Phase2EncryptionAlgorithmsListValueTypeDef],
        "Phase1IntegrityAlgorithms": List[Phase1IntegrityAlgorithmsListValueTypeDef],
        "Phase2IntegrityAlgorithms": List[Phase2IntegrityAlgorithmsListValueTypeDef],
        "Phase1DHGroupNumbers": List[Phase1DHGroupNumbersListValueTypeDef],
        "Phase2DHGroupNumbers": List[Phase2DHGroupNumbersListValueTypeDef],
        "IkeVersions": List[IKEVersionsListValueTypeDef],
        "StartupAction": str,
    },
    total=False,
)

ReservedInstancesListingTypeDef = TypedDict(
    "ReservedInstancesListingTypeDef",
    {
        "ClientToken": str,
        "CreateDate": datetime,
        "InstanceCounts": List[InstanceCountTypeDef],
        "PriceSchedules": List[PriceScheduleTypeDef],
        "ReservedInstancesId": str,
        "ReservedInstancesListingId": str,
        "Status": ListingStatusType,
        "StatusMessage": str,
        "Tags": List[TagTypeDef],
        "UpdateDate": datetime,
    },
    total=False,
)

ProvisionPublicIpv4PoolCidrResultTypeDef = TypedDict(
    "ProvisionPublicIpv4PoolCidrResultTypeDef",
    {
        "PoolId": str,
        "PoolAddressRange": PublicIpv4PoolRangeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PublicIpv4PoolTypeDef = TypedDict(
    "PublicIpv4PoolTypeDef",
    {
        "PoolId": str,
        "Description": str,
        "PoolAddressRanges": List[PublicIpv4PoolRangeTypeDef],
        "TotalAddressCount": int,
        "TotalAvailableAddressCount": int,
        "NetworkBorderGroup": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredPurchaseScheduledInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredPurchaseScheduledInstancesRequestRequestTypeDef",
    {
        "PurchaseRequests": Sequence[PurchaseRequestTypeDef],
    },
)
_OptionalPurchaseScheduledInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalPurchaseScheduledInstancesRequestRequestTypeDef",
    {
        "ClientToken": str,
        "DryRun": bool,
    },
    total=False,
)


class PurchaseScheduledInstancesRequestRequestTypeDef(
    _RequiredPurchaseScheduledInstancesRequestRequestTypeDef,
    _OptionalPurchaseScheduledInstancesRequestRequestTypeDef,
):
    pass


_RequiredPurchaseReservedInstancesOfferingRequestRequestTypeDef = TypedDict(
    "_RequiredPurchaseReservedInstancesOfferingRequestRequestTypeDef",
    {
        "InstanceCount": int,
        "ReservedInstancesOfferingId": str,
    },
)
_OptionalPurchaseReservedInstancesOfferingRequestRequestTypeDef = TypedDict(
    "_OptionalPurchaseReservedInstancesOfferingRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LimitPrice": ReservedInstanceLimitPriceTypeDef,
        "PurchaseTime": Union[datetime, str],
    },
    total=False,
)


class PurchaseReservedInstancesOfferingRequestRequestTypeDef(
    _RequiredPurchaseReservedInstancesOfferingRequestRequestTypeDef,
    _OptionalPurchaseReservedInstancesOfferingRequestRequestTypeDef,
):
    pass


ReservedInstancesOfferingTypeDef = TypedDict(
    "ReservedInstancesOfferingTypeDef",
    {
        "AvailabilityZone": str,
        "Duration": int,
        "FixedPrice": float,
        "InstanceType": InstanceTypeType,
        "ProductDescription": RIProductDescriptionType,
        "ReservedInstancesOfferingId": str,
        "UsagePrice": float,
        "CurrencyCode": Literal["USD"],
        "InstanceTenancy": TenancyType,
        "Marketplace": bool,
        "OfferingClass": OfferingClassTypeType,
        "OfferingType": OfferingTypeValuesType,
        "PricingDetails": List[PricingDetailTypeDef],
        "RecurringCharges": List[RecurringChargeTypeDef],
        "Scope": scopeType,
    },
    total=False,
)

ReservedInstancesTypeDef = TypedDict(
    "ReservedInstancesTypeDef",
    {
        "AvailabilityZone": str,
        "Duration": int,
        "End": datetime,
        "FixedPrice": float,
        "InstanceCount": int,
        "InstanceType": InstanceTypeType,
        "ProductDescription": RIProductDescriptionType,
        "ReservedInstancesId": str,
        "Start": datetime,
        "State": ReservedInstanceStateType,
        "UsagePrice": float,
        "CurrencyCode": Literal["USD"],
        "InstanceTenancy": TenancyType,
        "OfferingClass": OfferingClassTypeType,
        "OfferingType": OfferingTypeValuesType,
        "RecurringCharges": List[RecurringChargeTypeDef],
        "Scope": scopeType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

SecurityGroupRuleTypeDef = TypedDict(
    "SecurityGroupRuleTypeDef",
    {
        "SecurityGroupRuleId": str,
        "GroupId": str,
        "GroupOwnerId": str,
        "IsEgress": bool,
        "IpProtocol": str,
        "FromPort": int,
        "ToPort": int,
        "CidrIpv4": str,
        "CidrIpv6": str,
        "PrefixListId": str,
        "ReferencedGroupInfo": ReferencedSecurityGroupTypeDef,
        "Description": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

RegisterInstanceEventNotificationAttributesRequestRequestTypeDef = TypedDict(
    "RegisterInstanceEventNotificationAttributesRequestRequestTypeDef",
    {
        "DryRun": bool,
        "InstanceTagAttribute": RegisterInstanceTagAttributeRequestTypeDef,
    },
    total=False,
)

RegisterTransitGatewayMulticastGroupMembersResultTypeDef = TypedDict(
    "RegisterTransitGatewayMulticastGroupMembersResultTypeDef",
    {
        "RegisteredMulticastGroupMembers": TransitGatewayMulticastRegisteredGroupMembersTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterTransitGatewayMulticastGroupSourcesResultTypeDef = TypedDict(
    "RegisterTransitGatewayMulticastGroupSourcesResultTypeDef",
    {
        "RegisteredMulticastGroupSources": TransitGatewayMulticastRegisteredGroupSourcesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StorageTypeDef = TypedDict(
    "StorageTypeDef",
    {
        "S3": S3StorageTypeDef,
    },
    total=False,
)

ScheduledInstanceAvailabilityTypeDef = TypedDict(
    "ScheduledInstanceAvailabilityTypeDef",
    {
        "AvailabilityZone": str,
        "AvailableInstanceCount": int,
        "FirstSlotStartTime": datetime,
        "HourlyPrice": str,
        "InstanceType": str,
        "MaxTermDurationInDays": int,
        "MinTermDurationInDays": int,
        "NetworkPlatform": str,
        "Platform": str,
        "PurchaseToken": str,
        "Recurrence": ScheduledInstanceRecurrenceTypeDef,
        "SlotDurationInHours": int,
        "TotalScheduledInstanceHours": int,
    },
    total=False,
)

ScheduledInstanceTypeDef = TypedDict(
    "ScheduledInstanceTypeDef",
    {
        "AvailabilityZone": str,
        "CreateDate": datetime,
        "HourlyPrice": str,
        "InstanceCount": int,
        "InstanceType": str,
        "NetworkPlatform": str,
        "NextSlotStartTime": datetime,
        "Platform": str,
        "PreviousSlotEndTime": datetime,
        "Recurrence": ScheduledInstanceRecurrenceTypeDef,
        "ScheduledInstanceId": str,
        "SlotDurationInHours": int,
        "TermEndDate": datetime,
        "TermStartDate": datetime,
        "TotalScheduledInstanceHours": int,
    },
    total=False,
)

ScheduledInstancesBlockDeviceMappingTypeDef = TypedDict(
    "ScheduledInstancesBlockDeviceMappingTypeDef",
    {
        "DeviceName": str,
        "Ebs": ScheduledInstancesEbsTypeDef,
        "NoDevice": str,
        "VirtualName": str,
    },
    total=False,
)

ScheduledInstancesNetworkInterfaceTypeDef = TypedDict(
    "ScheduledInstancesNetworkInterfaceTypeDef",
    {
        "AssociatePublicIpAddress": bool,
        "DeleteOnTermination": bool,
        "Description": str,
        "DeviceIndex": int,
        "Groups": Sequence[str],
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[ScheduledInstancesIpv6AddressTypeDef],
        "NetworkInterfaceId": str,
        "PrivateIpAddress": str,
        "PrivateIpAddressConfigs": Sequence[ScheduledInstancesPrivateIpAddressConfigTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "SubnetId": str,
    },
    total=False,
)

SearchTransitGatewayMulticastGroupsResultTypeDef = TypedDict(
    "SearchTransitGatewayMulticastGroupsResultTypeDef",
    {
        "MulticastGroups": List[TransitGatewayMulticastGroupTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VpcEndpointTypeDef = TypedDict(
    "VpcEndpointTypeDef",
    {
        "VpcEndpointId": str,
        "VpcEndpointType": VpcEndpointTypeType,
        "VpcId": str,
        "ServiceName": str,
        "State": StateType,
        "PolicyDocument": str,
        "RouteTableIds": List[str],
        "SubnetIds": List[str],
        "Groups": List[SecurityGroupIdentifierTypeDef],
        "IpAddressType": IpAddressTypeType,
        "DnsOptions": DnsOptionsTypeDef,
        "PrivateDnsEnabled": bool,
        "RequesterManaged": bool,
        "NetworkInterfaceIds": List[str],
        "DnsEntries": List[DnsEntryTypeDef],
        "CreationTimestamp": datetime,
        "Tags": List[TagTypeDef],
        "OwnerId": str,
        "LastError": LastErrorTypeDef,
    },
    total=False,
)

SecurityGroupRuleUpdateTypeDef = TypedDict(
    "SecurityGroupRuleUpdateTypeDef",
    {
        "SecurityGroupRuleId": str,
        "SecurityGroupRule": SecurityGroupRuleRequestTypeDef,
    },
    total=False,
)

ServiceConfigurationTypeDef = TypedDict(
    "ServiceConfigurationTypeDef",
    {
        "ServiceType": List[ServiceTypeDetailTypeDef],
        "ServiceId": str,
        "ServiceName": str,
        "ServiceState": ServiceStateType,
        "AvailabilityZones": List[str],
        "AcceptanceRequired": bool,
        "ManagesVpcEndpoints": bool,
        "NetworkLoadBalancerArns": List[str],
        "GatewayLoadBalancerArns": List[str],
        "SupportedIpAddressTypes": List[ServiceConnectivityTypeType],
        "BaseEndpointDnsNames": List[str],
        "PrivateDnsName": str,
        "PrivateDnsNameConfiguration": PrivateDnsNameConfigurationTypeDef,
        "PayerResponsibility": Literal["ServiceOwner"],
        "Tags": List[TagTypeDef],
    },
    total=False,
)

ServiceDetailTypeDef = TypedDict(
    "ServiceDetailTypeDef",
    {
        "ServiceName": str,
        "ServiceId": str,
        "ServiceType": List[ServiceTypeDetailTypeDef],
        "AvailabilityZones": List[str],
        "Owner": str,
        "BaseEndpointDnsNames": List[str],
        "PrivateDnsName": str,
        "PrivateDnsNames": List[PrivateDnsDetailsTypeDef],
        "VpcEndpointPolicySupported": bool,
        "AcceptanceRequired": bool,
        "ManagesVpcEndpoints": bool,
        "PayerResponsibility": Literal["ServiceOwner"],
        "Tags": List[TagTypeDef],
        "PrivateDnsNameVerificationState": DnsNameStateType,
        "SupportedIpAddressTypes": List[ServiceConnectivityTypeType],
    },
    total=False,
)

SnapshotDetailTypeDef = TypedDict(
    "SnapshotDetailTypeDef",
    {
        "Description": str,
        "DeviceName": str,
        "DiskImageSize": float,
        "Format": str,
        "Progress": str,
        "SnapshotId": str,
        "Status": str,
        "StatusMessage": str,
        "Url": str,
        "UserBucket": UserBucketDetailsTypeDef,
    },
    total=False,
)

SnapshotTaskDetailTypeDef = TypedDict(
    "SnapshotTaskDetailTypeDef",
    {
        "Description": str,
        "DiskImageSize": float,
        "Encrypted": bool,
        "Format": str,
        "KmsKeyId": str,
        "Progress": str,
        "SnapshotId": str,
        "Status": str,
        "StatusMessage": str,
        "Url": str,
        "UserBucket": UserBucketDetailsTypeDef,
    },
    total=False,
)

SpotMaintenanceStrategiesTypeDef = TypedDict(
    "SpotMaintenanceStrategiesTypeDef",
    {
        "CapacityRebalance": SpotCapacityRebalanceTypeDef,
    },
    total=False,
)

SpotDatafeedSubscriptionTypeDef = TypedDict(
    "SpotDatafeedSubscriptionTypeDef",
    {
        "Bucket": str,
        "Fault": SpotInstanceStateFaultTypeDef,
        "OwnerId": str,
        "Prefix": str,
        "State": DatafeedSubscriptionStateType,
    },
    total=False,
)

TransitGatewayMulticastDomainAssociationTypeDef = TypedDict(
    "TransitGatewayMulticastDomainAssociationTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "ResourceOwnerId": str,
        "Subnet": SubnetAssociationTypeDef,
    },
    total=False,
)

TransitGatewayMulticastDomainAssociationsTypeDef = TypedDict(
    "TransitGatewayMulticastDomainAssociationsTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "TransitGatewayAttachmentId": str,
        "ResourceId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "ResourceOwnerId": str,
        "Subnets": List[SubnetAssociationTypeDef],
    },
    total=False,
)

SubnetIpv6CidrBlockAssociationTypeDef = TypedDict(
    "SubnetIpv6CidrBlockAssociationTypeDef",
    {
        "AssociationId": str,
        "Ipv6CidrBlock": str,
        "Ipv6CidrBlockState": SubnetCidrBlockStateTypeDef,
    },
    total=False,
)

TargetReservationValueTypeDef = TypedDict(
    "TargetReservationValueTypeDef",
    {
        "ReservationValue": ReservationValueTypeDef,
        "TargetConfiguration": TargetConfigurationTypeDef,
    },
    total=False,
)

TargetGroupsConfigTypeDef = TypedDict(
    "TargetGroupsConfigTypeDef",
    {
        "TargetGroups": List[TargetGroupTypeDef],
    },
    total=False,
)

TrafficMirrorFilterRuleTypeDef = TypedDict(
    "TrafficMirrorFilterRuleTypeDef",
    {
        "TrafficMirrorFilterRuleId": str,
        "TrafficMirrorFilterId": str,
        "TrafficDirection": TrafficDirectionType,
        "RuleNumber": int,
        "RuleAction": TrafficMirrorRuleActionType,
        "Protocol": int,
        "DestinationPortRange": TrafficMirrorPortRangeTypeDef,
        "SourcePortRange": TrafficMirrorPortRangeTypeDef,
        "DestinationCidrBlock": str,
        "SourceCidrBlock": str,
        "Description": str,
    },
    total=False,
)

TransitGatewayAttachmentTypeDef = TypedDict(
    "TransitGatewayAttachmentTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "TransitGatewayId": str,
        "TransitGatewayOwnerId": str,
        "ResourceOwnerId": str,
        "ResourceType": TransitGatewayAttachmentResourceTypeType,
        "ResourceId": str,
        "State": TransitGatewayAttachmentStateType,
        "Association": TransitGatewayAttachmentAssociationTypeDef,
        "CreationTime": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TransitGatewayConnectPeerConfigurationTypeDef = TypedDict(
    "TransitGatewayConnectPeerConfigurationTypeDef",
    {
        "TransitGatewayAddress": str,
        "PeerAddress": str,
        "InsideCidrBlocks": List[str],
        "Protocol": Literal["gre"],
        "BgpConfigurations": List[TransitGatewayAttachmentBgpConfigurationTypeDef],
    },
    total=False,
)

TransitGatewayConnectTypeDef = TypedDict(
    "TransitGatewayConnectTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "TransportTransitGatewayAttachmentId": str,
        "TransitGatewayId": str,
        "State": TransitGatewayAttachmentStateType,
        "CreationTime": datetime,
        "Options": TransitGatewayConnectOptionsTypeDef,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TransitGatewayMulticastDomainTypeDef = TypedDict(
    "TransitGatewayMulticastDomainTypeDef",
    {
        "TransitGatewayMulticastDomainId": str,
        "TransitGatewayId": str,
        "TransitGatewayMulticastDomainArn": str,
        "OwnerId": str,
        "Options": TransitGatewayMulticastDomainOptionsTypeDef,
        "State": TransitGatewayMulticastDomainStateType,
        "CreationTime": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TransitGatewayTypeDef = TypedDict(
    "TransitGatewayTypeDef",
    {
        "TransitGatewayId": str,
        "TransitGatewayArn": str,
        "State": TransitGatewayStateType,
        "OwnerId": str,
        "Description": str,
        "CreationTime": datetime,
        "Options": TransitGatewayOptionsTypeDef,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

TransitGatewayPrefixListReferenceTypeDef = TypedDict(
    "TransitGatewayPrefixListReferenceTypeDef",
    {
        "TransitGatewayRouteTableId": str,
        "PrefixListId": str,
        "PrefixListOwnerId": str,
        "State": TransitGatewayPrefixListReferenceStateType,
        "Blackhole": bool,
        "TransitGatewayAttachment": TransitGatewayPrefixListAttachmentTypeDef,
    },
    total=False,
)

TransitGatewayRouteTypeDef = TypedDict(
    "TransitGatewayRouteTypeDef",
    {
        "DestinationCidrBlock": str,
        "PrefixListId": str,
        "TransitGatewayAttachments": List[TransitGatewayRouteAttachmentTypeDef],
        "Type": TransitGatewayRouteTypeType,
        "State": TransitGatewayRouteStateType,
    },
    total=False,
)

TransitGatewayVpcAttachmentTypeDef = TypedDict(
    "TransitGatewayVpcAttachmentTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "TransitGatewayId": str,
        "VpcId": str,
        "VpcOwnerId": str,
        "State": TransitGatewayAttachmentStateType,
        "SubnetIds": List[str],
        "CreationTime": datetime,
        "Options": TransitGatewayVpcAttachmentOptionsTypeDef,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

UnsuccessfulInstanceCreditSpecificationItemTypeDef = TypedDict(
    "UnsuccessfulInstanceCreditSpecificationItemTypeDef",
    {
        "InstanceId": str,
        "Error": UnsuccessfulInstanceCreditSpecificationItemErrorTypeDef,
    },
    total=False,
)

UnsuccessfulItemTypeDef = TypedDict(
    "UnsuccessfulItemTypeDef",
    {
        "Error": UnsuccessfulItemErrorTypeDef,
        "ResourceId": str,
    },
    total=False,
)

ValidationWarningTypeDef = TypedDict(
    "ValidationWarningTypeDef",
    {
        "Errors": List[ValidationErrorTypeDef],
    },
    total=False,
)

VolumeResponseMetadataTypeDef = TypedDict(
    "VolumeResponseMetadataTypeDef",
    {
        "Attachments": List[VolumeAttachmentTypeDef],
        "AvailabilityZone": str,
        "CreateTime": datetime,
        "Encrypted": bool,
        "KmsKeyId": str,
        "OutpostArn": str,
        "Size": int,
        "SnapshotId": str,
        "State": VolumeStateType,
        "VolumeId": str,
        "Iops": int,
        "Tags": List[TagTypeDef],
        "VolumeType": VolumeTypeType,
        "FastRestored": bool,
        "MultiAttachEnabled": bool,
        "Throughput": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VolumeTypeDef = TypedDict(
    "VolumeTypeDef",
    {
        "Attachments": List[VolumeAttachmentTypeDef],
        "AvailabilityZone": str,
        "CreateTime": datetime,
        "Encrypted": bool,
        "KmsKeyId": str,
        "OutpostArn": str,
        "Size": int,
        "SnapshotId": str,
        "State": VolumeStateType,
        "VolumeId": str,
        "Iops": int,
        "Tags": List[TagTypeDef],
        "VolumeType": VolumeTypeType,
        "FastRestored": bool,
        "MultiAttachEnabled": bool,
        "Throughput": int,
    },
    total=False,
)

VolumeStatusInfoTypeDef = TypedDict(
    "VolumeStatusInfoTypeDef",
    {
        "Details": List[VolumeStatusDetailsTypeDef],
        "Status": VolumeStatusInfoStatusType,
    },
    total=False,
)

VpcCidrBlockAssociationTypeDef = TypedDict(
    "VpcCidrBlockAssociationTypeDef",
    {
        "AssociationId": str,
        "CidrBlock": str,
        "CidrBlockState": VpcCidrBlockStateTypeDef,
    },
    total=False,
)

VpcIpv6CidrBlockAssociationTypeDef = TypedDict(
    "VpcIpv6CidrBlockAssociationTypeDef",
    {
        "AssociationId": str,
        "Ipv6CidrBlock": str,
        "Ipv6CidrBlockState": VpcCidrBlockStateTypeDef,
        "NetworkBorderGroup": str,
        "Ipv6Pool": str,
    },
    total=False,
)

VpcPeeringConnectionVpcInfoResponseMetadataTypeDef = TypedDict(
    "VpcPeeringConnectionVpcInfoResponseMetadataTypeDef",
    {
        "CidrBlock": str,
        "Ipv6CidrBlockSet": List[Ipv6CidrBlockTypeDef],
        "CidrBlockSet": List[CidrBlockTypeDef],
        "OwnerId": str,
        "PeeringOptions": VpcPeeringConnectionOptionsDescriptionTypeDef,
        "VpcId": str,
        "Region": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VpcPeeringConnectionVpcInfoTypeDef = TypedDict(
    "VpcPeeringConnectionVpcInfoTypeDef",
    {
        "CidrBlock": str,
        "Ipv6CidrBlockSet": List[Ipv6CidrBlockTypeDef],
        "CidrBlockSet": List[CidrBlockTypeDef],
        "OwnerId": str,
        "PeeringOptions": VpcPeeringConnectionOptionsDescriptionTypeDef,
        "VpcId": str,
        "Region": str,
    },
    total=False,
)

DescribeAccountAttributesResultTypeDef = TypedDict(
    "DescribeAccountAttributesResultTypeDef",
    {
        "AccountAttributes": List[AccountAttributeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAddressesAttributeResultTypeDef = TypedDict(
    "DescribeAddressesAttributeResultTypeDef",
    {
        "Addresses": List[AddressAttributeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyAddressAttributeResultTypeDef = TypedDict(
    "ModifyAddressAttributeResultTypeDef",
    {
        "Address": AddressAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResetAddressAttributeResultTypeDef = TypedDict(
    "ResetAddressAttributeResultTypeDef",
    {
        "Address": AddressAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAddressesResultTypeDef = TypedDict(
    "DescribeAddressesResultTypeDef",
    {
        "Addresses": List[AddressTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCapacityReservationResultTypeDef = TypedDict(
    "CreateCapacityReservationResultTypeDef",
    {
        "CapacityReservation": CapacityReservationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCapacityReservationsResultTypeDef = TypedDict(
    "DescribeCapacityReservationsResultTypeDef",
    {
        "NextToken": str,
        "CapacityReservations": List[CapacityReservationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCarrierGatewayResultTypeDef = TypedDict(
    "CreateCarrierGatewayResultTypeDef",
    {
        "CarrierGateway": CarrierGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteCarrierGatewayResultTypeDef = TypedDict(
    "DeleteCarrierGatewayResultTypeDef",
    {
        "CarrierGateway": CarrierGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCarrierGatewaysResultTypeDef = TypedDict(
    "DescribeCarrierGatewaysResultTypeDef",
    {
        "CarrierGateways": List[CarrierGatewayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCoipPoolsResultTypeDef = TypedDict(
    "DescribeCoipPoolsResultTypeDef",
    {
        "CoipPools": List[CoipPoolTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCustomerGatewayResultTypeDef = TypedDict(
    "CreateCustomerGatewayResultTypeDef",
    {
        "CustomerGateway": CustomerGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCustomerGatewaysResultTypeDef = TypedDict(
    "DescribeCustomerGatewaysResultTypeDef",
    {
        "CustomerGateways": List[CustomerGatewayTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeHostReservationsResultTypeDef = TypedDict(
    "DescribeHostReservationsResultTypeDef",
    {
        "HostReservationSet": List[HostReservationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredAssociateInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateInstanceEventWindowRequestRequestTypeDef",
    {
        "InstanceEventWindowId": str,
        "AssociationTarget": InstanceEventWindowAssociationRequestTypeDef,
    },
)
_OptionalAssociateInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateInstanceEventWindowRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class AssociateInstanceEventWindowRequestRequestTypeDef(
    _RequiredAssociateInstanceEventWindowRequestRequestTypeDef,
    _OptionalAssociateInstanceEventWindowRequestRequestTypeDef,
):
    pass


InstanceEventWindowTypeDef = TypedDict(
    "InstanceEventWindowTypeDef",
    {
        "InstanceEventWindowId": str,
        "TimeRanges": List[InstanceEventWindowTimeRangeTypeDef],
        "Name": str,
        "CronExpression": str,
        "AssociationTarget": InstanceEventWindowAssociationTargetTypeDef,
        "State": InstanceEventWindowStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredDisassociateInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_RequiredDisassociateInstanceEventWindowRequestRequestTypeDef",
    {
        "InstanceEventWindowId": str,
        "AssociationTarget": InstanceEventWindowDisassociationRequestTypeDef,
    },
)
_OptionalDisassociateInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "_OptionalDisassociateInstanceEventWindowRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class DisassociateInstanceEventWindowRequestRequestTypeDef(
    _RequiredDisassociateInstanceEventWindowRequestRequestTypeDef,
    _OptionalDisassociateInstanceEventWindowRequestRequestTypeDef,
):
    pass


CreateIpamScopeResultTypeDef = TypedDict(
    "CreateIpamScopeResultTypeDef",
    {
        "IpamScope": IpamScopeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteIpamScopeResultTypeDef = TypedDict(
    "DeleteIpamScopeResultTypeDef",
    {
        "IpamScope": IpamScopeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIpamScopesResultTypeDef = TypedDict(
    "DescribeIpamScopesResultTypeDef",
    {
        "NextToken": str,
        "IpamScopes": List[IpamScopeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyIpamScopeResultTypeDef = TypedDict(
    "ModifyIpamScopeResultTypeDef",
    {
        "IpamScope": IpamScopeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeKeyPairsResultTypeDef = TypedDict(
    "DescribeKeyPairsResultTypeDef",
    {
        "KeyPairs": List[KeyPairInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLaunchTemplateResultTypeDef = TypedDict(
    "DeleteLaunchTemplateResultTypeDef",
    {
        "LaunchTemplate": LaunchTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLaunchTemplatesResultTypeDef = TypedDict(
    "DescribeLaunchTemplatesResultTypeDef",
    {
        "LaunchTemplates": List[LaunchTemplateTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyLaunchTemplateResultTypeDef = TypedDict(
    "ModifyLaunchTemplateResultTypeDef",
    {
        "LaunchTemplate": LaunchTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLocalGatewayRouteTablesResultTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTablesResultTypeDef",
    {
        "LocalGatewayRouteTables": List[LocalGatewayRouteTableTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResultTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResultTypeDef",
    {
        "LocalGatewayRouteTableVirtualInterfaceGroupAssociations": List[
            LocalGatewayRouteTableVirtualInterfaceGroupAssociationTypeDef
        ],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLocalGatewayRouteTableVpcAssociationResultTypeDef = TypedDict(
    "CreateLocalGatewayRouteTableVpcAssociationResultTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociation": LocalGatewayRouteTableVpcAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLocalGatewayRouteTableVpcAssociationResultTypeDef = TypedDict(
    "DeleteLocalGatewayRouteTableVpcAssociationResultTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociation": LocalGatewayRouteTableVpcAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLocalGatewayRouteTableVpcAssociationsResultTypeDef = TypedDict(
    "DescribeLocalGatewayRouteTableVpcAssociationsResultTypeDef",
    {
        "LocalGatewayRouteTableVpcAssociations": List[LocalGatewayRouteTableVpcAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLocalGatewaysResultTypeDef = TypedDict(
    "DescribeLocalGatewaysResultTypeDef",
    {
        "LocalGateways": List[LocalGatewayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLocalGatewayVirtualInterfaceGroupsResultTypeDef = TypedDict(
    "DescribeLocalGatewayVirtualInterfaceGroupsResultTypeDef",
    {
        "LocalGatewayVirtualInterfaceGroups": List[LocalGatewayVirtualInterfaceGroupTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLocalGatewayVirtualInterfacesResultTypeDef = TypedDict(
    "DescribeLocalGatewayVirtualInterfacesResultTypeDef",
    {
        "LocalGatewayVirtualInterfaces": List[LocalGatewayVirtualInterfaceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateManagedPrefixListResultTypeDef = TypedDict(
    "CreateManagedPrefixListResultTypeDef",
    {
        "PrefixList": ManagedPrefixListTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteManagedPrefixListResultTypeDef = TypedDict(
    "DeleteManagedPrefixListResultTypeDef",
    {
        "PrefixList": ManagedPrefixListTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeManagedPrefixListsResultTypeDef = TypedDict(
    "DescribeManagedPrefixListsResultTypeDef",
    {
        "NextToken": str,
        "PrefixLists": List[ManagedPrefixListTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyManagedPrefixListResultTypeDef = TypedDict(
    "ModifyManagedPrefixListResultTypeDef",
    {
        "PrefixList": ManagedPrefixListTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreManagedPrefixListVersionResultTypeDef = TypedDict(
    "RestoreManagedPrefixListVersionResultTypeDef",
    {
        "PrefixList": ManagedPrefixListTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInsightsAccessScopeAnalysesResultTypeDef = TypedDict(
    "DescribeNetworkInsightsAccessScopeAnalysesResultTypeDef",
    {
        "NetworkInsightsAccessScopeAnalyses": List[NetworkInsightsAccessScopeAnalysisTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartNetworkInsightsAccessScopeAnalysisResultTypeDef = TypedDict(
    "StartNetworkInsightsAccessScopeAnalysisResultTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysis": NetworkInsightsAccessScopeAnalysisTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInsightsAccessScopesResultTypeDef = TypedDict(
    "DescribeNetworkInsightsAccessScopesResultTypeDef",
    {
        "NetworkInsightsAccessScopes": List[NetworkInsightsAccessScopeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateNetworkInsightsPathResultTypeDef = TypedDict(
    "CreateNetworkInsightsPathResultTypeDef",
    {
        "NetworkInsightsPath": NetworkInsightsPathTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInsightsPathsResultTypeDef = TypedDict(
    "DescribeNetworkInsightsPathsResultTypeDef",
    {
        "NetworkInsightsPaths": List[NetworkInsightsPathTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePlacementGroupResultTypeDef = TypedDict(
    "CreatePlacementGroupResultTypeDef",
    {
        "PlacementGroup": PlacementGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePlacementGroupsResultTypeDef = TypedDict(
    "DescribePlacementGroupsResultTypeDef",
    {
        "PlacementGroups": List[PlacementGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateReplaceRootVolumeTaskResultTypeDef = TypedDict(
    "CreateReplaceRootVolumeTaskResultTypeDef",
    {
        "ReplaceRootVolumeTask": ReplaceRootVolumeTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeReplaceRootVolumeTasksResultTypeDef = TypedDict(
    "DescribeReplaceRootVolumeTasksResultTypeDef",
    {
        "ReplaceRootVolumeTasks": List[ReplaceRootVolumeTaskTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSnapshotsResultTypeDef = TypedDict(
    "CreateSnapshotsResultTypeDef",
    {
        "Snapshots": List[SnapshotInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSnapshotTierStatusResultTypeDef = TypedDict(
    "DescribeSnapshotTierStatusResultTypeDef",
    {
        "SnapshotTierStatuses": List[SnapshotTierStatusTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSnapshotsResultTypeDef = TypedDict(
    "DescribeSnapshotsResultTypeDef",
    {
        "Snapshots": List[SnapshotTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSubnetCidrReservationResultTypeDef = TypedDict(
    "CreateSubnetCidrReservationResultTypeDef",
    {
        "SubnetCidrReservation": SubnetCidrReservationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteSubnetCidrReservationResultTypeDef = TypedDict(
    "DeleteSubnetCidrReservationResultTypeDef",
    {
        "DeletedSubnetCidrReservation": SubnetCidrReservationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSubnetCidrReservationsResultTypeDef = TypedDict(
    "GetSubnetCidrReservationsResultTypeDef",
    {
        "SubnetIpv4CidrReservations": List[SubnetCidrReservationTypeDef],
        "SubnetIpv6CidrReservations": List[SubnetCidrReservationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AllocateAddressRequestRequestTypeDef = TypedDict(
    "AllocateAddressRequestRequestTypeDef",
    {
        "Domain": DomainTypeType,
        "Address": str,
        "PublicIpv4Pool": str,
        "NetworkBorderGroup": str,
        "CustomerOwnedIpv4Pool": str,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredAllocateHostsRequestRequestTypeDef = TypedDict(
    "_RequiredAllocateHostsRequestRequestTypeDef",
    {
        "AvailabilityZone": str,
        "Quantity": int,
    },
)
_OptionalAllocateHostsRequestRequestTypeDef = TypedDict(
    "_OptionalAllocateHostsRequestRequestTypeDef",
    {
        "AutoPlacement": AutoPlacementType,
        "ClientToken": str,
        "InstanceType": str,
        "InstanceFamily": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "HostRecovery": HostRecoveryType,
        "OutpostArn": str,
    },
    total=False,
)


class AllocateHostsRequestRequestTypeDef(
    _RequiredAllocateHostsRequestRequestTypeDef, _OptionalAllocateHostsRequestRequestTypeDef
):
    pass


_RequiredCopySnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCopySnapshotRequestRequestTypeDef",
    {
        "SourceRegion": str,
        "SourceSnapshotId": str,
    },
)
_OptionalCopySnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCopySnapshotRequestRequestTypeDef",
    {
        "Description": str,
        "DestinationOutpostArn": str,
        "DestinationRegion": str,
        "Encrypted": bool,
        "KmsKeyId": str,
        "PresignedUrl": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CopySnapshotRequestRequestTypeDef(
    _RequiredCopySnapshotRequestRequestTypeDef, _OptionalCopySnapshotRequestRequestTypeDef
):
    pass


_RequiredCopySnapshotRequestSnapshotCopyTypeDef = TypedDict(
    "_RequiredCopySnapshotRequestSnapshotCopyTypeDef",
    {
        "SourceRegion": str,
    },
)
_OptionalCopySnapshotRequestSnapshotCopyTypeDef = TypedDict(
    "_OptionalCopySnapshotRequestSnapshotCopyTypeDef",
    {
        "Description": str,
        "DestinationOutpostArn": str,
        "DestinationRegion": str,
        "Encrypted": bool,
        "KmsKeyId": str,
        "PresignedUrl": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CopySnapshotRequestSnapshotCopyTypeDef(
    _RequiredCopySnapshotRequestSnapshotCopyTypeDef, _OptionalCopySnapshotRequestSnapshotCopyTypeDef
):
    pass


_RequiredCreateCapacityReservationFleetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCapacityReservationFleetRequestRequestTypeDef",
    {
        "InstanceTypeSpecifications": Sequence[ReservationFleetInstanceSpecificationTypeDef],
        "TotalTargetCapacity": int,
    },
)
_OptionalCreateCapacityReservationFleetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCapacityReservationFleetRequestRequestTypeDef",
    {
        "AllocationStrategy": str,
        "ClientToken": str,
        "Tenancy": Literal["default"],
        "EndDate": Union[datetime, str],
        "InstanceMatchCriteria": Literal["open"],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateCapacityReservationFleetRequestRequestTypeDef(
    _RequiredCreateCapacityReservationFleetRequestRequestTypeDef,
    _OptionalCreateCapacityReservationFleetRequestRequestTypeDef,
):
    pass


_RequiredCreateCapacityReservationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCapacityReservationRequestRequestTypeDef",
    {
        "InstanceType": str,
        "InstancePlatform": CapacityReservationInstancePlatformType,
        "InstanceCount": int,
    },
)
_OptionalCreateCapacityReservationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCapacityReservationRequestRequestTypeDef",
    {
        "ClientToken": str,
        "AvailabilityZone": str,
        "AvailabilityZoneId": str,
        "Tenancy": CapacityReservationTenancyType,
        "EbsOptimized": bool,
        "EphemeralStorage": bool,
        "EndDate": Union[datetime, str],
        "EndDateType": EndDateTypeType,
        "InstanceMatchCriteria": InstanceMatchCriteriaType,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
        "OutpostArn": str,
        "PlacementGroupArn": str,
    },
    total=False,
)


class CreateCapacityReservationRequestRequestTypeDef(
    _RequiredCreateCapacityReservationRequestRequestTypeDef,
    _OptionalCreateCapacityReservationRequestRequestTypeDef,
):
    pass


_RequiredCreateCarrierGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCarrierGatewayRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateCarrierGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCarrierGatewayRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
        "ClientToken": str,
    },
    total=False,
)


class CreateCarrierGatewayRequestRequestTypeDef(
    _RequiredCreateCarrierGatewayRequestRequestTypeDef,
    _OptionalCreateCarrierGatewayRequestRequestTypeDef,
):
    pass


_RequiredCreateCustomerGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCustomerGatewayRequestRequestTypeDef",
    {
        "BgpAsn": int,
        "Type": Literal["ipsec.1"],
    },
)
_OptionalCreateCustomerGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCustomerGatewayRequestRequestTypeDef",
    {
        "PublicIp": str,
        "CertificateArn": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DeviceName": str,
        "DryRun": bool,
    },
    total=False,
)


class CreateCustomerGatewayRequestRequestTypeDef(
    _RequiredCreateCustomerGatewayRequestRequestTypeDef,
    _OptionalCreateCustomerGatewayRequestRequestTypeDef,
):
    pass


_RequiredCreateDhcpOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDhcpOptionsRequestRequestTypeDef",
    {
        "DhcpConfigurations": Sequence[NewDhcpConfigurationTypeDef],
    },
)
_OptionalCreateDhcpOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDhcpOptionsRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateDhcpOptionsRequestRequestTypeDef(
    _RequiredCreateDhcpOptionsRequestRequestTypeDef, _OptionalCreateDhcpOptionsRequestRequestTypeDef
):
    pass


_RequiredCreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef = TypedDict(
    "_RequiredCreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef",
    {
        "DhcpConfigurations": Sequence[NewDhcpConfigurationTypeDef],
    },
)
_OptionalCreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef = TypedDict(
    "_OptionalCreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef(
    _RequiredCreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef,
    _OptionalCreateDhcpOptionsRequestServiceResourceCreateDhcpOptionsTypeDef,
):
    pass


_RequiredCreateEgressOnlyInternetGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredCreateEgressOnlyInternetGatewayRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateEgressOnlyInternetGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalCreateEgressOnlyInternetGatewayRequestRequestTypeDef",
    {
        "ClientToken": str,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateEgressOnlyInternetGatewayRequestRequestTypeDef(
    _RequiredCreateEgressOnlyInternetGatewayRequestRequestTypeDef,
    _OptionalCreateEgressOnlyInternetGatewayRequestRequestTypeDef,
):
    pass


_RequiredCreateFlowLogsRequestRequestTypeDef = TypedDict(
    "_RequiredCreateFlowLogsRequestRequestTypeDef",
    {
        "ResourceIds": Sequence[str],
        "ResourceType": FlowLogsResourceTypeType,
        "TrafficType": TrafficTypeType,
    },
)
_OptionalCreateFlowLogsRequestRequestTypeDef = TypedDict(
    "_OptionalCreateFlowLogsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ClientToken": str,
        "DeliverLogsPermissionArn": str,
        "LogGroupName": str,
        "LogDestinationType": LogDestinationTypeType,
        "LogDestination": str,
        "LogFormat": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "MaxAggregationInterval": int,
        "DestinationOptions": DestinationOptionsRequestTypeDef,
    },
    total=False,
)


class CreateFlowLogsRequestRequestTypeDef(
    _RequiredCreateFlowLogsRequestRequestTypeDef, _OptionalCreateFlowLogsRequestRequestTypeDef
):
    pass


_RequiredCreateFpgaImageRequestRequestTypeDef = TypedDict(
    "_RequiredCreateFpgaImageRequestRequestTypeDef",
    {
        "InputStorageLocation": StorageLocationTypeDef,
    },
)
_OptionalCreateFpgaImageRequestRequestTypeDef = TypedDict(
    "_OptionalCreateFpgaImageRequestRequestTypeDef",
    {
        "DryRun": bool,
        "LogsStorageLocation": StorageLocationTypeDef,
        "Description": str,
        "Name": str,
        "ClientToken": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateFpgaImageRequestRequestTypeDef(
    _RequiredCreateFpgaImageRequestRequestTypeDef, _OptionalCreateFpgaImageRequestRequestTypeDef
):
    pass


CreateInstanceEventWindowRequestRequestTypeDef = TypedDict(
    "CreateInstanceEventWindowRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Name": str,
        "TimeRanges": Sequence[InstanceEventWindowTimeRangeRequestTypeDef],
        "CronExpression": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredCreateInstanceExportTaskRequestRequestTypeDef = TypedDict(
    "_RequiredCreateInstanceExportTaskRequestRequestTypeDef",
    {
        "ExportToS3Task": ExportToS3TaskSpecificationTypeDef,
        "InstanceId": str,
        "TargetEnvironment": ExportEnvironmentType,
    },
)
_OptionalCreateInstanceExportTaskRequestRequestTypeDef = TypedDict(
    "_OptionalCreateInstanceExportTaskRequestRequestTypeDef",
    {
        "Description": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateInstanceExportTaskRequestRequestTypeDef(
    _RequiredCreateInstanceExportTaskRequestRequestTypeDef,
    _OptionalCreateInstanceExportTaskRequestRequestTypeDef,
):
    pass


CreateInternetGatewayRequestRequestTypeDef = TypedDict(
    "CreateInternetGatewayRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)

CreateInternetGatewayRequestServiceResourceCreateInternetGatewayTypeDef = TypedDict(
    "CreateInternetGatewayRequestServiceResourceCreateInternetGatewayTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)

_RequiredCreateIpamPoolRequestRequestTypeDef = TypedDict(
    "_RequiredCreateIpamPoolRequestRequestTypeDef",
    {
        "IpamScopeId": str,
        "AddressFamily": AddressFamilyType,
    },
)
_OptionalCreateIpamPoolRequestRequestTypeDef = TypedDict(
    "_OptionalCreateIpamPoolRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Locale": str,
        "SourceIpamPoolId": str,
        "Description": str,
        "AutoImport": bool,
        "PubliclyAdvertisable": bool,
        "AllocationMinNetmaskLength": int,
        "AllocationMaxNetmaskLength": int,
        "AllocationDefaultNetmaskLength": int,
        "AllocationResourceTags": Sequence[RequestIpamResourceTagTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
        "AwsService": Literal["ec2"],
    },
    total=False,
)


class CreateIpamPoolRequestRequestTypeDef(
    _RequiredCreateIpamPoolRequestRequestTypeDef, _OptionalCreateIpamPoolRequestRequestTypeDef
):
    pass


CreateIpamRequestRequestTypeDef = TypedDict(
    "CreateIpamRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Description": str,
        "OperatingRegions": Sequence[AddIpamOperatingRegionTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
    },
    total=False,
)

_RequiredCreateIpamScopeRequestRequestTypeDef = TypedDict(
    "_RequiredCreateIpamScopeRequestRequestTypeDef",
    {
        "IpamId": str,
    },
)
_OptionalCreateIpamScopeRequestRequestTypeDef = TypedDict(
    "_OptionalCreateIpamScopeRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Description": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateIpamScopeRequestRequestTypeDef(
    _RequiredCreateIpamScopeRequestRequestTypeDef, _OptionalCreateIpamScopeRequestRequestTypeDef
):
    pass


_RequiredCreateKeyPairRequestRequestTypeDef = TypedDict(
    "_RequiredCreateKeyPairRequestRequestTypeDef",
    {
        "KeyName": str,
    },
)
_OptionalCreateKeyPairRequestRequestTypeDef = TypedDict(
    "_OptionalCreateKeyPairRequestRequestTypeDef",
    {
        "DryRun": bool,
        "KeyType": KeyTypeType,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "KeyFormat": KeyFormatType,
    },
    total=False,
)


class CreateKeyPairRequestRequestTypeDef(
    _RequiredCreateKeyPairRequestRequestTypeDef, _OptionalCreateKeyPairRequestRequestTypeDef
):
    pass


_RequiredCreateKeyPairRequestServiceResourceCreateKeyPairTypeDef = TypedDict(
    "_RequiredCreateKeyPairRequestServiceResourceCreateKeyPairTypeDef",
    {
        "KeyName": str,
    },
)
_OptionalCreateKeyPairRequestServiceResourceCreateKeyPairTypeDef = TypedDict(
    "_OptionalCreateKeyPairRequestServiceResourceCreateKeyPairTypeDef",
    {
        "DryRun": bool,
        "KeyType": KeyTypeType,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "KeyFormat": KeyFormatType,
    },
    total=False,
)


class CreateKeyPairRequestServiceResourceCreateKeyPairTypeDef(
    _RequiredCreateKeyPairRequestServiceResourceCreateKeyPairTypeDef,
    _OptionalCreateKeyPairRequestServiceResourceCreateKeyPairTypeDef,
):
    pass


_RequiredCreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef",
    {
        "LocalGatewayRouteTableId": str,
        "VpcId": str,
    },
)
_OptionalCreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef(
    _RequiredCreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef,
    _OptionalCreateLocalGatewayRouteTableVpcAssociationRequestRequestTypeDef,
):
    pass


_RequiredCreateManagedPrefixListRequestRequestTypeDef = TypedDict(
    "_RequiredCreateManagedPrefixListRequestRequestTypeDef",
    {
        "PrefixListName": str,
        "MaxEntries": int,
        "AddressFamily": str,
    },
)
_OptionalCreateManagedPrefixListRequestRequestTypeDef = TypedDict(
    "_OptionalCreateManagedPrefixListRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Entries": Sequence[AddPrefixListEntryTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateManagedPrefixListRequestRequestTypeDef(
    _RequiredCreateManagedPrefixListRequestRequestTypeDef,
    _OptionalCreateManagedPrefixListRequestRequestTypeDef,
):
    pass


_RequiredCreateNatGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNatGatewayRequestRequestTypeDef",
    {
        "SubnetId": str,
    },
)
_OptionalCreateNatGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNatGatewayRequestRequestTypeDef",
    {
        "AllocationId": str,
        "ClientToken": str,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ConnectivityType": ConnectivityTypeType,
    },
    total=False,
)


class CreateNatGatewayRequestRequestTypeDef(
    _RequiredCreateNatGatewayRequestRequestTypeDef, _OptionalCreateNatGatewayRequestRequestTypeDef
):
    pass


_RequiredCreateNetworkAclRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNetworkAclRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateNetworkAclRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNetworkAclRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateNetworkAclRequestRequestTypeDef(
    _RequiredCreateNetworkAclRequestRequestTypeDef, _OptionalCreateNetworkAclRequestRequestTypeDef
):
    pass


_RequiredCreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef = TypedDict(
    "_RequiredCreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef = TypedDict(
    "_OptionalCreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef(
    _RequiredCreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef,
    _OptionalCreateNetworkAclRequestServiceResourceCreateNetworkAclTypeDef,
):
    pass


CreateNetworkAclRequestVpcCreateNetworkAclTypeDef = TypedDict(
    "CreateNetworkAclRequestVpcCreateNetworkAclTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredCreateNetworkInsightsPathRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNetworkInsightsPathRequestRequestTypeDef",
    {
        "Source": str,
        "Destination": str,
        "Protocol": ProtocolType,
        "ClientToken": str,
    },
)
_OptionalCreateNetworkInsightsPathRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNetworkInsightsPathRequestRequestTypeDef",
    {
        "SourceIp": str,
        "DestinationIp": str,
        "DestinationPort": int,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateNetworkInsightsPathRequestRequestTypeDef(
    _RequiredCreateNetworkInsightsPathRequestRequestTypeDef,
    _OptionalCreateNetworkInsightsPathRequestRequestTypeDef,
):
    pass


_RequiredCreateNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNetworkInterfaceRequestRequestTypeDef",
    {
        "SubnetId": str,
    },
)
_OptionalCreateNetworkInterfaceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNetworkInterfaceRequestRequestTypeDef",
    {
        "Description": str,
        "DryRun": bool,
        "Groups": Sequence[str],
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressTypeDef],
        "PrivateIpAddress": str,
        "PrivateIpAddresses": Sequence[PrivateIpAddressSpecificationTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "Ipv4Prefixes": Sequence[Ipv4PrefixSpecificationRequestTypeDef],
        "Ipv4PrefixCount": int,
        "Ipv6Prefixes": Sequence[Ipv6PrefixSpecificationRequestTypeDef],
        "Ipv6PrefixCount": int,
        "InterfaceType": NetworkInterfaceCreationTypeType,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateNetworkInterfaceRequestRequestTypeDef(
    _RequiredCreateNetworkInterfaceRequestRequestTypeDef,
    _OptionalCreateNetworkInterfaceRequestRequestTypeDef,
):
    pass


_RequiredCreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef = TypedDict(
    "_RequiredCreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef",
    {
        "SubnetId": str,
    },
)
_OptionalCreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef = TypedDict(
    "_OptionalCreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef",
    {
        "Description": str,
        "DryRun": bool,
        "Groups": Sequence[str],
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressTypeDef],
        "PrivateIpAddress": str,
        "PrivateIpAddresses": Sequence[PrivateIpAddressSpecificationTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "Ipv4Prefixes": Sequence[Ipv4PrefixSpecificationRequestTypeDef],
        "Ipv4PrefixCount": int,
        "Ipv6Prefixes": Sequence[Ipv6PrefixSpecificationRequestTypeDef],
        "Ipv6PrefixCount": int,
        "InterfaceType": NetworkInterfaceCreationTypeType,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
    },
    total=False,
)


class CreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef(
    _RequiredCreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef,
    _OptionalCreateNetworkInterfaceRequestServiceResourceCreateNetworkInterfaceTypeDef,
):
    pass


CreateNetworkInterfaceRequestSubnetCreateNetworkInterfaceTypeDef = TypedDict(
    "CreateNetworkInterfaceRequestSubnetCreateNetworkInterfaceTypeDef",
    {
        "Description": str,
        "DryRun": bool,
        "Groups": Sequence[str],
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressTypeDef],
        "PrivateIpAddress": str,
        "PrivateIpAddresses": Sequence[PrivateIpAddressSpecificationTypeDef],
        "SecondaryPrivateIpAddressCount": int,
        "Ipv4Prefixes": Sequence[Ipv4PrefixSpecificationRequestTypeDef],
        "Ipv4PrefixCount": int,
        "Ipv6Prefixes": Sequence[Ipv6PrefixSpecificationRequestTypeDef],
        "Ipv6PrefixCount": int,
        "InterfaceType": NetworkInterfaceCreationTypeType,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "ClientToken": str,
    },
    total=False,
)

CreatePlacementGroupRequestRequestTypeDef = TypedDict(
    "CreatePlacementGroupRequestRequestTypeDef",
    {
        "DryRun": bool,
        "GroupName": str,
        "Strategy": PlacementStrategyType,
        "PartitionCount": int,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreatePlacementGroupRequestServiceResourceCreatePlacementGroupTypeDef = TypedDict(
    "CreatePlacementGroupRequestServiceResourceCreatePlacementGroupTypeDef",
    {
        "DryRun": bool,
        "GroupName": str,
        "Strategy": PlacementStrategyType,
        "PartitionCount": int,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreatePublicIpv4PoolRequestRequestTypeDef = TypedDict(
    "CreatePublicIpv4PoolRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredCreateReplaceRootVolumeTaskRequestRequestTypeDef = TypedDict(
    "_RequiredCreateReplaceRootVolumeTaskRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalCreateReplaceRootVolumeTaskRequestRequestTypeDef = TypedDict(
    "_OptionalCreateReplaceRootVolumeTaskRequestRequestTypeDef",
    {
        "SnapshotId": str,
        "ClientToken": str,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateReplaceRootVolumeTaskRequestRequestTypeDef(
    _RequiredCreateReplaceRootVolumeTaskRequestRequestTypeDef,
    _OptionalCreateReplaceRootVolumeTaskRequestRequestTypeDef,
):
    pass


_RequiredCreateRestoreImageTaskRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRestoreImageTaskRequestRequestTypeDef",
    {
        "Bucket": str,
        "ObjectKey": str,
    },
)
_OptionalCreateRestoreImageTaskRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRestoreImageTaskRequestRequestTypeDef",
    {
        "Name": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateRestoreImageTaskRequestRequestTypeDef(
    _RequiredCreateRestoreImageTaskRequestRequestTypeDef,
    _OptionalCreateRestoreImageTaskRequestRequestTypeDef,
):
    pass


_RequiredCreateRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRouteTableRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRouteTableRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateRouteTableRequestRequestTypeDef(
    _RequiredCreateRouteTableRequestRequestTypeDef, _OptionalCreateRouteTableRequestRequestTypeDef
):
    pass


_RequiredCreateRouteTableRequestServiceResourceCreateRouteTableTypeDef = TypedDict(
    "_RequiredCreateRouteTableRequestServiceResourceCreateRouteTableTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateRouteTableRequestServiceResourceCreateRouteTableTypeDef = TypedDict(
    "_OptionalCreateRouteTableRequestServiceResourceCreateRouteTableTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateRouteTableRequestServiceResourceCreateRouteTableTypeDef(
    _RequiredCreateRouteTableRequestServiceResourceCreateRouteTableTypeDef,
    _OptionalCreateRouteTableRequestServiceResourceCreateRouteTableTypeDef,
):
    pass


CreateRouteTableRequestVpcCreateRouteTableTypeDef = TypedDict(
    "CreateRouteTableRequestVpcCreateRouteTableTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredCreateSecurityGroupRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSecurityGroupRequestRequestTypeDef",
    {
        "Description": str,
        "GroupName": str,
    },
)
_OptionalCreateSecurityGroupRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSecurityGroupRequestRequestTypeDef",
    {
        "VpcId": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateSecurityGroupRequestRequestTypeDef(
    _RequiredCreateSecurityGroupRequestRequestTypeDef,
    _OptionalCreateSecurityGroupRequestRequestTypeDef,
):
    pass


_RequiredCreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef = TypedDict(
    "_RequiredCreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef",
    {
        "Description": str,
        "GroupName": str,
    },
)
_OptionalCreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef = TypedDict(
    "_OptionalCreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef",
    {
        "VpcId": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef(
    _RequiredCreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef,
    _OptionalCreateSecurityGroupRequestServiceResourceCreateSecurityGroupTypeDef,
):
    pass


_RequiredCreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef = TypedDict(
    "_RequiredCreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef",
    {
        "Description": str,
        "GroupName": str,
    },
)
_OptionalCreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef = TypedDict(
    "_OptionalCreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef(
    _RequiredCreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef,
    _OptionalCreateSecurityGroupRequestVpcCreateSecurityGroupTypeDef,
):
    pass


_RequiredCreateSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSnapshotRequestRequestTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalCreateSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSnapshotRequestRequestTypeDef",
    {
        "Description": str,
        "OutpostArn": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateSnapshotRequestRequestTypeDef(
    _RequiredCreateSnapshotRequestRequestTypeDef, _OptionalCreateSnapshotRequestRequestTypeDef
):
    pass


_RequiredCreateSnapshotRequestServiceResourceCreateSnapshotTypeDef = TypedDict(
    "_RequiredCreateSnapshotRequestServiceResourceCreateSnapshotTypeDef",
    {
        "VolumeId": str,
    },
)
_OptionalCreateSnapshotRequestServiceResourceCreateSnapshotTypeDef = TypedDict(
    "_OptionalCreateSnapshotRequestServiceResourceCreateSnapshotTypeDef",
    {
        "Description": str,
        "OutpostArn": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateSnapshotRequestServiceResourceCreateSnapshotTypeDef(
    _RequiredCreateSnapshotRequestServiceResourceCreateSnapshotTypeDef,
    _OptionalCreateSnapshotRequestServiceResourceCreateSnapshotTypeDef,
):
    pass


CreateSnapshotRequestVolumeCreateSnapshotTypeDef = TypedDict(
    "CreateSnapshotRequestVolumeCreateSnapshotTypeDef",
    {
        "Description": str,
        "OutpostArn": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)

_RequiredCreateSnapshotsRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSnapshotsRequestRequestTypeDef",
    {
        "InstanceSpecification": InstanceSpecificationTypeDef,
    },
)
_OptionalCreateSnapshotsRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSnapshotsRequestRequestTypeDef",
    {
        "Description": str,
        "OutpostArn": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
        "CopyTagsFromSource": Literal["volume"],
    },
    total=False,
)


class CreateSnapshotsRequestRequestTypeDef(
    _RequiredCreateSnapshotsRequestRequestTypeDef, _OptionalCreateSnapshotsRequestRequestTypeDef
):
    pass


_RequiredCreateSubnetCidrReservationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSubnetCidrReservationRequestRequestTypeDef",
    {
        "SubnetId": str,
        "Cidr": str,
        "ReservationType": SubnetCidrReservationTypeType,
    },
)
_OptionalCreateSubnetCidrReservationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSubnetCidrReservationRequestRequestTypeDef",
    {
        "Description": str,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateSubnetCidrReservationRequestRequestTypeDef(
    _RequiredCreateSubnetCidrReservationRequestRequestTypeDef,
    _OptionalCreateSubnetCidrReservationRequestRequestTypeDef,
):
    pass


_RequiredCreateSubnetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSubnetRequestRequestTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateSubnetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSubnetRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "AvailabilityZone": str,
        "AvailabilityZoneId": str,
        "CidrBlock": str,
        "Ipv6CidrBlock": str,
        "OutpostArn": str,
        "DryRun": bool,
        "Ipv6Native": bool,
    },
    total=False,
)


class CreateSubnetRequestRequestTypeDef(
    _RequiredCreateSubnetRequestRequestTypeDef, _OptionalCreateSubnetRequestRequestTypeDef
):
    pass


_RequiredCreateSubnetRequestServiceResourceCreateSubnetTypeDef = TypedDict(
    "_RequiredCreateSubnetRequestServiceResourceCreateSubnetTypeDef",
    {
        "VpcId": str,
    },
)
_OptionalCreateSubnetRequestServiceResourceCreateSubnetTypeDef = TypedDict(
    "_OptionalCreateSubnetRequestServiceResourceCreateSubnetTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "AvailabilityZone": str,
        "AvailabilityZoneId": str,
        "CidrBlock": str,
        "Ipv6CidrBlock": str,
        "OutpostArn": str,
        "DryRun": bool,
        "Ipv6Native": bool,
    },
    total=False,
)


class CreateSubnetRequestServiceResourceCreateSubnetTypeDef(
    _RequiredCreateSubnetRequestServiceResourceCreateSubnetTypeDef,
    _OptionalCreateSubnetRequestServiceResourceCreateSubnetTypeDef,
):
    pass


CreateSubnetRequestVpcCreateSubnetTypeDef = TypedDict(
    "CreateSubnetRequestVpcCreateSubnetTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "AvailabilityZone": str,
        "AvailabilityZoneId": str,
        "CidrBlock": str,
        "Ipv6CidrBlock": str,
        "OutpostArn": str,
        "DryRun": bool,
        "Ipv6Native": bool,
    },
    total=False,
)

CreateTrafficMirrorFilterRequestRequestTypeDef = TypedDict(
    "CreateTrafficMirrorFilterRequestRequestTypeDef",
    {
        "Description": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
        "ClientToken": str,
    },
    total=False,
)

_RequiredCreateTrafficMirrorSessionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTrafficMirrorSessionRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
        "TrafficMirrorTargetId": str,
        "TrafficMirrorFilterId": str,
        "SessionNumber": int,
    },
)
_OptionalCreateTrafficMirrorSessionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTrafficMirrorSessionRequestRequestTypeDef",
    {
        "PacketLength": int,
        "VirtualNetworkId": int,
        "Description": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
        "ClientToken": str,
    },
    total=False,
)


class CreateTrafficMirrorSessionRequestRequestTypeDef(
    _RequiredCreateTrafficMirrorSessionRequestRequestTypeDef,
    _OptionalCreateTrafficMirrorSessionRequestRequestTypeDef,
):
    pass


CreateTrafficMirrorTargetRequestRequestTypeDef = TypedDict(
    "CreateTrafficMirrorTargetRequestRequestTypeDef",
    {
        "NetworkInterfaceId": str,
        "NetworkLoadBalancerArn": str,
        "Description": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
        "ClientToken": str,
        "GatewayLoadBalancerEndpointId": str,
    },
    total=False,
)

_RequiredCreateTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "PeerAddress": str,
        "InsideCidrBlocks": Sequence[str],
    },
)
_OptionalCreateTransitGatewayConnectPeerRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayConnectPeerRequestRequestTypeDef",
    {
        "TransitGatewayAddress": str,
        "BgpOptions": TransitGatewayConnectRequestBgpOptionsTypeDef,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayConnectPeerRequestRequestTypeDef(
    _RequiredCreateTransitGatewayConnectPeerRequestRequestTypeDef,
    _OptionalCreateTransitGatewayConnectPeerRequestRequestTypeDef,
):
    pass


_RequiredCreateTransitGatewayConnectRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayConnectRequestRequestTypeDef",
    {
        "TransportTransitGatewayAttachmentId": str,
        "Options": CreateTransitGatewayConnectRequestOptionsTypeDef,
    },
)
_OptionalCreateTransitGatewayConnectRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayConnectRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayConnectRequestRequestTypeDef(
    _RequiredCreateTransitGatewayConnectRequestRequestTypeDef,
    _OptionalCreateTransitGatewayConnectRequestRequestTypeDef,
):
    pass


_RequiredCreateTransitGatewayMulticastDomainRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayMulticastDomainRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
    },
)
_OptionalCreateTransitGatewayMulticastDomainRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayMulticastDomainRequestRequestTypeDef",
    {
        "Options": CreateTransitGatewayMulticastDomainRequestOptionsTypeDef,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayMulticastDomainRequestRequestTypeDef(
    _RequiredCreateTransitGatewayMulticastDomainRequestRequestTypeDef,
    _OptionalCreateTransitGatewayMulticastDomainRequestRequestTypeDef,
):
    pass


_RequiredCreateTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
        "PeerTransitGatewayId": str,
        "PeerAccountId": str,
        "PeerRegion": str,
    },
)
_OptionalCreateTransitGatewayPeeringAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayPeeringAttachmentRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayPeeringAttachmentRequestRequestTypeDef(
    _RequiredCreateTransitGatewayPeeringAttachmentRequestRequestTypeDef,
    _OptionalCreateTransitGatewayPeeringAttachmentRequestRequestTypeDef,
):
    pass


CreateTransitGatewayRequestRequestTypeDef = TypedDict(
    "CreateTransitGatewayRequestRequestTypeDef",
    {
        "Description": str,
        "Options": TransitGatewayRequestOptionsTypeDef,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)

_RequiredCreateTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
    },
)
_OptionalCreateTransitGatewayRouteTableRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayRouteTableRequestRequestTypeDef",
    {
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayRouteTableRequestRequestTypeDef(
    _RequiredCreateTransitGatewayRouteTableRequestRequestTypeDef,
    _OptionalCreateTransitGatewayRouteTableRequestRequestTypeDef,
):
    pass


_RequiredCreateTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "TransitGatewayId": str,
        "VpcId": str,
        "SubnetIds": Sequence[str],
    },
)
_OptionalCreateTransitGatewayVpcAttachmentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateTransitGatewayVpcAttachmentRequestRequestTypeDef",
    {
        "Options": CreateTransitGatewayVpcAttachmentRequestOptionsTypeDef,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateTransitGatewayVpcAttachmentRequestRequestTypeDef(
    _RequiredCreateTransitGatewayVpcAttachmentRequestRequestTypeDef,
    _OptionalCreateTransitGatewayVpcAttachmentRequestRequestTypeDef,
):
    pass


_RequiredCreateVolumeRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVolumeRequestRequestTypeDef",
    {
        "AvailabilityZone": str,
    },
)
_OptionalCreateVolumeRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVolumeRequestRequestTypeDef",
    {
        "Encrypted": bool,
        "Iops": int,
        "KmsKeyId": str,
        "OutpostArn": str,
        "Size": int,
        "SnapshotId": str,
        "VolumeType": VolumeTypeType,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "MultiAttachEnabled": bool,
        "Throughput": int,
        "ClientToken": str,
    },
    total=False,
)


class CreateVolumeRequestRequestTypeDef(
    _RequiredCreateVolumeRequestRequestTypeDef, _OptionalCreateVolumeRequestRequestTypeDef
):
    pass


_RequiredCreateVolumeRequestServiceResourceCreateVolumeTypeDef = TypedDict(
    "_RequiredCreateVolumeRequestServiceResourceCreateVolumeTypeDef",
    {
        "AvailabilityZone": str,
    },
)
_OptionalCreateVolumeRequestServiceResourceCreateVolumeTypeDef = TypedDict(
    "_OptionalCreateVolumeRequestServiceResourceCreateVolumeTypeDef",
    {
        "Encrypted": bool,
        "Iops": int,
        "KmsKeyId": str,
        "OutpostArn": str,
        "Size": int,
        "SnapshotId": str,
        "VolumeType": VolumeTypeType,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "MultiAttachEnabled": bool,
        "Throughput": int,
        "ClientToken": str,
    },
    total=False,
)


class CreateVolumeRequestServiceResourceCreateVolumeTypeDef(
    _RequiredCreateVolumeRequestServiceResourceCreateVolumeTypeDef,
    _OptionalCreateVolumeRequestServiceResourceCreateVolumeTypeDef,
):
    pass


_RequiredCreateVpcEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpcEndpointRequestRequestTypeDef",
    {
        "VpcId": str,
        "ServiceName": str,
    },
)
_OptionalCreateVpcEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpcEndpointRequestRequestTypeDef",
    {
        "DryRun": bool,
        "VpcEndpointType": VpcEndpointTypeType,
        "PolicyDocument": str,
        "RouteTableIds": Sequence[str],
        "SubnetIds": Sequence[str],
        "SecurityGroupIds": Sequence[str],
        "IpAddressType": IpAddressTypeType,
        "DnsOptions": DnsOptionsSpecificationTypeDef,
        "ClientToken": str,
        "PrivateDnsEnabled": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateVpcEndpointRequestRequestTypeDef(
    _RequiredCreateVpcEndpointRequestRequestTypeDef, _OptionalCreateVpcEndpointRequestRequestTypeDef
):
    pass


CreateVpcEndpointServiceConfigurationRequestRequestTypeDef = TypedDict(
    "CreateVpcEndpointServiceConfigurationRequestRequestTypeDef",
    {
        "DryRun": bool,
        "AcceptanceRequired": bool,
        "PrivateDnsName": str,
        "NetworkLoadBalancerArns": Sequence[str],
        "GatewayLoadBalancerArns": Sequence[str],
        "SupportedIpAddressTypes": Sequence[str],
        "ClientToken": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreateVpcPeeringConnectionRequestRequestTypeDef = TypedDict(
    "CreateVpcPeeringConnectionRequestRequestTypeDef",
    {
        "DryRun": bool,
        "PeerOwnerId": str,
        "PeerVpcId": str,
        "VpcId": str,
        "PeerRegion": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreateVpcPeeringConnectionRequestServiceResourceCreateVpcPeeringConnectionTypeDef = TypedDict(
    "CreateVpcPeeringConnectionRequestServiceResourceCreateVpcPeeringConnectionTypeDef",
    {
        "DryRun": bool,
        "PeerOwnerId": str,
        "PeerVpcId": str,
        "VpcId": str,
        "PeerRegion": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreateVpcPeeringConnectionRequestVpcRequestVpcPeeringConnectionTypeDef = TypedDict(
    "CreateVpcPeeringConnectionRequestVpcRequestVpcPeeringConnectionTypeDef",
    {
        "DryRun": bool,
        "PeerOwnerId": str,
        "PeerVpcId": str,
        "PeerRegion": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreateVpcRequestRequestTypeDef = TypedDict(
    "CreateVpcRequestRequestTypeDef",
    {
        "CidrBlock": str,
        "AmazonProvidedIpv6CidrBlock": bool,
        "Ipv6Pool": str,
        "Ipv6CidrBlock": str,
        "Ipv4IpamPoolId": str,
        "Ipv4NetmaskLength": int,
        "Ipv6IpamPoolId": str,
        "Ipv6NetmaskLength": int,
        "DryRun": bool,
        "InstanceTenancy": TenancyType,
        "Ipv6CidrBlockNetworkBorderGroup": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

CreateVpcRequestServiceResourceCreateVpcTypeDef = TypedDict(
    "CreateVpcRequestServiceResourceCreateVpcTypeDef",
    {
        "CidrBlock": str,
        "AmazonProvidedIpv6CidrBlock": bool,
        "Ipv6Pool": str,
        "Ipv6CidrBlock": str,
        "Ipv4IpamPoolId": str,
        "Ipv4NetmaskLength": int,
        "Ipv6IpamPoolId": str,
        "Ipv6NetmaskLength": int,
        "DryRun": bool,
        "InstanceTenancy": TenancyType,
        "Ipv6CidrBlockNetworkBorderGroup": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredCreateVpnGatewayRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpnGatewayRequestRequestTypeDef",
    {
        "Type": Literal["ipsec.1"],
    },
)
_OptionalCreateVpnGatewayRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpnGatewayRequestRequestTypeDef",
    {
        "AvailabilityZone": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "AmazonSideAsn": int,
        "DryRun": bool,
    },
    total=False,
)


class CreateVpnGatewayRequestRequestTypeDef(
    _RequiredCreateVpnGatewayRequestRequestTypeDef, _OptionalCreateVpnGatewayRequestRequestTypeDef
):
    pass


_RequiredExportImageRequestRequestTypeDef = TypedDict(
    "_RequiredExportImageRequestRequestTypeDef",
    {
        "DiskImageFormat": DiskImageFormatType,
        "ImageId": str,
        "S3ExportLocation": ExportTaskS3LocationRequestTypeDef,
    },
)
_OptionalExportImageRequestRequestTypeDef = TypedDict(
    "_OptionalExportImageRequestRequestTypeDef",
    {
        "ClientToken": str,
        "Description": str,
        "DryRun": bool,
        "RoleName": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class ExportImageRequestRequestTypeDef(
    _RequiredExportImageRequestRequestTypeDef, _OptionalExportImageRequestRequestTypeDef
):
    pass


_RequiredImportKeyPairRequestRequestTypeDef = TypedDict(
    "_RequiredImportKeyPairRequestRequestTypeDef",
    {
        "KeyName": str,
        "PublicKeyMaterial": Union[str, bytes, IO[Any], StreamingBody],
    },
)
_OptionalImportKeyPairRequestRequestTypeDef = TypedDict(
    "_OptionalImportKeyPairRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class ImportKeyPairRequestRequestTypeDef(
    _RequiredImportKeyPairRequestRequestTypeDef, _OptionalImportKeyPairRequestRequestTypeDef
):
    pass


_RequiredImportKeyPairRequestServiceResourceImportKeyPairTypeDef = TypedDict(
    "_RequiredImportKeyPairRequestServiceResourceImportKeyPairTypeDef",
    {
        "KeyName": str,
        "PublicKeyMaterial": Union[str, bytes, IO[Any], StreamingBody],
    },
)
_OptionalImportKeyPairRequestServiceResourceImportKeyPairTypeDef = TypedDict(
    "_OptionalImportKeyPairRequestServiceResourceImportKeyPairTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class ImportKeyPairRequestServiceResourceImportKeyPairTypeDef(
    _RequiredImportKeyPairRequestServiceResourceImportKeyPairTypeDef,
    _OptionalImportKeyPairRequestServiceResourceImportKeyPairTypeDef,
):
    pass


_RequiredProvisionByoipCidrRequestRequestTypeDef = TypedDict(
    "_RequiredProvisionByoipCidrRequestRequestTypeDef",
    {
        "Cidr": str,
    },
)
_OptionalProvisionByoipCidrRequestRequestTypeDef = TypedDict(
    "_OptionalProvisionByoipCidrRequestRequestTypeDef",
    {
        "CidrAuthorizationContext": CidrAuthorizationContextTypeDef,
        "PubliclyAdvertisable": bool,
        "Description": str,
        "DryRun": bool,
        "PoolTagSpecifications": Sequence[TagSpecificationTypeDef],
        "MultiRegion": bool,
    },
    total=False,
)


class ProvisionByoipCidrRequestRequestTypeDef(
    _RequiredProvisionByoipCidrRequestRequestTypeDef,
    _OptionalProvisionByoipCidrRequestRequestTypeDef,
):
    pass


_RequiredPurchaseHostReservationRequestRequestTypeDef = TypedDict(
    "_RequiredPurchaseHostReservationRequestRequestTypeDef",
    {
        "HostIdSet": Sequence[str],
        "OfferingId": str,
    },
)
_OptionalPurchaseHostReservationRequestRequestTypeDef = TypedDict(
    "_OptionalPurchaseHostReservationRequestRequestTypeDef",
    {
        "ClientToken": str,
        "CurrencyCode": Literal["USD"],
        "LimitPrice": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class PurchaseHostReservationRequestRequestTypeDef(
    _RequiredPurchaseHostReservationRequestRequestTypeDef,
    _OptionalPurchaseHostReservationRequestRequestTypeDef,
):
    pass


_RequiredStartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef = TypedDict(
    "_RequiredStartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef",
    {
        "NetworkInsightsAccessScopeId": str,
        "ClientToken": str,
    },
)
_OptionalStartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef = TypedDict(
    "_OptionalStartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef",
    {
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class StartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef(
    _RequiredStartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef,
    _OptionalStartNetworkInsightsAccessScopeAnalysisRequestRequestTypeDef,
):
    pass


_RequiredStartNetworkInsightsAnalysisRequestRequestTypeDef = TypedDict(
    "_RequiredStartNetworkInsightsAnalysisRequestRequestTypeDef",
    {
        "NetworkInsightsPathId": str,
        "ClientToken": str,
    },
)
_OptionalStartNetworkInsightsAnalysisRequestRequestTypeDef = TypedDict(
    "_OptionalStartNetworkInsightsAnalysisRequestRequestTypeDef",
    {
        "FilterInArns": Sequence[str],
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class StartNetworkInsightsAnalysisRequestRequestTypeDef(
    _RequiredStartNetworkInsightsAnalysisRequestRequestTypeDef,
    _OptionalStartNetworkInsightsAnalysisRequestRequestTypeDef,
):
    pass


CreateTrafficMirrorSessionResultTypeDef = TypedDict(
    "CreateTrafficMirrorSessionResultTypeDef",
    {
        "TrafficMirrorSession": TrafficMirrorSessionTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrafficMirrorSessionsResultTypeDef = TypedDict(
    "DescribeTrafficMirrorSessionsResultTypeDef",
    {
        "TrafficMirrorSessions": List[TrafficMirrorSessionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyTrafficMirrorSessionResultTypeDef = TypedDict(
    "ModifyTrafficMirrorSessionResultTypeDef",
    {
        "TrafficMirrorSession": TrafficMirrorSessionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTrafficMirrorTargetResultTypeDef = TypedDict(
    "CreateTrafficMirrorTargetResultTypeDef",
    {
        "TrafficMirrorTarget": TrafficMirrorTargetTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrafficMirrorTargetsResultTypeDef = TypedDict(
    "DescribeTrafficMirrorTargetsResultTypeDef",
    {
        "TrafficMirrorTargets": List[TrafficMirrorTargetTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayRouteTableResultTypeDef = TypedDict(
    "CreateTransitGatewayRouteTableResultTypeDef",
    {
        "TransitGatewayRouteTable": TransitGatewayRouteTableTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayRouteTableResultTypeDef = TypedDict(
    "DeleteTransitGatewayRouteTableResultTypeDef",
    {
        "TransitGatewayRouteTable": TransitGatewayRouteTableTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewayRouteTablesResultTypeDef = TypedDict(
    "DescribeTransitGatewayRouteTablesResultTypeDef",
    {
        "TransitGatewayRouteTables": List[TransitGatewayRouteTableTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateTrunkInterfaceResultTypeDef = TypedDict(
    "AssociateTrunkInterfaceResultTypeDef",
    {
        "InterfaceAssociation": TrunkInterfaceAssociationTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrunkInterfaceAssociationsResultTypeDef = TypedDict(
    "DescribeTrunkInterfaceAssociationsResultTypeDef",
    {
        "InterfaceAssociations": List[TrunkInterfaceAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcClassicLinkResultTypeDef = TypedDict(
    "DescribeVpcClassicLinkResultTypeDef",
    {
        "Vpcs": List[VpcClassicLinkTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExplanationTypeDef = TypedDict(
    "ExplanationTypeDef",
    {
        "Acl": AnalysisComponentTypeDef,
        "AclRule": AnalysisAclRuleTypeDef,
        "Address": str,
        "Addresses": List[str],
        "AttachedTo": AnalysisComponentTypeDef,
        "AvailabilityZones": List[str],
        "Cidrs": List[str],
        "Component": AnalysisComponentTypeDef,
        "CustomerGateway": AnalysisComponentTypeDef,
        "Destination": AnalysisComponentTypeDef,
        "DestinationVpc": AnalysisComponentTypeDef,
        "Direction": str,
        "ExplanationCode": str,
        "IngressRouteTable": AnalysisComponentTypeDef,
        "InternetGateway": AnalysisComponentTypeDef,
        "LoadBalancerArn": str,
        "ClassicLoadBalancerListener": AnalysisLoadBalancerListenerTypeDef,
        "LoadBalancerListenerPort": int,
        "LoadBalancerTarget": AnalysisLoadBalancerTargetTypeDef,
        "LoadBalancerTargetGroup": AnalysisComponentTypeDef,
        "LoadBalancerTargetGroups": List[AnalysisComponentTypeDef],
        "LoadBalancerTargetPort": int,
        "ElasticLoadBalancerListener": AnalysisComponentTypeDef,
        "MissingComponent": str,
        "NatGateway": AnalysisComponentTypeDef,
        "NetworkInterface": AnalysisComponentTypeDef,
        "PacketField": str,
        "VpcPeeringConnection": AnalysisComponentTypeDef,
        "Port": int,
        "PortRanges": List[PortRangeTypeDef],
        "PrefixList": AnalysisComponentTypeDef,
        "Protocols": List[str],
        "RouteTableRoute": AnalysisRouteTableRouteTypeDef,
        "RouteTable": AnalysisComponentTypeDef,
        "SecurityGroup": AnalysisComponentTypeDef,
        "SecurityGroupRule": AnalysisSecurityGroupRuleTypeDef,
        "SecurityGroups": List[AnalysisComponentTypeDef],
        "SourceVpc": AnalysisComponentTypeDef,
        "State": str,
        "Subnet": AnalysisComponentTypeDef,
        "SubnetRouteTable": AnalysisComponentTypeDef,
        "Vpc": AnalysisComponentTypeDef,
        "VpcEndpoint": AnalysisComponentTypeDef,
        "VpnConnection": AnalysisComponentTypeDef,
        "VpnGateway": AnalysisComponentTypeDef,
        "TransitGateway": AnalysisComponentTypeDef,
        "TransitGatewayRouteTable": AnalysisComponentTypeDef,
        "TransitGatewayRouteTableRoute": TransitGatewayRouteTableRouteTypeDef,
        "TransitGatewayAttachment": AnalysisComponentTypeDef,
    },
    total=False,
)

PathComponentTypeDef = TypedDict(
    "PathComponentTypeDef",
    {
        "SequenceNumber": int,
        "AclRule": AnalysisAclRuleTypeDef,
        "AttachedTo": AnalysisComponentTypeDef,
        "Component": AnalysisComponentTypeDef,
        "DestinationVpc": AnalysisComponentTypeDef,
        "OutboundHeader": AnalysisPacketHeaderTypeDef,
        "InboundHeader": AnalysisPacketHeaderTypeDef,
        "RouteTableRoute": AnalysisRouteTableRouteTypeDef,
        "SecurityGroupRule": AnalysisSecurityGroupRuleTypeDef,
        "SourceVpc": AnalysisComponentTypeDef,
        "Subnet": AnalysisComponentTypeDef,
        "Vpc": AnalysisComponentTypeDef,
        "AdditionalDetails": List[AdditionalDetailTypeDef],
        "TransitGateway": AnalysisComponentTypeDef,
        "TransitGatewayRouteTableRoute": TransitGatewayRouteTableRouteTypeDef,
    },
    total=False,
)

DescribeClientVpnTargetNetworksResultTypeDef = TypedDict(
    "DescribeClientVpnTargetNetworksResultTypeDef",
    {
        "ClientVpnTargetNetworks": List[TargetNetworkTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RouteTableTypeDef = TypedDict(
    "RouteTableTypeDef",
    {
        "Associations": List[RouteTableAssociationTypeDef],
        "PropagatingVgws": List[PropagatingVgwTypeDef],
        "RouteTableId": str,
        "Routes": List[RouteTypeDef],
        "Tags": List[TagTypeDef],
        "VpcId": str,
        "OwnerId": str,
    },
    total=False,
)

_RequiredGetFlowLogsIntegrationTemplateRequestRequestTypeDef = TypedDict(
    "_RequiredGetFlowLogsIntegrationTemplateRequestRequestTypeDef",
    {
        "FlowLogId": str,
        "ConfigDeliveryS3DestinationArn": str,
        "IntegrateServices": IntegrateServicesTypeDef,
    },
)
_OptionalGetFlowLogsIntegrationTemplateRequestRequestTypeDef = TypedDict(
    "_OptionalGetFlowLogsIntegrationTemplateRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class GetFlowLogsIntegrationTemplateRequestRequestTypeDef(
    _RequiredGetFlowLogsIntegrationTemplateRequestRequestTypeDef,
    _OptionalGetFlowLogsIntegrationTemplateRequestRequestTypeDef,
):
    pass


CreateVpnGatewayResultTypeDef = TypedDict(
    "CreateVpnGatewayResultTypeDef",
    {
        "VpnGateway": VpnGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpnGatewaysResultTypeDef = TypedDict(
    "DescribeVpnGatewaysResultTypeDef",
    {
        "VpnGateways": List[VpnGatewayTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DhcpOptionsTypeDef = TypedDict(
    "DhcpOptionsTypeDef",
    {
        "DhcpConfigurations": List[DhcpConfigurationTypeDef],
        "DhcpOptionsId": str,
        "OwnerId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

DescribeClientVpnAuthorizationRulesResultTypeDef = TypedDict(
    "DescribeClientVpnAuthorizationRulesResultTypeDef",
    {
        "AuthorizationRules": List[AuthorizationRuleTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAvailabilityZonesResultTypeDef = TypedDict(
    "DescribeAvailabilityZonesResultTypeDef",
    {
        "AvailabilityZones": List[AvailabilityZoneTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HostTypeDef = TypedDict(
    "HostTypeDef",
    {
        "AutoPlacement": AutoPlacementType,
        "AvailabilityZone": str,
        "AvailableCapacity": AvailableCapacityTypeDef,
        "ClientToken": str,
        "HostId": str,
        "HostProperties": HostPropertiesTypeDef,
        "HostReservationId": str,
        "Instances": List[HostInstanceTypeDef],
        "State": AllocationStateType,
        "AllocationTime": datetime,
        "ReleaseTime": datetime,
        "Tags": List[TagTypeDef],
        "HostRecovery": HostRecoveryType,
        "AllowsMultipleInstanceTypes": AllowsMultipleInstanceTypesType,
        "OwnerId": str,
        "AvailabilityZoneId": str,
        "MemberOfServiceLinkedResourceGroup": bool,
        "OutpostArn": str,
    },
    total=False,
)

_RequiredCreateImageRequestInstanceCreateImageTypeDef = TypedDict(
    "_RequiredCreateImageRequestInstanceCreateImageTypeDef",
    {
        "Name": str,
    },
)
_OptionalCreateImageRequestInstanceCreateImageTypeDef = TypedDict(
    "_OptionalCreateImageRequestInstanceCreateImageTypeDef",
    {
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "Description": str,
        "DryRun": bool,
        "NoReboot": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateImageRequestInstanceCreateImageTypeDef(
    _RequiredCreateImageRequestInstanceCreateImageTypeDef,
    _OptionalCreateImageRequestInstanceCreateImageTypeDef,
):
    pass


_RequiredCreateImageRequestRequestTypeDef = TypedDict(
    "_RequiredCreateImageRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
    },
)
_OptionalCreateImageRequestRequestTypeDef = TypedDict(
    "_OptionalCreateImageRequestRequestTypeDef",
    {
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "Description": str,
        "DryRun": bool,
        "NoReboot": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateImageRequestRequestTypeDef(
    _RequiredCreateImageRequestRequestTypeDef, _OptionalCreateImageRequestRequestTypeDef
):
    pass


ImageAttributeTypeDef = TypedDict(
    "ImageAttributeTypeDef",
    {
        "BlockDeviceMappings": List[BlockDeviceMappingTypeDef],
        "ImageId": str,
        "LaunchPermissions": List[LaunchPermissionTypeDef],
        "ProductCodes": List[ProductCodeTypeDef],
        "Description": AttributeValueTypeDef,
        "KernelId": AttributeValueTypeDef,
        "RamdiskId": AttributeValueTypeDef,
        "SriovNetSupport": AttributeValueTypeDef,
        "BootMode": AttributeValueTypeDef,
        "TpmSupport": AttributeValueTypeDef,
        "UefiData": AttributeValueTypeDef,
        "LastLaunchedTime": AttributeValueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImageTypeDef = TypedDict(
    "ImageTypeDef",
    {
        "Architecture": ArchitectureValuesType,
        "CreationDate": str,
        "ImageId": str,
        "ImageLocation": str,
        "ImageType": ImageTypeValuesType,
        "Public": bool,
        "KernelId": str,
        "OwnerId": str,
        "Platform": Literal["Windows"],
        "PlatformDetails": str,
        "UsageOperation": str,
        "ProductCodes": List[ProductCodeTypeDef],
        "RamdiskId": str,
        "State": ImageStateType,
        "BlockDeviceMappings": List[BlockDeviceMappingTypeDef],
        "Description": str,
        "EnaSupport": bool,
        "Hypervisor": HypervisorTypeType,
        "ImageOwnerAlias": str,
        "Name": str,
        "RootDeviceName": str,
        "RootDeviceType": DeviceTypeType,
        "SriovNetSupport": str,
        "StateReason": StateReasonTypeDef,
        "Tags": List[TagTypeDef],
        "VirtualizationType": VirtualizationTypeType,
        "BootMode": BootModeValuesType,
        "TpmSupport": Literal["v2.0"],
        "DeprecationTime": str,
    },
    total=False,
)

_RequiredRegisterImageRequestRequestTypeDef = TypedDict(
    "_RequiredRegisterImageRequestRequestTypeDef",
    {
        "Name": str,
    },
)
_OptionalRegisterImageRequestRequestTypeDef = TypedDict(
    "_OptionalRegisterImageRequestRequestTypeDef",
    {
        "ImageLocation": str,
        "Architecture": ArchitectureValuesType,
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "Description": str,
        "DryRun": bool,
        "EnaSupport": bool,
        "KernelId": str,
        "BillingProducts": Sequence[str],
        "RamdiskId": str,
        "RootDeviceName": str,
        "SriovNetSupport": str,
        "VirtualizationType": str,
        "BootMode": BootModeValuesType,
        "TpmSupport": Literal["v2.0"],
        "UefiData": str,
    },
    total=False,
)


class RegisterImageRequestRequestTypeDef(
    _RequiredRegisterImageRequestRequestTypeDef, _OptionalRegisterImageRequestRequestTypeDef
):
    pass


_RequiredRegisterImageRequestServiceResourceRegisterImageTypeDef = TypedDict(
    "_RequiredRegisterImageRequestServiceResourceRegisterImageTypeDef",
    {
        "Name": str,
    },
)
_OptionalRegisterImageRequestServiceResourceRegisterImageTypeDef = TypedDict(
    "_OptionalRegisterImageRequestServiceResourceRegisterImageTypeDef",
    {
        "ImageLocation": str,
        "Architecture": ArchitectureValuesType,
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "Description": str,
        "DryRun": bool,
        "EnaSupport": bool,
        "KernelId": str,
        "BillingProducts": Sequence[str],
        "RamdiskId": str,
        "RootDeviceName": str,
        "SriovNetSupport": str,
        "VirtualizationType": str,
        "BootMode": BootModeValuesType,
        "TpmSupport": Literal["v2.0"],
        "UefiData": str,
    },
    total=False,
)


class RegisterImageRequestServiceResourceRegisterImageTypeDef(
    _RequiredRegisterImageRequestServiceResourceRegisterImageTypeDef,
    _OptionalRegisterImageRequestServiceResourceRegisterImageTypeDef,
):
    pass


CancelCapacityReservationFleetsResultTypeDef = TypedDict(
    "CancelCapacityReservationFleetsResultTypeDef",
    {
        "SuccessfulFleetCancellations": List[CapacityReservationFleetCancellationStateTypeDef],
        "FailedFleetCancellations": List[FailedCapacityReservationFleetCancellationResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CancelSpotFleetRequestsResponseTypeDef = TypedDict(
    "CancelSpotFleetRequestsResponseTypeDef",
    {
        "SuccessfulFleetRequests": List[CancelSpotFleetRequestsSuccessItemTypeDef],
        "UnsuccessfulFleetRequests": List[CancelSpotFleetRequestsErrorItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCapacityReservationFleetsResultTypeDef = TypedDict(
    "DescribeCapacityReservationFleetsResultTypeDef",
    {
        "CapacityReservationFleets": List[CapacityReservationFleetTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredModifyInstanceCapacityReservationAttributesRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceCapacityReservationAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "CapacityReservationSpecification": CapacityReservationSpecificationTypeDef,
    },
)
_OptionalModifyInstanceCapacityReservationAttributesRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceCapacityReservationAttributesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyInstanceCapacityReservationAttributesRequestRequestTypeDef(
    _RequiredModifyInstanceCapacityReservationAttributesRequestRequestTypeDef,
    _OptionalModifyInstanceCapacityReservationAttributesRequestRequestTypeDef,
):
    pass


DescribeClassicLinkInstancesResultTypeDef = TypedDict(
    "DescribeClassicLinkInstancesResultTypeDef",
    {
        "Instances": List[ClassicLinkInstanceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateClientVpnEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredCreateClientVpnEndpointRequestRequestTypeDef",
    {
        "ClientCidrBlock": str,
        "ServerCertificateArn": str,
        "AuthenticationOptions": Sequence[ClientVpnAuthenticationRequestTypeDef],
        "ConnectionLogOptions": ConnectionLogOptionsTypeDef,
    },
)
_OptionalCreateClientVpnEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalCreateClientVpnEndpointRequestRequestTypeDef",
    {
        "DnsServers": Sequence[str],
        "TransportProtocol": TransportProtocolType,
        "VpnPort": int,
        "Description": str,
        "SplitTunnel": bool,
        "DryRun": bool,
        "ClientToken": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "SecurityGroupIds": Sequence[str],
        "VpcId": str,
        "SelfServicePortal": SelfServicePortalType,
        "ClientConnectOptions": ClientConnectOptionsTypeDef,
        "SessionTimeoutHours": int,
        "ClientLoginBannerOptions": ClientLoginBannerOptionsTypeDef,
    },
    total=False,
)


class CreateClientVpnEndpointRequestRequestTypeDef(
    _RequiredCreateClientVpnEndpointRequestRequestTypeDef,
    _OptionalCreateClientVpnEndpointRequestRequestTypeDef,
):
    pass


ClientVpnEndpointTypeDef = TypedDict(
    "ClientVpnEndpointTypeDef",
    {
        "ClientVpnEndpointId": str,
        "Description": str,
        "Status": ClientVpnEndpointStatusTypeDef,
        "CreationTime": str,
        "DeletionTime": str,
        "DnsName": str,
        "ClientCidrBlock": str,
        "DnsServers": List[str],
        "SplitTunnel": bool,
        "VpnProtocol": Literal["openvpn"],
        "TransportProtocol": TransportProtocolType,
        "VpnPort": int,
        "AssociatedTargetNetworks": List[AssociatedTargetNetworkTypeDef],
        "ServerCertificateArn": str,
        "AuthenticationOptions": List[ClientVpnAuthenticationTypeDef],
        "ConnectionLogOptions": ConnectionLogResponseOptionsTypeDef,
        "Tags": List[TagTypeDef],
        "SecurityGroupIds": List[str],
        "VpcId": str,
        "SelfServicePortalUrl": str,
        "ClientConnectOptions": ClientConnectResponseOptionsTypeDef,
        "SessionTimeoutHours": int,
        "ClientLoginBannerOptions": ClientLoginBannerResponseOptionsTypeDef,
    },
    total=False,
)

DescribeClientVpnConnectionsResultTypeDef = TypedDict(
    "DescribeClientVpnConnectionsResultTypeDef",
    {
        "Connections": List[ClientVpnConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TerminateClientVpnConnectionsResultTypeDef = TypedDict(
    "TerminateClientVpnConnectionsResultTypeDef",
    {
        "ClientVpnEndpointId": str,
        "Username": str,
        "ConnectionStatuses": List[TerminateConnectionStatusTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeClientVpnRoutesResultTypeDef = TypedDict(
    "DescribeClientVpnRoutesResultTypeDef",
    {
        "Routes": List[ClientVpnRouteTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkAclTypeDef = TypedDict(
    "NetworkAclTypeDef",
    {
        "Associations": List[NetworkAclAssociationTypeDef],
        "Entries": List[NetworkAclEntryTypeDef],
        "IsDefault": bool,
        "NetworkAclId": str,
        "Tags": List[TagTypeDef],
        "VpcId": str,
        "OwnerId": str,
    },
    total=False,
)

LaunchSpecificationTypeDef = TypedDict(
    "LaunchSpecificationTypeDef",
    {
        "UserData": str,
        "SecurityGroups": List[GroupIdentifierTypeDef],
        "AddressingType": str,
        "BlockDeviceMappings": List[BlockDeviceMappingTypeDef],
        "EbsOptimized": bool,
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "KernelId": str,
        "KeyName": str,
        "NetworkInterfaces": List[InstanceNetworkInterfaceSpecificationTypeDef],
        "Placement": SpotPlacementTypeDef,
        "RamdiskId": str,
        "SubnetId": str,
        "Monitoring": RunInstancesMonitoringEnabledTypeDef,
    },
    total=False,
)

RequestSpotLaunchSpecificationTypeDef = TypedDict(
    "RequestSpotLaunchSpecificationTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "SecurityGroups": Sequence[str],
        "AddressingType": str,
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "EbsOptimized": bool,
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "KernelId": str,
        "KeyName": str,
        "Monitoring": RunInstancesMonitoringEnabledTypeDef,
        "NetworkInterfaces": Sequence[InstanceNetworkInterfaceSpecificationTypeDef],
        "Placement": SpotPlacementTypeDef,
        "RamdiskId": str,
        "SubnetId": str,
        "UserData": str,
    },
    total=False,
)

_RequiredModifySnapshotAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifySnapshotAttributeRequestRequestTypeDef",
    {
        "SnapshotId": str,
    },
)
_OptionalModifySnapshotAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifySnapshotAttributeRequestRequestTypeDef",
    {
        "Attribute": SnapshotAttributeNameType,
        "CreateVolumePermission": CreateVolumePermissionModificationsTypeDef,
        "GroupNames": Sequence[str],
        "OperationType": OperationTypeType,
        "UserIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)


class ModifySnapshotAttributeRequestRequestTypeDef(
    _RequiredModifySnapshotAttributeRequestRequestTypeDef,
    _OptionalModifySnapshotAttributeRequestRequestTypeDef,
):
    pass


ModifySnapshotAttributeRequestSnapshotModifyAttributeTypeDef = TypedDict(
    "ModifySnapshotAttributeRequestSnapshotModifyAttributeTypeDef",
    {
        "Attribute": SnapshotAttributeNameType,
        "CreateVolumePermission": CreateVolumePermissionModificationsTypeDef,
        "GroupNames": Sequence[str],
        "OperationType": OperationTypeType,
        "UserIds": Sequence[str],
        "DryRun": bool,
    },
    total=False,
)

DeleteFleetsResultTypeDef = TypedDict(
    "DeleteFleetsResultTypeDef",
    {
        "SuccessfulFleetDeletions": List[DeleteFleetSuccessItemTypeDef],
        "UnsuccessfulFleetDeletions": List[DeleteFleetErrorItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLaunchTemplateVersionsResultTypeDef = TypedDict(
    "DeleteLaunchTemplateVersionsResultTypeDef",
    {
        "SuccessfullyDeletedLaunchTemplateVersions": List[
            DeleteLaunchTemplateVersionsResponseSuccessItemTypeDef
        ],
        "UnsuccessfullyDeletedLaunchTemplateVersions": List[
            DeleteLaunchTemplateVersionsResponseErrorItemTypeDef
        ],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteQueuedReservedInstancesResultTypeDef = TypedDict(
    "DeleteQueuedReservedInstancesResultTypeDef",
    {
        "SuccessfulQueuedPurchaseDeletions": List[SuccessfulQueuedPurchaseDeletionTypeDef],
        "FailedQueuedPurchaseDeletions": List[FailedQueuedPurchaseDeletionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePrincipalIdFormatResultTypeDef = TypedDict(
    "DescribePrincipalIdFormatResultTypeDef",
    {
        "Principals": List[PrincipalIdFormatTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFastLaunchImagesResultTypeDef = TypedDict(
    "DescribeFastLaunchImagesResultTypeDef",
    {
        "FastLaunchImages": List[DescribeFastLaunchImagesSuccessItemTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFlowLogsResultTypeDef = TypedDict(
    "DescribeFlowLogsResultTypeDef",
    {
        "FlowLogs": List[FlowLogTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableFastSnapshotRestoreErrorItemTypeDef = TypedDict(
    "DisableFastSnapshotRestoreErrorItemTypeDef",
    {
        "SnapshotId": str,
        "FastSnapshotRestoreStateErrors": List[DisableFastSnapshotRestoreStateErrorItemTypeDef],
    },
    total=False,
)

ImportInstanceTaskDetailsTypeDef = TypedDict(
    "ImportInstanceTaskDetailsTypeDef",
    {
        "Description": str,
        "InstanceId": str,
        "Platform": Literal["Windows"],
        "Volumes": List[ImportInstanceVolumeDetailItemTypeDef],
    },
    total=False,
)

DescribeVpcEndpointConnectionsResultTypeDef = TypedDict(
    "DescribeVpcEndpointConnectionsResultTypeDef",
    {
        "VpcEndpointConnections": List[VpcEndpointConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyInstanceAttributeRequestInstanceModifyAttributeTypeDef = TypedDict(
    "ModifyInstanceAttributeRequestInstanceModifyAttributeTypeDef",
    {
        "SourceDestCheck": AttributeBooleanValueTypeDef,
        "Attribute": InstanceAttributeNameType,
        "BlockDeviceMappings": Sequence[InstanceBlockDeviceMappingSpecificationTypeDef],
        "DisableApiTermination": AttributeBooleanValueTypeDef,
        "DryRun": bool,
        "EbsOptimized": AttributeBooleanValueTypeDef,
        "EnaSupport": AttributeBooleanValueTypeDef,
        "Groups": Sequence[str],
        "InstanceInitiatedShutdownBehavior": AttributeValueTypeDef,
        "InstanceType": AttributeValueTypeDef,
        "Kernel": AttributeValueTypeDef,
        "Ramdisk": AttributeValueTypeDef,
        "SriovNetSupport": AttributeValueTypeDef,
        "UserData": BlobAttributeValueTypeDef,
        "Value": str,
        "DisableApiStop": AttributeBooleanValueTypeDef,
    },
    total=False,
)

_RequiredModifyInstanceAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyInstanceAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
_OptionalModifyInstanceAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyInstanceAttributeRequestRequestTypeDef",
    {
        "SourceDestCheck": AttributeBooleanValueTypeDef,
        "Attribute": InstanceAttributeNameType,
        "BlockDeviceMappings": Sequence[InstanceBlockDeviceMappingSpecificationTypeDef],
        "DisableApiTermination": AttributeBooleanValueTypeDef,
        "DryRun": bool,
        "EbsOptimized": AttributeBooleanValueTypeDef,
        "EnaSupport": AttributeBooleanValueTypeDef,
        "Groups": Sequence[str],
        "InstanceInitiatedShutdownBehavior": AttributeValueTypeDef,
        "InstanceType": AttributeValueTypeDef,
        "Kernel": AttributeValueTypeDef,
        "Ramdisk": AttributeValueTypeDef,
        "SriovNetSupport": AttributeValueTypeDef,
        "UserData": BlobAttributeValueTypeDef,
        "Value": str,
        "DisableApiStop": AttributeBooleanValueTypeDef,
    },
    total=False,
)


class ModifyInstanceAttributeRequestRequestTypeDef(
    _RequiredModifyInstanceAttributeRequestRequestTypeDef,
    _OptionalModifyInstanceAttributeRequestRequestTypeDef,
):
    pass


InstanceAttributeTypeDef = TypedDict(
    "InstanceAttributeTypeDef",
    {
        "Groups": List[GroupIdentifierTypeDef],
        "BlockDeviceMappings": List[InstanceBlockDeviceMappingTypeDef],
        "DisableApiTermination": AttributeBooleanValueTypeDef,
        "EnaSupport": AttributeBooleanValueTypeDef,
        "EnclaveOptions": EnclaveOptionsTypeDef,
        "EbsOptimized": AttributeBooleanValueTypeDef,
        "InstanceId": str,
        "InstanceInitiatedShutdownBehavior": AttributeValueTypeDef,
        "InstanceType": AttributeValueTypeDef,
        "KernelId": AttributeValueTypeDef,
        "ProductCodes": List[ProductCodeTypeDef],
        "RamdiskId": AttributeValueTypeDef,
        "RootDeviceName": AttributeValueTypeDef,
        "SourceDestCheck": AttributeBooleanValueTypeDef,
        "SriovNetSupport": AttributeValueTypeDef,
        "UserData": AttributeValueTypeDef,
        "DisableApiStop": AttributeBooleanValueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEgressOnlyInternetGatewayResultTypeDef = TypedDict(
    "CreateEgressOnlyInternetGatewayResultTypeDef",
    {
        "ClientToken": str,
        "EgressOnlyInternetGateway": EgressOnlyInternetGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEgressOnlyInternetGatewaysResultTypeDef = TypedDict(
    "DescribeEgressOnlyInternetGatewaysResultTypeDef",
    {
        "EgressOnlyInternetGateways": List[EgressOnlyInternetGatewayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInternetGatewayResultTypeDef = TypedDict(
    "CreateInternetGatewayResultTypeDef",
    {
        "InternetGateway": InternetGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInternetGatewaysResultTypeDef = TypedDict(
    "DescribeInternetGatewaysResultTypeDef",
    {
        "InternetGateways": List[InternetGatewayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeElasticGpusResultTypeDef = TypedDict(
    "DescribeElasticGpusResultTypeDef",
    {
        "ElasticGpuSet": List[ElasticGpusTypeDef],
        "MaxResults": int,
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableFastSnapshotRestoreErrorItemTypeDef = TypedDict(
    "EnableFastSnapshotRestoreErrorItemTypeDef",
    {
        "SnapshotId": str,
        "FastSnapshotRestoreStateErrors": List[EnableFastSnapshotRestoreStateErrorItemTypeDef],
    },
    total=False,
)

DescribeFleetHistoryResultTypeDef = TypedDict(
    "DescribeFleetHistoryResultTypeDef",
    {
        "HistoryRecords": List[HistoryRecordEntryTypeDef],
        "LastEvaluatedTime": datetime,
        "NextToken": str,
        "FleetId": str,
        "StartTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpotFleetRequestHistoryResponseTypeDef = TypedDict(
    "DescribeSpotFleetRequestHistoryResponseTypeDef",
    {
        "HistoryRecords": List[HistoryRecordTypeDef],
        "LastEvaluatedTime": datetime,
        "NextToken": str,
        "SpotFleetRequestId": str,
        "StartTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeExportImageTasksResultTypeDef = TypedDict(
    "DescribeExportImageTasksResultTypeDef",
    {
        "ExportImageTasks": List[ExportImageTaskTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInstanceExportTaskResultTypeDef = TypedDict(
    "CreateInstanceExportTaskResultTypeDef",
    {
        "ExportTask": ExportTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeExportTasksResultTypeDef = TypedDict(
    "DescribeExportTasksResultTypeDef",
    {
        "ExportTasks": List[ExportTaskTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SpotOptionsRequestTypeDef = TypedDict(
    "SpotOptionsRequestTypeDef",
    {
        "AllocationStrategy": SpotAllocationStrategyType,
        "MaintenanceStrategies": FleetSpotMaintenanceStrategiesRequestTypeDef,
        "InstanceInterruptionBehavior": SpotInstanceInterruptionBehaviorType,
        "InstancePoolsToUseCount": int,
        "SingleInstanceType": bool,
        "SingleAvailabilityZone": bool,
        "MinTargetCapacity": int,
        "MaxTotalPrice": str,
    },
    total=False,
)

SpotOptionsTypeDef = TypedDict(
    "SpotOptionsTypeDef",
    {
        "AllocationStrategy": SpotAllocationStrategyType,
        "MaintenanceStrategies": FleetSpotMaintenanceStrategiesTypeDef,
        "InstanceInterruptionBehavior": SpotInstanceInterruptionBehaviorType,
        "InstancePoolsToUseCount": int,
        "SingleInstanceType": bool,
        "SingleAvailabilityZone": bool,
        "MinTargetCapacity": int,
        "MaxTotalPrice": str,
    },
    total=False,
)

FpgaInfoTypeDef = TypedDict(
    "FpgaInfoTypeDef",
    {
        "Fpgas": List[FpgaDeviceInfoTypeDef],
        "TotalFpgaMemoryInMiB": int,
    },
    total=False,
)

DescribeFpgaImageAttributeResultTypeDef = TypedDict(
    "DescribeFpgaImageAttributeResultTypeDef",
    {
        "FpgaImageAttribute": FpgaImageAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyFpgaImageAttributeResultTypeDef = TypedDict(
    "ModifyFpgaImageAttributeResultTypeDef",
    {
        "FpgaImageAttribute": FpgaImageAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFpgaImagesResultTypeDef = TypedDict(
    "DescribeFpgaImagesResultTypeDef",
    {
        "FpgaImages": List[FpgaImageTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GpuInfoTypeDef = TypedDict(
    "GpuInfoTypeDef",
    {
        "Gpus": List[GpuDeviceInfoTypeDef],
        "TotalGpuMemoryInMiB": int,
    },
    total=False,
)

AssociateIamInstanceProfileResultTypeDef = TypedDict(
    "AssociateIamInstanceProfileResultTypeDef",
    {
        "IamInstanceProfileAssociation": IamInstanceProfileAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIamInstanceProfileAssociationsResultTypeDef = TypedDict(
    "DescribeIamInstanceProfileAssociationsResultTypeDef",
    {
        "IamInstanceProfileAssociations": List[IamInstanceProfileAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateIamInstanceProfileResultTypeDef = TypedDict(
    "DisassociateIamInstanceProfileResultTypeDef",
    {
        "IamInstanceProfileAssociation": IamInstanceProfileAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplaceIamInstanceProfileAssociationResultTypeDef = TypedDict(
    "ReplaceIamInstanceProfileAssociationResultTypeDef",
    {
        "IamInstanceProfileAssociation": IamInstanceProfileAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyImageAttributeRequestImageModifyAttributeTypeDef = TypedDict(
    "ModifyImageAttributeRequestImageModifyAttributeTypeDef",
    {
        "Attribute": str,
        "Description": AttributeValueTypeDef,
        "LaunchPermission": LaunchPermissionModificationsTypeDef,
        "OperationType": OperationTypeType,
        "ProductCodes": Sequence[str],
        "UserGroups": Sequence[str],
        "UserIds": Sequence[str],
        "Value": str,
        "DryRun": bool,
        "OrganizationArns": Sequence[str],
        "OrganizationalUnitArns": Sequence[str],
    },
    total=False,
)

_RequiredModifyImageAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyImageAttributeRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalModifyImageAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyImageAttributeRequestRequestTypeDef",
    {
        "Attribute": str,
        "Description": AttributeValueTypeDef,
        "LaunchPermission": LaunchPermissionModificationsTypeDef,
        "OperationType": OperationTypeType,
        "ProductCodes": Sequence[str],
        "UserGroups": Sequence[str],
        "UserIds": Sequence[str],
        "Value": str,
        "DryRun": bool,
        "OrganizationArns": Sequence[str],
        "OrganizationalUnitArns": Sequence[str],
    },
    total=False,
)


class ModifyImageAttributeRequestRequestTypeDef(
    _RequiredModifyImageAttributeRequestRequestTypeDef,
    _OptionalModifyImageAttributeRequestRequestTypeDef,
):
    pass


ImportImageRequestRequestTypeDef = TypedDict(
    "ImportImageRequestRequestTypeDef",
    {
        "Architecture": str,
        "ClientData": ClientDataTypeDef,
        "ClientToken": str,
        "Description": str,
        "DiskContainers": Sequence[ImageDiskContainerTypeDef],
        "DryRun": bool,
        "Encrypted": bool,
        "Hypervisor": str,
        "KmsKeyId": str,
        "LicenseType": str,
        "Platform": str,
        "RoleName": str,
        "LicenseSpecifications": Sequence[ImportImageLicenseConfigurationRequestTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "UsageOperation": str,
        "BootMode": BootModeValuesType,
    },
    total=False,
)

ImportSnapshotRequestRequestTypeDef = TypedDict(
    "ImportSnapshotRequestRequestTypeDef",
    {
        "ClientData": ClientDataTypeDef,
        "ClientToken": str,
        "Description": str,
        "DiskContainer": SnapshotDiskContainerTypeDef,
        "DryRun": bool,
        "Encrypted": bool,
        "KmsKeyId": str,
        "RoleName": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredImportInstanceRequestRequestTypeDef = TypedDict(
    "_RequiredImportInstanceRequestRequestTypeDef",
    {
        "Platform": Literal["Windows"],
    },
)
_OptionalImportInstanceRequestRequestTypeDef = TypedDict(
    "_OptionalImportInstanceRequestRequestTypeDef",
    {
        "Description": str,
        "DiskImages": Sequence[DiskImageTypeDef],
        "DryRun": bool,
        "LaunchSpecification": ImportInstanceLaunchSpecificationTypeDef,
    },
    total=False,
)


class ImportInstanceRequestRequestTypeDef(
    _RequiredImportInstanceRequestRequestTypeDef, _OptionalImportInstanceRequestRequestTypeDef
):
    pass


_RequiredRunInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredRunInstancesRequestRequestTypeDef",
    {
        "MaxCount": int,
        "MinCount": int,
    },
)
_OptionalRunInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalRunInstancesRequestRequestTypeDef",
    {
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressTypeDef],
        "KernelId": str,
        "KeyName": str,
        "Monitoring": RunInstancesMonitoringEnabledTypeDef,
        "Placement": PlacementTypeDef,
        "RamdiskId": str,
        "SecurityGroupIds": Sequence[str],
        "SecurityGroups": Sequence[str],
        "SubnetId": str,
        "UserData": str,
        "AdditionalInfo": str,
        "ClientToken": str,
        "DisableApiTermination": bool,
        "DryRun": bool,
        "EbsOptimized": bool,
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "InstanceInitiatedShutdownBehavior": ShutdownBehaviorType,
        "NetworkInterfaces": Sequence[InstanceNetworkInterfaceSpecificationTypeDef],
        "PrivateIpAddress": str,
        "ElasticGpuSpecification": Sequence[ElasticGpuSpecificationTypeDef],
        "ElasticInferenceAccelerators": Sequence[ElasticInferenceAcceleratorTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "LaunchTemplate": LaunchTemplateSpecificationTypeDef,
        "InstanceMarketOptions": InstanceMarketOptionsRequestTypeDef,
        "CreditSpecification": CreditSpecificationRequestTypeDef,
        "CpuOptions": CpuOptionsRequestTypeDef,
        "CapacityReservationSpecification": CapacityReservationSpecificationTypeDef,
        "HibernationOptions": HibernationOptionsRequestTypeDef,
        "LicenseSpecifications": Sequence[LicenseConfigurationRequestTypeDef],
        "MetadataOptions": InstanceMetadataOptionsRequestTypeDef,
        "EnclaveOptions": EnclaveOptionsRequestTypeDef,
        "PrivateDnsNameOptions": PrivateDnsNameOptionsRequestTypeDef,
        "MaintenanceOptions": InstanceMaintenanceOptionsRequestTypeDef,
        "DisableApiStop": bool,
    },
    total=False,
)


class RunInstancesRequestRequestTypeDef(
    _RequiredRunInstancesRequestRequestTypeDef, _OptionalRunInstancesRequestRequestTypeDef
):
    pass


_RequiredRunInstancesRequestServiceResourceCreateInstancesTypeDef = TypedDict(
    "_RequiredRunInstancesRequestServiceResourceCreateInstancesTypeDef",
    {
        "MaxCount": int,
        "MinCount": int,
    },
)
_OptionalRunInstancesRequestServiceResourceCreateInstancesTypeDef = TypedDict(
    "_OptionalRunInstancesRequestServiceResourceCreateInstancesTypeDef",
    {
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressTypeDef],
        "KernelId": str,
        "KeyName": str,
        "Monitoring": RunInstancesMonitoringEnabledTypeDef,
        "Placement": PlacementTypeDef,
        "RamdiskId": str,
        "SecurityGroupIds": Sequence[str],
        "SecurityGroups": Sequence[str],
        "SubnetId": str,
        "UserData": str,
        "AdditionalInfo": str,
        "ClientToken": str,
        "DisableApiTermination": bool,
        "DryRun": bool,
        "EbsOptimized": bool,
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "InstanceInitiatedShutdownBehavior": ShutdownBehaviorType,
        "NetworkInterfaces": Sequence[InstanceNetworkInterfaceSpecificationTypeDef],
        "PrivateIpAddress": str,
        "ElasticGpuSpecification": Sequence[ElasticGpuSpecificationTypeDef],
        "ElasticInferenceAccelerators": Sequence[ElasticInferenceAcceleratorTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "LaunchTemplate": LaunchTemplateSpecificationTypeDef,
        "InstanceMarketOptions": InstanceMarketOptionsRequestTypeDef,
        "CreditSpecification": CreditSpecificationRequestTypeDef,
        "CpuOptions": CpuOptionsRequestTypeDef,
        "CapacityReservationSpecification": CapacityReservationSpecificationTypeDef,
        "HibernationOptions": HibernationOptionsRequestTypeDef,
        "LicenseSpecifications": Sequence[LicenseConfigurationRequestTypeDef],
        "MetadataOptions": InstanceMetadataOptionsRequestTypeDef,
        "EnclaveOptions": EnclaveOptionsRequestTypeDef,
        "PrivateDnsNameOptions": PrivateDnsNameOptionsRequestTypeDef,
        "MaintenanceOptions": InstanceMaintenanceOptionsRequestTypeDef,
        "DisableApiStop": bool,
    },
    total=False,
)


class RunInstancesRequestServiceResourceCreateInstancesTypeDef(
    _RequiredRunInstancesRequestServiceResourceCreateInstancesTypeDef,
    _OptionalRunInstancesRequestServiceResourceCreateInstancesTypeDef,
):
    pass


_RequiredRunInstancesRequestSubnetCreateInstancesTypeDef = TypedDict(
    "_RequiredRunInstancesRequestSubnetCreateInstancesTypeDef",
    {
        "MaxCount": int,
        "MinCount": int,
    },
)
_OptionalRunInstancesRequestSubnetCreateInstancesTypeDef = TypedDict(
    "_OptionalRunInstancesRequestSubnetCreateInstancesTypeDef",
    {
        "BlockDeviceMappings": Sequence[BlockDeviceMappingTypeDef],
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "Ipv6AddressCount": int,
        "Ipv6Addresses": Sequence[InstanceIpv6AddressTypeDef],
        "KernelId": str,
        "KeyName": str,
        "Monitoring": RunInstancesMonitoringEnabledTypeDef,
        "Placement": PlacementTypeDef,
        "RamdiskId": str,
        "SecurityGroupIds": Sequence[str],
        "SecurityGroups": Sequence[str],
        "UserData": str,
        "AdditionalInfo": str,
        "ClientToken": str,
        "DisableApiTermination": bool,
        "DryRun": bool,
        "EbsOptimized": bool,
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "InstanceInitiatedShutdownBehavior": ShutdownBehaviorType,
        "NetworkInterfaces": Sequence[InstanceNetworkInterfaceSpecificationTypeDef],
        "PrivateIpAddress": str,
        "ElasticGpuSpecification": Sequence[ElasticGpuSpecificationTypeDef],
        "ElasticInferenceAccelerators": Sequence[ElasticInferenceAcceleratorTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "LaunchTemplate": LaunchTemplateSpecificationTypeDef,
        "InstanceMarketOptions": InstanceMarketOptionsRequestTypeDef,
        "CreditSpecification": CreditSpecificationRequestTypeDef,
        "CpuOptions": CpuOptionsRequestTypeDef,
        "CapacityReservationSpecification": CapacityReservationSpecificationTypeDef,
        "HibernationOptions": HibernationOptionsRequestTypeDef,
        "LicenseSpecifications": Sequence[LicenseConfigurationRequestTypeDef],
        "MetadataOptions": InstanceMetadataOptionsRequestTypeDef,
        "EnclaveOptions": EnclaveOptionsRequestTypeDef,
        "PrivateDnsNameOptions": PrivateDnsNameOptionsRequestTypeDef,
        "MaintenanceOptions": InstanceMaintenanceOptionsRequestTypeDef,
        "DisableApiStop": bool,
    },
    total=False,
)


class RunInstancesRequestSubnetCreateInstancesTypeDef(
    _RequiredRunInstancesRequestSubnetCreateInstancesTypeDef,
    _OptionalRunInstancesRequestSubnetCreateInstancesTypeDef,
):
    pass


MonitorInstancesResultTypeDef = TypedDict(
    "MonitorInstancesResultTypeDef",
    {
        "InstanceMonitorings": List[InstanceMonitoringTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UnmonitorInstancesResultTypeDef = TypedDict(
    "UnmonitorInstancesResultTypeDef",
    {
        "InstanceMonitorings": List[InstanceMonitoringTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceNetworkInterfaceTypeDef = TypedDict(
    "InstanceNetworkInterfaceTypeDef",
    {
        "Association": InstanceNetworkInterfaceAssociationTypeDef,
        "Attachment": InstanceNetworkInterfaceAttachmentTypeDef,
        "Description": str,
        "Groups": List[GroupIdentifierTypeDef],
        "Ipv6Addresses": List[InstanceIpv6AddressTypeDef],
        "MacAddress": str,
        "NetworkInterfaceId": str,
        "OwnerId": str,
        "PrivateDnsName": str,
        "PrivateIpAddress": str,
        "PrivateIpAddresses": List[InstancePrivateIpAddressTypeDef],
        "SourceDestCheck": bool,
        "Status": NetworkInterfaceStatusType,
        "SubnetId": str,
        "VpcId": str,
        "InterfaceType": str,
        "Ipv4Prefixes": List[InstanceIpv4PrefixTypeDef],
        "Ipv6Prefixes": List[InstanceIpv6PrefixTypeDef],
    },
    total=False,
)

FleetLaunchTemplateOverridesRequestTypeDef = TypedDict(
    "FleetLaunchTemplateOverridesRequestTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "MaxPrice": str,
        "SubnetId": str,
        "AvailabilityZone": str,
        "WeightedCapacity": float,
        "Priority": float,
        "Placement": PlacementTypeDef,
        "InstanceRequirements": InstanceRequirementsRequestTypeDef,
    },
    total=False,
)

_RequiredGetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef = TypedDict(
    "_RequiredGetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef",
    {
        "ArchitectureTypes": Sequence[ArchitectureTypeType],
        "VirtualizationTypes": Sequence[VirtualizationTypeType],
        "InstanceRequirements": InstanceRequirementsRequestTypeDef,
    },
)
_OptionalGetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef = TypedDict(
    "_OptionalGetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef",
    {
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef(
    _RequiredGetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef,
    _OptionalGetInstanceTypesFromInstanceRequirementsRequestGetInstanceTypesFromInstanceRequirementsPaginateTypeDef,
):
    pass


_RequiredGetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef = TypedDict(
    "_RequiredGetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef",
    {
        "ArchitectureTypes": Sequence[ArchitectureTypeType],
        "VirtualizationTypes": Sequence[VirtualizationTypeType],
        "InstanceRequirements": InstanceRequirementsRequestTypeDef,
    },
)
_OptionalGetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef = TypedDict(
    "_OptionalGetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef",
    {
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef(
    _RequiredGetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef,
    _OptionalGetInstanceTypesFromInstanceRequirementsRequestRequestTypeDef,
):
    pass


InstanceRequirementsWithMetadataRequestTypeDef = TypedDict(
    "InstanceRequirementsWithMetadataRequestTypeDef",
    {
        "ArchitectureTypes": Sequence[ArchitectureTypeType],
        "VirtualizationTypes": Sequence[VirtualizationTypeType],
        "InstanceRequirements": InstanceRequirementsRequestTypeDef,
    },
    total=False,
)

FleetLaunchTemplateOverridesTypeDef = TypedDict(
    "FleetLaunchTemplateOverridesTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "MaxPrice": str,
        "SubnetId": str,
        "AvailabilityZone": str,
        "WeightedCapacity": float,
        "Priority": float,
        "Placement": PlacementResponseTypeDef,
        "InstanceRequirements": InstanceRequirementsTypeDef,
    },
    total=False,
)

LaunchTemplateOverridesTypeDef = TypedDict(
    "LaunchTemplateOverridesTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "SpotPrice": str,
        "SubnetId": str,
        "AvailabilityZone": str,
        "WeightedCapacity": float,
        "Priority": float,
        "InstanceRequirements": InstanceRequirementsTypeDef,
    },
    total=False,
)

SpotFleetLaunchSpecificationTypeDef = TypedDict(
    "SpotFleetLaunchSpecificationTypeDef",
    {
        "SecurityGroups": List[GroupIdentifierTypeDef],
        "AddressingType": str,
        "BlockDeviceMappings": List[BlockDeviceMappingTypeDef],
        "EbsOptimized": bool,
        "IamInstanceProfile": IamInstanceProfileSpecificationTypeDef,
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "KernelId": str,
        "KeyName": str,
        "Monitoring": SpotFleetMonitoringTypeDef,
        "NetworkInterfaces": List[InstanceNetworkInterfaceSpecificationTypeDef],
        "Placement": SpotPlacementTypeDef,
        "RamdiskId": str,
        "SpotPrice": str,
        "SubnetId": str,
        "UserData": str,
        "WeightedCapacity": float,
        "TagSpecifications": List[SpotFleetTagSpecificationTypeDef],
        "InstanceRequirements": InstanceRequirementsTypeDef,
    },
    total=False,
)

StartInstancesResultTypeDef = TypedDict(
    "StartInstancesResultTypeDef",
    {
        "StartingInstances": List[InstanceStateChangeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopInstancesResultTypeDef = TypedDict(
    "StopInstancesResultTypeDef",
    {
        "StoppingInstances": List[InstanceStateChangeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TerminateInstancesResultTypeDef = TypedDict(
    "TerminateInstancesResultTypeDef",
    {
        "TerminatingInstances": List[InstanceStateChangeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceStatusTypeDef = TypedDict(
    "InstanceStatusTypeDef",
    {
        "AvailabilityZone": str,
        "OutpostArn": str,
        "Events": List[InstanceStatusEventTypeDef],
        "InstanceId": str,
        "InstanceState": InstanceStateTypeDef,
        "InstanceStatus": InstanceStatusSummaryTypeDef,
        "SystemStatus": InstanceStatusSummaryTypeDef,
    },
    total=False,
)

_RequiredAuthorizeSecurityGroupEgressRequestRequestTypeDef = TypedDict(
    "_RequiredAuthorizeSecurityGroupEgressRequestRequestTypeDef",
    {
        "GroupId": str,
    },
)
_OptionalAuthorizeSecurityGroupEgressRequestRequestTypeDef = TypedDict(
    "_OptionalAuthorizeSecurityGroupEgressRequestRequestTypeDef",
    {
        "DryRun": bool,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "CidrIp": str,
        "FromPort": int,
        "IpProtocol": str,
        "ToPort": int,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
    },
    total=False,
)


class AuthorizeSecurityGroupEgressRequestRequestTypeDef(
    _RequiredAuthorizeSecurityGroupEgressRequestRequestTypeDef,
    _OptionalAuthorizeSecurityGroupEgressRequestRequestTypeDef,
):
    pass


AuthorizeSecurityGroupEgressRequestSecurityGroupAuthorizeEgressTypeDef = TypedDict(
    "AuthorizeSecurityGroupEgressRequestSecurityGroupAuthorizeEgressTypeDef",
    {
        "DryRun": bool,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "CidrIp": str,
        "FromPort": int,
        "IpProtocol": str,
        "ToPort": int,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
    },
    total=False,
)

AuthorizeSecurityGroupIngressRequestRequestTypeDef = TypedDict(
    "AuthorizeSecurityGroupIngressRequestRequestTypeDef",
    {
        "CidrIp": str,
        "FromPort": int,
        "GroupId": str,
        "GroupName": str,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "IpProtocol": str,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
        "ToPort": int,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

AuthorizeSecurityGroupIngressRequestSecurityGroupAuthorizeIngressTypeDef = TypedDict(
    "AuthorizeSecurityGroupIngressRequestSecurityGroupAuthorizeIngressTypeDef",
    {
        "CidrIp": str,
        "FromPort": int,
        "GroupName": str,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "IpProtocol": str,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
        "ToPort": int,
        "DryRun": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)

_RequiredRevokeSecurityGroupEgressRequestRequestTypeDef = TypedDict(
    "_RequiredRevokeSecurityGroupEgressRequestRequestTypeDef",
    {
        "GroupId": str,
    },
)
_OptionalRevokeSecurityGroupEgressRequestRequestTypeDef = TypedDict(
    "_OptionalRevokeSecurityGroupEgressRequestRequestTypeDef",
    {
        "DryRun": bool,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "SecurityGroupRuleIds": Sequence[str],
        "CidrIp": str,
        "FromPort": int,
        "IpProtocol": str,
        "ToPort": int,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
    },
    total=False,
)


class RevokeSecurityGroupEgressRequestRequestTypeDef(
    _RequiredRevokeSecurityGroupEgressRequestRequestTypeDef,
    _OptionalRevokeSecurityGroupEgressRequestRequestTypeDef,
):
    pass


RevokeSecurityGroupEgressRequestSecurityGroupRevokeEgressTypeDef = TypedDict(
    "RevokeSecurityGroupEgressRequestSecurityGroupRevokeEgressTypeDef",
    {
        "DryRun": bool,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "SecurityGroupRuleIds": Sequence[str],
        "CidrIp": str,
        "FromPort": int,
        "IpProtocol": str,
        "ToPort": int,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
    },
    total=False,
)

RevokeSecurityGroupEgressResultTypeDef = TypedDict(
    "RevokeSecurityGroupEgressResultTypeDef",
    {
        "Return": bool,
        "UnknownIpPermissions": List[IpPermissionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RevokeSecurityGroupIngressRequestRequestTypeDef = TypedDict(
    "RevokeSecurityGroupIngressRequestRequestTypeDef",
    {
        "CidrIp": str,
        "FromPort": int,
        "GroupId": str,
        "GroupName": str,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "IpProtocol": str,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
        "ToPort": int,
        "DryRun": bool,
        "SecurityGroupRuleIds": Sequence[str],
    },
    total=False,
)

RevokeSecurityGroupIngressRequestSecurityGroupRevokeIngressTypeDef = TypedDict(
    "RevokeSecurityGroupIngressRequestSecurityGroupRevokeIngressTypeDef",
    {
        "CidrIp": str,
        "FromPort": int,
        "GroupName": str,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "IpProtocol": str,
        "SourceSecurityGroupName": str,
        "SourceSecurityGroupOwnerId": str,
        "ToPort": int,
        "DryRun": bool,
        "SecurityGroupRuleIds": Sequence[str],
    },
    total=False,
)

RevokeSecurityGroupIngressResultTypeDef = TypedDict(
    "RevokeSecurityGroupIngressResultTypeDef",
    {
        "Return": bool,
        "UnknownIpPermissions": List[IpPermissionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SecurityGroupTypeDef = TypedDict(
    "SecurityGroupTypeDef",
    {
        "Description": str,
        "GroupName": str,
        "IpPermissions": List[IpPermissionTypeDef],
        "OwnerId": str,
        "GroupId": str,
        "IpPermissionsEgress": List[IpPermissionTypeDef],
        "Tags": List[TagTypeDef],
        "VpcId": str,
    },
    total=False,
)

UpdateSecurityGroupRuleDescriptionsEgressRequestRequestTypeDef = TypedDict(
    "UpdateSecurityGroupRuleDescriptionsEgressRequestRequestTypeDef",
    {
        "DryRun": bool,
        "GroupId": str,
        "GroupName": str,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "SecurityGroupRuleDescriptions": Sequence[SecurityGroupRuleDescriptionTypeDef],
    },
    total=False,
)

UpdateSecurityGroupRuleDescriptionsIngressRequestRequestTypeDef = TypedDict(
    "UpdateSecurityGroupRuleDescriptionsIngressRequestRequestTypeDef",
    {
        "DryRun": bool,
        "GroupId": str,
        "GroupName": str,
        "IpPermissions": Sequence[IpPermissionTypeDef],
        "SecurityGroupRuleDescriptions": Sequence[SecurityGroupRuleDescriptionTypeDef],
    },
    total=False,
)

StaleSecurityGroupTypeDef = TypedDict(
    "StaleSecurityGroupTypeDef",
    {
        "Description": str,
        "GroupId": str,
        "GroupName": str,
        "StaleIpPermissions": List[StaleIpPermissionTypeDef],
        "StaleIpPermissionsEgress": List[StaleIpPermissionTypeDef],
        "VpcId": str,
    },
    total=False,
)

CreateIpamResultTypeDef = TypedDict(
    "CreateIpamResultTypeDef",
    {
        "Ipam": IpamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteIpamResultTypeDef = TypedDict(
    "DeleteIpamResultTypeDef",
    {
        "Ipam": IpamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIpamsResultTypeDef = TypedDict(
    "DescribeIpamsResultTypeDef",
    {
        "NextToken": str,
        "Ipams": List[IpamTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyIpamResultTypeDef = TypedDict(
    "ModifyIpamResultTypeDef",
    {
        "Ipam": IpamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeprovisionIpamPoolCidrResultTypeDef = TypedDict(
    "DeprovisionIpamPoolCidrResultTypeDef",
    {
        "IpamPoolCidr": IpamPoolCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetIpamPoolCidrsResultTypeDef = TypedDict(
    "GetIpamPoolCidrsResultTypeDef",
    {
        "IpamPoolCidrs": List[IpamPoolCidrTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ProvisionIpamPoolCidrResultTypeDef = TypedDict(
    "ProvisionIpamPoolCidrResultTypeDef",
    {
        "IpamPoolCidr": IpamPoolCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateIpamPoolResultTypeDef = TypedDict(
    "CreateIpamPoolResultTypeDef",
    {
        "IpamPool": IpamPoolTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteIpamPoolResultTypeDef = TypedDict(
    "DeleteIpamPoolResultTypeDef",
    {
        "IpamPool": IpamPoolTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIpamPoolsResultTypeDef = TypedDict(
    "DescribeIpamPoolsResultTypeDef",
    {
        "NextToken": str,
        "IpamPools": List[IpamPoolTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyIpamPoolResultTypeDef = TypedDict(
    "ModifyIpamPoolResultTypeDef",
    {
        "IpamPool": IpamPoolTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetIpamResourceCidrsResultTypeDef = TypedDict(
    "GetIpamResourceCidrsResultTypeDef",
    {
        "NextToken": str,
        "IpamResourceCidrs": List[IpamResourceCidrTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyIpamResourceCidrResultTypeDef = TypedDict(
    "ModifyIpamResourceCidrResultTypeDef",
    {
        "IpamResourceCidr": IpamResourceCidrTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeIpv6PoolsResultTypeDef = TypedDict(
    "DescribeIpv6PoolsResultTypeDef",
    {
        "Ipv6Pools": List[Ipv6PoolTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RequestLaunchTemplateDataTypeDef = TypedDict(
    "RequestLaunchTemplateDataTypeDef",
    {
        "KernelId": str,
        "EbsOptimized": bool,
        "IamInstanceProfile": LaunchTemplateIamInstanceProfileSpecificationRequestTypeDef,
        "BlockDeviceMappings": Sequence[LaunchTemplateBlockDeviceMappingRequestTypeDef],
        "NetworkInterfaces": Sequence[
            LaunchTemplateInstanceNetworkInterfaceSpecificationRequestTypeDef
        ],
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "KeyName": str,
        "Monitoring": LaunchTemplatesMonitoringRequestTypeDef,
        "Placement": LaunchTemplatePlacementRequestTypeDef,
        "RamDiskId": str,
        "DisableApiTermination": bool,
        "InstanceInitiatedShutdownBehavior": ShutdownBehaviorType,
        "UserData": str,
        "TagSpecifications": Sequence[LaunchTemplateTagSpecificationRequestTypeDef],
        "ElasticGpuSpecifications": Sequence[ElasticGpuSpecificationTypeDef],
        "ElasticInferenceAccelerators": Sequence[LaunchTemplateElasticInferenceAcceleratorTypeDef],
        "SecurityGroupIds": Sequence[str],
        "SecurityGroups": Sequence[str],
        "InstanceMarketOptions": LaunchTemplateInstanceMarketOptionsRequestTypeDef,
        "CreditSpecification": CreditSpecificationRequestTypeDef,
        "CpuOptions": LaunchTemplateCpuOptionsRequestTypeDef,
        "CapacityReservationSpecification": LaunchTemplateCapacityReservationSpecificationRequestTypeDef,
        "LicenseSpecifications": Sequence[LaunchTemplateLicenseConfigurationRequestTypeDef],
        "HibernationOptions": LaunchTemplateHibernationOptionsRequestTypeDef,
        "MetadataOptions": LaunchTemplateInstanceMetadataOptionsRequestTypeDef,
        "EnclaveOptions": LaunchTemplateEnclaveOptionsRequestTypeDef,
        "InstanceRequirements": InstanceRequirementsRequestTypeDef,
        "PrivateDnsNameOptions": LaunchTemplatePrivateDnsNameOptionsRequestTypeDef,
        "MaintenanceOptions": LaunchTemplateInstanceMaintenanceOptionsRequestTypeDef,
        "DisableApiStop": bool,
    },
    total=False,
)

ResponseLaunchTemplateDataTypeDef = TypedDict(
    "ResponseLaunchTemplateDataTypeDef",
    {
        "KernelId": str,
        "EbsOptimized": bool,
        "IamInstanceProfile": LaunchTemplateIamInstanceProfileSpecificationTypeDef,
        "BlockDeviceMappings": List[LaunchTemplateBlockDeviceMappingTypeDef],
        "NetworkInterfaces": List[LaunchTemplateInstanceNetworkInterfaceSpecificationTypeDef],
        "ImageId": str,
        "InstanceType": InstanceTypeType,
        "KeyName": str,
        "Monitoring": LaunchTemplatesMonitoringTypeDef,
        "Placement": LaunchTemplatePlacementTypeDef,
        "RamDiskId": str,
        "DisableApiTermination": bool,
        "InstanceInitiatedShutdownBehavior": ShutdownBehaviorType,
        "UserData": str,
        "TagSpecifications": List[LaunchTemplateTagSpecificationTypeDef],
        "ElasticGpuSpecifications": List[ElasticGpuSpecificationResponseTypeDef],
        "ElasticInferenceAccelerators": List[
            LaunchTemplateElasticInferenceAcceleratorResponseTypeDef
        ],
        "SecurityGroupIds": List[str],
        "SecurityGroups": List[str],
        "InstanceMarketOptions": LaunchTemplateInstanceMarketOptionsTypeDef,
        "CreditSpecification": CreditSpecificationTypeDef,
        "CpuOptions": LaunchTemplateCpuOptionsTypeDef,
        "CapacityReservationSpecification": LaunchTemplateCapacityReservationSpecificationResponseTypeDef,
        "LicenseSpecifications": List[LaunchTemplateLicenseConfigurationTypeDef],
        "HibernationOptions": LaunchTemplateHibernationOptionsTypeDef,
        "MetadataOptions": LaunchTemplateInstanceMetadataOptionsTypeDef,
        "EnclaveOptions": LaunchTemplateEnclaveOptionsTypeDef,
        "InstanceRequirements": InstanceRequirementsTypeDef,
        "PrivateDnsNameOptions": LaunchTemplatePrivateDnsNameOptionsTypeDef,
        "MaintenanceOptions": LaunchTemplateInstanceMaintenanceOptionsTypeDef,
        "DisableApiStop": bool,
    },
    total=False,
)

_RequiredModifyFpgaImageAttributeRequestRequestTypeDef = TypedDict(
    "_RequiredModifyFpgaImageAttributeRequestRequestTypeDef",
    {
        "FpgaImageId": str,
    },
)
_OptionalModifyFpgaImageAttributeRequestRequestTypeDef = TypedDict(
    "_OptionalModifyFpgaImageAttributeRequestRequestTypeDef",
    {
        "DryRun": bool,
        "Attribute": FpgaImageAttributeNameType,
        "OperationType": OperationTypeType,
        "UserIds": Sequence[str],
        "UserGroups": Sequence[str],
        "ProductCodes": Sequence[str],
        "LoadPermission": LoadPermissionModificationsTypeDef,
        "Description": str,
        "Name": str,
    },
    total=False,
)


class ModifyFpgaImageAttributeRequestRequestTypeDef(
    _RequiredModifyFpgaImageAttributeRequestRequestTypeDef,
    _OptionalModifyFpgaImageAttributeRequestRequestTypeDef,
):
    pass


ReservedInstancesModificationTypeDef = TypedDict(
    "ReservedInstancesModificationTypeDef",
    {
        "ClientToken": str,
        "CreateDate": datetime,
        "EffectiveDate": datetime,
        "ModificationResults": List[ReservedInstancesModificationResultTypeDef],
        "ReservedInstancesIds": List[ReservedInstancesIdTypeDef],
        "ReservedInstancesModificationId": str,
        "Status": str,
        "StatusMessage": str,
        "UpdateDate": datetime,
    },
    total=False,
)

_RequiredModifyVpnTunnelOptionsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyVpnTunnelOptionsRequestRequestTypeDef",
    {
        "VpnConnectionId": str,
        "VpnTunnelOutsideIpAddress": str,
        "TunnelOptions": ModifyVpnTunnelOptionsSpecificationTypeDef,
    },
)
_OptionalModifyVpnTunnelOptionsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyVpnTunnelOptionsRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifyVpnTunnelOptionsRequestRequestTypeDef(
    _RequiredModifyVpnTunnelOptionsRequestRequestTypeDef,
    _OptionalModifyVpnTunnelOptionsRequestRequestTypeDef,
):
    pass


VpnConnectionOptionsSpecificationTypeDef = TypedDict(
    "VpnConnectionOptionsSpecificationTypeDef",
    {
        "EnableAcceleration": bool,
        "StaticRoutesOnly": bool,
        "TunnelInsideIpVersion": TunnelInsideIpVersionType,
        "TunnelOptions": Sequence[VpnTunnelOptionsSpecificationTypeDef],
        "LocalIpv4NetworkCidr": str,
        "RemoteIpv4NetworkCidr": str,
        "LocalIpv6NetworkCidr": str,
        "RemoteIpv6NetworkCidr": str,
    },
    total=False,
)

CreateNatGatewayResultTypeDef = TypedDict(
    "CreateNatGatewayResultTypeDef",
    {
        "ClientToken": str,
        "NatGateway": NatGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNatGatewaysResultTypeDef = TypedDict(
    "DescribeNatGatewaysResultTypeDef",
    {
        "NatGateways": List[NatGatewayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "Association": NetworkInterfaceAssociationTypeDef,
        "Attachment": NetworkInterfaceAttachmentTypeDef,
        "AvailabilityZone": str,
        "Description": str,
        "Groups": List[GroupIdentifierTypeDef],
        "InterfaceType": NetworkInterfaceTypeType,
        "Ipv6Addresses": List[NetworkInterfaceIpv6AddressTypeDef],
        "MacAddress": str,
        "NetworkInterfaceId": str,
        "OutpostArn": str,
        "OwnerId": str,
        "PrivateDnsName": str,
        "PrivateIpAddress": str,
        "PrivateIpAddresses": List[NetworkInterfacePrivateIpAddressTypeDef],
        "Ipv4Prefixes": List[Ipv4PrefixSpecificationTypeDef],
        "Ipv6Prefixes": List[Ipv6PrefixSpecificationTypeDef],
        "RequesterId": str,
        "RequesterManaged": bool,
        "SourceDestCheck": bool,
        "Status": NetworkInterfaceStatusType,
        "SubnetId": str,
        "TagSet": List[TagTypeDef],
        "VpcId": str,
        "DenyAllIgwTraffic": bool,
        "Ipv6Native": bool,
        "Ipv6Address": str,
    },
    total=False,
)

CreateNetworkInterfacePermissionResultTypeDef = TypedDict(
    "CreateNetworkInterfacePermissionResultTypeDef",
    {
        "InterfacePermission": NetworkInterfacePermissionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInterfacePermissionsResultTypeDef = TypedDict(
    "DescribeNetworkInterfacePermissionsResultTypeDef",
    {
        "NetworkInterfacePermissions": List[NetworkInterfacePermissionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AccessScopePathRequestTypeDef = TypedDict(
    "AccessScopePathRequestTypeDef",
    {
        "Source": PathStatementRequestTypeDef,
        "Destination": PathStatementRequestTypeDef,
        "ThroughResources": Sequence[ThroughResourcesStatementRequestTypeDef],
    },
    total=False,
)

AccessScopePathTypeDef = TypedDict(
    "AccessScopePathTypeDef",
    {
        "Source": PathStatementTypeDef,
        "Destination": PathStatementTypeDef,
        "ThroughResources": List[ThroughResourcesStatementTypeDef],
    },
    total=False,
)

AcceptTransitGatewayPeeringAttachmentResultTypeDef = TypedDict(
    "AcceptTransitGatewayPeeringAttachmentResultTypeDef",
    {
        "TransitGatewayPeeringAttachment": TransitGatewayPeeringAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayPeeringAttachmentResultTypeDef = TypedDict(
    "CreateTransitGatewayPeeringAttachmentResultTypeDef",
    {
        "TransitGatewayPeeringAttachment": TransitGatewayPeeringAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayPeeringAttachmentResultTypeDef = TypedDict(
    "DeleteTransitGatewayPeeringAttachmentResultTypeDef",
    {
        "TransitGatewayPeeringAttachment": TransitGatewayPeeringAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewayPeeringAttachmentsResultTypeDef = TypedDict(
    "DescribeTransitGatewayPeeringAttachmentsResultTypeDef",
    {
        "TransitGatewayPeeringAttachments": List[TransitGatewayPeeringAttachmentTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RejectTransitGatewayPeeringAttachmentResultTypeDef = TypedDict(
    "RejectTransitGatewayPeeringAttachmentResultTypeDef",
    {
        "TransitGatewayPeeringAttachment": TransitGatewayPeeringAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VpnConnectionOptionsTypeDef = TypedDict(
    "VpnConnectionOptionsTypeDef",
    {
        "EnableAcceleration": bool,
        "StaticRoutesOnly": bool,
        "LocalIpv4NetworkCidr": str,
        "RemoteIpv4NetworkCidr": str,
        "LocalIpv6NetworkCidr": str,
        "RemoteIpv6NetworkCidr": str,
        "TunnelInsideIpVersion": TunnelInsideIpVersionType,
        "TunnelOptions": List[TunnelOptionTypeDef],
    },
    total=False,
)

CancelReservedInstancesListingResultTypeDef = TypedDict(
    "CancelReservedInstancesListingResultTypeDef",
    {
        "ReservedInstancesListings": List[ReservedInstancesListingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateReservedInstancesListingResultTypeDef = TypedDict(
    "CreateReservedInstancesListingResultTypeDef",
    {
        "ReservedInstancesListings": List[ReservedInstancesListingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeReservedInstancesListingsResultTypeDef = TypedDict(
    "DescribeReservedInstancesListingsResultTypeDef",
    {
        "ReservedInstancesListings": List[ReservedInstancesListingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePublicIpv4PoolsResultTypeDef = TypedDict(
    "DescribePublicIpv4PoolsResultTypeDef",
    {
        "PublicIpv4Pools": List[PublicIpv4PoolTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeReservedInstancesOfferingsResultTypeDef = TypedDict(
    "DescribeReservedInstancesOfferingsResultTypeDef",
    {
        "ReservedInstancesOfferings": List[ReservedInstancesOfferingTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeReservedInstancesResultTypeDef = TypedDict(
    "DescribeReservedInstancesResultTypeDef",
    {
        "ReservedInstances": List[ReservedInstancesTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AuthorizeSecurityGroupEgressResultTypeDef = TypedDict(
    "AuthorizeSecurityGroupEgressResultTypeDef",
    {
        "Return": bool,
        "SecurityGroupRules": List[SecurityGroupRuleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AuthorizeSecurityGroupIngressResultTypeDef = TypedDict(
    "AuthorizeSecurityGroupIngressResultTypeDef",
    {
        "Return": bool,
        "SecurityGroupRules": List[SecurityGroupRuleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSecurityGroupRulesResultTypeDef = TypedDict(
    "DescribeSecurityGroupRulesResultTypeDef",
    {
        "SecurityGroupRules": List[SecurityGroupRuleTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredBundleInstanceRequestRequestTypeDef = TypedDict(
    "_RequiredBundleInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Storage": StorageTypeDef,
    },
)
_OptionalBundleInstanceRequestRequestTypeDef = TypedDict(
    "_OptionalBundleInstanceRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class BundleInstanceRequestRequestTypeDef(
    _RequiredBundleInstanceRequestRequestTypeDef, _OptionalBundleInstanceRequestRequestTypeDef
):
    pass


BundleTaskTypeDef = TypedDict(
    "BundleTaskTypeDef",
    {
        "BundleId": str,
        "BundleTaskError": BundleTaskErrorTypeDef,
        "InstanceId": str,
        "Progress": str,
        "StartTime": datetime,
        "State": BundleTaskStateType,
        "Storage": StorageTypeDef,
        "UpdateTime": datetime,
    },
    total=False,
)

DescribeScheduledInstanceAvailabilityResultTypeDef = TypedDict(
    "DescribeScheduledInstanceAvailabilityResultTypeDef",
    {
        "NextToken": str,
        "ScheduledInstanceAvailabilitySet": List[ScheduledInstanceAvailabilityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeScheduledInstancesResultTypeDef = TypedDict(
    "DescribeScheduledInstancesResultTypeDef",
    {
        "NextToken": str,
        "ScheduledInstanceSet": List[ScheduledInstanceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PurchaseScheduledInstancesResultTypeDef = TypedDict(
    "PurchaseScheduledInstancesResultTypeDef",
    {
        "ScheduledInstanceSet": List[ScheduledInstanceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredScheduledInstancesLaunchSpecificationTypeDef = TypedDict(
    "_RequiredScheduledInstancesLaunchSpecificationTypeDef",
    {
        "ImageId": str,
    },
)
_OptionalScheduledInstancesLaunchSpecificationTypeDef = TypedDict(
    "_OptionalScheduledInstancesLaunchSpecificationTypeDef",
    {
        "BlockDeviceMappings": Sequence[ScheduledInstancesBlockDeviceMappingTypeDef],
        "EbsOptimized": bool,
        "IamInstanceProfile": ScheduledInstancesIamInstanceProfileTypeDef,
        "InstanceType": str,
        "KernelId": str,
        "KeyName": str,
        "Monitoring": ScheduledInstancesMonitoringTypeDef,
        "NetworkInterfaces": Sequence[ScheduledInstancesNetworkInterfaceTypeDef],
        "Placement": ScheduledInstancesPlacementTypeDef,
        "RamdiskId": str,
        "SecurityGroupIds": Sequence[str],
        "SubnetId": str,
        "UserData": str,
    },
    total=False,
)


class ScheduledInstancesLaunchSpecificationTypeDef(
    _RequiredScheduledInstancesLaunchSpecificationTypeDef,
    _OptionalScheduledInstancesLaunchSpecificationTypeDef,
):
    pass


CreateVpcEndpointResultTypeDef = TypedDict(
    "CreateVpcEndpointResultTypeDef",
    {
        "VpcEndpoint": VpcEndpointTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcEndpointsResultTypeDef = TypedDict(
    "DescribeVpcEndpointsResultTypeDef",
    {
        "VpcEndpoints": List[VpcEndpointTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredModifySecurityGroupRulesRequestRequestTypeDef = TypedDict(
    "_RequiredModifySecurityGroupRulesRequestRequestTypeDef",
    {
        "GroupId": str,
        "SecurityGroupRules": Sequence[SecurityGroupRuleUpdateTypeDef],
    },
)
_OptionalModifySecurityGroupRulesRequestRequestTypeDef = TypedDict(
    "_OptionalModifySecurityGroupRulesRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class ModifySecurityGroupRulesRequestRequestTypeDef(
    _RequiredModifySecurityGroupRulesRequestRequestTypeDef,
    _OptionalModifySecurityGroupRulesRequestRequestTypeDef,
):
    pass


CreateVpcEndpointServiceConfigurationResultTypeDef = TypedDict(
    "CreateVpcEndpointServiceConfigurationResultTypeDef",
    {
        "ServiceConfiguration": ServiceConfigurationTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcEndpointServiceConfigurationsResultTypeDef = TypedDict(
    "DescribeVpcEndpointServiceConfigurationsResultTypeDef",
    {
        "ServiceConfigurations": List[ServiceConfigurationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcEndpointServicesResultTypeDef = TypedDict(
    "DescribeVpcEndpointServicesResultTypeDef",
    {
        "ServiceNames": List[str],
        "ServiceDetails": List[ServiceDetailTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportImageResultTypeDef = TypedDict(
    "ImportImageResultTypeDef",
    {
        "Architecture": str,
        "Description": str,
        "Encrypted": bool,
        "Hypervisor": str,
        "ImageId": str,
        "ImportTaskId": str,
        "KmsKeyId": str,
        "LicenseType": str,
        "Platform": str,
        "Progress": str,
        "SnapshotDetails": List[SnapshotDetailTypeDef],
        "Status": str,
        "StatusMessage": str,
        "LicenseSpecifications": List[ImportImageLicenseConfigurationResponseTypeDef],
        "Tags": List[TagTypeDef],
        "UsageOperation": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportImageTaskTypeDef = TypedDict(
    "ImportImageTaskTypeDef",
    {
        "Architecture": str,
        "Description": str,
        "Encrypted": bool,
        "Hypervisor": str,
        "ImageId": str,
        "ImportTaskId": str,
        "KmsKeyId": str,
        "LicenseType": str,
        "Platform": str,
        "Progress": str,
        "SnapshotDetails": List[SnapshotDetailTypeDef],
        "Status": str,
        "StatusMessage": str,
        "Tags": List[TagTypeDef],
        "LicenseSpecifications": List[ImportImageLicenseConfigurationResponseTypeDef],
        "UsageOperation": str,
        "BootMode": BootModeValuesType,
    },
    total=False,
)

ImportSnapshotResultTypeDef = TypedDict(
    "ImportSnapshotResultTypeDef",
    {
        "Description": str,
        "ImportTaskId": str,
        "SnapshotTaskDetail": SnapshotTaskDetailTypeDef,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportSnapshotTaskTypeDef = TypedDict(
    "ImportSnapshotTaskTypeDef",
    {
        "Description": str,
        "ImportTaskId": str,
        "SnapshotTaskDetail": SnapshotTaskDetailTypeDef,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

CreateSpotDatafeedSubscriptionResultTypeDef = TypedDict(
    "CreateSpotDatafeedSubscriptionResultTypeDef",
    {
        "SpotDatafeedSubscription": SpotDatafeedSubscriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpotDatafeedSubscriptionResultTypeDef = TypedDict(
    "DescribeSpotDatafeedSubscriptionResultTypeDef",
    {
        "SpotDatafeedSubscription": SpotDatafeedSubscriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayMulticastDomainAssociationsResultTypeDef = TypedDict(
    "GetTransitGatewayMulticastDomainAssociationsResultTypeDef",
    {
        "MulticastDomainAssociations": List[TransitGatewayMulticastDomainAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AcceptTransitGatewayMulticastDomainAssociationsResultTypeDef = TypedDict(
    "AcceptTransitGatewayMulticastDomainAssociationsResultTypeDef",
    {
        "Associations": TransitGatewayMulticastDomainAssociationsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateTransitGatewayMulticastDomainResultTypeDef = TypedDict(
    "AssociateTransitGatewayMulticastDomainResultTypeDef",
    {
        "Associations": TransitGatewayMulticastDomainAssociationsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateTransitGatewayMulticastDomainResultTypeDef = TypedDict(
    "DisassociateTransitGatewayMulticastDomainResultTypeDef",
    {
        "Associations": TransitGatewayMulticastDomainAssociationsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RejectTransitGatewayMulticastDomainAssociationsResultTypeDef = TypedDict(
    "RejectTransitGatewayMulticastDomainAssociationsResultTypeDef",
    {
        "Associations": TransitGatewayMulticastDomainAssociationsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateSubnetCidrBlockResultTypeDef = TypedDict(
    "AssociateSubnetCidrBlockResultTypeDef",
    {
        "Ipv6CidrBlockAssociation": SubnetIpv6CidrBlockAssociationTypeDef,
        "SubnetId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateSubnetCidrBlockResultTypeDef = TypedDict(
    "DisassociateSubnetCidrBlockResultTypeDef",
    {
        "Ipv6CidrBlockAssociation": SubnetIpv6CidrBlockAssociationTypeDef,
        "SubnetId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SubnetTypeDef = TypedDict(
    "SubnetTypeDef",
    {
        "AvailabilityZone": str,
        "AvailabilityZoneId": str,
        "AvailableIpAddressCount": int,
        "CidrBlock": str,
        "DefaultForAz": bool,
        "EnableLniAtDeviceIndex": int,
        "MapPublicIpOnLaunch": bool,
        "MapCustomerOwnedIpOnLaunch": bool,
        "CustomerOwnedIpv4Pool": str,
        "State": SubnetStateType,
        "SubnetId": str,
        "VpcId": str,
        "OwnerId": str,
        "AssignIpv6AddressOnCreation": bool,
        "Ipv6CidrBlockAssociationSet": List[SubnetIpv6CidrBlockAssociationTypeDef],
        "Tags": List[TagTypeDef],
        "SubnetArn": str,
        "OutpostArn": str,
        "EnableDns64": bool,
        "Ipv6Native": bool,
        "PrivateDnsNameOptionsOnLaunch": PrivateDnsNameOptionsOnLaunchTypeDef,
    },
    total=False,
)

GetReservedInstancesExchangeQuoteResultTypeDef = TypedDict(
    "GetReservedInstancesExchangeQuoteResultTypeDef",
    {
        "CurrencyCode": str,
        "IsValidExchange": bool,
        "OutputReservedInstancesWillExpireAt": datetime,
        "PaymentDue": str,
        "ReservedInstanceValueRollup": ReservationValueTypeDef,
        "ReservedInstanceValueSet": List[ReservedInstanceReservationValueTypeDef],
        "TargetConfigurationValueRollup": ReservationValueTypeDef,
        "TargetConfigurationValueSet": List[TargetReservationValueTypeDef],
        "ValidationFailureReason": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LoadBalancersConfigTypeDef = TypedDict(
    "LoadBalancersConfigTypeDef",
    {
        "ClassicLoadBalancersConfig": ClassicLoadBalancersConfigTypeDef,
        "TargetGroupsConfig": TargetGroupsConfigTypeDef,
    },
    total=False,
)

CreateTrafficMirrorFilterRuleResultTypeDef = TypedDict(
    "CreateTrafficMirrorFilterRuleResultTypeDef",
    {
        "TrafficMirrorFilterRule": TrafficMirrorFilterRuleTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyTrafficMirrorFilterRuleResultTypeDef = TypedDict(
    "ModifyTrafficMirrorFilterRuleResultTypeDef",
    {
        "TrafficMirrorFilterRule": TrafficMirrorFilterRuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TrafficMirrorFilterTypeDef = TypedDict(
    "TrafficMirrorFilterTypeDef",
    {
        "TrafficMirrorFilterId": str,
        "IngressFilterRules": List[TrafficMirrorFilterRuleTypeDef],
        "EgressFilterRules": List[TrafficMirrorFilterRuleTypeDef],
        "NetworkServices": List[Literal["amazon-dns"]],
        "Description": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

DescribeTransitGatewayAttachmentsResultTypeDef = TypedDict(
    "DescribeTransitGatewayAttachmentsResultTypeDef",
    {
        "TransitGatewayAttachments": List[TransitGatewayAttachmentTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TransitGatewayConnectPeerTypeDef = TypedDict(
    "TransitGatewayConnectPeerTypeDef",
    {
        "TransitGatewayAttachmentId": str,
        "TransitGatewayConnectPeerId": str,
        "State": TransitGatewayConnectPeerStateType,
        "CreationTime": datetime,
        "ConnectPeerConfiguration": TransitGatewayConnectPeerConfigurationTypeDef,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

CreateTransitGatewayConnectResultTypeDef = TypedDict(
    "CreateTransitGatewayConnectResultTypeDef",
    {
        "TransitGatewayConnect": TransitGatewayConnectTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayConnectResultTypeDef = TypedDict(
    "DeleteTransitGatewayConnectResultTypeDef",
    {
        "TransitGatewayConnect": TransitGatewayConnectTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewayConnectsResultTypeDef = TypedDict(
    "DescribeTransitGatewayConnectsResultTypeDef",
    {
        "TransitGatewayConnects": List[TransitGatewayConnectTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayMulticastDomainResultTypeDef = TypedDict(
    "CreateTransitGatewayMulticastDomainResultTypeDef",
    {
        "TransitGatewayMulticastDomain": TransitGatewayMulticastDomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayMulticastDomainResultTypeDef = TypedDict(
    "DeleteTransitGatewayMulticastDomainResultTypeDef",
    {
        "TransitGatewayMulticastDomain": TransitGatewayMulticastDomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewayMulticastDomainsResultTypeDef = TypedDict(
    "DescribeTransitGatewayMulticastDomainsResultTypeDef",
    {
        "TransitGatewayMulticastDomains": List[TransitGatewayMulticastDomainTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayResultTypeDef = TypedDict(
    "CreateTransitGatewayResultTypeDef",
    {
        "TransitGateway": TransitGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayResultTypeDef = TypedDict(
    "DeleteTransitGatewayResultTypeDef",
    {
        "TransitGateway": TransitGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewaysResultTypeDef = TypedDict(
    "DescribeTransitGatewaysResultTypeDef",
    {
        "TransitGateways": List[TransitGatewayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyTransitGatewayResultTypeDef = TypedDict(
    "ModifyTransitGatewayResultTypeDef",
    {
        "TransitGateway": TransitGatewayTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayPrefixListReferenceResultTypeDef = TypedDict(
    "CreateTransitGatewayPrefixListReferenceResultTypeDef",
    {
        "TransitGatewayPrefixListReference": TransitGatewayPrefixListReferenceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayPrefixListReferenceResultTypeDef = TypedDict(
    "DeleteTransitGatewayPrefixListReferenceResultTypeDef",
    {
        "TransitGatewayPrefixListReference": TransitGatewayPrefixListReferenceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTransitGatewayPrefixListReferencesResultTypeDef = TypedDict(
    "GetTransitGatewayPrefixListReferencesResultTypeDef",
    {
        "TransitGatewayPrefixListReferences": List[TransitGatewayPrefixListReferenceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyTransitGatewayPrefixListReferenceResultTypeDef = TypedDict(
    "ModifyTransitGatewayPrefixListReferenceResultTypeDef",
    {
        "TransitGatewayPrefixListReference": TransitGatewayPrefixListReferenceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayRouteResultTypeDef = TypedDict(
    "CreateTransitGatewayRouteResultTypeDef",
    {
        "Route": TransitGatewayRouteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayRouteResultTypeDef = TypedDict(
    "DeleteTransitGatewayRouteResultTypeDef",
    {
        "Route": TransitGatewayRouteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplaceTransitGatewayRouteResultTypeDef = TypedDict(
    "ReplaceTransitGatewayRouteResultTypeDef",
    {
        "Route": TransitGatewayRouteTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchTransitGatewayRoutesResultTypeDef = TypedDict(
    "SearchTransitGatewayRoutesResultTypeDef",
    {
        "Routes": List[TransitGatewayRouteTypeDef],
        "AdditionalRoutesAvailable": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AcceptTransitGatewayVpcAttachmentResultTypeDef = TypedDict(
    "AcceptTransitGatewayVpcAttachmentResultTypeDef",
    {
        "TransitGatewayVpcAttachment": TransitGatewayVpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayVpcAttachmentResultTypeDef = TypedDict(
    "CreateTransitGatewayVpcAttachmentResultTypeDef",
    {
        "TransitGatewayVpcAttachment": TransitGatewayVpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayVpcAttachmentResultTypeDef = TypedDict(
    "DeleteTransitGatewayVpcAttachmentResultTypeDef",
    {
        "TransitGatewayVpcAttachment": TransitGatewayVpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewayVpcAttachmentsResultTypeDef = TypedDict(
    "DescribeTransitGatewayVpcAttachmentsResultTypeDef",
    {
        "TransitGatewayVpcAttachments": List[TransitGatewayVpcAttachmentTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyTransitGatewayVpcAttachmentResultTypeDef = TypedDict(
    "ModifyTransitGatewayVpcAttachmentResultTypeDef",
    {
        "TransitGatewayVpcAttachment": TransitGatewayVpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RejectTransitGatewayVpcAttachmentResultTypeDef = TypedDict(
    "RejectTransitGatewayVpcAttachmentResultTypeDef",
    {
        "TransitGatewayVpcAttachment": TransitGatewayVpcAttachmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyInstanceCreditSpecificationResultTypeDef = TypedDict(
    "ModifyInstanceCreditSpecificationResultTypeDef",
    {
        "SuccessfulInstanceCreditSpecifications": List[
            SuccessfulInstanceCreditSpecificationItemTypeDef
        ],
        "UnsuccessfulInstanceCreditSpecifications": List[
            UnsuccessfulInstanceCreditSpecificationItemTypeDef
        ],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AcceptVpcEndpointConnectionsResultTypeDef = TypedDict(
    "AcceptVpcEndpointConnectionsResultTypeDef",
    {
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFlowLogsResultTypeDef = TypedDict(
    "CreateFlowLogsResultTypeDef",
    {
        "ClientToken": str,
        "FlowLogIds": List[str],
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteFlowLogsResultTypeDef = TypedDict(
    "DeleteFlowLogsResultTypeDef",
    {
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteVpcEndpointConnectionNotificationsResultTypeDef = TypedDict(
    "DeleteVpcEndpointConnectionNotificationsResultTypeDef",
    {
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteVpcEndpointServiceConfigurationsResultTypeDef = TypedDict(
    "DeleteVpcEndpointServiceConfigurationsResultTypeDef",
    {
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteVpcEndpointsResultTypeDef = TypedDict(
    "DeleteVpcEndpointsResultTypeDef",
    {
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyHostsResultTypeDef = TypedDict(
    "ModifyHostsResultTypeDef",
    {
        "Successful": List[str],
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RejectVpcEndpointConnectionsResultTypeDef = TypedDict(
    "RejectVpcEndpointConnectionsResultTypeDef",
    {
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReleaseHostsResultTypeDef = TypedDict(
    "ReleaseHostsResultTypeDef",
    {
        "Successful": List[str],
        "Unsuccessful": List[UnsuccessfulItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLaunchTemplateResultTypeDef = TypedDict(
    "CreateLaunchTemplateResultTypeDef",
    {
        "LaunchTemplate": LaunchTemplateTypeDef,
        "Warning": ValidationWarningTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVolumesResultTypeDef = TypedDict(
    "DescribeVolumesResultTypeDef",
    {
        "Volumes": List[VolumeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VolumeStatusItemTypeDef = TypedDict(
    "VolumeStatusItemTypeDef",
    {
        "Actions": List[VolumeStatusActionTypeDef],
        "AvailabilityZone": str,
        "OutpostArn": str,
        "Events": List[VolumeStatusEventTypeDef],
        "VolumeId": str,
        "VolumeStatus": VolumeStatusInfoTypeDef,
        "AttachmentStatuses": List[VolumeStatusAttachmentStatusTypeDef],
    },
    total=False,
)

AssociateVpcCidrBlockResultTypeDef = TypedDict(
    "AssociateVpcCidrBlockResultTypeDef",
    {
        "Ipv6CidrBlockAssociation": VpcIpv6CidrBlockAssociationTypeDef,
        "CidrBlockAssociation": VpcCidrBlockAssociationTypeDef,
        "VpcId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateVpcCidrBlockResultTypeDef = TypedDict(
    "DisassociateVpcCidrBlockResultTypeDef",
    {
        "Ipv6CidrBlockAssociation": VpcIpv6CidrBlockAssociationTypeDef,
        "CidrBlockAssociation": VpcCidrBlockAssociationTypeDef,
        "VpcId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

VpcTypeDef = TypedDict(
    "VpcTypeDef",
    {
        "CidrBlock": str,
        "DhcpOptionsId": str,
        "State": VpcStateType,
        "VpcId": str,
        "OwnerId": str,
        "InstanceTenancy": TenancyType,
        "Ipv6CidrBlockAssociationSet": List[VpcIpv6CidrBlockAssociationTypeDef],
        "CidrBlockAssociationSet": List[VpcCidrBlockAssociationTypeDef],
        "IsDefault": bool,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

VpcPeeringConnectionTypeDef = TypedDict(
    "VpcPeeringConnectionTypeDef",
    {
        "AccepterVpcInfo": VpcPeeringConnectionVpcInfoTypeDef,
        "ExpirationTime": datetime,
        "RequesterVpcInfo": VpcPeeringConnectionVpcInfoTypeDef,
        "Status": VpcPeeringConnectionStateReasonTypeDef,
        "Tags": List[TagTypeDef],
        "VpcPeeringConnectionId": str,
    },
    total=False,
)

AssociateInstanceEventWindowResultTypeDef = TypedDict(
    "AssociateInstanceEventWindowResultTypeDef",
    {
        "InstanceEventWindow": InstanceEventWindowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInstanceEventWindowResultTypeDef = TypedDict(
    "CreateInstanceEventWindowResultTypeDef",
    {
        "InstanceEventWindow": InstanceEventWindowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInstanceEventWindowsResultTypeDef = TypedDict(
    "DescribeInstanceEventWindowsResultTypeDef",
    {
        "InstanceEventWindows": List[InstanceEventWindowTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateInstanceEventWindowResultTypeDef = TypedDict(
    "DisassociateInstanceEventWindowResultTypeDef",
    {
        "InstanceEventWindow": InstanceEventWindowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyInstanceEventWindowResultTypeDef = TypedDict(
    "ModifyInstanceEventWindowResultTypeDef",
    {
        "InstanceEventWindow": InstanceEventWindowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AccessScopeAnalysisFindingTypeDef = TypedDict(
    "AccessScopeAnalysisFindingTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisId": str,
        "NetworkInsightsAccessScopeId": str,
        "FindingId": str,
        "FindingComponents": List[PathComponentTypeDef],
    },
    total=False,
)

NetworkInsightsAnalysisTypeDef = TypedDict(
    "NetworkInsightsAnalysisTypeDef",
    {
        "NetworkInsightsAnalysisId": str,
        "NetworkInsightsAnalysisArn": str,
        "NetworkInsightsPathId": str,
        "FilterInArns": List[str],
        "StartDate": datetime,
        "Status": AnalysisStatusType,
        "StatusMessage": str,
        "WarningMessage": str,
        "NetworkPathFound": bool,
        "ForwardPathComponents": List[PathComponentTypeDef],
        "ReturnPathComponents": List[PathComponentTypeDef],
        "Explanations": List[ExplanationTypeDef],
        "AlternatePathHints": List[AlternatePathHintTypeDef],
        "Tags": List[TagTypeDef],
    },
    total=False,
)

CreateRouteTableResultTypeDef = TypedDict(
    "CreateRouteTableResultTypeDef",
    {
        "RouteTable": RouteTableTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRouteTablesResultTypeDef = TypedDict(
    "DescribeRouteTablesResultTypeDef",
    {
        "RouteTables": List[RouteTableTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDhcpOptionsResultTypeDef = TypedDict(
    "CreateDhcpOptionsResultTypeDef",
    {
        "DhcpOptions": DhcpOptionsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDhcpOptionsResultTypeDef = TypedDict(
    "DescribeDhcpOptionsResultTypeDef",
    {
        "DhcpOptions": List[DhcpOptionsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeHostsResultTypeDef = TypedDict(
    "DescribeHostsResultTypeDef",
    {
        "Hosts": List[HostTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImagesResultTypeDef = TypedDict(
    "DescribeImagesResultTypeDef",
    {
        "Images": List[ImageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeClientVpnEndpointsResultTypeDef = TypedDict(
    "DescribeClientVpnEndpointsResultTypeDef",
    {
        "ClientVpnEndpoints": List[ClientVpnEndpointTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateNetworkAclResultTypeDef = TypedDict(
    "CreateNetworkAclResultTypeDef",
    {
        "NetworkAcl": NetworkAclTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkAclsResultTypeDef = TypedDict(
    "DescribeNetworkAclsResultTypeDef",
    {
        "NetworkAcls": List[NetworkAclTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SpotInstanceRequestTypeDef = TypedDict(
    "SpotInstanceRequestTypeDef",
    {
        "ActualBlockHourlyPrice": str,
        "AvailabilityZoneGroup": str,
        "BlockDurationMinutes": int,
        "CreateTime": datetime,
        "Fault": SpotInstanceStateFaultTypeDef,
        "InstanceId": str,
        "LaunchGroup": str,
        "LaunchSpecification": LaunchSpecificationTypeDef,
        "LaunchedAvailabilityZone": str,
        "ProductDescription": RIProductDescriptionType,
        "SpotInstanceRequestId": str,
        "SpotPrice": str,
        "State": SpotInstanceStateType,
        "Status": SpotInstanceStatusTypeDef,
        "Tags": List[TagTypeDef],
        "Type": SpotInstanceTypeType,
        "ValidFrom": datetime,
        "ValidUntil": datetime,
        "InstanceInterruptionBehavior": InstanceInterruptionBehaviorType,
    },
    total=False,
)

RequestSpotInstancesRequestRequestTypeDef = TypedDict(
    "RequestSpotInstancesRequestRequestTypeDef",
    {
        "AvailabilityZoneGroup": str,
        "BlockDurationMinutes": int,
        "ClientToken": str,
        "DryRun": bool,
        "InstanceCount": int,
        "LaunchGroup": str,
        "LaunchSpecification": RequestSpotLaunchSpecificationTypeDef,
        "SpotPrice": str,
        "Type": SpotInstanceTypeType,
        "ValidFrom": Union[datetime, str],
        "ValidUntil": Union[datetime, str],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "InstanceInterruptionBehavior": InstanceInterruptionBehaviorType,
    },
    total=False,
)

DisableFastSnapshotRestoresResultTypeDef = TypedDict(
    "DisableFastSnapshotRestoresResultTypeDef",
    {
        "Successful": List[DisableFastSnapshotRestoreSuccessItemTypeDef],
        "Unsuccessful": List[DisableFastSnapshotRestoreErrorItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ConversionTaskTypeDef = TypedDict(
    "ConversionTaskTypeDef",
    {
        "ConversionTaskId": str,
        "ExpirationTime": str,
        "ImportInstance": ImportInstanceTaskDetailsTypeDef,
        "ImportVolume": ImportVolumeTaskDetailsTypeDef,
        "State": ConversionTaskStateType,
        "StatusMessage": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

EnableFastSnapshotRestoresResultTypeDef = TypedDict(
    "EnableFastSnapshotRestoresResultTypeDef",
    {
        "Successful": List[EnableFastSnapshotRestoreSuccessItemTypeDef],
        "Unsuccessful": List[EnableFastSnapshotRestoreErrorItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceTypeInfoTypeDef = TypedDict(
    "InstanceTypeInfoTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "CurrentGeneration": bool,
        "FreeTierEligible": bool,
        "SupportedUsageClasses": List[UsageClassTypeType],
        "SupportedRootDeviceTypes": List[RootDeviceTypeType],
        "SupportedVirtualizationTypes": List[VirtualizationTypeType],
        "BareMetal": bool,
        "Hypervisor": InstanceTypeHypervisorType,
        "ProcessorInfo": ProcessorInfoTypeDef,
        "VCpuInfo": VCpuInfoTypeDef,
        "MemoryInfo": MemoryInfoTypeDef,
        "InstanceStorageSupported": bool,
        "InstanceStorageInfo": InstanceStorageInfoTypeDef,
        "EbsInfo": EbsInfoTypeDef,
        "NetworkInfo": NetworkInfoTypeDef,
        "GpuInfo": GpuInfoTypeDef,
        "FpgaInfo": FpgaInfoTypeDef,
        "PlacementGroupInfo": PlacementGroupInfoTypeDef,
        "InferenceAcceleratorInfo": InferenceAcceleratorInfoTypeDef,
        "HibernationSupported": bool,
        "BurstablePerformanceSupported": bool,
        "DedicatedHostsSupported": bool,
        "AutoRecoverySupported": bool,
        "SupportedBootModes": List[BootModeTypeType],
    },
    total=False,
)

InstanceTypeDef = TypedDict(
    "InstanceTypeDef",
    {
        "AmiLaunchIndex": int,
        "ImageId": str,
        "InstanceId": str,
        "InstanceType": InstanceTypeType,
        "KernelId": str,
        "KeyName": str,
        "LaunchTime": datetime,
        "Monitoring": MonitoringTypeDef,
        "Placement": PlacementTypeDef,
        "Platform": Literal["Windows"],
        "PrivateDnsName": str,
        "PrivateIpAddress": str,
        "ProductCodes": List[ProductCodeTypeDef],
        "PublicDnsName": str,
        "PublicIpAddress": str,
        "RamdiskId": str,
        "State": InstanceStateTypeDef,
        "StateTransitionReason": str,
        "SubnetId": str,
        "VpcId": str,
        "Architecture": ArchitectureValuesType,
        "BlockDeviceMappings": List[InstanceBlockDeviceMappingTypeDef],
        "ClientToken": str,
        "EbsOptimized": bool,
        "EnaSupport": bool,
        "Hypervisor": HypervisorTypeType,
        "IamInstanceProfile": IamInstanceProfileTypeDef,
        "InstanceLifecycle": InstanceLifecycleTypeType,
        "ElasticGpuAssociations": List[ElasticGpuAssociationTypeDef],
        "ElasticInferenceAcceleratorAssociations": List[
            ElasticInferenceAcceleratorAssociationTypeDef
        ],
        "NetworkInterfaces": List[InstanceNetworkInterfaceTypeDef],
        "OutpostArn": str,
        "RootDeviceName": str,
        "RootDeviceType": DeviceTypeType,
        "SecurityGroups": List[GroupIdentifierTypeDef],
        "SourceDestCheck": bool,
        "SpotInstanceRequestId": str,
        "SriovNetSupport": str,
        "StateReason": StateReasonTypeDef,
        "Tags": List[TagTypeDef],
        "VirtualizationType": VirtualizationTypeType,
        "CpuOptions": CpuOptionsTypeDef,
        "CapacityReservationId": str,
        "CapacityReservationSpecification": CapacityReservationSpecificationResponseTypeDef,
        "HibernationOptions": HibernationOptionsTypeDef,
        "Licenses": List[LicenseConfigurationTypeDef],
        "MetadataOptions": InstanceMetadataOptionsResponseTypeDef,
        "EnclaveOptions": EnclaveOptionsTypeDef,
        "BootMode": BootModeValuesType,
        "PlatformDetails": str,
        "UsageOperation": str,
        "UsageOperationUpdateTime": datetime,
        "PrivateDnsNameOptions": PrivateDnsNameOptionsResponseTypeDef,
        "Ipv6Address": str,
        "TpmSupport": str,
        "MaintenanceOptions": InstanceMaintenanceOptionsTypeDef,
    },
    total=False,
)

FleetLaunchTemplateConfigRequestTypeDef = TypedDict(
    "FleetLaunchTemplateConfigRequestTypeDef",
    {
        "LaunchTemplateSpecification": FleetLaunchTemplateSpecificationRequestTypeDef,
        "Overrides": Sequence[FleetLaunchTemplateOverridesRequestTypeDef],
    },
    total=False,
)

_RequiredGetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef = TypedDict(
    "_RequiredGetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef",
    {
        "TargetCapacity": int,
    },
)
_OptionalGetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef = TypedDict(
    "_OptionalGetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef",
    {
        "InstanceTypes": Sequence[str],
        "TargetCapacityUnitType": TargetCapacityUnitTypeType,
        "SingleAvailabilityZone": bool,
        "RegionNames": Sequence[str],
        "InstanceRequirementsWithMetadata": InstanceRequirementsWithMetadataRequestTypeDef,
        "DryRun": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef(
    _RequiredGetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef,
    _OptionalGetSpotPlacementScoresRequestGetSpotPlacementScoresPaginateTypeDef,
):
    pass


_RequiredGetSpotPlacementScoresRequestRequestTypeDef = TypedDict(
    "_RequiredGetSpotPlacementScoresRequestRequestTypeDef",
    {
        "TargetCapacity": int,
    },
)
_OptionalGetSpotPlacementScoresRequestRequestTypeDef = TypedDict(
    "_OptionalGetSpotPlacementScoresRequestRequestTypeDef",
    {
        "InstanceTypes": Sequence[str],
        "TargetCapacityUnitType": TargetCapacityUnitTypeType,
        "SingleAvailabilityZone": bool,
        "RegionNames": Sequence[str],
        "InstanceRequirementsWithMetadata": InstanceRequirementsWithMetadataRequestTypeDef,
        "DryRun": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetSpotPlacementScoresRequestRequestTypeDef(
    _RequiredGetSpotPlacementScoresRequestRequestTypeDef,
    _OptionalGetSpotPlacementScoresRequestRequestTypeDef,
):
    pass


FleetLaunchTemplateConfigTypeDef = TypedDict(
    "FleetLaunchTemplateConfigTypeDef",
    {
        "LaunchTemplateSpecification": FleetLaunchTemplateSpecificationTypeDef,
        "Overrides": List[FleetLaunchTemplateOverridesTypeDef],
    },
    total=False,
)

LaunchTemplateAndOverridesResponseTypeDef = TypedDict(
    "LaunchTemplateAndOverridesResponseTypeDef",
    {
        "LaunchTemplateSpecification": FleetLaunchTemplateSpecificationTypeDef,
        "Overrides": FleetLaunchTemplateOverridesTypeDef,
    },
    total=False,
)

LaunchTemplateConfigTypeDef = TypedDict(
    "LaunchTemplateConfigTypeDef",
    {
        "LaunchTemplateSpecification": FleetLaunchTemplateSpecificationTypeDef,
        "Overrides": List[LaunchTemplateOverridesTypeDef],
    },
    total=False,
)

DescribeInstanceStatusResultTypeDef = TypedDict(
    "DescribeInstanceStatusResultTypeDef",
    {
        "InstanceStatuses": List[InstanceStatusTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSecurityGroupsResultTypeDef = TypedDict(
    "DescribeSecurityGroupsResultTypeDef",
    {
        "SecurityGroups": List[SecurityGroupTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStaleSecurityGroupsResultTypeDef = TypedDict(
    "DescribeStaleSecurityGroupsResultTypeDef",
    {
        "NextToken": str,
        "StaleSecurityGroupSet": List[StaleSecurityGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateLaunchTemplateRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLaunchTemplateRequestRequestTypeDef",
    {
        "LaunchTemplateName": str,
        "LaunchTemplateData": RequestLaunchTemplateDataTypeDef,
    },
)
_OptionalCreateLaunchTemplateRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLaunchTemplateRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ClientToken": str,
        "VersionDescription": str,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateLaunchTemplateRequestRequestTypeDef(
    _RequiredCreateLaunchTemplateRequestRequestTypeDef,
    _OptionalCreateLaunchTemplateRequestRequestTypeDef,
):
    pass


_RequiredCreateLaunchTemplateVersionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLaunchTemplateVersionRequestRequestTypeDef",
    {
        "LaunchTemplateData": RequestLaunchTemplateDataTypeDef,
    },
)
_OptionalCreateLaunchTemplateVersionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLaunchTemplateVersionRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ClientToken": str,
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "SourceVersion": str,
        "VersionDescription": str,
    },
    total=False,
)


class CreateLaunchTemplateVersionRequestRequestTypeDef(
    _RequiredCreateLaunchTemplateVersionRequestRequestTypeDef,
    _OptionalCreateLaunchTemplateVersionRequestRequestTypeDef,
):
    pass


GetLaunchTemplateDataResultTypeDef = TypedDict(
    "GetLaunchTemplateDataResultTypeDef",
    {
        "LaunchTemplateData": ResponseLaunchTemplateDataTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LaunchTemplateVersionTypeDef = TypedDict(
    "LaunchTemplateVersionTypeDef",
    {
        "LaunchTemplateId": str,
        "LaunchTemplateName": str,
        "VersionNumber": int,
        "VersionDescription": str,
        "CreateTime": datetime,
        "CreatedBy": str,
        "DefaultVersion": bool,
        "LaunchTemplateData": ResponseLaunchTemplateDataTypeDef,
    },
    total=False,
)

DescribeReservedInstancesModificationsResultTypeDef = TypedDict(
    "DescribeReservedInstancesModificationsResultTypeDef",
    {
        "NextToken": str,
        "ReservedInstancesModifications": List[ReservedInstancesModificationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateVpnConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpnConnectionRequestRequestTypeDef",
    {
        "CustomerGatewayId": str,
        "Type": str,
    },
)
_OptionalCreateVpnConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpnConnectionRequestRequestTypeDef",
    {
        "VpnGatewayId": str,
        "TransitGatewayId": str,
        "DryRun": bool,
        "Options": VpnConnectionOptionsSpecificationTypeDef,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
    },
    total=False,
)


class CreateVpnConnectionRequestRequestTypeDef(
    _RequiredCreateVpnConnectionRequestRequestTypeDef,
    _OptionalCreateVpnConnectionRequestRequestTypeDef,
):
    pass


CreateNetworkInterfaceResultTypeDef = TypedDict(
    "CreateNetworkInterfaceResultTypeDef",
    {
        "NetworkInterface": NetworkInterfaceTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInterfacesResultTypeDef = TypedDict(
    "DescribeNetworkInterfacesResultTypeDef",
    {
        "NetworkInterfaces": List[NetworkInterfaceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateNetworkInsightsAccessScopeRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNetworkInsightsAccessScopeRequestRequestTypeDef",
    {
        "ClientToken": str,
    },
)
_OptionalCreateNetworkInsightsAccessScopeRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNetworkInsightsAccessScopeRequestRequestTypeDef",
    {
        "MatchPaths": Sequence[AccessScopePathRequestTypeDef],
        "ExcludePaths": Sequence[AccessScopePathRequestTypeDef],
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "DryRun": bool,
    },
    total=False,
)


class CreateNetworkInsightsAccessScopeRequestRequestTypeDef(
    _RequiredCreateNetworkInsightsAccessScopeRequestRequestTypeDef,
    _OptionalCreateNetworkInsightsAccessScopeRequestRequestTypeDef,
):
    pass


NetworkInsightsAccessScopeContentTypeDef = TypedDict(
    "NetworkInsightsAccessScopeContentTypeDef",
    {
        "NetworkInsightsAccessScopeId": str,
        "MatchPaths": List[AccessScopePathTypeDef],
        "ExcludePaths": List[AccessScopePathTypeDef],
    },
    total=False,
)

VpnConnectionTypeDef = TypedDict(
    "VpnConnectionTypeDef",
    {
        "CustomerGatewayConfiguration": str,
        "CustomerGatewayId": str,
        "Category": str,
        "State": VpnStateType,
        "Type": Literal["ipsec.1"],
        "VpnConnectionId": str,
        "VpnGatewayId": str,
        "TransitGatewayId": str,
        "CoreNetworkArn": str,
        "CoreNetworkAttachmentArn": str,
        "GatewayAssociationState": GatewayAssociationStateType,
        "Options": VpnConnectionOptionsTypeDef,
        "Routes": List[VpnStaticRouteTypeDef],
        "Tags": List[TagTypeDef],
        "VgwTelemetry": List[VgwTelemetryTypeDef],
    },
    total=False,
)

BundleInstanceResultTypeDef = TypedDict(
    "BundleInstanceResultTypeDef",
    {
        "BundleTask": BundleTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CancelBundleTaskResultTypeDef = TypedDict(
    "CancelBundleTaskResultTypeDef",
    {
        "BundleTask": BundleTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeBundleTasksResultTypeDef = TypedDict(
    "DescribeBundleTasksResultTypeDef",
    {
        "BundleTasks": List[BundleTaskTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredRunScheduledInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredRunScheduledInstancesRequestRequestTypeDef",
    {
        "LaunchSpecification": ScheduledInstancesLaunchSpecificationTypeDef,
        "ScheduledInstanceId": str,
    },
)
_OptionalRunScheduledInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalRunScheduledInstancesRequestRequestTypeDef",
    {
        "ClientToken": str,
        "DryRun": bool,
        "InstanceCount": int,
    },
    total=False,
)


class RunScheduledInstancesRequestRequestTypeDef(
    _RequiredRunScheduledInstancesRequestRequestTypeDef,
    _OptionalRunScheduledInstancesRequestRequestTypeDef,
):
    pass


DescribeImportImageTasksResultTypeDef = TypedDict(
    "DescribeImportImageTasksResultTypeDef",
    {
        "ImportImageTasks": List[ImportImageTaskTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImportSnapshotTasksResultTypeDef = TypedDict(
    "DescribeImportSnapshotTasksResultTypeDef",
    {
        "ImportSnapshotTasks": List[ImportSnapshotTaskTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDefaultSubnetResultTypeDef = TypedDict(
    "CreateDefaultSubnetResultTypeDef",
    {
        "Subnet": SubnetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSubnetResultTypeDef = TypedDict(
    "CreateSubnetResultTypeDef",
    {
        "Subnet": SubnetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSubnetsResultTypeDef = TypedDict(
    "DescribeSubnetsResultTypeDef",
    {
        "Subnets": List[SubnetTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTrafficMirrorFilterResultTypeDef = TypedDict(
    "CreateTrafficMirrorFilterResultTypeDef",
    {
        "TrafficMirrorFilter": TrafficMirrorFilterTypeDef,
        "ClientToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrafficMirrorFiltersResultTypeDef = TypedDict(
    "DescribeTrafficMirrorFiltersResultTypeDef",
    {
        "TrafficMirrorFilters": List[TrafficMirrorFilterTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyTrafficMirrorFilterNetworkServicesResultTypeDef = TypedDict(
    "ModifyTrafficMirrorFilterNetworkServicesResultTypeDef",
    {
        "TrafficMirrorFilter": TrafficMirrorFilterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransitGatewayConnectPeerResultTypeDef = TypedDict(
    "CreateTransitGatewayConnectPeerResultTypeDef",
    {
        "TransitGatewayConnectPeer": TransitGatewayConnectPeerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTransitGatewayConnectPeerResultTypeDef = TypedDict(
    "DeleteTransitGatewayConnectPeerResultTypeDef",
    {
        "TransitGatewayConnectPeer": TransitGatewayConnectPeerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTransitGatewayConnectPeersResultTypeDef = TypedDict(
    "DescribeTransitGatewayConnectPeersResultTypeDef",
    {
        "TransitGatewayConnectPeers": List[TransitGatewayConnectPeerTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVolumeStatusResultTypeDef = TypedDict(
    "DescribeVolumeStatusResultTypeDef",
    {
        "NextToken": str,
        "VolumeStatuses": List[VolumeStatusItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDefaultVpcResultTypeDef = TypedDict(
    "CreateDefaultVpcResultTypeDef",
    {
        "Vpc": VpcTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateVpcResultTypeDef = TypedDict(
    "CreateVpcResultTypeDef",
    {
        "Vpc": VpcTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcsResultTypeDef = TypedDict(
    "DescribeVpcsResultTypeDef",
    {
        "Vpcs": List[VpcTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AcceptVpcPeeringConnectionResultTypeDef = TypedDict(
    "AcceptVpcPeeringConnectionResultTypeDef",
    {
        "VpcPeeringConnection": VpcPeeringConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateVpcPeeringConnectionResultTypeDef = TypedDict(
    "CreateVpcPeeringConnectionResultTypeDef",
    {
        "VpcPeeringConnection": VpcPeeringConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcPeeringConnectionsResultTypeDef = TypedDict(
    "DescribeVpcPeeringConnectionsResultTypeDef",
    {
        "VpcPeeringConnections": List[VpcPeeringConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetNetworkInsightsAccessScopeAnalysisFindingsResultTypeDef = TypedDict(
    "GetNetworkInsightsAccessScopeAnalysisFindingsResultTypeDef",
    {
        "NetworkInsightsAccessScopeAnalysisId": str,
        "AnalysisStatus": AnalysisStatusType,
        "AnalysisFindings": List[AccessScopeAnalysisFindingTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeNetworkInsightsAnalysesResultTypeDef = TypedDict(
    "DescribeNetworkInsightsAnalysesResultTypeDef",
    {
        "NetworkInsightsAnalyses": List[NetworkInsightsAnalysisTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartNetworkInsightsAnalysisResultTypeDef = TypedDict(
    "StartNetworkInsightsAnalysisResultTypeDef",
    {
        "NetworkInsightsAnalysis": NetworkInsightsAnalysisTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpotInstanceRequestsResultTypeDef = TypedDict(
    "DescribeSpotInstanceRequestsResultTypeDef",
    {
        "SpotInstanceRequests": List[SpotInstanceRequestTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RequestSpotInstancesResultTypeDef = TypedDict(
    "RequestSpotInstancesResultTypeDef",
    {
        "SpotInstanceRequests": List[SpotInstanceRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeConversionTasksResultTypeDef = TypedDict(
    "DescribeConversionTasksResultTypeDef",
    {
        "ConversionTasks": List[ConversionTaskTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportInstanceResultTypeDef = TypedDict(
    "ImportInstanceResultTypeDef",
    {
        "ConversionTask": ConversionTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportVolumeResultTypeDef = TypedDict(
    "ImportVolumeResultTypeDef",
    {
        "ConversionTask": ConversionTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInstanceTypesResultTypeDef = TypedDict(
    "DescribeInstanceTypesResultTypeDef",
    {
        "InstanceTypes": List[InstanceTypeInfoTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReservationResponseMetadataTypeDef = TypedDict(
    "ReservationResponseMetadataTypeDef",
    {
        "Groups": List[GroupIdentifierTypeDef],
        "Instances": List[InstanceTypeDef],
        "OwnerId": str,
        "RequesterId": str,
        "ReservationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReservationTypeDef = TypedDict(
    "ReservationTypeDef",
    {
        "Groups": List[GroupIdentifierTypeDef],
        "Instances": List[InstanceTypeDef],
        "OwnerId": str,
        "RequesterId": str,
        "ReservationId": str,
    },
    total=False,
)

_RequiredCreateFleetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateFleetRequestRequestTypeDef",
    {
        "LaunchTemplateConfigs": Sequence[FleetLaunchTemplateConfigRequestTypeDef],
        "TargetCapacitySpecification": TargetCapacitySpecificationRequestTypeDef,
    },
)
_OptionalCreateFleetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateFleetRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ClientToken": str,
        "SpotOptions": SpotOptionsRequestTypeDef,
        "OnDemandOptions": OnDemandOptionsRequestTypeDef,
        "ExcessCapacityTerminationPolicy": FleetExcessCapacityTerminationPolicyType,
        "TerminateInstancesWithExpiration": bool,
        "Type": FleetTypeType,
        "ValidFrom": Union[datetime, str],
        "ValidUntil": Union[datetime, str],
        "ReplaceUnhealthyInstances": bool,
        "TagSpecifications": Sequence[TagSpecificationTypeDef],
        "Context": str,
    },
    total=False,
)


class CreateFleetRequestRequestTypeDef(
    _RequiredCreateFleetRequestRequestTypeDef, _OptionalCreateFleetRequestRequestTypeDef
):
    pass


_RequiredModifyFleetRequestRequestTypeDef = TypedDict(
    "_RequiredModifyFleetRequestRequestTypeDef",
    {
        "FleetId": str,
    },
)
_OptionalModifyFleetRequestRequestTypeDef = TypedDict(
    "_OptionalModifyFleetRequestRequestTypeDef",
    {
        "DryRun": bool,
        "ExcessCapacityTerminationPolicy": FleetExcessCapacityTerminationPolicyType,
        "LaunchTemplateConfigs": Sequence[FleetLaunchTemplateConfigRequestTypeDef],
        "TargetCapacitySpecification": TargetCapacitySpecificationRequestTypeDef,
        "Context": str,
    },
    total=False,
)


class ModifyFleetRequestRequestTypeDef(
    _RequiredModifyFleetRequestRequestTypeDef, _OptionalModifyFleetRequestRequestTypeDef
):
    pass


CreateFleetErrorTypeDef = TypedDict(
    "CreateFleetErrorTypeDef",
    {
        "LaunchTemplateAndOverrides": LaunchTemplateAndOverridesResponseTypeDef,
        "Lifecycle": InstanceLifecycleType,
        "ErrorCode": str,
        "ErrorMessage": str,
    },
    total=False,
)

CreateFleetInstanceTypeDef = TypedDict(
    "CreateFleetInstanceTypeDef",
    {
        "LaunchTemplateAndOverrides": LaunchTemplateAndOverridesResponseTypeDef,
        "Lifecycle": InstanceLifecycleType,
        "InstanceIds": List[str],
        "InstanceType": InstanceTypeType,
        "Platform": Literal["Windows"],
    },
    total=False,
)

DescribeFleetErrorTypeDef = TypedDict(
    "DescribeFleetErrorTypeDef",
    {
        "LaunchTemplateAndOverrides": LaunchTemplateAndOverridesResponseTypeDef,
        "Lifecycle": InstanceLifecycleType,
        "ErrorCode": str,
        "ErrorMessage": str,
    },
    total=False,
)

DescribeFleetsInstancesTypeDef = TypedDict(
    "DescribeFleetsInstancesTypeDef",
    {
        "LaunchTemplateAndOverrides": LaunchTemplateAndOverridesResponseTypeDef,
        "Lifecycle": InstanceLifecycleType,
        "InstanceIds": List[str],
        "InstanceType": InstanceTypeType,
        "Platform": Literal["Windows"],
    },
    total=False,
)

_RequiredModifySpotFleetRequestRequestRequestTypeDef = TypedDict(
    "_RequiredModifySpotFleetRequestRequestRequestTypeDef",
    {
        "SpotFleetRequestId": str,
    },
)
_OptionalModifySpotFleetRequestRequestRequestTypeDef = TypedDict(
    "_OptionalModifySpotFleetRequestRequestRequestTypeDef",
    {
        "ExcessCapacityTerminationPolicy": ExcessCapacityTerminationPolicyType,
        "LaunchTemplateConfigs": Sequence[LaunchTemplateConfigTypeDef],
        "TargetCapacity": int,
        "OnDemandTargetCapacity": int,
        "Context": str,
    },
    total=False,
)


class ModifySpotFleetRequestRequestRequestTypeDef(
    _RequiredModifySpotFleetRequestRequestRequestTypeDef,
    _OptionalModifySpotFleetRequestRequestRequestTypeDef,
):
    pass


_RequiredSpotFleetRequestConfigDataTypeDef = TypedDict(
    "_RequiredSpotFleetRequestConfigDataTypeDef",
    {
        "IamFleetRole": str,
        "TargetCapacity": int,
    },
)
_OptionalSpotFleetRequestConfigDataTypeDef = TypedDict(
    "_OptionalSpotFleetRequestConfigDataTypeDef",
    {
        "AllocationStrategy": AllocationStrategyType,
        "OnDemandAllocationStrategy": OnDemandAllocationStrategyType,
        "SpotMaintenanceStrategies": SpotMaintenanceStrategiesTypeDef,
        "ClientToken": str,
        "ExcessCapacityTerminationPolicy": ExcessCapacityTerminationPolicyType,
        "FulfilledCapacity": float,
        "OnDemandFulfilledCapacity": float,
        "LaunchSpecifications": List[SpotFleetLaunchSpecificationTypeDef],
        "LaunchTemplateConfigs": List[LaunchTemplateConfigTypeDef],
        "SpotPrice": str,
        "OnDemandTargetCapacity": int,
        "OnDemandMaxTotalPrice": str,
        "SpotMaxTotalPrice": str,
        "TerminateInstancesWithExpiration": bool,
        "Type": FleetTypeType,
        "ValidFrom": datetime,
        "ValidUntil": datetime,
        "ReplaceUnhealthyInstances": bool,
        "InstanceInterruptionBehavior": InstanceInterruptionBehaviorType,
        "LoadBalancersConfig": LoadBalancersConfigTypeDef,
        "InstancePoolsToUseCount": int,
        "Context": str,
        "TargetCapacityUnitType": TargetCapacityUnitTypeType,
        "TagSpecifications": List[TagSpecificationTypeDef],
    },
    total=False,
)


class SpotFleetRequestConfigDataTypeDef(
    _RequiredSpotFleetRequestConfigDataTypeDef, _OptionalSpotFleetRequestConfigDataTypeDef
):
    pass


CreateLaunchTemplateVersionResultTypeDef = TypedDict(
    "CreateLaunchTemplateVersionResultTypeDef",
    {
        "LaunchTemplateVersion": LaunchTemplateVersionTypeDef,
        "Warning": ValidationWarningTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLaunchTemplateVersionsResultTypeDef = TypedDict(
    "DescribeLaunchTemplateVersionsResultTypeDef",
    {
        "LaunchTemplateVersions": List[LaunchTemplateVersionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateNetworkInsightsAccessScopeResultTypeDef = TypedDict(
    "CreateNetworkInsightsAccessScopeResultTypeDef",
    {
        "NetworkInsightsAccessScope": NetworkInsightsAccessScopeTypeDef,
        "NetworkInsightsAccessScopeContent": NetworkInsightsAccessScopeContentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetNetworkInsightsAccessScopeContentResultTypeDef = TypedDict(
    "GetNetworkInsightsAccessScopeContentResultTypeDef",
    {
        "NetworkInsightsAccessScopeContent": NetworkInsightsAccessScopeContentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateVpnConnectionResultTypeDef = TypedDict(
    "CreateVpnConnectionResultTypeDef",
    {
        "VpnConnection": VpnConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpnConnectionsResultTypeDef = TypedDict(
    "DescribeVpnConnectionsResultTypeDef",
    {
        "VpnConnections": List[VpnConnectionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpnConnectionOptionsResultTypeDef = TypedDict(
    "ModifyVpnConnectionOptionsResultTypeDef",
    {
        "VpnConnection": VpnConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpnConnectionResultTypeDef = TypedDict(
    "ModifyVpnConnectionResultTypeDef",
    {
        "VpnConnection": VpnConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpnTunnelCertificateResultTypeDef = TypedDict(
    "ModifyVpnTunnelCertificateResultTypeDef",
    {
        "VpnConnection": VpnConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyVpnTunnelOptionsResultTypeDef = TypedDict(
    "ModifyVpnTunnelOptionsResultTypeDef",
    {
        "VpnConnection": VpnConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeInstancesResultTypeDef = TypedDict(
    "DescribeInstancesResultTypeDef",
    {
        "Reservations": List[ReservationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFleetResultTypeDef = TypedDict(
    "CreateFleetResultTypeDef",
    {
        "FleetId": str,
        "Errors": List[CreateFleetErrorTypeDef],
        "Instances": List[CreateFleetInstanceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FleetDataTypeDef = TypedDict(
    "FleetDataTypeDef",
    {
        "ActivityStatus": FleetActivityStatusType,
        "CreateTime": datetime,
        "FleetId": str,
        "FleetState": FleetStateCodeType,
        "ClientToken": str,
        "ExcessCapacityTerminationPolicy": FleetExcessCapacityTerminationPolicyType,
        "FulfilledCapacity": float,
        "FulfilledOnDemandCapacity": float,
        "LaunchTemplateConfigs": List[FleetLaunchTemplateConfigTypeDef],
        "TargetCapacitySpecification": TargetCapacitySpecificationTypeDef,
        "TerminateInstancesWithExpiration": bool,
        "Type": FleetTypeType,
        "ValidFrom": datetime,
        "ValidUntil": datetime,
        "ReplaceUnhealthyInstances": bool,
        "SpotOptions": SpotOptionsTypeDef,
        "OnDemandOptions": OnDemandOptionsTypeDef,
        "Tags": List[TagTypeDef],
        "Errors": List[DescribeFleetErrorTypeDef],
        "Instances": List[DescribeFleetsInstancesTypeDef],
        "Context": str,
    },
    total=False,
)

_RequiredRequestSpotFleetRequestRequestTypeDef = TypedDict(
    "_RequiredRequestSpotFleetRequestRequestTypeDef",
    {
        "SpotFleetRequestConfig": SpotFleetRequestConfigDataTypeDef,
    },
)
_OptionalRequestSpotFleetRequestRequestTypeDef = TypedDict(
    "_OptionalRequestSpotFleetRequestRequestTypeDef",
    {
        "DryRun": bool,
    },
    total=False,
)


class RequestSpotFleetRequestRequestTypeDef(
    _RequiredRequestSpotFleetRequestRequestTypeDef, _OptionalRequestSpotFleetRequestRequestTypeDef
):
    pass


SpotFleetRequestConfigTypeDef = TypedDict(
    "SpotFleetRequestConfigTypeDef",
    {
        "ActivityStatus": ActivityStatusType,
        "CreateTime": datetime,
        "SpotFleetRequestConfig": SpotFleetRequestConfigDataTypeDef,
        "SpotFleetRequestId": str,
        "SpotFleetRequestState": BatchStateType,
        "Tags": List[TagTypeDef],
    },
    total=False,
)

DescribeFleetsResultTypeDef = TypedDict(
    "DescribeFleetsResultTypeDef",
    {
        "NextToken": str,
        "Fleets": List[FleetDataTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpotFleetRequestsResponseTypeDef = TypedDict(
    "DescribeSpotFleetRequestsResponseTypeDef",
    {
        "NextToken": str,
        "SpotFleetRequestConfigs": List[SpotFleetRequestConfigTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
