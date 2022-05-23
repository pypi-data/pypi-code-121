import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccountLinked = bool
AddGwMetadata = bool
AmazonId = str
AmazonResourceName = str
AppEui = str
AppKey = str
AppSKey = str
AppServerPrivateKey = str
AutoCreateTasks = bool
CertificatePEM = str
CertificateValue = str
ChannelMask = str
ClassBTimeout = int
ClassCTimeout = int
ClientRequestToken = str
Description = str
DestinationArn = str
DestinationName = str
DevAddr = str
DevEui = str
DevStatusReqFreq = int
DeviceProfileArn = str
DeviceProfileId = str
DeviceProfileName = str
DlBucketSize = int
DlDr = int
DlFreq = int
DlRate = int
DlRatePolicy = str
Double = float
DrMax = int
DrMin = int
EndPoint = str
Expression = str
FCntStart = int
FNwkSIntKey = str
FPort = int
Fingerprint = str
FirmwareUpdateImage = str
FirmwareUpdateRole = str
FuotaTaskArn = str
FuotaTaskId = str
FuotaTaskName = str
GatewayEui = str
GenAppKey = str
HrAllowed = bool
ISODateTimeString = str
Identifier = str
Integer = int
IotCertificateId = str
JoinEui = str
MacVersion = str
MaxDutyCycle = int
MaxEirp = int
MaxResults = int
McGroupId = int
Message = str
MessageId = str
MinGwDiversity = int
Model = str
MulticastDeviceStatus = str
MulticastGroupArn = str
MulticastGroupId = str
MulticastGroupMessageId = str
MulticastGroupName = str
MulticastGroupStatus = str
NetId = str
NetworkAnalyzerConfigurationArn = str
NetworkAnalyzerConfigurationName = str
NextToken = str
NumberOfDevicesInGroup = int
NumberOfDevicesRequested = int
NwkGeoLoc = bool
NwkKey = str
NwkSEncKey = str
NwkSKey = str
PackageVersion = str
PartnerAccountArn = str
PartnerAccountId = str
PayloadData = str
PingSlotDr = int
PingSlotFreq = int
PingSlotPeriod = int
PrAllowed = bool
PresetFreq = int
QueryString = str
RaAllowed = bool
RegParamsRevision = str
ReportDevStatusBattery = bool
ReportDevStatusMargin = bool
ResourceId = str
ResourceIdentifier = str
ResourceType = str
Result = str
RfRegion = str
RoleArn = str
RxDataRate2 = int
RxDelay1 = int
RxDrOffset1 = int
RxFreq2 = int
SNwkSIntKey = str
Seq = int
ServiceProfileArn = str
ServiceProfileId = str
ServiceProfileName = str
SessionTimeout = int
SidewalkId = str
SidewalkManufacturingSn = str
Station = str
SubBand = int
Supports32BitFCnt = bool
SupportsClassB = bool
SupportsClassC = bool
SupportsJoin = bool
TagKey = str
TagValue = str
TargetPer = int
ThingArn = str
ThingName = str
TransmitMode = int
UlBucketSize = int
UlRate = int
UlRatePolicy = str
UpdateDataSource = str
UpdateSignature = str
WirelessDeviceArn = str
WirelessDeviceId = str
WirelessDeviceName = str
WirelessGatewayArn = str
WirelessGatewayId = str
WirelessGatewayName = str
WirelessGatewayTaskDefinitionArn = str
WirelessGatewayTaskDefinitionId = str
WirelessGatewayTaskName = str


class BatteryLevel(str):
    normal = "normal"
    low = "low"
    critical = "critical"


class ConnectionStatus(str):
    Connected = "Connected"
    Disconnected = "Disconnected"


class DeviceState(str):
    Provisioned = "Provisioned"
    RegisteredNotSeen = "RegisteredNotSeen"
    RegisteredReachable = "RegisteredReachable"
    RegisteredUnreachable = "RegisteredUnreachable"


class DlClass(str):
    ClassB = "ClassB"
    ClassC = "ClassC"


class Event(str):
    discovered = "discovered"
    lost = "lost"
    ack = "ack"
    nack = "nack"
    passthrough = "passthrough"


class EventNotificationPartnerType(str):
    Sidewalk = "Sidewalk"


class EventNotificationResourceType(str):
    SidewalkAccount = "SidewalkAccount"
    WirelessDevice = "WirelessDevice"
    WirelessGateway = "WirelessGateway"


class EventNotificationTopicStatus(str):
    Enabled = "Enabled"
    Disabled = "Disabled"


class ExpressionType(str):
    RuleName = "RuleName"
    MqttTopic = "MqttTopic"


class FuotaDeviceStatus(str):
    Initial = "Initial"
    Package_Not_Supported = "Package_Not_Supported"
    FragAlgo_unsupported = "FragAlgo_unsupported"
    Not_enough_memory = "Not_enough_memory"
    FragIndex_unsupported = "FragIndex_unsupported"
    Wrong_descriptor = "Wrong_descriptor"
    SessionCnt_replay = "SessionCnt_replay"
    MissingFrag = "MissingFrag"
    MemoryError = "MemoryError"
    MICError = "MICError"
    Successful = "Successful"


class FuotaTaskStatus(str):
    Pending = "Pending"
    FuotaSession_Waiting = "FuotaSession_Waiting"
    In_FuotaSession = "In_FuotaSession"
    FuotaDone = "FuotaDone"
    Delete_Waiting = "Delete_Waiting"


class IdentifierType(str):
    PartnerAccountId = "PartnerAccountId"
    DevEui = "DevEui"
    GatewayEui = "GatewayEui"
    WirelessDeviceId = "WirelessDeviceId"
    WirelessGatewayId = "WirelessGatewayId"


class LogLevel(str):
    INFO = "INFO"
    ERROR = "ERROR"
    DISABLED = "DISABLED"


class MessageType(str):
    CUSTOM_COMMAND_ID_NOTIFY = "CUSTOM_COMMAND_ID_NOTIFY"
    CUSTOM_COMMAND_ID_GET = "CUSTOM_COMMAND_ID_GET"
    CUSTOM_COMMAND_ID_SET = "CUSTOM_COMMAND_ID_SET"
    CUSTOM_COMMAND_ID_RESP = "CUSTOM_COMMAND_ID_RESP"


class PartnerType(str):
    Sidewalk = "Sidewalk"


class SigningAlg(str):
    Ed25519 = "Ed25519"
    P256r1 = "P256r1"


class SupportedRfRegion(str):
    EU868 = "EU868"
    US915 = "US915"
    AU915 = "AU915"
    AS923_1 = "AS923-1"


class WirelessDeviceEvent(str):
    Join = "Join"
    Rejoin = "Rejoin"
    Uplink_Data = "Uplink_Data"
    Downlink_Data = "Downlink_Data"
    Registration = "Registration"


