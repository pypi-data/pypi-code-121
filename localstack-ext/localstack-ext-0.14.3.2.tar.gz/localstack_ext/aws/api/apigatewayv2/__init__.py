import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Arn = str
Id = str
IntegerWithLengthBetween0And3600 = int
IntegerWithLengthBetween50And30000 = int
IntegerWithLengthBetweenMinus1And86400 = int
NextToken = str
SelectionExpression = str
SelectionKey = str
StringWithLengthBetween0And1024 = str
StringWithLengthBetween0And2048 = str
StringWithLengthBetween0And32K = str
StringWithLengthBetween1And1024 = str
StringWithLengthBetween1And128 = str
StringWithLengthBetween1And1600 = str
StringWithLengthBetween1And256 = str
StringWithLengthBetween1And512 = str
StringWithLengthBetween1And64 = str
UriWithLengthBetween1And2048 = str
_boolean = bool
_double = float
_integer = int
_string = str


class AuthorizationType(str):
    NONE = "NONE"
    AWS_IAM = "AWS_IAM"
    CUSTOM = "CUSTOM"
    JWT = "JWT"


class AuthorizerType(str):
    REQUEST = "REQUEST"
    JWT = "JWT"


class ConnectionType(str):
    INTERNET = "INTERNET"
    VPC_LINK = "VPC_LINK"


class ContentHandlingStrategy(str):
    CONVERT_TO_BINARY = "CONVERT_TO_BINARY"
    CONVERT_TO_TEXT = "CONVERT_TO_TEXT"


class DeploymentStatus(str):
    PENDING = "PENDING"
    FAILED = "FAILED"
    DEPLOYED = "DEPLOYED"


class DomainNameStatus(str):
    AVAILABLE = "AVAILABLE"
    UPDATING = "UPDATING"
    PENDING_CERTIFICATE_REIMPORT = "PENDING_CERTIFICATE_REIMPORT"
    PENDING_OWNERSHIP_VERIFICATION = "PENDING_OWNERSHIP_VERIFICATION"


class EndpointType(str):
    REGIONAL = "REGIONAL"
    EDGE = "EDGE"


class IntegrationType(str):
    AWS = "AWS"
    HTTP = "HTTP"
    MOCK = "MOCK"
    HTTP_PROXY = "HTTP_PROXY"
    AWS_PROXY = "AWS_PROXY"


class LoggingLevel(str):
    ERROR = "ERROR"
    INFO = "INFO"
    OFF = "OFF"


class PassthroughBehavior(str):
    WHEN_NO_MATCH = "WHEN_NO_MATCH"
    NEVER = "NEVER"
    WHEN_NO_TEMPLATES = "WHEN_NO_TEMPLATES"


class ProtocolType(str):
    WEBSOCKET = "WEBSOCKET"
    HTTP = "HTTP"


class SecurityPolicy(str):
    TLS_1_0 = "TLS_1_0"
    TLS_1_2 = "TLS_1_2"


class VpcLinkStatus(str):
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"
    DELETING = "DELETING"
    FAILED = "FAILED"
    INACTIVE = "INACTIVE"


class VpcLinkVersion(str):
    V2 = "V2"


class AccessDeniedException(ServiceException):
    Message: Optional[_string]


class BadRequestException(ServiceException):
    """The request is not valid, for example, the input is incomplete or
    incorrect. See the accompanying error message for details.
    """

    Message: Optional[_string]


class ConflictException(ServiceException):
    """The requested operation would cause a conflict with the current state of
    a service resource associated with the request. Resolve the conflict
    before retrying this request. See the accompanying error message for
    details.
    """

    Message: Optional[_string]


class NotFoundException(ServiceException):
    """The resource specified in the request was not found. See the message
    field for more information.
    """

    Message: Optional[_string]
    ResourceType: Optional[_string]


class TooManyRequestsException(ServiceException):
    """A limit has been exceeded. See the accompanying error message for
    details.
    """

    LimitType: Optional[_string]
    Message: Optional[_string]


class AccessLogSettings(TypedDict, total=False):
    """Settings for logging access in a stage."""

    DestinationArn: Optional[Arn]
    Format: Optional[StringWithLengthBetween1And1024]


_listOf__string = List[_string]
Tags = Dict[_string, StringWithLengthBetween1And1600]
_timestampIso8601 = datetime
CorsHeaderList = List[_string]
CorsOriginList = List[_string]
CorsMethodList = List[StringWithLengthBetween1And64]


class Cors(TypedDict, total=False):
    """Represents a CORS configuration. Supported only for HTTP APIs. See
    `Configuring
    CORS <https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html>`__
    for more information.
    """

    AllowCredentials: Optional[_boolean]
    AllowHeaders: Optional[CorsHeaderList]
    AllowMethods: Optional[CorsMethodList]
    AllowOrigins: Optional[CorsOriginList]
    ExposeHeaders: Optional[CorsHeaderList]
    MaxAge: Optional[IntegerWithLengthBetweenMinus1And86400]


class Api(TypedDict, total=False):
    """Represents an API."""

    ApiEndpoint: Optional[_string]
    ApiGatewayManaged: Optional[_boolean]
    ApiId: Optional[Id]
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CreatedDate: Optional[_timestampIso8601]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    ImportInfo: Optional[_listOf__string]
    Name: StringWithLengthBetween1And128
    ProtocolType: ProtocolType
    RouteSelectionExpression: SelectionExpression
    Tags: Optional[Tags]
    Version: Optional[StringWithLengthBetween1And64]
    Warnings: Optional[_listOf__string]


class ApiMapping(TypedDict, total=False):
    """Represents an API mapping."""

    ApiId: Id
    ApiMappingId: Optional[Id]
    ApiMappingKey: Optional[SelectionKey]
    Stage: StringWithLengthBetween1And128


_listOfApiMapping = List[ApiMapping]


class ApiMappings(TypedDict, total=False):
    """Represents a collection of ApiMappings resources."""

    Items: Optional[_listOfApiMapping]
    NextToken: Optional[NextToken]


_listOfApi = List[Api]


class Apis(TypedDict, total=False):
    """Represents a collection of APIs."""

    Items: Optional[_listOfApi]
    NextToken: Optional[NextToken]


AuthorizationScopes = List[StringWithLengthBetween1And64]


class JWTConfiguration(TypedDict, total=False):
    """Represents the configuration of a JWT authorizer. Required for the JWT
    authorizer type. Supported only for HTTP APIs.
    """

    Audience: Optional[_listOf__string]
    Issuer: Optional[UriWithLengthBetween1And2048]


IdentitySourceList = List[_string]


class Authorizer(TypedDict, total=False):
    """Represents an authorizer."""

    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerId: Optional[Id]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: Optional[AuthorizerType]
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: Optional[IdentitySourceList]
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: StringWithLengthBetween1And128


_listOfAuthorizer = List[Authorizer]


class Authorizers(TypedDict, total=False):
    """Represents a collection of authorizers."""

    Items: Optional[_listOfAuthorizer]
    NextToken: Optional[NextToken]


class CreateApiInput(TypedDict, total=False):
    """Represents the input parameters for a CreateApi request."""

    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    Name: StringWithLengthBetween1And128
    ProtocolType: ProtocolType
    RouteKey: Optional[SelectionKey]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Target: Optional[UriWithLengthBetween1And2048]
    Version: Optional[StringWithLengthBetween1And64]


class CreateApiMappingInput(TypedDict, total=False):
    """Represents the input parameters for a CreateApiMapping request."""

    ApiId: Id
    ApiMappingKey: Optional[SelectionKey]
    Stage: StringWithLengthBetween1And128


class CreateApiMappingRequest(ServiceRequest):
    """Creates a new ApiMapping resource to represent an API mapping."""

    ApiId: Id
    ApiMappingKey: Optional[SelectionKey]
    DomainName: _string
    Stage: StringWithLengthBetween1And128


class CreateApiMappingResponse(TypedDict, total=False):
    ApiId: Optional[Id]
    ApiMappingId: Optional[Id]
    ApiMappingKey: Optional[SelectionKey]
    Stage: Optional[StringWithLengthBetween1And128]


class CreateApiRequest(ServiceRequest):
    """Creates a new Api resource to represent an API."""

    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    Name: StringWithLengthBetween1And128
    ProtocolType: ProtocolType
    RouteKey: Optional[SelectionKey]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Target: Optional[UriWithLengthBetween1And2048]
    Version: Optional[StringWithLengthBetween1And64]


class CreateApiResponse(TypedDict, total=False):
    ApiEndpoint: Optional[_string]
    ApiGatewayManaged: Optional[_boolean]
    ApiId: Optional[Id]
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CreatedDate: Optional[_timestampIso8601]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    ImportInfo: Optional[_listOf__string]
    Name: Optional[StringWithLengthBetween1And128]
    ProtocolType: Optional[ProtocolType]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Version: Optional[StringWithLengthBetween1And64]
    Warnings: Optional[_listOf__string]


class CreateAuthorizerInput(TypedDict, total=False):
    """Represents the input parameters for a CreateAuthorizer request."""

    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: AuthorizerType
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: IdentitySourceList
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: StringWithLengthBetween1And128


class CreateAuthorizerRequest(ServiceRequest):
    """Creates a new Authorizer resource to represent an authorizer."""

    ApiId: _string
    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: AuthorizerType
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: IdentitySourceList
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: StringWithLengthBetween1And128


class CreateAuthorizerResponse(TypedDict, total=False):
    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerId: Optional[Id]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: Optional[AuthorizerType]
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: Optional[IdentitySourceList]
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: Optional[StringWithLengthBetween1And128]


class CreateDeploymentInput(TypedDict, total=False):
    """Represents the input parameters for a CreateDeployment request."""

    Description: Optional[StringWithLengthBetween0And1024]
    StageName: Optional[StringWithLengthBetween1And128]


class CreateDeploymentRequest(ServiceRequest):
    """Creates a new Deployment resource to represent a deployment."""

    ApiId: _string
    Description: Optional[StringWithLengthBetween0And1024]
    StageName: Optional[StringWithLengthBetween1And128]


class CreateDeploymentResponse(TypedDict, total=False):
    AutoDeployed: Optional[_boolean]
    CreatedDate: Optional[_timestampIso8601]
    DeploymentId: Optional[Id]
    DeploymentStatus: Optional[DeploymentStatus]
    DeploymentStatusMessage: Optional[_string]
    Description: Optional[StringWithLengthBetween0And1024]


class MutualTlsAuthenticationInput(TypedDict, total=False):
    TruststoreUri: Optional[UriWithLengthBetween1And2048]
    TruststoreVersion: Optional[StringWithLengthBetween1And64]


class DomainNameConfiguration(TypedDict, total=False):
    """The domain name configuration."""

    ApiGatewayDomainName: Optional[_string]
    CertificateArn: Optional[Arn]
    CertificateName: Optional[StringWithLengthBetween1And128]
    CertificateUploadDate: Optional[_timestampIso8601]
    DomainNameStatus: Optional[DomainNameStatus]
    DomainNameStatusMessage: Optional[_string]
    EndpointType: Optional[EndpointType]
    HostedZoneId: Optional[_string]
    SecurityPolicy: Optional[SecurityPolicy]
    OwnershipVerificationCertificateArn: Optional[Arn]


DomainNameConfigurations = List[DomainNameConfiguration]


class CreateDomainNameInput(TypedDict, total=False):
    """Represents the input parameters for a CreateDomainName request."""

    DomainName: StringWithLengthBetween1And512
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthenticationInput]
    Tags: Optional[Tags]


class CreateDomainNameRequest(ServiceRequest):
    """Creates a new DomainName resource to represent a domain name."""

    DomainName: StringWithLengthBetween1And512
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthenticationInput]
    Tags: Optional[Tags]


class MutualTlsAuthentication(TypedDict, total=False):
    TruststoreUri: Optional[UriWithLengthBetween1And2048]
    TruststoreVersion: Optional[StringWithLengthBetween1And64]
    TruststoreWarnings: Optional[_listOf__string]


class CreateDomainNameResponse(TypedDict, total=False):
    ApiMappingSelectionExpression: Optional[SelectionExpression]
    DomainName: Optional[StringWithLengthBetween1And512]
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthentication]
    Tags: Optional[Tags]


class TlsConfigInput(TypedDict, total=False):
    """The TLS configuration for a private integration. If you specify a TLS
    configuration, private integration traffic uses the HTTPS protocol.
    Supported only for HTTP APIs.
    """

    ServerNameToVerify: Optional[StringWithLengthBetween1And512]


IntegrationParameters = Dict[_string, StringWithLengthBetween1And512]
ResponseParameters = Dict[_string, IntegrationParameters]
TemplateMap = Dict[_string, StringWithLengthBetween0And32K]


class CreateIntegrationInput(TypedDict, total=False):
    """Represents the input parameters for a CreateIntegration request."""

    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: IntegrationType
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfigInput]


class CreateIntegrationRequest(ServiceRequest):
    """Creates a new Integration resource to represent an integration."""

    ApiId: _string
    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: IntegrationType
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfigInput]


class TlsConfig(TypedDict, total=False):
    """The TLS configuration for a private integration. If you specify a TLS
    configuration, private integration traffic uses the HTTPS protocol.
    Supported only for HTTP APIs.
    """

    ServerNameToVerify: Optional[StringWithLengthBetween1And512]


class CreateIntegrationResult(TypedDict, total=False):
    ApiGatewayManaged: Optional[_boolean]
    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationId: Optional[Id]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationResponseSelectionExpression: Optional[SelectionExpression]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: Optional[IntegrationType]
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfig]


class CreateIntegrationResponseInput(TypedDict, total=False):
    """Represents the input parameters for a CreateIntegrationResponse request."""

    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationResponseKey: SelectionKey
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class CreateIntegrationResponseRequest(ServiceRequest):
    """Creates a new IntegrationResponse resource to represent an integration
    response.
    """

    ApiId: _string
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationId: _string
    IntegrationResponseKey: SelectionKey
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class CreateIntegrationResponseResponse(TypedDict, total=False):
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationResponseId: Optional[Id]
    IntegrationResponseKey: Optional[SelectionKey]
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class CreateModelInput(TypedDict, total=False):
    """Represents the input parameters for a CreateModel request."""

    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    Name: StringWithLengthBetween1And128
    Schema: StringWithLengthBetween0And32K


class CreateModelRequest(ServiceRequest):
    """Creates a new Model."""

    ApiId: _string
    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    Name: StringWithLengthBetween1And128
    Schema: StringWithLengthBetween0And32K


class CreateModelResponse(TypedDict, total=False):
    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    ModelId: Optional[Id]
    Name: Optional[StringWithLengthBetween1And128]
    Schema: Optional[StringWithLengthBetween0And32K]


class ParameterConstraints(TypedDict, total=False):
    """Validation constraints imposed on parameters of a request (path, query
    string, headers).
    """

    Required: Optional[_boolean]


RouteParameters = Dict[_string, ParameterConstraints]
RouteModels = Dict[_string, StringWithLengthBetween1And128]


class CreateRouteInput(TypedDict, total=False):
    """Represents the input parameters for a CreateRoute request."""

    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteKey: SelectionKey
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class CreateRouteRequest(ServiceRequest):
    """Creates a new Route resource to represent a route."""

    ApiId: _string
    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteKey: SelectionKey
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class CreateRouteResult(TypedDict, total=False):
    ApiGatewayManaged: Optional[_boolean]
    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteId: Optional[Id]
    RouteKey: Optional[SelectionKey]
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class CreateRouteResponseInput(TypedDict, total=False):
    """Represents the input parameters for an CreateRouteResponse request."""

    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteResponseKey: SelectionKey


class CreateRouteResponseRequest(ServiceRequest):
    """Creates a new RouteResponse resource to represent a route response."""

    ApiId: _string
    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteId: _string
    RouteResponseKey: SelectionKey


class CreateRouteResponseResponse(TypedDict, total=False):
    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteResponseId: Optional[Id]
    RouteResponseKey: Optional[SelectionKey]


StageVariablesMap = Dict[_string, StringWithLengthBetween0And2048]


class RouteSettings(TypedDict, total=False):
    """Represents a collection of route settings."""

    DataTraceEnabled: Optional[_boolean]
    DetailedMetricsEnabled: Optional[_boolean]
    LoggingLevel: Optional[LoggingLevel]
    ThrottlingBurstLimit: Optional[_integer]
    ThrottlingRateLimit: Optional[_double]


RouteSettingsMap = Dict[_string, RouteSettings]


class CreateStageInput(TypedDict, total=False):
    """Represents the input parameters for a CreateStage request."""

    AccessLogSettings: Optional[AccessLogSettings]
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: StringWithLengthBetween1And128
    StageVariables: Optional[StageVariablesMap]
    Tags: Optional[Tags]


class CreateStageRequest(ServiceRequest):
    """Creates a new Stage resource to represent a stage."""

    AccessLogSettings: Optional[AccessLogSettings]
    ApiId: _string
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: StringWithLengthBetween1And128
    StageVariables: Optional[StageVariablesMap]
    Tags: Optional[Tags]


class CreateStageResponse(TypedDict, total=False):
    AccessLogSettings: Optional[AccessLogSettings]
    ApiGatewayManaged: Optional[_boolean]
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    CreatedDate: Optional[_timestampIso8601]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    LastDeploymentStatusMessage: Optional[_string]
    LastUpdatedDate: Optional[_timestampIso8601]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: Optional[StringWithLengthBetween1And128]
    StageVariables: Optional[StageVariablesMap]
    Tags: Optional[Tags]


SubnetIdList = List[_string]
SecurityGroupIdList = List[_string]


class CreateVpcLinkInput(TypedDict, total=False):
    """Represents the input parameters for a CreateVpcLink request."""

    Name: StringWithLengthBetween1And128
    SecurityGroupIds: Optional[SecurityGroupIdList]
    SubnetIds: SubnetIdList
    Tags: Optional[Tags]


class CreateVpcLinkRequest(ServiceRequest):
    """Creates a VPC link"""

    Name: StringWithLengthBetween1And128
    SecurityGroupIds: Optional[SecurityGroupIdList]
    SubnetIds: SubnetIdList
    Tags: Optional[Tags]


class CreateVpcLinkResponse(TypedDict, total=False):
    CreatedDate: Optional[_timestampIso8601]
    Name: Optional[StringWithLengthBetween1And128]
    SecurityGroupIds: Optional[SecurityGroupIdList]
    SubnetIds: Optional[SubnetIdList]
    Tags: Optional[Tags]
    VpcLinkId: Optional[Id]
    VpcLinkStatus: Optional[VpcLinkStatus]
    VpcLinkStatusMessage: Optional[StringWithLengthBetween0And1024]
    VpcLinkVersion: Optional[VpcLinkVersion]


class DeleteAccessLogSettingsRequest(ServiceRequest):
    ApiId: _string
    StageName: _string


class DeleteApiMappingRequest(ServiceRequest):
    ApiMappingId: _string
    DomainName: _string


class DeleteApiRequest(ServiceRequest):
    ApiId: _string


class DeleteAuthorizerRequest(ServiceRequest):
    ApiId: _string
    AuthorizerId: _string


class DeleteCorsConfigurationRequest(ServiceRequest):
    ApiId: _string


class DeleteDeploymentRequest(ServiceRequest):
    ApiId: _string
    DeploymentId: _string


class DeleteDomainNameRequest(ServiceRequest):
    DomainName: _string


class DeleteIntegrationRequest(ServiceRequest):
    ApiId: _string
    IntegrationId: _string


class DeleteIntegrationResponseRequest(ServiceRequest):
    ApiId: _string
    IntegrationId: _string
    IntegrationResponseId: _string


class DeleteModelRequest(ServiceRequest):
    ApiId: _string
    ModelId: _string


class DeleteRouteRequest(ServiceRequest):
    ApiId: _string
    RouteId: _string


class DeleteRouteRequestParameterRequest(ServiceRequest):
    ApiId: _string
    RequestParameterKey: _string
    RouteId: _string


class DeleteRouteResponseRequest(ServiceRequest):
    ApiId: _string
    RouteId: _string
    RouteResponseId: _string


class DeleteRouteSettingsRequest(ServiceRequest):
    ApiId: _string
    RouteKey: _string
    StageName: _string


class DeleteStageRequest(ServiceRequest):
    ApiId: _string
    StageName: _string


class DeleteVpcLinkRequest(ServiceRequest):
    VpcLinkId: _string


class DeleteVpcLinkResponse(TypedDict, total=False):
    pass


class Deployment(TypedDict, total=False):
    """An immutable representation of an API that can be called by users. A
    Deployment must be associated with a Stage for it to be callable over
    the internet.
    """

    AutoDeployed: Optional[_boolean]
    CreatedDate: Optional[_timestampIso8601]
    DeploymentId: Optional[Id]
    DeploymentStatus: Optional[DeploymentStatus]
    DeploymentStatusMessage: Optional[_string]
    Description: Optional[StringWithLengthBetween0And1024]


_listOfDeployment = List[Deployment]


class Deployments(TypedDict, total=False):
    """A collection resource that contains zero or more references to your
    existing deployments, and links that guide you on how to interact with
    your collection. The collection offers a paginated view of the contained
    deployments.
    """

    Items: Optional[_listOfDeployment]
    NextToken: Optional[NextToken]


class DomainName(TypedDict, total=False):
    """Represents a domain name."""

    ApiMappingSelectionExpression: Optional[SelectionExpression]
    DomainName: StringWithLengthBetween1And512
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthentication]
    Tags: Optional[Tags]


_listOfDomainName = List[DomainName]


class DomainNames(TypedDict, total=False):
    """Represents a collection of domain names."""

    Items: Optional[_listOfDomainName]
    NextToken: Optional[NextToken]


class ExportApiRequest(ServiceRequest):
    ApiId: _string
    ExportVersion: Optional[_string]
    IncludeExtensions: Optional[_boolean]
    OutputType: _string
    Specification: _string
    StageName: Optional[_string]


ExportedApi = bytes


class ExportApiResponse(TypedDict, total=False):
    body: Optional[ExportedApi]


class ResetAuthorizersCacheRequest(ServiceRequest):
    ApiId: _string
    StageName: _string


class GetApiMappingRequest(ServiceRequest):
    ApiMappingId: _string
    DomainName: _string


class GetApiMappingResponse(TypedDict, total=False):
    ApiId: Optional[Id]
    ApiMappingId: Optional[Id]
    ApiMappingKey: Optional[SelectionKey]
    Stage: Optional[StringWithLengthBetween1And128]


class GetApiMappingsRequest(ServiceRequest):
    DomainName: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class GetApiMappingsResponse(TypedDict, total=False):
    Items: Optional[_listOfApiMapping]
    NextToken: Optional[NextToken]


class GetApiRequest(ServiceRequest):
    ApiId: _string


class GetApiResponse(TypedDict, total=False):
    ApiEndpoint: Optional[_string]
    ApiGatewayManaged: Optional[_boolean]
    ApiId: Optional[Id]
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CreatedDate: Optional[_timestampIso8601]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    ImportInfo: Optional[_listOf__string]
    Name: Optional[StringWithLengthBetween1And128]
    ProtocolType: Optional[ProtocolType]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Version: Optional[StringWithLengthBetween1And64]
    Warnings: Optional[_listOf__string]


class GetApisRequest(ServiceRequest):
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class GetApisResponse(TypedDict, total=False):
    Items: Optional[_listOfApi]
    NextToken: Optional[NextToken]


class GetAuthorizerRequest(ServiceRequest):
    ApiId: _string
    AuthorizerId: _string


class GetAuthorizerResponse(TypedDict, total=False):
    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerId: Optional[Id]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: Optional[AuthorizerType]
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: Optional[IdentitySourceList]
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: Optional[StringWithLengthBetween1And128]


class GetAuthorizersRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class GetAuthorizersResponse(TypedDict, total=False):
    Items: Optional[_listOfAuthorizer]
    NextToken: Optional[NextToken]


class GetDeploymentRequest(ServiceRequest):
    ApiId: _string
    DeploymentId: _string


class GetDeploymentResponse(TypedDict, total=False):
    AutoDeployed: Optional[_boolean]
    CreatedDate: Optional[_timestampIso8601]
    DeploymentId: Optional[Id]
    DeploymentStatus: Optional[DeploymentStatus]
    DeploymentStatusMessage: Optional[_string]
    Description: Optional[StringWithLengthBetween0And1024]


class GetDeploymentsRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class GetDeploymentsResponse(TypedDict, total=False):
    Items: Optional[_listOfDeployment]
    NextToken: Optional[NextToken]


class GetDomainNameRequest(ServiceRequest):
    DomainName: _string


class GetDomainNameResponse(TypedDict, total=False):
    ApiMappingSelectionExpression: Optional[SelectionExpression]
    DomainName: Optional[StringWithLengthBetween1And512]
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthentication]
    Tags: Optional[Tags]


class GetDomainNamesRequest(ServiceRequest):
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class GetDomainNamesResponse(TypedDict, total=False):
    Items: Optional[_listOfDomainName]
    NextToken: Optional[NextToken]


class GetIntegrationRequest(ServiceRequest):
    ApiId: _string
    IntegrationId: _string


class GetIntegrationResult(TypedDict, total=False):
    ApiGatewayManaged: Optional[_boolean]
    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationId: Optional[Id]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationResponseSelectionExpression: Optional[SelectionExpression]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: Optional[IntegrationType]
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfig]


class GetIntegrationResponseRequest(ServiceRequest):
    ApiId: _string
    IntegrationId: _string
    IntegrationResponseId: _string


class GetIntegrationResponseResponse(TypedDict, total=False):
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationResponseId: Optional[Id]
    IntegrationResponseKey: Optional[SelectionKey]
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class GetIntegrationResponsesRequest(ServiceRequest):
    ApiId: _string
    IntegrationId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class IntegrationResponse(TypedDict, total=False):
    """Represents an integration response."""

    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationResponseId: Optional[Id]
    IntegrationResponseKey: SelectionKey
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


_listOfIntegrationResponse = List[IntegrationResponse]


class GetIntegrationResponsesResponse(TypedDict, total=False):
    Items: Optional[_listOfIntegrationResponse]
    NextToken: Optional[NextToken]


class GetIntegrationsRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class Integration(TypedDict, total=False):
    """Represents an integration."""

    ApiGatewayManaged: Optional[_boolean]
    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationId: Optional[Id]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationResponseSelectionExpression: Optional[SelectionExpression]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: Optional[IntegrationType]
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfig]


_listOfIntegration = List[Integration]


class GetIntegrationsResponse(TypedDict, total=False):
    Items: Optional[_listOfIntegration]
    NextToken: Optional[NextToken]


class GetModelRequest(ServiceRequest):
    ApiId: _string
    ModelId: _string


class GetModelResponse(TypedDict, total=False):
    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    ModelId: Optional[Id]
    Name: Optional[StringWithLengthBetween1And128]
    Schema: Optional[StringWithLengthBetween0And32K]


class GetModelTemplateRequest(ServiceRequest):
    ApiId: _string
    ModelId: _string


class GetModelTemplateResponse(TypedDict, total=False):
    Value: Optional[_string]


class GetModelsRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class Model(TypedDict, total=False):
    """Represents a data model for an API. Supported only for WebSocket APIs.
    See `Create Models and Mapping Templates for Request and Response
    Mappings <https://docs.aws.amazon.com/apigateway/latest/developerguide/models-mappings.html>`__.
    """

    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    ModelId: Optional[Id]
    Name: StringWithLengthBetween1And128
    Schema: Optional[StringWithLengthBetween0And32K]


_listOfModel = List[Model]


class GetModelsResponse(TypedDict, total=False):
    Items: Optional[_listOfModel]
    NextToken: Optional[NextToken]


class GetRouteRequest(ServiceRequest):
    ApiId: _string
    RouteId: _string


class GetRouteResult(TypedDict, total=False):
    ApiGatewayManaged: Optional[_boolean]
    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteId: Optional[Id]
    RouteKey: Optional[SelectionKey]
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class GetRouteResponseRequest(ServiceRequest):
    ApiId: _string
    RouteId: _string
    RouteResponseId: _string


class GetRouteResponseResponse(TypedDict, total=False):
    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteResponseId: Optional[Id]
    RouteResponseKey: Optional[SelectionKey]


class GetRouteResponsesRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]
    RouteId: _string


class RouteResponse(TypedDict, total=False):
    """Represents a route response."""

    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteResponseId: Optional[Id]
    RouteResponseKey: SelectionKey


_listOfRouteResponse = List[RouteResponse]


class GetRouteResponsesResponse(TypedDict, total=False):
    Items: Optional[_listOfRouteResponse]
    NextToken: Optional[NextToken]


class GetRoutesRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class Route(TypedDict, total=False):
    """Represents a route."""

    ApiGatewayManaged: Optional[_boolean]
    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteId: Optional[Id]
    RouteKey: SelectionKey
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


_listOfRoute = List[Route]


class GetRoutesResponse(TypedDict, total=False):
    Items: Optional[_listOfRoute]
    NextToken: Optional[NextToken]


class GetStageRequest(ServiceRequest):
    ApiId: _string
    StageName: _string


class GetStageResponse(TypedDict, total=False):
    AccessLogSettings: Optional[AccessLogSettings]
    ApiGatewayManaged: Optional[_boolean]
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    CreatedDate: Optional[_timestampIso8601]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    LastDeploymentStatusMessage: Optional[_string]
    LastUpdatedDate: Optional[_timestampIso8601]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: Optional[StringWithLengthBetween1And128]
    StageVariables: Optional[StageVariablesMap]
    Tags: Optional[Tags]


class GetStagesRequest(ServiceRequest):
    ApiId: _string
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class Stage(TypedDict, total=False):
    """Represents an API stage."""

    AccessLogSettings: Optional[AccessLogSettings]
    ApiGatewayManaged: Optional[_boolean]
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    CreatedDate: Optional[_timestampIso8601]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    LastDeploymentStatusMessage: Optional[_string]
    LastUpdatedDate: Optional[_timestampIso8601]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: StringWithLengthBetween1And128
    StageVariables: Optional[StageVariablesMap]
    Tags: Optional[Tags]


_listOfStage = List[Stage]


class GetStagesResponse(TypedDict, total=False):
    Items: Optional[_listOfStage]
    NextToken: Optional[NextToken]


class GetTagsRequest(ServiceRequest):
    ResourceArn: _string


class GetTagsResponse(TypedDict, total=False):
    Tags: Optional[Tags]


class GetVpcLinkRequest(ServiceRequest):
    VpcLinkId: _string


class GetVpcLinkResponse(TypedDict, total=False):
    CreatedDate: Optional[_timestampIso8601]
    Name: Optional[StringWithLengthBetween1And128]
    SecurityGroupIds: Optional[SecurityGroupIdList]
    SubnetIds: Optional[SubnetIdList]
    Tags: Optional[Tags]
    VpcLinkId: Optional[Id]
    VpcLinkStatus: Optional[VpcLinkStatus]
    VpcLinkStatusMessage: Optional[StringWithLengthBetween0And1024]
    VpcLinkVersion: Optional[VpcLinkVersion]


class GetVpcLinksRequest(ServiceRequest):
    MaxResults: Optional[_string]
    NextToken: Optional[_string]


class VpcLink(TypedDict, total=False):
    """Represents a VPC link."""

    CreatedDate: Optional[_timestampIso8601]
    Name: StringWithLengthBetween1And128
    SecurityGroupIds: SecurityGroupIdList
    SubnetIds: SubnetIdList
    Tags: Optional[Tags]
    VpcLinkId: Id
    VpcLinkStatus: Optional[VpcLinkStatus]
    VpcLinkStatusMessage: Optional[StringWithLengthBetween0And1024]
    VpcLinkVersion: Optional[VpcLinkVersion]


_listOfVpcLink = List[VpcLink]


class GetVpcLinksResponse(TypedDict, total=False):
    Items: Optional[_listOfVpcLink]
    NextToken: Optional[NextToken]


class ImportApiInput(TypedDict, total=False):
    """Represents the input to ImportAPI. Supported only for HTTP APIs."""

    Body: _string


class ImportApiRequest(ServiceRequest):
    Basepath: Optional[_string]
    Body: _string
    FailOnWarnings: Optional[_boolean]


class ImportApiResponse(TypedDict, total=False):
    ApiEndpoint: Optional[_string]
    ApiGatewayManaged: Optional[_boolean]
    ApiId: Optional[Id]
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CreatedDate: Optional[_timestampIso8601]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    ImportInfo: Optional[_listOf__string]
    Name: Optional[StringWithLengthBetween1And128]
    ProtocolType: Optional[ProtocolType]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Version: Optional[StringWithLengthBetween1And64]
    Warnings: Optional[_listOf__string]


class IntegrationResponses(TypedDict, total=False):
    """Represents a collection of integration responses."""

    Items: Optional[_listOfIntegrationResponse]
    NextToken: Optional[NextToken]


class Integrations(TypedDict, total=False):
    """Represents a collection of integrations."""

    Items: Optional[_listOfIntegration]
    NextToken: Optional[NextToken]


class LimitExceededException(TypedDict, total=False):
    """A limit has been exceeded. See the accompanying error message for
    details.
    """

    LimitType: Optional[_string]
    Message: Optional[_string]


class Models(TypedDict, total=False):
    """Represents a collection of data models. See `Create Models and Mapping
    Templates for Request and Response
    Mappings <https://docs.aws.amazon.com/apigateway/latest/developerguide/models-mappings.html>`__.
    """

    Items: Optional[_listOfModel]
    NextToken: Optional[NextToken]


class ReimportApiInput(TypedDict, total=False):
    """Overwrites the configuration of an existing API using the provided
    definition. Supported only for HTTP APIs.
    """

    Body: _string


class ReimportApiRequest(ServiceRequest):
    ApiId: _string
    Basepath: Optional[_string]
    Body: _string
    FailOnWarnings: Optional[_boolean]


class ReimportApiResponse(TypedDict, total=False):
    ApiEndpoint: Optional[_string]
    ApiGatewayManaged: Optional[_boolean]
    ApiId: Optional[Id]
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CreatedDate: Optional[_timestampIso8601]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    ImportInfo: Optional[_listOf__string]
    Name: Optional[StringWithLengthBetween1And128]
    ProtocolType: Optional[ProtocolType]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Version: Optional[StringWithLengthBetween1And64]
    Warnings: Optional[_listOf__string]


class RouteResponses(TypedDict, total=False):
    """Represents a collection of route responses."""

    Items: Optional[_listOfRouteResponse]
    NextToken: Optional[NextToken]


class Routes(TypedDict, total=False):
    """Represents a collection of routes."""

    Items: Optional[_listOfRoute]
    NextToken: Optional[NextToken]


class Stages(TypedDict, total=False):
    """A collection of Stage resources that are associated with the ApiKey
    resource.
    """

    Items: Optional[_listOfStage]
    NextToken: Optional[NextToken]


class TagResourceInput(TypedDict, total=False):
    """Represents the input parameters for a TagResource request."""

    Tags: Optional[Tags]


class TagResourceRequest(ServiceRequest):
    """Creates a new Tag resource to represent a tag."""

    ResourceArn: _string
    Tags: Optional[Tags]


class TagResourceResponse(TypedDict, total=False):
    pass


class Template(TypedDict, total=False):
    """Represents a template."""

    Value: Optional[_string]


class UntagResourceRequest(ServiceRequest):
    ResourceArn: _string
    TagKeys: _listOf__string


class UpdateApiInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateApi request."""

    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableExecuteApiEndpoint: Optional[_boolean]
    DisableSchemaValidation: Optional[_boolean]
    Name: Optional[StringWithLengthBetween1And128]
    RouteKey: Optional[SelectionKey]
    RouteSelectionExpression: Optional[SelectionExpression]
    Target: Optional[UriWithLengthBetween1And2048]
    Version: Optional[StringWithLengthBetween1And64]


class UpdateApiMappingInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateApiMapping request."""

    ApiId: Optional[Id]
    ApiMappingKey: Optional[SelectionKey]
    Stage: Optional[StringWithLengthBetween1And128]


class UpdateApiMappingRequest(ServiceRequest):
    """Updates an ApiMapping."""

    ApiId: Id
    ApiMappingId: _string
    ApiMappingKey: Optional[SelectionKey]
    DomainName: _string
    Stage: Optional[StringWithLengthBetween1And128]


class UpdateApiMappingResponse(TypedDict, total=False):
    ApiId: Optional[Id]
    ApiMappingId: Optional[Id]
    ApiMappingKey: Optional[SelectionKey]
    Stage: Optional[StringWithLengthBetween1And128]


class UpdateApiRequest(ServiceRequest):
    """Updates an Api."""

    ApiId: _string
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    Name: Optional[StringWithLengthBetween1And128]
    RouteKey: Optional[SelectionKey]
    RouteSelectionExpression: Optional[SelectionExpression]
    Target: Optional[UriWithLengthBetween1And2048]
    Version: Optional[StringWithLengthBetween1And64]


class UpdateApiResponse(TypedDict, total=False):
    ApiEndpoint: Optional[_string]
    ApiGatewayManaged: Optional[_boolean]
    ApiId: Optional[Id]
    ApiKeySelectionExpression: Optional[SelectionExpression]
    CorsConfiguration: Optional[Cors]
    CreatedDate: Optional[_timestampIso8601]
    Description: Optional[StringWithLengthBetween0And1024]
    DisableSchemaValidation: Optional[_boolean]
    DisableExecuteApiEndpoint: Optional[_boolean]
    ImportInfo: Optional[_listOf__string]
    Name: Optional[StringWithLengthBetween1And128]
    ProtocolType: Optional[ProtocolType]
    RouteSelectionExpression: Optional[SelectionExpression]
    Tags: Optional[Tags]
    Version: Optional[StringWithLengthBetween1And64]
    Warnings: Optional[_listOf__string]


class UpdateAuthorizerInput(TypedDict, total=False):
    """The input parameters for an UpdateAuthorizer request."""

    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: Optional[AuthorizerType]
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: Optional[IdentitySourceList]
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: Optional[StringWithLengthBetween1And128]


class UpdateAuthorizerRequest(ServiceRequest):
    """Updates an Authorizer."""

    ApiId: _string
    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerId: _string
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: Optional[AuthorizerType]
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: Optional[IdentitySourceList]
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: Optional[StringWithLengthBetween1And128]


class UpdateAuthorizerResponse(TypedDict, total=False):
    AuthorizerCredentialsArn: Optional[Arn]
    AuthorizerId: Optional[Id]
    AuthorizerPayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    AuthorizerResultTtlInSeconds: Optional[IntegerWithLengthBetween0And3600]
    AuthorizerType: Optional[AuthorizerType]
    AuthorizerUri: Optional[UriWithLengthBetween1And2048]
    EnableSimpleResponses: Optional[_boolean]
    IdentitySource: Optional[IdentitySourceList]
    IdentityValidationExpression: Optional[StringWithLengthBetween0And1024]
    JwtConfiguration: Optional[JWTConfiguration]
    Name: Optional[StringWithLengthBetween1And128]


class UpdateDeploymentInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateDeployment request."""

    Description: Optional[StringWithLengthBetween0And1024]


class UpdateDeploymentRequest(ServiceRequest):
    """Updates a Deployment."""

    ApiId: _string
    DeploymentId: _string
    Description: Optional[StringWithLengthBetween0And1024]


class UpdateDeploymentResponse(TypedDict, total=False):
    AutoDeployed: Optional[_boolean]
    CreatedDate: Optional[_timestampIso8601]
    DeploymentId: Optional[Id]
    DeploymentStatus: Optional[DeploymentStatus]
    DeploymentStatusMessage: Optional[_string]
    Description: Optional[StringWithLengthBetween0And1024]


class UpdateDomainNameInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateDomainName request."""

    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthenticationInput]


class UpdateDomainNameRequest(ServiceRequest):
    """Updates a DomainName."""

    DomainName: _string
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthenticationInput]


class UpdateDomainNameResponse(TypedDict, total=False):
    ApiMappingSelectionExpression: Optional[SelectionExpression]
    DomainName: Optional[StringWithLengthBetween1And512]
    DomainNameConfigurations: Optional[DomainNameConfigurations]
    MutualTlsAuthentication: Optional[MutualTlsAuthentication]
    Tags: Optional[Tags]


class UpdateIntegrationInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateIntegration request."""

    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: Optional[IntegrationType]
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfigInput]


class UpdateIntegrationRequest(ServiceRequest):
    """Updates an Integration."""

    ApiId: _string
    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationId: _string
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: Optional[IntegrationType]
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfigInput]


class UpdateIntegrationResult(TypedDict, total=False):
    ApiGatewayManaged: Optional[_boolean]
    ConnectionId: Optional[StringWithLengthBetween1And1024]
    ConnectionType: Optional[ConnectionType]
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    CredentialsArn: Optional[Arn]
    Description: Optional[StringWithLengthBetween0And1024]
    IntegrationId: Optional[Id]
    IntegrationMethod: Optional[StringWithLengthBetween1And64]
    IntegrationResponseSelectionExpression: Optional[SelectionExpression]
    IntegrationSubtype: Optional[StringWithLengthBetween1And128]
    IntegrationType: Optional[IntegrationType]
    IntegrationUri: Optional[UriWithLengthBetween1And2048]
    PassthroughBehavior: Optional[PassthroughBehavior]
    PayloadFormatVersion: Optional[StringWithLengthBetween1And64]
    RequestParameters: Optional[IntegrationParameters]
    RequestTemplates: Optional[TemplateMap]
    ResponseParameters: Optional[ResponseParameters]
    TemplateSelectionExpression: Optional[SelectionExpression]
    TimeoutInMillis: Optional[IntegerWithLengthBetween50And30000]
    TlsConfig: Optional[TlsConfig]


class UpdateIntegrationResponseInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateIntegrationResponse
    request.
    """

    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationResponseKey: Optional[SelectionKey]
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class UpdateIntegrationResponseRequest(ServiceRequest):
    """Updates an IntegrationResponses."""

    ApiId: _string
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationId: _string
    IntegrationResponseId: _string
    IntegrationResponseKey: Optional[SelectionKey]
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class UpdateIntegrationResponseResponse(TypedDict, total=False):
    ContentHandlingStrategy: Optional[ContentHandlingStrategy]
    IntegrationResponseId: Optional[Id]
    IntegrationResponseKey: Optional[SelectionKey]
    ResponseParameters: Optional[IntegrationParameters]
    ResponseTemplates: Optional[TemplateMap]
    TemplateSelectionExpression: Optional[SelectionExpression]


class UpdateModelInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateModel request. Supported
    only for WebSocket APIs.
    """

    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    Name: Optional[StringWithLengthBetween1And128]
    Schema: Optional[StringWithLengthBetween0And32K]


class UpdateModelRequest(ServiceRequest):
    """Updates a Model."""

    ApiId: _string
    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    ModelId: _string
    Name: Optional[StringWithLengthBetween1And128]
    Schema: Optional[StringWithLengthBetween0And32K]


class UpdateModelResponse(TypedDict, total=False):
    ContentType: Optional[StringWithLengthBetween1And256]
    Description: Optional[StringWithLengthBetween0And1024]
    ModelId: Optional[Id]
    Name: Optional[StringWithLengthBetween1And128]
    Schema: Optional[StringWithLengthBetween0And32K]


class UpdateRouteInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateRoute request."""

    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteKey: Optional[SelectionKey]
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class UpdateRouteRequest(ServiceRequest):
    """Updates a Route."""

    ApiId: _string
    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteId: _string
    RouteKey: Optional[SelectionKey]
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class UpdateRouteResult(TypedDict, total=False):
    ApiGatewayManaged: Optional[_boolean]
    ApiKeyRequired: Optional[_boolean]
    AuthorizationScopes: Optional[AuthorizationScopes]
    AuthorizationType: Optional[AuthorizationType]
    AuthorizerId: Optional[Id]
    ModelSelectionExpression: Optional[SelectionExpression]
    OperationName: Optional[StringWithLengthBetween1And64]
    RequestModels: Optional[RouteModels]
    RequestParameters: Optional[RouteParameters]
    RouteId: Optional[Id]
    RouteKey: Optional[SelectionKey]
    RouteResponseSelectionExpression: Optional[SelectionExpression]
    Target: Optional[StringWithLengthBetween1And128]


class UpdateRouteResponseInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateRouteResponse request."""

    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteResponseKey: Optional[SelectionKey]


class UpdateRouteResponseRequest(ServiceRequest):
    """Updates a RouteResponse."""

    ApiId: _string
    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteId: _string
    RouteResponseId: _string
    RouteResponseKey: Optional[SelectionKey]


class UpdateRouteResponseResponse(TypedDict, total=False):
    ModelSelectionExpression: Optional[SelectionExpression]
    ResponseModels: Optional[RouteModels]
    ResponseParameters: Optional[RouteParameters]
    RouteResponseId: Optional[Id]
    RouteResponseKey: Optional[SelectionKey]


class UpdateStageInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateStage request."""

    AccessLogSettings: Optional[AccessLogSettings]
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    RouteSettings: Optional[RouteSettingsMap]
    StageVariables: Optional[StageVariablesMap]


class UpdateStageRequest(ServiceRequest):
    """Updates a Stage."""

    AccessLogSettings: Optional[AccessLogSettings]
    ApiId: _string
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: _string
    StageVariables: Optional[StageVariablesMap]


class UpdateStageResponse(TypedDict, total=False):
    AccessLogSettings: Optional[AccessLogSettings]
    ApiGatewayManaged: Optional[_boolean]
    AutoDeploy: Optional[_boolean]
    ClientCertificateId: Optional[Id]
    CreatedDate: Optional[_timestampIso8601]
    DefaultRouteSettings: Optional[RouteSettings]
    DeploymentId: Optional[Id]
    Description: Optional[StringWithLengthBetween0And1024]
    LastDeploymentStatusMessage: Optional[_string]
    LastUpdatedDate: Optional[_timestampIso8601]
    RouteSettings: Optional[RouteSettingsMap]
    StageName: Optional[StringWithLengthBetween1And128]
    StageVariables: Optional[StageVariablesMap]
    Tags: Optional[Tags]


class UpdateVpcLinkInput(TypedDict, total=False):
    """Represents the input parameters for an UpdateVpcLink request."""

    Name: Optional[StringWithLengthBetween1And128]


class UpdateVpcLinkRequest(ServiceRequest):
    """Updates a VPC link."""

    Name: Optional[StringWithLengthBetween1And128]
    VpcLinkId: _string


class UpdateVpcLinkResponse(TypedDict, total=False):
    CreatedDate: Optional[_timestampIso8601]
    Name: Optional[StringWithLengthBetween1And128]
    SecurityGroupIds: Optional[SecurityGroupIdList]
    SubnetIds: Optional[SubnetIdList]
    Tags: Optional[Tags]
    VpcLinkId: Optional[Id]
    VpcLinkStatus: Optional[VpcLinkStatus]
    VpcLinkStatusMessage: Optional[StringWithLengthBetween0And1024]
    VpcLinkVersion: Optional[VpcLinkVersion]


class VpcLinks(TypedDict, total=False):
    """Represents a collection of VPCLinks."""

    Items: Optional[_listOfVpcLink]
    NextToken: Optional[NextToken]


_long = int
_timestampUnix = datetime


class Apigatewayv2Api:

    service = "apigatewayv2"
    version = "2018-11-29"

    @handler("CreateApi")
    def create_api(
        self,
        context: RequestContext,
        protocol_type: ProtocolType,
        name: StringWithLengthBetween1And128,
        api_key_selection_expression: SelectionExpression = None,
        cors_configuration: Cors = None,
        credentials_arn: Arn = None,
        description: StringWithLengthBetween0And1024 = None,
        disable_schema_validation: _boolean = None,
        disable_execute_api_endpoint: _boolean = None,
        route_key: SelectionKey = None,
        route_selection_expression: SelectionExpression = None,
        tags: Tags = None,
        target: UriWithLengthBetween1And2048 = None,
        version: StringWithLengthBetween1And64 = None,
    ) -> CreateApiResponse:
        """Creates an Api resource.

        :param protocol_type: The API protocol.
        :param name: The name of the API.
        :param api_key_selection_expression: An API key selection expression.
        :param cors_configuration: A CORS configuration.
        :param credentials_arn: This property is part of quick create.
        :param description: The description of the API.
        :param disable_schema_validation: Avoid validating models when creating a deployment.
        :param disable_execute_api_endpoint: Specifies whether clients can invoke your API by using the default
        execute-api endpoint.
        :param route_key: This property is part of quick create.
        :param route_selection_expression: The route selection expression for the API.
        :param tags: The collection of tags.
        :param target: This property is part of quick create.
        :param version: A version identifier for the API.
        :returns: CreateApiResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateApiMapping")
    def create_api_mapping(
        self,
        context: RequestContext,
        domain_name: _string,
        stage: StringWithLengthBetween1And128,
        api_id: Id,
        api_mapping_key: SelectionKey = None,
    ) -> CreateApiMappingResponse:
        """Creates an API mapping.

        :param domain_name: The domain name.
        :param stage: The API stage.
        :param api_id: The API identifier.
        :param api_mapping_key: The API mapping key.
        :returns: CreateApiMappingResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateAuthorizer")
    def create_authorizer(
        self,
        context: RequestContext,
        api_id: _string,
        authorizer_type: AuthorizerType,
        identity_source: IdentitySourceList,
        name: StringWithLengthBetween1And128,
        authorizer_credentials_arn: Arn = None,
        authorizer_payload_format_version: StringWithLengthBetween1And64 = None,
        authorizer_result_ttl_in_seconds: IntegerWithLengthBetween0And3600 = None,
        authorizer_uri: UriWithLengthBetween1And2048 = None,
        enable_simple_responses: _boolean = None,
        identity_validation_expression: StringWithLengthBetween0And1024 = None,
        jwt_configuration: JWTConfiguration = None,
    ) -> CreateAuthorizerResponse:
        """Creates an Authorizer for an API.

        :param api_id: The API identifier.
        :param authorizer_type: The authorizer type.
        :param identity_source: The identity source for which authorization is requested.
        :param name: The name of the authorizer.
        :param authorizer_credentials_arn: Specifies the required credentials as an IAM role for API Gateway to
        invoke the authorizer.
        :param authorizer_payload_format_version: Specifies the format of the payload sent to an HTTP API Lambda
        authorizer.
        :param authorizer_result_ttl_in_seconds: The time to live (TTL) for cached authorizer results, in seconds.
        :param authorizer_uri: The authorizer's Uniform Resource Identifier (URI).
        :param enable_simple_responses: Specifies whether a Lambda authorizer returns a response in a simple
        format.
        :param identity_validation_expression: This parameter is not used.
        :param jwt_configuration: Represents the configuration of a JWT authorizer.
        :returns: CreateAuthorizerResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateDeployment")
    def create_deployment(
        self,
        context: RequestContext,
        api_id: _string,
        description: StringWithLengthBetween0And1024 = None,
        stage_name: StringWithLengthBetween1And128 = None,
    ) -> CreateDeploymentResponse:
        """Creates a Deployment for an API.

        :param api_id: The API identifier.
        :param description: The description for the deployment resource.
        :param stage_name: The name of the Stage resource for the Deployment resource to create.
        :returns: CreateDeploymentResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateDomainName")
    def create_domain_name(
        self,
        context: RequestContext,
        domain_name: StringWithLengthBetween1And512,
        domain_name_configurations: DomainNameConfigurations = None,
        mutual_tls_authentication: MutualTlsAuthenticationInput = None,
        tags: Tags = None,
    ) -> CreateDomainNameResponse:
        """Creates a domain name.

        :param domain_name: The domain name.
        :param domain_name_configurations: The domain name configurations.
        :param mutual_tls_authentication: The mutual TLS authentication configuration for a custom domain name.
        :param tags: The collection of tags associated with a domain name.
        :returns: CreateDomainNameResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("CreateIntegration")
    def create_integration(
        self,
        context: RequestContext,
        api_id: _string,
        integration_type: IntegrationType,
        connection_id: StringWithLengthBetween1And1024 = None,
        connection_type: ConnectionType = None,
        content_handling_strategy: ContentHandlingStrategy = None,
        credentials_arn: Arn = None,
        description: StringWithLengthBetween0And1024 = None,
        integration_method: StringWithLengthBetween1And64 = None,
        integration_subtype: StringWithLengthBetween1And128 = None,
        integration_uri: UriWithLengthBetween1And2048 = None,
        passthrough_behavior: PassthroughBehavior = None,
        payload_format_version: StringWithLengthBetween1And64 = None,
        request_parameters: IntegrationParameters = None,
        request_templates: TemplateMap = None,
        response_parameters: ResponseParameters = None,
        template_selection_expression: SelectionExpression = None,
        timeout_in_millis: IntegerWithLengthBetween50And30000 = None,
        tls_config: TlsConfigInput = None,
    ) -> CreateIntegrationResult:
        """Creates an Integration.

        :param api_id: The API identifier.
        :param integration_type: The integration type of an integration.
        :param connection_id: The ID of the VPC link for a private integration.
        :param connection_type: The type of the network connection to the integration endpoint.
        :param content_handling_strategy: Supported only for WebSocket APIs.
        :param credentials_arn: Specifies the credentials required for the integration, if any.
        :param description: The description of the integration.
        :param integration_method: Specifies the integration's HTTP method type.
        :param integration_subtype: Supported only for HTTP API AWS_PROXY integrations.
        :param integration_uri: For a Lambda integration, specify the URI of a Lambda function.
        :param passthrough_behavior: Specifies the pass-through behavior for incoming requests based on the
        Content-Type header in the request, and the available mapping templates
        specified as the requestTemplates property on the Integration resource.
        :param payload_format_version: Specifies the format of the payload sent to an integration.
        :param request_parameters: For WebSocket APIs, a key-value map specifying request parameters that
        are passed from the method request to the backend.
        :param request_templates: Represents a map of Velocity templates that are applied on the request
        payload based on the value of the Content-Type header sent by the
        client.
        :param response_parameters: Supported only for HTTP APIs.
        :param template_selection_expression: The template selection expression for the integration.
        :param timeout_in_millis: Custom timeout between 50 and 29,000 milliseconds for WebSocket APIs and
        between 50 and 30,000 milliseconds for HTTP APIs.
        :param tls_config: The TLS configuration for a private integration.
        :returns: CreateIntegrationResult
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateIntegrationResponse")
    def create_integration_response(
        self,
        context: RequestContext,
        api_id: _string,
        integration_id: _string,
        integration_response_key: SelectionKey,
        content_handling_strategy: ContentHandlingStrategy = None,
        response_parameters: IntegrationParameters = None,
        response_templates: TemplateMap = None,
        template_selection_expression: SelectionExpression = None,
    ) -> CreateIntegrationResponseResponse:
        """Creates an IntegrationResponses.

        :param api_id: The API identifier.
        :param integration_id: The integration ID.
        :param integration_response_key: The integration response key.
        :param content_handling_strategy: Specifies how to handle response payload content type conversions.
        :param response_parameters: A key-value map specifying response parameters that are passed to the
        method response from the backend.
        :param response_templates: The collection of response templates for the integration response as a
        string-to-string map of key-value pairs.
        :param template_selection_expression: The template selection expression for the integration response.
        :returns: CreateIntegrationResponseResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateModel")
    def create_model(
        self,
        context: RequestContext,
        api_id: _string,
        schema: StringWithLengthBetween0And32K,
        name: StringWithLengthBetween1And128,
        content_type: StringWithLengthBetween1And256 = None,
        description: StringWithLengthBetween0And1024 = None,
    ) -> CreateModelResponse:
        """Creates a Model for an API.

        :param api_id: The API identifier.
        :param schema: The schema for the model.
        :param name: The name of the model.
        :param content_type: The content-type for the model, for example, "application/json".
        :param description: The description of the model.
        :returns: CreateModelResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateRoute")
    def create_route(
        self,
        context: RequestContext,
        api_id: _string,
        route_key: SelectionKey,
        api_key_required: _boolean = None,
        authorization_scopes: AuthorizationScopes = None,
        authorization_type: AuthorizationType = None,
        authorizer_id: Id = None,
        model_selection_expression: SelectionExpression = None,
        operation_name: StringWithLengthBetween1And64 = None,
        request_models: RouteModels = None,
        request_parameters: RouteParameters = None,
        route_response_selection_expression: SelectionExpression = None,
        target: StringWithLengthBetween1And128 = None,
    ) -> CreateRouteResult:
        """Creates a Route for an API.

        :param api_id: The API identifier.
        :param route_key: The route key for the route.
        :param api_key_required: Specifies whether an API key is required for the route.
        :param authorization_scopes: The authorization scopes supported by this route.
        :param authorization_type: The authorization type for the route.
        :param authorizer_id: The identifier of the Authorizer resource to be associated with this
        route.
        :param model_selection_expression: The model selection expression for the route.
        :param operation_name: The operation name for the route.
        :param request_models: The request models for the route.
        :param request_parameters: The request parameters for the route.
        :param route_response_selection_expression: The route response selection expression for the route.
        :param target: The target for the route.
        :returns: CreateRouteResult
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateRouteResponse")
    def create_route_response(
        self,
        context: RequestContext,
        api_id: _string,
        route_id: _string,
        route_response_key: SelectionKey,
        model_selection_expression: SelectionExpression = None,
        response_models: RouteModels = None,
        response_parameters: RouteParameters = None,
    ) -> CreateRouteResponseResponse:
        """Creates a RouteResponse for a Route.

        :param api_id: The API identifier.
        :param route_id: The route ID.
        :param route_response_key: The route response key.
        :param model_selection_expression: The model selection expression for the route response.
        :param response_models: The response models for the route response.
        :param response_parameters: The route response parameters.
        :returns: CreateRouteResponseResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateStage")
    def create_stage(
        self,
        context: RequestContext,
        api_id: _string,
        stage_name: StringWithLengthBetween1And128,
        access_log_settings: AccessLogSettings = None,
        auto_deploy: _boolean = None,
        client_certificate_id: Id = None,
        default_route_settings: RouteSettings = None,
        deployment_id: Id = None,
        description: StringWithLengthBetween0And1024 = None,
        route_settings: RouteSettingsMap = None,
        stage_variables: StageVariablesMap = None,
        tags: Tags = None,
    ) -> CreateStageResponse:
        """Creates a Stage for an API.

        :param api_id: The API identifier.
        :param stage_name: The name of the stage.
        :param access_log_settings: Settings for logging access in this stage.
        :param auto_deploy: Specifies whether updates to an API automatically trigger a new
        deployment.
        :param client_certificate_id: The identifier of a client certificate for a Stage.
        :param default_route_settings: The default route settings for the stage.
        :param deployment_id: The deployment identifier of the API stage.
        :param description: The description for the API stage.
        :param route_settings: Route settings for the stage, by routeKey.
        :param stage_variables: A map that defines the stage variables for a Stage.
        :param tags: The collection of tags.
        :returns: CreateStageResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateVpcLink")
    def create_vpc_link(
        self,
        context: RequestContext,
        subnet_ids: SubnetIdList,
        name: StringWithLengthBetween1And128,
        security_group_ids: SecurityGroupIdList = None,
        tags: Tags = None,
    ) -> CreateVpcLinkResponse:
        """Creates a VPC link.

        :param subnet_ids: A list of subnet IDs to include in the VPC link.
        :param name: The name of the VPC link.
        :param security_group_ids: A list of security group IDs for the VPC link.
        :param tags: A list of tags.
        :returns: CreateVpcLinkResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteAccessLogSettings")
    def delete_access_log_settings(
        self, context: RequestContext, stage_name: _string, api_id: _string
    ) -> None:
        """Deletes the AccessLogSettings for a Stage. To disable access logging for
        a Stage, delete its AccessLogSettings.

        :param stage_name: The stage name.
        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteApi")
    def delete_api(self, context: RequestContext, api_id: _string) -> None:
        """Deletes an Api resource.

        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteApiMapping")
    def delete_api_mapping(
        self, context: RequestContext, api_mapping_id: _string, domain_name: _string
    ) -> None:
        """Deletes an API mapping.

        :param api_mapping_id: The API mapping identifier.
        :param domain_name: The domain name.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteAuthorizer")
    def delete_authorizer(
        self, context: RequestContext, authorizer_id: _string, api_id: _string
    ) -> None:
        """Deletes an Authorizer.

        :param authorizer_id: The authorizer identifier.
        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteCorsConfiguration")
    def delete_cors_configuration(self, context: RequestContext, api_id: _string) -> None:
        """Deletes a CORS configuration.

        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteDeployment")
    def delete_deployment(
        self, context: RequestContext, api_id: _string, deployment_id: _string
    ) -> None:
        """Deletes a Deployment.

        :param api_id: The API identifier.
        :param deployment_id: The deployment ID.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteDomainName")
    def delete_domain_name(self, context: RequestContext, domain_name: _string) -> None:
        """Deletes a domain name.

        :param domain_name: The domain name.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteIntegration")
    def delete_integration(
        self, context: RequestContext, api_id: _string, integration_id: _string
    ) -> None:
        """Deletes an Integration.

        :param api_id: The API identifier.
        :param integration_id: The integration ID.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteIntegrationResponse")
    def delete_integration_response(
        self,
        context: RequestContext,
        api_id: _string,
        integration_response_id: _string,
        integration_id: _string,
    ) -> None:
        """Deletes an IntegrationResponses.

        :param api_id: The API identifier.
        :param integration_response_id: The integration response ID.
        :param integration_id: The integration ID.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteModel")
    def delete_model(self, context: RequestContext, model_id: _string, api_id: _string) -> None:
        """Deletes a Model.

        :param model_id: The model ID.
        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteRoute")
    def delete_route(self, context: RequestContext, api_id: _string, route_id: _string) -> None:
        """Deletes a Route.

        :param api_id: The API identifier.
        :param route_id: The route ID.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteRouteRequestParameter")
    def delete_route_request_parameter(
        self,
        context: RequestContext,
        request_parameter_key: _string,
        api_id: _string,
        route_id: _string,
    ) -> None:
        """Deletes a route request parameter.

        :param request_parameter_key: The route request parameter key.
        :param api_id: The API identifier.
        :param route_id: The route ID.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteRouteResponse")
    def delete_route_response(
        self,
        context: RequestContext,
        route_response_id: _string,
        api_id: _string,
        route_id: _string,
    ) -> None:
        """Deletes a RouteResponse.

        :param route_response_id: The route response ID.
        :param api_id: The API identifier.
        :param route_id: The route ID.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteRouteSettings")
    def delete_route_settings(
        self, context: RequestContext, stage_name: _string, route_key: _string, api_id: _string
    ) -> None:
        """Deletes the RouteSettings for a stage.

        :param stage_name: The stage name.
        :param route_key: The route key.
        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteStage")
    def delete_stage(self, context: RequestContext, stage_name: _string, api_id: _string) -> None:
        """Deletes a Stage.

        :param stage_name: The stage name.
        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteVpcLink")
    def delete_vpc_link(
        self, context: RequestContext, vpc_link_id: _string
    ) -> DeleteVpcLinkResponse:
        """Deletes a VPC link.

        :param vpc_link_id: The ID of the VPC link.
        :returns: DeleteVpcLinkResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ExportApi")
    def export_api(
        self,
        context: RequestContext,
        specification: _string,
        output_type: _string,
        api_id: _string,
        export_version: _string = None,
        include_extensions: _boolean = None,
        stage_name: _string = None,
    ) -> ExportApiResponse:
        """

        :param specification: The version of the API specification to use.
        :param output_type: The output type of the exported definition file.
        :param api_id: The API identifier.
        :param export_version: The version of the API Gateway export algorithm.
        :param include_extensions: Specifies whether to include `API Gateway
        extensions <https://docs.
        :param stage_name: The name of the API stage to export.
        :returns: ExportApiResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ResetAuthorizersCache")
    def reset_authorizers_cache(
        self, context: RequestContext, stage_name: _string, api_id: _string
    ) -> None:
        """Resets all authorizer cache entries on a stage. Supported only for HTTP
        APIs.

        :param stage_name: The stage name.
        :param api_id: The API identifier.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetApi")
    def get_api(self, context: RequestContext, api_id: _string) -> GetApiResponse:
        """Gets an Api resource.

        :param api_id: The API identifier.
        :returns: GetApiResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetApiMapping")
    def get_api_mapping(
        self, context: RequestContext, api_mapping_id: _string, domain_name: _string
    ) -> GetApiMappingResponse:
        """Gets an API mapping.

        :param api_mapping_id: The API mapping identifier.
        :param domain_name: The domain name.
        :returns: GetApiMappingResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetApiMappings")
    def get_api_mappings(
        self,
        context: RequestContext,
        domain_name: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetApiMappingsResponse:
        """Gets API mappings.

        :param domain_name: The domain name.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetApiMappingsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetApis")
    def get_apis(
        self, context: RequestContext, max_results: _string = None, next_token: _string = None
    ) -> GetApisResponse:
        """Gets a collection of Api resources.

        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetApisResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetAuthorizer")
    def get_authorizer(
        self, context: RequestContext, authorizer_id: _string, api_id: _string
    ) -> GetAuthorizerResponse:
        """Gets an Authorizer.

        :param authorizer_id: The authorizer identifier.
        :param api_id: The API identifier.
        :returns: GetAuthorizerResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetAuthorizers")
    def get_authorizers(
        self,
        context: RequestContext,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetAuthorizersResponse:
        """Gets the Authorizers for an API.

        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetAuthorizersResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDeployment")
    def get_deployment(
        self, context: RequestContext, api_id: _string, deployment_id: _string
    ) -> GetDeploymentResponse:
        """Gets a Deployment.

        :param api_id: The API identifier.
        :param deployment_id: The deployment ID.
        :returns: GetDeploymentResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetDeployments")
    def get_deployments(
        self,
        context: RequestContext,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetDeploymentsResponse:
        """Gets the Deployments for an API.

        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetDeploymentsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDomainName")
    def get_domain_name(
        self, context: RequestContext, domain_name: _string
    ) -> GetDomainNameResponse:
        """Gets a domain name.

        :param domain_name: The domain name.
        :returns: GetDomainNameResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetDomainNames")
    def get_domain_names(
        self, context: RequestContext, max_results: _string = None, next_token: _string = None
    ) -> GetDomainNamesResponse:
        """Gets the domain names for an AWS account.

        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetDomainNamesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetIntegration")
    def get_integration(
        self, context: RequestContext, api_id: _string, integration_id: _string
    ) -> GetIntegrationResult:
        """Gets an Integration.

        :param api_id: The API identifier.
        :param integration_id: The integration ID.
        :returns: GetIntegrationResult
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetIntegrationResponse")
    def get_integration_response(
        self,
        context: RequestContext,
        api_id: _string,
        integration_response_id: _string,
        integration_id: _string,
    ) -> GetIntegrationResponseResponse:
        """Gets an IntegrationResponses.

        :param api_id: The API identifier.
        :param integration_response_id: The integration response ID.
        :param integration_id: The integration ID.
        :returns: GetIntegrationResponseResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetIntegrationResponses")
    def get_integration_responses(
        self,
        context: RequestContext,
        integration_id: _string,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetIntegrationResponsesResponse:
        """Gets the IntegrationResponses for an Integration.

        :param integration_id: The integration ID.
        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetIntegrationResponsesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetIntegrations")
    def get_integrations(
        self,
        context: RequestContext,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetIntegrationsResponse:
        """Gets the Integrations for an API.

        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetIntegrationsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetModel")
    def get_model(
        self, context: RequestContext, model_id: _string, api_id: _string
    ) -> GetModelResponse:
        """Gets a Model.

        :param model_id: The model ID.
        :param api_id: The API identifier.
        :returns: GetModelResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetModelTemplate")
    def get_model_template(
        self, context: RequestContext, model_id: _string, api_id: _string
    ) -> GetModelTemplateResponse:
        """Gets a model template.

        :param model_id: The model ID.
        :param api_id: The API identifier.
        :returns: GetModelTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetModels")
    def get_models(
        self,
        context: RequestContext,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetModelsResponse:
        """Gets the Models for an API.

        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetModelsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetRoute")
    def get_route(
        self, context: RequestContext, api_id: _string, route_id: _string
    ) -> GetRouteResult:
        """Gets a Route.

        :param api_id: The API identifier.
        :param route_id: The route ID.
        :returns: GetRouteResult
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetRouteResponse")
    def get_route_response(
        self,
        context: RequestContext,
        route_response_id: _string,
        api_id: _string,
        route_id: _string,
    ) -> GetRouteResponseResponse:
        """Gets a RouteResponse.

        :param route_response_id: The route response ID.
        :param api_id: The API identifier.
        :param route_id: The route ID.
        :returns: GetRouteResponseResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetRouteResponses")
    def get_route_responses(
        self,
        context: RequestContext,
        route_id: _string,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetRouteResponsesResponse:
        """Gets the RouteResponses for a Route.

        :param route_id: The route ID.
        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetRouteResponsesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetRoutes")
    def get_routes(
        self,
        context: RequestContext,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetRoutesResponse:
        """Gets the Routes for an API.

        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetRoutesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetStage")
    def get_stage(
        self, context: RequestContext, stage_name: _string, api_id: _string
    ) -> GetStageResponse:
        """Gets a Stage.

        :param stage_name: The stage name.
        :param api_id: The API identifier.
        :returns: GetStageResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetStages")
    def get_stages(
        self,
        context: RequestContext,
        api_id: _string,
        max_results: _string = None,
        next_token: _string = None,
    ) -> GetStagesResponse:
        """Gets the Stages for an API.

        :param api_id: The API identifier.
        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetStagesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetTags")
    def get_tags(self, context: RequestContext, resource_arn: _string) -> GetTagsResponse:
        """Gets a collection of Tag resources.

        :param resource_arn: The resource ARN for the tag.
        :returns: GetTagsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("GetVpcLink")
    def get_vpc_link(self, context: RequestContext, vpc_link_id: _string) -> GetVpcLinkResponse:
        """Gets a VPC link.

        :param vpc_link_id: The ID of the VPC link.
        :returns: GetVpcLinkResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetVpcLinks")
    def get_vpc_links(
        self, context: RequestContext, max_results: _string = None, next_token: _string = None
    ) -> GetVpcLinksResponse:
        """Gets a collection of VPC links.

        :param max_results: The maximum number of elements to be returned for this resource.
        :param next_token: The next page of elements from this collection.
        :returns: GetVpcLinksResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ImportApi")
    def import_api(
        self,
        context: RequestContext,
        body: _string,
        basepath: _string = None,
        fail_on_warnings: _boolean = None,
    ) -> ImportApiResponse:
        """Imports an API.

        :param body: The OpenAPI definition.
        :param basepath: Specifies how to interpret the base path of the API during import.
        :param fail_on_warnings: Specifies whether to rollback the API creation when a warning is
        encountered.
        :returns: ImportApiResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("ReimportApi")
    def reimport_api(
        self,
        context: RequestContext,
        api_id: _string,
        body: _string,
        basepath: _string = None,
        fail_on_warnings: _boolean = None,
    ) -> ReimportApiResponse:
        """Puts an Api resource.

        :param api_id: The API identifier.
        :param body: The OpenAPI definition.
        :param basepath: Specifies how to interpret the base path of the API during import.
        :param fail_on_warnings: Specifies whether to rollback the API creation when a warning is
        encountered.
        :returns: ReimportApiResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: _string, tags: Tags = None
    ) -> TagResourceResponse:
        """Creates a new Tag resource to represent a tag.

        :param resource_arn: The resource ARN for the tag.
        :param tags: The collection of tags.
        :returns: TagResourceResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: _string, tag_keys: _listOf__string
    ) -> None:
        """Deletes a Tag.

        :param resource_arn: The resource ARN for the tag.
        :param tag_keys: The Tag keys to delete.
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateApi")
    def update_api(
        self,
        context: RequestContext,
        api_id: _string,
        api_key_selection_expression: SelectionExpression = None,
        cors_configuration: Cors = None,
        credentials_arn: Arn = None,
        description: StringWithLengthBetween0And1024 = None,
        disable_schema_validation: _boolean = None,
        disable_execute_api_endpoint: _boolean = None,
        name: StringWithLengthBetween1And128 = None,
        route_key: SelectionKey = None,
        route_selection_expression: SelectionExpression = None,
        target: UriWithLengthBetween1And2048 = None,
        version: StringWithLengthBetween1And64 = None,
    ) -> UpdateApiResponse:
        """Updates an Api resource.

        :param api_id: The API identifier.
        :param api_key_selection_expression: An API key selection expression.
        :param cors_configuration: A CORS configuration.
        :param credentials_arn: This property is part of quick create.
        :param description: The description of the API.
        :param disable_schema_validation: Avoid validating models when creating a deployment.
        :param disable_execute_api_endpoint: Specifies whether clients can invoke your API by using the default
        execute-api endpoint.
        :param name: The name of the API.
        :param route_key: This property is part of quick create.
        :param route_selection_expression: The route selection expression for the API.
        :param target: This property is part of quick create.
        :param version: A version identifier for the API.
        :returns: UpdateApiResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateApiMapping")
    def update_api_mapping(
        self,
        context: RequestContext,
        api_mapping_id: _string,
        api_id: Id,
        domain_name: _string,
        api_mapping_key: SelectionKey = None,
        stage: StringWithLengthBetween1And128 = None,
    ) -> UpdateApiMappingResponse:
        """The API mapping.

        :param api_mapping_id: The API mapping identifier.
        :param api_id: The API identifier.
        :param domain_name: The domain name.
        :param api_mapping_key: The API mapping key.
        :param stage: The API stage.
        :returns: UpdateApiMappingResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateAuthorizer")
    def update_authorizer(
        self,
        context: RequestContext,
        authorizer_id: _string,
        api_id: _string,
        authorizer_credentials_arn: Arn = None,
        authorizer_payload_format_version: StringWithLengthBetween1And64 = None,
        authorizer_result_ttl_in_seconds: IntegerWithLengthBetween0And3600 = None,
        authorizer_type: AuthorizerType = None,
        authorizer_uri: UriWithLengthBetween1And2048 = None,
        enable_simple_responses: _boolean = None,
        identity_source: IdentitySourceList = None,
        identity_validation_expression: StringWithLengthBetween0And1024 = None,
        jwt_configuration: JWTConfiguration = None,
        name: StringWithLengthBetween1And128 = None,
    ) -> UpdateAuthorizerResponse:
        """Updates an Authorizer.

        :param authorizer_id: The authorizer identifier.
        :param api_id: The API identifier.
        :param authorizer_credentials_arn: Specifies the required credentials as an IAM role for API Gateway to
        invoke the authorizer.
        :param authorizer_payload_format_version: Specifies the format of the payload sent to an HTTP API Lambda
        authorizer.
        :param authorizer_result_ttl_in_seconds: The time to live (TTL) for cached authorizer results, in seconds.
        :param authorizer_type: The authorizer type.
        :param authorizer_uri: The authorizer's Uniform Resource Identifier (URI).
        :param enable_simple_responses: Specifies whether a Lambda authorizer returns a response in a simple
        format.
        :param identity_source: The identity source for which authorization is requested.
        :param identity_validation_expression: This parameter is not used.
        :param jwt_configuration: Represents the configuration of a JWT authorizer.
        :param name: The name of the authorizer.
        :returns: UpdateAuthorizerResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateDeployment")
    def update_deployment(
        self,
        context: RequestContext,
        api_id: _string,
        deployment_id: _string,
        description: StringWithLengthBetween0And1024 = None,
    ) -> UpdateDeploymentResponse:
        """Updates a Deployment.

        :param api_id: The API identifier.
        :param deployment_id: The deployment ID.
        :param description: The description for the deployment resource.
        :returns: UpdateDeploymentResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateDomainName")
    def update_domain_name(
        self,
        context: RequestContext,
        domain_name: _string,
        domain_name_configurations: DomainNameConfigurations = None,
        mutual_tls_authentication: MutualTlsAuthenticationInput = None,
    ) -> UpdateDomainNameResponse:
        """Updates a domain name.

        :param domain_name: The domain name.
        :param domain_name_configurations: The domain name configurations.
        :param mutual_tls_authentication: The mutual TLS authentication configuration for a custom domain name.
        :returns: UpdateDomainNameResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateIntegration")
    def update_integration(
        self,
        context: RequestContext,
        api_id: _string,
        integration_id: _string,
        connection_id: StringWithLengthBetween1And1024 = None,
        connection_type: ConnectionType = None,
        content_handling_strategy: ContentHandlingStrategy = None,
        credentials_arn: Arn = None,
        description: StringWithLengthBetween0And1024 = None,
        integration_method: StringWithLengthBetween1And64 = None,
        integration_subtype: StringWithLengthBetween1And128 = None,
        integration_type: IntegrationType = None,
        integration_uri: UriWithLengthBetween1And2048 = None,
        passthrough_behavior: PassthroughBehavior = None,
        payload_format_version: StringWithLengthBetween1And64 = None,
        request_parameters: IntegrationParameters = None,
        request_templates: TemplateMap = None,
        response_parameters: ResponseParameters = None,
        template_selection_expression: SelectionExpression = None,
        timeout_in_millis: IntegerWithLengthBetween50And30000 = None,
        tls_config: TlsConfigInput = None,
    ) -> UpdateIntegrationResult:
        """Updates an Integration.

        :param api_id: The API identifier.
        :param integration_id: The integration ID.
        :param connection_id: The ID of the VPC link for a private integration.
        :param connection_type: The type of the network connection to the integration endpoint.
        :param content_handling_strategy: Supported only for WebSocket APIs.
        :param credentials_arn: Specifies the credentials required for the integration, if any.
        :param description: The description of the integration.
        :param integration_method: Specifies the integration's HTTP method type.
        :param integration_subtype: Supported only for HTTP API AWS_PROXY integrations.
        :param integration_type: The integration type of an integration.
        :param integration_uri: For a Lambda integration, specify the URI of a Lambda function.
        :param passthrough_behavior: Specifies the pass-through behavior for incoming requests based on the
        Content-Type header in the request, and the available mapping templates
        specified as the requestTemplates property on the Integration resource.
        :param payload_format_version: Specifies the format of the payload sent to an integration.
        :param request_parameters: For WebSocket APIs, a key-value map specifying request parameters that
        are passed from the method request to the backend.
        :param request_templates: Represents a map of Velocity templates that are applied on the request
        payload based on the value of the Content-Type header sent by the
        client.
        :param response_parameters: Supported only for HTTP APIs.
        :param template_selection_expression: The template selection expression for the integration.
        :param timeout_in_millis: Custom timeout between 50 and 29,000 milliseconds for WebSocket APIs and
        between 50 and 30,000 milliseconds for HTTP APIs.
        :param tls_config: The TLS configuration for a private integration.
        :returns: UpdateIntegrationResult
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateIntegrationResponse")
    def update_integration_response(
        self,
        context: RequestContext,
        api_id: _string,
        integration_response_id: _string,
        integration_id: _string,
        content_handling_strategy: ContentHandlingStrategy = None,
        integration_response_key: SelectionKey = None,
        response_parameters: IntegrationParameters = None,
        response_templates: TemplateMap = None,
        template_selection_expression: SelectionExpression = None,
    ) -> UpdateIntegrationResponseResponse:
        """Updates an IntegrationResponses.

        :param api_id: The API identifier.
        :param integration_response_id: The integration response ID.
        :param integration_id: The integration ID.
        :param content_handling_strategy: Supported only for WebSocket APIs.
        :param integration_response_key: The integration response key.
        :param response_parameters: A key-value map specifying response parameters that are passed to the
        method response from the backend.
        :param response_templates: The collection of response templates for the integration response as a
        string-to-string map of key-value pairs.
        :param template_selection_expression: The template selection expression for the integration response.
        :returns: UpdateIntegrationResponseResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateModel")
    def update_model(
        self,
        context: RequestContext,
        model_id: _string,
        api_id: _string,
        content_type: StringWithLengthBetween1And256 = None,
        description: StringWithLengthBetween0And1024 = None,
        name: StringWithLengthBetween1And128 = None,
        schema: StringWithLengthBetween0And32K = None,
    ) -> UpdateModelResponse:
        """Updates a Model.

        :param model_id: The model ID.
        :param api_id: The API identifier.
        :param content_type: The content-type for the model, for example, "application/json".
        :param description: The description of the model.
        :param name: The name of the model.
        :param schema: The schema for the model.
        :returns: UpdateModelResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateRoute")
    def update_route(
        self,
        context: RequestContext,
        api_id: _string,
        route_id: _string,
        api_key_required: _boolean = None,
        authorization_scopes: AuthorizationScopes = None,
        authorization_type: AuthorizationType = None,
        authorizer_id: Id = None,
        model_selection_expression: SelectionExpression = None,
        operation_name: StringWithLengthBetween1And64 = None,
        request_models: RouteModels = None,
        request_parameters: RouteParameters = None,
        route_key: SelectionKey = None,
        route_response_selection_expression: SelectionExpression = None,
        target: StringWithLengthBetween1And128 = None,
    ) -> UpdateRouteResult:
        """Updates a Route.

        :param api_id: The API identifier.
        :param route_id: The route ID.
        :param api_key_required: Specifies whether an API key is required for the route.
        :param authorization_scopes: The authorization scopes supported by this route.
        :param authorization_type: The authorization type for the route.
        :param authorizer_id: The identifier of the Authorizer resource to be associated with this
        route.
        :param model_selection_expression: The model selection expression for the route.
        :param operation_name: The operation name for the route.
        :param request_models: The request models for the route.
        :param request_parameters: The request parameters for the route.
        :param route_key: The route key for the route.
        :param route_response_selection_expression: The route response selection expression for the route.
        :param target: The target for the route.
        :returns: UpdateRouteResult
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateRouteResponse")
    def update_route_response(
        self,
        context: RequestContext,
        route_response_id: _string,
        api_id: _string,
        route_id: _string,
        model_selection_expression: SelectionExpression = None,
        response_models: RouteModels = None,
        response_parameters: RouteParameters = None,
        route_response_key: SelectionKey = None,
    ) -> UpdateRouteResponseResponse:
        """Updates a RouteResponse.

        :param route_response_id: The route response ID.
        :param api_id: The API identifier.
        :param route_id: The route ID.
        :param model_selection_expression: The model selection expression for the route response.
        :param response_models: The response models for the route response.
        :param response_parameters: The route response parameters.
        :param route_response_key: The route response key.
        :returns: UpdateRouteResponseResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateStage")
    def update_stage(
        self,
        context: RequestContext,
        stage_name: _string,
        api_id: _string,
        access_log_settings: AccessLogSettings = None,
        auto_deploy: _boolean = None,
        client_certificate_id: Id = None,
        default_route_settings: RouteSettings = None,
        deployment_id: Id = None,
        description: StringWithLengthBetween0And1024 = None,
        route_settings: RouteSettingsMap = None,
        stage_variables: StageVariablesMap = None,
    ) -> UpdateStageResponse:
        """Updates a Stage.

        :param stage_name: The stage name.
        :param api_id: The API identifier.
        :param access_log_settings: Settings for logging access in this stage.
        :param auto_deploy: Specifies whether updates to an API automatically trigger a new
        deployment.
        :param client_certificate_id: The identifier of a client certificate for a Stage.
        :param default_route_settings: The default route settings for the stage.
        :param deployment_id: The deployment identifier for the API stage.
        :param description: The description for the API stage.
        :param route_settings: Route settings for the stage.
        :param stage_variables: A map that defines the stage variables for a Stage.
        :returns: UpdateStageResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("UpdateVpcLink")
    def update_vpc_link(
        self,
        context: RequestContext,
        vpc_link_id: _string,
        name: StringWithLengthBetween1And128 = None,
    ) -> UpdateVpcLinkResponse:
        """Updates a VPC link.

        :param vpc_link_id: The ID of the VPC link.
        :param name: The name of the VPC link.
        :returns: UpdateVpcLinkResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError
