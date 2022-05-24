import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AirflowVersion = str
CloudWatchLogGroupArn = str
ConfigKey = str
ConfigValue = str
Double = float
EnvironmentArn = str
EnvironmentClass = str
EnvironmentName = str
ErrorCode = str
ErrorMessage = str
Hostname = str
IamRoleArn = str
Integer = int
KmsKey = str
ListEnvironmentsInputMaxResultsInteger = int
LoggingEnabled = bool
MaxWorkers = int
MinWorkers = int
NextToken = str
RelativePath = str
S3BucketArn = str
S3ObjectVersion = str
Schedulers = int
SecurityGroupId = str
String = str
SubnetId = str
SyntheticCreateCliTokenResponseToken = str
SyntheticCreateWebLoginTokenResponseToken = str
TagKey = str
TagValue = str
UpdateSource = str
WebserverUrl = str
WeeklyMaintenanceWindowStart = str


class EnvironmentStatus(str):
    CREATING = "CREATING"
    CREATE_FAILED = "CREATE_FAILED"
    AVAILABLE = "AVAILABLE"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    DELETED = "DELETED"
    UNAVAILABLE = "UNAVAILABLE"
    UPDATE_FAILED = "UPDATE_FAILED"


class LoggingLevel(str):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class Unit(str):
    Seconds = "Seconds"
    Microseconds = "Microseconds"
    Milliseconds = "Milliseconds"
    Bytes = "Bytes"
    Kilobytes = "Kilobytes"
    Megabytes = "Megabytes"
    Gigabytes = "Gigabytes"
    Terabytes = "Terabytes"
    Bits = "Bits"
    Kilobits = "Kilobits"
    Megabits = "Megabits"
    Gigabits = "Gigabits"
    Terabits = "Terabits"
    Percent = "Percent"
    Count = "Count"
    Bytes_Second = "Bytes/Second"
    Kilobytes_Second = "Kilobytes/Second"
    Megabytes_Second = "Megabytes/Second"
    Gigabytes_Second = "Gigabytes/Second"
    Terabytes_Second = "Terabytes/Second"
    Bits_Second = "Bits/Second"
    Kilobits_Second = "Kilobits/Second"
    Megabits_Second = "Megabits/Second"
    Gigabits_Second = "Gigabits/Second"
    Terabits_Second = "Terabits/Second"
    Count_Second = "Count/Second"
    None_ = "None"


class UpdateStatus(str):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


class WebserverAccessMode(str):
    PRIVATE_ONLY = "PRIVATE_ONLY"
    PUBLIC_ONLY = "PUBLIC_ONLY"


class AccessDeniedException(ServiceException):
    """Access to the Apache Airflow Web UI or CLI has been denied due to
    insufficient permissions. To learn more, see `Accessing an Amazon MWAA
    environment <https://docs.aws.amazon.com/mwaa/latest/userguide/access-policies.html>`__.
    """

    Message: Optional[String]


class InternalServerException(ServiceException):
    """InternalServerException: An internal error has occurred."""

    message: Optional[String]


class ResourceNotFoundException(ServiceException):
    """ResourceNotFoundException: The resource is not available."""

    message: Optional[String]


class ValidationException(ServiceException):
    """ValidationException: The provided input is not valid."""

    message: Optional[String]


AirflowConfigurationOptions = Dict[ConfigKey, ConfigValue]


class CreateCliTokenRequest(ServiceRequest):
    Name: EnvironmentName


class CreateCliTokenResponse(TypedDict, total=False):
    CliToken: Optional[SyntheticCreateCliTokenResponseToken]
    WebServerHostname: Optional[Hostname]


TagMap = Dict[TagKey, TagValue]
SubnetList = List[SubnetId]
SecurityGroupList = List[SecurityGroupId]


class NetworkConfiguration(TypedDict, total=False):
    """Describes the VPC networking components used to secure and enable
    network traffic between the Amazon Web Services resources for your
    environment. To learn more, see `About networking on Amazon
    MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/networking-about.html>`__.
    """

    SecurityGroupIds: Optional[SecurityGroupList]
    SubnetIds: Optional[SubnetList]


class ModuleLoggingConfigurationInput(TypedDict, total=False):
    """Enables the Apache Airflow log type (e.g. ``DagProcessingLogs``) and
    defines the log level to send to CloudWatch Logs (e.g. ``INFO``).
    """

    Enabled: LoggingEnabled
    LogLevel: LoggingLevel


class LoggingConfigurationInput(TypedDict, total=False):
    """Defines the Apache Airflow log types to send to CloudWatch Logs."""

    DagProcessingLogs: Optional[ModuleLoggingConfigurationInput]
    SchedulerLogs: Optional[ModuleLoggingConfigurationInput]
    TaskLogs: Optional[ModuleLoggingConfigurationInput]
    WebserverLogs: Optional[ModuleLoggingConfigurationInput]
    WorkerLogs: Optional[ModuleLoggingConfigurationInput]


SyntheticCreateEnvironmentInputAirflowConfigurationOptions = Dict[ConfigKey, ConfigValue]


class CreateEnvironmentInput(ServiceRequest):
    """This section contains the Amazon Managed Workflows for Apache Airflow
    (MWAA) API reference documentation to create an environment. For more
    information, see `Get started with Amazon Managed Workflows for Apache
    Airflow <https://docs.aws.amazon.com/mwaa/latest/userguide/get-started.html>`__.
    """

    AirflowConfigurationOptions: Optional[
        SyntheticCreateEnvironmentInputAirflowConfigurationOptions
    ]
    AirflowVersion: Optional[AirflowVersion]
    DagS3Path: RelativePath
    EnvironmentClass: Optional[EnvironmentClass]
    ExecutionRoleArn: IamRoleArn
    KmsKey: Optional[KmsKey]
    LoggingConfiguration: Optional[LoggingConfigurationInput]
    MaxWorkers: Optional[MaxWorkers]
    MinWorkers: Optional[MinWorkers]
    Name: EnvironmentName
    NetworkConfiguration: NetworkConfiguration
    PluginsS3ObjectVersion: Optional[S3ObjectVersion]
    PluginsS3Path: Optional[RelativePath]
    RequirementsS3ObjectVersion: Optional[S3ObjectVersion]
    RequirementsS3Path: Optional[RelativePath]
    Schedulers: Optional[Schedulers]
    SourceBucketArn: S3BucketArn
    Tags: Optional[TagMap]
    WebserverAccessMode: Optional[WebserverAccessMode]
    WeeklyMaintenanceWindowStart: Optional[WeeklyMaintenanceWindowStart]


class CreateEnvironmentOutput(TypedDict, total=False):
    Arn: Optional[EnvironmentArn]


class CreateWebLoginTokenRequest(ServiceRequest):
    Name: EnvironmentName


class CreateWebLoginTokenResponse(TypedDict, total=False):
    WebServerHostname: Optional[Hostname]
    WebToken: Optional[SyntheticCreateWebLoginTokenResponseToken]


CreatedAt = datetime


class DeleteEnvironmentInput(ServiceRequest):
    Name: EnvironmentName


class DeleteEnvironmentOutput(TypedDict, total=False):
    pass


class Dimension(TypedDict, total=False):
    """**Internal only**. Represents the dimensions of a metric. To learn more
    about the metrics published to Amazon CloudWatch, see `Amazon MWAA
    performance metrics in Amazon
    CloudWatch <https://docs.aws.amazon.com/mwaa/latest/userguide/cw-metrics.html>`__.
    """

    Name: String
    Value: String


Dimensions = List[Dimension]


class ModuleLoggingConfiguration(TypedDict, total=False):
    """Describes the Apache Airflow log details for the log type (e.g.
    ``DagProcessingLogs``).
    """

    CloudWatchLogGroupArn: Optional[CloudWatchLogGroupArn]
    Enabled: Optional[LoggingEnabled]
    LogLevel: Optional[LoggingLevel]


class LoggingConfiguration(TypedDict, total=False):
    """Describes the Apache Airflow log types that are published to CloudWatch
    Logs.
    """

    DagProcessingLogs: Optional[ModuleLoggingConfiguration]
    SchedulerLogs: Optional[ModuleLoggingConfiguration]
    TaskLogs: Optional[ModuleLoggingConfiguration]
    WebserverLogs: Optional[ModuleLoggingConfiguration]
    WorkerLogs: Optional[ModuleLoggingConfiguration]


class UpdateError(TypedDict, total=False):
    """Describes the error(s) encountered with the last update of the
    environment.
    """

    ErrorCode: Optional[ErrorCode]
    ErrorMessage: Optional[ErrorMessage]


UpdateCreatedAt = datetime


class LastUpdate(TypedDict, total=False):
    """Describes the status of the last update on the environment, and any
    errors that were encountered.
    """

    CreatedAt: Optional[UpdateCreatedAt]
    Error: Optional[UpdateError]
    Source: Optional[UpdateSource]
    Status: Optional[UpdateStatus]


class Environment(TypedDict, total=False):
    """Describes an Amazon Managed Workflows for Apache Airflow (MWAA)
    environment.
    """

    AirflowConfigurationOptions: Optional[AirflowConfigurationOptions]
    AirflowVersion: Optional[AirflowVersion]
    Arn: Optional[EnvironmentArn]
    CreatedAt: Optional[CreatedAt]
    DagS3Path: Optional[RelativePath]
    EnvironmentClass: Optional[EnvironmentClass]
    ExecutionRoleArn: Optional[IamRoleArn]
    KmsKey: Optional[KmsKey]
    LastUpdate: Optional[LastUpdate]
    LoggingConfiguration: Optional[LoggingConfiguration]
    MaxWorkers: Optional[MaxWorkers]
    MinWorkers: Optional[MinWorkers]
    Name: Optional[EnvironmentName]
    NetworkConfiguration: Optional[NetworkConfiguration]
    PluginsS3ObjectVersion: Optional[S3ObjectVersion]
    PluginsS3Path: Optional[RelativePath]
    RequirementsS3ObjectVersion: Optional[S3ObjectVersion]
    RequirementsS3Path: Optional[RelativePath]
    Schedulers: Optional[Schedulers]
    ServiceRoleArn: Optional[IamRoleArn]
    SourceBucketArn: Optional[S3BucketArn]
    Status: Optional[EnvironmentStatus]
    Tags: Optional[TagMap]
    WebserverAccessMode: Optional[WebserverAccessMode]
    WebserverUrl: Optional[WebserverUrl]
    WeeklyMaintenanceWindowStart: Optional[WeeklyMaintenanceWindowStart]


EnvironmentList = List[EnvironmentName]


class GetEnvironmentInput(ServiceRequest):
    Name: EnvironmentName


class GetEnvironmentOutput(TypedDict, total=False):
    Environment: Optional[Environment]


class ListEnvironmentsInput(ServiceRequest):
    MaxResults: Optional[ListEnvironmentsInputMaxResultsInteger]
    NextToken: Optional[NextToken]


class ListEnvironmentsOutput(TypedDict, total=False):
    Environments: EnvironmentList
    NextToken: Optional[NextToken]


class ListTagsForResourceInput(ServiceRequest):
    ResourceArn: EnvironmentArn


class ListTagsForResourceOutput(TypedDict, total=False):
    Tags: Optional[TagMap]


Timestamp = datetime


class StatisticSet(TypedDict, total=False):
    """**Internal only**. Represents a set of statistics that describe a
    specific metric. To learn more about the metrics published to Amazon
    CloudWatch, see `Amazon MWAA performance metrics in Amazon
    CloudWatch <https://docs.aws.amazon.com/mwaa/latest/userguide/cw-metrics.html>`__.
    """

    Maximum: Optional[Double]
    Minimum: Optional[Double]
    SampleCount: Optional[Integer]
    Sum: Optional[Double]


class MetricDatum(TypedDict, total=False):
    """**Internal only**. Collects Apache Airflow metrics. To learn more about
    the metrics published to Amazon CloudWatch, see `Amazon MWAA performance
    metrics in Amazon
    CloudWatch <https://docs.aws.amazon.com/mwaa/latest/userguide/cw-metrics.html>`__.
    """

    Dimensions: Optional[Dimensions]
    MetricName: String
    StatisticValues: Optional[StatisticSet]
    Timestamp: Timestamp
    Unit: Optional[Unit]
    Value: Optional[Double]


MetricData = List[MetricDatum]


class PublishMetricsInput(ServiceRequest):
    EnvironmentName: EnvironmentName
    MetricData: MetricData


class PublishMetricsOutput(TypedDict, total=False):
    pass


SyntheticUpdateEnvironmentInputAirflowConfigurationOptions = Dict[ConfigKey, ConfigValue]
TagKeyList = List[TagKey]


class TagResourceInput(ServiceRequest):
    ResourceArn: EnvironmentArn
    Tags: TagMap


class TagResourceOutput(TypedDict, total=False):
    pass


class UntagResourceInput(ServiceRequest):
    ResourceArn: EnvironmentArn
    tagKeys: TagKeyList


class UntagResourceOutput(TypedDict, total=False):
    pass


class UpdateNetworkConfigurationInput(TypedDict, total=False):
    """Defines the VPC networking components used to secure and enable network
    traffic between the Amazon Web Services resources for your environment.
    To learn more, see `About networking on Amazon
    MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/networking-about.html>`__.
    """

    SecurityGroupIds: SecurityGroupList


class UpdateEnvironmentInput(ServiceRequest):
    AirflowConfigurationOptions: Optional[
        SyntheticUpdateEnvironmentInputAirflowConfigurationOptions
    ]
    AirflowVersion: Optional[AirflowVersion]
    DagS3Path: Optional[RelativePath]
    EnvironmentClass: Optional[EnvironmentClass]
    ExecutionRoleArn: Optional[IamRoleArn]
    LoggingConfiguration: Optional[LoggingConfigurationInput]
    MaxWorkers: Optional[MaxWorkers]
    MinWorkers: Optional[MinWorkers]
    Name: EnvironmentName
    NetworkConfiguration: Optional[UpdateNetworkConfigurationInput]
    PluginsS3ObjectVersion: Optional[S3ObjectVersion]
    PluginsS3Path: Optional[RelativePath]
    RequirementsS3ObjectVersion: Optional[S3ObjectVersion]
    RequirementsS3Path: Optional[RelativePath]
    Schedulers: Optional[Schedulers]
    SourceBucketArn: Optional[S3BucketArn]
    WebserverAccessMode: Optional[WebserverAccessMode]
    WeeklyMaintenanceWindowStart: Optional[WeeklyMaintenanceWindowStart]


class UpdateEnvironmentOutput(TypedDict, total=False):
    Arn: Optional[EnvironmentArn]


class MwaaApi:

    service = "mwaa"
    version = "2020-07-01"

    @handler("CreateCliToken")
    def create_cli_token(
        self, context: RequestContext, name: EnvironmentName
    ) -> CreateCliTokenResponse:
        """Creates a CLI token for the Airflow CLI. To learn more, see `Creating an
        Apache Airflow CLI
        token <https://docs.aws.amazon.com/mwaa/latest/userguide/call-mwaa-apis-cli.html>`__.

        :param name: The name of the Amazon MWAA environment.
        :returns: CreateCliTokenResponse
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("CreateEnvironment")
    def create_environment(
        self,
        context: RequestContext,
        dag_s3_path: RelativePath,
        execution_role_arn: IamRoleArn,
        name: EnvironmentName,
        network_configuration: NetworkConfiguration,
        source_bucket_arn: S3BucketArn,
        airflow_configuration_options: SyntheticCreateEnvironmentInputAirflowConfigurationOptions = None,
        airflow_version: AirflowVersion = None,
        environment_class: EnvironmentClass = None,
        kms_key: KmsKey = None,
        logging_configuration: LoggingConfigurationInput = None,
        max_workers: MaxWorkers = None,
        min_workers: MinWorkers = None,
        plugins_s3_object_version: S3ObjectVersion = None,
        plugins_s3_path: RelativePath = None,
        requirements_s3_object_version: S3ObjectVersion = None,
        requirements_s3_path: RelativePath = None,
        schedulers: Schedulers = None,
        tags: TagMap = None,
        webserver_access_mode: WebserverAccessMode = None,
        weekly_maintenance_window_start: WeeklyMaintenanceWindowStart = None,
    ) -> CreateEnvironmentOutput:
        """Creates an Amazon Managed Workflows for Apache Airflow (MWAA)
        environment.

        :param dag_s3_path: The relative path to the DAGs folder on your Amazon S3 bucket.
        :param execution_role_arn: The Amazon Resource Name (ARN) of the execution role for your
        environment.
        :param name: The name of the Amazon MWAA environment.
        :param network_configuration: The VPC networking components used to secure and enable network traffic
        between the Amazon Web Services resources for your environment.
        :param source_bucket_arn: The Amazon Resource Name (ARN) of the Amazon S3 bucket where your DAG
        code and supporting files are stored.
        :param airflow_configuration_options: A list of key-value pairs containing the Apache Airflow configuration
        options you want to attach to your environment.
        :param airflow_version: The Apache Airflow version for your environment.
        :param environment_class: The environment class type.
        :param kms_key: The Amazon Web Services Key Management Service (KMS) key to encrypt the
        data in your environment.
        :param logging_configuration: Defines the Apache Airflow logs to send to CloudWatch Logs.
        :param max_workers: The maximum number of workers that you want to run in your environment.
        :param min_workers: The minimum number of workers that you want to run in your environment.
        :param plugins_s3_object_version: The version of the plugins.
        :param plugins_s3_path: The relative path to the ``plugins.
        :param requirements_s3_object_version: The version of the requirements.
        :param requirements_s3_path: The relative path to the ``requirements.
        :param schedulers: The number of Apache Airflow schedulers to run in your environment.
        :param tags: The key-value tag pairs you want to associate to your environment.
        :param webserver_access_mode: The Apache Airflow *Web server* access mode.
        :param weekly_maintenance_window_start: The day and time of the week in Coordinated Universal Time (UTC) 24-hour
        standard time to start weekly maintenance updates of your environment in
        the following format: ``DAY:HH:MM``.
        :returns: CreateEnvironmentOutput
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("CreateWebLoginToken")
    def create_web_login_token(
        self, context: RequestContext, name: EnvironmentName
    ) -> CreateWebLoginTokenResponse:
        """Creates a web login token for the Airflow Web UI. To learn more, see
        `Creating an Apache Airflow web login
        token <https://docs.aws.amazon.com/mwaa/latest/userguide/call-mwaa-apis-web.html>`__.

        :param name: The name of the Amazon MWAA environment.
        :returns: CreateWebLoginTokenResponse
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DeleteEnvironment")
    def delete_environment(
        self, context: RequestContext, name: EnvironmentName
    ) -> DeleteEnvironmentOutput:
        """Deletes an Amazon Managed Workflows for Apache Airflow (MWAA)
        environment.

        :param name: The name of the Amazon MWAA environment.
        :returns: DeleteEnvironmentOutput
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("GetEnvironment")
    def get_environment(
        self, context: RequestContext, name: EnvironmentName
    ) -> GetEnvironmentOutput:
        """Describes an Amazon Managed Workflows for Apache Airflow (MWAA)
        environment.

        :param name: The name of the Amazon MWAA environment.
        :returns: GetEnvironmentOutput
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListEnvironments")
    def list_environments(
        self,
        context: RequestContext,
        max_results: ListEnvironmentsInputMaxResultsInteger = None,
        next_token: NextToken = None,
    ) -> ListEnvironmentsOutput:
        """Lists the Amazon Managed Workflows for Apache Airflow (MWAA)
        environments.

        :param max_results: The maximum number of results to retrieve per page.
        :param next_token: Retrieves the next page of the results.
        :returns: ListEnvironmentsOutput
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: EnvironmentArn
    ) -> ListTagsForResourceOutput:
        """Lists the key-value tag pairs associated to the Amazon Managed Workflows
        for Apache Airflow (MWAA) environment. For example,
        ``"Environment": "Staging"``.

        :param resource_arn: The Amazon Resource Name (ARN) of the Amazon MWAA environment.
        :returns: ListTagsForResourceOutput
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("PublishMetrics")
    def publish_metrics(
        self, context: RequestContext, environment_name: EnvironmentName, metric_data: MetricData
    ) -> PublishMetricsOutput:
        """**Internal only**. Publishes environment health metrics to Amazon
        CloudWatch.

        :param environment_name: **Internal only**.
        :param metric_data: **Internal only**.
        :returns: PublishMetricsOutput
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: EnvironmentArn, tags: TagMap
    ) -> TagResourceOutput:
        """Associates key-value tag pairs to your Amazon Managed Workflows for
        Apache Airflow (MWAA) environment.

        :param resource_arn: The Amazon Resource Name (ARN) of the Amazon MWAA environment.
        :param tags: The key-value tag pairs you want to associate to your environment.
        :returns: TagResourceOutput
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: EnvironmentArn, tag_keys: TagKeyList
    ) -> UntagResourceOutput:
        """Removes key-value tag pairs associated to your Amazon Managed Workflows
        for Apache Airflow (MWAA) environment. For example,
        ``"Environment": "Staging"``.

        :param resource_arn: The Amazon Resource Name (ARN) of the Amazon MWAA environment.
        :param tag_keys: The key-value tag pair you want to remove.
        :returns: UntagResourceOutput
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("UpdateEnvironment")
    def update_environment(
        self,
        context: RequestContext,
        name: EnvironmentName,
        airflow_configuration_options: SyntheticUpdateEnvironmentInputAirflowConfigurationOptions = None,
        airflow_version: AirflowVersion = None,
        dag_s3_path: RelativePath = None,
        environment_class: EnvironmentClass = None,
        execution_role_arn: IamRoleArn = None,
        logging_configuration: LoggingConfigurationInput = None,
        max_workers: MaxWorkers = None,
        min_workers: MinWorkers = None,
        network_configuration: UpdateNetworkConfigurationInput = None,
        plugins_s3_object_version: S3ObjectVersion = None,
        plugins_s3_path: RelativePath = None,
        requirements_s3_object_version: S3ObjectVersion = None,
        requirements_s3_path: RelativePath = None,
        schedulers: Schedulers = None,
        source_bucket_arn: S3BucketArn = None,
        webserver_access_mode: WebserverAccessMode = None,
        weekly_maintenance_window_start: WeeklyMaintenanceWindowStart = None,
    ) -> UpdateEnvironmentOutput:
        """Updates an Amazon Managed Workflows for Apache Airflow (MWAA)
        environment.

        :param name: The name of your Amazon MWAA environment.
        :param airflow_configuration_options: A list of key-value pairs containing the Apache Airflow configuration
        options you want to attach to your environment.
        :param airflow_version: The Apache Airflow version for your environment.
        :param dag_s3_path: The relative path to the DAGs folder on your Amazon S3 bucket.
        :param environment_class: The environment class type.
        :param execution_role_arn: The Amazon Resource Name (ARN) of the execution role in IAM that allows
        MWAA to access Amazon Web Services resources in your environment.
        :param logging_configuration: The Apache Airflow log types to send to CloudWatch Logs.
        :param max_workers: The maximum number of workers that you want to run in your environment.
        :param min_workers: The minimum number of workers that you want to run in your environment.
        :param network_configuration: The VPC networking components used to secure and enable network traffic
        between the Amazon Web Services resources for your environment.
        :param plugins_s3_object_version: The version of the plugins.
        :param plugins_s3_path: The relative path to the ``plugins.
        :param requirements_s3_object_version: The version of the requirements.
        :param requirements_s3_path: The relative path to the ``requirements.
        :param schedulers: The number of Apache Airflow schedulers to run in your Amazon MWAA
        environment.
        :param source_bucket_arn: The Amazon Resource Name (ARN) of the Amazon S3 bucket where your DAG
        code and supporting files are stored.
        :param webserver_access_mode: The Apache Airflow *Web server* access mode.
        :param weekly_maintenance_window_start: The day and time of the week in Coordinated Universal Time (UTC) 24-hour
        standard time to start weekly maintenance updates of your environment in
        the following format: ``DAY:HH:MM``.
        :returns: UpdateEnvironmentOutput
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError
