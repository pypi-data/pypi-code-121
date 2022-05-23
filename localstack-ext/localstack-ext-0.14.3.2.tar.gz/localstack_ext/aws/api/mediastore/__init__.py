import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ContainerARN = str
ContainerAccessLoggingEnabled = bool
ContainerListLimit = int
ContainerName = str
ContainerPolicy = str
Endpoint = str
ErrorMessage = str
Header = str
LifecyclePolicy = str
MaxAgeSeconds = int
ObjectGroup = str
ObjectGroupName = str
Origin = str
PaginationToken = str
TagKey = str
TagValue = str


class ContainerLevelMetrics(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class ContainerStatus(str):
    ACTIVE = "ACTIVE"
    CREATING = "CREATING"
    DELETING = "DELETING"


class MethodName(str):
    PUT = "PUT"
    GET = "GET"
    DELETE = "DELETE"
    HEAD = "HEAD"


class ContainerInUseException(ServiceException):
    """The container that you specified in the request already exists or is
    being updated.
    """

    Message: Optional[ErrorMessage]


class ContainerNotFoundException(ServiceException):
    """The container that you specified in the request does not exist."""

    Message: Optional[ErrorMessage]


class CorsPolicyNotFoundException(ServiceException):
    """The CORS policy that you specified in the request does not exist."""

    Message: Optional[ErrorMessage]


class InternalServerError(ServiceException):
    """The service is temporarily unavailable."""

    Message: Optional[ErrorMessage]


class LimitExceededException(ServiceException):
    """A service limit has been exceeded."""

    Message: Optional[ErrorMessage]


class PolicyNotFoundException(ServiceException):
    """The policy that you specified in the request does not exist."""

    Message: Optional[ErrorMessage]


AllowedHeaders = List[Header]
AllowedMethods = List[MethodName]
AllowedOrigins = List[Origin]
TimeStamp = datetime


class Container(TypedDict, total=False):
    """This section describes operations that you can perform on an AWS
    Elemental MediaStore container.
    """

    Endpoint: Optional[Endpoint]
    CreationTime: Optional[TimeStamp]
    ARN: Optional[ContainerARN]
    Name: Optional[ContainerName]
    Status: Optional[ContainerStatus]
    AccessLoggingEnabled: Optional[ContainerAccessLoggingEnabled]


ContainerList = List[Container]
ExposeHeaders = List[Header]


class CorsRule(TypedDict, total=False):
    """A rule for a CORS policy. You can add up to 100 rules to a CORS policy.
    If more than one rule applies, the service uses the first applicable
    rule listed.
    """

    AllowedOrigins: AllowedOrigins
    AllowedMethods: Optional[AllowedMethods]
    AllowedHeaders: AllowedHeaders
    MaxAgeSeconds: Optional[MaxAgeSeconds]
    ExposeHeaders: Optional[ExposeHeaders]


CorsPolicy = List[CorsRule]


class Tag(TypedDict, total=False):
    """A collection of tags associated with a container. Each tag consists of a
    key:value pair, which can be anything you define. Typically, the tag key
    represents a category (such as "environment") and the tag value
    represents a specific value within that category (such as "test,"
    "development," or "production"). You can add up to 50 tags to each
    container. For more information about tagging, including naming and
    usage conventions, see `Tagging Resources in
    MediaStore <https://docs.aws.amazon.com/mediastore/latest/ug/tagging.html>`__.
    """

    Key: TagKey
    Value: Optional[TagValue]


TagList = List[Tag]


class CreateContainerInput(ServiceRequest):
    ContainerName: ContainerName
    Tags: Optional[TagList]


class CreateContainerOutput(TypedDict, total=False):
    Container: Container


class DeleteContainerInput(ServiceRequest):
    ContainerName: ContainerName


class DeleteContainerOutput(TypedDict, total=False):
    pass


class DeleteContainerPolicyInput(ServiceRequest):
    ContainerName: ContainerName


class DeleteContainerPolicyOutput(TypedDict, total=False):
    pass


class DeleteCorsPolicyInput(ServiceRequest):
    ContainerName: ContainerName


class DeleteCorsPolicyOutput(TypedDict, total=False):
    pass


class DeleteLifecyclePolicyInput(ServiceRequest):
    ContainerName: ContainerName


class DeleteLifecyclePolicyOutput(TypedDict, total=False):
    pass


class DeleteMetricPolicyInput(ServiceRequest):
    ContainerName: ContainerName


class DeleteMetricPolicyOutput(TypedDict, total=False):
    pass


class DescribeContainerInput(ServiceRequest):
    ContainerName: Optional[ContainerName]


class DescribeContainerOutput(TypedDict, total=False):
    Container: Optional[Container]


class GetContainerPolicyInput(ServiceRequest):
    ContainerName: ContainerName


class GetContainerPolicyOutput(TypedDict, total=False):
    Policy: ContainerPolicy


class GetCorsPolicyInput(ServiceRequest):
    ContainerName: ContainerName


class GetCorsPolicyOutput(TypedDict, total=False):
    CorsPolicy: CorsPolicy


class GetLifecyclePolicyInput(ServiceRequest):
    ContainerName: ContainerName


class GetLifecyclePolicyOutput(TypedDict, total=False):
    LifecyclePolicy: LifecyclePolicy


class GetMetricPolicyInput(ServiceRequest):
    ContainerName: ContainerName


class MetricPolicyRule(TypedDict, total=False):
    """A setting that enables metrics at the object level. Each rule contains
    an object group and an object group name. If the policy includes the
    MetricPolicyRules parameter, you must include at least one rule. Each
    metric policy can include up to five rules by default. You can also
    `request a quota
    increase <https://console.aws.amazon.com/servicequotas/home?region=us-east-1#!/services/mediastore/quotas>`__
    to allow up to 300 rules per policy.
    """

    ObjectGroup: ObjectGroup
    ObjectGroupName: ObjectGroupName


MetricPolicyRules = List[MetricPolicyRule]


class MetricPolicy(TypedDict, total=False):
    """The metric policy that is associated with the container. A metric policy
    allows AWS Elemental MediaStore to send metrics to Amazon CloudWatch. In
    the policy, you must indicate whether you want MediaStore to send
    container-level metrics. You can also include rules to define groups of
    objects that you want MediaStore to send object-level metrics for.

    To view examples of how to construct a metric policy for your use case,
    see `Example Metric
    Policies <https://docs.aws.amazon.com/mediastore/latest/ug/policies-metric-examples.html>`__.
    """

    ContainerLevelMetrics: ContainerLevelMetrics
    MetricPolicyRules: Optional[MetricPolicyRules]


class GetMetricPolicyOutput(TypedDict, total=False):
    MetricPolicy: MetricPolicy


class ListContainersInput(ServiceRequest):
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[ContainerListLimit]


class ListContainersOutput(TypedDict, total=False):
    Containers: ContainerList
    NextToken: Optional[PaginationToken]


class ListTagsForResourceInput(ServiceRequest):
    Resource: ContainerARN


class ListTagsForResourceOutput(TypedDict, total=False):
    Tags: Optional[TagList]


class PutContainerPolicyInput(ServiceRequest):
    ContainerName: ContainerName
    Policy: ContainerPolicy


class PutContainerPolicyOutput(TypedDict, total=False):
    pass


class PutCorsPolicyInput(ServiceRequest):
    ContainerName: ContainerName
    CorsPolicy: CorsPolicy


class PutCorsPolicyOutput(TypedDict, total=False):
    pass


class PutLifecyclePolicyInput(ServiceRequest):
    ContainerName: ContainerName
    LifecyclePolicy: LifecyclePolicy


class PutLifecyclePolicyOutput(TypedDict, total=False):
    pass


class PutMetricPolicyInput(ServiceRequest):
    ContainerName: ContainerName
    MetricPolicy: MetricPolicy


class PutMetricPolicyOutput(TypedDict, total=False):
    pass


class StartAccessLoggingInput(ServiceRequest):
    ContainerName: ContainerName


class StartAccessLoggingOutput(TypedDict, total=False):
    pass


class StopAccessLoggingInput(ServiceRequest):
    ContainerName: ContainerName


class StopAccessLoggingOutput(TypedDict, total=False):
    pass


TagKeyList = List[TagKey]


class TagResourceInput(ServiceRequest):
    Resource: ContainerARN
    Tags: TagList


class TagResourceOutput(TypedDict, total=False):
    pass


class UntagResourceInput(ServiceRequest):
    Resource: ContainerARN
    TagKeys: TagKeyList


class UntagResourceOutput(TypedDict, total=False):
    pass


class MediastoreApi:

    service = "mediastore"
    version = "2017-09-01"

    @handler("CreateContainer")
    def create_container(
        self, context: RequestContext, container_name: ContainerName, tags: TagList = None
    ) -> CreateContainerOutput:
        """Creates a storage container to hold objects. A container is similar to a
        bucket in the Amazon S3 service.

        :param container_name: The name for the container.
        :param tags: An array of key:value pairs that you define.
        :returns: CreateContainerOutput
        :raises ContainerInUseException:
        :raises LimitExceededException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DeleteContainer")
    def delete_container(
        self, context: RequestContext, container_name: ContainerName
    ) -> DeleteContainerOutput:
        """Deletes the specified container. Before you make a ``DeleteContainer``
        request, delete any objects in the container or in any folders in the
        container. You can delete only empty containers.

        :param container_name: The name of the container to delete.
        :returns: DeleteContainerOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DeleteContainerPolicy")
    def delete_container_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> DeleteContainerPolicyOutput:
        """Deletes the access policy that is associated with the specified
        container.

        :param container_name: The name of the container that holds the policy.
        :returns: DeleteContainerPolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises PolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DeleteCorsPolicy")
    def delete_cors_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> DeleteCorsPolicyOutput:
        """Deletes the cross-origin resource sharing (CORS) configuration
        information that is set for the container.

        To use this operation, you must have permission to perform the
        ``MediaStore:DeleteCorsPolicy`` action. The container owner has this
        permission by default and can grant this permission to others.

        :param container_name: The name of the container to remove the policy from.
        :returns: DeleteCorsPolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises CorsPolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DeleteLifecyclePolicy")
    def delete_lifecycle_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> DeleteLifecyclePolicyOutput:
        """Removes an object lifecycle policy from a container. It takes up to 20
        minutes for the change to take effect.

        :param container_name: The name of the container that holds the object lifecycle policy.
        :returns: DeleteLifecyclePolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises PolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DeleteMetricPolicy")
    def delete_metric_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> DeleteMetricPolicyOutput:
        """Deletes the metric policy that is associated with the specified
        container. If there is no metric policy associated with the container,
        MediaStore doesn't send metrics to CloudWatch.

        :param container_name: The name of the container that is associated with the metric policy that
        you want to delete.
        :returns: DeleteMetricPolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises PolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DescribeContainer")
    def describe_container(
        self, context: RequestContext, container_name: ContainerName = None
    ) -> DescribeContainerOutput:
        """Retrieves the properties of the requested container. This request is
        commonly used to retrieve the endpoint of a container. An endpoint is a
        value assigned by the service when a new container is created. A
        container's endpoint does not change after it has been assigned. The
        ``DescribeContainer`` request returns a single ``Container`` object
        based on ``ContainerName``. To return all ``Container`` objects that are
        associated with a specified AWS account, use ListContainers.

        :param container_name: The name of the container to query.
        :returns: DescribeContainerOutput
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("GetContainerPolicy")
    def get_container_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> GetContainerPolicyOutput:
        """Retrieves the access policy for the specified container. For information
        about the data that is included in an access policy, see the `AWS
        Identity and Access Management User
        Guide <https://aws.amazon.com/documentation/iam/>`__.

        :param container_name: The name of the container.
        :returns: GetContainerPolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises PolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("GetCorsPolicy")
    def get_cors_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> GetCorsPolicyOutput:
        """Returns the cross-origin resource sharing (CORS) configuration
        information that is set for the container.

        To use this operation, you must have permission to perform the
        ``MediaStore:GetCorsPolicy`` action. By default, the container owner has
        this permission and can grant it to others.

        :param container_name: The name of the container that the policy is assigned to.
        :returns: GetCorsPolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises CorsPolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("GetLifecyclePolicy")
    def get_lifecycle_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> GetLifecyclePolicyOutput:
        """Retrieves the object lifecycle policy that is assigned to a container.

        :param container_name: The name of the container that the object lifecycle policy is assigned
        to.
        :returns: GetLifecyclePolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises PolicyNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("GetMetricPolicy")
    def get_metric_policy(
        self, context: RequestContext, container_name: ContainerName
    ) -> GetMetricPolicyOutput:
        """Returns the metric policy for the specified container.

        :param container_name: The name of the container that is associated with the metric policy.
        :returns: GetMetricPolicyOutput
        :raises ContainerNotFoundException:
        :raises PolicyNotFoundException:
        :raises ContainerInUseException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("ListContainers")
    def list_containers(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: ContainerListLimit = None,
    ) -> ListContainersOutput:
        """Lists the properties of all containers in AWS Elemental MediaStore.

        You can query to receive all the containers in one response. Or you can
        include the ``MaxResults`` parameter to receive a limited number of
        containers in each response. In this case, the response includes a
        token. To get the next set of containers, send the command again, this
        time with the ``NextToken`` parameter (with the returned token as its
        value). The next set of responses appears, with a token if there are
        still more containers to receive.

        See also DescribeContainer, which gets the properties of one container.

        :param next_token: Only if you used ``MaxResults`` in the first command, enter the token
        (which was included in the previous response) to obtain the next set of
        containers.
        :param max_results: Enter the maximum number of containers in the response.
        :returns: ListContainersOutput
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource: ContainerARN
    ) -> ListTagsForResourceOutput:
        """Returns a list of the tags assigned to the specified container.

        :param resource: The Amazon Resource Name (ARN) for the container.
        :returns: ListTagsForResourceOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutContainerPolicy")
    def put_container_policy(
        self, context: RequestContext, container_name: ContainerName, policy: ContainerPolicy
    ) -> PutContainerPolicyOutput:
        """Creates an access policy for the specified container to restrict the
        users and clients that can access it. For information about the data
        that is included in an access policy, see the `AWS Identity and Access
        Management User Guide <https://aws.amazon.com/documentation/iam/>`__.

        For this release of the REST API, you can create only one policy for a
        container. If you enter ``PutContainerPolicy`` twice, the second command
        modifies the existing policy.

        :param container_name: The name of the container.
        :param policy: The contents of the policy, which includes the following:

        -  One ``Version`` tag

        -  One ``Statement`` tag that contains the standard tags for the policy.
        :returns: PutContainerPolicyOutput
        :raises ContainerNotFoundException:
        :raises ContainerInUseException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutCorsPolicy")
    def put_cors_policy(
        self, context: RequestContext, container_name: ContainerName, cors_policy: CorsPolicy
    ) -> PutCorsPolicyOutput:
        """Sets the cross-origin resource sharing (CORS) configuration on a
        container so that the container can service cross-origin requests. For
        example, you might want to enable a request whose origin is
        http://www.example.com to access your AWS Elemental MediaStore container
        at my.example.container.com by using the browser's XMLHttpRequest
        capability.

        To enable CORS on a container, you attach a CORS policy to the
        container. In the CORS policy, you configure rules that identify origins
        and the HTTP methods that can be executed on your container. The policy
        can contain up to 398,000 characters. You can add up to 100 rules to a
        CORS policy. If more than one rule applies, the service uses the first
        applicable rule listed.

        To learn more about CORS, see `Cross-Origin Resource Sharing (CORS) in
        AWS Elemental
        MediaStore <https://docs.aws.amazon.com/mediastore/latest/ug/cors-policy.html>`__.

        :param container_name: The name of the container that you want to assign the CORS policy to.
        :param cors_policy: The CORS policy to apply to the container.
        :returns: PutCorsPolicyOutput
        :raises ContainerNotFoundException:
        :raises ContainerInUseException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutLifecyclePolicy")
    def put_lifecycle_policy(
        self,
        context: RequestContext,
        container_name: ContainerName,
        lifecycle_policy: LifecyclePolicy,
    ) -> PutLifecyclePolicyOutput:
        """Writes an object lifecycle policy to a container. If the container
        already has an object lifecycle policy, the service replaces the
        existing policy with the new policy. It takes up to 20 minutes for the
        change to take effect.

        For information about how to construct an object lifecycle policy, see
        `Components of an Object Lifecycle
        Policy <https://docs.aws.amazon.com/mediastore/latest/ug/policies-object-lifecycle-components.html>`__.

        :param container_name: The name of the container that you want to assign the object lifecycle
        policy to.
        :param lifecycle_policy: The object lifecycle policy to apply to the container.
        :returns: PutLifecyclePolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutMetricPolicy")
    def put_metric_policy(
        self, context: RequestContext, container_name: ContainerName, metric_policy: MetricPolicy
    ) -> PutMetricPolicyOutput:
        """The metric policy that you want to add to the container. A metric policy
        allows AWS Elemental MediaStore to send metrics to Amazon CloudWatch. It
        takes up to 20 minutes for the new policy to take effect.

        :param container_name: The name of the container that you want to add the metric policy to.
        :param metric_policy: The metric policy that you want to associate with the container.
        :returns: PutMetricPolicyOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("StartAccessLogging")
    def start_access_logging(
        self, context: RequestContext, container_name: ContainerName
    ) -> StartAccessLoggingOutput:
        """Starts access logging on the specified container. When you enable access
        logging on a container, MediaStore delivers access logs for objects
        stored in that container to Amazon CloudWatch Logs.

        :param container_name: The name of the container that you want to start access logging on.
        :returns: StartAccessLoggingOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("StopAccessLogging")
    def stop_access_logging(
        self, context: RequestContext, container_name: ContainerName
    ) -> StopAccessLoggingOutput:
        """Stops access logging on the specified container. When you stop access
        logging on a container, MediaStore stops sending access logs to Amazon
        CloudWatch Logs. These access logs are not saved and are not
        retrievable.

        :param container_name: The name of the container that you want to stop access logging on.
        :returns: StopAccessLoggingOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource: ContainerARN, tags: TagList
    ) -> TagResourceOutput:
        """Adds tags to the specified AWS Elemental MediaStore container. Tags are
        key:value pairs that you can associate with AWS resources. For example,
        the tag key might be "customer" and the tag value might be "companyA."
        You can specify one or more tags to add to each container. You can add
        up to 50 tags to each container. For more information about tagging,
        including naming and usage conventions, see `Tagging Resources in
        MediaStore <https://docs.aws.amazon.com/mediastore/latest/ug/tagging.html>`__.

        :param resource: The Amazon Resource Name (ARN) for the container.
        :param tags: An array of key:value pairs that you want to add to the container.
        :returns: TagResourceOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource: ContainerARN, tag_keys: TagKeyList
    ) -> UntagResourceOutput:
        """Removes tags from the specified container. You can specify one or more
        tags to remove.

        :param resource: The Amazon Resource Name (ARN) for the container.
        :param tag_keys: A comma-separated list of keys for tags that you want to remove from the
        container.
        :returns: UntagResourceOutput
        :raises ContainerInUseException:
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError
