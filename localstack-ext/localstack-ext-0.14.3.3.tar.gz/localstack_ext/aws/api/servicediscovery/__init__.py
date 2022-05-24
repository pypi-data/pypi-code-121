import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AmazonResourceName = str
Arn = str
AttrKey = str
AttrValue = str
Code = str
DiscoverMaxResults = int
ErrorMessage = str
FailureThreshold = int
FilterValue = str
InstanceId = str
MaxResults = int
Message = str
NamespaceName = str
NamespaceNameHttp = str
NamespaceNamePrivate = str
NamespaceNamePublic = str
NextToken = str
OperationId = str
ResourceCount = int
ResourceDescription = str
ResourceId = str
ResourcePath = str
ServiceName = str
TagKey = str
TagValue = str


class CustomHealthStatus(str):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


class FilterCondition(str):
    EQ = "EQ"
    IN = "IN"
    BETWEEN = "BETWEEN"


class HealthCheckType(str):
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    TCP = "TCP"


class HealthStatus(str):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class HealthStatusFilter(str):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    ALL = "ALL"
    HEALTHY_OR_ELSE_ALL = "HEALTHY_OR_ELSE_ALL"


class NamespaceFilterName(str):
    TYPE = "TYPE"


class NamespaceType(str):
    DNS_PUBLIC = "DNS_PUBLIC"
    DNS_PRIVATE = "DNS_PRIVATE"
    HTTP = "HTTP"


class OperationFilterName(str):
    NAMESPACE_ID = "NAMESPACE_ID"
    SERVICE_ID = "SERVICE_ID"
    STATUS = "STATUS"
    TYPE = "TYPE"
    UPDATE_DATE = "UPDATE_DATE"


class OperationStatus(str):
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


class OperationTargetType(str):
    NAMESPACE = "NAMESPACE"
    SERVICE = "SERVICE"
    INSTANCE = "INSTANCE"


class OperationType(str):
    CREATE_NAMESPACE = "CREATE_NAMESPACE"
    DELETE_NAMESPACE = "DELETE_NAMESPACE"
    UPDATE_NAMESPACE = "UPDATE_NAMESPACE"
    UPDATE_SERVICE = "UPDATE_SERVICE"
    REGISTER_INSTANCE = "REGISTER_INSTANCE"
    DEREGISTER_INSTANCE = "DEREGISTER_INSTANCE"


class RecordType(str):
    SRV = "SRV"
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"


class RoutingPolicy(str):
    MULTIVALUE = "MULTIVALUE"
    WEIGHTED = "WEIGHTED"


class ServiceFilterName(str):
    NAMESPACE_ID = "NAMESPACE_ID"


class ServiceType(str):
    HTTP = "HTTP"
    DNS_HTTP = "DNS_HTTP"
    DNS = "DNS"


class ServiceTypeOption(str):
    HTTP = "HTTP"


class CustomHealthNotFound(ServiceException):
    """The health check for the instance that's specified by ``ServiceId`` and
    ``InstanceId`` isn't a custom health check.
    """

    Message: Optional[ErrorMessage]


class DuplicateRequest(ServiceException):
    """The operation is already in progress."""

    Message: Optional[ErrorMessage]
    DuplicateOperationId: Optional[ResourceId]


class InstanceNotFound(ServiceException):
    """No instance exists with the specified ID, or the instance was recently
    registered, and information about the instance hasn't propagated yet.
    """

    Message: Optional[ErrorMessage]


class InvalidInput(ServiceException):
    """One or more specified values aren't valid. For example, a required value
    might be missing, a numeric value might be outside the allowed range, or
    a string value might exceed length constraints.
    """

    Message: Optional[ErrorMessage]


class NamespaceAlreadyExists(ServiceException):
    """The namespace that you're trying to create already exists."""

    Message: Optional[ErrorMessage]
    CreatorRequestId: Optional[ResourceId]
    NamespaceId: Optional[ResourceId]


class NamespaceNotFound(ServiceException):
    """No namespace exists with the specified ID."""

    Message: Optional[ErrorMessage]


class OperationNotFound(ServiceException):
    """No operation exists with the specified ID."""

    Message: Optional[ErrorMessage]


class RequestLimitExceeded(ServiceException):
    """The operation can't be completed because you've reached the quota for
    the number of requests. For more information, see `Cloud Map API request
    throttling
    quota <https://docs.aws.amazon.com/cloud-map/latest/dg/throttling.html>`__
    in the *Cloud Map Developer Guide*.
    """

    Message: Optional[ErrorMessage]


class ResourceInUse(ServiceException):
    """The specified resource can't be deleted because it contains other
    resources. For example, you can't delete a service that contains any
    instances.
    """

    Message: Optional[ErrorMessage]


class ResourceLimitExceeded(ServiceException):
    """The resource can't be created because you've reached the quota on the
    number of resources.
    """

    Message: Optional[ErrorMessage]


class ResourceNotFoundException(ServiceException):
    """The operation can't be completed because the resource was not found."""

    Message: Optional[ErrorMessage]


class ServiceAlreadyExists(ServiceException):
    """The service can't be created because a service with the same name
    already exists.
    """

    Message: Optional[ErrorMessage]
    CreatorRequestId: Optional[ResourceId]
    ServiceId: Optional[ResourceId]


class ServiceNotFound(ServiceException):
    """No service exists with the specified ID."""

    Message: Optional[ErrorMessage]


class TooManyTagsException(ServiceException):
    """The list of tags on the resource is over the quota. The maximum number
    of tags that can be applied to a resource is 50.
    """

    Message: Optional[ErrorMessage]
    ResourceName: Optional[AmazonResourceName]


Attributes = Dict[AttrKey, AttrValue]


class Tag(TypedDict, total=False):
    """A custom key-value pair that's associated with a resource."""

    Key: TagKey
    Value: TagValue


TagList = List[Tag]


class CreateHttpNamespaceRequest(ServiceRequest):
    Name: NamespaceNameHttp
    CreatorRequestId: Optional[ResourceId]
    Description: Optional[ResourceDescription]
    Tags: Optional[TagList]


class CreateHttpNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


RecordTTL = int


class SOA(TypedDict, total=False):
    """Start of Authority (SOA) properties for a public or private DNS
    namespace.
    """

    TTL: RecordTTL


class PrivateDnsPropertiesMutable(TypedDict, total=False):
    """DNS properties for the private DNS namespace."""

    SOA: SOA


class PrivateDnsNamespaceProperties(TypedDict, total=False):
    """DNS properties for the private DNS namespace."""

    DnsProperties: PrivateDnsPropertiesMutable


class CreatePrivateDnsNamespaceRequest(ServiceRequest):
    Name: NamespaceNamePrivate
    CreatorRequestId: Optional[ResourceId]
    Description: Optional[ResourceDescription]
    Vpc: ResourceId
    Tags: Optional[TagList]
    Properties: Optional[PrivateDnsNamespaceProperties]


class CreatePrivateDnsNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class PublicDnsPropertiesMutable(TypedDict, total=False):
    """DNS properties for the public DNS namespace."""

    SOA: SOA


class PublicDnsNamespaceProperties(TypedDict, total=False):
    """DNS properties for the public DNS namespace."""

    DnsProperties: PublicDnsPropertiesMutable


class CreatePublicDnsNamespaceRequest(ServiceRequest):
    Name: NamespaceNamePublic
    CreatorRequestId: Optional[ResourceId]
    Description: Optional[ResourceDescription]
    Tags: Optional[TagList]
    Properties: Optional[PublicDnsNamespaceProperties]


class CreatePublicDnsNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class HealthCheckCustomConfig(TypedDict, total=False):
    """A complex type that contains information about an optional custom health
    check. A custom health check, which requires that you use a third-party
    health checker to evaluate the health of your resources, is useful in
    the following circumstances:

    -  You can't use a health check that's defined by ``HealthCheckConfig``
       because the resource isn't available over the internet. For example,
       you can use a custom health check when the instance is in an Amazon
       VPC. (To check the health of resources in a VPC, the health checker
       must also be in the VPC.)

    -  You want to use a third-party health checker regardless of where your
       resources are located.

    If you specify a health check configuration, you can specify either
    ``HealthCheckCustomConfig`` or ``HealthCheckConfig`` but not both.

    To change the status of a custom health check, submit an
    ``UpdateInstanceCustomHealthStatus`` request. Cloud Map doesn't monitor
    the status of the resource, it just keeps a record of the status
    specified in the most recent ``UpdateInstanceCustomHealthStatus``
    request.

    Here's how custom health checks work:

    #. You create a service.

    #. You register an instance.

    #. You configure a third-party health checker to monitor the resource
       that's associated with the new instance.

       Cloud Map doesn't check the health of the resource directly.

    #. The third-party health-checker determines that the resource is
       unhealthy and notifies your application.

    #. Your application submits an ``UpdateInstanceCustomHealthStatus``
       request.

    #. Cloud Map waits for 30 seconds.

    #. If another ``UpdateInstanceCustomHealthStatus`` request doesn't
       arrive during that time to change the status back to healthy, Cloud
       Map stops routing traffic to the resource.
    """

    FailureThreshold: Optional[FailureThreshold]


class HealthCheckConfig(TypedDict, total=False):
    """*Public DNS and HTTP namespaces only.* A complex type that contains
    settings for an optional health check. If you specify settings for a
    health check, Cloud Map associates the health check with the records
    that you specify in ``DnsConfig``.

    If you specify a health check configuration, you can specify either
    ``HealthCheckCustomConfig`` or ``HealthCheckConfig`` but not both.

    Health checks are basic Route 53 health checks that monitor an Amazon
    Web Services endpoint. For information about pricing for health checks,
    see `Amazon Route 53
    Pricing <http://aws.amazon.com/route53/pricing/>`__.

    Note the following about configuring health checks.

    A and AAAA records
       If ``DnsConfig`` includes configurations for both ``A`` and ``AAAA``
       records, Cloud Map creates a health check that uses the IPv4 address
       to check the health of the resource. If the endpoint tthat's
       specified by the IPv4 address is unhealthy, Route 53 considers both
       the ``A`` and ``AAAA`` records to be unhealthy.

    CNAME records
       You can't specify settings for ``HealthCheckConfig`` when the
       ``DNSConfig`` includes ``CNAME`` for the value of ``Type``. If you
       do, the ``CreateService`` request will fail with an ``InvalidInput``
       error.

    Request interval
       A Route 53 health checker in each health-checking Amazon Web Services
       Region sends a health check request to an endpoint every 30 seconds.
       On average, your endpoint receives a health check request about every
       two seconds. However, health checkers don't coordinate with one
       another. Therefore, you might sometimes see several requests in one
       second that's followed by a few seconds with no health checks at all.

    Health checking regions
       Health checkers perform checks from all Route 53 health-checking
       Regions. For a list of the current Regions, see
       `Regions <https://docs.aws.amazon.com/Route53/latest/APIReference/API_HealthCheckConfig.html#Route53-Type-HealthCheckConfig-Regions>`__.

    Alias records
       When you register an instance, if you include the
       ``AWS_ALIAS_DNS_NAME`` attribute, Cloud Map creates a Route 53 alias
       record. Note the following:

       -  Route 53 automatically sets ``EvaluateTargetHealth`` to true for
          alias records. When ``EvaluateTargetHealth`` is true, the alias
          record inherits the health of the referenced Amazon Web Services
          resource. such as an ELB load balancer. For more information, see
          `EvaluateTargetHealth <https://docs.aws.amazon.com/Route53/latest/APIReference/API_AliasTarget.html#Route53-Type-AliasTarget-EvaluateTargetHealth>`__.

       -  If you include ``HealthCheckConfig`` and then use the service to
          register an instance that creates an alias record, Route 53
          doesn't create the health check.

    Charges for health checks
       Health checks are basic Route 53 health checks that monitor an Amazon
       Web Services endpoint. For information about pricing for health
       checks, see `Amazon Route 53
       Pricing <http://aws.amazon.com/route53/pricing/>`__.
    """

    Type: HealthCheckType
    ResourcePath: Optional[ResourcePath]
    FailureThreshold: Optional[FailureThreshold]


class DnsRecord(TypedDict, total=False):
    """A complex type that contains information about the Route 53 DNS records
    that you want Cloud Map to create when you register an instance.
    """

    Type: RecordType
    TTL: RecordTTL


DnsRecordList = List[DnsRecord]


class DnsConfig(TypedDict, total=False):
    """A complex type that contains information about the Amazon Route 53 DNS
    records that you want Cloud Map to create when you register an instance.
    """

    NamespaceId: Optional[ResourceId]
    RoutingPolicy: Optional[RoutingPolicy]
    DnsRecords: DnsRecordList


class CreateServiceRequest(ServiceRequest):
    Name: ServiceName
    NamespaceId: Optional[ResourceId]
    CreatorRequestId: Optional[ResourceId]
    Description: Optional[ResourceDescription]
    DnsConfig: Optional[DnsConfig]
    HealthCheckConfig: Optional[HealthCheckConfig]
    HealthCheckCustomConfig: Optional[HealthCheckCustomConfig]
    Tags: Optional[TagList]
    Type: Optional[ServiceTypeOption]


Timestamp = datetime


class Service(TypedDict, total=False):
    """A complex type that contains information about the specified service."""

    Id: Optional[ResourceId]
    Arn: Optional[Arn]
    Name: Optional[ServiceName]
    NamespaceId: Optional[ResourceId]
    Description: Optional[ResourceDescription]
    InstanceCount: Optional[ResourceCount]
    DnsConfig: Optional[DnsConfig]
    Type: Optional[ServiceType]
    HealthCheckConfig: Optional[HealthCheckConfig]
    HealthCheckCustomConfig: Optional[HealthCheckCustomConfig]
    CreateDate: Optional[Timestamp]
    CreatorRequestId: Optional[ResourceId]


class CreateServiceResponse(TypedDict, total=False):
    Service: Optional[Service]


class DeleteNamespaceRequest(ServiceRequest):
    Id: ResourceId


class DeleteNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class DeleteServiceRequest(ServiceRequest):
    Id: ResourceId


class DeleteServiceResponse(TypedDict, total=False):
    pass


class DeregisterInstanceRequest(ServiceRequest):
    ServiceId: ResourceId
    InstanceId: ResourceId


class DeregisterInstanceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class DiscoverInstancesRequest(ServiceRequest):
    NamespaceName: NamespaceName
    ServiceName: ServiceName
    MaxResults: Optional[DiscoverMaxResults]
    QueryParameters: Optional[Attributes]
    OptionalParameters: Optional[Attributes]
    HealthStatus: Optional[HealthStatusFilter]


class HttpInstanceSummary(TypedDict, total=False):
    """In a response to a
    `DiscoverInstances <https://docs.aws.amazon.com/cloud-map/latest/api/API_DiscoverInstances.html>`__
    request, ``HttpInstanceSummary`` contains information about one instance
    that matches the values that you specified in the request.
    """

    InstanceId: Optional[ResourceId]
    NamespaceName: Optional[NamespaceNameHttp]
    ServiceName: Optional[ServiceName]
    HealthStatus: Optional[HealthStatus]
    Attributes: Optional[Attributes]


HttpInstanceSummaryList = List[HttpInstanceSummary]


class DiscoverInstancesResponse(TypedDict, total=False):
    Instances: Optional[HttpInstanceSummaryList]


class DnsConfigChange(TypedDict, total=False):
    """A complex type that contains information about changes to the Route 53
    DNS records that Cloud Map creates when you register an instance.
    """

    DnsRecords: DnsRecordList


class DnsProperties(TypedDict, total=False):
    """A complex type that contains the ID for the Route 53 hosted zone that
    Cloud Map creates when you create a namespace.
    """

    HostedZoneId: Optional[ResourceId]
    SOA: Optional[SOA]


FilterValues = List[FilterValue]


class GetInstanceRequest(ServiceRequest):
    ServiceId: ResourceId
    InstanceId: ResourceId


class Instance(TypedDict, total=False):
    """A complex type that contains information about an instance that Cloud
    Map creates when you submit a ``RegisterInstance`` request.
    """

    Id: ResourceId
    CreatorRequestId: Optional[ResourceId]
    Attributes: Optional[Attributes]


class GetInstanceResponse(TypedDict, total=False):
    Instance: Optional[Instance]


InstanceIdList = List[ResourceId]


class GetInstancesHealthStatusRequest(ServiceRequest):
    ServiceId: ResourceId
    Instances: Optional[InstanceIdList]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


InstanceHealthStatusMap = Dict[ResourceId, HealthStatus]


class GetInstancesHealthStatusResponse(TypedDict, total=False):
    Status: Optional[InstanceHealthStatusMap]
    NextToken: Optional[NextToken]


class GetNamespaceRequest(ServiceRequest):
    Id: ResourceId


class HttpProperties(TypedDict, total=False):
    """A complex type that contains the name of an HTTP namespace."""

    HttpName: Optional[NamespaceName]


class NamespaceProperties(TypedDict, total=False):
    """A complex type that contains information that's specific to the
    namespace type.
    """

    DnsProperties: Optional[DnsProperties]
    HttpProperties: Optional[HttpProperties]


class Namespace(TypedDict, total=False):
    """A complex type that contains information about a specified namespace."""

    Id: Optional[ResourceId]
    Arn: Optional[Arn]
    Name: Optional[NamespaceName]
    Type: Optional[NamespaceType]
    Description: Optional[ResourceDescription]
    ServiceCount: Optional[ResourceCount]
    Properties: Optional[NamespaceProperties]
    CreateDate: Optional[Timestamp]
    CreatorRequestId: Optional[ResourceId]


class GetNamespaceResponse(TypedDict, total=False):
    Namespace: Optional[Namespace]


class GetOperationRequest(ServiceRequest):
    OperationId: ResourceId


OperationTargetsMap = Dict[OperationTargetType, ResourceId]


class Operation(TypedDict, total=False):
    """A complex type that contains information about a specified operation."""

    Id: Optional[OperationId]
    Type: Optional[OperationType]
    Status: Optional[OperationStatus]
    ErrorMessage: Optional[Message]
    ErrorCode: Optional[Code]
    CreateDate: Optional[Timestamp]
    UpdateDate: Optional[Timestamp]
    Targets: Optional[OperationTargetsMap]


class GetOperationResponse(TypedDict, total=False):
    Operation: Optional[Operation]


class GetServiceRequest(ServiceRequest):
    Id: ResourceId


class GetServiceResponse(TypedDict, total=False):
    Service: Optional[Service]


class HttpNamespaceChange(TypedDict, total=False):
    """Updated properties for the HTTP namespace."""

    Description: ResourceDescription


class InstanceSummary(TypedDict, total=False):
    """A complex type that contains information about the instances that you
    registered by using a specified service.
    """

    Id: Optional[ResourceId]
    Attributes: Optional[Attributes]


InstanceSummaryList = List[InstanceSummary]


class ListInstancesRequest(ServiceRequest):
    ServiceId: ResourceId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListInstancesResponse(TypedDict, total=False):
    Instances: Optional[InstanceSummaryList]
    NextToken: Optional[NextToken]


class NamespaceFilter(TypedDict, total=False):
    """A complex type that identifies the namespaces that you want to list. You
    can choose to list public or private namespaces.
    """

    Name: NamespaceFilterName
    Values: FilterValues
    Condition: Optional[FilterCondition]


NamespaceFilters = List[NamespaceFilter]


class ListNamespacesRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]
    Filters: Optional[NamespaceFilters]


class NamespaceSummary(TypedDict, total=False):
    """A complex type that contains information about a namespace."""

    Id: Optional[ResourceId]
    Arn: Optional[Arn]
    Name: Optional[NamespaceName]
    Type: Optional[NamespaceType]
    Description: Optional[ResourceDescription]
    ServiceCount: Optional[ResourceCount]
    Properties: Optional[NamespaceProperties]
    CreateDate: Optional[Timestamp]


NamespaceSummariesList = List[NamespaceSummary]


class ListNamespacesResponse(TypedDict, total=False):
    Namespaces: Optional[NamespaceSummariesList]
    NextToken: Optional[NextToken]


class OperationFilter(TypedDict, total=False):
    """A complex type that lets you select the operations that you want to
    list.
    """

    Name: OperationFilterName
    Values: FilterValues
    Condition: Optional[FilterCondition]


OperationFilters = List[OperationFilter]


class ListOperationsRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]
    Filters: Optional[OperationFilters]


class OperationSummary(TypedDict, total=False):
    """A complex type that contains information about an operation that matches
    the criteria that you specified in a
    `ListOperations <https://docs.aws.amazon.com/cloud-map/latest/api/API_ListOperations.html>`__
    request.
    """

    Id: Optional[OperationId]
    Status: Optional[OperationStatus]


OperationSummaryList = List[OperationSummary]


class ListOperationsResponse(TypedDict, total=False):
    Operations: Optional[OperationSummaryList]
    NextToken: Optional[NextToken]


class ServiceFilter(TypedDict, total=False):
    """A complex type that lets you specify the namespaces that you want to
    list services for.
    """

    Name: ServiceFilterName
    Values: FilterValues
    Condition: Optional[FilterCondition]


ServiceFilters = List[ServiceFilter]


class ListServicesRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]
    Filters: Optional[ServiceFilters]


class ServiceSummary(TypedDict, total=False):
    """A complex type that contains information about a specified service."""

    Id: Optional[ResourceId]
    Arn: Optional[Arn]
    Name: Optional[ServiceName]
    Type: Optional[ServiceType]
    Description: Optional[ResourceDescription]
    InstanceCount: Optional[ResourceCount]
    DnsConfig: Optional[DnsConfig]
    HealthCheckConfig: Optional[HealthCheckConfig]
    HealthCheckCustomConfig: Optional[HealthCheckCustomConfig]
    CreateDate: Optional[Timestamp]


ServiceSummariesList = List[ServiceSummary]


class ListServicesResponse(TypedDict, total=False):
    Services: Optional[ServiceSummariesList]
    NextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[TagList]


class SOAChange(TypedDict, total=False):
    """Updated Start of Authority (SOA) properties for a public or private DNS
    namespace.
    """

    TTL: RecordTTL


class PrivateDnsPropertiesMutableChange(TypedDict, total=False):
    """Updated DNS properties for the private DNS namespace."""

    SOA: SOAChange


class PrivateDnsNamespacePropertiesChange(TypedDict, total=False):
    """Updated properties for the private DNS namespace."""

    DnsProperties: PrivateDnsPropertiesMutableChange


class PrivateDnsNamespaceChange(TypedDict, total=False):
    """Updated properties for the private DNS namespace."""

    Description: Optional[ResourceDescription]
    Properties: Optional[PrivateDnsNamespacePropertiesChange]


class PublicDnsPropertiesMutableChange(TypedDict, total=False):
    """Updated DNS properties for the public DNS namespace."""

    SOA: SOAChange


class PublicDnsNamespacePropertiesChange(TypedDict, total=False):
    """Updated properties for the public DNS namespace."""

    DnsProperties: PublicDnsPropertiesMutableChange


class PublicDnsNamespaceChange(TypedDict, total=False):
    """Updated properties for the public DNS namespace."""

    Description: Optional[ResourceDescription]
    Properties: Optional[PublicDnsNamespacePropertiesChange]


class RegisterInstanceRequest(ServiceRequest):
    ServiceId: ResourceId
    InstanceId: InstanceId
    CreatorRequestId: Optional[ResourceId]
    Attributes: Attributes


class RegisterInstanceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class ServiceChange(TypedDict, total=False):
    """A complex type that contains changes to an existing service."""

    Description: Optional[ResourceDescription]
    DnsConfig: Optional[DnsConfigChange]
    HealthCheckConfig: Optional[HealthCheckConfig]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    Tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    TagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateHttpNamespaceRequest(ServiceRequest):
    Id: ResourceId
    UpdaterRequestId: Optional[ResourceId]
    Namespace: HttpNamespaceChange


class UpdateHttpNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class UpdateInstanceCustomHealthStatusRequest(ServiceRequest):
    ServiceId: ResourceId
    InstanceId: ResourceId
    Status: CustomHealthStatus


class UpdatePrivateDnsNamespaceRequest(ServiceRequest):
    Id: ResourceId
    UpdaterRequestId: Optional[ResourceId]
    Namespace: PrivateDnsNamespaceChange


class UpdatePrivateDnsNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class UpdatePublicDnsNamespaceRequest(ServiceRequest):
    Id: ResourceId
    UpdaterRequestId: Optional[ResourceId]
    Namespace: PublicDnsNamespaceChange


class UpdatePublicDnsNamespaceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class UpdateServiceRequest(ServiceRequest):
    Id: ResourceId
    Service: ServiceChange


class UpdateServiceResponse(TypedDict, total=False):
    OperationId: Optional[OperationId]


class ServicediscoveryApi:

    service = "servicediscovery"
    version = "2017-03-14"

    @handler("CreateHttpNamespace")
    def create_http_namespace(
        self,
        context: RequestContext,
        name: NamespaceNameHttp,
        creator_request_id: ResourceId = None,
        description: ResourceDescription = None,
        tags: TagList = None,
    ) -> CreateHttpNamespaceResponse:
        """Creates an HTTP namespace. Service instances registered using an HTTP
        namespace can be discovered using a ``DiscoverInstances`` request but
        can't be discovered using DNS.

        For the current quota on the number of namespaces that you can create
        using the same account, see `Cloud Map
        quotas <https://docs.aws.amazon.com/cloud-map/latest/dg/cloud-map-limits.html>`__
        in the *Cloud Map Developer Guide*.

        :param name: The name that you want to assign to this namespace.
        :param creator_request_id: A unique string that identifies the request and that allows failed
        ``CreateHttpNamespace`` requests to be retried without the risk of
        running the operation twice.
        :param description: A description for the namespace.
        :param tags: The tags to add to the namespace.
        :returns: CreateHttpNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceAlreadyExists:
        :raises ResourceLimitExceeded:
        :raises DuplicateRequest:
        :raises TooManyTagsException:
        """
        raise NotImplementedError

    @handler("CreatePrivateDnsNamespace")
    def create_private_dns_namespace(
        self,
        context: RequestContext,
        name: NamespaceNamePrivate,
        vpc: ResourceId,
        creator_request_id: ResourceId = None,
        description: ResourceDescription = None,
        tags: TagList = None,
        properties: PrivateDnsNamespaceProperties = None,
    ) -> CreatePrivateDnsNamespaceResponse:
        """Creates a private namespace based on DNS, which is visible only inside a
        specified Amazon VPC. The namespace defines your service naming scheme.
        For example, if you name your namespace ``example.com`` and name your
        service ``backend``, the resulting DNS name for the service is
        ``backend.example.com``. Service instances that are registered using a
        private DNS namespace can be discovered using either a
        ``DiscoverInstances`` request or using DNS. For the current quota on the
        number of namespaces that you can create using the same account, see
        `Cloud Map
        quotas <https://docs.aws.amazon.com/cloud-map/latest/dg/cloud-map-limits.html>`__
        in the *Cloud Map Developer Guide*.

        :param name: The name that you want to assign to this namespace.
        :param vpc: The ID of the Amazon VPC that you want to associate the namespace with.
        :param creator_request_id: A unique string that identifies the request and that allows failed
        ``CreatePrivateDnsNamespace`` requests to be retried without the risk of
        running the operation twice.
        :param description: A description for the namespace.
        :param tags: The tags to add to the namespace.
        :param properties: Properties for the private DNS namespace.
        :returns: CreatePrivateDnsNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceAlreadyExists:
        :raises ResourceLimitExceeded:
        :raises DuplicateRequest:
        :raises TooManyTagsException:
        """
        raise NotImplementedError

    @handler("CreatePublicDnsNamespace")
    def create_public_dns_namespace(
        self,
        context: RequestContext,
        name: NamespaceNamePublic,
        creator_request_id: ResourceId = None,
        description: ResourceDescription = None,
        tags: TagList = None,
        properties: PublicDnsNamespaceProperties = None,
    ) -> CreatePublicDnsNamespaceResponse:
        """Creates a public namespace based on DNS, which is visible on the
        internet. The namespace defines your service naming scheme. For example,
        if you name your namespace ``example.com`` and name your service
        ``backend``, the resulting DNS name for the service is
        ``backend.example.com``. You can discover instances that were registered
        with a public DNS namespace by using either a ``DiscoverInstances``
        request or using DNS. For the current quota on the number of namespaces
        that you can create using the same account, see `Cloud Map
        quotas <https://docs.aws.amazon.com/cloud-map/latest/dg/cloud-map-limits.html>`__
        in the *Cloud Map Developer Guide*.

        :param name: The name that you want to assign to this namespace.
        :param creator_request_id: A unique string that identifies the request and that allows failed
        ``CreatePublicDnsNamespace`` requests to be retried without the risk of
        running the operation twice.
        :param description: A description for the namespace.
        :param tags: The tags to add to the namespace.
        :param properties: Properties for the public DNS namespace.
        :returns: CreatePublicDnsNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceAlreadyExists:
        :raises ResourceLimitExceeded:
        :raises DuplicateRequest:
        :raises TooManyTagsException:
        """
        raise NotImplementedError

    @handler("CreateService", expand=False)
    def create_service(
        self, context: RequestContext, request: CreateServiceRequest
    ) -> CreateServiceResponse:
        """Creates a service. This action defines the configuration for the
        following entities:

        -  For public and private DNS namespaces, one of the following
           combinations of DNS records in Amazon Route 53:

           -  ``A``

           -  ``AAAA``

           -  ``A`` and ``AAAA``

           -  ``SRV``

           -  ``CNAME``

        -  Optionally, a health check

        After you create the service, you can submit a
        `RegisterInstance <https://docs.aws.amazon.com/cloud-map/latest/api/API_RegisterInstance.html>`__
        request, and Cloud Map uses the values in the configuration to create
        the specified entities.

        For the current quota on the number of instances that you can register
        using the same namespace and using the same service, see `Cloud Map
        quotas <https://docs.aws.amazon.com/cloud-map/latest/dg/cloud-map-limits.html>`__
        in the *Cloud Map Developer Guide*.

        :param name: The name that you want to assign to the service.
        :param namespace_id: The ID of the namespace that you want to use to create the service.
        :param creator_request_id: A unique string that identifies the request and that allows failed
        ``CreateService`` requests to be retried without the risk of running the
        operation twice.
        :param description: A description for the service.
        :param dns_config: A complex type that contains information about the Amazon Route 53
        records that you want Cloud Map to create when you register an instance.
        :param health_check_config: *Public DNS and HTTP namespaces only.
        :param health_check_custom_config: A complex type that contains information about an optional custom health
        check.
        :param tags: The tags to add to the service.
        :param type: If present, specifies that the service instances are only discoverable
        using the ``DiscoverInstances`` API operation.
        :returns: CreateServiceResponse
        :raises InvalidInput:
        :raises ResourceLimitExceeded:
        :raises NamespaceNotFound:
        :raises ServiceAlreadyExists:
        :raises TooManyTagsException:
        """
        raise NotImplementedError

    @handler("DeleteNamespace")
    def delete_namespace(self, context: RequestContext, id: ResourceId) -> DeleteNamespaceResponse:
        """Deletes a namespace from the current account. If the namespace still
        contains one or more services, the request fails.

        :param id: The ID of the namespace that you want to delete.
        :returns: DeleteNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceNotFound:
        :raises ResourceInUse:
        :raises DuplicateRequest:
        """
        raise NotImplementedError

    @handler("DeleteService")
    def delete_service(self, context: RequestContext, id: ResourceId) -> DeleteServiceResponse:
        """Deletes a specified service. If the service still contains one or more
        registered instances, the request fails.

        :param id: The ID of the service that you want to delete.
        :returns: DeleteServiceResponse
        :raises InvalidInput:
        :raises ServiceNotFound:
        :raises ResourceInUse:
        """
        raise NotImplementedError

    @handler("DeregisterInstance")
    def deregister_instance(
        self, context: RequestContext, service_id: ResourceId, instance_id: ResourceId
    ) -> DeregisterInstanceResponse:
        """Deletes the Amazon Route 53 DNS records and health check, if any, that
        Cloud Map created for the specified instance.

        :param service_id: The ID of the service that the instance is associated with.
        :param instance_id: The value that you specified for ``Id`` in the
        `RegisterInstance <https://docs.
        :returns: DeregisterInstanceResponse
        :raises DuplicateRequest:
        :raises InvalidInput:
        :raises InstanceNotFound:
        :raises ResourceInUse:
        :raises ServiceNotFound:
        """
        raise NotImplementedError

    @handler("DiscoverInstances")
    def discover_instances(
        self,
        context: RequestContext,
        namespace_name: NamespaceName,
        service_name: ServiceName,
        max_results: DiscoverMaxResults = None,
        query_parameters: Attributes = None,
        optional_parameters: Attributes = None,
        health_status: HealthStatusFilter = None,
    ) -> DiscoverInstancesResponse:
        """Discovers registered instances for a specified namespace and service.
        You can use ``DiscoverInstances`` to discover instances for any type of
        namespace. For public and private DNS namespaces, you can also use DNS
        queries to discover instances.

        :param namespace_name: The ``HttpName`` name of the namespace.
        :param service_name: The name of the service that you specified when you registered the
        instance.
        :param max_results: The maximum number of instances that you want Cloud Map to return in the
        response to a ``DiscoverInstances`` request.
        :param query_parameters: Filters to scope the results based on custom attributes for the instance
        (for example, ``{version=v1, az=1a}``).
        :param optional_parameters: Opportunistic filters to scope the results based on custom attributes.
        :param health_status: The health status of the instances that you want to discover.
        :returns: DiscoverInstancesResponse
        :raises ServiceNotFound:
        :raises NamespaceNotFound:
        :raises InvalidInput:
        :raises RequestLimitExceeded:
        """
        raise NotImplementedError

    @handler("GetInstance")
    def get_instance(
        self, context: RequestContext, service_id: ResourceId, instance_id: ResourceId
    ) -> GetInstanceResponse:
        """Gets information about a specified instance.

        :param service_id: The ID of the service that the instance is associated with.
        :param instance_id: The ID of the instance that you want to get information about.
        :returns: GetInstanceResponse
        :raises InstanceNotFound:
        :raises InvalidInput:
        :raises ServiceNotFound:
        """
        raise NotImplementedError

    @handler("GetInstancesHealthStatus")
    def get_instances_health_status(
        self,
        context: RequestContext,
        service_id: ResourceId,
        instances: InstanceIdList = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> GetInstancesHealthStatusResponse:
        """Gets the current health status (``Healthy``, ``Unhealthy``, or
        ``Unknown``) of one or more instances that are associated with a
        specified service.

        There's a brief delay between when you register an instance and when the
        health status for the instance is available.

        :param service_id: The ID of the service that the instance is associated with.
        :param instances: An array that contains the IDs of all the instances that you want to get
        the health status for.
        :param max_results: The maximum number of instances that you want Cloud Map to return in the
        response to a ``GetInstancesHealthStatus`` request.
        :param next_token: For the first ``GetInstancesHealthStatus`` request, omit this value.
        :returns: GetInstancesHealthStatusResponse
        :raises InstanceNotFound:
        :raises InvalidInput:
        :raises ServiceNotFound:
        """
        raise NotImplementedError

    @handler("GetNamespace")
    def get_namespace(self, context: RequestContext, id: ResourceId) -> GetNamespaceResponse:
        """Gets information about a namespace.

        :param id: The ID of the namespace that you want to get information about.
        :returns: GetNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceNotFound:
        """
        raise NotImplementedError

    @handler("GetOperation")
    def get_operation(
        self, context: RequestContext, operation_id: ResourceId
    ) -> GetOperationResponse:
        """Gets information about any operation that returns an operation ID in the
        response, such as a ``CreateService`` request.

        To get a list of operations that match specified criteria, see
        `ListOperations <https://docs.aws.amazon.com/cloud-map/latest/api/API_ListOperations.html>`__.

        :param operation_id: The ID of the operation that you want to get more information about.
        :returns: GetOperationResponse
        :raises InvalidInput:
        :raises OperationNotFound:
        """
        raise NotImplementedError

    @handler("GetService")
    def get_service(self, context: RequestContext, id: ResourceId) -> GetServiceResponse:
        """Gets the settings for a specified service.

        :param id: The ID of the service that you want to get settings for.
        :returns: GetServiceResponse
        :raises InvalidInput:
        :raises ServiceNotFound:
        """
        raise NotImplementedError

    @handler("ListInstances")
    def list_instances(
        self,
        context: RequestContext,
        service_id: ResourceId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListInstancesResponse:
        """Lists summary information about the instances that you registered by
        using a specified service.

        :param service_id: The ID of the service that you want to list instances for.
        :param next_token: For the first ``ListInstances`` request, omit this value.
        :param max_results: The maximum number of instances that you want Cloud Map to return in the
        response to a ``ListInstances`` request.
        :returns: ListInstancesResponse
        :raises ServiceNotFound:
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("ListNamespaces")
    def list_namespaces(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        filters: NamespaceFilters = None,
    ) -> ListNamespacesResponse:
        """Lists summary information about the namespaces that were created by the
        current account.

        :param next_token: For the first ``ListNamespaces`` request, omit this value.
        :param max_results: The maximum number of namespaces that you want Cloud Map to return in
        the response to a ``ListNamespaces`` request.
        :param filters: A complex type that contains specifications for the namespaces that you
        want to list.
        :returns: ListNamespacesResponse
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("ListOperations")
    def list_operations(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        filters: OperationFilters = None,
    ) -> ListOperationsResponse:
        """Lists operations that match the criteria that you specify.

        :param next_token: For the first ``ListOperations`` request, omit this value.
        :param max_results: The maximum number of items that you want Cloud Map to return in the
        response to a ``ListOperations`` request.
        :param filters: A complex type that contains specifications for the operations that you
        want to list, for example, operations that you started between a
        specified start date and end date.
        :returns: ListOperationsResponse
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("ListServices")
    def list_services(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        filters: ServiceFilters = None,
    ) -> ListServicesResponse:
        """Lists summary information for all the services that are associated with
        one or more specified namespaces.

        :param next_token: For the first ``ListServices`` request, omit this value.
        :param max_results: The maximum number of services that you want Cloud Map to return in the
        response to a ``ListServices`` request.
        :param filters: A complex type that contains specifications for the namespaces that you
        want to list services for.
        :returns: ListServicesResponse
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName
    ) -> ListTagsForResourceResponse:
        """Lists tags for the specified resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to retrieve
        tags for.
        :returns: ListTagsForResourceResponse
        :raises ResourceNotFoundException:
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("RegisterInstance")
    def register_instance(
        self,
        context: RequestContext,
        service_id: ResourceId,
        instance_id: InstanceId,
        attributes: Attributes,
        creator_request_id: ResourceId = None,
    ) -> RegisterInstanceResponse:
        """Creates or updates one or more records and, optionally, creates a health
        check based on the settings in a specified service. When you submit a
        ``RegisterInstance`` request, the following occurs:

        -  For each DNS record that you define in the service that's specified
           by ``ServiceId``, a record is created or updated in the hosted zone
           that's associated with the corresponding namespace.

        -  If the service includes ``HealthCheckConfig``, a health check is
           created based on the settings in the health check configuration.

        -  The health check, if any, is associated with each of the new or
           updated records.

        One ``RegisterInstance`` request must complete before you can submit
        another request and specify the same service ID and instance ID.

        For more information, see
        `CreateService <https://docs.aws.amazon.com/cloud-map/latest/api/API_CreateService.html>`__.

        When Cloud Map receives a DNS query for the specified DNS name, it
        returns the applicable value:

        -  **If the health check is healthy**: returns all the records

        -  **If the health check is unhealthy**: returns the applicable value
           for the last healthy instance

        -  **If you didn't specify a health check configuration**: returns all
           the records

        For the current quota on the number of instances that you can register
        using the same namespace and using the same service, see `Cloud Map
        quotas <https://docs.aws.amazon.com/cloud-map/latest/dg/cloud-map-limits.html>`__
        in the *Cloud Map Developer Guide*.

        :param service_id: The ID of the service that you want to use for settings for the
        instance.
        :param instance_id: An identifier that you want to associate with the instance.
        :param attributes: A string map that contains the following information for the service
        that you specify in ``ServiceId``:

        -  The attributes that apply to the records that are defined in the
           service.
        :param creator_request_id: A unique string that identifies the request and that allows failed
        ``RegisterInstance`` requests to be retried without the risk of
        executing the operation twice.
        :returns: RegisterInstanceResponse
        :raises DuplicateRequest:
        :raises InvalidInput:
        :raises ResourceInUse:
        :raises ResourceLimitExceeded:
        :raises ServiceNotFound:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceResponse:
        """Adds one or more tags to the specified resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to retrieve
        tags for.
        :param tags: The tags to add to the specified resource.
        :returns: TagResourceResponse
        :raises ResourceNotFoundException:
        :raises TooManyTagsException:
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes one or more tags from the specified resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to retrieve
        tags for.
        :param tag_keys: The tag keys to remove from the specified resource.
        :returns: UntagResourceResponse
        :raises ResourceNotFoundException:
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("UpdateHttpNamespace")
    def update_http_namespace(
        self,
        context: RequestContext,
        id: ResourceId,
        namespace: HttpNamespaceChange,
        updater_request_id: ResourceId = None,
    ) -> UpdateHttpNamespaceResponse:
        """Updates an HTTP namespace.

        :param id: The ID of the namespace that you want to update.
        :param namespace: Updated properties for the the HTTP namespace.
        :param updater_request_id: A unique string that identifies the request and that allows failed
        ``UpdateHttpNamespace`` requests to be retried without the risk of
        running the operation twice.
        :returns: UpdateHttpNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceNotFound:
        :raises ResourceInUse:
        :raises DuplicateRequest:
        """
        raise NotImplementedError

    @handler("UpdateInstanceCustomHealthStatus")
    def update_instance_custom_health_status(
        self,
        context: RequestContext,
        service_id: ResourceId,
        instance_id: ResourceId,
        status: CustomHealthStatus,
    ) -> None:
        """Submits a request to change the health status of a custom health check
        to healthy or unhealthy.

        You can use ``UpdateInstanceCustomHealthStatus`` to change the status
        only for custom health checks, which you define using
        ``HealthCheckCustomConfig`` when you create a service. You can't use it
        to change the status for Route 53 health checks, which you define using
        ``HealthCheckConfig``.

        For more information, see
        `HealthCheckCustomConfig <https://docs.aws.amazon.com/cloud-map/latest/api/API_HealthCheckCustomConfig.html>`__.

        :param service_id: The ID of the service that includes the configuration for the custom
        health check that you want to change the status for.
        :param instance_id: The ID of the instance that you want to change the health status for.
        :param status: The new status of the instance, ``HEALTHY`` or ``UNHEALTHY``.
        :raises InstanceNotFound:
        :raises ServiceNotFound:
        :raises CustomHealthNotFound:
        :raises InvalidInput:
        """
        raise NotImplementedError

    @handler("UpdatePrivateDnsNamespace")
    def update_private_dns_namespace(
        self,
        context: RequestContext,
        id: ResourceId,
        namespace: PrivateDnsNamespaceChange,
        updater_request_id: ResourceId = None,
    ) -> UpdatePrivateDnsNamespaceResponse:
        """Updates a private DNS namespace.

        :param id: The ID of the namespace that you want to update.
        :param namespace: Updated properties for the private DNS namespace.
        :param updater_request_id: A unique string that identifies the request and that allows failed
        ``UpdatePrivateDnsNamespace`` requests to be retried without the risk of
        running the operation twice.
        :returns: UpdatePrivateDnsNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceNotFound:
        :raises ResourceInUse:
        :raises DuplicateRequest:
        """
        raise NotImplementedError

    @handler("UpdatePublicDnsNamespace")
    def update_public_dns_namespace(
        self,
        context: RequestContext,
        id: ResourceId,
        namespace: PublicDnsNamespaceChange,
        updater_request_id: ResourceId = None,
    ) -> UpdatePublicDnsNamespaceResponse:
        """Updates a public DNS namespace.

        :param id: The ID of the namespace being updated.
        :param namespace: Updated properties for the public DNS namespace.
        :param updater_request_id: A unique string that identifies the request and that allows failed
        ``UpdatePublicDnsNamespace`` requests to be retried without the risk of
        running the operation twice.
        :returns: UpdatePublicDnsNamespaceResponse
        :raises InvalidInput:
        :raises NamespaceNotFound:
        :raises ResourceInUse:
        :raises DuplicateRequest:
        """
        raise NotImplementedError

    @handler("UpdateService")
    def update_service(
        self, context: RequestContext, id: ResourceId, service: ServiceChange
    ) -> UpdateServiceResponse:
        """Submits a request to perform the following operations:

        -  Update the TTL setting for existing ``DnsRecords`` configurations

        -  Add, update, or delete ``HealthCheckConfig`` for a specified service

           You can't add, update, or delete a ``HealthCheckCustomConfig``
           configuration.

        For public and private DNS namespaces, note the following:

        -  If you omit any existing ``DnsRecords`` or ``HealthCheckConfig``
           configurations from an ``UpdateService`` request, the configurations
           are deleted from the service.

        -  If you omit an existing ``HealthCheckCustomConfig`` configuration
           from an ``UpdateService`` request, the configuration isn't deleted
           from the service.

        When you update settings for a service, Cloud Map also updates the
        corresponding settings in all the records and health checks that were
        created by using the specified service.

        :param id: The ID of the service that you want to update.
        :param service: A complex type that contains the new settings for the service.
        :returns: UpdateServiceResponse
        :raises DuplicateRequest:
        :raises InvalidInput:
        :raises ServiceNotFound:
        """
        raise NotImplementedError