class WirelessDeviceFrameInfo(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class WirelessDeviceIdType(str):
    WirelessDeviceId = "WirelessDeviceId"
    DevEui = "DevEui"
    ThingName = "ThingName"
    SidewalkManufacturingSn = "SidewalkManufacturingSn"


class WirelessDeviceType(str):
    Sidewalk = "Sidewalk"
    LoRaWAN = "LoRaWAN"


class WirelessGatewayEvent(str):
    CUPS_Request = "CUPS_Request"
    Certificate = "Certificate"


class WirelessGatewayIdType(str):
    GatewayEui = "GatewayEui"
    WirelessGatewayId = "WirelessGatewayId"
    ThingName = "ThingName"


class WirelessGatewayServiceType(str):
    CUPS = "CUPS"
    LNS = "LNS"


class WirelessGatewayTaskDefinitionType(str):
    UPDATE = "UPDATE"


class WirelessGatewayTaskStatus(str):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    FIRST_RETRY = "FIRST_RETRY"
    SECOND_RETRY = "SECOND_RETRY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WirelessGatewayType(str):
    LoRaWAN = "LoRaWAN"


class AccessDeniedException(ServiceException):
    """User does not have permission to perform this action."""

    Message: Optional[Message]


class ConflictException(ServiceException):
    """Adding, updating, or deleting the resource can cause an inconsistent
    state.
    """

    Message: Optional[Message]
    ResourceId: Optional[ResourceId]
    ResourceType: Optional[ResourceType]


class InternalServerException(ServiceException):
    """An unexpected error occurred while processing a request."""

    Message: Optional[Message]


class ResourceNotFoundException(ServiceException):
    """Resource does not exist."""

    Message: Optional[Message]
    ResourceId: Optional[ResourceId]
    ResourceType: Optional[ResourceType]


class ThrottlingException(ServiceException):
    """The request was denied because it exceeded the allowed API request rate."""

    Message: Optional[Message]


class TooManyTagsException(ServiceException):
    """The request was denied because the resource can't have any more tags."""

    Message: Optional[Message]
    ResourceName: Optional[AmazonResourceName]


class ValidationException(ServiceException):
    """The input did not meet the specified constraints."""

    Message: Optional[Message]


class SessionKeysAbpV1_0_x(TypedDict, total=False):
    """Session keys for ABP v1.1"""

    NwkSKey: Optional[NwkSKey]
    AppSKey: Optional[AppSKey]


class AbpV1_0_x(TypedDict, total=False):
    """ABP device object for LoRaWAN specification v1.0.x"""

    DevAddr: Optional[DevAddr]
    SessionKeys: Optional[SessionKeysAbpV1_0_x]
    FCntStart: Optional[FCntStart]


class SessionKeysAbpV1_1(TypedDict, total=False):
    """Session keys for ABP v1.1"""

    FNwkSIntKey: Optional[FNwkSIntKey]
    SNwkSIntKey: Optional[SNwkSIntKey]
    NwkSEncKey: Optional[NwkSEncKey]
    AppSKey: Optional[AppSKey]


class AbpV1_1(TypedDict, total=False):
    """ABP device object for LoRaWAN specification v1.1"""

    DevAddr: Optional[DevAddr]
    SessionKeys: Optional[SessionKeysAbpV1_1]
    FCntStart: Optional[FCntStart]


class Tag(TypedDict, total=False):
    """A simple label consisting of a customer-defined key-value pair"""

    Key: TagKey
    Value: TagValue


TagList = List[Tag]


class SidewalkAccountInfo(TypedDict, total=False):
    """Information about a Sidewalk account."""

    AmazonId: Optional[AmazonId]
    AppServerPrivateKey: Optional[AppServerPrivateKey]


class AssociateAwsAccountWithPartnerAccountRequest(ServiceRequest):
    Sidewalk: SidewalkAccountInfo
    ClientRequestToken: Optional[ClientRequestToken]
    Tags: Optional[TagList]


class AssociateAwsAccountWithPartnerAccountResponse(TypedDict, total=False):
    Sidewalk: Optional[SidewalkAccountInfo]
    Arn: Optional[PartnerAccountArn]


class AssociateMulticastGroupWithFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    MulticastGroupId: MulticastGroupId


class AssociateMulticastGroupWithFuotaTaskResponse(TypedDict, total=False):
    pass


class AssociateWirelessDeviceWithFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    WirelessDeviceId: WirelessDeviceId


class AssociateWirelessDeviceWithFuotaTaskResponse(TypedDict, total=False):
    pass


class AssociateWirelessDeviceWithMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId
    WirelessDeviceId: WirelessDeviceId


class AssociateWirelessDeviceWithMulticastGroupResponse(TypedDict, total=False):
    pass


class AssociateWirelessDeviceWithThingRequest(ServiceRequest):
    Id: WirelessDeviceId
    ThingArn: ThingArn


class AssociateWirelessDeviceWithThingResponse(TypedDict, total=False):
    pass


class AssociateWirelessGatewayWithCertificateRequest(ServiceRequest):
    Id: WirelessGatewayId
    IotCertificateId: IotCertificateId


class AssociateWirelessGatewayWithCertificateResponse(TypedDict, total=False):
    IotCertificateId: Optional[IotCertificateId]


class AssociateWirelessGatewayWithThingRequest(ServiceRequest):
    Id: WirelessGatewayId
    ThingArn: ThingArn


class AssociateWirelessGatewayWithThingResponse(TypedDict, total=False):
    pass


class CancelMulticastGroupSessionRequest(ServiceRequest):
    Id: MulticastGroupId


class CancelMulticastGroupSessionResponse(TypedDict, total=False):
    pass


class CertificateList(TypedDict, total=False):
    """List of sidewalk certificates."""

    SigningAlg: SigningAlg
    Value: CertificateValue


class LoRaWANConnectionStatusEventNotificationConfigurations(TypedDict, total=False):
    """Object for LoRaWAN connection status resource type event configuration."""

    GatewayEuiEventTopic: Optional[EventNotificationTopicStatus]


class ConnectionStatusEventConfiguration(TypedDict, total=False):
    """Connection status event configuration object for enabling or disabling
    topic.
    """

    LoRaWAN: Optional[LoRaWANConnectionStatusEventNotificationConfigurations]
    WirelessGatewayIdEventTopic: Optional[EventNotificationTopicStatus]


class LoRaWANConnectionStatusResourceTypeEventConfiguration(TypedDict, total=False):
    """Object for LoRaWAN connection status resource type event configuration."""

    WirelessGatewayEventTopic: Optional[EventNotificationTopicStatus]


class ConnectionStatusResourceTypeEventConfiguration(TypedDict, total=False):
    """Connection status resource type event configuration object for enabling
    or disabling topic.
    """

    LoRaWAN: Optional[LoRaWANConnectionStatusResourceTypeEventConfiguration]


Crc = int


class CreateDestinationRequest(ServiceRequest):
    Name: DestinationName
    ExpressionType: ExpressionType
    Expression: Expression
    Description: Optional[Description]
    RoleArn: RoleArn
    Tags: Optional[TagList]
    ClientRequestToken: Optional[ClientRequestToken]


class CreateDestinationResponse(TypedDict, total=False):
    Arn: Optional[DestinationArn]
    Name: Optional[DestinationName]


FactoryPresetFreqsList = List[PresetFreq]


class LoRaWANDeviceProfile(TypedDict, total=False):
    """LoRaWANDeviceProfile object."""

    SupportsClassB: Optional[SupportsClassB]
    ClassBTimeout: Optional[ClassBTimeout]
    PingSlotPeriod: Optional[PingSlotPeriod]
    PingSlotDr: Optional[PingSlotDr]
    PingSlotFreq: Optional[PingSlotFreq]
    SupportsClassC: Optional[SupportsClassC]
    ClassCTimeout: Optional[ClassCTimeout]
    MacVersion: Optional[MacVersion]
    RegParamsRevision: Optional[RegParamsRevision]
    RxDelay1: Optional[RxDelay1]
    RxDrOffset1: Optional[RxDrOffset1]
    RxDataRate2: Optional[RxDataRate2]
    RxFreq2: Optional[RxFreq2]
    FactoryPresetFreqsList: Optional[FactoryPresetFreqsList]
    MaxEirp: Optional[MaxEirp]
    MaxDutyCycle: Optional[MaxDutyCycle]
    RfRegion: Optional[RfRegion]
    SupportsJoin: Optional[SupportsJoin]
    Supports32BitFCnt: Optional[Supports32BitFCnt]


class CreateDeviceProfileRequest(ServiceRequest):
    Name: Optional[DeviceProfileName]
    LoRaWAN: Optional[LoRaWANDeviceProfile]
    Tags: Optional[TagList]
    ClientRequestToken: Optional[ClientRequestToken]


class CreateDeviceProfileResponse(TypedDict, total=False):
    Arn: Optional[DeviceProfileArn]
    Id: Optional[DeviceProfileId]


class LoRaWANFuotaTask(TypedDict, total=False):
    """The LoRaWAN information used with a FUOTA task."""

    RfRegion: Optional[SupportedRfRegion]


class CreateFuotaTaskRequest(ServiceRequest):
    Name: Optional[FuotaTaskName]
    Description: Optional[Description]
    ClientRequestToken: Optional[ClientRequestToken]
    LoRaWAN: Optional[LoRaWANFuotaTask]
    FirmwareUpdateImage: FirmwareUpdateImage
    FirmwareUpdateRole: FirmwareUpdateRole
    Tags: Optional[TagList]


class CreateFuotaTaskResponse(TypedDict, total=False):
    Arn: Optional[FuotaTaskArn]
    Id: Optional[FuotaTaskId]


class LoRaWANMulticast(TypedDict, total=False):
    """The LoRaWAN information that is to be used with the multicast group."""

    RfRegion: Optional[SupportedRfRegion]
    DlClass: Optional[DlClass]


class CreateMulticastGroupRequest(ServiceRequest):
    Name: Optional[MulticastGroupName]
    Description: Optional[Description]
    ClientRequestToken: Optional[ClientRequestToken]
    LoRaWAN: LoRaWANMulticast
    Tags: Optional[TagList]


class CreateMulticastGroupResponse(TypedDict, total=False):
    Arn: Optional[MulticastGroupArn]
    Id: Optional[MulticastGroupId]


WirelessGatewayList = List[WirelessGatewayId]
WirelessDeviceList = List[WirelessDeviceId]


class TraceContent(TypedDict, total=False):
    """Trace content for your wireless gateway and wireless device resources."""

    WirelessDeviceFrameInfo: Optional[WirelessDeviceFrameInfo]
    LogLevel: Optional[LogLevel]


class CreateNetworkAnalyzerConfigurationRequest(ServiceRequest):
    Name: NetworkAnalyzerConfigurationName
    TraceContent: Optional[TraceContent]
    WirelessDevices: Optional[WirelessDeviceList]
    WirelessGateways: Optional[WirelessGatewayList]
    Description: Optional[Description]
    Tags: Optional[TagList]
    ClientRequestToken: Optional[ClientRequestToken]


class CreateNetworkAnalyzerConfigurationResponse(TypedDict, total=False):
    Arn: Optional[NetworkAnalyzerConfigurationArn]
    Name: Optional[NetworkAnalyzerConfigurationName]


class LoRaWANServiceProfile(TypedDict, total=False):
    """LoRaWANServiceProfile object."""

    AddGwMetadata: Optional[AddGwMetadata]


class CreateServiceProfileRequest(ServiceRequest):
    Name: Optional[ServiceProfileName]
    LoRaWAN: Optional[LoRaWANServiceProfile]
    Tags: Optional[TagList]
    ClientRequestToken: Optional[ClientRequestToken]


class CreateServiceProfileResponse(TypedDict, total=False):
    Arn: Optional[ServiceProfileArn]
    Id: Optional[ServiceProfileId]


class FPorts(TypedDict, total=False):
    """List of FPort assigned for different LoRaWAN application packages to use"""

    Fuota: Optional[FPort]
    Multicast: Optional[FPort]
    ClockSync: Optional[FPort]


class OtaaV1_0_x(TypedDict, total=False):
    """OTAA device object for v1.0.x"""

    AppKey: Optional[AppKey]
    AppEui: Optional[AppEui]
    GenAppKey: Optional[GenAppKey]


class OtaaV1_1(TypedDict, total=False):
    """OTAA device object for v1.1"""

    AppKey: Optional[AppKey]
    NwkKey: Optional[NwkKey]
    JoinEui: Optional[JoinEui]


class LoRaWANDevice(TypedDict, total=False):
    """LoRaWAN object for create functions."""

    DevEui: Optional[DevEui]
    DeviceProfileId: Optional[DeviceProfileId]
    ServiceProfileId: Optional[ServiceProfileId]
    OtaaV1_1: Optional[OtaaV1_1]
    OtaaV1_0_x: Optional[OtaaV1_0_x]
    AbpV1_1: Optional[AbpV1_1]
    AbpV1_0_x: Optional[AbpV1_0_x]
    FPorts: Optional[FPorts]


class CreateWirelessDeviceRequest(ServiceRequest):
    Type: WirelessDeviceType
    Name: Optional[WirelessDeviceName]
    Description: Optional[Description]
    DestinationName: DestinationName
    ClientRequestToken: Optional[ClientRequestToken]
    LoRaWAN: Optional[LoRaWANDevice]
    Tags: Optional[TagList]


class CreateWirelessDeviceResponse(TypedDict, total=False):
    Arn: Optional[WirelessDeviceArn]
    Id: Optional[WirelessDeviceId]


SubBands = List[SubBand]
NetIdFilters = List[NetId]
JoinEuiRange = List[JoinEui]
JoinEuiFilters = List[JoinEuiRange]


class LoRaWANGateway(TypedDict, total=False):
    """LoRaWANGateway object."""

    GatewayEui: Optional[GatewayEui]
    RfRegion: Optional[RfRegion]
    JoinEuiFilters: Optional[JoinEuiFilters]
    NetIdFilters: Optional[NetIdFilters]
    SubBands: Optional[SubBands]


class CreateWirelessGatewayRequest(ServiceRequest):
    Name: Optional[WirelessGatewayName]
    Description: Optional[Description]
    LoRaWAN: LoRaWANGateway
    Tags: Optional[TagList]
    ClientRequestToken: Optional[ClientRequestToken]


class CreateWirelessGatewayResponse(TypedDict, total=False):
    Arn: Optional[WirelessGatewayArn]
    Id: Optional[WirelessDeviceId]


class LoRaWANGatewayVersion(TypedDict, total=False):
    """LoRaWANGatewayVersion object."""

    PackageVersion: Optional[PackageVersion]
    Model: Optional[Model]
    Station: Optional[Station]


class LoRaWANUpdateGatewayTaskCreate(TypedDict, total=False):
    """LoRaWANUpdateGatewayTaskCreate object."""

    UpdateSignature: Optional[UpdateSignature]
    SigKeyCrc: Optional[Crc]
    CurrentVersion: Optional[LoRaWANGatewayVersion]
    UpdateVersion: Optional[LoRaWANGatewayVersion]


class UpdateWirelessGatewayTaskCreate(TypedDict, total=False):
    """UpdateWirelessGatewayTaskCreate object."""

    UpdateDataSource: Optional[UpdateDataSource]
    UpdateDataRole: Optional[UpdateDataSource]
    LoRaWAN: Optional[LoRaWANUpdateGatewayTaskCreate]


class CreateWirelessGatewayTaskDefinitionRequest(ServiceRequest):
    AutoCreateTasks: AutoCreateTasks
    Name: Optional[WirelessGatewayTaskName]
    Update: Optional[UpdateWirelessGatewayTaskCreate]
    ClientRequestToken: Optional[ClientRequestToken]
    Tags: Optional[TagList]


class CreateWirelessGatewayTaskDefinitionResponse(TypedDict, total=False):
    Id: Optional[WirelessGatewayTaskDefinitionId]
    Arn: Optional[WirelessGatewayTaskDefinitionArn]


class CreateWirelessGatewayTaskRequest(ServiceRequest):
    Id: WirelessGatewayId
    WirelessGatewayTaskDefinitionId: WirelessGatewayTaskDefinitionId


class CreateWirelessGatewayTaskResponse(TypedDict, total=False):
    WirelessGatewayTaskDefinitionId: Optional[WirelessGatewayTaskDefinitionId]
    Status: Optional[WirelessGatewayTaskStatus]


CreatedAt = datetime


class DeleteDestinationRequest(ServiceRequest):
    Name: DestinationName


class DeleteDestinationResponse(TypedDict, total=False):
    pass


class DeleteDeviceProfileRequest(ServiceRequest):
    Id: DeviceProfileId


class DeleteDeviceProfileResponse(TypedDict, total=False):
    pass


class DeleteFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId


class DeleteFuotaTaskResponse(TypedDict, total=False):
    pass


class DeleteMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId


class DeleteMulticastGroupResponse(TypedDict, total=False):
    pass


class DeleteNetworkAnalyzerConfigurationRequest(ServiceRequest):
    ConfigurationName: NetworkAnalyzerConfigurationName


class DeleteNetworkAnalyzerConfigurationResponse(TypedDict, total=False):
    pass


class DeleteQueuedMessagesRequest(ServiceRequest):
    Id: WirelessDeviceId
    MessageId: MessageId
    WirelessDeviceType: Optional[WirelessDeviceType]


class DeleteQueuedMessagesResponse(TypedDict, total=False):
    pass


class DeleteServiceProfileRequest(ServiceRequest):
    Id: ServiceProfileId


class DeleteServiceProfileResponse(TypedDict, total=False):
    pass


class DeleteWirelessDeviceRequest(ServiceRequest):
    Id: WirelessDeviceId


class DeleteWirelessDeviceResponse(TypedDict, total=False):
    pass


class DeleteWirelessGatewayRequest(ServiceRequest):
    Id: WirelessGatewayId


class DeleteWirelessGatewayResponse(TypedDict, total=False):
    pass


class DeleteWirelessGatewayTaskDefinitionRequest(ServiceRequest):
    Id: WirelessGatewayTaskDefinitionId


class DeleteWirelessGatewayTaskDefinitionResponse(TypedDict, total=False):
    pass


class DeleteWirelessGatewayTaskRequest(ServiceRequest):
    Id: WirelessGatewayId


class DeleteWirelessGatewayTaskResponse(TypedDict, total=False):
    pass


class Destinations(TypedDict, total=False):
    """Describes a destination."""

    Arn: Optional[DestinationArn]
    Name: Optional[DestinationName]
    ExpressionType: Optional[ExpressionType]
    Expression: Optional[Expression]
    Description: Optional[Description]
    RoleArn: Optional[RoleArn]


DestinationList = List[Destinations]
DeviceCertificateList = List[CertificateList]


class DeviceProfile(TypedDict, total=False):
    """Describes a device profile."""

    Arn: Optional[DeviceProfileArn]
    Name: Optional[DeviceProfileName]
    Id: Optional[DeviceProfileId]


DeviceProfileList = List[DeviceProfile]


class SidewalkEventNotificationConfigurations(TypedDict, total=False):
    """SidewalkEventNotificationConfigurations object Event configuration
    object for Sidewalk related event topics.
    """

    AmazonIdEventTopic: Optional[EventNotificationTopicStatus]


class DeviceRegistrationStateEventConfiguration(TypedDict, total=False):
    """Device registration state event configuration object for enabling and
    disabling relevant topics.
    """

    Sidewalk: Optional[SidewalkEventNotificationConfigurations]
    WirelessDeviceIdEventTopic: Optional[EventNotificationTopicStatus]


class SidewalkResourceTypeEventConfiguration(TypedDict, total=False):
    """Sidewalk resource type event configuration object for enabling or
    disabling topic.
    """

    WirelessDeviceEventTopic: Optional[EventNotificationTopicStatus]


class DeviceRegistrationStateResourceTypeEventConfiguration(TypedDict, total=False):
    """Device registration state resource type event configuration object for
    enabling or disabling topic.
    """

    Sidewalk: Optional[SidewalkResourceTypeEventConfiguration]


class DisassociateAwsAccountFromPartnerAccountRequest(ServiceRequest):
    PartnerAccountId: PartnerAccountId
    PartnerType: PartnerType


class DisassociateAwsAccountFromPartnerAccountResponse(TypedDict, total=False):
    pass


class DisassociateMulticastGroupFromFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    MulticastGroupId: MulticastGroupId


class DisassociateMulticastGroupFromFuotaTaskResponse(TypedDict, total=False):
    pass


class DisassociateWirelessDeviceFromFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    WirelessDeviceId: WirelessDeviceId


class DisassociateWirelessDeviceFromFuotaTaskResponse(TypedDict, total=False):
    pass


class DisassociateWirelessDeviceFromMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId
    WirelessDeviceId: WirelessDeviceId


class DisassociateWirelessDeviceFromMulticastGroupResponse(TypedDict, total=False):
    pass


class DisassociateWirelessDeviceFromThingRequest(ServiceRequest):
    Id: WirelessDeviceId


class DisassociateWirelessDeviceFromThingResponse(TypedDict, total=False):
    pass


class DisassociateWirelessGatewayFromCertificateRequest(ServiceRequest):
    Id: WirelessGatewayId


class DisassociateWirelessGatewayFromCertificateResponse(TypedDict, total=False):
    pass


class DisassociateWirelessGatewayFromThingRequest(ServiceRequest):
    Id: WirelessGatewayId


class DisassociateWirelessGatewayFromThingResponse(TypedDict, total=False):
    pass


class LoRaWANSendDataToDevice(TypedDict, total=False):
    """LoRaWAN router info."""

    FPort: Optional[FPort]


class DownlinkQueueMessage(TypedDict, total=False):
    """The message in the downlink queue."""

    MessageId: Optional[MessageId]
    TransmitMode: Optional[TransmitMode]
    ReceivedAt: Optional[ISODateTimeString]
    LoRaWAN: Optional[LoRaWANSendDataToDevice]


DownlinkQueueMessagesList = List[DownlinkQueueMessage]


class LoRaWANJoinEventNotificationConfigurations(TypedDict, total=False):
    """Object for LoRaWAN join resource type event configuration."""

    DevEuiEventTopic: Optional[EventNotificationTopicStatus]


class JoinEventConfiguration(TypedDict, total=False):
    """Join event configuration object for enabling or disabling topic."""

    LoRaWAN: Optional[LoRaWANJoinEventNotificationConfigurations]
    WirelessDeviceIdEventTopic: Optional[EventNotificationTopicStatus]


class ProximityEventConfiguration(TypedDict, total=False):
    """Proximity event configuration object for enabling and disabling relevant
    topics.
    """

    Sidewalk: Optional[SidewalkEventNotificationConfigurations]
    WirelessDeviceIdEventTopic: Optional[EventNotificationTopicStatus]


class EventNotificationItemConfigurations(TypedDict, total=False):
    """Object of all event configurations and the status of the event topics."""

    DeviceRegistrationState: Optional[DeviceRegistrationStateEventConfiguration]
    Proximity: Optional[ProximityEventConfiguration]
    Join: Optional[JoinEventConfiguration]
    ConnectionStatus: Optional[ConnectionStatusEventConfiguration]


class EventConfigurationItem(TypedDict, total=False):
    """Event configuration object for a single resource."""

    Identifier: Optional[Identifier]
    IdentifierType: Optional[IdentifierType]
    PartnerType: Optional[EventNotificationPartnerType]
    Events: Optional[EventNotificationItemConfigurations]


EventConfigurationsList = List[EventConfigurationItem]


class FuotaTask(TypedDict, total=False):
    """A FUOTA task."""

    Id: Optional[FuotaTaskId]
    Arn: Optional[FuotaTaskArn]
    Name: Optional[FuotaTaskName]


FuotaTaskList = List[FuotaTask]


class GetDestinationRequest(ServiceRequest):
    Name: DestinationName


class GetDestinationResponse(TypedDict, total=False):
    Arn: Optional[DestinationArn]
    Name: Optional[DestinationName]
    Expression: Optional[Expression]
    ExpressionType: Optional[ExpressionType]
    Description: Optional[Description]
    RoleArn: Optional[RoleArn]


class GetDeviceProfileRequest(ServiceRequest):
    Id: DeviceProfileId


class GetDeviceProfileResponse(TypedDict, total=False):
    Arn: Optional[DeviceProfileArn]
    Name: Optional[DeviceProfileName]
    Id: Optional[DeviceProfileId]
    LoRaWAN: Optional[LoRaWANDeviceProfile]


class GetEventConfigurationByResourceTypesRequest(ServiceRequest):
    pass


class LoRaWANJoinResourceTypeEventConfiguration(TypedDict, total=False):
    """Object for LoRaWAN join resource type event configuration."""

    WirelessDeviceEventTopic: Optional[EventNotificationTopicStatus]


class JoinResourceTypeEventConfiguration(TypedDict, total=False):
    """Join resource type event configuration object for enabling or disabling
    topic.
    """

    LoRaWAN: Optional[LoRaWANJoinResourceTypeEventConfiguration]


class ProximityResourceTypeEventConfiguration(TypedDict, total=False):
    """Proximity resource type event configuration object for enabling or
    disabling topic.
    """

    Sidewalk: Optional[SidewalkResourceTypeEventConfiguration]


class GetEventConfigurationByResourceTypesResponse(TypedDict, total=False):
    DeviceRegistrationState: Optional[DeviceRegistrationStateResourceTypeEventConfiguration]
    Proximity: Optional[ProximityResourceTypeEventConfiguration]
    Join: Optional[JoinResourceTypeEventConfiguration]
    ConnectionStatus: Optional[ConnectionStatusResourceTypeEventConfiguration]


class GetFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId


StartTime = datetime


class LoRaWANFuotaTaskGetInfo(TypedDict, total=False):
    """The LoRaWAN information returned from getting a FUOTA task."""

    RfRegion: Optional[RfRegion]
    StartTime: Optional[StartTime]


class GetFuotaTaskResponse(TypedDict, total=False):
    Arn: Optional[FuotaTaskArn]
    Id: Optional[FuotaTaskId]
    Status: Optional[FuotaTaskStatus]
    Name: Optional[FuotaTaskName]
    Description: Optional[Description]
    LoRaWAN: Optional[LoRaWANFuotaTaskGetInfo]
    FirmwareUpdateImage: Optional[FirmwareUpdateImage]
    FirmwareUpdateRole: Optional[FirmwareUpdateRole]
    CreatedAt: Optional[CreatedAt]


class GetLogLevelsByResourceTypesRequest(ServiceRequest):
    pass


class WirelessDeviceEventLogOption(TypedDict, total=False):
    """The log options for a wireless device event and can be used to set log
    levels for a specific wireless device event.

    For a LoRaWAN device, possible events for a log messsage are: ``Join``,
    ``Rejoin``, ``Downlink_Data``, and ``Uplink_Data``. For a Sidewalk
    device, possible events for a log message are ``Registration``,
    ``Downlink_Data``, and ``Uplink_Data``.
    """

    Event: WirelessDeviceEvent
    LogLevel: LogLevel


WirelessDeviceEventLogOptionList = List[WirelessDeviceEventLogOption]


class WirelessDeviceLogOption(TypedDict, total=False):
    """The log options for wireless devices and can be used to set log levels
    for a specific type of wireless device.
    """

    Type: WirelessDeviceType
    LogLevel: LogLevel
    Events: Optional[WirelessDeviceEventLogOptionList]


WirelessDeviceLogOptionList = List[WirelessDeviceLogOption]


class WirelessGatewayEventLogOption(TypedDict, total=False):
    """The log options for a wireless gateway event and can be used to set log
    levels for a specific wireless gateway event.

    For a LoRaWAN gateway, possible events for a log message are
    ``CUPS_Request`` and ``Certificate``.
    """

    Event: WirelessGatewayEvent
    LogLevel: LogLevel


WirelessGatewayEventLogOptionList = List[WirelessGatewayEventLogOption]


class WirelessGatewayLogOption(TypedDict, total=False):
    """The log options for wireless gateways and can be used to set log levels
    for a specific type of wireless gateway.
    """

    Type: WirelessGatewayType
    LogLevel: LogLevel
    Events: Optional[WirelessGatewayEventLogOptionList]


WirelessGatewayLogOptionList = List[WirelessGatewayLogOption]


class GetLogLevelsByResourceTypesResponse(TypedDict, total=False):
    DefaultLogLevel: Optional[LogLevel]
    WirelessGatewayLogOptions: Optional[WirelessGatewayLogOptionList]
    WirelessDeviceLogOptions: Optional[WirelessDeviceLogOptionList]


class GetMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId


class LoRaWANMulticastGet(TypedDict, total=False):
    """The LoRaWAN information that is to be returned from getting multicast
    group information.
    """

    RfRegion: Optional[SupportedRfRegion]
    DlClass: Optional[DlClass]
    NumberOfDevicesRequested: Optional[NumberOfDevicesRequested]
    NumberOfDevicesInGroup: Optional[NumberOfDevicesInGroup]


class GetMulticastGroupResponse(TypedDict, total=False):
    Arn: Optional[MulticastGroupArn]
    Id: Optional[MulticastGroupId]
    Name: Optional[MulticastGroupName]
    Description: Optional[Description]
    Status: Optional[MulticastGroupStatus]
    LoRaWAN: Optional[LoRaWANMulticastGet]
    CreatedAt: Optional[CreatedAt]


class GetMulticastGroupSessionRequest(ServiceRequest):
    Id: MulticastGroupId


SessionStartTimeTimestamp = datetime


class LoRaWANMulticastSession(TypedDict, total=False):
    """The LoRaWAN information used with the multicast session."""

    DlDr: Optional[DlDr]
    DlFreq: Optional[DlFreq]
    SessionStartTime: Optional[SessionStartTimeTimestamp]
    SessionTimeout: Optional[SessionTimeout]


class GetMulticastGroupSessionResponse(TypedDict, total=False):
    LoRaWAN: Optional[LoRaWANMulticastSession]


class GetNetworkAnalyzerConfigurationRequest(ServiceRequest):
    ConfigurationName: NetworkAnalyzerConfigurationName


class GetNetworkAnalyzerConfigurationResponse(TypedDict, total=False):
    TraceContent: Optional[TraceContent]
    WirelessDevices: Optional[WirelessDeviceList]
    WirelessGateways: Optional[WirelessGatewayList]
    Description: Optional[Description]
    Arn: Optional[NetworkAnalyzerConfigurationArn]
    Name: Optional[NetworkAnalyzerConfigurationName]


class GetPartnerAccountRequest(ServiceRequest):
    PartnerAccountId: PartnerAccountId
    PartnerType: PartnerType


class SidewalkAccountInfoWithFingerprint(TypedDict, total=False):
    """Information about a Sidewalk account."""

    AmazonId: Optional[AmazonId]
    Fingerprint: Optional[Fingerprint]
    Arn: Optional[PartnerAccountArn]


class GetPartnerAccountResponse(TypedDict, total=False):
    Sidewalk: Optional[SidewalkAccountInfoWithFingerprint]
    AccountLinked: Optional[AccountLinked]


class GetResourceEventConfigurationRequest(ServiceRequest):
    Identifier: Identifier
    IdentifierType: IdentifierType
    PartnerType: Optional[EventNotificationPartnerType]


class GetResourceEventConfigurationResponse(TypedDict, total=False):
    DeviceRegistrationState: Optional[DeviceRegistrationStateEventConfiguration]
    Proximity: Optional[ProximityEventConfiguration]
    Join: Optional[JoinEventConfiguration]
    ConnectionStatus: Optional[ConnectionStatusEventConfiguration]


class GetResourceLogLevelRequest(ServiceRequest):
    ResourceIdentifier: ResourceIdentifier
    ResourceType: ResourceType


class GetResourceLogLevelResponse(TypedDict, total=False):
    LogLevel: Optional[LogLevel]


class GetServiceEndpointRequest(ServiceRequest):
    ServiceType: Optional[WirelessGatewayServiceType]


class GetServiceEndpointResponse(TypedDict, total=False):
    ServiceType: Optional[WirelessGatewayServiceType]
    ServiceEndpoint: Optional[EndPoint]
    ServerTrust: Optional[CertificatePEM]


class GetServiceProfileRequest(ServiceRequest):
    Id: ServiceProfileId


class LoRaWANGetServiceProfileInfo(TypedDict, total=False):
    """LoRaWANGetServiceProfileInfo object."""

    UlRate: Optional[UlRate]
    UlBucketSize: Optional[UlBucketSize]
    UlRatePolicy: Optional[UlRatePolicy]
    DlRate: Optional[DlRate]
    DlBucketSize: Optional[DlBucketSize]
    DlRatePolicy: Optional[DlRatePolicy]
    AddGwMetadata: Optional[AddGwMetadata]
    DevStatusReqFreq: Optional[DevStatusReqFreq]
    ReportDevStatusBattery: Optional[ReportDevStatusBattery]
    ReportDevStatusMargin: Optional[ReportDevStatusMargin]
    DrMin: Optional[DrMin]
    DrMax: Optional[DrMax]
    ChannelMask: Optional[ChannelMask]
    PrAllowed: Optional[PrAllowed]
    HrAllowed: Optional[HrAllowed]
    RaAllowed: Optional[RaAllowed]
    NwkGeoLoc: Optional[NwkGeoLoc]
    TargetPer: Optional[TargetPer]
    MinGwDiversity: Optional[MinGwDiversity]


class GetServiceProfileResponse(TypedDict, total=False):
    Arn: Optional[ServiceProfileArn]
    Name: Optional[ServiceProfileName]
    Id: Optional[ServiceProfileId]
    LoRaWAN: Optional[LoRaWANGetServiceProfileInfo]


class GetWirelessDeviceRequest(ServiceRequest):
    Identifier: Identifier
    IdentifierType: WirelessDeviceIdType


class SidewalkDevice(TypedDict, total=False):
    """Sidewalk device object."""

    AmazonId: Optional[AmazonId]
    SidewalkId: Optional[SidewalkId]
    SidewalkManufacturingSn: Optional[SidewalkManufacturingSn]
    DeviceCertificates: Optional[DeviceCertificateList]


class GetWirelessDeviceResponse(TypedDict, total=False):
    Type: Optional[WirelessDeviceType]
    Name: Optional[WirelessDeviceName]
    Description: Optional[Description]
    DestinationName: Optional[DestinationName]
    Id: Optional[WirelessDeviceId]
    Arn: Optional[WirelessDeviceArn]
    ThingName: Optional[ThingName]
    ThingArn: Optional[ThingArn]
    LoRaWAN: Optional[LoRaWANDevice]
    Sidewalk: Optional[SidewalkDevice]


class GetWirelessDeviceStatisticsRequest(ServiceRequest):
    WirelessDeviceId: WirelessDeviceId


class SidewalkDeviceMetadata(TypedDict, total=False):
    """MetaData for Sidewalk device."""

    Rssi: Optional[Integer]
    BatteryLevel: Optional[BatteryLevel]
    Event: Optional[Event]
    DeviceState: Optional[DeviceState]


class LoRaWANGatewayMetadata(TypedDict, total=False):
    """LoRaWAN gateway metatdata."""

    GatewayEui: Optional[GatewayEui]
    Snr: Optional[Double]
    Rssi: Optional[Double]


LoRaWANGatewayMetadataList = List[LoRaWANGatewayMetadata]


class LoRaWANDeviceMetadata(TypedDict, total=False):
    """LoRaWAN device metatdata."""

    DevEui: Optional[DevEui]
    FPort: Optional[Integer]
    DataRate: Optional[Integer]
    Frequency: Optional[Integer]
    Timestamp: Optional[ISODateTimeString]
    Gateways: Optional[LoRaWANGatewayMetadataList]


class GetWirelessDeviceStatisticsResponse(TypedDict, total=False):
    WirelessDeviceId: Optional[WirelessDeviceId]
    LastUplinkReceivedAt: Optional[ISODateTimeString]
    LoRaWAN: Optional[LoRaWANDeviceMetadata]
    Sidewalk: Optional[SidewalkDeviceMetadata]


class GetWirelessGatewayCertificateRequest(ServiceRequest):
    Id: WirelessGatewayId


class GetWirelessGatewayCertificateResponse(TypedDict, total=False):
    IotCertificateId: Optional[IotCertificateId]
    LoRaWANNetworkServerCertificateId: Optional[IotCertificateId]


class GetWirelessGatewayFirmwareInformationRequest(ServiceRequest):
    Id: WirelessGatewayId


class LoRaWANGatewayCurrentVersion(TypedDict, total=False):
    """LoRaWANGatewayCurrentVersion object."""

    CurrentVersion: Optional[LoRaWANGatewayVersion]


class GetWirelessGatewayFirmwareInformationResponse(TypedDict, total=False):
    LoRaWAN: Optional[LoRaWANGatewayCurrentVersion]


class GetWirelessGatewayRequest(ServiceRequest):
    Identifier: Identifier
    IdentifierType: WirelessGatewayIdType


class GetWirelessGatewayResponse(TypedDict, total=False):
    Name: Optional[WirelessGatewayName]
    Id: Optional[WirelessGatewayId]
    Description: Optional[Description]
    LoRaWAN: Optional[LoRaWANGateway]
    Arn: Optional[WirelessGatewayArn]
    ThingName: Optional[ThingName]
    ThingArn: Optional[ThingArn]


class GetWirelessGatewayStatisticsRequest(ServiceRequest):
    WirelessGatewayId: WirelessGatewayId


class GetWirelessGatewayStatisticsResponse(TypedDict, total=False):
    WirelessGatewayId: Optional[WirelessGatewayId]
    LastUplinkReceivedAt: Optional[ISODateTimeString]
    ConnectionStatus: Optional[ConnectionStatus]


class GetWirelessGatewayTaskDefinitionRequest(ServiceRequest):
    Id: WirelessGatewayTaskDefinitionId


class GetWirelessGatewayTaskDefinitionResponse(TypedDict, total=False):
    AutoCreateTasks: Optional[AutoCreateTasks]
    Name: Optional[WirelessGatewayTaskName]
    Update: Optional[UpdateWirelessGatewayTaskCreate]
    Arn: Optional[WirelessGatewayTaskDefinitionArn]


class GetWirelessGatewayTaskRequest(ServiceRequest):
    Id: WirelessGatewayId


class GetWirelessGatewayTaskResponse(TypedDict, total=False):
    WirelessGatewayId: Optional[WirelessGatewayId]
    WirelessGatewayTaskDefinitionId: Optional[WirelessGatewayTaskDefinitionId]
    LastUplinkReceivedAt: Optional[ISODateTimeString]
    TaskCreatedAt: Optional[ISODateTimeString]
    Status: Optional[WirelessGatewayTaskStatus]


class ListDestinationsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListDestinationsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    DestinationList: Optional[DestinationList]


class ListDeviceProfilesRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListDeviceProfilesResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    DeviceProfileList: Optional[DeviceProfileList]


class ListEventConfigurationsRequest(ServiceRequest):
    ResourceType: EventNotificationResourceType
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListEventConfigurationsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    EventConfigurationsList: Optional[EventConfigurationsList]


class ListFuotaTasksRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListFuotaTasksResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    FuotaTaskList: Optional[FuotaTaskList]


class ListMulticastGroupsByFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class MulticastGroupByFuotaTask(TypedDict, total=False):
    """A multicast group that is associated with a FUOTA task."""

    Id: Optional[MulticastGroupId]


MulticastGroupListByFuotaTask = List[MulticastGroupByFuotaTask]


class ListMulticastGroupsByFuotaTaskResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    MulticastGroupList: Optional[MulticastGroupListByFuotaTask]


class ListMulticastGroupsRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class MulticastGroup(TypedDict, total=False):
    """A multicast group."""

    Id: Optional[MulticastGroupId]
    Arn: Optional[MulticastGroupArn]
    Name: Optional[MulticastGroupName]


MulticastGroupList = List[MulticastGroup]


class ListMulticastGroupsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    MulticastGroupList: Optional[MulticastGroupList]


class ListNetworkAnalyzerConfigurationsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class NetworkAnalyzerConfigurations(TypedDict, total=False):
    """Network analyzer configurations."""

    Arn: Optional[NetworkAnalyzerConfigurationArn]
    Name: Optional[NetworkAnalyzerConfigurationName]


NetworkAnalyzerConfigurationList = List[NetworkAnalyzerConfigurations]


class ListNetworkAnalyzerConfigurationsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    NetworkAnalyzerConfigurationList: Optional[NetworkAnalyzerConfigurationList]


class ListPartnerAccountsRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


SidewalkAccountList = List[SidewalkAccountInfoWithFingerprint]


class ListPartnerAccountsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    Sidewalk: Optional[SidewalkAccountList]


class ListQueuedMessagesRequest(ServiceRequest):
    Id: WirelessDeviceId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]
    WirelessDeviceType: Optional[WirelessDeviceType]


class ListQueuedMessagesResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    DownlinkQueueMessagesList: Optional[DownlinkQueueMessagesList]


class ListServiceProfilesRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ServiceProfile(TypedDict, total=False):
    """Information about a service profile."""

    Arn: Optional[ServiceProfileArn]
    Name: Optional[ServiceProfileName]
    Id: Optional[ServiceProfileId]


ServiceProfileList = List[ServiceProfile]


class ListServiceProfilesResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    ServiceProfileList: Optional[ServiceProfileList]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceArn: AmazonResourceName


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[TagList]


class ListWirelessDevicesRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]
    DestinationName: Optional[DestinationName]
    DeviceProfileId: Optional[DeviceProfileId]
    ServiceProfileId: Optional[ServiceProfileId]
    WirelessDeviceType: Optional[WirelessDeviceType]
    FuotaTaskId: Optional[FuotaTaskId]
    MulticastGroupId: Optional[MulticastGroupId]


class SidewalkListDevice(TypedDict, total=False):
    """Sidewalk object used by list functions."""

    AmazonId: Optional[AmazonId]
    SidewalkId: Optional[SidewalkId]
    SidewalkManufacturingSn: Optional[SidewalkManufacturingSn]
    DeviceCertificates: Optional[DeviceCertificateList]


class LoRaWANListDevice(TypedDict, total=False):
    """LoRaWAN object for list functions."""

    DevEui: Optional[DevEui]


class WirelessDeviceStatistics(TypedDict, total=False):
    """Information about a wireless device's operation."""

    Arn: Optional[WirelessDeviceArn]
    Id: Optional[WirelessDeviceId]
    Type: Optional[WirelessDeviceType]
    Name: Optional[WirelessDeviceName]
    DestinationName: Optional[DestinationName]
    LastUplinkReceivedAt: Optional[ISODateTimeString]
    LoRaWAN: Optional[LoRaWANListDevice]
    Sidewalk: Optional[SidewalkListDevice]
    FuotaDeviceStatus: Optional[FuotaDeviceStatus]
    MulticastDeviceStatus: Optional[MulticastDeviceStatus]
    McGroupId: Optional[McGroupId]


WirelessDeviceStatisticsList = List[WirelessDeviceStatistics]


class ListWirelessDevicesResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    WirelessDeviceList: Optional[WirelessDeviceStatisticsList]


class ListWirelessGatewayTaskDefinitionsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]
    TaskDefinitionType: Optional[WirelessGatewayTaskDefinitionType]


class LoRaWANUpdateGatewayTaskEntry(TypedDict, total=False):
    """LoRaWANUpdateGatewayTaskEntry object."""

    CurrentVersion: Optional[LoRaWANGatewayVersion]
    UpdateVersion: Optional[LoRaWANGatewayVersion]


class UpdateWirelessGatewayTaskEntry(TypedDict, total=False):
    """UpdateWirelessGatewayTaskEntry object."""

    Id: Optional[WirelessGatewayTaskDefinitionId]
    LoRaWAN: Optional[LoRaWANUpdateGatewayTaskEntry]
    Arn: Optional[WirelessGatewayTaskDefinitionArn]


WirelessGatewayTaskDefinitionList = List[UpdateWirelessGatewayTaskEntry]


class ListWirelessGatewayTaskDefinitionsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    TaskDefinitions: Optional[WirelessGatewayTaskDefinitionList]


class ListWirelessGatewaysRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class WirelessGatewayStatistics(TypedDict, total=False):
    """Information about a wireless gateway's operation."""

    Arn: Optional[WirelessGatewayArn]
    Id: Optional[WirelessGatewayId]
    Name: Optional[WirelessGatewayName]
    Description: Optional[Description]
    LoRaWAN: Optional[LoRaWANGateway]
    LastUplinkReceivedAt: Optional[ISODateTimeString]


WirelessGatewayStatisticsList = List[WirelessGatewayStatistics]


class ListWirelessGatewaysResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    WirelessGatewayList: Optional[WirelessGatewayStatisticsList]


class LoRaWANMulticastMetadata(TypedDict, total=False):
    """The metadata information of the LoRaWAN multicast group."""

    FPort: Optional[FPort]


class LoRaWANStartFuotaTask(TypedDict, total=False):
    """The LoRaWAN information used to start a FUOTA task."""

    StartTime: Optional[StartTime]


class UpdateAbpV1_0_x(TypedDict, total=False):
    """ABP device object for LoRaWAN specification v1.0.x"""

    FCntStart: Optional[FCntStart]


class UpdateAbpV1_1(TypedDict, total=False):
    """ABP device object for LoRaWAN specification v1.1"""

    FCntStart: Optional[FCntStart]


class LoRaWANUpdateDevice(TypedDict, total=False):
    """LoRaWAN object for update functions."""

    DeviceProfileId: Optional[DeviceProfileId]
    ServiceProfileId: Optional[ServiceProfileId]
    AbpV1_1: Optional[UpdateAbpV1_1]
    AbpV1_0_x: Optional[UpdateAbpV1_0_x]


class MulticastWirelessMetadata(TypedDict, total=False):
    """Wireless metadata that is to be sent to multicast group."""

    LoRaWAN: Optional[LoRaWANMulticastMetadata]


class PutResourceLogLevelRequest(ServiceRequest):
    ResourceIdentifier: ResourceIdentifier
    ResourceType: ResourceType
    LogLevel: LogLevel


class PutResourceLogLevelResponse(TypedDict, total=False):
    pass


class ResetAllResourceLogLevelsRequest(ServiceRequest):
    pass


class ResetAllResourceLogLevelsResponse(TypedDict, total=False):
    pass


class ResetResourceLogLevelRequest(ServiceRequest):
    ResourceIdentifier: ResourceIdentifier
    ResourceType: ResourceType


class ResetResourceLogLevelResponse(TypedDict, total=False):
    pass


class SendDataToMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId
    PayloadData: PayloadData
    WirelessMetadata: MulticastWirelessMetadata


class SendDataToMulticastGroupResponse(TypedDict, total=False):
    MessageId: Optional[MulticastGroupMessageId]


class SidewalkSendDataToDevice(TypedDict, total=False):
    """Information about a Sidewalk router."""

    Seq: Optional[Seq]
    MessageType: Optional[MessageType]


class WirelessMetadata(TypedDict, total=False):
    """WirelessMetadata object."""

    LoRaWAN: Optional[LoRaWANSendDataToDevice]
    Sidewalk: Optional[SidewalkSendDataToDevice]


class SendDataToWirelessDeviceRequest(ServiceRequest):
    Id: WirelessDeviceId
    TransmitMode: TransmitMode
    PayloadData: PayloadData
    WirelessMetadata: Optional[WirelessMetadata]


class SendDataToWirelessDeviceResponse(TypedDict, total=False):
    MessageId: Optional[MessageId]


class SidewalkUpdateAccount(TypedDict, total=False):
    """Sidewalk update."""

    AppServerPrivateKey: Optional[AppServerPrivateKey]


class StartBulkAssociateWirelessDeviceWithMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId
    QueryString: Optional[QueryString]
    Tags: Optional[TagList]


class StartBulkAssociateWirelessDeviceWithMulticastGroupResponse(TypedDict, total=False):
    pass


class StartBulkDisassociateWirelessDeviceFromMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId
    QueryString: Optional[QueryString]
    Tags: Optional[TagList]


class StartBulkDisassociateWirelessDeviceFromMulticastGroupResponse(TypedDict, total=False):
    pass


class StartFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    LoRaWAN: Optional[LoRaWANStartFuotaTask]


class StartFuotaTaskResponse(TypedDict, total=False):
    pass


class StartMulticastGroupSessionRequest(ServiceRequest):
    Id: MulticastGroupId
    LoRaWAN: LoRaWANMulticastSession


class StartMulticastGroupSessionResponse(TypedDict, total=False):
    pass


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceArn: AmazonResourceName
    Tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class TestWirelessDeviceRequest(ServiceRequest):
    Id: WirelessDeviceId


class TestWirelessDeviceResponse(TypedDict, total=False):
    Result: Optional[Result]


class UntagResourceRequest(ServiceRequest):
    ResourceArn: AmazonResourceName
    TagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateDestinationRequest(ServiceRequest):
    Name: DestinationName
    ExpressionType: Optional[ExpressionType]
    Expression: Optional[Expression]
    Description: Optional[Description]
    RoleArn: Optional[RoleArn]


class UpdateDestinationResponse(TypedDict, total=False):
    pass


class UpdateEventConfigurationByResourceTypesRequest(ServiceRequest):
    DeviceRegistrationState: Optional[DeviceRegistrationStateResourceTypeEventConfiguration]
    Proximity: Optional[ProximityResourceTypeEventConfiguration]
    Join: Optional[JoinResourceTypeEventConfiguration]
    ConnectionStatus: Optional[ConnectionStatusResourceTypeEventConfiguration]


class UpdateEventConfigurationByResourceTypesResponse(TypedDict, total=False):
    pass


class UpdateFuotaTaskRequest(ServiceRequest):
    Id: FuotaTaskId
    Name: Optional[FuotaTaskName]
    Description: Optional[Description]
    LoRaWAN: Optional[LoRaWANFuotaTask]
    FirmwareUpdateImage: Optional[FirmwareUpdateImage]
    FirmwareUpdateRole: Optional[FirmwareUpdateRole]


class UpdateFuotaTaskResponse(TypedDict, total=False):
    pass


class UpdateLogLevelsByResourceTypesRequest(ServiceRequest):
    DefaultLogLevel: Optional[LogLevel]
    WirelessDeviceLogOptions: Optional[WirelessDeviceLogOptionList]
    WirelessGatewayLogOptions: Optional[WirelessGatewayLogOptionList]


class UpdateLogLevelsByResourceTypesResponse(TypedDict, total=False):
    pass


class UpdateMulticastGroupRequest(ServiceRequest):
    Id: MulticastGroupId
    Name: Optional[MulticastGroupName]
    Description: Optional[Description]
    LoRaWAN: Optional[LoRaWANMulticast]


class UpdateMulticastGroupResponse(TypedDict, total=False):
    pass


class UpdateNetworkAnalyzerConfigurationRequest(ServiceRequest):
    ConfigurationName: NetworkAnalyzerConfigurationName
    TraceContent: Optional[TraceContent]
    WirelessDevicesToAdd: Optional[WirelessDeviceList]
    WirelessDevicesToRemove: Optional[WirelessDeviceList]
    WirelessGatewaysToAdd: Optional[WirelessGatewayList]
    WirelessGatewaysToRemove: Optional[WirelessGatewayList]
    Description: Optional[Description]


class UpdateNetworkAnalyzerConfigurationResponse(TypedDict, total=False):
    pass


class UpdatePartnerAccountRequest(ServiceRequest):
    Sidewalk: SidewalkUpdateAccount
    PartnerAccountId: PartnerAccountId
    PartnerType: PartnerType


class UpdatePartnerAccountResponse(TypedDict, total=False):
    pass


class UpdateResourceEventConfigurationRequest(ServiceRequest):
    Identifier: Identifier
    IdentifierType: IdentifierType
    PartnerType: Optional[EventNotificationPartnerType]
    DeviceRegistrationState: Optional[DeviceRegistrationStateEventConfiguration]
    Proximity: Optional[ProximityEventConfiguration]
    Join: Optional[JoinEventConfiguration]
    ConnectionStatus: Optional[ConnectionStatusEventConfiguration]


class UpdateResourceEventConfigurationResponse(TypedDict, total=False):
    pass


class UpdateWirelessDeviceRequest(ServiceRequest):
    Id: WirelessDeviceId
    DestinationName: Optional[DestinationName]
    Name: Optional[WirelessDeviceName]
    Description: Optional[Description]
    LoRaWAN: Optional[LoRaWANUpdateDevice]


class UpdateWirelessDeviceResponse(TypedDict, total=False):
    pass


class UpdateWirelessGatewayRequest(ServiceRequest):
    Id: WirelessGatewayId
    Name: Optional[WirelessGatewayName]
    Description: Optional[Description]
    JoinEuiFilters: Optional[JoinEuiFilters]
    NetIdFilters: Optional[NetIdFilters]


class UpdateWirelessGatewayResponse(TypedDict, total=False):
    pass


class IotwirelessApi:

    service = "iotwireless"
    version = "2020-11-22"

    @handler("AssociateAwsAccountWithPartnerAccount")
    def associate_aws_account_with_partner_account(
        self,
        context: RequestContext,
        sidewalk: SidewalkAccountInfo,
        client_request_token: ClientRequestToken = None,
        tags: TagList = None,
    ) -> AssociateAwsAccountWithPartnerAccountResponse:
        """Associates a partner account with your AWS account.

        :param sidewalk: The Sidewalk account credentials.
        :param client_request_token: Each resource must have a unique client request token.
        :param tags: The tags to attach to the specified resource.
        :returns: AssociateAwsAccountWithPartnerAccountResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ConflictException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("AssociateMulticastGroupWithFuotaTask")
    def associate_multicast_group_with_fuota_task(
        self, context: RequestContext, id: FuotaTaskId, multicast_group_id: MulticastGroupId
    ) -> AssociateMulticastGroupWithFuotaTaskResponse:
        """Associate a multicast group with a FUOTA task.

        :param id: The ID of a FUOTA task.
        :param multicast_group_id: The ID of the multicast group.
        :returns: AssociateMulticastGroupWithFuotaTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("AssociateWirelessDeviceWithFuotaTask")
    def associate_wireless_device_with_fuota_task(
        self, context: RequestContext, id: FuotaTaskId, wireless_device_id: WirelessDeviceId
    ) -> AssociateWirelessDeviceWithFuotaTaskResponse:
        """Associate a wireless device with a FUOTA task.

        :param id: The ID of a FUOTA task.
        :param wireless_device_id: The ID of the wireless device.
        :returns: AssociateWirelessDeviceWithFuotaTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("AssociateWirelessDeviceWithMulticastGroup")
    def associate_wireless_device_with_multicast_group(
        self, context: RequestContext, id: MulticastGroupId, wireless_device_id: WirelessDeviceId
    ) -> AssociateWirelessDeviceWithMulticastGroupResponse:
        """Associates a wireless device with a multicast group.

        :param id: The ID of the multicast group.
        :param wireless_device_id: The ID of the wireless device.
        :returns: AssociateWirelessDeviceWithMulticastGroupResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("AssociateWirelessDeviceWithThing")
    def associate_wireless_device_with_thing(
        self, context: RequestContext, id: WirelessDeviceId, thing_arn: ThingArn
    ) -> AssociateWirelessDeviceWithThingResponse:
        """Associates a wireless device with a thing.

        :param id: The ID of the resource to update.
        :param thing_arn: The ARN of the thing to associate with the wireless device.
        :returns: AssociateWirelessDeviceWithThingResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("AssociateWirelessGatewayWithCertificate")
    def associate_wireless_gateway_with_certificate(
        self, context: RequestContext, id: WirelessGatewayId, iot_certificate_id: IotCertificateId
    ) -> AssociateWirelessGatewayWithCertificateResponse:
        """Associates a wireless gateway with a certificate.

        :param id: The ID of the resource to update.
        :param iot_certificate_id: The ID of the certificate to associate with the wireless gateway.
        :returns: AssociateWirelessGatewayWithCertificateResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("AssociateWirelessGatewayWithThing")
    def associate_wireless_gateway_with_thing(
        self, context: RequestContext, id: WirelessGatewayId, thing_arn: ThingArn
    ) -> AssociateWirelessGatewayWithThingResponse:
        """Associates a wireless gateway with a thing.

        :param id: The ID of the resource to update.
        :param thing_arn: The ARN of the thing to associate with the wireless gateway.
        :returns: AssociateWirelessGatewayWithThingResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("CancelMulticastGroupSession")
    def cancel_multicast_group_session(
        self, context: RequestContext, id: MulticastGroupId
    ) -> CancelMulticastGroupSessionResponse:
        """Cancels an existing multicast group session.

        :param id: The ID of the multicast group.
        :returns: CancelMulticastGroupSessionResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateDestination")
    def create_destination(
        self,
        context: RequestContext,
        name: DestinationName,
        expression_type: ExpressionType,
        expression: Expression,
        role_arn: RoleArn,
        description: Description = None,
        tags: TagList = None,
        client_request_token: ClientRequestToken = None,
    ) -> CreateDestinationResponse:
        """Creates a new destination that maps a device message to an AWS IoT rule.

        :param name: The name of the new resource.
        :param expression_type: The type of value in ``Expression``.
        :param expression: The rule name or topic rule to send messages to.
        :param role_arn: The ARN of the IAM Role that authorizes the destination.
        :param description: The description of the new resource.
        :param tags: The tags to attach to the new destination.
        :param client_request_token: Each resource must have a unique client request token.
        :returns: CreateDestinationResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateDeviceProfile")
    def create_device_profile(
        self,
        context: RequestContext,
        name: DeviceProfileName = None,
        lo_ra_wan: LoRaWANDeviceProfile = None,
        tags: TagList = None,
        client_request_token: ClientRequestToken = None,
    ) -> CreateDeviceProfileResponse:
        """Creates a new device profile.

        :param name: The name of the new resource.
        :param lo_ra_wan: The device profile information to use to create the device profile.
        :param tags: The tags to attach to the new device profile.
        :param client_request_token: Each resource must have a unique client request token.
        :returns: CreateDeviceProfileResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateFuotaTask")
    def create_fuota_task(
        self,
        context: RequestContext,
        firmware_update_image: FirmwareUpdateImage,
        firmware_update_role: FirmwareUpdateRole,
        name: FuotaTaskName = None,
        description: Description = None,
        client_request_token: ClientRequestToken = None,
        lo_ra_wan: LoRaWANFuotaTask = None,
        tags: TagList = None,
    ) -> CreateFuotaTaskResponse:
        """Creates a FUOTA task.

        :param firmware_update_image: The S3 URI points to a firmware update image that is to be used with a
        FUOTA task.
        :param firmware_update_role: The firmware update role that is to be used with a FUOTA task.
        :param name: The name of a FUOTA task.
        :param description: The description of the new resource.
        :param client_request_token: Each resource must have a unique client request token.
        :param lo_ra_wan: The LoRaWAN information used with a FUOTA task.
        :param tags: The tag to attach to the specified resource.
        :returns: CreateFuotaTaskResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateMulticastGroup")
    def create_multicast_group(
        self,
        context: RequestContext,
        lo_ra_wan: LoRaWANMulticast,
        name: MulticastGroupName = None,
        description: Description = None,
        client_request_token: ClientRequestToken = None,
        tags: TagList = None,
    ) -> CreateMulticastGroupResponse:
        """Creates a multicast group.

        :param lo_ra_wan: The LoRaWAN information that is to be used with the multicast group.
        :param name: The name of the multicast group.
        :param description: The description of the multicast group.
        :param client_request_token: Each resource must have a unique client request token.
        :param tags: The tag to attach to the specified resource.
        :returns: CreateMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateNetworkAnalyzerConfiguration")
    def create_network_analyzer_configuration(
        self,
        context: RequestContext,
        name: NetworkAnalyzerConfigurationName,
        trace_content: TraceContent = None,
        wireless_devices: WirelessDeviceList = None,
        wireless_gateways: WirelessGatewayList = None,
        description: Description = None,
        tags: TagList = None,
        client_request_token: ClientRequestToken = None,
    ) -> CreateNetworkAnalyzerConfigurationResponse:
        """Creates a new network analyzer configuration.

        :param name: Name of the network analyzer configuration.
        :param trace_content: Trace content for your wireless gateway and wireless device resources.
        :param wireless_devices: Wireless device resources to add to the network analyzer configuration.
        :param wireless_gateways: Wireless gateway resources to add to the network analyzer configuration.
        :param description: The description of the new resource.
        :param tags: The tag to attach to the specified resource.
        :param client_request_token: Each resource must have a unique client request token.
        :returns: CreateNetworkAnalyzerConfigurationResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateServiceProfile")
    def create_service_profile(
        self,
        context: RequestContext,
        name: ServiceProfileName = None,
        lo_ra_wan: LoRaWANServiceProfile = None,
        tags: TagList = None,
        client_request_token: ClientRequestToken = None,
    ) -> CreateServiceProfileResponse:
        """Creates a new service profile.

        :param name: The name of the new resource.
        :param lo_ra_wan: The service profile information to use to create the service profile.
        :param tags: The tags to attach to the new service profile.
        :param client_request_token: Each resource must have a unique client request token.
        :returns: CreateServiceProfileResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateWirelessDevice", expand=False)
    def create_wireless_device(
        self, context: RequestContext, request: CreateWirelessDeviceRequest
    ) -> CreateWirelessDeviceResponse:
        """Provisions a wireless device.

        :param type: The wireless device type.
        :param destination_name: The name of the destination to assign to the new wireless device.
        :param name: The name of the new resource.
        :param description: The description of the new resource.
        :param client_request_token: Each resource must have a unique client request token.
        :param lo_ra_wan: The device configuration information to use to create the wireless
        device.
        :param tags: The tags to attach to the new wireless device.
        :returns: CreateWirelessDeviceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateWirelessGateway")
    def create_wireless_gateway(
        self,
        context: RequestContext,
        lo_ra_wan: LoRaWANGateway,
        name: WirelessGatewayName = None,
        description: Description = None,
        tags: TagList = None,
        client_request_token: ClientRequestToken = None,
    ) -> CreateWirelessGatewayResponse:
        """Provisions a wireless gateway.

        :param lo_ra_wan: The gateway configuration information to use to create the wireless
        gateway.
        :param name: The name of the new resource.
        :param description: The description of the new resource.
        :param tags: The tags to attach to the new wireless gateway.
        :param client_request_token: Each resource must have a unique client request token.
        :returns: CreateWirelessGatewayResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateWirelessGatewayTask")
    def create_wireless_gateway_task(
        self,
        context: RequestContext,
        id: WirelessGatewayId,
        wireless_gateway_task_definition_id: WirelessGatewayTaskDefinitionId,
    ) -> CreateWirelessGatewayTaskResponse:
        """Creates a task for a wireless gateway.

        :param id: The ID of the resource to update.
        :param wireless_gateway_task_definition_id: The ID of the WirelessGatewayTaskDefinition.
        :returns: CreateWirelessGatewayTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateWirelessGatewayTaskDefinition")
    def create_wireless_gateway_task_definition(
        self,
        context: RequestContext,
        auto_create_tasks: AutoCreateTasks,
        name: WirelessGatewayTaskName = None,
        update: UpdateWirelessGatewayTaskCreate = None,
        client_request_token: ClientRequestToken = None,
        tags: TagList = None,
    ) -> CreateWirelessGatewayTaskDefinitionResponse:
        """Creates a gateway task definition.

        :param auto_create_tasks: Whether to automatically create tasks using this task definition for all
        gateways with the specified current version.
        :param name: The name of the new resource.
        :param update: Information about the gateways to update.
        :param client_request_token: Each resource must have a unique client request token.
        :param tags: The tags to attach to the specified resource.
        :returns: CreateWirelessGatewayTaskDefinitionResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteDestination")
    def delete_destination(
        self, context: RequestContext, name: DestinationName
    ) -> DeleteDestinationResponse:
        """Deletes a destination.

        :param name: The name of the resource to delete.
        :returns: DeleteDestinationResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ConflictException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteDeviceProfile")
    def delete_device_profile(
        self, context: RequestContext, id: DeviceProfileId
    ) -> DeleteDeviceProfileResponse:
        """Deletes a device profile.

        :param id: The ID of the resource to delete.
        :returns: DeleteDeviceProfileResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ConflictException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteFuotaTask")
    def delete_fuota_task(
        self, context: RequestContext, id: FuotaTaskId
    ) -> DeleteFuotaTaskResponse:
        """Deletes a FUOTA task.

        :param id: The ID of a FUOTA task.
        :returns: DeleteFuotaTaskResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteMulticastGroup")
    def delete_multicast_group(
        self, context: RequestContext, id: MulticastGroupId
    ) -> DeleteMulticastGroupResponse:
        """Deletes a multicast group if it is not in use by a fuota task.

        :param id: The ID of the multicast group.
        :returns: DeleteMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteNetworkAnalyzerConfiguration")
    def delete_network_analyzer_configuration(
        self, context: RequestContext, configuration_name: NetworkAnalyzerConfigurationName
    ) -> DeleteNetworkAnalyzerConfigurationResponse:
        """Deletes a network analyzer configuration.

        :param configuration_name: Name of the network analyzer configuration.
        :returns: DeleteNetworkAnalyzerConfigurationResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ConflictException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteQueuedMessages")
    def delete_queued_messages(
        self,
        context: RequestContext,
        id: WirelessDeviceId,
        message_id: MessageId,
        wireless_device_type: WirelessDeviceType = None,
    ) -> DeleteQueuedMessagesResponse:
        """Remove queued messages from the downlink queue.

        :param id: The ID of a given wireless device for which downlink messages will be
        deleted.
        :param message_id: If message ID is ``"*"``, it cleares the entire downlink queue for a
        given device, specified by the wireless device ID.
        :param wireless_device_type: The wireless device type, which can be either Sidewalk or LoRaWAN.
        :returns: DeleteQueuedMessagesResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalServerException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("DeleteServiceProfile")
    def delete_service_profile(
        self, context: RequestContext, id: ServiceProfileId
    ) -> DeleteServiceProfileResponse:
        """Deletes a service profile.

        :param id: The ID of the resource to delete.
        :returns: DeleteServiceProfileResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ConflictException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteWirelessDevice")
    def delete_wireless_device(
        self, context: RequestContext, id: WirelessDeviceId
    ) -> DeleteWirelessDeviceResponse:
        """Deletes a wireless device.

        :param id: The ID of the resource to delete.
        :returns: DeleteWirelessDeviceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteWirelessGateway")
    def delete_wireless_gateway(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> DeleteWirelessGatewayResponse:
        """Deletes a wireless gateway.

        :param id: The ID of the resource to delete.
        :returns: DeleteWirelessGatewayResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteWirelessGatewayTask")
    def delete_wireless_gateway_task(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> DeleteWirelessGatewayTaskResponse:
        """Deletes a wireless gateway task.

        :param id: The ID of the resource to delete.
        :returns: DeleteWirelessGatewayTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteWirelessGatewayTaskDefinition")
    def delete_wireless_gateway_task_definition(
        self, context: RequestContext, id: WirelessGatewayTaskDefinitionId
    ) -> DeleteWirelessGatewayTaskDefinitionResponse:
        """Deletes a wireless gateway task definition. Deleting this task
        definition does not affect tasks that are currently in progress.

        :param id: The ID of the resource to delete.
        :returns: DeleteWirelessGatewayTaskDefinitionResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DisassociateAwsAccountFromPartnerAccount")
    def disassociate_aws_account_from_partner_account(
        self,
        context: RequestContext,
        partner_account_id: PartnerAccountId,
        partner_type: PartnerType,
    ) -> DisassociateAwsAccountFromPartnerAccountResponse:
        """Disassociates your AWS account from a partner account. If
        ``PartnerAccountId`` and ``PartnerType`` are ``null``, disassociates
        your AWS account from all partner accounts.

        :param partner_account_id: The partner account ID to disassociate from the AWS account.
        :param partner_type: The partner type.
        :returns: DisassociateAwsAccountFromPartnerAccountResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DisassociateMulticastGroupFromFuotaTask")
    def disassociate_multicast_group_from_fuota_task(
        self, context: RequestContext, id: FuotaTaskId, multicast_group_id: MulticastGroupId
    ) -> DisassociateMulticastGroupFromFuotaTaskResponse:
        """Disassociates a multicast group from a fuota task.

        :param id: The ID of a FUOTA task.
        :param multicast_group_id: The ID of the multicast group.
        :returns: DisassociateMulticastGroupFromFuotaTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DisassociateWirelessDeviceFromFuotaTask")
    def disassociate_wireless_device_from_fuota_task(
        self, context: RequestContext, id: FuotaTaskId, wireless_device_id: WirelessDeviceId
    ) -> DisassociateWirelessDeviceFromFuotaTaskResponse:
        """Disassociates a wireless device from a FUOTA task.

        :param id: The ID of a FUOTA task.
        :param wireless_device_id: The ID of the wireless device.
        :returns: DisassociateWirelessDeviceFromFuotaTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DisassociateWirelessDeviceFromMulticastGroup")
    def disassociate_wireless_device_from_multicast_group(
        self, context: RequestContext, id: MulticastGroupId, wireless_device_id: WirelessDeviceId
    ) -> DisassociateWirelessDeviceFromMulticastGroupResponse:
        """Disassociates a wireless device from a multicast group.

        :param id: The ID of the multicast group.
        :param wireless_device_id: The ID of the wireless device.
        :returns: DisassociateWirelessDeviceFromMulticastGroupResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DisassociateWirelessDeviceFromThing")
    def disassociate_wireless_device_from_thing(
        self, context: RequestContext, id: WirelessDeviceId
    ) -> DisassociateWirelessDeviceFromThingResponse:
        """Disassociates a wireless device from its currently associated thing.

        :param id: The ID of the resource to update.
        :returns: DisassociateWirelessDeviceFromThingResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DisassociateWirelessGatewayFromCertificate")
    def disassociate_wireless_gateway_from_certificate(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> DisassociateWirelessGatewayFromCertificateResponse:
        """Disassociates a wireless gateway from its currently associated
        certificate.

        :param id: The ID of the resource to update.
        :returns: DisassociateWirelessGatewayFromCertificateResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DisassociateWirelessGatewayFromThing")
    def disassociate_wireless_gateway_from_thing(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> DisassociateWirelessGatewayFromThingResponse:
        """Disassociates a wireless gateway from its currently associated thing.

        :param id: The ID of the resource to update.
        :returns: DisassociateWirelessGatewayFromThingResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("GetDestination")
    def get_destination(
        self, context: RequestContext, name: DestinationName
    ) -> GetDestinationResponse:
        """Gets information about a destination.

        :param name: The name of the resource to get.
        :returns: GetDestinationResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetDeviceProfile")
    def get_device_profile(
        self, context: RequestContext, id: DeviceProfileId
    ) -> GetDeviceProfileResponse:
        """Gets information about a device profile.

        :param id: The ID of the resource to get.
        :returns: GetDeviceProfileResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetEventConfigurationByResourceTypes")
    def get_event_configuration_by_resource_types(
        self,
        context: RequestContext,
    ) -> GetEventConfigurationByResourceTypesResponse:
        """Get the event configuration by resource types.

        :returns: GetEventConfigurationByResourceTypesResponse
        :raises AccessDeniedException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("GetFuotaTask")
    def get_fuota_task(self, context: RequestContext, id: FuotaTaskId) -> GetFuotaTaskResponse:
        """Gets information about a FUOTA task.

        :param id: The ID of a FUOTA task.
        :returns: GetFuotaTaskResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetLogLevelsByResourceTypes")
    def get_log_levels_by_resource_types(
        self,
        context: RequestContext,
    ) -> GetLogLevelsByResourceTypesResponse:
        """Returns current default log levels or log levels by resource types.
        Based on resource types, log levels can be for wireless device log
        options or wireless gateway log options.

        :returns: GetLogLevelsByResourceTypesResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("GetMulticastGroup")
    def get_multicast_group(
        self, context: RequestContext, id: MulticastGroupId
    ) -> GetMulticastGroupResponse:
        """Gets information about a multicast group.

        :param id: The ID of the multicast group.
        :returns: GetMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetMulticastGroupSession")
    def get_multicast_group_session(
        self, context: RequestContext, id: MulticastGroupId
    ) -> GetMulticastGroupSessionResponse:
        """Gets information about a multicast group session.

        :param id: The ID of the multicast group.
        :returns: GetMulticastGroupSessionResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetNetworkAnalyzerConfiguration")
    def get_network_analyzer_configuration(
        self, context: RequestContext, configuration_name: NetworkAnalyzerConfigurationName
    ) -> GetNetworkAnalyzerConfigurationResponse:
        """Get network analyzer configuration.

        :param configuration_name: Name of the network analyzer configuration.
        :returns: GetNetworkAnalyzerConfigurationResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetPartnerAccount")
    def get_partner_account(
        self,
        context: RequestContext,
        partner_account_id: PartnerAccountId,
        partner_type: PartnerType,
    ) -> GetPartnerAccountResponse:
        """Gets information about a partner account. If ``PartnerAccountId`` and
        ``PartnerType`` are ``null``, returns all partner accounts.

        :param partner_account_id: The partner account ID to disassociate from the AWS account.
        :param partner_type: The partner type.
        :returns: GetPartnerAccountResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetResourceEventConfiguration")
    def get_resource_event_configuration(
        self,
        context: RequestContext,
        identifier: Identifier,
        identifier_type: IdentifierType,
        partner_type: EventNotificationPartnerType = None,
    ) -> GetResourceEventConfigurationResponse:
        """Get the event configuration for a particular resource identifier.

        :param identifier: Resource identifier to opt in for event messaging.
        :param identifier_type: Identifier type of the particular resource identifier for event
        configuration.
        :param partner_type: Partner type of the resource if the identifier type is PartnerAccountId.
        :returns: GetResourceEventConfigurationResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("GetResourceLogLevel")
    def get_resource_log_level(
        self,
        context: RequestContext,
        resource_identifier: ResourceIdentifier,
        resource_type: ResourceType,
    ) -> GetResourceLogLevelResponse:
        """Fetches the log-level override, if any, for a given resource-ID and
        resource-type. It can be used for a wireless device or a wireless
        gateway.

        :param resource_identifier: The identifier of the resource.
        :param resource_type: The type of the resource, which can be ``WirelessDevice`` or
        ``WirelessGateway``.
        :returns: GetResourceLogLevelResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("GetServiceEndpoint")
    def get_service_endpoint(
        self, context: RequestContext, service_type: WirelessGatewayServiceType = None
    ) -> GetServiceEndpointResponse:
        """Gets the account-specific endpoint for Configuration and Update Server
        (CUPS) protocol or LoRaWAN Network Server (LNS) connections.

        :param service_type: The service type for which to get endpoint information about.
        :returns: GetServiceEndpointResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetServiceProfile")
    def get_service_profile(
        self, context: RequestContext, id: ServiceProfileId
    ) -> GetServiceProfileResponse:
        """Gets information about a service profile.

        :param id: The ID of the resource to get.
        :returns: GetServiceProfileResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessDevice")
    def get_wireless_device(
        self, context: RequestContext, identifier: Identifier, identifier_type: WirelessDeviceIdType
    ) -> GetWirelessDeviceResponse:
        """Gets information about a wireless device.

        :param identifier: The identifier of the wireless device to get.
        :param identifier_type: The type of identifier used in ``identifier``.
        :returns: GetWirelessDeviceResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessDeviceStatistics")
    def get_wireless_device_statistics(
        self, context: RequestContext, wireless_device_id: WirelessDeviceId
    ) -> GetWirelessDeviceStatisticsResponse:
        """Gets operating information about a wireless device.

        :param wireless_device_id: The ID of the wireless device for which to get the data.
        :returns: GetWirelessDeviceStatisticsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessGateway")
    def get_wireless_gateway(
        self,
        context: RequestContext,
        identifier: Identifier,
        identifier_type: WirelessGatewayIdType,
    ) -> GetWirelessGatewayResponse:
        """Gets information about a wireless gateway.

        :param identifier: The identifier of the wireless gateway to get.
        :param identifier_type: The type of identifier used in ``identifier``.
        :returns: GetWirelessGatewayResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessGatewayCertificate")
    def get_wireless_gateway_certificate(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> GetWirelessGatewayCertificateResponse:
        """Gets the ID of the certificate that is currently associated with a
        wireless gateway.

        :param id: The ID of the resource to get.
        :returns: GetWirelessGatewayCertificateResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessGatewayFirmwareInformation")
    def get_wireless_gateway_firmware_information(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> GetWirelessGatewayFirmwareInformationResponse:
        """Gets the firmware version and other information about a wireless
        gateway.

        :param id: The ID of the resource to get.
        :returns: GetWirelessGatewayFirmwareInformationResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessGatewayStatistics")
    def get_wireless_gateway_statistics(
        self, context: RequestContext, wireless_gateway_id: WirelessGatewayId
    ) -> GetWirelessGatewayStatisticsResponse:
        """Gets operating information about a wireless gateway.

        :param wireless_gateway_id: The ID of the wireless gateway for which to get the data.
        :returns: GetWirelessGatewayStatisticsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessGatewayTask")
    def get_wireless_gateway_task(
        self, context: RequestContext, id: WirelessGatewayId
    ) -> GetWirelessGatewayTaskResponse:
        """Gets information about a wireless gateway task.

        :param id: The ID of the resource to get.
        :returns: GetWirelessGatewayTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetWirelessGatewayTaskDefinition")
    def get_wireless_gateway_task_definition(
        self, context: RequestContext, id: WirelessGatewayTaskDefinitionId
    ) -> GetWirelessGatewayTaskDefinitionResponse:
        """Gets information about a wireless gateway task definition.

        :param id: The ID of the resource to get.
        :returns: GetWirelessGatewayTaskDefinitionResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListDestinations")
    def list_destinations(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListDestinationsResponse:
        """Lists the destinations registered to your AWS account.

        :param max_results: The maximum number of results to return in this operation.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :returns: ListDestinationsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListDeviceProfiles")
    def list_device_profiles(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListDeviceProfilesResponse:
        """Lists the device profiles registered to your AWS account.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListDeviceProfilesResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListEventConfigurations")
    def list_event_configurations(
        self,
        context: RequestContext,
        resource_type: EventNotificationResourceType,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListEventConfigurationsResponse:
        """List event configurations where at least one event topic has been
        enabled.

        :param resource_type: Resource type to filter event configurations.
        :param max_results: The maximum number of results to return in this operation.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :returns: ListEventConfigurationsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListFuotaTasks")
    def list_fuota_tasks(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListFuotaTasksResponse:
        """Lists the FUOTA tasks registered to your AWS account.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListFuotaTasksResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListMulticastGroups")
    def list_multicast_groups(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListMulticastGroupsResponse:
        """Lists the multicast groups registered to your AWS account.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListMulticastGroupsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListMulticastGroupsByFuotaTask")
    def list_multicast_groups_by_fuota_task(
        self,
        context: RequestContext,
        id: FuotaTaskId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListMulticastGroupsByFuotaTaskResponse:
        """List all multicast groups associated with a fuota task.

        :param id: The ID of a FUOTA task.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListMulticastGroupsByFuotaTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListNetworkAnalyzerConfigurations")
    def list_network_analyzer_configurations(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListNetworkAnalyzerConfigurationsResponse:
        """Lists the network analyzer configurations.

        :param max_results: The maximum number of results to return in this operation.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :returns: ListNetworkAnalyzerConfigurationsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListPartnerAccounts")
    def list_partner_accounts(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListPartnerAccountsResponse:
        """Lists the partner accounts associated with your AWS account.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListPartnerAccountsResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListQueuedMessages")
    def list_queued_messages(
        self,
        context: RequestContext,
        id: WirelessDeviceId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        wireless_device_type: WirelessDeviceType = None,
    ) -> ListQueuedMessagesResponse:
        """List queued messages in the downlink queue.

        :param id: The ID of a given wireless device which the downlink message packets are
        being sent.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :param wireless_device_type: The wireless device type, whic can be either Sidewalk or LoRaWAN.
        :returns: ListQueuedMessagesResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("ListServiceProfiles")
    def list_service_profiles(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListServiceProfilesResponse:
        """Lists the service profiles registered to your AWS account.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListServiceProfilesResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName
    ) -> ListTagsForResourceResponse:
        """Lists the tags (metadata) you have assigned to the resource.

        :param resource_arn: The ARN of the resource for which you want to list tags.
        :returns: ListTagsForResourceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListWirelessDevices")
    def list_wireless_devices(
        self,
        context: RequestContext,
        max_results: MaxResults = None,
        next_token: NextToken = None,
        destination_name: DestinationName = None,
        device_profile_id: DeviceProfileId = None,
        service_profile_id: ServiceProfileId = None,
        wireless_device_type: WirelessDeviceType = None,
        fuota_task_id: FuotaTaskId = None,
        multicast_group_id: MulticastGroupId = None,
    ) -> ListWirelessDevicesResponse:
        """Lists the wireless devices registered to your AWS account.

        :param max_results: The maximum number of results to return in this operation.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param destination_name: A filter to list only the wireless devices that use this destination.
        :param device_profile_id: A filter to list only the wireless devices that use this device profile.
        :param service_profile_id: A filter to list only the wireless devices that use this service
        profile.
        :param wireless_device_type: A filter to list only the wireless devices that use this wireless device
        type.
        :param fuota_task_id: The ID of a FUOTA task.
        :param multicast_group_id: The ID of the multicast group.
        :returns: ListWirelessDevicesResponse
        :raises ValidationException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("ListWirelessGatewayTaskDefinitions")
    def list_wireless_gateway_task_definitions(
        self,
        context: RequestContext,
        max_results: MaxResults = None,
        next_token: NextToken = None,
        task_definition_type: WirelessGatewayTaskDefinitionType = None,
    ) -> ListWirelessGatewayTaskDefinitionsResponse:
        """List the wireless gateway tasks definitions registered to your AWS
        account.

        :param max_results: The maximum number of results to return in this operation.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param task_definition_type: A filter to list only the wireless gateway task definitions that use
        this task definition type.
        :returns: ListWirelessGatewayTaskDefinitionsResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListWirelessGateways")
    def list_wireless_gateways(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListWirelessGatewaysResponse:
        """Lists the wireless gateways registered to your AWS account.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListWirelessGatewaysResponse
        :raises ValidationException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("PutResourceLogLevel")
    def put_resource_log_level(
        self,
        context: RequestContext,
        resource_identifier: ResourceIdentifier,
        resource_type: ResourceType,
        log_level: LogLevel,
    ) -> PutResourceLogLevelResponse:
        """Sets the log-level override for a resource-ID and resource-type. This
        option can be specified for a wireless gateway or a wireless device. A
        limit of 200 log level override can be set per account.

        :param resource_identifier: The identifier of the resource.
        :param resource_type: The type of the resource, which can be ``WirelessDevice`` or
        ``WirelessGateway``.
        :param log_level: The log level for a log message.
        :returns: PutResourceLogLevelResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("ResetAllResourceLogLevels")
    def reset_all_resource_log_levels(
        self,
        context: RequestContext,
    ) -> ResetAllResourceLogLevelsResponse:
        """Removes the log-level overrides for all resources; both wireless devices
        and wireless gateways.

        :returns: ResetAllResourceLogLevelsResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("ResetResourceLogLevel")
    def reset_resource_log_level(
        self,
        context: RequestContext,
        resource_identifier: ResourceIdentifier,
        resource_type: ResourceType,
    ) -> ResetResourceLogLevelResponse:
        """Removes the log-level override, if any, for a specific resource-ID and
        resource-type. It can be used for a wireless device or a wireless
        gateway.

        :param resource_identifier: The identifier of the resource.
        :param resource_type: The type of the resource, which can be ``WirelessDevice`` or
        ``WirelessGateway``.
        :returns: ResetResourceLogLevelResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("SendDataToMulticastGroup")
    def send_data_to_multicast_group(
        self,
        context: RequestContext,
        id: MulticastGroupId,
        payload_data: PayloadData,
        wireless_metadata: MulticastWirelessMetadata,
    ) -> SendDataToMulticastGroupResponse:
        """Sends the specified data to a multicast group.

        :param id: The ID of the multicast group.
        :param payload_data: The binary to be sent to the end device, encoded in base64.
        :param wireless_metadata: Wireless metadata that is to be sent to multicast group.
        :returns: SendDataToMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("SendDataToWirelessDevice")
    def send_data_to_wireless_device(
        self,
        context: RequestContext,
        id: WirelessDeviceId,
        transmit_mode: TransmitMode,
        payload_data: PayloadData,
        wireless_metadata: WirelessMetadata = None,
    ) -> SendDataToWirelessDeviceResponse:
        """Sends a decrypted application data frame to a device.

        :param id: The ID of the wireless device to receive the data.
        :param transmit_mode: The transmit mode to use to send data to the wireless device.
        :param payload_data: The binary to be sent to the end device, encoded in base64.
        :param wireless_metadata: Metadata about the message request.
        :returns: SendDataToWirelessDeviceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("StartBulkAssociateWirelessDeviceWithMulticastGroup")
    def start_bulk_associate_wireless_device_with_multicast_group(
        self,
        context: RequestContext,
        id: MulticastGroupId,
        query_string: QueryString = None,
        tags: TagList = None,
    ) -> StartBulkAssociateWirelessDeviceWithMulticastGroupResponse:
        """Starts a bulk association of all qualifying wireless devices with a
        multicast group.

        :param id: The ID of the multicast group.
        :param query_string: Query string used to search for wireless devices as part of the bulk
        associate and disassociate process.
        :param tags: The tag to attach to the specified resource.
        :returns: StartBulkAssociateWirelessDeviceWithMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("StartBulkDisassociateWirelessDeviceFromMulticastGroup")
    def start_bulk_disassociate_wireless_device_from_multicast_group(
        self,
        context: RequestContext,
        id: MulticastGroupId,
        query_string: QueryString = None,
        tags: TagList = None,
    ) -> StartBulkDisassociateWirelessDeviceFromMulticastGroupResponse:
        """Starts a bulk disassociatin of all qualifying wireless devices from a
        multicast group.

        :param id: The ID of the multicast group.
        :param query_string: Query string used to search for wireless devices as part of the bulk
        associate and disassociate process.
        :param tags: The tag to attach to the specified resource.
        :returns: StartBulkDisassociateWirelessDeviceFromMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("StartFuotaTask")
    def start_fuota_task(
        self, context: RequestContext, id: FuotaTaskId, lo_ra_wan: LoRaWANStartFuotaTask = None
    ) -> StartFuotaTaskResponse:
        """Starts a FUOTA task.

        :param id: The ID of a FUOTA task.
        :param lo_ra_wan: The LoRaWAN information used to start a FUOTA task.
        :returns: StartFuotaTaskResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("StartMulticastGroupSession")
    def start_multicast_group_session(
        self, context: RequestContext, id: MulticastGroupId, lo_ra_wan: LoRaWANMulticastSession
    ) -> StartMulticastGroupSessionResponse:
        """Starts a multicast group session.

        :param id: The ID of the multicast group.
        :param lo_ra_wan: The LoRaWAN information used with the multicast session.
        :returns: StartMulticastGroupSessionResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceResponse:
        """Adds a tag to a resource.

        :param resource_arn: The ARN of the resource to add tags to.
        :param tags: Adds to or modifies the tags of the given resource.
        :returns: TagResourceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises TooManyTagsException:
        """
        raise NotImplementedError

    @handler("TestWirelessDevice")
    def test_wireless_device(
        self, context: RequestContext, id: WirelessDeviceId
    ) -> TestWirelessDeviceResponse:
        """Simulates a provisioned device by sending an uplink data payload of
        ``Hello``.

        :param id: The ID of the wireless device to test.
        :returns: TestWirelessDeviceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes one or more tags from a resource.

        :param resource_arn: The ARN of the resource to remove tags from.
        :param tag_keys: A list of the keys of the tags to remove from the resource.
        :returns: UntagResourceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateDestination")
    def update_destination(
        self,
        context: RequestContext,
        name: DestinationName,
        expression_type: ExpressionType = None,
        expression: Expression = None,
        description: Description = None,
        role_arn: RoleArn = None,
    ) -> UpdateDestinationResponse:
        """Updates properties of a destination.

        :param name: The new name of the resource.
        :param expression_type: The type of value in ``Expression``.
        :param expression: The new rule name or topic rule to send messages to.
        :param description: A new description of the resource.
        :param role_arn: The ARN of the IAM Role that authorizes the destination.
        :returns: UpdateDestinationResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateEventConfigurationByResourceTypes")
    def update_event_configuration_by_resource_types(
        self,
        context: RequestContext,
        device_registration_state: DeviceRegistrationStateResourceTypeEventConfiguration = None,
        proximity: ProximityResourceTypeEventConfiguration = None,
        join: JoinResourceTypeEventConfiguration = None,
        connection_status: ConnectionStatusResourceTypeEventConfiguration = None,
    ) -> UpdateEventConfigurationByResourceTypesResponse:
        """Update the event configuration by resource types.

        :param device_registration_state: Device registration state resource type event configuration object for
        enabling and disabling wireless gateway topic.
        :param proximity: Proximity resource type event configuration object for enabling and
        disabling wireless gateway topic.
        :param join: Join resource type event configuration object for enabling and disabling
        wireless device topic.
        :param connection_status: Connection status resource type event configuration object for enabling
        and disabling wireless gateway topic.
        :returns: UpdateEventConfigurationByResourceTypesResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateFuotaTask")
    def update_fuota_task(
        self,
        context: RequestContext,
        id: FuotaTaskId,
        name: FuotaTaskName = None,
        description: Description = None,
        lo_ra_wan: LoRaWANFuotaTask = None,
        firmware_update_image: FirmwareUpdateImage = None,
        firmware_update_role: FirmwareUpdateRole = None,
    ) -> UpdateFuotaTaskResponse:
        """Updates properties of a FUOTA task.

        :param id: The ID of a FUOTA task.
        :param name: The name of a FUOTA task.
        :param description: The description of the new resource.
        :param lo_ra_wan: The LoRaWAN information used with a FUOTA task.
        :param firmware_update_image: The S3 URI points to a firmware update image that is to be used with a
        FUOTA task.
        :param firmware_update_role: The firmware update role that is to be used with a FUOTA task.
        :returns: UpdateFuotaTaskResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateLogLevelsByResourceTypes")
    def update_log_levels_by_resource_types(
        self,
        context: RequestContext,
        default_log_level: LogLevel = None,
        wireless_device_log_options: WirelessDeviceLogOptionList = None,
        wireless_gateway_log_options: WirelessGatewayLogOptionList = None,
    ) -> UpdateLogLevelsByResourceTypesResponse:
        """Set default log level, or log levels by resource types. This can be for
        wireless device log options or wireless gateways log options and is used
        to control the log messages that'll be displayed in CloudWatch.

        :param default_log_level: The log level for a log message.
        :param wireless_device_log_options: The list of wireless device log options.
        :param wireless_gateway_log_options: The list of wireless gateway log options.
        :returns: UpdateLogLevelsByResourceTypesResponse
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("UpdateMulticastGroup")
    def update_multicast_group(
        self,
        context: RequestContext,
        id: MulticastGroupId,
        name: MulticastGroupName = None,
        description: Description = None,
        lo_ra_wan: LoRaWANMulticast = None,
    ) -> UpdateMulticastGroupResponse:
        """Updates properties of a multicast group session.

        :param id: The ID of the multicast group.
        :param name: The name of the multicast group.
        :param description: The description of the new resource.
        :param lo_ra_wan: The LoRaWAN information that is to be used with the multicast group.
        :returns: UpdateMulticastGroupResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateNetworkAnalyzerConfiguration")
    def update_network_analyzer_configuration(
        self,
        context: RequestContext,
        configuration_name: NetworkAnalyzerConfigurationName,
        trace_content: TraceContent = None,
        wireless_devices_to_add: WirelessDeviceList = None,
        wireless_devices_to_remove: WirelessDeviceList = None,
        wireless_gateways_to_add: WirelessGatewayList = None,
        wireless_gateways_to_remove: WirelessGatewayList = None,
        description: Description = None,
    ) -> UpdateNetworkAnalyzerConfigurationResponse:
        """Update network analyzer configuration.

        :param configuration_name: Name of the network analyzer configuration.
        :param trace_content: Trace content for your wireless gateway and wireless device resources.
        :param wireless_devices_to_add: Wireless device resources to add to the network analyzer configuration.
        :param wireless_devices_to_remove: Wireless device resources to remove from the network analyzer
        configuration.
        :param wireless_gateways_to_add: Wireless gateway resources to add to the network analyzer configuration.
        :param wireless_gateways_to_remove: Wireless gateway resources to remove from the network analyzer
        configuration.
        :param description: The description of the new resource.
        :returns: UpdateNetworkAnalyzerConfigurationResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdatePartnerAccount")
    def update_partner_account(
        self,
        context: RequestContext,
        sidewalk: SidewalkUpdateAccount,
        partner_account_id: PartnerAccountId,
        partner_type: PartnerType,
    ) -> UpdatePartnerAccountResponse:
        """Updates properties of a partner account.

        :param sidewalk: The Sidewalk account credentials.
        :param partner_account_id: The ID of the partner account to update.
        :param partner_type: The partner type.
        :returns: UpdatePartnerAccountResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateResourceEventConfiguration")
    def update_resource_event_configuration(
        self,
        context: RequestContext,
        identifier: Identifier,
        identifier_type: IdentifierType,
        partner_type: EventNotificationPartnerType = None,
        device_registration_state: DeviceRegistrationStateEventConfiguration = None,
        proximity: ProximityEventConfiguration = None,
        join: JoinEventConfiguration = None,
        connection_status: ConnectionStatusEventConfiguration = None,
    ) -> UpdateResourceEventConfigurationResponse:
        """Update the event configuration for a particular resource identifier.

        :param identifier: Resource identifier to opt in for event messaging.
        :param identifier_type: Identifier type of the particular resource identifier for event
        configuration.
        :param partner_type: Partner type of the resource if the identifier type is PartnerAccountId.
        :param device_registration_state: Event configuration for the device registration state event.
        :param proximity: Event configuration for the Proximity event.
        :param join: Event configuration for the join event.
        :param connection_status: Event configuration for the connection status event.
        :returns: UpdateResourceEventConfigurationResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateWirelessDevice")
    def update_wireless_device(
        self,
        context: RequestContext,
        id: WirelessDeviceId,
        destination_name: DestinationName = None,
        name: WirelessDeviceName = None,
        description: Description = None,
        lo_ra_wan: LoRaWANUpdateDevice = None,
    ) -> UpdateWirelessDeviceResponse:
        """Updates properties of a wireless device.

        :param id: The ID of the resource to update.
        :param destination_name: The name of the new destination for the device.
        :param name: The new name of the resource.
        :param description: A new description of the resource.
        :param lo_ra_wan: The updated wireless device's configuration.
        :returns: UpdateWirelessDeviceResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateWirelessGateway")
    def update_wireless_gateway(
        self,
        context: RequestContext,
        id: WirelessGatewayId,
        name: WirelessGatewayName = None,
        description: Description = None,
        join_eui_filters: JoinEuiFilters = None,
        net_id_filters: NetIdFilters = None,
    ) -> UpdateWirelessGatewayResponse:
        """Updates properties of a wireless gateway.

        :param id: The ID of the resource to update.
        :param name: The new name of the resource.
        :param description: A new description of the resource.
        :param join_eui_filters: A list of JoinEuiRange used by LoRa gateways to filter LoRa frames.
        :param net_id_filters: A list of NetId values that are used by LoRa gateways to filter the
        uplink frames.
        :returns: UpdateWirelessGatewayResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        """
        raise NotImplementedError
