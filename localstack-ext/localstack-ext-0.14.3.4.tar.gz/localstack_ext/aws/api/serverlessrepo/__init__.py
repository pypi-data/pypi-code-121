import sys
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

MaxItems = int
_boolean = bool
_double = float
_integer = int
_string = str


class Capability(str):
    CAPABILITY_IAM = "CAPABILITY_IAM"
    CAPABILITY_NAMED_IAM = "CAPABILITY_NAMED_IAM"
    CAPABILITY_AUTO_EXPAND = "CAPABILITY_AUTO_EXPAND"
    CAPABILITY_RESOURCE_POLICY = "CAPABILITY_RESOURCE_POLICY"


class Status(str):
    PREPARING = "PREPARING"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class BadRequestException(ServiceException):
    """One of the parameters in the request is invalid."""

    ErrorCode: Optional[_string]
    Message: Optional[_string]


class ConflictException(ServiceException):
    """The resource already exists."""

    ErrorCode: Optional[_string]
    Message: Optional[_string]


class ForbiddenException(ServiceException):
    """The client is not authenticated."""

    ErrorCode: Optional[_string]
    Message: Optional[_string]


class InternalServerErrorException(ServiceException):
    """The AWS Serverless Application Repository service encountered an
    internal error.
    """

    ErrorCode: Optional[_string]
    Message: Optional[_string]


class NotFoundException(ServiceException):
    """The resource (for example, an access policy statement) specified in the
    request doesn't exist.
    """

    ErrorCode: Optional[_string]
    Message: Optional[_string]


class TooManyRequestsException(ServiceException):
    """The client is sending more than the allowed number of requests per unit
    of time.
    """

    ErrorCode: Optional[_string]
    Message: Optional[_string]


_listOfCapability = List[Capability]
_listOf__string = List[_string]


class ParameterDefinition(TypedDict, total=False):
    """Parameters supported by the application."""

    AllowedPattern: Optional[_string]
    AllowedValues: Optional[_listOf__string]
    ConstraintDescription: Optional[_string]
    DefaultValue: Optional[_string]
    Description: Optional[_string]
    MaxLength: Optional[_integer]
    MaxValue: Optional[_integer]
    MinLength: Optional[_integer]
    MinValue: Optional[_integer]
    Name: _string
    NoEcho: Optional[_boolean]
    ReferencedByResources: _listOf__string
    Type: Optional[_string]


_listOfParameterDefinition = List[ParameterDefinition]


class Version(TypedDict, total=False):
    """Application version details."""

    ApplicationId: _string
    CreationTime: _string
    ParameterDefinitions: _listOfParameterDefinition
    RequiredCapabilities: _listOfCapability
    ResourcesSupported: _boolean
    SemanticVersion: _string
    SourceCodeArchiveUrl: Optional[_string]
    SourceCodeUrl: Optional[_string]
    TemplateUrl: _string


class Application(TypedDict, total=False):
    """Details about the application."""

    ApplicationId: _string
    Author: _string
    CreationTime: Optional[_string]
    Description: _string
    HomePageUrl: Optional[_string]
    IsVerifiedAuthor: Optional[_boolean]
    Labels: Optional[_listOf__string]
    LicenseUrl: Optional[_string]
    Name: _string
    ReadmeUrl: Optional[_string]
    SpdxLicenseId: Optional[_string]
    VerifiedAuthorUrl: Optional[_string]
    Version: Optional[Version]


class ApplicationDependencySummary(TypedDict, total=False):
    """A nested application summary."""

    ApplicationId: _string
    SemanticVersion: _string


_listOfApplicationDependencySummary = List[ApplicationDependencySummary]


class ApplicationDependencyPage(TypedDict, total=False):
    """A list of application summaries nested in the application."""

    Dependencies: _listOfApplicationDependencySummary
    NextToken: Optional[_string]


class ApplicationSummary(TypedDict, total=False):
    """Summary of details about the application."""

    ApplicationId: _string
    Author: _string
    CreationTime: Optional[_string]
    Description: _string
    HomePageUrl: Optional[_string]
    Labels: Optional[_listOf__string]
    Name: _string
    SpdxLicenseId: Optional[_string]


_listOfApplicationSummary = List[ApplicationSummary]


class ApplicationPage(TypedDict, total=False):
    """A list of application details."""

    Applications: _listOfApplicationSummary
    NextToken: Optional[_string]


class ApplicationPolicyStatement(TypedDict, total=False):
    """Policy statement applied to the application."""

    Actions: _listOf__string
    PrincipalOrgIDs: Optional[_listOf__string]
    Principals: _listOf__string
    StatementId: Optional[_string]


_listOfApplicationPolicyStatement = List[ApplicationPolicyStatement]


class ApplicationPolicy(TypedDict, total=False):
    """Policy statements applied to the application."""

    Statements: _listOfApplicationPolicyStatement


class VersionSummary(TypedDict, total=False):
    """An application version summary."""

    ApplicationId: _string
    CreationTime: _string
    SemanticVersion: _string
    SourceCodeUrl: Optional[_string]


_listOfVersionSummary = List[VersionSummary]


class ApplicationVersionPage(TypedDict, total=False):
    """A list of version summaries for the application."""

    NextToken: Optional[_string]
    Versions: _listOfVersionSummary


class ChangeSetDetails(TypedDict, total=False):
    """Details of the change set."""

    ApplicationId: _string
    ChangeSetId: _string
    SemanticVersion: _string
    StackId: _string


class CreateApplicationInput(TypedDict, total=False):
    """Create an application request."""

    Author: _string
    Description: _string
    HomePageUrl: Optional[_string]
    Labels: Optional[_listOf__string]
    LicenseBody: Optional[_string]
    LicenseUrl: Optional[_string]
    Name: _string
    ReadmeBody: Optional[_string]
    ReadmeUrl: Optional[_string]
    SemanticVersion: Optional[_string]
    SourceCodeArchiveUrl: Optional[_string]
    SourceCodeUrl: Optional[_string]
    SpdxLicenseId: Optional[_string]
    TemplateBody: Optional[_string]
    TemplateUrl: Optional[_string]


class CreateApplicationRequest(ServiceRequest):
    Author: _string
    Description: _string
    HomePageUrl: Optional[_string]
    Labels: Optional[_listOf__string]
    LicenseBody: Optional[_string]
    LicenseUrl: Optional[_string]
    Name: _string
    ReadmeBody: Optional[_string]
    ReadmeUrl: Optional[_string]
    SemanticVersion: Optional[_string]
    SourceCodeArchiveUrl: Optional[_string]
    SourceCodeUrl: Optional[_string]
    SpdxLicenseId: Optional[_string]
    TemplateBody: Optional[_string]
    TemplateUrl: Optional[_string]


class CreateApplicationResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    Author: Optional[_string]
    CreationTime: Optional[_string]
    Description: Optional[_string]
    HomePageUrl: Optional[_string]
    IsVerifiedAuthor: Optional[_boolean]
    Labels: Optional[_listOf__string]
    LicenseUrl: Optional[_string]
    Name: Optional[_string]
    ReadmeUrl: Optional[_string]
    SpdxLicenseId: Optional[_string]
    VerifiedAuthorUrl: Optional[_string]
    Version: Optional[Version]


class CreateApplicationVersionInput(TypedDict, total=False):
    """Create a version request."""

    SourceCodeArchiveUrl: Optional[_string]
    SourceCodeUrl: Optional[_string]
    TemplateBody: Optional[_string]
    TemplateUrl: Optional[_string]


class CreateApplicationVersionRequest(ServiceRequest):
    ApplicationId: _string
    SemanticVersion: _string
    SourceCodeArchiveUrl: Optional[_string]
    SourceCodeUrl: Optional[_string]
    TemplateBody: Optional[_string]
    TemplateUrl: Optional[_string]


class CreateApplicationVersionResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    CreationTime: Optional[_string]
    ParameterDefinitions: Optional[_listOfParameterDefinition]
    RequiredCapabilities: Optional[_listOfCapability]
    ResourcesSupported: Optional[_boolean]
    SemanticVersion: Optional[_string]
    SourceCodeArchiveUrl: Optional[_string]
    SourceCodeUrl: Optional[_string]
    TemplateUrl: Optional[_string]


class Tag(TypedDict, total=False):
    """This property corresponds to the *AWS
    CloudFormation* `Tag <https://docs.aws.amazon.com/goto/WebAPI/cloudformation-2010-05-15/Tag>`__
    Data Type.
    """

    Key: _string
    Value: _string


_listOfTag = List[Tag]


class RollbackTrigger(TypedDict, total=False):
    """This property corresponds to the *AWS
    CloudFormation* `RollbackTrigger <https://docs.aws.amazon.com/goto/WebAPI/cloudformation-2010-05-15/RollbackTrigger>`__
    Data Type.
    """

    Arn: _string
    Type: _string


_listOfRollbackTrigger = List[RollbackTrigger]


class RollbackConfiguration(TypedDict, total=False):
    """This property corresponds to the *AWS
    CloudFormation* `RollbackConfiguration <https://docs.aws.amazon.com/goto/WebAPI/cloudformation-2010-05-15/RollbackConfiguration>`__
    Data Type.
    """

    MonitoringTimeInMinutes: Optional[_integer]
    RollbackTriggers: Optional[_listOfRollbackTrigger]


class ParameterValue(TypedDict, total=False):
    """Parameter value of the application."""

    Name: _string
    Value: _string


_listOfParameterValue = List[ParameterValue]


class CreateCloudFormationChangeSetInput(TypedDict, total=False):
    """Create an application change set request."""

    Capabilities: Optional[_listOf__string]
    ChangeSetName: Optional[_string]
    ClientToken: Optional[_string]
    Description: Optional[_string]
    NotificationArns: Optional[_listOf__string]
    ParameterOverrides: Optional[_listOfParameterValue]
    ResourceTypes: Optional[_listOf__string]
    RollbackConfiguration: Optional[RollbackConfiguration]
    SemanticVersion: Optional[_string]
    StackName: _string
    Tags: Optional[_listOfTag]
    TemplateId: Optional[_string]


class CreateCloudFormationChangeSetRequest(ServiceRequest):
    ApplicationId: _string
    Capabilities: Optional[_listOf__string]
    ChangeSetName: Optional[_string]
    ClientToken: Optional[_string]
    Description: Optional[_string]
    NotificationArns: Optional[_listOf__string]
    ParameterOverrides: Optional[_listOfParameterValue]
    ResourceTypes: Optional[_listOf__string]
    RollbackConfiguration: Optional[RollbackConfiguration]
    SemanticVersion: Optional[_string]
    StackName: _string
    Tags: Optional[_listOfTag]
    TemplateId: Optional[_string]


class CreateCloudFormationChangeSetResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    ChangeSetId: Optional[_string]
    SemanticVersion: Optional[_string]
    StackId: Optional[_string]


class CreateCloudFormationTemplateRequest(ServiceRequest):
    ApplicationId: _string
    SemanticVersion: Optional[_string]


class CreateCloudFormationTemplateResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    CreationTime: Optional[_string]
    ExpirationTime: Optional[_string]
    SemanticVersion: Optional[_string]
    Status: Optional[Status]
    TemplateId: Optional[_string]
    TemplateUrl: Optional[_string]


class DeleteApplicationRequest(ServiceRequest):
    ApplicationId: _string


class GetApplicationPolicyRequest(ServiceRequest):
    ApplicationId: _string


class GetApplicationPolicyResponse(TypedDict, total=False):
    Statements: Optional[_listOfApplicationPolicyStatement]


class GetApplicationRequest(ServiceRequest):
    ApplicationId: _string
    SemanticVersion: Optional[_string]


class GetApplicationResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    Author: Optional[_string]
    CreationTime: Optional[_string]
    Description: Optional[_string]
    HomePageUrl: Optional[_string]
    IsVerifiedAuthor: Optional[_boolean]
    Labels: Optional[_listOf__string]
    LicenseUrl: Optional[_string]
    Name: Optional[_string]
    ReadmeUrl: Optional[_string]
    SpdxLicenseId: Optional[_string]
    VerifiedAuthorUrl: Optional[_string]
    Version: Optional[Version]


class GetCloudFormationTemplateRequest(ServiceRequest):
    ApplicationId: _string
    TemplateId: _string


class GetCloudFormationTemplateResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    CreationTime: Optional[_string]
    ExpirationTime: Optional[_string]
    SemanticVersion: Optional[_string]
    Status: Optional[Status]
    TemplateId: Optional[_string]
    TemplateUrl: Optional[_string]


class ListApplicationDependenciesRequest(ServiceRequest):
    ApplicationId: _string
    MaxItems: Optional[MaxItems]
    NextToken: Optional[_string]
    SemanticVersion: Optional[_string]


class ListApplicationDependenciesResponse(TypedDict, total=False):
    Dependencies: Optional[_listOfApplicationDependencySummary]
    NextToken: Optional[_string]


class ListApplicationVersionsRequest(ServiceRequest):
    ApplicationId: _string
    MaxItems: Optional[MaxItems]
    NextToken: Optional[_string]


class ListApplicationVersionsResponse(TypedDict, total=False):
    NextToken: Optional[_string]
    Versions: Optional[_listOfVersionSummary]


class ListApplicationsRequest(ServiceRequest):
    MaxItems: Optional[MaxItems]
    NextToken: Optional[_string]


class ListApplicationsResponse(TypedDict, total=False):
    Applications: Optional[_listOfApplicationSummary]
    NextToken: Optional[_string]


class PutApplicationPolicyRequest(ServiceRequest):
    ApplicationId: _string
    Statements: _listOfApplicationPolicyStatement


class PutApplicationPolicyResponse(TypedDict, total=False):
    Statements: Optional[_listOfApplicationPolicyStatement]


class TemplateDetails(TypedDict, total=False):
    """Details of the template."""

    ApplicationId: _string
    CreationTime: _string
    ExpirationTime: _string
    SemanticVersion: _string
    Status: Status
    TemplateId: _string
    TemplateUrl: _string


class UnshareApplicationInput(TypedDict, total=False):
    """Unshare application request."""

    OrganizationId: _string


class UnshareApplicationRequest(ServiceRequest):
    ApplicationId: _string
    OrganizationId: _string


class UpdateApplicationInput(TypedDict, total=False):
    """Update the application request."""

    Author: Optional[_string]
    Description: Optional[_string]
    HomePageUrl: Optional[_string]
    Labels: Optional[_listOf__string]
    ReadmeBody: Optional[_string]
    ReadmeUrl: Optional[_string]


class UpdateApplicationRequest(ServiceRequest):
    ApplicationId: _string
    Author: Optional[_string]
    Description: Optional[_string]
    HomePageUrl: Optional[_string]
    Labels: Optional[_listOf__string]
    ReadmeBody: Optional[_string]
    ReadmeUrl: Optional[_string]


class UpdateApplicationResponse(TypedDict, total=False):
    ApplicationId: Optional[_string]
    Author: Optional[_string]
    CreationTime: Optional[_string]
    Description: Optional[_string]
    HomePageUrl: Optional[_string]
    IsVerifiedAuthor: Optional[_boolean]
    Labels: Optional[_listOf__string]
    LicenseUrl: Optional[_string]
    Name: Optional[_string]
    ReadmeUrl: Optional[_string]
    SpdxLicenseId: Optional[_string]
    VerifiedAuthorUrl: Optional[_string]
    Version: Optional[Version]


_long = int


class ServerlessrepoApi:

    service = "serverlessrepo"
    version = "2017-09-08"

    @handler("CreateApplication")
    def create_application(
        self,
        context: RequestContext,
        description: _string,
        name: _string,
        author: _string,
        home_page_url: _string = None,
        labels: _listOf__string = None,
        license_body: _string = None,
        license_url: _string = None,
        readme_body: _string = None,
        readme_url: _string = None,
        semantic_version: _string = None,
        source_code_archive_url: _string = None,
        source_code_url: _string = None,
        spdx_license_id: _string = None,
        template_body: _string = None,
        template_url: _string = None,
    ) -> CreateApplicationResponse:
        """Creates an application, optionally including an AWS SAM file to create
        the first application version in the same call.

        :param description: The description of the application.
        :param name: The name of the application that you want to publish.
        :param author: The name of the author publishing the app.
        :param home_page_url: A URL with more information about the application, for example the
        location of your GitHub repository for the application.
        :param labels: Labels to improve discovery of apps in search results.
        :param license_body: A local text file that contains the license of the app that matches the
        spdxLicenseID value of your application.
        :param license_url: A link to the S3 object that contains the license of the app that
        matches the spdxLicenseID value of your application.
        :param readme_body: A local text readme file in Markdown language that contains a more
        detailed description of the application and how it works.
        :param readme_url: A link to the S3 object in Markdown language that contains a more
        detailed description of the application and how it works.
        :param semantic_version: The semantic version of the application:

        https://semver.
        :param source_code_archive_url: A link to the S3 object that contains the ZIP archive of the source code
        for this version of your application.
        :param source_code_url: A link to a public repository for the source code of your application,
        for example the URL of a specific GitHub commit.
        :param spdx_license_id: A valid identifier from https://spdx.
        :param template_body: The local raw packaged AWS SAM template file of your application.
        :param template_url: A link to the S3 object containing the packaged AWS SAM template of your
        application.
        :returns: CreateApplicationResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ConflictException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("CreateApplicationVersion")
    def create_application_version(
        self,
        context: RequestContext,
        application_id: _string,
        semantic_version: _string,
        source_code_archive_url: _string = None,
        source_code_url: _string = None,
        template_body: _string = None,
        template_url: _string = None,
    ) -> CreateApplicationVersionResponse:
        """Creates an application version.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param semantic_version: The semantic version of the new version.
        :param source_code_archive_url: A link to the S3 object that contains the ZIP archive of the source code
        for this version of your application.
        :param source_code_url: A link to a public repository for the source code of your application,
        for example the URL of a specific GitHub commit.
        :param template_body: The raw packaged AWS SAM template of your application.
        :param template_url: A link to the packaged AWS SAM template of your application.
        :returns: CreateApplicationVersionResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ConflictException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("CreateCloudFormationChangeSet")
    def create_cloud_formation_change_set(
        self,
        context: RequestContext,
        application_id: _string,
        stack_name: _string,
        capabilities: _listOf__string = None,
        change_set_name: _string = None,
        client_token: _string = None,
        description: _string = None,
        notification_arns: _listOf__string = None,
        parameter_overrides: _listOfParameterValue = None,
        resource_types: _listOf__string = None,
        rollback_configuration: RollbackConfiguration = None,
        semantic_version: _string = None,
        tags: _listOfTag = None,
        template_id: _string = None,
    ) -> CreateCloudFormationChangeSetResponse:
        """Creates an AWS CloudFormation change set for the given application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param stack_name: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param capabilities: A list of values that you must specify before you can deploy certain
        applications.
        :param change_set_name: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param client_token: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param description: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param notification_arns: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param parameter_overrides: A list of parameter values for the parameters of the application.
        :param resource_types: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param rollback_configuration: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param semantic_version: The semantic version of the application:

        https://semver.
        :param tags: This property corresponds to the parameter of the same name for the *AWS
        CloudFormation* `CreateChangeSet <https://docs.
        :param template_id: The UUID returned by CreateCloudFormationTemplate.
        :returns: CreateCloudFormationChangeSetResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("CreateCloudFormationTemplate")
    def create_cloud_formation_template(
        self, context: RequestContext, application_id: _string, semantic_version: _string = None
    ) -> CreateCloudFormationTemplateResponse:
        """Creates an AWS CloudFormation template.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param semantic_version: The semantic version of the application:

        https://semver.
        :returns: CreateCloudFormationTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("DeleteApplication")
    def delete_application(self, context: RequestContext, application_id: _string) -> None:
        """Deletes the specified application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("GetApplication")
    def get_application(
        self, context: RequestContext, application_id: _string, semantic_version: _string = None
    ) -> GetApplicationResponse:
        """Gets the specified application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param semantic_version: The semantic version of the application to get.
        :returns: GetApplicationResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("GetApplicationPolicy")
    def get_application_policy(
        self, context: RequestContext, application_id: _string
    ) -> GetApplicationPolicyResponse:
        """Retrieves the policy for the application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :returns: GetApplicationPolicyResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("GetCloudFormationTemplate")
    def get_cloud_formation_template(
        self, context: RequestContext, application_id: _string, template_id: _string
    ) -> GetCloudFormationTemplateResponse:
        """Gets the specified AWS CloudFormation template.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param template_id: The UUID returned by CreateCloudFormationTemplate.
        :returns: GetCloudFormationTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("ListApplicationDependencies")
    def list_application_dependencies(
        self,
        context: RequestContext,
        application_id: _string,
        max_items: MaxItems = None,
        next_token: _string = None,
        semantic_version: _string = None,
    ) -> ListApplicationDependenciesResponse:
        """Retrieves the list of applications nested in the containing application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param max_items: The total number of items to return.
        :param next_token: A token to specify where to start paginating.
        :param semantic_version: The semantic version of the application to get.
        :returns: ListApplicationDependenciesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("ListApplicationVersions")
    def list_application_versions(
        self,
        context: RequestContext,
        application_id: _string,
        max_items: MaxItems = None,
        next_token: _string = None,
    ) -> ListApplicationVersionsResponse:
        """Lists versions for the specified application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param max_items: The total number of items to return.
        :param next_token: A token to specify where to start paginating.
        :returns: ListApplicationVersionsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("ListApplications")
    def list_applications(
        self, context: RequestContext, max_items: MaxItems = None, next_token: _string = None
    ) -> ListApplicationsResponse:
        """Lists applications owned by the requester.

        :param max_items: The total number of items to return.
        :param next_token: A token to specify where to start paginating.
        :returns: ListApplicationsResponse
        :raises NotFoundException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("PutApplicationPolicy")
    def put_application_policy(
        self,
        context: RequestContext,
        application_id: _string,
        statements: _listOfApplicationPolicyStatement,
    ) -> PutApplicationPolicyResponse:
        """Sets the permission policy for an application. For the list of actions
        supported for this operation, see `Application
        Permissions <https://docs.aws.amazon.com/serverlessrepo/latest/devguide/access-control-resource-based.html#application-permissions>`__
        .

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param statements: An array of policy statements applied to the application.
        :returns: PutApplicationPolicyResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("UnshareApplication")
    def unshare_application(
        self, context: RequestContext, application_id: _string, organization_id: _string
    ) -> None:
        """Unshares an application from an AWS Organization.

        This operation can be called only from the organization's master
        account.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param organization_id: The AWS Organization ID to unshare the application from.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("UpdateApplication")
    def update_application(
        self,
        context: RequestContext,
        application_id: _string,
        author: _string = None,
        description: _string = None,
        home_page_url: _string = None,
        labels: _listOf__string = None,
        readme_body: _string = None,
        readme_url: _string = None,
    ) -> UpdateApplicationResponse:
        """Updates the specified application.

        :param application_id: The Amazon Resource Name (ARN) of the application.
        :param author: The name of the author publishing the app.
        :param description: The description of the application.
        :param home_page_url: A URL with more information about the application, for example the
        location of your GitHub repository for the application.
        :param labels: Labels to improve discovery of apps in search results.
        :param readme_body: A text readme file in Markdown language that contains a more detailed
        description of the application and how it works.
        :param readme_url: A link to the readme file in Markdown language that contains a more
        detailed description of the application and how it works.
        :returns: UpdateApplicationResponse
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises ConflictException:
        """
        raise NotImplementedError
