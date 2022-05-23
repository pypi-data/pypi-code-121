import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Arn = str
ConfigurationProfileType = str
DeploymentStrategyId = str
Description = str
Float = float
GrowthFactor = float
Id = str
Integer = int
MaxResults = int
MinutesBetween0And24Hours = int
Name = str
NextToken = str
Percentage = float
RoleArn = str
String = str
StringWithLengthBetween0And32768 = str
StringWithLengthBetween1And2048 = str
StringWithLengthBetween1And255 = str
StringWithLengthBetween1And64 = str
TagKey = str
TagValue = str
Uri = str
Version = str


class BadRequestReason(str):
    InvalidConfiguration = "InvalidConfiguration"


class BytesMeasure(str):
    KILOBYTES = "KILOBYTES"


class DeploymentEventType(str):
    PERCENTAGE_UPDATED = "PERCENTAGE_UPDATED"
    ROLLBACK_STARTED = "ROLLBACK_STARTED"
    ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"
    BAKE_TIME_STARTED = "BAKE_TIME_STARTED"
    DEPLOYMENT_STARTED = "DEPLOYMENT_STARTED"
    DEPLOYMENT_COMPLETED = "DEPLOYMENT_COMPLETED"


class DeploymentState(str):
    BAKING = "BAKING"
    VALIDATING = "VALIDATING"
    DEPLOYING = "DEPLOYING"
    COMPLETE = "COMPLETE"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"


class EnvironmentState(str):
    READY_FOR_DEPLOYMENT = "READY_FOR_DEPLOYMENT"
    DEPLOYING = "DEPLOYING"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"


class GrowthType(str):
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"


class ReplicateTo(str):
    NONE = "NONE"
    SSM_DOCUMENT = "SSM_DOCUMENT"


class TriggeredBy(str):
    USER = "USER"
    APPCONFIG = "APPCONFIG"
    CLOUDWATCH_ALARM = "CLOUDWATCH_ALARM"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ValidatorType(str):
    JSON_SCHEMA = "JSON_SCHEMA"
    LAMBDA = "LAMBDA"


class InvalidConfigurationDetail(TypedDict, total=False):
    """Detailed information about the bad request exception error when creating
    a hosted configuration version.
    """

    Constraint: Optional[String]
    Location: Optional[String]
    Reason: Optional[String]
    Type: Optional[String]


InvalidConfigurationDetailList = List[InvalidConfigurationDetail]


class BadRequestDetails(TypedDict, total=False):
    """Detailed information about the input that failed to satisfy the
    constraints specified by a call.
    """

    InvalidConfiguration: Optional[InvalidConfigurationDetailList]


class BadRequestException(ServiceException):
    """The input fails to satisfy the constraints specified by an Amazon Web
    Services service.
    """

    Message: Optional[String]
    Reason: Optional[BadRequestReason]
    Details: Optional[BadRequestDetails]


class ConflictException(ServiceException):
    """The request could not be processed because of conflict in the current
    state of the resource.
    """

    Message: Optional[String]


class InternalServerException(ServiceException):
    """There was an internal failure in the AppConfig service."""

    Message: Optional[String]


class PayloadTooLargeException(ServiceException):
    """The configuration size is too large."""

    Message: Optional[String]
    Measure: Optional[BytesMeasure]
    Limit: Optional[Float]
    Size: Optional[Float]


class ResourceNotFoundException(ServiceException):
    """The requested resource could not be found."""

    Message: Optional[String]
    ResourceName: Optional[String]


class ServiceQuotaExceededException(ServiceException):
    """The number of hosted configuration versions exceeds the limit for the
    AppConfig hosted configuration store. Delete one or more versions and
    try again.
    """

    Message: Optional[String]


class Application(TypedDict, total=False):
    Id: Optional[Id]
    Name: Optional[Name]
    Description: Optional[Description]


ApplicationList = List[Application]


class Applications(TypedDict, total=False):
    Items: Optional[ApplicationList]
    NextToken: Optional[NextToken]


Blob = bytes


class Configuration(TypedDict, total=False):
    Content: Optional[Blob]
    ConfigurationVersion: Optional[Version]
    ContentType: Optional[String]


class Validator(TypedDict, total=False):
    """A validator provides a syntactic or semantic check to ensure the
    configuration that you want to deploy functions as intended. To validate
    your application configuration data, you provide a schema or an Amazon
    Web Services Lambda function that runs against the configuration. The
    configuration deployment or update can only proceed when the
    configuration data is valid.
    """

    Type: ValidatorType
    Content: StringWithLengthBetween0And32768


ValidatorList = List[Validator]


class ConfigurationProfile(TypedDict, total=False):
    ApplicationId: Optional[Id]
    Id: Optional[Id]
    Name: Optional[Name]
    Description: Optional[Description]
    LocationUri: Optional[Uri]
    RetrievalRoleArn: Optional[RoleArn]
    Validators: Optional[ValidatorList]
    Type: Optional[ConfigurationProfileType]


ValidatorTypeList = List[ValidatorType]


class ConfigurationProfileSummary(TypedDict, total=False):
    """A summary of a configuration profile."""

    ApplicationId: Optional[Id]
    Id: Optional[Id]
    Name: Optional[Name]
    LocationUri: Optional[Uri]
    ValidatorTypes: Optional[ValidatorTypeList]
    Type: Optional[ConfigurationProfileType]


ConfigurationProfileSummaryList = List[ConfigurationProfileSummary]


class ConfigurationProfiles(TypedDict, total=False):
    Items: Optional[ConfigurationProfileSummaryList]
    NextToken: Optional[NextToken]


TagMap = Dict[TagKey, TagValue]


class CreateApplicationRequest(ServiceRequest):
    Name: Name
    Description: Optional[Description]
    Tags: Optional[TagMap]


class CreateConfigurationProfileRequest(ServiceRequest):
    ApplicationId: Id
    Name: Name
    Description: Optional[Description]
    LocationUri: Uri
    RetrievalRoleArn: Optional[RoleArn]
    Validators: Optional[ValidatorList]
    Tags: Optional[TagMap]
    Type: Optional[ConfigurationProfileType]


class CreateDeploymentStrategyRequest(ServiceRequest):
    Name: Name
    Description: Optional[Description]
    DeploymentDurationInMinutes: MinutesBetween0And24Hours
    FinalBakeTimeInMinutes: Optional[MinutesBetween0And24Hours]
    GrowthFactor: GrowthFactor
    GrowthType: Optional[GrowthType]
    ReplicateTo: ReplicateTo
    Tags: Optional[TagMap]


class Monitor(TypedDict, total=False):
    """Amazon CloudWatch alarms to monitor during the deployment process."""

    AlarmArn: StringWithLengthBetween1And2048
    AlarmRoleArn: Optional[RoleArn]


MonitorList = List[Monitor]


class CreateEnvironmentRequest(ServiceRequest):
    ApplicationId: Id
    Name: Name
    Description: Optional[Description]
    Monitors: Optional[MonitorList]
    Tags: Optional[TagMap]


class CreateHostedConfigurationVersionRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id
    Description: Optional[Description]
    Content: Blob
    ContentType: StringWithLengthBetween1And255
    LatestVersionNumber: Optional[Integer]


class DeleteApplicationRequest(ServiceRequest):
    ApplicationId: Id


class DeleteConfigurationProfileRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id


class DeleteDeploymentStrategyRequest(ServiceRequest):
    DeploymentStrategyId: DeploymentStrategyId


class DeleteEnvironmentRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id


class DeleteHostedConfigurationVersionRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id
    VersionNumber: Integer


Iso8601DateTime = datetime


class DeploymentEvent(TypedDict, total=False):
    """An object that describes a deployment event."""

    EventType: Optional[DeploymentEventType]
    TriggeredBy: Optional[TriggeredBy]
    Description: Optional[Description]
    OccurredAt: Optional[Iso8601DateTime]


DeploymentEvents = List[DeploymentEvent]


class Deployment(TypedDict, total=False):
    ApplicationId: Optional[Id]
    EnvironmentId: Optional[Id]
    DeploymentStrategyId: Optional[Id]
    ConfigurationProfileId: Optional[Id]
    DeploymentNumber: Optional[Integer]
    ConfigurationName: Optional[Name]
    ConfigurationLocationUri: Optional[Uri]
    ConfigurationVersion: Optional[Version]
    Description: Optional[Description]
    DeploymentDurationInMinutes: Optional[MinutesBetween0And24Hours]
    GrowthType: Optional[GrowthType]
    GrowthFactor: Optional[Percentage]
    FinalBakeTimeInMinutes: Optional[MinutesBetween0And24Hours]
    State: Optional[DeploymentState]
    EventLog: Optional[DeploymentEvents]
    PercentageComplete: Optional[Percentage]
    StartedAt: Optional[Iso8601DateTime]
    CompletedAt: Optional[Iso8601DateTime]


class DeploymentSummary(TypedDict, total=False):
    """Information about the deployment."""

    DeploymentNumber: Optional[Integer]
    ConfigurationName: Optional[Name]
    ConfigurationVersion: Optional[Version]
    DeploymentDurationInMinutes: Optional[MinutesBetween0And24Hours]
    GrowthType: Optional[GrowthType]
    GrowthFactor: Optional[Percentage]
    FinalBakeTimeInMinutes: Optional[MinutesBetween0And24Hours]
    State: Optional[DeploymentState]
    PercentageComplete: Optional[Percentage]
    StartedAt: Optional[Iso8601DateTime]
    CompletedAt: Optional[Iso8601DateTime]


DeploymentList = List[DeploymentSummary]


class DeploymentStrategy(TypedDict, total=False):
    Id: Optional[Id]
    Name: Optional[Name]
    Description: Optional[Description]
    DeploymentDurationInMinutes: Optional[MinutesBetween0And24Hours]
    GrowthType: Optional[GrowthType]
    GrowthFactor: Optional[Percentage]
    FinalBakeTimeInMinutes: Optional[MinutesBetween0And24Hours]
    ReplicateTo: Optional[ReplicateTo]


DeploymentStrategyList = List[DeploymentStrategy]


class DeploymentStrategies(TypedDict, total=False):
    Items: Optional[DeploymentStrategyList]
    NextToken: Optional[NextToken]


class Deployments(TypedDict, total=False):
    Items: Optional[DeploymentList]
    NextToken: Optional[NextToken]


class Environment(TypedDict, total=False):
    ApplicationId: Optional[Id]
    Id: Optional[Id]
    Name: Optional[Name]
    Description: Optional[Description]
    State: Optional[EnvironmentState]
    Monitors: Optional[MonitorList]


EnvironmentList = List[Environment]


class Environments(TypedDict, total=False):
    Items: Optional[EnvironmentList]
    NextToken: Optional[NextToken]


class GetApplicationRequest(ServiceRequest):
    ApplicationId: Id


class GetConfigurationProfileRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id


class GetConfigurationRequest(ServiceRequest):
    Application: StringWithLengthBetween1And64
    Environment: StringWithLengthBetween1And64
    Configuration: StringWithLengthBetween1And64
    ClientId: StringWithLengthBetween1And64
    ClientConfigurationVersion: Optional[Version]


class GetDeploymentRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id
    DeploymentNumber: Integer


class GetDeploymentStrategyRequest(ServiceRequest):
    DeploymentStrategyId: DeploymentStrategyId


class GetEnvironmentRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id


class GetHostedConfigurationVersionRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id
    VersionNumber: Integer


class HostedConfigurationVersion(TypedDict, total=False):
    ApplicationId: Optional[Id]
    ConfigurationProfileId: Optional[Id]
    VersionNumber: Optional[Integer]
    Description: Optional[Description]
    Content: Optional[Blob]
    ContentType: Optional[StringWithLengthBetween1And255]


class HostedConfigurationVersionSummary(TypedDict, total=False):
    """Information about the configuration."""

    ApplicationId: Optional[Id]
    ConfigurationProfileId: Optional[Id]
    VersionNumber: Optional[Integer]
    Description: Optional[Description]
    ContentType: Optional[StringWithLengthBetween1And255]


HostedConfigurationVersionSummaryList = List[HostedConfigurationVersionSummary]


class HostedConfigurationVersions(TypedDict, total=False):
    Items: Optional[HostedConfigurationVersionSummaryList]
    NextToken: Optional[NextToken]


class ListApplicationsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListConfigurationProfilesRequest(ServiceRequest):
    ApplicationId: Id
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]
    Type: Optional[ConfigurationProfileType]


class ListDeploymentStrategiesRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListDeploymentsRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListEnvironmentsRequest(ServiceRequest):
    ApplicationId: Id
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListHostedConfigurationVersionsRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceArn: Arn


class ResourceTags(TypedDict, total=False):
    Tags: Optional[TagMap]


class StartDeploymentRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id
    DeploymentStrategyId: DeploymentStrategyId
    ConfigurationProfileId: Id
    ConfigurationVersion: Version
    Description: Optional[Description]
    Tags: Optional[TagMap]


class StopDeploymentRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id
    DeploymentNumber: Integer


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceArn: Arn
    Tags: TagMap


class UntagResourceRequest(ServiceRequest):
    ResourceArn: Arn
    TagKeys: TagKeyList


class UpdateApplicationRequest(ServiceRequest):
    ApplicationId: Id
    Name: Optional[Name]
    Description: Optional[Description]


class UpdateConfigurationProfileRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id
    Name: Optional[Name]
    Description: Optional[Description]
    RetrievalRoleArn: Optional[RoleArn]
    Validators: Optional[ValidatorList]


class UpdateDeploymentStrategyRequest(ServiceRequest):
    DeploymentStrategyId: DeploymentStrategyId
    Description: Optional[Description]
    DeploymentDurationInMinutes: Optional[MinutesBetween0And24Hours]
    FinalBakeTimeInMinutes: Optional[MinutesBetween0And24Hours]
    GrowthFactor: Optional[GrowthFactor]
    GrowthType: Optional[GrowthType]


class UpdateEnvironmentRequest(ServiceRequest):
    ApplicationId: Id
    EnvironmentId: Id
    Name: Optional[Name]
    Description: Optional[Description]
    Monitors: Optional[MonitorList]


class ValidateConfigurationRequest(ServiceRequest):
    ApplicationId: Id
    ConfigurationProfileId: Id
    ConfigurationVersion: Version


class AppconfigApi:

    service = "appconfig"
    version = "2019-10-09"

    @handler("CreateApplication")
    def create_application(
        self,
        context: RequestContext,
        name: Name,
        description: Description = None,
        tags: TagMap = None,
    ) -> Application:
        """Creates an application. An application in AppConfig is a logical unit of
        code that provides capabilities for your customers. For example, an
        application can be a microservice that runs on Amazon EC2 instances, a
        mobile application installed by your users, a serverless application
        using Amazon API Gateway and Lambda, or any system you run on behalf of
        others.

        :param name: A name for the application.
        :param description: A description of the application.
        :param tags: Metadata to assign to the application.
        :returns: Application
        :raises BadRequestException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("CreateConfigurationProfile", expand=False)
    def create_configuration_profile(
        self, context: RequestContext, request: CreateConfigurationProfileRequest
    ) -> ConfigurationProfile:
        """Creates a configuration profile, which is information that enables
        AppConfig to access the configuration source. Valid configuration
        sources include the AppConfig hosted configuration store, Amazon Web
        Services Systems Manager (SSM) documents, SSM Parameter Store
        parameters, Amazon S3 objects, or any `integration source
        action <http://docs.aws.amazon.com/codepipeline/latest/userguide/integrations-action-type.html#integrations-source>`__
        supported by CodePipeline. A configuration profile includes the
        following information:

        -  The URI location of the configuration data.

        -  The Identity and Access Management (IAM) role that provides access to
           the configuration data.

        -  A validator for the configuration data. Available validators include
           either a JSON Schema or an Amazon Web Services Lambda function.

        For more information, see `Create a Configuration and a Configuration
        Profile <http://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile.html>`__
        in the *AppConfig User Guide*.

        :param application_id: The application ID.
        :param name: A name for the configuration profile.
        :param location_uri: A URI to locate the configuration.
        :param description: A description of the configuration profile.
        :param retrieval_role_arn: The ARN of an IAM role with permission to access the configuration at
        the specified ``LocationUri``.
        :param validators: A list of methods for validating the configuration.
        :param tags: Metadata to assign to the configuration profile.
        :param type: The type of configurations contained in the profile.
        :returns: ConfigurationProfile
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("CreateDeploymentStrategy")
    def create_deployment_strategy(
        self,
        context: RequestContext,
        name: Name,
        deployment_duration_in_minutes: MinutesBetween0And24Hours,
        growth_factor: GrowthFactor,
        replicate_to: ReplicateTo,
        description: Description = None,
        final_bake_time_in_minutes: MinutesBetween0And24Hours = None,
        growth_type: GrowthType = None,
        tags: TagMap = None,
    ) -> DeploymentStrategy:
        """Creates a deployment strategy that defines important criteria for
        rolling out your configuration to the designated targets. A deployment
        strategy includes the overall duration required, a percentage of targets
        to receive the deployment during each interval, an algorithm that
        defines how percentage grows, and bake time.

        :param name: A name for the deployment strategy.
        :param deployment_duration_in_minutes: Total amount of time for a deployment to last.
        :param growth_factor: The percentage of targets to receive a deployed configuration during
        each interval.
        :param replicate_to: Save the deployment strategy to a Systems Manager (SSM) document.
        :param description: A description of the deployment strategy.
        :param final_bake_time_in_minutes: The amount of time AppConfig monitors for alarms before considering the
        deployment to be complete and no longer eligible for automatic roll
        back.
        :param growth_type: The algorithm used to define how percentage grows over time.
        :param tags: Metadata to assign to the deployment strategy.
        :returns: DeploymentStrategy
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("CreateEnvironment")
    def create_environment(
        self,
        context: RequestContext,
        application_id: Id,
        name: Name,
        description: Description = None,
        monitors: MonitorList = None,
        tags: TagMap = None,
    ) -> Environment:
        """Creates an environment. For each application, you define one or more
        environments. An environment is a logical deployment group of AppConfig
        targets, such as applications in a ``Beta`` or ``Production``
        environment. You can also define environments for application
        subcomponents such as the ``Web``, ``Mobile`` and ``Back-end``
        components for your application. You can configure Amazon CloudWatch
        alarms for each environment. The system monitors alarms during a
        configuration deployment. If an alarm is triggered, the system rolls
        back the configuration.

        :param application_id: The application ID.
        :param name: A name for the environment.
        :param description: A description of the environment.
        :param monitors: Amazon CloudWatch alarms to monitor during the deployment process.
        :param tags: Metadata to assign to the environment.
        :returns: Environment
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("CreateHostedConfigurationVersion")
    def create_hosted_configuration_version(
        self,
        context: RequestContext,
        application_id: Id,
        configuration_profile_id: Id,
        content: Blob,
        content_type: StringWithLengthBetween1And255,
        description: Description = None,
        latest_version_number: Integer = None,
    ) -> HostedConfigurationVersion:
        """Creates a new configuration in the AppConfig hosted configuration store.

        :param application_id: The application ID.
        :param configuration_profile_id: The configuration profile ID.
        :param content: The content of the configuration or the configuration data.
        :param content_type: A standard MIME type describing the format of the configuration content.
        :param description: A description of the configuration.
        :param latest_version_number: An optional locking token used to prevent race conditions from
        overwriting configuration updates when creating a new version.
        :returns: HostedConfigurationVersion
        :raises BadRequestException:
        :raises ServiceQuotaExceededException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises PayloadTooLargeException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DeleteApplication")
    def delete_application(self, context: RequestContext, application_id: Id) -> None:
        """Deletes an application. Deleting an application does not delete a
        configuration from a host.

        :param application_id: The ID of the application to delete.
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteConfigurationProfile")
    def delete_configuration_profile(
        self, context: RequestContext, application_id: Id, configuration_profile_id: Id
    ) -> None:
        """Deletes a configuration profile. Deleting a configuration profile does
        not delete a configuration from a host.

        :param application_id: The application ID that includes the configuration profile you want to
        delete.
        :param configuration_profile_id: The ID of the configuration profile you want to delete.
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteDeploymentStrategy")
    def delete_deployment_strategy(
        self, context: RequestContext, deployment_strategy_id: DeploymentStrategyId
    ) -> None:
        """Deletes a deployment strategy. Deleting a deployment strategy does not
        delete a configuration from a host.

        :param deployment_strategy_id: The ID of the deployment strategy you want to delete.
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteEnvironment")
    def delete_environment(
        self, context: RequestContext, application_id: Id, environment_id: Id
    ) -> None:
        """Deletes an environment. Deleting an environment does not delete a
        configuration from a host.

        :param application_id: The application ID that includes the environment that you want to
        delete.
        :param environment_id: The ID of the environment that you want to delete.
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteHostedConfigurationVersion")
    def delete_hosted_configuration_version(
        self,
        context: RequestContext,
        application_id: Id,
        configuration_profile_id: Id,
        version_number: Integer,
    ) -> None:
        """Deletes a version of a configuration from the AppConfig hosted
        configuration store.

        :param application_id: The application ID.
        :param configuration_profile_id: The configuration profile ID.
        :param version_number: The versions number to delete.
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("GetApplication")
    def get_application(self, context: RequestContext, application_id: Id) -> Application:
        """Retrieves information about an application.

        :param application_id: The ID of the application you want to get.
        :returns: Application
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetConfiguration")
    def get_configuration(
        self,
        context: RequestContext,
        application: StringWithLengthBetween1And64,
        environment: StringWithLengthBetween1And64,
        configuration: StringWithLengthBetween1And64,
        client_id: StringWithLengthBetween1And64,
        client_configuration_version: Version = None,
    ) -> Configuration:
        """Retrieves the latest deployed configuration.

        Note the following important information.

        -  This API action has been deprecated. Calls to receive configuration
           data should use the
           `StartConfigurationSession <https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/API_appconfigdata_StartConfigurationSession.html>`__
           and
           `GetLatestConfiguration <https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/API_appconfigdata_GetLatestConfiguration.html>`__
           APIs instead.

        -  ``GetConfiguration`` is a priced call. For more information, see
           `Pricing <https://aws.amazon.com/systems-manager/pricing/>`__.

        -  AppConfig uses the value of the ``ClientConfigurationVersion``
           parameter to identify the configuration version on your clients. If
           you don’t send ``ClientConfigurationVersion`` with each call to
           ``GetConfiguration``, your clients receive the current configuration.
           You are charged each time your clients receive a configuration.

           To avoid excess charges, we recommend you use the
           `StartConfigurationSession <https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/StartConfigurationSession.html>`__
           and
           `GetLatestConfiguration <https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/GetLatestConfiguration.html>`__
           APIs, which track the client configuration version on your behalf. If
           you choose to continue using ``GetConfiguration``, we recommend that
           you include the ``ClientConfigurationVersion`` value with every call
           to ``GetConfiguration``. The value to use for
           ``ClientConfigurationVersion`` comes from the
           ``ConfigurationVersion`` attribute returned by ``GetConfiguration``
           when there is new or updated data, and should be saved for subsequent
           calls to ``GetConfiguration``.

        :param application: The application to get.
        :param environment: The environment to get.
        :param configuration: The configuration to get.
        :param client_id: The clientId parameter in the following command is a unique,
        user-specified ID to identify the client for the configuration.
        :param client_configuration_version: The configuration version returned in the most recent
        ``GetConfiguration`` response.
        :returns: Configuration
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetConfigurationProfile")
    def get_configuration_profile(
        self, context: RequestContext, application_id: Id, configuration_profile_id: Id
    ) -> ConfigurationProfile:
        """Retrieves information about a configuration profile.

        :param application_id: The ID of the application that includes the configuration profile you
        want to get.
        :param configuration_profile_id: The ID of the configuration profile that you want to get.
        :returns: ConfigurationProfile
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDeployment")
    def get_deployment(
        self,
        context: RequestContext,
        application_id: Id,
        environment_id: Id,
        deployment_number: Integer,
    ) -> Deployment:
        """Retrieves information about a configuration deployment.

        :param application_id: The ID of the application that includes the deployment you want to get.
        :param environment_id: The ID of the environment that includes the deployment you want to get.
        :param deployment_number: The sequence number of the deployment.
        :returns: Deployment
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDeploymentStrategy")
    def get_deployment_strategy(
        self, context: RequestContext, deployment_strategy_id: DeploymentStrategyId
    ) -> DeploymentStrategy:
        """Retrieves information about a deployment strategy. A deployment strategy
        defines important criteria for rolling out your configuration to the
        designated targets. A deployment strategy includes the overall duration
        required, a percentage of targets to receive the deployment during each
        interval, an algorithm that defines how percentage grows, and bake time.

        :param deployment_strategy_id: The ID of the deployment strategy to get.
        :returns: DeploymentStrategy
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetEnvironment")
    def get_environment(
        self, context: RequestContext, application_id: Id, environment_id: Id
    ) -> Environment:
        """Retrieves information about an environment. An environment is a logical
        deployment group of AppConfig applications, such as applications in a
        ``Production`` environment or in an ``EU_Region`` environment. Each
        configuration deployment targets an environment. You can enable one or
        more Amazon CloudWatch alarms for an environment. If an alarm is
        triggered during a deployment, AppConfig roles back the configuration.

        :param application_id: The ID of the application that includes the environment you want to get.
        :param environment_id: The ID of the environment that you want to get.
        :returns: Environment
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetHostedConfigurationVersion")
    def get_hosted_configuration_version(
        self,
        context: RequestContext,
        application_id: Id,
        configuration_profile_id: Id,
        version_number: Integer,
    ) -> HostedConfigurationVersion:
        """Retrieves information about a specific configuration version.

        :param application_id: The application ID.
        :param configuration_profile_id: The configuration profile ID.
        :param version_number: The version.
        :returns: HostedConfigurationVersion
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListApplications")
    def list_applications(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> Applications:
        """Lists all applications in your Amazon Web Services account.

        :param max_results: The maximum number of items to return for this call.
        :param next_token: A token to start the list.
        :returns: Applications
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListConfigurationProfiles", expand=False)
    def list_configuration_profiles(
        self, context: RequestContext, request: ListConfigurationProfilesRequest
    ) -> ConfigurationProfiles:
        """Lists the configuration profiles for an application.

        :param application_id: The application ID.
        :param max_results: The maximum number of items to return for this call.
        :param next_token: A token to start the list.
        :param type: A filter based on the type of configurations that the configuration
        profile contains.
        :returns: ConfigurationProfiles
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListDeploymentStrategies")
    def list_deployment_strategies(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> DeploymentStrategies:
        """Lists deployment strategies.

        :param max_results: The maximum number of items to return for this call.
        :param next_token: A token to start the list.
        :returns: DeploymentStrategies
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListDeployments")
    def list_deployments(
        self,
        context: RequestContext,
        application_id: Id,
        environment_id: Id,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> Deployments:
        """Lists the deployments for an environment in descending deployment number
        order.

        :param application_id: The application ID.
        :param environment_id: The environment ID.
        :param max_results: The maximum number of items that may be returned for this call.
        :param next_token: The token returned by a prior call to this operation indicating the next
        set of results to be returned.
        :returns: Deployments
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListEnvironments")
    def list_environments(
        self,
        context: RequestContext,
        application_id: Id,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> Environments:
        """Lists the environments for an application.

        :param application_id: The application ID.
        :param max_results: The maximum number of items to return for this call.
        :param next_token: A token to start the list.
        :returns: Environments
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListHostedConfigurationVersions")
    def list_hosted_configuration_versions(
        self,
        context: RequestContext,
        application_id: Id,
        configuration_profile_id: Id,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> HostedConfigurationVersions:
        """Lists configurations stored in the AppConfig hosted configuration store
        by version.

        :param application_id: The application ID.
        :param configuration_profile_id: The configuration profile ID.
        :param max_results: The maximum number of items to return for this call.
        :param next_token: A token to start the list.
        :returns: HostedConfigurationVersions
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(self, context: RequestContext, resource_arn: Arn) -> ResourceTags:
        """Retrieves the list of key-value tags assigned to the resource.

        :param resource_arn: The resource ARN.
        :returns: ResourceTags
        :raises ResourceNotFoundException:
        :raises BadRequestException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("StartDeployment")
    def start_deployment(
        self,
        context: RequestContext,
        application_id: Id,
        environment_id: Id,
        deployment_strategy_id: DeploymentStrategyId,
        configuration_profile_id: Id,
        configuration_version: Version,
        description: Description = None,
        tags: TagMap = None,
    ) -> Deployment:
        """Starts a deployment.

        :param application_id: The application ID.
        :param environment_id: The environment ID.
        :param deployment_strategy_id: The deployment strategy ID.
        :param configuration_profile_id: The configuration profile ID.
        :param configuration_version: The configuration version to deploy.
        :param description: A description of the deployment.
        :param tags: Metadata to assign to the deployment.
        :returns: Deployment
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("StopDeployment")
    def stop_deployment(
        self,
        context: RequestContext,
        application_id: Id,
        environment_id: Id,
        deployment_number: Integer,
    ) -> Deployment:
        """Stops a deployment. This API action works only on deployments that have
        a status of ``DEPLOYING``. This action moves the deployment to a status
        of ``ROLLED_BACK``.

        :param application_id: The application ID.
        :param environment_id: The environment ID.
        :param deployment_number: The sequence number of the deployment.
        :returns: Deployment
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(self, context: RequestContext, resource_arn: Arn, tags: TagMap) -> None:
        """Assigns metadata to an AppConfig resource. Tags help organize and
        categorize your AppConfig resources. Each tag consists of a key and an
        optional value, both of which you define. You can specify a maximum of
        50 tags for a resource.

        :param resource_arn: The ARN of the resource for which to retrieve tags.
        :param tags: The key-value string map.
        :raises ResourceNotFoundException:
        :raises BadRequestException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: Arn, tag_keys: TagKeyList
    ) -> None:
        """Deletes a tag key and value from an AppConfig resource.

        :param resource_arn: The ARN of the resource for which to remove tags.
        :param tag_keys: The tag keys to delete.
        :raises ResourceNotFoundException:
        :raises BadRequestException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateApplication")
    def update_application(
        self,
        context: RequestContext,
        application_id: Id,
        name: Name = None,
        description: Description = None,
    ) -> Application:
        """Updates an application.

        :param application_id: The application ID.
        :param name: The name of the application.
        :param description: A description of the application.
        :returns: Application
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateConfigurationProfile")
    def update_configuration_profile(
        self,
        context: RequestContext,
        application_id: Id,
        configuration_profile_id: Id,
        name: Name = None,
        description: Description = None,
        retrieval_role_arn: RoleArn = None,
        validators: ValidatorList = None,
    ) -> ConfigurationProfile:
        """Updates a configuration profile.

        :param application_id: The application ID.
        :param configuration_profile_id: The ID of the configuration profile.
        :param name: The name of the configuration profile.
        :param description: A description of the configuration profile.
        :param retrieval_role_arn: The ARN of an IAM role with permission to access the configuration at
        the specified ``LocationUri``.
        :param validators: A list of methods for validating the configuration.
        :returns: ConfigurationProfile
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateDeploymentStrategy")
    def update_deployment_strategy(
        self,
        context: RequestContext,
        deployment_strategy_id: DeploymentStrategyId,
        description: Description = None,
        deployment_duration_in_minutes: MinutesBetween0And24Hours = None,
        final_bake_time_in_minutes: MinutesBetween0And24Hours = None,
        growth_factor: GrowthFactor = None,
        growth_type: GrowthType = None,
    ) -> DeploymentStrategy:
        """Updates a deployment strategy.

        :param deployment_strategy_id: The deployment strategy ID.
        :param description: A description of the deployment strategy.
        :param deployment_duration_in_minutes: Total amount of time for a deployment to last.
        :param final_bake_time_in_minutes: The amount of time that AppConfig monitors for alarms before considering
        the deployment to be complete and no longer eligible for automatic
        rollback.
        :param growth_factor: The percentage of targets to receive a deployed configuration during
        each interval.
        :param growth_type: The algorithm used to define how percentage grows over time.
        :returns: DeploymentStrategy
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateEnvironment")
    def update_environment(
        self,
        context: RequestContext,
        application_id: Id,
        environment_id: Id,
        name: Name = None,
        description: Description = None,
        monitors: MonitorList = None,
    ) -> Environment:
        """Updates an environment.

        :param application_id: The application ID.
        :param environment_id: The environment ID.
        :param name: The name of the environment.
        :param description: A description of the environment.
        :param monitors: Amazon CloudWatch alarms to monitor during the deployment process.
        :returns: Environment
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ValidateConfiguration")
    def validate_configuration(
        self,
        context: RequestContext,
        application_id: Id,
        configuration_profile_id: Id,
        configuration_version: Version,
    ) -> None:
        """Uses the validators in a configuration profile to validate a
        configuration.

        :param application_id: The application ID.
        :param configuration_profile_id: The configuration profile ID.
        :param configuration_version: The version of the configuration to validate.
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError
