import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccessToken = str
ActiveJobId = str
AppArn = str
AppId = str
ArtifactFileName = str
ArtifactId = str
ArtifactUrl = str
ArtifactsUrl = str
AssociatedResource = str
AutoBranchCreationPattern = str
AutoSubDomainCreationPattern = str
AutoSubDomainIAMRole = str
BackendEnvironmentArn = str
BasicAuthCredentials = str
BranchArn = str
BranchName = str
BuildSpec = str
CertificateVerificationDNSRecord = str
Code = str
CommitId = str
CommitMessage = str
Condition = str
Context = str
CustomDomain = str
CustomHeaders = str
DNSRecord = str
DefaultDomain = str
DeploymentArtifacts = str
Description = str
DisplayName = str
DomainAssociationArn = str
DomainName = str
DomainPrefix = str
EnableAutoBranchCreation = bool
EnableAutoBuild = bool
EnableAutoSubDomain = bool
EnableBasicAuth = bool
EnableBranchAutoBuild = bool
EnableBranchAutoDeletion = bool
EnableNotification = bool
EnablePerformanceMode = bool
EnablePullRequestPreview = bool
EnvKey = str
EnvValue = str
EnvironmentName = str
ErrorMessage = str
FileName = str
Framework = str
JobArn = str
JobId = str
JobReason = str
LogUrl = str
MD5Hash = str
MaxResults = int
Name = str
NextToken = str
OauthToken = str
PullRequestEnvironmentName = str
Repository = str
ResourceArn = str
ServiceRoleArn = str
Source = str
SourceUrl = str
StackName = str
Status = str
StatusReason = str
StepName = str
TTL = str
TagKey = str
TagValue = str
Target = str
TestArtifactsUrl = str
TestConfigUrl = str
ThumbnailName = str
ThumbnailUrl = str
TotalNumberOfJobs = str
UploadUrl = str
Verified = bool
WebhookArn = str
WebhookId = str
WebhookUrl = str


class DomainStatus(str):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    IN_PROGRESS = "IN_PROGRESS"
    AVAILABLE = "AVAILABLE"
    PENDING_DEPLOYMENT = "PENDING_DEPLOYMENT"
    FAILED = "FAILED"
    CREATING = "CREATING"
    REQUESTING_CERTIFICATE = "REQUESTING_CERTIFICATE"
    UPDATING = "UPDATING"


class JobStatus(str):
    PENDING = "PENDING"
    PROVISIONING = "PROVISIONING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEED = "SUCCEED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


class JobType(str):
    RELEASE = "RELEASE"
    RETRY = "RETRY"
    MANUAL = "MANUAL"
    WEB_HOOK = "WEB_HOOK"


class Platform(str):
    WEB = "WEB"
    WEB_DYNAMIC = "WEB_DYNAMIC"


class RepositoryCloneMethod(str):
    SSH = "SSH"
    TOKEN = "TOKEN"
    SIGV4 = "SIGV4"


class Stage(str):
    PRODUCTION = "PRODUCTION"
    BETA = "BETA"
    DEVELOPMENT = "DEVELOPMENT"
    EXPERIMENTAL = "EXPERIMENTAL"
    PULL_REQUEST = "PULL_REQUEST"


class BadRequestException(ServiceException):
    """A request contains unexpected data."""

    message: Optional[ErrorMessage]


class DependentServiceFailureException(ServiceException):
    """An operation failed because a dependent service threw an exception."""

    message: Optional[ErrorMessage]


class InternalFailureException(ServiceException):
    """The service failed to perform an operation due to an internal issue."""

    message: Optional[ErrorMessage]


class LimitExceededException(ServiceException):
    """A resource could not be created because service quotas were exceeded."""

    message: Optional[ErrorMessage]


class NotFoundException(ServiceException):
    """An entity was not found during an operation."""

    message: Optional[ErrorMessage]


class ResourceNotFoundException(ServiceException):
    """An operation failed due to a non-existent resource."""

    code: Code
    message: ErrorMessage


class UnauthorizedException(ServiceException):
    """An operation failed due to a lack of access."""

    message: Optional[ErrorMessage]


EnvironmentVariables = Dict[EnvKey, EnvValue]


class AutoBranchCreationConfig(TypedDict, total=False):
    """Describes the automated branch creation configuration."""

    stage: Optional[Stage]
    framework: Optional[Framework]
    enableAutoBuild: Optional[EnableAutoBuild]
    environmentVariables: Optional[EnvironmentVariables]
    basicAuthCredentials: Optional[BasicAuthCredentials]
    enableBasicAuth: Optional[EnableBasicAuth]
    enablePerformanceMode: Optional[EnablePerformanceMode]
    buildSpec: Optional[BuildSpec]
    enablePullRequestPreview: Optional[EnablePullRequestPreview]
    pullRequestEnvironmentName: Optional[PullRequestEnvironmentName]


AutoBranchCreationPatterns = List[AutoBranchCreationPattern]
LastDeployTime = datetime


class ProductionBranch(TypedDict, total=False):
    """Describes the information about a production branch for an Amplify app."""

    lastDeployTime: Optional[LastDeployTime]
    status: Optional[Status]
    thumbnailUrl: Optional[ThumbnailUrl]
    branchName: Optional[BranchName]


class CustomRule(TypedDict, total=False):
    """Describes a custom rewrite or redirect rule."""

    source: Source
    target: Target
    status: Optional[Status]
    condition: Optional[Condition]


CustomRules = List[CustomRule]
UpdateTime = datetime
CreateTime = datetime
TagMap = Dict[TagKey, TagValue]


class App(TypedDict, total=False):
    """Represents the different branches of a repository for building,
    deploying, and hosting an Amplify app.
    """

    appId: AppId
    appArn: AppArn
    name: Name
    tags: Optional[TagMap]
    description: Description
    repository: Repository
    platform: Platform
    createTime: CreateTime
    updateTime: UpdateTime
    iamServiceRoleArn: Optional[ServiceRoleArn]
    environmentVariables: EnvironmentVariables
    defaultDomain: DefaultDomain
    enableBranchAutoBuild: EnableBranchAutoBuild
    enableBranchAutoDeletion: Optional[EnableBranchAutoDeletion]
    enableBasicAuth: EnableBasicAuth
    basicAuthCredentials: Optional[BasicAuthCredentials]
    customRules: Optional[CustomRules]
    productionBranch: Optional[ProductionBranch]
    buildSpec: Optional[BuildSpec]
    customHeaders: Optional[CustomHeaders]
    enableAutoBranchCreation: Optional[EnableAutoBranchCreation]
    autoBranchCreationPatterns: Optional[AutoBranchCreationPatterns]
    autoBranchCreationConfig: Optional[AutoBranchCreationConfig]
    repositoryCloneMethod: Optional[RepositoryCloneMethod]


Apps = List[App]


class Artifact(TypedDict, total=False):
    """Describes an artifact."""

    artifactFileName: ArtifactFileName
    artifactId: ArtifactId


Artifacts = List[Artifact]
AssociatedResources = List[AssociatedResource]
AutoSubDomainCreationPatterns = List[AutoSubDomainCreationPattern]


class BackendEnvironment(TypedDict, total=False):
    """Describes the backend environment for an Amplify app."""

    backendEnvironmentArn: BackendEnvironmentArn
    environmentName: EnvironmentName
    stackName: Optional[StackName]
    deploymentArtifacts: Optional[DeploymentArtifacts]
    createTime: CreateTime
    updateTime: UpdateTime


BackendEnvironments = List[BackendEnvironment]
CustomDomains = List[CustomDomain]


class Branch(TypedDict, total=False):
    """The branch for an Amplify app, which maps to a third-party repository
    branch.
    """

    branchArn: BranchArn
    branchName: BranchName
    description: Description
    tags: Optional[TagMap]
    stage: Stage
    displayName: DisplayName
    enableNotification: EnableNotification
    createTime: CreateTime
    updateTime: UpdateTime
    environmentVariables: EnvironmentVariables
    enableAutoBuild: EnableAutoBuild
    customDomains: CustomDomains
    framework: Framework
    activeJobId: ActiveJobId
    totalNumberOfJobs: TotalNumberOfJobs
    enableBasicAuth: EnableBasicAuth
    enablePerformanceMode: Optional[EnablePerformanceMode]
    thumbnailUrl: Optional[ThumbnailUrl]
    basicAuthCredentials: Optional[BasicAuthCredentials]
    buildSpec: Optional[BuildSpec]
    ttl: TTL
    associatedResources: Optional[AssociatedResources]
    enablePullRequestPreview: EnablePullRequestPreview
    pullRequestEnvironmentName: Optional[PullRequestEnvironmentName]
    destinationBranch: Optional[BranchName]
    sourceBranch: Optional[BranchName]
    backendEnvironmentArn: Optional[BackendEnvironmentArn]


Branches = List[Branch]
CommitTime = datetime


class CreateAppRequest(ServiceRequest):
    """The request structure used to create apps in Amplify."""

    name: Name
    description: Optional[Description]
    repository: Optional[Repository]
    platform: Optional[Platform]
    iamServiceRoleArn: Optional[ServiceRoleArn]
    oauthToken: Optional[OauthToken]
    accessToken: Optional[AccessToken]
    environmentVariables: Optional[EnvironmentVariables]
    enableBranchAutoBuild: Optional[EnableBranchAutoBuild]
    enableBranchAutoDeletion: Optional[EnableBranchAutoDeletion]
    enableBasicAuth: Optional[EnableBasicAuth]
    basicAuthCredentials: Optional[BasicAuthCredentials]
    customRules: Optional[CustomRules]
    tags: Optional[TagMap]
    buildSpec: Optional[BuildSpec]
    customHeaders: Optional[CustomHeaders]
    enableAutoBranchCreation: Optional[EnableAutoBranchCreation]
    autoBranchCreationPatterns: Optional[AutoBranchCreationPatterns]
    autoBranchCreationConfig: Optional[AutoBranchCreationConfig]


class CreateAppResult(TypedDict, total=False):
    app: App


class CreateBackendEnvironmentRequest(ServiceRequest):
    """The request structure for the backend environment create request."""

    appId: AppId
    environmentName: EnvironmentName
    stackName: Optional[StackName]
    deploymentArtifacts: Optional[DeploymentArtifacts]


class CreateBackendEnvironmentResult(TypedDict, total=False):
    """The result structure for the create backend environment request."""

    backendEnvironment: BackendEnvironment


class CreateBranchRequest(ServiceRequest):
    """The request structure for the create branch request."""

    appId: AppId
    branchName: BranchName
    description: Optional[Description]
    stage: Optional[Stage]
    framework: Optional[Framework]
    enableNotification: Optional[EnableNotification]
    enableAutoBuild: Optional[EnableAutoBuild]
    environmentVariables: Optional[EnvironmentVariables]
    basicAuthCredentials: Optional[BasicAuthCredentials]
    enableBasicAuth: Optional[EnableBasicAuth]
    enablePerformanceMode: Optional[EnablePerformanceMode]
    tags: Optional[TagMap]
    buildSpec: Optional[BuildSpec]
    ttl: Optional[TTL]
    displayName: Optional[DisplayName]
    enablePullRequestPreview: Optional[EnablePullRequestPreview]
    pullRequestEnvironmentName: Optional[PullRequestEnvironmentName]
    backendEnvironmentArn: Optional[BackendEnvironmentArn]


class CreateBranchResult(TypedDict, total=False):
    """The result structure for create branch request."""

    branch: Branch


FileMap = Dict[FileName, MD5Hash]


class CreateDeploymentRequest(ServiceRequest):
    """The request structure for the create a new deployment request."""

    appId: AppId
    branchName: BranchName
    fileMap: Optional[FileMap]


FileUploadUrls = Dict[FileName, UploadUrl]


class CreateDeploymentResult(TypedDict, total=False):
    """The result structure for the create a new deployment request."""

    jobId: Optional[JobId]
    fileUploadUrls: FileUploadUrls
    zipUploadUrl: UploadUrl


class SubDomainSetting(TypedDict, total=False):
    """Describes the settings for the subdomain."""

    prefix: DomainPrefix
    branchName: BranchName


SubDomainSettings = List[SubDomainSetting]


class CreateDomainAssociationRequest(ServiceRequest):
    """The request structure for the create domain association request."""

    appId: AppId
    domainName: DomainName
    enableAutoSubDomain: Optional[EnableAutoSubDomain]
    subDomainSettings: SubDomainSettings
    autoSubDomainCreationPatterns: Optional[AutoSubDomainCreationPatterns]
    autoSubDomainIAMRole: Optional[AutoSubDomainIAMRole]


class SubDomain(TypedDict, total=False):
    """The subdomain for the domain association."""

    subDomainSetting: SubDomainSetting
    verified: Verified
    dnsRecord: DNSRecord


SubDomains = List[SubDomain]


class DomainAssociation(TypedDict, total=False):
    """Describes a domain association that associates a custom domain with an
    Amplify app.
    """

    domainAssociationArn: DomainAssociationArn
    domainName: DomainName
    enableAutoSubDomain: EnableAutoSubDomain
    autoSubDomainCreationPatterns: Optional[AutoSubDomainCreationPatterns]
    autoSubDomainIAMRole: Optional[AutoSubDomainIAMRole]
    domainStatus: DomainStatus
    statusReason: StatusReason
    certificateVerificationDNSRecord: Optional[CertificateVerificationDNSRecord]
    subDomains: SubDomains


class CreateDomainAssociationResult(TypedDict, total=False):
    """The result structure for the create domain association request."""

    domainAssociation: DomainAssociation


class CreateWebhookRequest(ServiceRequest):
    """The request structure for the create webhook request."""

    appId: AppId
    branchName: BranchName
    description: Optional[Description]


class Webhook(TypedDict, total=False):
    """Describes a webhook that connects repository events to an Amplify app."""

    webhookArn: WebhookArn
    webhookId: WebhookId
    webhookUrl: WebhookUrl
    branchName: BranchName
    description: Description
    createTime: CreateTime
    updateTime: UpdateTime


class CreateWebhookResult(TypedDict, total=False):
    """The result structure for the create webhook request."""

    webhook: Webhook


class DeleteAppRequest(ServiceRequest):
    """Describes the request structure for the delete app request."""

    appId: AppId


class DeleteAppResult(TypedDict, total=False):
    """The result structure for the delete app request."""

    app: App


class DeleteBackendEnvironmentRequest(ServiceRequest):
    """The request structure for the delete backend environment request."""

    appId: AppId
    environmentName: EnvironmentName


class DeleteBackendEnvironmentResult(TypedDict, total=False):
    """The result structure of the delete backend environment result."""

    backendEnvironment: BackendEnvironment


class DeleteBranchRequest(ServiceRequest):
    """The request structure for the delete branch request."""

    appId: AppId
    branchName: BranchName


class DeleteBranchResult(TypedDict, total=False):
    """The result structure for the delete branch request."""

    branch: Branch


class DeleteDomainAssociationRequest(ServiceRequest):
    """The request structure for the delete domain association request."""

    appId: AppId
    domainName: DomainName


class DeleteDomainAssociationResult(TypedDict, total=False):
    domainAssociation: DomainAssociation


class DeleteJobRequest(ServiceRequest):
    """The request structure for the delete job request."""

    appId: AppId
    branchName: BranchName
    jobId: JobId


EndTime = datetime
StartTime = datetime


class JobSummary(TypedDict, total=False):
    """Describes the summary for an execution job for an Amplify app."""

    jobArn: JobArn
    jobId: JobId
    commitId: CommitId
    commitMessage: CommitMessage
    commitTime: CommitTime
    startTime: StartTime
    status: JobStatus
    endTime: Optional[EndTime]
    jobType: JobType


class DeleteJobResult(TypedDict, total=False):
    """The result structure for the delete job request."""

    jobSummary: JobSummary


class DeleteWebhookRequest(ServiceRequest):
    """The request structure for the delete webhook request."""

    webhookId: WebhookId


class DeleteWebhookResult(TypedDict, total=False):
    """The result structure for the delete webhook request."""

    webhook: Webhook


DomainAssociations = List[DomainAssociation]


class GenerateAccessLogsRequest(ServiceRequest):
    """The request structure for the generate access logs request."""

    startTime: Optional[StartTime]
    endTime: Optional[EndTime]
    domainName: DomainName
    appId: AppId


class GenerateAccessLogsResult(TypedDict, total=False):
    """The result structure for the generate access logs request."""

    logUrl: Optional[LogUrl]


class GetAppRequest(ServiceRequest):
    """The request structure for the get app request."""

    appId: AppId


class GetAppResult(TypedDict, total=False):
    app: App


class GetArtifactUrlRequest(ServiceRequest):
    """Returns the request structure for the get artifact request."""

    artifactId: ArtifactId


class GetArtifactUrlResult(TypedDict, total=False):
    """Returns the result structure for the get artifact request."""

    artifactId: ArtifactId
    artifactUrl: ArtifactUrl


class GetBackendEnvironmentRequest(ServiceRequest):
    """The request structure for the get backend environment request."""

    appId: AppId
    environmentName: EnvironmentName


class GetBackendEnvironmentResult(TypedDict, total=False):
    """The result structure for the get backend environment result."""

    backendEnvironment: BackendEnvironment


class GetBranchRequest(ServiceRequest):
    """The request structure for the get branch request."""

    appId: AppId
    branchName: BranchName


class GetBranchResult(TypedDict, total=False):
    branch: Branch


class GetDomainAssociationRequest(ServiceRequest):
    """The request structure for the get domain association request."""

    appId: AppId
    domainName: DomainName


class GetDomainAssociationResult(TypedDict, total=False):
    """The result structure for the get domain association request."""

    domainAssociation: DomainAssociation


class GetJobRequest(ServiceRequest):
    """The request structure for the get job request."""

    appId: AppId
    branchName: BranchName
    jobId: JobId


Screenshots = Dict[ThumbnailName, ThumbnailUrl]


class Step(TypedDict, total=False):
    """Describes an execution step, for an execution job, for an Amplify app."""

    stepName: StepName
    startTime: StartTime
    status: JobStatus
    endTime: EndTime
    logUrl: Optional[LogUrl]
    artifactsUrl: Optional[ArtifactsUrl]
    testArtifactsUrl: Optional[TestArtifactsUrl]
    testConfigUrl: Optional[TestConfigUrl]
    screenshots: Optional[Screenshots]
    statusReason: Optional[StatusReason]
    context: Optional[Context]


Steps = List[Step]


class Job(TypedDict, total=False):
    """Describes an execution job for an Amplify app."""

    summary: JobSummary
    steps: Steps


class GetJobResult(TypedDict, total=False):
    job: Job


class GetWebhookRequest(ServiceRequest):
    """The request structure for the get webhook request."""

    webhookId: WebhookId


class GetWebhookResult(TypedDict, total=False):
    """The result structure for the get webhook request."""

    webhook: Webhook


JobSummaries = List[JobSummary]


class ListAppsRequest(ServiceRequest):
    """The request structure for the list apps request."""

    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListAppsResult(TypedDict, total=False):
    """The result structure for an Amplify app list request."""

    apps: Apps
    nextToken: Optional[NextToken]


class ListArtifactsRequest(ServiceRequest):
    """Describes the request structure for the list artifacts request."""

    appId: AppId
    branchName: BranchName
    jobId: JobId
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListArtifactsResult(TypedDict, total=False):
    """The result structure for the list artifacts request."""

    artifacts: Artifacts
    nextToken: Optional[NextToken]


class ListBackendEnvironmentsRequest(ServiceRequest):
    """The request structure for the list backend environments request."""

    appId: AppId
    environmentName: Optional[EnvironmentName]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListBackendEnvironmentsResult(TypedDict, total=False):
    """The result structure for the list backend environments result."""

    backendEnvironments: BackendEnvironments
    nextToken: Optional[NextToken]


class ListBranchesRequest(ServiceRequest):
    """The request structure for the list branches request."""

    appId: AppId
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListBranchesResult(TypedDict, total=False):
    """The result structure for the list branches request."""

    branches: Branches
    nextToken: Optional[NextToken]


class ListDomainAssociationsRequest(ServiceRequest):
    """The request structure for the list domain associations request."""

    appId: AppId
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListDomainAssociationsResult(TypedDict, total=False):
    """The result structure for the list domain association request."""

    domainAssociations: DomainAssociations
    nextToken: Optional[NextToken]


class ListJobsRequest(ServiceRequest):
    """The request structure for the list jobs request."""

    appId: AppId
    branchName: BranchName
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListJobsResult(TypedDict, total=False):
    """The maximum number of records to list in a single response."""

    jobSummaries: JobSummaries
    nextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    """The request structure to use to list tags for a resource."""

    resourceArn: ResourceArn


class ListTagsForResourceResponse(TypedDict, total=False):
    """The response for the list tags for resource request."""

    tags: Optional[TagMap]


class ListWebhooksRequest(ServiceRequest):
    """The request structure for the list webhooks request."""

    appId: AppId
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


Webhooks = List[Webhook]


class ListWebhooksResult(TypedDict, total=False):
    """The result structure for the list webhooks request."""

    webhooks: Webhooks
    nextToken: Optional[NextToken]


class StartDeploymentRequest(ServiceRequest):
    """The request structure for the start a deployment request."""

    appId: AppId
    branchName: BranchName
    jobId: Optional[JobId]
    sourceUrl: Optional[SourceUrl]


class StartDeploymentResult(TypedDict, total=False):
    """The result structure for the start a deployment request."""

    jobSummary: JobSummary


class StartJobRequest(ServiceRequest):
    """The request structure for the start job request."""

    appId: AppId
    branchName: BranchName
    jobId: Optional[JobId]
    jobType: JobType
    jobReason: Optional[JobReason]
    commitId: Optional[CommitId]
    commitMessage: Optional[CommitMessage]
    commitTime: Optional[CommitTime]


class StartJobResult(TypedDict, total=False):
    """The result structure for the run job request."""

    jobSummary: JobSummary


class StopJobRequest(ServiceRequest):
    """The request structure for the stop job request."""

    appId: AppId
    branchName: BranchName
    jobId: JobId


class StopJobResult(TypedDict, total=False):
    """The result structure for the stop job request."""

    jobSummary: JobSummary


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    """The request structure to tag a resource with a tag key and value."""

    resourceArn: ResourceArn
    tags: TagMap


class TagResourceResponse(TypedDict, total=False):
    """The response for the tag resource request."""


class UntagResourceRequest(ServiceRequest):
    """The request structure for the untag resource request."""

    resourceArn: ResourceArn
    tagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    """The response for the untag resource request."""


class UpdateAppRequest(ServiceRequest):
    """The request structure for the update app request."""

    appId: AppId
    name: Optional[Name]
    description: Optional[Description]
    platform: Optional[Platform]
    iamServiceRoleArn: Optional[ServiceRoleArn]
    environmentVariables: Optional[EnvironmentVariables]
    enableBranchAutoBuild: Optional[EnableAutoBuild]
    enableBranchAutoDeletion: Optional[EnableBranchAutoDeletion]
    enableBasicAuth: Optional[EnableBasicAuth]
    basicAuthCredentials: Optional[BasicAuthCredentials]
    customRules: Optional[CustomRules]
    buildSpec: Optional[BuildSpec]
    customHeaders: Optional[CustomHeaders]
    enableAutoBranchCreation: Optional[EnableAutoBranchCreation]
    autoBranchCreationPatterns: Optional[AutoBranchCreationPatterns]
    autoBranchCreationConfig: Optional[AutoBranchCreationConfig]
    repository: Optional[Repository]
    oauthToken: Optional[OauthToken]
    accessToken: Optional[AccessToken]


class UpdateAppResult(TypedDict, total=False):
    """The result structure for an Amplify app update request."""

    app: App


class UpdateBranchRequest(ServiceRequest):
    """The request structure for the update branch request."""

    appId: AppId
    branchName: BranchName
    description: Optional[Description]
    framework: Optional[Framework]
    stage: Optional[Stage]
    enableNotification: Optional[EnableNotification]
    enableAutoBuild: Optional[EnableAutoBuild]
    environmentVariables: Optional[EnvironmentVariables]
    basicAuthCredentials: Optional[BasicAuthCredentials]
    enableBasicAuth: Optional[EnableBasicAuth]
    enablePerformanceMode: Optional[EnablePerformanceMode]
    buildSpec: Optional[BuildSpec]
    ttl: Optional[TTL]
    displayName: Optional[DisplayName]
    enablePullRequestPreview: Optional[EnablePullRequestPreview]
    pullRequestEnvironmentName: Optional[PullRequestEnvironmentName]
    backendEnvironmentArn: Optional[BackendEnvironmentArn]


class UpdateBranchResult(TypedDict, total=False):
    """The result structure for the update branch request."""

    branch: Branch


class UpdateDomainAssociationRequest(ServiceRequest):
    """The request structure for the update domain association request."""

    appId: AppId
    domainName: DomainName
    enableAutoSubDomain: Optional[EnableAutoSubDomain]
    subDomainSettings: Optional[SubDomainSettings]
    autoSubDomainCreationPatterns: Optional[AutoSubDomainCreationPatterns]
    autoSubDomainIAMRole: Optional[AutoSubDomainIAMRole]


class UpdateDomainAssociationResult(TypedDict, total=False):
    """The result structure for the update domain association request."""

    domainAssociation: DomainAssociation


class UpdateWebhookRequest(ServiceRequest):
    """The request structure for the update webhook request."""

    webhookId: WebhookId
    branchName: Optional[BranchName]
    description: Optional[Description]


class UpdateWebhookResult(TypedDict, total=False):
    """The result structure for the update webhook request."""

    webhook: Webhook


class AmplifyApi:

    service = "amplify"
    version = "2017-07-25"

    @handler("CreateApp")
    def create_app(
        self,
        context: RequestContext,
        name: Name,
        description: Description = None,
        repository: Repository = None,
        platform: Platform = None,
        iam_service_role_arn: ServiceRoleArn = None,
        oauth_token: OauthToken = None,
        access_token: AccessToken = None,
        environment_variables: EnvironmentVariables = None,
        enable_branch_auto_build: EnableBranchAutoBuild = None,
        enable_branch_auto_deletion: EnableBranchAutoDeletion = None,
        enable_basic_auth: EnableBasicAuth = None,
        basic_auth_credentials: BasicAuthCredentials = None,
        custom_rules: CustomRules = None,
        tags: TagMap = None,
        build_spec: BuildSpec = None,
        custom_headers: CustomHeaders = None,
        enable_auto_branch_creation: EnableAutoBranchCreation = None,
        auto_branch_creation_patterns: AutoBranchCreationPatterns = None,
        auto_branch_creation_config: AutoBranchCreationConfig = None,
    ) -> CreateAppResult:
        """Creates a new Amplify app.

        :param name: The name for an Amplify app.
        :param description: The description for an Amplify app.
        :param repository: The repository for an Amplify app.
        :param platform: The platform or framework for an Amplify app.
        :param iam_service_role_arn: The AWS Identity and Access Management (IAM) service role for an Amplify
        app.
        :param oauth_token: The OAuth token for a third-party source control system for an Amplify
        app.
        :param access_token: The personal access token for a GitHub repository for an Amplify app.
        :param environment_variables: The environment variables map for an Amplify app.
        :param enable_branch_auto_build: Enables the auto building of branches for an Amplify app.
        :param enable_branch_auto_deletion: Automatically disconnects a branch in the Amplify Console when you
        delete a branch from your Git repository.
        :param enable_basic_auth: Enables basic authorization for an Amplify app.
        :param basic_auth_credentials: The credentials for basic authorization for an Amplify app.
        :param custom_rules: The custom rewrite and redirect rules for an Amplify app.
        :param tags: The tag for an Amplify app.
        :param build_spec: The build specification (build spec) for an Amplify app.
        :param custom_headers: The custom HTTP headers for an Amplify app.
        :param enable_auto_branch_creation: Enables automated branch creation for an Amplify app.
        :param auto_branch_creation_patterns: The automated branch creation glob patterns for an Amplify app.
        :param auto_branch_creation_config: The automated branch creation configuration for an Amplify app.
        :returns: CreateAppResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("CreateBackendEnvironment")
    def create_backend_environment(
        self,
        context: RequestContext,
        app_id: AppId,
        environment_name: EnvironmentName,
        stack_name: StackName = None,
        deployment_artifacts: DeploymentArtifacts = None,
    ) -> CreateBackendEnvironmentResult:
        """Creates a new backend environment for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param environment_name: The name for the backend environment.
        :param stack_name: The AWS CloudFormation stack name of a backend environment.
        :param deployment_artifacts: The name of deployment artifacts.
        :returns: CreateBackendEnvironmentResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateBranch")
    def create_branch(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        description: Description = None,
        stage: Stage = None,
        framework: Framework = None,
        enable_notification: EnableNotification = None,
        enable_auto_build: EnableAutoBuild = None,
        environment_variables: EnvironmentVariables = None,
        basic_auth_credentials: BasicAuthCredentials = None,
        enable_basic_auth: EnableBasicAuth = None,
        enable_performance_mode: EnablePerformanceMode = None,
        tags: TagMap = None,
        build_spec: BuildSpec = None,
        ttl: TTL = None,
        display_name: DisplayName = None,
        enable_pull_request_preview: EnablePullRequestPreview = None,
        pull_request_environment_name: PullRequestEnvironmentName = None,
        backend_environment_arn: BackendEnvironmentArn = None,
    ) -> CreateBranchResult:
        """Creates a new branch for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch.
        :param description: The description for the branch.
        :param stage: Describes the current stage for the branch.
        :param framework: The framework for the branch.
        :param enable_notification: Enables notifications for the branch.
        :param enable_auto_build: Enables auto building for the branch.
        :param environment_variables: The environment variables for the branch.
        :param basic_auth_credentials: The basic authorization credentials for the branch.
        :param enable_basic_auth: Enables basic authorization for the branch.
        :param enable_performance_mode: Enables performance mode for the branch.
        :param tags: The tag for the branch.
        :param build_spec: The build specification (build spec) for the branch.
        :param ttl: The content Time To Live (TTL) for the website in seconds.
        :param display_name: The display name for a branch.
        :param enable_pull_request_preview: Enables pull request previews for this branch.
        :param pull_request_environment_name: The Amplify environment name for the pull request.
        :param backend_environment_arn: The Amazon Resource Name (ARN) for a backend environment that is part of
        an Amplify app.
        :returns: CreateBranchResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("CreateDeployment")
    def create_deployment(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        file_map: FileMap = None,
    ) -> CreateDeploymentResult:
        """Creates a deployment for a manually deployed Amplify app. Manually
        deployed apps are not connected to a repository.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch, for the job.
        :param file_map: An optional file map that contains the file name as the key and the file
        content md5 hash as the value.
        :returns: CreateDeploymentResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateDomainAssociation")
    def create_domain_association(
        self,
        context: RequestContext,
        app_id: AppId,
        domain_name: DomainName,
        sub_domain_settings: SubDomainSettings,
        enable_auto_sub_domain: EnableAutoSubDomain = None,
        auto_sub_domain_creation_patterns: AutoSubDomainCreationPatterns = None,
        auto_sub_domain_iam_role: AutoSubDomainIAMRole = None,
    ) -> CreateDomainAssociationResult:
        """Creates a new domain association for an Amplify app. This action
        associates a custom domain with the Amplify app

        :param app_id: The unique ID for an Amplify app.
        :param domain_name: The domain name for the domain association.
        :param sub_domain_settings: The setting for the subdomain.
        :param enable_auto_sub_domain: Enables the automated creation of subdomains for branches.
        :param auto_sub_domain_creation_patterns: Sets the branch patterns for automatic subdomain creation.
        :param auto_sub_domain_iam_role: The required AWS Identity and Access Management (IAM) service role for
        the Amazon Resource Name (ARN) for automatically creating subdomains.
        :returns: CreateDomainAssociationResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("CreateWebhook")
    def create_webhook(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        description: Description = None,
    ) -> CreateWebhookResult:
        """Creates a new webhook on an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for a branch that is part of an Amplify app.
        :param description: The description for a webhook.
        :returns: CreateWebhookResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("DeleteApp")
    def delete_app(self, context: RequestContext, app_id: AppId) -> DeleteAppResult:
        """Deletes an existing Amplify app specified by an app ID.

        :param app_id: The unique ID for an Amplify app.
        :returns: DeleteAppResult
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("DeleteBackendEnvironment")
    def delete_backend_environment(
        self, context: RequestContext, app_id: AppId, environment_name: EnvironmentName
    ) -> DeleteBackendEnvironmentResult:
        """Deletes a backend environment for an Amplify app.

        :param app_id: The unique ID of an Amplify app.
        :param environment_name: The name of a backend environment of an Amplify app.
        :returns: DeleteBackendEnvironmentResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("DeleteBranch")
    def delete_branch(
        self, context: RequestContext, app_id: AppId, branch_name: BranchName
    ) -> DeleteBranchResult:
        """Deletes a branch for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch.
        :returns: DeleteBranchResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("DeleteDomainAssociation")
    def delete_domain_association(
        self, context: RequestContext, app_id: AppId, domain_name: DomainName
    ) -> DeleteDomainAssociationResult:
        """Deletes a domain association for an Amplify app.

        :param app_id: The unique id for an Amplify app.
        :param domain_name: The name of the domain.
        :returns: DeleteDomainAssociationResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("DeleteJob")
    def delete_job(
        self, context: RequestContext, app_id: AppId, branch_name: BranchName, job_id: JobId
    ) -> DeleteJobResult:
        """Deletes a job for a branch of an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch, for the job.
        :param job_id: The unique ID for the job.
        :returns: DeleteJobResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DeleteWebhook")
    def delete_webhook(self, context: RequestContext, webhook_id: WebhookId) -> DeleteWebhookResult:
        """Deletes a webhook.

        :param webhook_id: The unique ID for a webhook.
        :returns: DeleteWebhookResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("GenerateAccessLogs")
    def generate_access_logs(
        self,
        context: RequestContext,
        domain_name: DomainName,
        app_id: AppId,
        start_time: StartTime = None,
        end_time: EndTime = None,
    ) -> GenerateAccessLogsResult:
        """Returns the website access logs for a specific time range using a
        presigned URL.

        :param domain_name: The name of the domain.
        :param app_id: The unique ID for an Amplify app.
        :param start_time: The time at which the logs should start.
        :param end_time: The time at which the logs should end.
        :returns: GenerateAccessLogsResult
        :raises NotFoundException:
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetApp")
    def get_app(self, context: RequestContext, app_id: AppId) -> GetAppResult:
        """Returns an existing Amplify app by appID.

        :param app_id: The unique ID for an Amplify app.
        :returns: GetAppResult
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetArtifactUrl")
    def get_artifact_url(
        self, context: RequestContext, artifact_id: ArtifactId
    ) -> GetArtifactUrlResult:
        """Returns the artifact info that corresponds to an artifact id.

        :param artifact_id: The unique ID for an artifact.
        :returns: GetArtifactUrlResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("GetBackendEnvironment")
    def get_backend_environment(
        self, context: RequestContext, app_id: AppId, environment_name: EnvironmentName
    ) -> GetBackendEnvironmentResult:
        """Returns a backend environment for an Amplify app.

        :param app_id: The unique id for an Amplify app.
        :param environment_name: The name for the backend environment.
        :returns: GetBackendEnvironmentResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetBranch")
    def get_branch(
        self, context: RequestContext, app_id: AppId, branch_name: BranchName
    ) -> GetBranchResult:
        """Returns a branch for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch.
        :returns: GetBranchResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetDomainAssociation")
    def get_domain_association(
        self, context: RequestContext, app_id: AppId, domain_name: DomainName
    ) -> GetDomainAssociationResult:
        """Returns the domain information for an Amplify app.

        :param app_id: The unique id for an Amplify app.
        :param domain_name: The name of the domain.
        :returns: GetDomainAssociationResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetJob")
    def get_job(
        self, context: RequestContext, app_id: AppId, branch_name: BranchName, job_id: JobId
    ) -> GetJobResult:
        """Returns a job for a branch of an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The branch name for the job.
        :param job_id: The unique ID for the job.
        :returns: GetJobResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("GetWebhook")
    def get_webhook(self, context: RequestContext, webhook_id: WebhookId) -> GetWebhookResult:
        """Returns the webhook information that corresponds to a specified webhook
        ID.

        :param webhook_id: The unique ID for a webhook.
        :returns: GetWebhookResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ListApps")
    def list_apps(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListAppsResult:
        """Returns a list of the existing Amplify apps.

        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListAppsResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListArtifacts")
    def list_artifacts(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        job_id: JobId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListArtifactsResult:
        """Returns a list of artifacts for a specified app, branch, and job.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name of a branch that is part of an Amplify app.
        :param job_id: The unique ID for a job.
        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListArtifactsResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ListBackendEnvironments")
    def list_backend_environments(
        self,
        context: RequestContext,
        app_id: AppId,
        environment_name: EnvironmentName = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListBackendEnvironmentsResult:
        """Lists the backend environments for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param environment_name: The name of the backend environment.
        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListBackendEnvironmentsResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListBranches")
    def list_branches(
        self,
        context: RequestContext,
        app_id: AppId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListBranchesResult:
        """Lists the branches of an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListBranchesResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListDomainAssociations")
    def list_domain_associations(
        self,
        context: RequestContext,
        app_id: AppId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListDomainAssociationsResult:
        """Returns the domain associations for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListDomainAssociationsResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListJobs")
    def list_jobs(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListJobsResult:
        """Lists the jobs for a branch of an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for a branch.
        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListJobsResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ResourceArn
    ) -> ListTagsForResourceResponse:
        """Returns a list of tags for a specified Amazon Resource Name (ARN).

        :param resource_arn: The Amazon Resource Name (ARN) to use to list tags.
        :returns: ListTagsForResourceResponse
        :raises InternalFailureException:
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListWebhooks")
    def list_webhooks(
        self,
        context: RequestContext,
        app_id: AppId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListWebhooksResult:
        """Returns a list of webhooks for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param next_token: A pagination token.
        :param max_results: The maximum number of records to list in a single response.
        :returns: ListWebhooksResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("StartDeployment")
    def start_deployment(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        job_id: JobId = None,
        source_url: SourceUrl = None,
    ) -> StartDeploymentResult:
        """Starts a deployment for a manually deployed app. Manually deployed apps
        are not connected to a repository.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch, for the job.
        :param job_id: The job ID for this deployment, generated by the create deployment
        request.
        :param source_url: The source URL for this deployment, used when calling start deployment
        without create deployment.
        :returns: StartDeploymentResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("StartJob")
    def start_job(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        job_type: JobType,
        job_id: JobId = None,
        job_reason: JobReason = None,
        commit_id: CommitId = None,
        commit_message: CommitMessage = None,
        commit_time: CommitTime = None,
    ) -> StartJobResult:
        """Starts a new job for a branch of an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The branch name for the job.
        :param job_type: Describes the type for the job.
        :param job_id: The unique ID for an existing job.
        :param job_reason: A descriptive reason for starting this job.
        :param commit_id: The commit ID from a third-party repository provider for the job.
        :param commit_message: The commit message from a third-party repository provider for the job.
        :param commit_time: The commit date and time for the job.
        :returns: StartJobResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("StopJob")
    def stop_job(
        self, context: RequestContext, app_id: AppId, branch_name: BranchName, job_id: JobId
    ) -> StopJobResult:
        """Stops a job that is in progress for a branch of an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch, for the job.
        :param job_id: The unique id for the job.
        :returns: StopJobResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises NotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tags: TagMap
    ) -> TagResourceResponse:
        """Tags the resource with a tag key and value.

        :param resource_arn: The Amazon Resource Name (ARN) to use to tag a resource.
        :param tags: The tags used to tag the resource.
        :returns: TagResourceResponse
        :raises InternalFailureException:
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Untags a resource with a specified Amazon Resource Name (ARN).

        :param resource_arn: The Amazon Resource Name (ARN) to use to untag a resource.
        :param tag_keys: The tag keys to use to untag a resource.
        :returns: UntagResourceResponse
        :raises InternalFailureException:
        :raises BadRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateApp")
    def update_app(
        self,
        context: RequestContext,
        app_id: AppId,
        name: Name = None,
        description: Description = None,
        platform: Platform = None,
        iam_service_role_arn: ServiceRoleArn = None,
        environment_variables: EnvironmentVariables = None,
        enable_branch_auto_build: EnableAutoBuild = None,
        enable_branch_auto_deletion: EnableBranchAutoDeletion = None,
        enable_basic_auth: EnableBasicAuth = None,
        basic_auth_credentials: BasicAuthCredentials = None,
        custom_rules: CustomRules = None,
        build_spec: BuildSpec = None,
        custom_headers: CustomHeaders = None,
        enable_auto_branch_creation: EnableAutoBranchCreation = None,
        auto_branch_creation_patterns: AutoBranchCreationPatterns = None,
        auto_branch_creation_config: AutoBranchCreationConfig = None,
        repository: Repository = None,
        oauth_token: OauthToken = None,
        access_token: AccessToken = None,
    ) -> UpdateAppResult:
        """Updates an existing Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param name: The name for an Amplify app.
        :param description: The description for an Amplify app.
        :param platform: The platform for an Amplify app.
        :param iam_service_role_arn: The AWS Identity and Access Management (IAM) service role for an Amplify
        app.
        :param environment_variables: The environment variables for an Amplify app.
        :param enable_branch_auto_build: Enables branch auto-building for an Amplify app.
        :param enable_branch_auto_deletion: Automatically disconnects a branch in the Amplify Console when you
        delete a branch from your Git repository.
        :param enable_basic_auth: Enables basic authorization for an Amplify app.
        :param basic_auth_credentials: The basic authorization credentials for an Amplify app.
        :param custom_rules: The custom redirect and rewrite rules for an Amplify app.
        :param build_spec: The build specification (build spec) for an Amplify app.
        :param custom_headers: The custom HTTP headers for an Amplify app.
        :param enable_auto_branch_creation: Enables automated branch creation for an Amplify app.
        :param auto_branch_creation_patterns: Describes the automated branch creation glob patterns for an Amplify
        app.
        :param auto_branch_creation_config: The automated branch creation configuration for an Amplify app.
        :param repository: The name of the repository for an Amplify app.
        :param oauth_token: The OAuth token for a third-party source control system for an Amplify
        app.
        :param access_token: The personal access token for a GitHub repository for an Amplify app.
        :returns: UpdateAppResult
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateBranch")
    def update_branch(
        self,
        context: RequestContext,
        app_id: AppId,
        branch_name: BranchName,
        description: Description = None,
        framework: Framework = None,
        stage: Stage = None,
        enable_notification: EnableNotification = None,
        enable_auto_build: EnableAutoBuild = None,
        environment_variables: EnvironmentVariables = None,
        basic_auth_credentials: BasicAuthCredentials = None,
        enable_basic_auth: EnableBasicAuth = None,
        enable_performance_mode: EnablePerformanceMode = None,
        build_spec: BuildSpec = None,
        ttl: TTL = None,
        display_name: DisplayName = None,
        enable_pull_request_preview: EnablePullRequestPreview = None,
        pull_request_environment_name: PullRequestEnvironmentName = None,
        backend_environment_arn: BackendEnvironmentArn = None,
    ) -> UpdateBranchResult:
        """Updates a branch for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param branch_name: The name for the branch.
        :param description: The description for the branch.
        :param framework: The framework for the branch.
        :param stage: Describes the current stage for the branch.
        :param enable_notification: Enables notifications for the branch.
        :param enable_auto_build: Enables auto building for the branch.
        :param environment_variables: The environment variables for the branch.
        :param basic_auth_credentials: The basic authorization credentials for the branch.
        :param enable_basic_auth: Enables basic authorization for the branch.
        :param enable_performance_mode: Enables performance mode for the branch.
        :param build_spec: The build specification (build spec) for the branch.
        :param ttl: The content Time to Live (TTL) for the website in seconds.
        :param display_name: The display name for a branch.
        :param enable_pull_request_preview: Enables pull request previews for this branch.
        :param pull_request_environment_name: The Amplify environment name for the pull request.
        :param backend_environment_arn: The Amazon Resource Name (ARN) for a backend environment that is part of
        an Amplify app.
        :returns: UpdateBranchResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("UpdateDomainAssociation")
    def update_domain_association(
        self,
        context: RequestContext,
        app_id: AppId,
        domain_name: DomainName,
        enable_auto_sub_domain: EnableAutoSubDomain = None,
        sub_domain_settings: SubDomainSettings = None,
        auto_sub_domain_creation_patterns: AutoSubDomainCreationPatterns = None,
        auto_sub_domain_iam_role: AutoSubDomainIAMRole = None,
    ) -> UpdateDomainAssociationResult:
        """Creates a new domain association for an Amplify app.

        :param app_id: The unique ID for an Amplify app.
        :param domain_name: The name of the domain.
        :param enable_auto_sub_domain: Enables the automated creation of subdomains for branches.
        :param sub_domain_settings: Describes the settings for the subdomain.
        :param auto_sub_domain_creation_patterns: Sets the branch patterns for automatic subdomain creation.
        :param auto_sub_domain_iam_role: The required AWS Identity and Access Management (IAM) service role for
        the Amazon Resource Name (ARN) for automatically creating subdomains.
        :returns: UpdateDomainAssociationResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError

    @handler("UpdateWebhook")
    def update_webhook(
        self,
        context: RequestContext,
        webhook_id: WebhookId,
        branch_name: BranchName = None,
        description: Description = None,
    ) -> UpdateWebhookResult:
        """Updates a webhook.

        :param webhook_id: The unique ID for a webhook.
        :param branch_name: The name for a branch that is part of an Amplify app.
        :param description: The description for a webhook.
        :returns: UpdateWebhookResult
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises NotFoundException:
        :raises InternalFailureException:
        :raises DependentServiceFailureException:
        """
        raise NotImplementedError
