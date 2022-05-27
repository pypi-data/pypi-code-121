import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccessLogEnabled = bool
AccessLogInterval = int
AccessLogPrefix = str
AccessPointName = str
AccessPointPort = int
AdditionalAttributeKey = str
AdditionalAttributeValue = str
AttributeName = str
AttributeType = str
AttributeValue = str
AvailabilityZone = str
Cardinality = str
ConnectionDrainingEnabled = bool
ConnectionDrainingTimeout = int
CookieName = str
CrossZoneLoadBalancingEnabled = bool
DNSName = str
DefaultValue = str
Description = str
EndPointPort = int
HealthCheckInterval = int
HealthCheckTarget = str
HealthCheckTimeout = int
HealthyThreshold = int
IdleTimeout = int
InstanceId = str
InstancePort = int
LoadBalancerScheme = str
Marker = str
Max = str
Name = str
PageSize = int
PolicyName = str
PolicyTypeName = str
Protocol = str
ReasonCode = str
S3BucketName = str
SSLCertificateId = str
SecurityGroupId = str
SecurityGroupName = str
SecurityGroupOwnerAlias = str
State = str
SubnetId = str
TagKey = str
TagValue = str
UnhealthyThreshold = int
VPCId = str


class AccessPointNotFoundException(ServiceException):
    """The specified load balancer does not exist."""


class CertificateNotFoundException(ServiceException):
    """The specified ARN does not refer to a valid SSL certificate in AWS
    Identity and Access Management (IAM) or AWS Certificate Manager (ACM).
    Note that if you recently uploaded the certificate to IAM, this error
    might indicate that the certificate is not fully available yet.
    """


class DependencyThrottleException(ServiceException):
    """A request made by Elastic Load Balancing to another service exceeds the
    maximum request rate permitted for your account.
    """


class DuplicateAccessPointNameException(ServiceException):
    """The specified load balancer name already exists for this account."""


class DuplicateListenerException(ServiceException):
    """A listener already exists for the specified load balancer name and port,
    but with a different instance port, protocol, or SSL certificate.
    """


class DuplicatePolicyNameException(ServiceException):
    """A policy with the specified name already exists for this load balancer."""


class DuplicateTagKeysException(ServiceException):
    """A tag key was specified more than once."""


class InvalidConfigurationRequestException(ServiceException):
    """The requested configuration change is not valid."""


class InvalidEndPointException(ServiceException):
    """The specified endpoint is not valid."""


class InvalidSchemeException(ServiceException):
    """The specified value for the schema is not valid. You can only specify a
    scheme for load balancers in a VPC.
    """


class InvalidSecurityGroupException(ServiceException):
    """One or more of the specified security groups do not exist."""


class InvalidSubnetException(ServiceException):
    """The specified VPC has no associated Internet gateway."""


class ListenerNotFoundException(ServiceException):
    """The load balancer does not have a listener configured at the specified
    port.
    """


class LoadBalancerAttributeNotFoundException(ServiceException):
    """The specified load balancer attribute does not exist."""


class OperationNotPermittedException(ServiceException):
    """This operation is not allowed."""


class PolicyNotFoundException(ServiceException):
    """One or more of the specified policies do not exist."""


class PolicyTypeNotFoundException(ServiceException):
    """One or more of the specified policy types do not exist."""


class SubnetNotFoundException(ServiceException):
    """One or more of the specified subnets do not exist."""


class TooManyAccessPointsException(ServiceException):
    """The quota for the number of load balancers has been reached."""


class TooManyPoliciesException(ServiceException):
    """The quota for the number of policies for this load balancer has been
    reached.
    """


class TooManyTagsException(ServiceException):
    """The quota for the number of tags that can be assigned to a load balancer
    has been reached.
    """


class UnsupportedProtocolException(ServiceException):
    """The specified protocol or signature version is not supported."""


class AccessLog(TypedDict, total=False):
    """Information about the ``AccessLog`` attribute."""

    Enabled: AccessLogEnabled
    S3BucketName: Optional[S3BucketName]
    EmitInterval: Optional[AccessLogInterval]
    S3BucketPrefix: Optional[AccessLogPrefix]


AvailabilityZones = List[AvailabilityZone]


class AddAvailabilityZonesInput(ServiceRequest):
    """Contains the parameters for EnableAvailabilityZonesForLoadBalancer."""

    LoadBalancerName: AccessPointName
    AvailabilityZones: AvailabilityZones


class AddAvailabilityZonesOutput(TypedDict, total=False):
    """Contains the output of EnableAvailabilityZonesForLoadBalancer."""

    AvailabilityZones: Optional[AvailabilityZones]


class Tag(TypedDict, total=False):
    """Information about a tag."""

    Key: TagKey
    Value: Optional[TagValue]


TagList = List[Tag]
LoadBalancerNames = List[AccessPointName]


class AddTagsInput(ServiceRequest):
    """Contains the parameters for AddTags."""

    LoadBalancerNames: LoadBalancerNames
    Tags: TagList


class AddTagsOutput(TypedDict, total=False):
    """Contains the output of AddTags."""


class AdditionalAttribute(TypedDict, total=False):
    """Information about additional load balancer attributes."""

    Key: Optional[AdditionalAttributeKey]
    Value: Optional[AdditionalAttributeValue]


AdditionalAttributes = List[AdditionalAttribute]


class AppCookieStickinessPolicy(TypedDict, total=False):
    """Information about a policy for application-controlled session
    stickiness.
    """

    PolicyName: Optional[PolicyName]
    CookieName: Optional[CookieName]


AppCookieStickinessPolicies = List[AppCookieStickinessPolicy]
SecurityGroups = List[SecurityGroupId]


class ApplySecurityGroupsToLoadBalancerInput(ServiceRequest):
    """Contains the parameters for ApplySecurityGroupsToLoadBalancer."""

    LoadBalancerName: AccessPointName
    SecurityGroups: SecurityGroups


class ApplySecurityGroupsToLoadBalancerOutput(TypedDict, total=False):
    """Contains the output of ApplySecurityGroupsToLoadBalancer."""

    SecurityGroups: Optional[SecurityGroups]


Subnets = List[SubnetId]


class AttachLoadBalancerToSubnetsInput(ServiceRequest):
    """Contains the parameters for AttachLoaBalancerToSubnets."""

    LoadBalancerName: AccessPointName
    Subnets: Subnets


class AttachLoadBalancerToSubnetsOutput(TypedDict, total=False):
    """Contains the output of AttachLoadBalancerToSubnets."""

    Subnets: Optional[Subnets]


PolicyNames = List[PolicyName]


class BackendServerDescription(TypedDict, total=False):
    """Information about the configuration of an EC2 instance."""

    InstancePort: Optional[InstancePort]
    PolicyNames: Optional[PolicyNames]


BackendServerDescriptions = List[BackendServerDescription]


class HealthCheck(TypedDict, total=False):
    """Information about a health check."""

    Target: HealthCheckTarget
    Interval: HealthCheckInterval
    Timeout: HealthCheckTimeout
    UnhealthyThreshold: UnhealthyThreshold
    HealthyThreshold: HealthyThreshold


class ConfigureHealthCheckInput(ServiceRequest):
    """Contains the parameters for ConfigureHealthCheck."""

    LoadBalancerName: AccessPointName
    HealthCheck: HealthCheck


class ConfigureHealthCheckOutput(TypedDict, total=False):
    """Contains the output of ConfigureHealthCheck."""

    HealthCheck: Optional[HealthCheck]


class ConnectionDraining(TypedDict, total=False):
    """Information about the ``ConnectionDraining`` attribute."""

    Enabled: ConnectionDrainingEnabled
    Timeout: Optional[ConnectionDrainingTimeout]


class ConnectionSettings(TypedDict, total=False):
    """Information about the ``ConnectionSettings`` attribute."""

    IdleTimeout: IdleTimeout


CookieExpirationPeriod = int


class Listener(TypedDict, total=False):
    """Information about a listener.

    For information about the protocols and the ports supported by Elastic
    Load Balancing, see `Listeners for Your Classic Load
    Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-listener-config.html>`__
    in the *Classic Load Balancers Guide*.
    """

    Protocol: Protocol
    LoadBalancerPort: AccessPointPort
    InstanceProtocol: Optional[Protocol]
    InstancePort: InstancePort
    SSLCertificateId: Optional[SSLCertificateId]


Listeners = List[Listener]


class CreateAccessPointInput(ServiceRequest):
    """Contains the parameters for CreateLoadBalancer."""

    LoadBalancerName: AccessPointName
    Listeners: Listeners
    AvailabilityZones: Optional[AvailabilityZones]
    Subnets: Optional[Subnets]
    SecurityGroups: Optional[SecurityGroups]
    Scheme: Optional[LoadBalancerScheme]
    Tags: Optional[TagList]


class CreateAccessPointOutput(TypedDict, total=False):
    """Contains the output for CreateLoadBalancer."""

    DNSName: Optional[DNSName]


class CreateAppCookieStickinessPolicyInput(ServiceRequest):
    """Contains the parameters for CreateAppCookieStickinessPolicy."""

    LoadBalancerName: AccessPointName
    PolicyName: PolicyName
    CookieName: CookieName


class CreateAppCookieStickinessPolicyOutput(TypedDict, total=False):
    """Contains the output for CreateAppCookieStickinessPolicy."""


class CreateLBCookieStickinessPolicyInput(ServiceRequest):
    """Contains the parameters for CreateLBCookieStickinessPolicy."""

    LoadBalancerName: AccessPointName
    PolicyName: PolicyName
    CookieExpirationPeriod: Optional[CookieExpirationPeriod]


class CreateLBCookieStickinessPolicyOutput(TypedDict, total=False):
    """Contains the output for CreateLBCookieStickinessPolicy."""


class CreateLoadBalancerListenerInput(ServiceRequest):
    """Contains the parameters for CreateLoadBalancerListeners."""

    LoadBalancerName: AccessPointName
    Listeners: Listeners


class CreateLoadBalancerListenerOutput(TypedDict, total=False):
    """Contains the parameters for CreateLoadBalancerListener."""


class PolicyAttribute(TypedDict, total=False):
    """Information about a policy attribute."""

    AttributeName: Optional[AttributeName]
    AttributeValue: Optional[AttributeValue]


PolicyAttributes = List[PolicyAttribute]


class CreateLoadBalancerPolicyInput(ServiceRequest):
    """Contains the parameters for CreateLoadBalancerPolicy."""

    LoadBalancerName: AccessPointName
    PolicyName: PolicyName
    PolicyTypeName: PolicyTypeName
    PolicyAttributes: Optional[PolicyAttributes]


class CreateLoadBalancerPolicyOutput(TypedDict, total=False):
    """Contains the output of CreateLoadBalancerPolicy."""


CreatedTime = datetime


class CrossZoneLoadBalancing(TypedDict, total=False):
    """Information about the ``CrossZoneLoadBalancing`` attribute."""

    Enabled: CrossZoneLoadBalancingEnabled


class DeleteAccessPointInput(ServiceRequest):
    """Contains the parameters for DeleteLoadBalancer."""

    LoadBalancerName: AccessPointName


class DeleteAccessPointOutput(TypedDict, total=False):
    """Contains the output of DeleteLoadBalancer."""


Ports = List[AccessPointPort]


class DeleteLoadBalancerListenerInput(ServiceRequest):
    """Contains the parameters for DeleteLoadBalancerListeners."""

    LoadBalancerName: AccessPointName
    LoadBalancerPorts: Ports


class DeleteLoadBalancerListenerOutput(TypedDict, total=False):
    """Contains the output of DeleteLoadBalancerListeners."""


class DeleteLoadBalancerPolicyInput(ServiceRequest):
    """Contains the parameters for DeleteLoadBalancerPolicy."""

    LoadBalancerName: AccessPointName
    PolicyName: PolicyName


class DeleteLoadBalancerPolicyOutput(TypedDict, total=False):
    """Contains the output of DeleteLoadBalancerPolicy."""


class Instance(TypedDict, total=False):
    """The ID of an EC2 instance."""

    InstanceId: Optional[InstanceId]


Instances = List[Instance]


class DeregisterEndPointsInput(ServiceRequest):
    """Contains the parameters for DeregisterInstancesFromLoadBalancer."""

    LoadBalancerName: AccessPointName
    Instances: Instances


class DeregisterEndPointsOutput(TypedDict, total=False):
    """Contains the output of DeregisterInstancesFromLoadBalancer."""

    Instances: Optional[Instances]


class DescribeAccessPointsInput(ServiceRequest):
    """Contains the parameters for DescribeLoadBalancers."""

    LoadBalancerNames: Optional[LoadBalancerNames]
    Marker: Optional[Marker]
    PageSize: Optional[PageSize]


class SourceSecurityGroup(TypedDict, total=False):
    """Information about a source security group."""

    OwnerAlias: Optional[SecurityGroupOwnerAlias]
    GroupName: Optional[SecurityGroupName]


class LBCookieStickinessPolicy(TypedDict, total=False):
    """Information about a policy for duration-based session stickiness."""

    PolicyName: Optional[PolicyName]
    CookieExpirationPeriod: Optional[CookieExpirationPeriod]


LBCookieStickinessPolicies = List[LBCookieStickinessPolicy]


class Policies(TypedDict, total=False):
    """The policies for a load balancer."""

    AppCookieStickinessPolicies: Optional[AppCookieStickinessPolicies]
    LBCookieStickinessPolicies: Optional[LBCookieStickinessPolicies]
    OtherPolicies: Optional[PolicyNames]


class ListenerDescription(TypedDict, total=False):
    """The policies enabled for a listener."""

    Listener: Optional[Listener]
    PolicyNames: Optional[PolicyNames]


ListenerDescriptions = List[ListenerDescription]


class LoadBalancerDescription(TypedDict, total=False):
    """Information about a load balancer."""

    LoadBalancerName: Optional[AccessPointName]
    DNSName: Optional[DNSName]
    CanonicalHostedZoneName: Optional[DNSName]
    CanonicalHostedZoneNameID: Optional[DNSName]
    ListenerDescriptions: Optional[ListenerDescriptions]
    Policies: Optional[Policies]
    BackendServerDescriptions: Optional[BackendServerDescriptions]
    AvailabilityZones: Optional[AvailabilityZones]
    Subnets: Optional[Subnets]
    VPCId: Optional[VPCId]
    Instances: Optional[Instances]
    HealthCheck: Optional[HealthCheck]
    SourceSecurityGroup: Optional[SourceSecurityGroup]
    SecurityGroups: Optional[SecurityGroups]
    CreatedTime: Optional[CreatedTime]
    Scheme: Optional[LoadBalancerScheme]


LoadBalancerDescriptions = List[LoadBalancerDescription]


class DescribeAccessPointsOutput(TypedDict, total=False):
    """Contains the parameters for DescribeLoadBalancers."""

    LoadBalancerDescriptions: Optional[LoadBalancerDescriptions]
    NextMarker: Optional[Marker]


class DescribeAccountLimitsInput(ServiceRequest):
    Marker: Optional[Marker]
    PageSize: Optional[PageSize]


class Limit(TypedDict, total=False):
    """Information about an Elastic Load Balancing resource limit for your AWS
    account.
    """

    Name: Optional[Name]
    Max: Optional[Max]


Limits = List[Limit]


class DescribeAccountLimitsOutput(TypedDict, total=False):
    Limits: Optional[Limits]
    NextMarker: Optional[Marker]


class DescribeEndPointStateInput(ServiceRequest):
    """Contains the parameters for DescribeInstanceHealth."""

    LoadBalancerName: AccessPointName
    Instances: Optional[Instances]


class InstanceState(TypedDict, total=False):
    """Information about the state of an EC2 instance."""

    InstanceId: Optional[InstanceId]
    State: Optional[State]
    ReasonCode: Optional[ReasonCode]
    Description: Optional[Description]


InstanceStates = List[InstanceState]


class DescribeEndPointStateOutput(TypedDict, total=False):
    """Contains the output for DescribeInstanceHealth."""

    InstanceStates: Optional[InstanceStates]


class DescribeLoadBalancerAttributesInput(ServiceRequest):
    """Contains the parameters for DescribeLoadBalancerAttributes."""

    LoadBalancerName: AccessPointName


class LoadBalancerAttributes(TypedDict, total=False):
    """The attributes for a load balancer."""

    CrossZoneLoadBalancing: Optional[CrossZoneLoadBalancing]
    AccessLog: Optional[AccessLog]
    ConnectionDraining: Optional[ConnectionDraining]
    ConnectionSettings: Optional[ConnectionSettings]
    AdditionalAttributes: Optional[AdditionalAttributes]


class DescribeLoadBalancerAttributesOutput(TypedDict, total=False):
    """Contains the output of DescribeLoadBalancerAttributes."""

    LoadBalancerAttributes: Optional[LoadBalancerAttributes]


class DescribeLoadBalancerPoliciesInput(ServiceRequest):
    """Contains the parameters for DescribeLoadBalancerPolicies."""

    LoadBalancerName: Optional[AccessPointName]
    PolicyNames: Optional[PolicyNames]


class PolicyAttributeDescription(TypedDict, total=False):
    """Information about a policy attribute."""

    AttributeName: Optional[AttributeName]
    AttributeValue: Optional[AttributeValue]


PolicyAttributeDescriptions = List[PolicyAttributeDescription]


class PolicyDescription(TypedDict, total=False):
    """Information about a policy."""

    PolicyName: Optional[PolicyName]
    PolicyTypeName: Optional[PolicyTypeName]
    PolicyAttributeDescriptions: Optional[PolicyAttributeDescriptions]


PolicyDescriptions = List[PolicyDescription]


class DescribeLoadBalancerPoliciesOutput(TypedDict, total=False):
    """Contains the output of DescribeLoadBalancerPolicies."""

    PolicyDescriptions: Optional[PolicyDescriptions]


PolicyTypeNames = List[PolicyTypeName]


class DescribeLoadBalancerPolicyTypesInput(ServiceRequest):
    """Contains the parameters for DescribeLoadBalancerPolicyTypes."""

    PolicyTypeNames: Optional[PolicyTypeNames]


class PolicyAttributeTypeDescription(TypedDict, total=False):
    """Information about a policy attribute type."""

    AttributeName: Optional[AttributeName]
    AttributeType: Optional[AttributeType]
    Description: Optional[Description]
    DefaultValue: Optional[DefaultValue]
    Cardinality: Optional[Cardinality]


PolicyAttributeTypeDescriptions = List[PolicyAttributeTypeDescription]


class PolicyTypeDescription(TypedDict, total=False):
    """Information about a policy type."""

    PolicyTypeName: Optional[PolicyTypeName]
    Description: Optional[Description]
    PolicyAttributeTypeDescriptions: Optional[PolicyAttributeTypeDescriptions]


PolicyTypeDescriptions = List[PolicyTypeDescription]


class DescribeLoadBalancerPolicyTypesOutput(TypedDict, total=False):
    """Contains the output of DescribeLoadBalancerPolicyTypes."""

    PolicyTypeDescriptions: Optional[PolicyTypeDescriptions]


LoadBalancerNamesMax20 = List[AccessPointName]


class DescribeTagsInput(ServiceRequest):
    """Contains the parameters for DescribeTags."""

    LoadBalancerNames: LoadBalancerNamesMax20


class TagDescription(TypedDict, total=False):
    """The tags associated with a load balancer."""

    LoadBalancerName: Optional[AccessPointName]
    Tags: Optional[TagList]


TagDescriptions = List[TagDescription]


class DescribeTagsOutput(TypedDict, total=False):
    """Contains the output for DescribeTags."""

    TagDescriptions: Optional[TagDescriptions]


class DetachLoadBalancerFromSubnetsInput(ServiceRequest):
    """Contains the parameters for DetachLoadBalancerFromSubnets."""

    LoadBalancerName: AccessPointName
    Subnets: Subnets


class DetachLoadBalancerFromSubnetsOutput(TypedDict, total=False):
    """Contains the output of DetachLoadBalancerFromSubnets."""

    Subnets: Optional[Subnets]


class ModifyLoadBalancerAttributesInput(ServiceRequest):
    """Contains the parameters for ModifyLoadBalancerAttributes."""

    LoadBalancerName: AccessPointName
    LoadBalancerAttributes: LoadBalancerAttributes


class ModifyLoadBalancerAttributesOutput(TypedDict, total=False):
    """Contains the output of ModifyLoadBalancerAttributes."""

    LoadBalancerName: Optional[AccessPointName]
    LoadBalancerAttributes: Optional[LoadBalancerAttributes]


class RegisterEndPointsInput(ServiceRequest):
    """Contains the parameters for RegisterInstancesWithLoadBalancer."""

    LoadBalancerName: AccessPointName
    Instances: Instances


class RegisterEndPointsOutput(TypedDict, total=False):
    """Contains the output of RegisterInstancesWithLoadBalancer."""

    Instances: Optional[Instances]


class RemoveAvailabilityZonesInput(ServiceRequest):
    """Contains the parameters for DisableAvailabilityZonesForLoadBalancer."""

    LoadBalancerName: AccessPointName
    AvailabilityZones: AvailabilityZones


class RemoveAvailabilityZonesOutput(TypedDict, total=False):
    """Contains the output for DisableAvailabilityZonesForLoadBalancer."""

    AvailabilityZones: Optional[AvailabilityZones]


class TagKeyOnly(TypedDict, total=False):
    """The key of a tag."""

    Key: Optional[TagKey]


TagKeyList = List[TagKeyOnly]


class RemoveTagsInput(ServiceRequest):
    """Contains the parameters for RemoveTags."""

    LoadBalancerNames: LoadBalancerNames
    Tags: TagKeyList


class RemoveTagsOutput(TypedDict, total=False):
    """Contains the output of RemoveTags."""


class SetLoadBalancerListenerSSLCertificateInput(ServiceRequest):
    """Contains the parameters for SetLoadBalancerListenerSSLCertificate."""

    LoadBalancerName: AccessPointName
    LoadBalancerPort: AccessPointPort
    SSLCertificateId: SSLCertificateId


class SetLoadBalancerListenerSSLCertificateOutput(TypedDict, total=False):
    """Contains the output of SetLoadBalancerListenerSSLCertificate."""


class SetLoadBalancerPoliciesForBackendServerInput(ServiceRequest):
    """Contains the parameters for SetLoadBalancerPoliciesForBackendServer."""

    LoadBalancerName: AccessPointName
    InstancePort: EndPointPort
    PolicyNames: PolicyNames


class SetLoadBalancerPoliciesForBackendServerOutput(TypedDict, total=False):
    """Contains the output of SetLoadBalancerPoliciesForBackendServer."""


class SetLoadBalancerPoliciesOfListenerInput(ServiceRequest):
    """Contains the parameters for SetLoadBalancePoliciesOfListener."""

    LoadBalancerName: AccessPointName
    LoadBalancerPort: AccessPointPort
    PolicyNames: PolicyNames


class SetLoadBalancerPoliciesOfListenerOutput(TypedDict, total=False):
    """Contains the output of SetLoadBalancePoliciesOfListener."""


class ElbApi:

    service = "elb"
    version = "2012-06-01"

    @handler("AddTags")
    def add_tags(
        self, context: RequestContext, load_balancer_names: LoadBalancerNames, tags: TagList
    ) -> AddTagsOutput:
        """Adds the specified tags to the specified load balancer. Each load
        balancer can have a maximum of 10 tags.

        Each tag consists of a key and an optional value. If a tag with the same
        key is already associated with the load balancer, ``AddTags`` updates
        its value.

        For more information, see `Tag Your Classic Load
        Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/add-remove-tags.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_names: The name of the load balancer.
        :param tags: The tags.
        :returns: AddTagsOutput
        :raises AccessPointNotFoundException:
        :raises TooManyTagsException:
        :raises DuplicateTagKeysException:
        """
        raise NotImplementedError

    @handler("ApplySecurityGroupsToLoadBalancer")
    def apply_security_groups_to_load_balancer(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        security_groups: SecurityGroups,
    ) -> ApplySecurityGroupsToLoadBalancerOutput:
        """Associates one or more security groups with your load balancer in a
        virtual private cloud (VPC). The specified security groups override the
        previously associated security groups.

        For more information, see `Security Groups for Load Balancers in a
        VPC <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-security-groups.html#elb-vpc-security-groups>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param security_groups: The IDs of the security groups to associate with the load balancer.
        :returns: ApplySecurityGroupsToLoadBalancerOutput
        :raises AccessPointNotFoundException:
        :raises InvalidConfigurationRequestException:
        :raises InvalidSecurityGroupException:
        """
        raise NotImplementedError

    @handler("AttachLoadBalancerToSubnets")
    def attach_load_balancer_to_subnets(
        self, context: RequestContext, load_balancer_name: AccessPointName, subnets: Subnets
    ) -> AttachLoadBalancerToSubnetsOutput:
        """Adds one or more subnets to the set of configured subnets for the
        specified load balancer.

        The load balancer evenly distributes requests across all registered
        subnets. For more information, see `Add or Remove Subnets for Your Load
        Balancer in a
        VPC <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-manage-subnets.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param subnets: The IDs of the subnets to add.
        :returns: AttachLoadBalancerToSubnetsOutput
        :raises AccessPointNotFoundException:
        :raises InvalidConfigurationRequestException:
        :raises SubnetNotFoundException:
        :raises InvalidSubnetException:
        """
        raise NotImplementedError

    @handler("ConfigureHealthCheck")
    def configure_health_check(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        health_check: HealthCheck,
    ) -> ConfigureHealthCheckOutput:
        """Specifies the health check settings to use when evaluating the health
        state of your EC2 instances.

        For more information, see `Configure Health Checks for Your Load
        Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-healthchecks.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param health_check: The configuration information.
        :returns: ConfigureHealthCheckOutput
        :raises AccessPointNotFoundException:
        """
        raise NotImplementedError

    @handler("CreateAppCookieStickinessPolicy")
    def create_app_cookie_stickiness_policy(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        policy_name: PolicyName,
        cookie_name: CookieName,
    ) -> CreateAppCookieStickinessPolicyOutput:
        """Generates a stickiness policy with sticky session lifetimes that follow
        that of an application-generated cookie. This policy can be associated
        only with HTTP/HTTPS listeners.

        This policy is similar to the policy created by
        CreateLBCookieStickinessPolicy, except that the lifetime of the special
        Elastic Load Balancing cookie, ``AWSELB``, follows the lifetime of the
        application-generated cookie specified in the policy configuration. The
        load balancer only inserts a new stickiness cookie when the application
        response includes a new application cookie.

        If the application cookie is explicitly removed or expires, the session
        stops being sticky until a new application cookie is issued.

        For more information, see `Application-Controlled Session
        Stickiness <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-sticky-sessions.html#enable-sticky-sessions-application>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param policy_name: The name of the policy being created.
        :param cookie_name: The name of the application cookie used for stickiness.
        :returns: CreateAppCookieStickinessPolicyOutput
        :raises AccessPointNotFoundException:
        :raises DuplicatePolicyNameException:
        :raises TooManyPoliciesException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("CreateLBCookieStickinessPolicy")
    def create_lb_cookie_stickiness_policy(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        policy_name: PolicyName,
        cookie_expiration_period: CookieExpirationPeriod = None,
    ) -> CreateLBCookieStickinessPolicyOutput:
        """Generates a stickiness policy with sticky session lifetimes controlled
        by the lifetime of the browser (user-agent) or a specified expiration
        period. This policy can be associated only with HTTP/HTTPS listeners.

        When a load balancer implements this policy, the load balancer uses a
        special cookie to track the instance for each request. When the load
        balancer receives a request, it first checks to see if this cookie is
        present in the request. If so, the load balancer sends the request to
        the application server specified in the cookie. If not, the load
        balancer sends the request to a server that is chosen based on the
        existing load-balancing algorithm.

        A cookie is inserted into the response for binding subsequent requests
        from the same user to that server. The validity of the cookie is based
        on the cookie expiration time, which is specified in the policy
        configuration.

        For more information, see `Duration-Based Session
        Stickiness <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-sticky-sessions.html#enable-sticky-sessions-duration>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param policy_name: The name of the policy being created.
        :param cookie_expiration_period: The time period, in seconds, after which the cookie should be considered
        stale.
        :returns: CreateLBCookieStickinessPolicyOutput
        :raises AccessPointNotFoundException:
        :raises DuplicatePolicyNameException:
        :raises TooManyPoliciesException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("CreateLoadBalancer")
    def create_load_balancer(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        listeners: Listeners,
        availability_zones: AvailabilityZones = None,
        subnets: Subnets = None,
        security_groups: SecurityGroups = None,
        scheme: LoadBalancerScheme = None,
        tags: TagList = None,
    ) -> CreateAccessPointOutput:
        """Creates a Classic Load Balancer.

        You can add listeners, security groups, subnets, and tags when you
        create your load balancer, or you can add them later using
        CreateLoadBalancerListeners, ApplySecurityGroupsToLoadBalancer,
        AttachLoadBalancerToSubnets, and AddTags.

        To describe your current load balancers, see DescribeLoadBalancers. When
        you are finished with a load balancer, you can delete it using
        DeleteLoadBalancer.

        You can create up to 20 load balancers per region per account. You can
        request an increase for the number of load balancers for your account.
        For more information, see `Limits for Your Classic Load
        Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-limits.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param listeners: The listeners.
        :param availability_zones: One or more Availability Zones from the same region as the load
        balancer.
        :param subnets: The IDs of the subnets in your VPC to attach to the load balancer.
        :param security_groups: The IDs of the security groups to assign to the load balancer.
        :param scheme: The type of a load balancer.
        :param tags: A list of tags to assign to the load balancer.
        :returns: CreateAccessPointOutput
        :raises DuplicateAccessPointNameException:
        :raises TooManyAccessPointsException:
        :raises CertificateNotFoundException:
        :raises InvalidConfigurationRequestException:
        :raises SubnetNotFoundException:
        :raises InvalidSubnetException:
        :raises InvalidSecurityGroupException:
        :raises InvalidSchemeException:
        :raises TooManyTagsException:
        :raises DuplicateTagKeysException:
        :raises UnsupportedProtocolException:
        :raises OperationNotPermittedException:
        """
        raise NotImplementedError

    @handler("CreateLoadBalancerListeners")
    def create_load_balancer_listeners(
        self, context: RequestContext, load_balancer_name: AccessPointName, listeners: Listeners
    ) -> CreateLoadBalancerListenerOutput:
        """Creates one or more listeners for the specified load balancer. If a
        listener with the specified port does not already exist, it is created;
        otherwise, the properties of the new listener must match the properties
        of the existing listener.

        For more information, see `Listeners for Your Classic Load
        Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-listener-config.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param listeners: The listeners.
        :returns: CreateLoadBalancerListenerOutput
        :raises AccessPointNotFoundException:
        :raises DuplicateListenerException:
        :raises CertificateNotFoundException:
        :raises InvalidConfigurationRequestException:
        :raises UnsupportedProtocolException:
        """
        raise NotImplementedError

    @handler("CreateLoadBalancerPolicy")
    def create_load_balancer_policy(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        policy_name: PolicyName,
        policy_type_name: PolicyTypeName,
        policy_attributes: PolicyAttributes = None,
    ) -> CreateLoadBalancerPolicyOutput:
        """Creates a policy with the specified attributes for the specified load
        balancer.

        Policies are settings that are saved for your load balancer and that can
        be applied to the listener or the application server, depending on the
        policy type.

        :param load_balancer_name: The name of the load balancer.
        :param policy_name: The name of the load balancer policy to be created.
        :param policy_type_name: The name of the base policy type.
        :param policy_attributes: The policy attributes.
        :returns: CreateLoadBalancerPolicyOutput
        :raises AccessPointNotFoundException:
        :raises PolicyTypeNotFoundException:
        :raises DuplicatePolicyNameException:
        :raises TooManyPoliciesException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("DeleteLoadBalancer")
    def delete_load_balancer(
        self, context: RequestContext, load_balancer_name: AccessPointName
    ) -> DeleteAccessPointOutput:
        """Deletes the specified load balancer.

        If you are attempting to recreate a load balancer, you must reconfigure
        all settings. The DNS name associated with a deleted load balancer are
        no longer usable. The name and associated DNS record of the deleted load
        balancer no longer exist and traffic sent to any of its IP addresses is
        no longer delivered to your instances.

        If the load balancer does not exist or has already been deleted, the
        call to ``DeleteLoadBalancer`` still succeeds.

        :param load_balancer_name: The name of the load balancer.
        :returns: DeleteAccessPointOutput
        """
        raise NotImplementedError

    @handler("DeleteLoadBalancerListeners")
    def delete_load_balancer_listeners(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        load_balancer_ports: Ports,
    ) -> DeleteLoadBalancerListenerOutput:
        """Deletes the specified listeners from the specified load balancer.

        :param load_balancer_name: The name of the load balancer.
        :param load_balancer_ports: The client port numbers of the listeners.
        :returns: DeleteLoadBalancerListenerOutput
        :raises AccessPointNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteLoadBalancerPolicy")
    def delete_load_balancer_policy(
        self, context: RequestContext, load_balancer_name: AccessPointName, policy_name: PolicyName
    ) -> DeleteLoadBalancerPolicyOutput:
        """Deletes the specified policy from the specified load balancer. This
        policy must not be enabled for any listeners.

        :param load_balancer_name: The name of the load balancer.
        :param policy_name: The name of the policy.
        :returns: DeleteLoadBalancerPolicyOutput
        :raises AccessPointNotFoundException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("DeregisterInstancesFromLoadBalancer")
    def deregister_instances_from_load_balancer(
        self, context: RequestContext, load_balancer_name: AccessPointName, instances: Instances
    ) -> DeregisterEndPointsOutput:
        """Deregisters the specified instances from the specified load balancer.
        After the instance is deregistered, it no longer receives traffic from
        the load balancer.

        You can use DescribeLoadBalancers to verify that the instance is
        deregistered from the load balancer.

        For more information, see `Register or De-Register EC2
        Instances <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-deregister-register-instances.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param instances: The IDs of the instances.
        :returns: DeregisterEndPointsOutput
        :raises AccessPointNotFoundException:
        :raises InvalidEndPointException:
        """
        raise NotImplementedError

    @handler("DescribeAccountLimits")
    def describe_account_limits(
        self, context: RequestContext, marker: Marker = None, page_size: PageSize = None
    ) -> DescribeAccountLimitsOutput:
        """Describes the current Elastic Load Balancing resource limits for your
        AWS account.

        For more information, see `Limits for Your Classic Load
        Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-limits.html>`__
        in the *Classic Load Balancers Guide*.

        :param marker: The marker for the next set of results.
        :param page_size: The maximum number of results to return with this call.
        :returns: DescribeAccountLimitsOutput
        """
        raise NotImplementedError

    @handler("DescribeInstanceHealth")
    def describe_instance_health(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        instances: Instances = None,
    ) -> DescribeEndPointStateOutput:
        """Describes the state of the specified instances with respect to the
        specified load balancer. If no instances are specified, the call
        describes the state of all instances that are currently registered with
        the load balancer. If instances are specified, their state is returned
        even if they are no longer registered with the load balancer. The state
        of terminated instances is not returned.

        :param load_balancer_name: The name of the load balancer.
        :param instances: The IDs of the instances.
        :returns: DescribeEndPointStateOutput
        :raises AccessPointNotFoundException:
        :raises InvalidEndPointException:
        """
        raise NotImplementedError

    @handler("DescribeLoadBalancerAttributes")
    def describe_load_balancer_attributes(
        self, context: RequestContext, load_balancer_name: AccessPointName
    ) -> DescribeLoadBalancerAttributesOutput:
        """Describes the attributes for the specified load balancer.

        :param load_balancer_name: The name of the load balancer.
        :returns: DescribeLoadBalancerAttributesOutput
        :raises AccessPointNotFoundException:
        :raises LoadBalancerAttributeNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeLoadBalancerPolicies")
    def describe_load_balancer_policies(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName = None,
        policy_names: PolicyNames = None,
    ) -> DescribeLoadBalancerPoliciesOutput:
        """Describes the specified policies.

        If you specify a load balancer name, the action returns the descriptions
        of all policies created for the load balancer. If you specify a policy
        name associated with your load balancer, the action returns the
        description of that policy. If you don't specify a load balancer name,
        the action returns descriptions of the specified sample policies, or
        descriptions of all sample policies. The names of the sample policies
        have the ``ELBSample-`` prefix.

        :param load_balancer_name: The name of the load balancer.
        :param policy_names: The names of the policies.
        :returns: DescribeLoadBalancerPoliciesOutput
        :raises AccessPointNotFoundException:
        :raises PolicyNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeLoadBalancerPolicyTypes")
    def describe_load_balancer_policy_types(
        self, context: RequestContext, policy_type_names: PolicyTypeNames = None
    ) -> DescribeLoadBalancerPolicyTypesOutput:
        """Describes the specified load balancer policy types or all load balancer
        policy types.

        The description of each type indicates how it can be used. For example,
        some policies can be used only with layer 7 listeners, some policies can
        be used only with layer 4 listeners, and some policies can be used only
        with your EC2 instances.

        You can use CreateLoadBalancerPolicy to create a policy configuration
        for any of these policy types. Then, depending on the policy type, use
        either SetLoadBalancerPoliciesOfListener or
        SetLoadBalancerPoliciesForBackendServer to set the policy.

        :param policy_type_names: The names of the policy types.
        :returns: DescribeLoadBalancerPolicyTypesOutput
        :raises PolicyTypeNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeLoadBalancers")
    def describe_load_balancers(
        self,
        context: RequestContext,
        load_balancer_names: LoadBalancerNames = None,
        marker: Marker = None,
        page_size: PageSize = None,
    ) -> DescribeAccessPointsOutput:
        """Describes the specified the load balancers. If no load balancers are
        specified, the call describes all of your load balancers.

        :param load_balancer_names: The names of the load balancers.
        :param marker: The marker for the next set of results.
        :param page_size: The maximum number of results to return with this call (a number from 1
        to 400).
        :returns: DescribeAccessPointsOutput
        :raises AccessPointNotFoundException:
        :raises DependencyThrottleException:
        """
        raise NotImplementedError

    @handler("DescribeTags")
    def describe_tags(
        self, context: RequestContext, load_balancer_names: LoadBalancerNamesMax20
    ) -> DescribeTagsOutput:
        """Describes the tags associated with the specified load balancers.

        :param load_balancer_names: The names of the load balancers.
        :returns: DescribeTagsOutput
        :raises AccessPointNotFoundException:
        """
        raise NotImplementedError

    @handler("DetachLoadBalancerFromSubnets")
    def detach_load_balancer_from_subnets(
        self, context: RequestContext, load_balancer_name: AccessPointName, subnets: Subnets
    ) -> DetachLoadBalancerFromSubnetsOutput:
        """Removes the specified subnets from the set of configured subnets for the
        load balancer.

        After a subnet is removed, all EC2 instances registered with the load
        balancer in the removed subnet go into the ``OutOfService`` state. Then,
        the load balancer balances the traffic among the remaining routable
        subnets.

        :param load_balancer_name: The name of the load balancer.
        :param subnets: The IDs of the subnets.
        :returns: DetachLoadBalancerFromSubnetsOutput
        :raises AccessPointNotFoundException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("DisableAvailabilityZonesForLoadBalancer")
    def disable_availability_zones_for_load_balancer(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        availability_zones: AvailabilityZones,
    ) -> RemoveAvailabilityZonesOutput:
        """Removes the specified Availability Zones from the set of Availability
        Zones for the specified load balancer in EC2-Classic or a default VPC.

        For load balancers in a non-default VPC, use
        DetachLoadBalancerFromSubnets.

        There must be at least one Availability Zone registered with a load
        balancer at all times. After an Availability Zone is removed, all
        instances registered with the load balancer that are in the removed
        Availability Zone go into the ``OutOfService`` state. Then, the load
        balancer attempts to equally balance the traffic among its remaining
        Availability Zones.

        For more information, see `Add or Remove Availability
        Zones <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-disable-az.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param availability_zones: The Availability Zones.
        :returns: RemoveAvailabilityZonesOutput
        :raises AccessPointNotFoundException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("EnableAvailabilityZonesForLoadBalancer")
    def enable_availability_zones_for_load_balancer(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        availability_zones: AvailabilityZones,
    ) -> AddAvailabilityZonesOutput:
        """Adds the specified Availability Zones to the set of Availability Zones
        for the specified load balancer in EC2-Classic or a default VPC.

        For load balancers in a non-default VPC, use
        AttachLoadBalancerToSubnets.

        The load balancer evenly distributes requests across all its registered
        Availability Zones that contain instances. For more information, see
        `Add or Remove Availability
        Zones <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-disable-az.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param availability_zones: The Availability Zones.
        :returns: AddAvailabilityZonesOutput
        :raises AccessPointNotFoundException:
        """
        raise NotImplementedError

    @handler("ModifyLoadBalancerAttributes")
    def modify_load_balancer_attributes(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        load_balancer_attributes: LoadBalancerAttributes,
    ) -> ModifyLoadBalancerAttributesOutput:
        """Modifies the attributes of the specified load balancer.

        You can modify the load balancer attributes, such as ``AccessLogs``,
        ``ConnectionDraining``, and ``CrossZoneLoadBalancing`` by either
        enabling or disabling them. Or, you can modify the load balancer
        attribute ``ConnectionSettings`` by specifying an idle connection
        timeout value for your load balancer.

        For more information, see the following in the *Classic Load Balancers
        Guide*:

        -  `Cross-Zone Load
           Balancing <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-disable-crosszone-lb.html>`__

        -  `Connection
           Draining <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/config-conn-drain.html>`__

        -  `Access
           Logs <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/access-log-collection.html>`__

        -  `Idle Connection
           Timeout <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/config-idle-timeout.html>`__

        :param load_balancer_name: The name of the load balancer.
        :param load_balancer_attributes: The attributes for the load balancer.
        :returns: ModifyLoadBalancerAttributesOutput
        :raises AccessPointNotFoundException:
        :raises LoadBalancerAttributeNotFoundException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("RegisterInstancesWithLoadBalancer")
    def register_instances_with_load_balancer(
        self, context: RequestContext, load_balancer_name: AccessPointName, instances: Instances
    ) -> RegisterEndPointsOutput:
        """Adds the specified instances to the specified load balancer.

        The instance must be a running instance in the same network as the load
        balancer (EC2-Classic or the same VPC). If you have EC2-Classic
        instances and a load balancer in a VPC with ClassicLink enabled, you can
        link the EC2-Classic instances to that VPC and then register the linked
        EC2-Classic instances with the load balancer in the VPC.

        Note that ``RegisterInstanceWithLoadBalancer`` completes when the
        request has been registered. Instance registration takes a little time
        to complete. To check the state of the registered instances, use
        DescribeLoadBalancers or DescribeInstanceHealth.

        After the instance is registered, it starts receiving traffic and
        requests from the load balancer. Any instance that is not in one of the
        Availability Zones registered for the load balancer is moved to the
        ``OutOfService`` state. If an Availability Zone is added to the load
        balancer later, any instances registered with the load balancer move to
        the ``InService`` state.

        To deregister instances from a load balancer, use
        DeregisterInstancesFromLoadBalancer.

        For more information, see `Register or De-Register EC2
        Instances <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-deregister-register-instances.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param instances: The IDs of the instances.
        :returns: RegisterEndPointsOutput
        :raises AccessPointNotFoundException:
        :raises InvalidEndPointException:
        """
        raise NotImplementedError

    @handler("RemoveTags")
    def remove_tags(
        self, context: RequestContext, load_balancer_names: LoadBalancerNames, tags: TagKeyList
    ) -> RemoveTagsOutput:
        """Removes one or more tags from the specified load balancer.

        :param load_balancer_names: The name of the load balancer.
        :param tags: The list of tag keys to remove.
        :returns: RemoveTagsOutput
        :raises AccessPointNotFoundException:
        """
        raise NotImplementedError

    @handler("SetLoadBalancerListenerSSLCertificate")
    def set_load_balancer_listener_ssl_certificate(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        load_balancer_port: AccessPointPort,
        ssl_certificate_id: SSLCertificateId,
    ) -> SetLoadBalancerListenerSSLCertificateOutput:
        """Sets the certificate that terminates the specified listener's SSL
        connections. The specified certificate replaces any prior certificate
        that was used on the same load balancer and port.

        For more information about updating your SSL certificate, see `Replace
        the SSL Certificate for Your Load
        Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-update-ssl-cert.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param load_balancer_port: The port that uses the specified SSL certificate.
        :param ssl_certificate_id: The Amazon Resource Name (ARN) of the SSL certificate.
        :returns: SetLoadBalancerListenerSSLCertificateOutput
        :raises CertificateNotFoundException:
        :raises AccessPointNotFoundException:
        :raises ListenerNotFoundException:
        :raises InvalidConfigurationRequestException:
        :raises UnsupportedProtocolException:
        """
        raise NotImplementedError

    @handler("SetLoadBalancerPoliciesForBackendServer")
    def set_load_balancer_policies_for_backend_server(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        instance_port: EndPointPort,
        policy_names: PolicyNames,
    ) -> SetLoadBalancerPoliciesForBackendServerOutput:
        """Replaces the set of policies associated with the specified port on which
        the EC2 instance is listening with a new set of policies. At this time,
        only the back-end server authentication policy type can be applied to
        the instance ports; this policy type is composed of multiple public key
        policies.

        Each time you use ``SetLoadBalancerPoliciesForBackendServer`` to enable
        the policies, use the ``PolicyNames`` parameter to list the policies
        that you want to enable.

        You can use DescribeLoadBalancers or DescribeLoadBalancerPolicies to
        verify that the policy is associated with the EC2 instance.

        For more information about enabling back-end instance authentication,
        see `Configure Back-end Instance
        Authentication <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-create-https-ssl-load-balancer.html#configure_backendauth_clt>`__
        in the *Classic Load Balancers Guide*. For more information about Proxy
        Protocol, see `Configure Proxy Protocol
        Support <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-proxy-protocol.html>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param instance_port: The port number associated with the EC2 instance.
        :param policy_names: The names of the policies.
        :returns: SetLoadBalancerPoliciesForBackendServerOutput
        :raises AccessPointNotFoundException:
        :raises PolicyNotFoundException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError

    @handler("SetLoadBalancerPoliciesOfListener")
    def set_load_balancer_policies_of_listener(
        self,
        context: RequestContext,
        load_balancer_name: AccessPointName,
        load_balancer_port: AccessPointPort,
        policy_names: PolicyNames,
    ) -> SetLoadBalancerPoliciesOfListenerOutput:
        """Replaces the current set of policies for the specified load balancer
        port with the specified set of policies.

        To enable back-end server authentication, use
        SetLoadBalancerPoliciesForBackendServer.

        For more information about setting policies, see `Update the SSL
        Negotiation
        Configuration <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/ssl-config-update.html>`__,
        `Duration-Based Session
        Stickiness <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-sticky-sessions.html#enable-sticky-sessions-duration>`__,
        and `Application-Controlled Session
        Stickiness <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-sticky-sessions.html#enable-sticky-sessions-application>`__
        in the *Classic Load Balancers Guide*.

        :param load_balancer_name: The name of the load balancer.
        :param load_balancer_port: The external port of the load balancer.
        :param policy_names: The names of the policies.
        :returns: SetLoadBalancerPoliciesOfListenerOutput
        :raises AccessPointNotFoundException:
        :raises PolicyNotFoundException:
        :raises ListenerNotFoundException:
        :raises InvalidConfigurationRequestException:
        """
        raise NotImplementedError
