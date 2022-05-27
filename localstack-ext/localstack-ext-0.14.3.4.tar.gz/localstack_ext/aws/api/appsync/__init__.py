import sys
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Boolean = bool
BooleanValue = bool
CertificateArn = str
Description = str
DomainName = str
ErrorMessage = str
MappingTemplate = str
MaxBatchSize = int
MaxResults = int
PaginationToken = str
ResourceArn = str
ResourceName = str
String = str
TTL = int
TagKey = str
TagValue = str


class ApiCacheStatus(str):
    AVAILABLE = "AVAILABLE"
    CREATING = "CREATING"
    DELETING = "DELETING"
    MODIFYING = "MODIFYING"
    FAILED = "FAILED"


class ApiCacheType(str):
    T2_SMALL = "T2_SMALL"
    T2_MEDIUM = "T2_MEDIUM"
    R4_LARGE = "R4_LARGE"
    R4_XLARGE = "R4_XLARGE"
    R4_2XLARGE = "R4_2XLARGE"
    R4_4XLARGE = "R4_4XLARGE"
    R4_8XLARGE = "R4_8XLARGE"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    XLARGE = "XLARGE"
    LARGE_2X = "LARGE_2X"
    LARGE_4X = "LARGE_4X"
    LARGE_8X = "LARGE_8X"
    LARGE_12X = "LARGE_12X"


class ApiCachingBehavior(str):
    FULL_REQUEST_CACHING = "FULL_REQUEST_CACHING"
    PER_RESOLVER_CACHING = "PER_RESOLVER_CACHING"


class AssociationStatus(str):
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"


class AuthenticationType(str):
    API_KEY = "API_KEY"
    AWS_IAM = "AWS_IAM"
    AMAZON_COGNITO_USER_POOLS = "AMAZON_COGNITO_USER_POOLS"
    OPENID_CONNECT = "OPENID_CONNECT"
    AWS_LAMBDA = "AWS_LAMBDA"


class AuthorizationType(str):
    AWS_IAM = "AWS_IAM"


class ConflictDetectionType(str):
    VERSION = "VERSION"
    NONE = "NONE"


class ConflictHandlerType(str):
    OPTIMISTIC_CONCURRENCY = "OPTIMISTIC_CONCURRENCY"
    LAMBDA = "LAMBDA"
    AUTOMERGE = "AUTOMERGE"
    NONE = "NONE"


class DataSourceType(str):
    AWS_LAMBDA = "AWS_LAMBDA"
    AMAZON_DYNAMODB = "AMAZON_DYNAMODB"
    AMAZON_ELASTICSEARCH = "AMAZON_ELASTICSEARCH"
    NONE = "NONE"
    HTTP = "HTTP"
    RELATIONAL_DATABASE = "RELATIONAL_DATABASE"
    AMAZON_OPENSEARCH_SERVICE = "AMAZON_OPENSEARCH_SERVICE"


class DefaultAction(str):
    ALLOW = "ALLOW"
    DENY = "DENY"


class FieldLogLevel(str):
    NONE = "NONE"
    ERROR = "ERROR"
    ALL = "ALL"


class OutputType(str):
    SDL = "SDL"
    JSON = "JSON"


class RelationalDatabaseSourceType(str):
    RDS_HTTP_ENDPOINT = "RDS_HTTP_ENDPOINT"


class ResolverKind(str):
    UNIT = "UNIT"
    PIPELINE = "PIPELINE"


class SchemaStatus(str):
    PROCESSING = "PROCESSING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class TypeDefinitionFormat(str):
    SDL = "SDL"
    JSON = "JSON"


class AccessDeniedException(ServiceException):
    """You don't have access to perform this operation on this resource."""

    message: Optional[String]


class ApiKeyLimitExceededException(ServiceException):
    """The API key exceeded a limit. Try your request again."""

    message: Optional[String]


class ApiKeyValidityOutOfBoundsException(ServiceException):
    """The API key expiration must be set to a value between 1 and 365 days
    from creation (for ``CreateApiKey``) or from update (for
    ``UpdateApiKey``).
    """

    message: Optional[String]


class ApiLimitExceededException(ServiceException):
    """The GraphQL API exceeded a limit. Try your request again."""

    message: Optional[String]


class BadRequestException(ServiceException):
    """The request is not well formed. For example, a value is invalid or a
    required field is missing. Check the field values, and then try again.
    """

    message: Optional[ErrorMessage]


class ConcurrentModificationException(ServiceException):
    """Another modification is in progress at this time and it must complete
    before you can make your change.
    """

    message: Optional[ErrorMessage]


class GraphQLSchemaException(ServiceException):
    """The GraphQL schema is not valid."""

    message: Optional[ErrorMessage]


class InternalFailureException(ServiceException):
    """An internal AppSync error occurred. Try your request again."""

    message: Optional[String]


class LimitExceededException(ServiceException):
    """The request exceeded a limit. Try your request again."""

    message: Optional[String]


class NotFoundException(ServiceException):
    """The resource specified in the request was not found. Check the resource,
    and then try again.
    """

    message: Optional[String]


class UnauthorizedException(ServiceException):
    """You aren't authorized to perform this operation."""

    message: Optional[String]


class LambdaAuthorizerConfig(TypedDict, total=False):
    """A ``LambdaAuthorizerConfig`` specifies how to authorize AppSync API
    access when using the ``AWS_LAMBDA`` authorizer mode. Be aware that an
    AppSync API can have only one Lambda authorizer configured at a time.
    """

    authorizerResultTtlInSeconds: Optional[TTL]
    authorizerUri: String
    identityValidationExpression: Optional[String]


class CognitoUserPoolConfig(TypedDict, total=False):
    """Describes an Amazon Cognito user pool configuration."""

    userPoolId: String
    awsRegion: String
    appIdClientRegex: Optional[String]


Long = int


class OpenIDConnectConfig(TypedDict, total=False):
    """Describes an OpenID Connect (OIDC) configuration."""

    issuer: String
    clientId: Optional[String]
    iatTTL: Optional[Long]
    authTTL: Optional[Long]


class AdditionalAuthenticationProvider(TypedDict, total=False):
    """Describes an additional authentication provider."""

    authenticationType: Optional[AuthenticationType]
    openIDConnectConfig: Optional[OpenIDConnectConfig]
    userPoolConfig: Optional[CognitoUserPoolConfig]
    lambdaAuthorizerConfig: Optional[LambdaAuthorizerConfig]


AdditionalAuthenticationProviders = List[AdditionalAuthenticationProvider]


class ApiAssociation(TypedDict, total=False):
    """Describes an ``ApiAssociation`` object."""

    domainName: Optional[DomainName]
    apiId: Optional[String]
    associationStatus: Optional[AssociationStatus]
    deploymentDetail: Optional[String]


ApiCache = TypedDict(
    "ApiCache",
    {
        "ttl": Optional[Long],
        "apiCachingBehavior": Optional[ApiCachingBehavior],
        "transitEncryptionEnabled": Optional[Boolean],
        "atRestEncryptionEnabled": Optional[Boolean],
        "type": Optional[ApiCacheType],
        "status": Optional[ApiCacheStatus],
    },
    total=False,
)


class ApiKey(TypedDict, total=False):
    """Describes an API key.

    Customers invoke AppSync GraphQL API operations with API keys as an
    identity mechanism. There are two key versions:

    **da1**: We introduced this version at launch in November 2017. These
    keys always expire after 7 days. Amazon DynamoDB TTL manages key
    expiration. These keys ceased to be valid after February 21, 2018, and
    they should no longer be used.

    -  ``ListApiKeys`` returns the expiration time in milliseconds.

    -  ``CreateApiKey`` returns the expiration time in milliseconds.

    -  ``UpdateApiKey`` is not available for this key version.

    -  ``DeleteApiKey`` deletes the item from the table.

    -  Expiration is stored in DynamoDB as milliseconds. This results in a
       bug where keys are not automatically deleted because DynamoDB expects
       the TTL to be stored in seconds. As a one-time action, we deleted
       these keys from the table on February 21, 2018.

    **da2**: We introduced this version in February 2018 when AppSync added
    support to extend key expiration.

    -  ``ListApiKeys`` returns the expiration time and deletion time in
       seconds.

    -  ``CreateApiKey`` returns the expiration time and deletion time in
       seconds and accepts a user-provided expiration time in seconds.

    -  ``UpdateApiKey`` returns the expiration time and and deletion time in
       seconds and accepts a user-provided expiration time in seconds.
       Expired API keys are kept for 60 days after the expiration time. You
       can update the key expiration time as long as the key isn't deleted.

    -  ``DeleteApiKey`` deletes the item from the table.

    -  Expiration is stored in DynamoDB as seconds. After the expiration
       time, using the key to authenticate will fail. However, you can
       reinstate the key before deletion.

    -  Deletion is stored in DynamoDB as seconds. The key is deleted after
       deletion time.
    """

    id: Optional[String]
    description: Optional[String]
    expires: Optional[Long]
    deletes: Optional[Long]


ApiKeys = List[ApiKey]


class AssociateApiRequest(ServiceRequest):
    domainName: DomainName
    apiId: String


class AssociateApiResponse(TypedDict, total=False):
    apiAssociation: Optional[ApiAssociation]


class AwsIamConfig(TypedDict, total=False):
    """The Identity and Access Management (IAM) configuration."""

    signingRegion: Optional[String]
    signingServiceName: Optional[String]


class AuthorizationConfig(TypedDict, total=False):
    """The authorization configuration in case the HTTP endpoint requires
    authorization.
    """

    authorizationType: AuthorizationType
    awsIamConfig: Optional[AwsIamConfig]


Blob = bytes
CachingKeys = List[String]


class CachingConfig(TypedDict, total=False):
    """The caching configuration for a resolver that has caching activated."""

    ttl: Optional[Long]
    cachingKeys: Optional[CachingKeys]


CreateApiCacheRequest = TypedDict(
    "CreateApiCacheRequest",
    {
        "apiId": String,
        "ttl": Long,
        "transitEncryptionEnabled": Optional[Boolean],
        "atRestEncryptionEnabled": Optional[Boolean],
        "apiCachingBehavior": ApiCachingBehavior,
        "type": ApiCacheType,
    },
    total=False,
)


class CreateApiCacheResponse(TypedDict, total=False):
    """Represents the output of a ``CreateApiCache`` operation."""

    apiCache: Optional[ApiCache]


class CreateApiKeyRequest(ServiceRequest):
    apiId: String
    description: Optional[String]
    expires: Optional[Long]


class CreateApiKeyResponse(TypedDict, total=False):
    apiKey: Optional[ApiKey]


class RdsHttpEndpointConfig(TypedDict, total=False):
    """The Amazon Relational Database Service (Amazon RDS) HTTP endpoint
    configuration.
    """

    awsRegion: Optional[String]
    dbClusterIdentifier: Optional[String]
    databaseName: Optional[String]
    schema: Optional[String]
    awsSecretStoreArn: Optional[String]


class RelationalDatabaseDataSourceConfig(TypedDict, total=False):
    """Describes a relational database data source configuration."""

    relationalDatabaseSourceType: Optional[RelationalDatabaseSourceType]
    rdsHttpEndpointConfig: Optional[RdsHttpEndpointConfig]


class HttpDataSourceConfig(TypedDict, total=False):
    """Describes an HTTP data source configuration."""

    endpoint: Optional[String]
    authorizationConfig: Optional[AuthorizationConfig]


class OpenSearchServiceDataSourceConfig(TypedDict, total=False):
    """Describes an OpenSearch data source configuration."""

    endpoint: String
    awsRegion: String


class ElasticsearchDataSourceConfig(TypedDict, total=False):
    """Describes an OpenSearch data source configuration.

    As of September 2021, Amazon Elasticsearch service is Amazon OpenSearch
    Service. This configuration is deprecated. For new data sources, use
    OpenSearchServiceDataSourceConfig to specify an OpenSearch data source.
    """

    endpoint: String
    awsRegion: String


class LambdaDataSourceConfig(TypedDict, total=False):
    """Describes an Lambda data source configuration."""

    lambdaFunctionArn: String


class DeltaSyncConfig(TypedDict, total=False):
    """Describes a Delta Sync configuration."""

    baseTableTTL: Optional[Long]
    deltaSyncTableName: Optional[String]
    deltaSyncTableTTL: Optional[Long]


class DynamodbDataSourceConfig(TypedDict, total=False):
    """Describes an Amazon DynamoDB data source configuration."""

    tableName: String
    awsRegion: String
    useCallerCredentials: Optional[Boolean]
    deltaSyncConfig: Optional[DeltaSyncConfig]
    versioned: Optional[Boolean]


CreateDataSourceRequest = TypedDict(
    "CreateDataSourceRequest",
    {
        "apiId": String,
        "name": ResourceName,
        "description": Optional[String],
        "type": DataSourceType,
        "serviceRoleArn": Optional[String],
        "dynamodbConfig": Optional[DynamodbDataSourceConfig],
        "lambdaConfig": Optional[LambdaDataSourceConfig],
        "elasticsearchConfig": Optional[ElasticsearchDataSourceConfig],
        "openSearchServiceConfig": Optional[OpenSearchServiceDataSourceConfig],
        "httpConfig": Optional[HttpDataSourceConfig],
        "relationalDatabaseConfig": Optional[RelationalDatabaseDataSourceConfig],
    },
    total=False,
)
DataSource = TypedDict(
    "DataSource",
    {
        "dataSourceArn": Optional[String],
        "name": Optional[ResourceName],
        "description": Optional[String],
        "type": Optional[DataSourceType],
        "serviceRoleArn": Optional[String],
        "dynamodbConfig": Optional[DynamodbDataSourceConfig],
        "lambdaConfig": Optional[LambdaDataSourceConfig],
        "elasticsearchConfig": Optional[ElasticsearchDataSourceConfig],
        "openSearchServiceConfig": Optional[OpenSearchServiceDataSourceConfig],
        "httpConfig": Optional[HttpDataSourceConfig],
        "relationalDatabaseConfig": Optional[RelationalDatabaseDataSourceConfig],
    },
    total=False,
)


class CreateDataSourceResponse(TypedDict, total=False):
    dataSource: Optional[DataSource]


class CreateDomainNameRequest(ServiceRequest):
    domainName: DomainName
    certificateArn: CertificateArn
    description: Optional[Description]


class DomainNameConfig(TypedDict, total=False):
    """Describes a configuration for a custom domain."""

    domainName: Optional[DomainName]
    description: Optional[Description]
    certificateArn: Optional[CertificateArn]
    appsyncDomainName: Optional[String]
    hostedZoneId: Optional[String]


class CreateDomainNameResponse(TypedDict, total=False):
    domainNameConfig: Optional[DomainNameConfig]


class LambdaConflictHandlerConfig(TypedDict, total=False):
    """The ``LambdaConflictHandlerConfig`` object when configuring ``LAMBDA``
    as the Conflict Handler.
    """

    lambdaConflictHandlerArn: Optional[String]


class SyncConfig(TypedDict, total=False):
    """Describes a Sync configuration for a resolver.

    Specifies which Conflict Detection strategy and Resolution strategy to
    use when the resolver is invoked.
    """

    conflictHandler: Optional[ConflictHandlerType]
    conflictDetection: Optional[ConflictDetectionType]
    lambdaConflictHandlerConfig: Optional[LambdaConflictHandlerConfig]


class CreateFunctionRequest(ServiceRequest):
    apiId: String
    name: ResourceName
    description: Optional[String]
    dataSourceName: ResourceName
    requestMappingTemplate: Optional[MappingTemplate]
    responseMappingTemplate: Optional[MappingTemplate]
    functionVersion: String
    syncConfig: Optional[SyncConfig]
    maxBatchSize: Optional[MaxBatchSize]


class FunctionConfiguration(TypedDict, total=False):
    """A function is a reusable entity. You can use multiple functions to
    compose the resolver logic.
    """

    functionId: Optional[String]
    functionArn: Optional[String]
    name: Optional[ResourceName]
    description: Optional[String]
    dataSourceName: Optional[ResourceName]
    requestMappingTemplate: Optional[MappingTemplate]
    responseMappingTemplate: Optional[MappingTemplate]
    functionVersion: Optional[String]
    syncConfig: Optional[SyncConfig]
    maxBatchSize: Optional[MaxBatchSize]


class CreateFunctionResponse(TypedDict, total=False):
    functionConfiguration: Optional[FunctionConfiguration]


TagMap = Dict[TagKey, TagValue]


class UserPoolConfig(TypedDict, total=False):
    """Describes an Amazon Cognito user pool configuration."""

    userPoolId: String
    awsRegion: String
    defaultAction: DefaultAction
    appIdClientRegex: Optional[String]


class LogConfig(TypedDict, total=False):
    """The Amazon CloudWatch Logs configuration."""

    fieldLogLevel: FieldLogLevel
    cloudWatchLogsRoleArn: String
    excludeVerboseContent: Optional[Boolean]


class CreateGraphqlApiRequest(ServiceRequest):
    name: String
    logConfig: Optional[LogConfig]
    authenticationType: AuthenticationType
    userPoolConfig: Optional[UserPoolConfig]
    openIDConnectConfig: Optional[OpenIDConnectConfig]
    tags: Optional[TagMap]
    additionalAuthenticationProviders: Optional[AdditionalAuthenticationProviders]
    xrayEnabled: Optional[Boolean]
    lambdaAuthorizerConfig: Optional[LambdaAuthorizerConfig]


MapOfStringToString = Dict[String, String]


class GraphqlApi(TypedDict, total=False):
    """Describes a GraphQL API."""

    name: Optional[ResourceName]
    apiId: Optional[String]
    authenticationType: Optional[AuthenticationType]
    logConfig: Optional[LogConfig]
    userPoolConfig: Optional[UserPoolConfig]
    openIDConnectConfig: Optional[OpenIDConnectConfig]
    arn: Optional[String]
    uris: Optional[MapOfStringToString]
    tags: Optional[TagMap]
    additionalAuthenticationProviders: Optional[AdditionalAuthenticationProviders]
    xrayEnabled: Optional[Boolean]
    wafWebAclArn: Optional[String]
    lambdaAuthorizerConfig: Optional[LambdaAuthorizerConfig]


class CreateGraphqlApiResponse(TypedDict, total=False):
    graphqlApi: Optional[GraphqlApi]


FunctionsIds = List[String]


class PipelineConfig(TypedDict, total=False):
    """The pipeline configuration for a resolver of kind ``PIPELINE``."""

    functions: Optional[FunctionsIds]


class CreateResolverRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName
    fieldName: ResourceName
    dataSourceName: Optional[ResourceName]
    requestMappingTemplate: Optional[MappingTemplate]
    responseMappingTemplate: Optional[MappingTemplate]
    kind: Optional[ResolverKind]
    pipelineConfig: Optional[PipelineConfig]
    syncConfig: Optional[SyncConfig]
    cachingConfig: Optional[CachingConfig]
    maxBatchSize: Optional[MaxBatchSize]


class Resolver(TypedDict, total=False):
    """Describes a resolver."""

    typeName: Optional[ResourceName]
    fieldName: Optional[ResourceName]
    dataSourceName: Optional[ResourceName]
    resolverArn: Optional[String]
    requestMappingTemplate: Optional[MappingTemplate]
    responseMappingTemplate: Optional[MappingTemplate]
    kind: Optional[ResolverKind]
    pipelineConfig: Optional[PipelineConfig]
    syncConfig: Optional[SyncConfig]
    cachingConfig: Optional[CachingConfig]
    maxBatchSize: Optional[MaxBatchSize]


class CreateResolverResponse(TypedDict, total=False):
    resolver: Optional[Resolver]


class CreateTypeRequest(ServiceRequest):
    apiId: String
    definition: String
    format: TypeDefinitionFormat


class Type(TypedDict, total=False):
    """Describes a type."""

    name: Optional[ResourceName]
    description: Optional[String]
    arn: Optional[String]
    definition: Optional[String]
    format: Optional[TypeDefinitionFormat]


CreateTypeResponse = TypedDict(
    "CreateTypeResponse",
    {
        "type": Optional[Type],
    },
    total=False,
)
DataSources = List[DataSource]


class DeleteApiCacheRequest(ServiceRequest):
    """Represents the input of a ``DeleteApiCache`` operation."""

    apiId: String


class DeleteApiCacheResponse(TypedDict, total=False):
    """Represents the output of a ``DeleteApiCache`` operation."""


class DeleteApiKeyRequest(ServiceRequest):
    apiId: String
    id: String


class DeleteApiKeyResponse(TypedDict, total=False):
    pass


class DeleteDataSourceRequest(ServiceRequest):
    apiId: String
    name: ResourceName


class DeleteDataSourceResponse(TypedDict, total=False):
    pass


class DeleteDomainNameRequest(ServiceRequest):
    domainName: DomainName


class DeleteDomainNameResponse(TypedDict, total=False):
    pass


class DeleteFunctionRequest(ServiceRequest):
    apiId: String
    functionId: ResourceName


class DeleteFunctionResponse(TypedDict, total=False):
    pass


class DeleteGraphqlApiRequest(ServiceRequest):
    apiId: String


class DeleteGraphqlApiResponse(TypedDict, total=False):
    pass


class DeleteResolverRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName
    fieldName: ResourceName


class DeleteResolverResponse(TypedDict, total=False):
    pass


class DeleteTypeRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName


class DeleteTypeResponse(TypedDict, total=False):
    pass


class DisassociateApiRequest(ServiceRequest):
    domainName: DomainName


class DisassociateApiResponse(TypedDict, total=False):
    pass


DomainNameConfigs = List[DomainNameConfig]


class FlushApiCacheRequest(ServiceRequest):
    """Represents the input of a ``FlushApiCache`` operation."""

    apiId: String


class FlushApiCacheResponse(TypedDict, total=False):
    """Represents the output of a ``FlushApiCache`` operation."""


Functions = List[FunctionConfiguration]


class GetApiAssociationRequest(ServiceRequest):
    domainName: DomainName


class GetApiAssociationResponse(TypedDict, total=False):
    apiAssociation: Optional[ApiAssociation]


class GetApiCacheRequest(ServiceRequest):
    """Represents the input of a ``GetApiCache`` operation."""

    apiId: String


class GetApiCacheResponse(TypedDict, total=False):
    """Represents the output of a ``GetApiCache`` operation."""

    apiCache: Optional[ApiCache]


class GetDataSourceRequest(ServiceRequest):
    apiId: String
    name: ResourceName


class GetDataSourceResponse(TypedDict, total=False):
    dataSource: Optional[DataSource]


class GetDomainNameRequest(ServiceRequest):
    domainName: DomainName


class GetDomainNameResponse(TypedDict, total=False):
    domainNameConfig: Optional[DomainNameConfig]


class GetFunctionRequest(ServiceRequest):
    apiId: String
    functionId: ResourceName


class GetFunctionResponse(TypedDict, total=False):
    functionConfiguration: Optional[FunctionConfiguration]


class GetGraphqlApiRequest(ServiceRequest):
    apiId: String


class GetGraphqlApiResponse(TypedDict, total=False):
    graphqlApi: Optional[GraphqlApi]


class GetIntrospectionSchemaRequest(ServiceRequest):
    apiId: String
    format: OutputType
    includeDirectives: Optional[BooleanValue]


class GetIntrospectionSchemaResponse(TypedDict, total=False):
    schema: Optional[Blob]


class GetResolverRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName
    fieldName: ResourceName


class GetResolverResponse(TypedDict, total=False):
    resolver: Optional[Resolver]


class GetSchemaCreationStatusRequest(ServiceRequest):
    apiId: String


class GetSchemaCreationStatusResponse(TypedDict, total=False):
    status: Optional[SchemaStatus]
    details: Optional[String]


class GetTypeRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName
    format: TypeDefinitionFormat


GetTypeResponse = TypedDict(
    "GetTypeResponse",
    {
        "type": Optional[Type],
    },
    total=False,
)
GraphqlApis = List[GraphqlApi]


class ListApiKeysRequest(ServiceRequest):
    apiId: String
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


class ListApiKeysResponse(TypedDict, total=False):
    apiKeys: Optional[ApiKeys]
    nextToken: Optional[PaginationToken]


class ListDataSourcesRequest(ServiceRequest):
    apiId: String
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


class ListDataSourcesResponse(TypedDict, total=False):
    dataSources: Optional[DataSources]
    nextToken: Optional[PaginationToken]


class ListDomainNamesRequest(ServiceRequest):
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


class ListDomainNamesResponse(TypedDict, total=False):
    domainNameConfigs: Optional[DomainNameConfigs]
    nextToken: Optional[PaginationToken]


class ListFunctionsRequest(ServiceRequest):
    apiId: String
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


class ListFunctionsResponse(TypedDict, total=False):
    functions: Optional[Functions]
    nextToken: Optional[PaginationToken]


class ListGraphqlApisRequest(ServiceRequest):
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


class ListGraphqlApisResponse(TypedDict, total=False):
    graphqlApis: Optional[GraphqlApis]
    nextToken: Optional[PaginationToken]


class ListResolversByFunctionRequest(ServiceRequest):
    apiId: String
    functionId: String
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


Resolvers = List[Resolver]


class ListResolversByFunctionResponse(TypedDict, total=False):
    resolvers: Optional[Resolvers]
    nextToken: Optional[PaginationToken]


class ListResolversRequest(ServiceRequest):
    apiId: String
    typeName: String
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


class ListResolversResponse(TypedDict, total=False):
    resolvers: Optional[Resolvers]
    nextToken: Optional[PaginationToken]


class ListTagsForResourceRequest(ServiceRequest):
    resourceArn: ResourceArn


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[TagMap]


class ListTypesRequest(ServiceRequest):
    apiId: String
    format: TypeDefinitionFormat
    nextToken: Optional[PaginationToken]
    maxResults: Optional[MaxResults]


TypeList = List[Type]


class ListTypesResponse(TypedDict, total=False):
    types: Optional[TypeList]
    nextToken: Optional[PaginationToken]


class StartSchemaCreationRequest(ServiceRequest):
    apiId: String
    definition: Blob


class StartSchemaCreationResponse(TypedDict, total=False):
    status: Optional[SchemaStatus]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    tags: TagMap


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    tagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


UpdateApiCacheRequest = TypedDict(
    "UpdateApiCacheRequest",
    {
        "apiId": String,
        "ttl": Long,
        "apiCachingBehavior": ApiCachingBehavior,
        "type": ApiCacheType,
    },
    total=False,
)


class UpdateApiCacheResponse(TypedDict, total=False):
    """Represents the output of a ``UpdateApiCache`` operation."""

    apiCache: Optional[ApiCache]


class UpdateApiKeyRequest(ServiceRequest):
    apiId: String
    id: String
    description: Optional[String]
    expires: Optional[Long]


class UpdateApiKeyResponse(TypedDict, total=False):
    apiKey: Optional[ApiKey]


UpdateDataSourceRequest = TypedDict(
    "UpdateDataSourceRequest",
    {
        "apiId": String,
        "name": ResourceName,
        "description": Optional[String],
        "type": DataSourceType,
        "serviceRoleArn": Optional[String],
        "dynamodbConfig": Optional[DynamodbDataSourceConfig],
        "lambdaConfig": Optional[LambdaDataSourceConfig],
        "elasticsearchConfig": Optional[ElasticsearchDataSourceConfig],
        "openSearchServiceConfig": Optional[OpenSearchServiceDataSourceConfig],
        "httpConfig": Optional[HttpDataSourceConfig],
        "relationalDatabaseConfig": Optional[RelationalDatabaseDataSourceConfig],
    },
    total=False,
)


class UpdateDataSourceResponse(TypedDict, total=False):
    dataSource: Optional[DataSource]


class UpdateDomainNameRequest(ServiceRequest):
    domainName: DomainName
    description: Optional[Description]


class UpdateDomainNameResponse(TypedDict, total=False):
    domainNameConfig: Optional[DomainNameConfig]


class UpdateFunctionRequest(ServiceRequest):
    apiId: String
    name: ResourceName
    description: Optional[String]
    functionId: ResourceName
    dataSourceName: ResourceName
    requestMappingTemplate: Optional[MappingTemplate]
    responseMappingTemplate: Optional[MappingTemplate]
    functionVersion: String
    syncConfig: Optional[SyncConfig]
    maxBatchSize: Optional[MaxBatchSize]


class UpdateFunctionResponse(TypedDict, total=False):
    functionConfiguration: Optional[FunctionConfiguration]


class UpdateGraphqlApiRequest(ServiceRequest):
    apiId: String
    name: String
    logConfig: Optional[LogConfig]
    authenticationType: Optional[AuthenticationType]
    userPoolConfig: Optional[UserPoolConfig]
    openIDConnectConfig: Optional[OpenIDConnectConfig]
    additionalAuthenticationProviders: Optional[AdditionalAuthenticationProviders]
    xrayEnabled: Optional[Boolean]
    lambdaAuthorizerConfig: Optional[LambdaAuthorizerConfig]


class UpdateGraphqlApiResponse(TypedDict, total=False):
    graphqlApi: Optional[GraphqlApi]


class UpdateResolverRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName
    fieldName: ResourceName
    dataSourceName: Optional[ResourceName]
    requestMappingTemplate: Optional[MappingTemplate]
    responseMappingTemplate: Optional[MappingTemplate]
    kind: Optional[ResolverKind]
    pipelineConfig: Optional[PipelineConfig]
    syncConfig: Optional[SyncConfig]
    cachingConfig: Optional[CachingConfig]
    maxBatchSize: Optional[MaxBatchSize]


class UpdateResolverResponse(TypedDict, total=False):
    resolver: Optional[Resolver]


class UpdateTypeRequest(ServiceRequest):
    apiId: String
    typeName: ResourceName
    definition: Optional[String]
    format: TypeDefinitionFormat


UpdateTypeResponse = TypedDict(
    "UpdateTypeResponse",
    {
        "type": Optional[Type],
    },
    total=False,
)


class AppsyncApi:

    service = "appsync"
    version = "2017-07-25"

    @handler("AssociateApi")
    def associate_api(
        self, context: RequestContext, domain_name: DomainName, api_id: String
    ) -> AssociateApiResponse:
        """Maps an endpoint to your custom domain.

        :param domain_name: The domain name.
        :param api_id: The API ID.
        :returns: AssociateApiResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises InternalFailureException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("CreateApiCache", expand=False)
    def create_api_cache(
        self, context: RequestContext, request: CreateApiCacheRequest
    ) -> CreateApiCacheResponse:
        """Creates a cache for the GraphQL API.

        :param api_id: The GraphQL API ID.
        :param ttl: TTL in seconds for cache entries.
        :param api_caching_behavior: Caching behavior.
        :param type: The cache instance type.
        :param transit_encryption_enabled: Transit encryption flag when connecting to cache.
        :param at_rest_encryption_enabled: At-rest encryption flag for cache.
        :returns: CreateApiCacheResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateApiKey")
    def create_api_key(
        self,
        context: RequestContext,
        api_id: String,
        description: String = None,
        expires: Long = None,
    ) -> CreateApiKeyResponse:
        """Creates a unique key that you can distribute to clients who invoke your
        API.

        :param api_id: The ID for your GraphQL API.
        :param description: A description of the purpose of the API key.
        :param expires: From the creation time, the time after which the API key expires.
        :returns: CreateApiKeyResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises LimitExceededException:
        :raises UnauthorizedException:
        :raises LimitExceededException:
        :raises InternalFailureException:
        :raises ApiKeyLimitExceededException:
        :raises ApiKeyValidityOutOfBoundsException:
        """
        raise NotImplementedError

    @handler("CreateDataSource", expand=False)
    def create_data_source(
        self, context: RequestContext, request: CreateDataSourceRequest
    ) -> CreateDataSourceResponse:
        """Creates a ``DataSource`` object.

        :param api_id: The API ID for the GraphQL API for the ``DataSource``.
        :param name: A user-supplied name for the ``DataSource``.
        :param type: The type of the ``DataSource``.
        :param description: A description of the ``DataSource``.
        :param service_role_arn: The Identity and Access Management (IAM) service role Amazon Resource
        Name (ARN) for the data source.
        :param dynamodb_config: Amazon DynamoDB settings.
        :param lambda_config: Lambda settings.
        :param elasticsearch_config: Amazon OpenSearch Service settings.
        :param open_search_service_config: Amazon OpenSearch Service settings.
        :param http_config: HTTP endpoint settings.
        :param relational_database_config: Relational database settings.
        :returns: CreateDataSourceResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateDomainName")
    def create_domain_name(
        self,
        context: RequestContext,
        domain_name: DomainName,
        certificate_arn: CertificateArn,
        description: Description = None,
    ) -> CreateDomainNameResponse:
        """Creates a custom ``DomainName`` object.

        :param domain_name: The domain name.
        :param certificate_arn: The Amazon Resource Name (ARN) of the certificate.
        :param description: A description of the ``DomainName``.
        :returns: CreateDomainNameResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateFunction")
    def create_function(
        self,
        context: RequestContext,
        api_id: String,
        name: ResourceName,
        data_source_name: ResourceName,
        function_version: String,
        description: String = None,
        request_mapping_template: MappingTemplate = None,
        response_mapping_template: MappingTemplate = None,
        sync_config: SyncConfig = None,
        max_batch_size: MaxBatchSize = None,
    ) -> CreateFunctionResponse:
        """Creates a ``Function`` object.

        A function is a reusable entity. You can use multiple functions to
        compose the resolver logic.

        :param api_id: The GraphQL API ID.
        :param name: The ``Function`` name.
        :param data_source_name: The ``Function`` ``DataSource`` name.
        :param function_version: The ``version`` of the request mapping template.
        :param description: The ``Function`` description.
        :param request_mapping_template: The ``Function`` request mapping template.
        :param response_mapping_template: The ``Function`` response mapping template.
        :param sync_config: Describes a Sync configuration for a resolver.
        :param max_batch_size: The maximum batching size for a resolver.
        :returns: CreateFunctionResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateGraphqlApi")
    def create_graphql_api(
        self,
        context: RequestContext,
        name: String,
        authentication_type: AuthenticationType,
        log_config: LogConfig = None,
        user_pool_config: UserPoolConfig = None,
        open_id_connect_config: OpenIDConnectConfig = None,
        tags: TagMap = None,
        additional_authentication_providers: AdditionalAuthenticationProviders = None,
        xray_enabled: Boolean = None,
        lambda_authorizer_config: LambdaAuthorizerConfig = None,
    ) -> CreateGraphqlApiResponse:
        """Creates a ``GraphqlApi`` object.

        :param name: A user-supplied name for the ``GraphqlApi``.
        :param authentication_type: The authentication type: API key, Identity and Access Management (IAM),
        OpenID Connect (OIDC), Amazon Cognito user pools, or Lambda.
        :param log_config: The Amazon CloudWatch Logs configuration.
        :param user_pool_config: The Amazon Cognito user pool configuration.
        :param open_id_connect_config: The OIDC configuration.
        :param tags: A ``TagMap`` object.
        :param additional_authentication_providers: A list of additional authentication providers for the ``GraphqlApi``
        API.
        :param xray_enabled: A flag indicating whether to use X-Ray tracing for the ``GraphqlApi``.
        :param lambda_authorizer_config: Configuration for Lambda function authorization.
        :returns: CreateGraphqlApiResponse
        :raises BadRequestException:
        :raises LimitExceededException:
        :raises ConcurrentModificationException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ApiLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateResolver")
    def create_resolver(
        self,
        context: RequestContext,
        api_id: String,
        type_name: ResourceName,
        field_name: ResourceName,
        data_source_name: ResourceName = None,
        request_mapping_template: MappingTemplate = None,
        response_mapping_template: MappingTemplate = None,
        kind: ResolverKind = None,
        pipeline_config: PipelineConfig = None,
        sync_config: SyncConfig = None,
        caching_config: CachingConfig = None,
        max_batch_size: MaxBatchSize = None,
    ) -> CreateResolverResponse:
        """Creates a ``Resolver`` object.

        A resolver converts incoming requests into a format that a data source
        can understand, and converts the data source's responses into GraphQL.

        :param api_id: The ID for the GraphQL API for which the resolver is being created.
        :param type_name: The name of the ``Type``.
        :param field_name: The name of the field to attach the resolver to.
        :param data_source_name: The name of the data source for which the resolver is being created.
        :param request_mapping_template: The mapping template to use for requests.
        :param response_mapping_template: The mapping template to use for responses from the data source.
        :param kind: The resolver type.
        :param pipeline_config: The ``PipelineConfig``.
        :param sync_config: The ``SyncConfig`` for a resolver attached to a versioned data source.
        :param caching_config: The caching configuration for the resolver.
        :param max_batch_size: The maximum batching size for a resolver.
        :returns: CreateResolverResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateType")
    def create_type(
        self,
        context: RequestContext,
        api_id: String,
        definition: String,
        format: TypeDefinitionFormat,
    ) -> CreateTypeResponse:
        """Creates a ``Type`` object.

        :param api_id: The API ID.
        :param definition: The type definition, in GraphQL Schema Definition Language (SDL) format.
        :param format: The type format: SDL or JSON.
        :returns: CreateTypeResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteApiCache")
    def delete_api_cache(self, context: RequestContext, api_id: String) -> DeleteApiCacheResponse:
        """Deletes an ``ApiCache`` object.

        :param api_id: The API ID.
        :returns: DeleteApiCacheResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteApiKey")
    def delete_api_key(
        self, context: RequestContext, api_id: String, id: String
    ) -> DeleteApiKeyResponse:
        """Deletes an API key.

        :param api_id: The API ID.
        :param id: The ID for the API key.
        :returns: DeleteApiKeyResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteDataSource")
    def delete_data_source(
        self, context: RequestContext, api_id: String, name: ResourceName
    ) -> DeleteDataSourceResponse:
        """Deletes a ``DataSource`` object.

        :param api_id: The API ID.
        :param name: The name of the data source.
        :returns: DeleteDataSourceResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteDomainName")
    def delete_domain_name(
        self, context: RequestContext, domain_name: DomainName
    ) -> DeleteDomainNameResponse:
        """Deletes a custom ``DomainName`` object.

        :param domain_name: The domain name.
        :returns: DeleteDomainNameResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises InternalFailureException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteFunction")
    def delete_function(
        self, context: RequestContext, api_id: String, function_id: ResourceName
    ) -> DeleteFunctionResponse:
        """Deletes a ``Function``.

        :param api_id: The GraphQL API ID.
        :param function_id: The ``Function`` ID.
        :returns: DeleteFunctionResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteGraphqlApi")
    def delete_graphql_api(
        self, context: RequestContext, api_id: String
    ) -> DeleteGraphqlApiResponse:
        """Deletes a ``GraphqlApi`` object.

        :param api_id: The API ID.
        :returns: DeleteGraphqlApiResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("DeleteResolver")
    def delete_resolver(
        self,
        context: RequestContext,
        api_id: String,
        type_name: ResourceName,
        field_name: ResourceName,
    ) -> DeleteResolverResponse:
        """Deletes a ``Resolver`` object.

        :param api_id: The API ID.
        :param type_name: The name of the resolver type.
        :param field_name: The resolver field name.
        :returns: DeleteResolverResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteType")
    def delete_type(
        self, context: RequestContext, api_id: String, type_name: ResourceName
    ) -> DeleteTypeResponse:
        """Deletes a ``Type`` object.

        :param api_id: The API ID.
        :param type_name: The type name.
        :returns: DeleteTypeResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DisassociateApi")
    def disassociate_api(
        self, context: RequestContext, domain_name: DomainName
    ) -> DisassociateApiResponse:
        """Removes an ``ApiAssociation`` object from a custom domain.

        :param domain_name: The domain name.
        :returns: DisassociateApiResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises InternalFailureException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("FlushApiCache")
    def flush_api_cache(self, context: RequestContext, api_id: String) -> FlushApiCacheResponse:
        """Flushes an ``ApiCache`` object.

        :param api_id: The API ID.
        :returns: FlushApiCacheResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetApiAssociation")
    def get_api_association(
        self, context: RequestContext, domain_name: DomainName
    ) -> GetApiAssociationResponse:
        """Retrieves an ``ApiAssociation`` object.

        :param domain_name: The domain name.
        :returns: GetApiAssociationResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises InternalFailureException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("GetApiCache")
    def get_api_cache(self, context: RequestContext, api_id: String) -> GetApiCacheResponse:
        """Retrieves an ``ApiCache`` object.

        :param api_id: The API ID.
        :returns: GetApiCacheResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetDataSource")
    def get_data_source(
        self, context: RequestContext, api_id: String, name: ResourceName
    ) -> GetDataSourceResponse:
        """Retrieves a ``DataSource`` object.

        :param api_id: The API ID.
        :param name: The name of the data source.
        :returns: GetDataSourceResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetDomainName")
    def get_domain_name(
        self, context: RequestContext, domain_name: DomainName
    ) -> GetDomainNameResponse:
        """Retrieves a custom ``DomainName`` object.

        :param domain_name: The domain name.
        :returns: GetDomainNameResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises InternalFailureException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("GetFunction")
    def get_function(
        self, context: RequestContext, api_id: String, function_id: ResourceName
    ) -> GetFunctionResponse:
        """Get a ``Function``.

        :param api_id: The GraphQL API ID.
        :param function_id: The ``Function`` ID.
        :returns: GetFunctionResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("GetGraphqlApi")
    def get_graphql_api(self, context: RequestContext, api_id: String) -> GetGraphqlApiResponse:
        """Retrieves a ``GraphqlApi`` object.

        :param api_id: The API ID for the GraphQL API.
        :returns: GetGraphqlApiResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("GetIntrospectionSchema")
    def get_introspection_schema(
        self,
        context: RequestContext,
        api_id: String,
        format: OutputType,
        include_directives: BooleanValue = None,
    ) -> GetIntrospectionSchemaResponse:
        """Retrieves the introspection schema for a GraphQL API.

        :param api_id: The API ID.
        :param format: The schema format: SDL or JSON.
        :param include_directives: A flag that specifies whether the schema introspection should contain
        directives.
        :returns: GetIntrospectionSchemaResponse
        :raises GraphQLSchemaException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetResolver")
    def get_resolver(
        self,
        context: RequestContext,
        api_id: String,
        type_name: ResourceName,
        field_name: ResourceName,
    ) -> GetResolverResponse:
        """Retrieves a ``Resolver`` object.

        :param api_id: The API ID.
        :param type_name: The resolver type name.
        :param field_name: The resolver field name.
        :returns: GetResolverResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("GetSchemaCreationStatus")
    def get_schema_creation_status(
        self, context: RequestContext, api_id: String
    ) -> GetSchemaCreationStatusResponse:
        """Retrieves the current status of a schema creation operation.

        :param api_id: The API ID.
        :returns: GetSchemaCreationStatusResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetType")
    def get_type(
        self,
        context: RequestContext,
        api_id: String,
        type_name: ResourceName,
        format: TypeDefinitionFormat,
    ) -> GetTypeResponse:
        """Retrieves a ``Type`` object.

        :param api_id: The API ID.
        :param type_name: The type name.
        :param format: The type format: SDL or JSON.
        :returns: GetTypeResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListApiKeys")
    def list_api_keys(
        self,
        context: RequestContext,
        api_id: String,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListApiKeysResponse:
        """Lists the API keys for a given API.

        API keys are deleted automatically 60 days after they expire. However,
        they may still be included in the response until they have actually been
        deleted. You can safely call ``DeleteApiKey`` to manually delete a key
        before it's automatically deleted.

        :param api_id: The API ID.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListApiKeysResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListDataSources")
    def list_data_sources(
        self,
        context: RequestContext,
        api_id: String,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListDataSourcesResponse:
        """Lists the data sources for a given API.

        :param api_id: The API ID.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListDataSourcesResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListDomainNames")
    def list_domain_names(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListDomainNamesResponse:
        """Lists multiple custom domain names.

        :param next_token: The API token.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListDomainNamesResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListFunctions")
    def list_functions(
        self,
        context: RequestContext,
        api_id: String,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListFunctionsResponse:
        """List multiple functions.

        :param api_id: The GraphQL API ID.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListFunctionsResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListGraphqlApis")
    def list_graphql_apis(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListGraphqlApisResponse:
        """Lists your GraphQL APIs.

        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListGraphqlApisResponse
        :raises BadRequestException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListResolvers")
    def list_resolvers(
        self,
        context: RequestContext,
        api_id: String,
        type_name: String,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListResolversResponse:
        """Lists the resolvers for a given API and type.

        :param api_id: The API ID.
        :param type_name: The type name.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListResolversResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListResolversByFunction")
    def list_resolvers_by_function(
        self,
        context: RequestContext,
        api_id: String,
        function_id: String,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListResolversByFunctionResponse:
        """List the resolvers that are associated with a specific function.

        :param api_id: The API ID.
        :param function_id: The function ID.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListResolversByFunctionResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ResourceArn
    ) -> ListTagsForResourceResponse:
        """Lists the tags for a resource.

        :param resource_arn: The ``GraphqlApi`` Amazon Resource Name (ARN).
        :returns: ListTagsForResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises LimitExceededException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("ListTypes")
    def list_types(
        self,
        context: RequestContext,
        api_id: String,
        format: TypeDefinitionFormat,
        next_token: PaginationToken = None,
        max_results: MaxResults = None,
    ) -> ListTypesResponse:
        """Lists the types for a given API.

        :param api_id: The API ID.
        :param format: The type format: SDL or JSON.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which you can use to return the next set of items in the
        list.
        :param max_results: The maximum number of results that you want the request to return.
        :returns: ListTypesResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("StartSchemaCreation")
    def start_schema_creation(
        self, context: RequestContext, api_id: String, definition: Blob
    ) -> StartSchemaCreationResponse:
        """Adds a new schema to your GraphQL API.

        This operation is asynchronous. Use to determine when it has completed.

        :param api_id: The API ID.
        :param definition: The schema definition, in GraphQL schema language format.
        :returns: StartSchemaCreationResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tags: TagMap
    ) -> TagResourceResponse:
        """Tags a resource with user-supplied tags.

        :param resource_arn: The ``GraphqlApi`` Amazon Resource Name (ARN).
        :param tags: A ``TagMap`` object.
        :returns: TagResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises LimitExceededException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Untags a resource.

        :param resource_arn: The ``GraphqlApi`` Amazon Resource Name (ARN).
        :param tag_keys: A list of ``TagKey`` objects.
        :returns: UntagResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises LimitExceededException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UpdateApiCache", expand=False)
    def update_api_cache(
        self, context: RequestContext, request: UpdateApiCacheRequest
    ) -> UpdateApiCacheResponse:
        """Updates the cache for the GraphQL API.

        :param api_id: The GraphQL API ID.
        :param ttl: TTL in seconds for cache entries.
        :param api_caching_behavior: Caching behavior.
        :param type: The cache instance type.
        :returns: UpdateApiCacheResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateApiKey")
    def update_api_key(
        self,
        context: RequestContext,
        api_id: String,
        id: String,
        description: String = None,
        expires: Long = None,
    ) -> UpdateApiKeyResponse:
        """Updates an API key. You can update the key as long as it's not deleted.

        :param api_id: The ID for the GraphQL API.
        :param id: The API key ID.
        :param description: A description of the purpose of the API key.
        :param expires: From the update time, the time after which the API key expires.
        :returns: UpdateApiKeyResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises LimitExceededException:
        :raises InternalFailureException:
        :raises ApiKeyValidityOutOfBoundsException:
        """
        raise NotImplementedError

    @handler("UpdateDataSource", expand=False)
    def update_data_source(
        self, context: RequestContext, request: UpdateDataSourceRequest
    ) -> UpdateDataSourceResponse:
        """Updates a ``DataSource`` object.

        :param api_id: The API ID.
        :param name: The new name for the data source.
        :param type: The new data source type.
        :param description: The new description for the data source.
        :param service_role_arn: The new service role Amazon Resource Name (ARN) for the data source.
        :param dynamodb_config: The new Amazon DynamoDB configuration.
        :param lambda_config: The new Lambda configuration.
        :param elasticsearch_config: The new OpenSearch configuration.
        :param open_search_service_config: The new OpenSearch configuration.
        :param http_config: The new HTTP endpoint configuration.
        :param relational_database_config: The new relational database configuration.
        :returns: UpdateDataSourceResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateDomainName")
    def update_domain_name(
        self, context: RequestContext, domain_name: DomainName, description: Description = None
    ) -> UpdateDomainNameResponse:
        """Updates a custom ``DomainName`` object.

        :param domain_name: The domain name.
        :param description: A description of the ``DomainName``.
        :returns: UpdateDomainNameResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises InternalFailureException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateFunction")
    def update_function(
        self,
        context: RequestContext,
        api_id: String,
        name: ResourceName,
        function_id: ResourceName,
        data_source_name: ResourceName,
        function_version: String,
        description: String = None,
        request_mapping_template: MappingTemplate = None,
        response_mapping_template: MappingTemplate = None,
        sync_config: SyncConfig = None,
        max_batch_size: MaxBatchSize = None,
    ) -> UpdateFunctionResponse:
        """Updates a ``Function`` object.

        :param api_id: The GraphQL API ID.
        :param name: The ``Function`` name.
        :param function_id: The function ID.
        :param data_source_name: The ``Function`` ``DataSource`` name.
        :param function_version: The ``version`` of the request mapping template.
        :param description: The ``Function`` description.
        :param request_mapping_template: The ``Function`` request mapping template.
        :param response_mapping_template: The ``Function`` request mapping template.
        :param sync_config: Describes a Sync configuration for a resolver.
        :param max_batch_size: The maximum batching size for a resolver.
        :returns: UpdateFunctionResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateGraphqlApi")
    def update_graphql_api(
        self,
        context: RequestContext,
        api_id: String,
        name: String,
        log_config: LogConfig = None,
        authentication_type: AuthenticationType = None,
        user_pool_config: UserPoolConfig = None,
        open_id_connect_config: OpenIDConnectConfig = None,
        additional_authentication_providers: AdditionalAuthenticationProviders = None,
        xray_enabled: Boolean = None,
        lambda_authorizer_config: LambdaAuthorizerConfig = None,
    ) -> UpdateGraphqlApiResponse:
        """Updates a ``GraphqlApi`` object.

        :param api_id: The API ID.
        :param name: The new name for the ``GraphqlApi`` object.
        :param log_config: The Amazon CloudWatch Logs configuration for the ``GraphqlApi`` object.
        :param authentication_type: The new authentication type for the ``GraphqlApi`` object.
        :param user_pool_config: The new Amazon Cognito user pool configuration for the ``~GraphqlApi``
        object.
        :param open_id_connect_config: The OpenID Connect configuration for the ``GraphqlApi`` object.
        :param additional_authentication_providers: A list of additional authentication providers for the ``GraphqlApi``
        API.
        :param xray_enabled: A flag indicating whether to use X-Ray tracing for the ``GraphqlApi``.
        :param lambda_authorizer_config: Configuration for Lambda function authorization.
        :returns: UpdateGraphqlApiResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UpdateResolver")
    def update_resolver(
        self,
        context: RequestContext,
        api_id: String,
        type_name: ResourceName,
        field_name: ResourceName,
        data_source_name: ResourceName = None,
        request_mapping_template: MappingTemplate = None,
        response_mapping_template: MappingTemplate = None,
        kind: ResolverKind = None,
        pipeline_config: PipelineConfig = None,
        sync_config: SyncConfig = None,
        caching_config: CachingConfig = None,
        max_batch_size: MaxBatchSize = None,
    ) -> UpdateResolverResponse:
        """Updates a ``Resolver`` object.

        :param api_id: The API ID.
        :param type_name: The new type name.
        :param field_name: The new field name.
        :param data_source_name: The new data source name.
        :param request_mapping_template: The new request mapping template.
        :param response_mapping_template: The new response mapping template.
        :param kind: The resolver type.
        :param pipeline_config: The ``PipelineConfig``.
        :param sync_config: The ``SyncConfig`` for a resolver attached to a versioned data source.
        :param caching_config: The caching configuration for the resolver.
        :param max_batch_size: The maximum batching size for a resolver.
        :returns: UpdateResolverResponse
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateType")
    def update_type(
        self,
        context: RequestContext,
        api_id: String,
        type_name: ResourceName,
        format: TypeDefinitionFormat,
        definition: String = None,
    ) -> UpdateTypeResponse:
        """Updates a ``Type`` object.

        :param api_id: The API ID.
        :param type_name: The new type name.
        :param format: The new type format: SDL or JSON.
        :param definition: The new definition.
        :returns: UpdateTypeResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError
