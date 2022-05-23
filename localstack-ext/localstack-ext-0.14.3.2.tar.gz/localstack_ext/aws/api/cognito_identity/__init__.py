import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ARNString = str
AccessKeyString = str
AccountId = str
ClaimName = str
ClaimValue = str
ClassicFlow = bool
CognitoIdentityProviderClientId = str
CognitoIdentityProviderName = str
CognitoIdentityProviderTokenCheck = bool
DeveloperProviderName = str
DeveloperUserIdentifier = str
HideDisabled = bool
IdentityId = str
IdentityPoolId = str
IdentityPoolName = str
IdentityPoolUnauthenticated = bool
IdentityProviderId = str
IdentityProviderName = str
IdentityProviderToken = str
OIDCToken = str
PaginationKey = str
PrincipalTagID = str
PrincipalTagValue = str
QueryLimit = int
RoleType = str
SecretKeyString = str
SessionTokenString = str
String = str
TagKeysType = str
TagValueType = str
UseDefaults = bool


class AmbiguousRoleResolutionType(str):
    AuthenticatedRole = "AuthenticatedRole"
    Deny = "Deny"


class ErrorCode(str):
    AccessDenied = "AccessDenied"
    InternalServerError = "InternalServerError"


class MappingRuleMatchType(str):
    Equals = "Equals"
    Contains = "Contains"
    StartsWith = "StartsWith"
    NotEqual = "NotEqual"


class RoleMappingType(str):
    Token = "Token"
    Rules = "Rules"


class ConcurrentModificationException(ServiceException):
    """Thrown if there are parallel requests to modify a resource."""

    message: Optional[String]


class DeveloperUserAlreadyRegisteredException(ServiceException):
    """The provided developer user identifier is already registered with
    Cognito under a different identity ID.
    """

    message: Optional[String]


class ExternalServiceException(ServiceException):
    """An exception thrown when a dependent service such as Facebook or Twitter
    is not responding
    """

    message: Optional[String]


class InternalErrorException(ServiceException):
    """Thrown when the service encounters an error during processing the
    request.
    """

    message: Optional[String]


class InvalidIdentityPoolConfigurationException(ServiceException):
    """Thrown if the identity pool has no role associated for the given auth
    type (auth/unauth) or if the AssumeRole fails.
    """

    message: Optional[String]


class InvalidParameterException(ServiceException):
    """Thrown for missing or bad input parameter(s)."""

    message: Optional[String]


class LimitExceededException(ServiceException):
    """Thrown when the total number of user pools has exceeded a preset limit."""

    message: Optional[String]


class NotAuthorizedException(ServiceException):
    """Thrown when a user is not authorized to access the requested resource."""

    message: Optional[String]


class ResourceConflictException(ServiceException):
    """Thrown when a user tries to use a login which is already linked to
    another account.
    """

    message: Optional[String]


class ResourceNotFoundException(ServiceException):
    """Thrown when the requested resource (for example, a dataset or record)
    does not exist.
    """

    message: Optional[String]


class TooManyRequestsException(ServiceException):
    """Thrown when a request is throttled."""

    message: Optional[String]


class CognitoIdentityProvider(TypedDict, total=False):
    """A provider representing an Amazon Cognito user pool and its client ID."""

    ProviderName: Optional[CognitoIdentityProviderName]
    ClientId: Optional[CognitoIdentityProviderClientId]
    ServerSideTokenCheck: Optional[CognitoIdentityProviderTokenCheck]


CognitoIdentityProviderList = List[CognitoIdentityProvider]
IdentityPoolTagsType = Dict[TagKeysType, TagValueType]
SAMLProviderList = List[ARNString]
OIDCProviderList = List[ARNString]
IdentityProviders = Dict[IdentityProviderName, IdentityProviderId]


class CreateIdentityPoolInput(ServiceRequest):
    """Input to the CreateIdentityPool action."""

    IdentityPoolName: IdentityPoolName
    AllowUnauthenticatedIdentities: IdentityPoolUnauthenticated
    AllowClassicFlow: Optional[ClassicFlow]
    SupportedLoginProviders: Optional[IdentityProviders]
    DeveloperProviderName: Optional[DeveloperProviderName]
    OpenIdConnectProviderARNs: Optional[OIDCProviderList]
    CognitoIdentityProviders: Optional[CognitoIdentityProviderList]
    SamlProviderARNs: Optional[SAMLProviderList]
    IdentityPoolTags: Optional[IdentityPoolTagsType]


DateType = datetime


class Credentials(TypedDict, total=False):
    """Credentials for the provided identity ID."""

    AccessKeyId: Optional[AccessKeyString]
    SecretKey: Optional[SecretKeyString]
    SessionToken: Optional[SessionTokenString]
    Expiration: Optional[DateType]


IdentityIdList = List[IdentityId]


class DeleteIdentitiesInput(ServiceRequest):
    """Input to the ``DeleteIdentities`` action."""

    IdentityIdsToDelete: IdentityIdList


class UnprocessedIdentityId(TypedDict, total=False):
    """An array of UnprocessedIdentityId objects, each of which contains an
    ErrorCode and IdentityId.
    """

    IdentityId: Optional[IdentityId]
    ErrorCode: Optional[ErrorCode]


UnprocessedIdentityIdList = List[UnprocessedIdentityId]


class DeleteIdentitiesResponse(TypedDict, total=False):
    """Returned in response to a successful ``DeleteIdentities`` operation."""

    UnprocessedIdentityIds: Optional[UnprocessedIdentityIdList]


class DeleteIdentityPoolInput(ServiceRequest):
    """Input to the DeleteIdentityPool action."""

    IdentityPoolId: IdentityPoolId


class DescribeIdentityInput(ServiceRequest):
    """Input to the ``DescribeIdentity`` action."""

    IdentityId: IdentityId


class DescribeIdentityPoolInput(ServiceRequest):
    """Input to the DescribeIdentityPool action."""

    IdentityPoolId: IdentityPoolId


DeveloperUserIdentifierList = List[DeveloperUserIdentifier]
LoginsMap = Dict[IdentityProviderName, IdentityProviderToken]


class GetCredentialsForIdentityInput(ServiceRequest):
    """Input to the ``GetCredentialsForIdentity`` action."""

    IdentityId: IdentityId
    Logins: Optional[LoginsMap]
    CustomRoleArn: Optional[ARNString]


class GetCredentialsForIdentityResponse(TypedDict, total=False):
    """Returned in response to a successful ``GetCredentialsForIdentity``
    operation.
    """

    IdentityId: Optional[IdentityId]
    Credentials: Optional[Credentials]


class GetIdInput(ServiceRequest):
    """Input to the GetId action."""

    AccountId: Optional[AccountId]
    IdentityPoolId: IdentityPoolId
    Logins: Optional[LoginsMap]


class GetIdResponse(TypedDict, total=False):
    """Returned in response to a GetId request."""

    IdentityId: Optional[IdentityId]


class GetIdentityPoolRolesInput(ServiceRequest):
    """Input to the ``GetIdentityPoolRoles`` action."""

    IdentityPoolId: IdentityPoolId


class MappingRule(TypedDict, total=False):
    """A rule that maps a claim name, a claim value, and a match type to a role
    ARN.
    """

    Claim: ClaimName
    MatchType: MappingRuleMatchType
    Value: ClaimValue
    RoleARN: ARNString


MappingRulesList = List[MappingRule]


class RulesConfigurationType(TypedDict, total=False):
    """A container for rules."""

    Rules: MappingRulesList


class RoleMapping(TypedDict, total=False):
    """A role mapping."""

    Type: RoleMappingType
    AmbiguousRoleResolution: Optional[AmbiguousRoleResolutionType]
    RulesConfiguration: Optional[RulesConfigurationType]


RoleMappingMap = Dict[IdentityProviderName, RoleMapping]
RolesMap = Dict[RoleType, ARNString]


class GetIdentityPoolRolesResponse(TypedDict, total=False):
    """Returned in response to a successful ``GetIdentityPoolRoles`` operation."""

    IdentityPoolId: Optional[IdentityPoolId]
    Roles: Optional[RolesMap]
    RoleMappings: Optional[RoleMappingMap]


TokenDuration = int
PrincipalTags = Dict[PrincipalTagID, PrincipalTagValue]


class GetOpenIdTokenForDeveloperIdentityInput(ServiceRequest):
    """Input to the ``GetOpenIdTokenForDeveloperIdentity`` action."""

    IdentityPoolId: IdentityPoolId
    IdentityId: Optional[IdentityId]
    Logins: LoginsMap
    PrincipalTags: Optional[PrincipalTags]
    TokenDuration: Optional[TokenDuration]


class GetOpenIdTokenForDeveloperIdentityResponse(TypedDict, total=False):
    """Returned in response to a successful
    ``GetOpenIdTokenForDeveloperIdentity`` request.
    """

    IdentityId: Optional[IdentityId]
    Token: Optional[OIDCToken]


class GetOpenIdTokenInput(ServiceRequest):
    """Input to the GetOpenIdToken action."""

    IdentityId: IdentityId
    Logins: Optional[LoginsMap]


class GetOpenIdTokenResponse(TypedDict, total=False):
    """Returned in response to a successful GetOpenIdToken request."""

    IdentityId: Optional[IdentityId]
    Token: Optional[OIDCToken]


class GetPrincipalTagAttributeMapInput(ServiceRequest):
    IdentityPoolId: IdentityPoolId
    IdentityProviderName: IdentityProviderName


class GetPrincipalTagAttributeMapResponse(TypedDict, total=False):
    IdentityPoolId: Optional[IdentityPoolId]
    IdentityProviderName: Optional[IdentityProviderName]
    UseDefaults: Optional[UseDefaults]
    PrincipalTags: Optional[PrincipalTags]


LoginsList = List[IdentityProviderName]


class IdentityDescription(TypedDict, total=False):
    """A description of the identity."""

    IdentityId: Optional[IdentityId]
    Logins: Optional[LoginsList]
    CreationDate: Optional[DateType]
    LastModifiedDate: Optional[DateType]


IdentitiesList = List[IdentityDescription]


class IdentityPool(ServiceRequest):
    """An object representing an Amazon Cognito identity pool."""

    IdentityPoolId: IdentityPoolId
    IdentityPoolName: IdentityPoolName
    AllowUnauthenticatedIdentities: IdentityPoolUnauthenticated
    AllowClassicFlow: Optional[ClassicFlow]
    SupportedLoginProviders: Optional[IdentityProviders]
    DeveloperProviderName: Optional[DeveloperProviderName]
    OpenIdConnectProviderARNs: Optional[OIDCProviderList]
    CognitoIdentityProviders: Optional[CognitoIdentityProviderList]
    SamlProviderARNs: Optional[SAMLProviderList]
    IdentityPoolTags: Optional[IdentityPoolTagsType]


class IdentityPoolShortDescription(TypedDict, total=False):
    """A description of the identity pool."""

    IdentityPoolId: Optional[IdentityPoolId]
    IdentityPoolName: Optional[IdentityPoolName]


IdentityPoolTagsListType = List[TagKeysType]
IdentityPoolsList = List[IdentityPoolShortDescription]


class ListIdentitiesInput(ServiceRequest):
    """Input to the ListIdentities action."""

    IdentityPoolId: IdentityPoolId
    MaxResults: QueryLimit
    NextToken: Optional[PaginationKey]
    HideDisabled: Optional[HideDisabled]


class ListIdentitiesResponse(TypedDict, total=False):
    """The response to a ListIdentities request."""

    IdentityPoolId: Optional[IdentityPoolId]
    Identities: Optional[IdentitiesList]
    NextToken: Optional[PaginationKey]


class ListIdentityPoolsInput(ServiceRequest):
    """Input to the ListIdentityPools action."""

    MaxResults: QueryLimit
    NextToken: Optional[PaginationKey]


class ListIdentityPoolsResponse(TypedDict, total=False):
    """The result of a successful ListIdentityPools action."""

    IdentityPools: Optional[IdentityPoolsList]
    NextToken: Optional[PaginationKey]


class ListTagsForResourceInput(ServiceRequest):
    ResourceArn: ARNString


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[IdentityPoolTagsType]


class LookupDeveloperIdentityInput(ServiceRequest):
    """Input to the ``LookupDeveloperIdentityInput`` action."""

    IdentityPoolId: IdentityPoolId
    IdentityId: Optional[IdentityId]
    DeveloperUserIdentifier: Optional[DeveloperUserIdentifier]
    MaxResults: Optional[QueryLimit]
    NextToken: Optional[PaginationKey]


class LookupDeveloperIdentityResponse(TypedDict, total=False):
    """Returned in response to a successful ``LookupDeveloperIdentity`` action."""

    IdentityId: Optional[IdentityId]
    DeveloperUserIdentifierList: Optional[DeveloperUserIdentifierList]
    NextToken: Optional[PaginationKey]


class MergeDeveloperIdentitiesInput(ServiceRequest):
    """Input to the ``MergeDeveloperIdentities`` action."""

    SourceUserIdentifier: DeveloperUserIdentifier
    DestinationUserIdentifier: DeveloperUserIdentifier
    DeveloperProviderName: DeveloperProviderName
    IdentityPoolId: IdentityPoolId


class MergeDeveloperIdentitiesResponse(TypedDict, total=False):
    """Returned in response to a successful ``MergeDeveloperIdentities``
    action.
    """

    IdentityId: Optional[IdentityId]


class SetIdentityPoolRolesInput(ServiceRequest):
    """Input to the ``SetIdentityPoolRoles`` action."""

    IdentityPoolId: IdentityPoolId
    Roles: RolesMap
    RoleMappings: Optional[RoleMappingMap]


class SetPrincipalTagAttributeMapInput(ServiceRequest):
    IdentityPoolId: IdentityPoolId
    IdentityProviderName: IdentityProviderName
    UseDefaults: Optional[UseDefaults]
    PrincipalTags: Optional[PrincipalTags]


class SetPrincipalTagAttributeMapResponse(TypedDict, total=False):
    IdentityPoolId: Optional[IdentityPoolId]
    IdentityProviderName: Optional[IdentityProviderName]
    UseDefaults: Optional[UseDefaults]
    PrincipalTags: Optional[PrincipalTags]


class TagResourceInput(ServiceRequest):
    ResourceArn: ARNString
    Tags: IdentityPoolTagsType


class TagResourceResponse(TypedDict, total=False):
    pass


class UnlinkDeveloperIdentityInput(ServiceRequest):
    """Input to the ``UnlinkDeveloperIdentity`` action."""

    IdentityId: IdentityId
    IdentityPoolId: IdentityPoolId
    DeveloperProviderName: DeveloperProviderName
    DeveloperUserIdentifier: DeveloperUserIdentifier


class UnlinkIdentityInput(ServiceRequest):
    """Input to the UnlinkIdentity action."""

    IdentityId: IdentityId
    Logins: LoginsMap
    LoginsToRemove: LoginsList


class UntagResourceInput(ServiceRequest):
    ResourceArn: ARNString
    TagKeys: IdentityPoolTagsListType


class UntagResourceResponse(TypedDict, total=False):
    pass


class CognitoIdentityApi:

    service = "cognito-identity"
    version = "2014-06-30"

    @handler("CreateIdentityPool")
    def create_identity_pool(
        self,
        context: RequestContext,
        identity_pool_name: IdentityPoolName,
        allow_unauthenticated_identities: IdentityPoolUnauthenticated,
        allow_classic_flow: ClassicFlow = None,
        supported_login_providers: IdentityProviders = None,
        developer_provider_name: DeveloperProviderName = None,
        open_id_connect_provider_arns: OIDCProviderList = None,
        cognito_identity_providers: CognitoIdentityProviderList = None,
        saml_provider_arns: SAMLProviderList = None,
        identity_pool_tags: IdentityPoolTagsType = None,
    ) -> IdentityPool:
        """Creates a new identity pool. The identity pool is a store of user
        identity information that is specific to your AWS account. The keys for
        ``SupportedLoginProviders`` are as follows:

        -  Facebook: ``graph.facebook.com``

        -  Google: ``accounts.google.com``

        -  Amazon: ``www.amazon.com``

        -  Twitter: ``api.twitter.com``

        -  Digits: ``www.digits.com``

        You must use AWS Developer credentials to call this API.

        :param identity_pool_name: A string that you provide.
        :param allow_unauthenticated_identities: TRUE if the identity pool supports unauthenticated logins.
        :param allow_classic_flow: Enables or disables the Basic (Classic) authentication flow.
        :param supported_login_providers: Optional key:value pairs mapping provider names to provider app IDs.
        :param developer_provider_name: The "domain" by which Cognito will refer to your users.
        :param open_id_connect_provider_arns: The Amazon Resource Names (ARN) of the OpenID Connect providers.
        :param cognito_identity_providers: An array of Amazon Cognito user pools and their client IDs.
        :param saml_provider_arns: An array of Amazon Resource Names (ARNs) of the SAML provider for your
        identity pool.
        :param identity_pool_tags: Tags to assign to the identity pool.
        :returns: IdentityPool
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DeleteIdentities")
    def delete_identities(
        self, context: RequestContext, identity_ids_to_delete: IdentityIdList
    ) -> DeleteIdentitiesResponse:
        """Deletes identities from an identity pool. You can specify a list of 1-60
        identities that you want to delete.

        You must use AWS Developer credentials to call this API.

        :param identity_ids_to_delete: A list of 1-60 identities that you want to delete.
        :returns: DeleteIdentitiesResponse
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteIdentityPool")
    def delete_identity_pool(
        self, context: RequestContext, identity_pool_id: IdentityPoolId
    ) -> None:
        """Deletes an identity pool. Once a pool is deleted, users will not be able
        to authenticate with the pool.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeIdentity")
    def describe_identity(
        self, context: RequestContext, identity_id: IdentityId
    ) -> IdentityDescription:
        """Returns metadata related to the given identity, including when the
        identity was created and any associated linked logins.

        You must use AWS Developer credentials to call this API.

        :param identity_id: A unique identifier in the format REGION:GUID.
        :returns: IdentityDescription
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeIdentityPool")
    def describe_identity_pool(
        self, context: RequestContext, identity_pool_id: IdentityPoolId
    ) -> IdentityPool:
        """Gets details about a particular identity pool, including the pool name,
        ID description, creation date, and current number of users.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :returns: IdentityPool
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetCredentialsForIdentity")
    def get_credentials_for_identity(
        self,
        context: RequestContext,
        identity_id: IdentityId,
        logins: LoginsMap = None,
        custom_role_arn: ARNString = None,
    ) -> GetCredentialsForIdentityResponse:
        """Returns credentials for the provided identity ID. Any provided logins
        will be validated against supported login providers. If the token is for
        cognito-identity.amazonaws.com, it will be passed through to AWS
        Security Token Service with the appropriate role for the token.

        This is a public API. You do not need any credentials to call this API.

        :param identity_id: A unique identifier in the format REGION:GUID.
        :param logins: A set of optional name-value pairs that map provider names to provider
        tokens.
        :param custom_role_arn: The Amazon Resource Name (ARN) of the role to be assumed when multiple
        roles were received in the token from the identity provider.
        :returns: GetCredentialsForIdentityResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InvalidIdentityPoolConfigurationException:
        :raises InternalErrorException:
        :raises ExternalServiceException:
        """
        raise NotImplementedError

    @handler("GetId")
    def get_id(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        account_id: AccountId = None,
        logins: LoginsMap = None,
    ) -> GetIdResponse:
        """Generates (or retrieves) a Cognito ID. Supplying multiple logins will
        create an implicit linked account.

        This is a public API. You do not need any credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param account_id: A standard AWS account ID (9+ digits).
        :param logins: A set of optional name-value pairs that map provider names to provider
        tokens.
        :returns: GetIdResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises LimitExceededException:
        :raises ExternalServiceException:
        """
        raise NotImplementedError

    @handler("GetIdentityPoolRoles")
    def get_identity_pool_roles(
        self, context: RequestContext, identity_pool_id: IdentityPoolId
    ) -> GetIdentityPoolRolesResponse:
        """Gets the roles for an identity pool.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :returns: GetIdentityPoolRolesResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetOpenIdToken")
    def get_open_id_token(
        self, context: RequestContext, identity_id: IdentityId, logins: LoginsMap = None
    ) -> GetOpenIdTokenResponse:
        """Gets an OpenID token, using a known Cognito ID. This known Cognito ID is
        returned by GetId. You can optionally add additional logins for the
        identity. Supplying multiple logins creates an implicit link.

        The OpenID token is valid for 10 minutes.

        This is a public API. You do not need any credentials to call this API.

        :param identity_id: A unique identifier in the format REGION:GUID.
        :param logins: A set of optional name-value pairs that map provider names to provider
        tokens.
        :returns: GetOpenIdTokenResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises ExternalServiceException:
        """
        raise NotImplementedError

    @handler("GetOpenIdTokenForDeveloperIdentity")
    def get_open_id_token_for_developer_identity(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        logins: LoginsMap,
        identity_id: IdentityId = None,
        principal_tags: PrincipalTags = None,
        token_duration: TokenDuration = None,
    ) -> GetOpenIdTokenForDeveloperIdentityResponse:
        """Registers (or retrieves) a Cognito ``IdentityId`` and an OpenID Connect
        token for a user authenticated by your backend authentication process.
        Supplying multiple logins will create an implicit linked account. You
        can only specify one developer provider as part of the ``Logins`` map,
        which is linked to the identity pool. The developer provider is the
        "domain" by which Cognito will refer to your users.

        You can use ``GetOpenIdTokenForDeveloperIdentity`` to create a new
        identity and to link new logins (that is, user credentials issued by a
        public provider or developer provider) to an existing identity. When you
        want to create a new identity, the ``IdentityId`` should be null. When
        you want to associate a new login with an existing
        authenticated/unauthenticated identity, you can do so by providing the
        existing ``IdentityId``. This API will create the identity in the
        specified ``IdentityPoolId``.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param logins: A set of optional name-value pairs that map provider names to provider
        tokens.
        :param identity_id: A unique identifier in the format REGION:GUID.
        :param principal_tags: Use this operation to configure attribute mappings for custom providers.
        :param token_duration: The expiration time of the token, in seconds.
        :returns: GetOpenIdTokenForDeveloperIdentityResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises DeveloperUserAlreadyRegisteredException:
        """
        raise NotImplementedError

    @handler("GetPrincipalTagAttributeMap")
    def get_principal_tag_attribute_map(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        identity_provider_name: IdentityProviderName,
    ) -> GetPrincipalTagAttributeMapResponse:
        """Use ``GetPrincipalTagAttributeMap`` to list all mappings between
        ``PrincipalTags`` and user attributes.

        :param identity_pool_id: You can use this operation to get the ID of the Identity Pool you setup
        attribute mappings for.
        :param identity_provider_name: You can use this operation to get the provider name.
        :returns: GetPrincipalTagAttributeMapResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListIdentities")
    def list_identities(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        max_results: QueryLimit,
        next_token: PaginationKey = None,
        hide_disabled: HideDisabled = None,
    ) -> ListIdentitiesResponse:
        """Lists the identities in an identity pool.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param max_results: The maximum number of identities to return.
        :param next_token: A pagination token.
        :param hide_disabled: An optional boolean parameter that allows you to hide disabled
        identities.
        :returns: ListIdentitiesResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListIdentityPools")
    def list_identity_pools(
        self, context: RequestContext, max_results: QueryLimit, next_token: PaginationKey = None
    ) -> ListIdentityPoolsResponse:
        """Lists all of the Cognito identity pools registered for your account.

        You must use AWS Developer credentials to call this API.

        :param max_results: The maximum number of identities to return.
        :param next_token: A pagination token.
        :returns: ListIdentityPoolsResponse
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises ResourceNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ARNString
    ) -> ListTagsForResourceResponse:
        """Lists the tags that are assigned to an Amazon Cognito identity pool.

        A tag is a label that you can apply to identity pools to categorize and
        manage them in different ways, such as by purpose, owner, environment,
        or other criteria.

        You can use this action up to 10 times per second, per account.

        :param resource_arn: The Amazon Resource Name (ARN) of the identity pool that the tags are
        assigned to.
        :returns: ListTagsForResourceResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("LookupDeveloperIdentity")
    def lookup_developer_identity(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        identity_id: IdentityId = None,
        developer_user_identifier: DeveloperUserIdentifier = None,
        max_results: QueryLimit = None,
        next_token: PaginationKey = None,
    ) -> LookupDeveloperIdentityResponse:
        """Retrieves the ``IdentityID`` associated with a
        ``DeveloperUserIdentifier`` or the list of ``DeveloperUserIdentifier``
        values associated with an ``IdentityId`` for an existing identity.
        Either ``IdentityID`` or ``DeveloperUserIdentifier`` must not be null.
        If you supply only one of these values, the other value will be searched
        in the database and returned as a part of the response. If you supply
        both, ``DeveloperUserIdentifier`` will be matched against
        ``IdentityID``. If the values are verified against the database, the
        response returns both values and is the same as the request. Otherwise a
        ``ResourceConflictException`` is thrown.

        ``LookupDeveloperIdentity`` is intended for low-throughput control plane
        operations: for example, to enable customer service to locate an
        identity ID by username. If you are using it for higher-volume
        operations such as user authentication, your requests are likely to be
        throttled. GetOpenIdTokenForDeveloperIdentity is a better option for
        higher-volume operations for user authentication.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param identity_id: A unique identifier in the format REGION:GUID.
        :param developer_user_identifier: A unique ID used by your backend authentication process to identify a
        user.
        :param max_results: The maximum number of identities to return.
        :param next_token: A pagination token.
        :returns: LookupDeveloperIdentityResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("MergeDeveloperIdentities")
    def merge_developer_identities(
        self,
        context: RequestContext,
        source_user_identifier: DeveloperUserIdentifier,
        destination_user_identifier: DeveloperUserIdentifier,
        developer_provider_name: DeveloperProviderName,
        identity_pool_id: IdentityPoolId,
    ) -> MergeDeveloperIdentitiesResponse:
        """Merges two users having different ``IdentityId`` s, existing in the
        same identity pool, and identified by the same developer provider. You
        can use this action to request that discrete users be merged and
        identified as a single user in the Cognito environment. Cognito
        associates the given source user (``SourceUserIdentifier``) with the
        ``IdentityId`` of the ``DestinationUserIdentifier``. Only
        developer-authenticated users can be merged. If the users to be merged
        are associated with the same public provider, but as two different
        users, an exception will be thrown.

        The number of linked logins is limited to 20. So, the number of linked
        logins for the source user, ``SourceUserIdentifier``, and the
        destination user, ``DestinationUserIdentifier``, together should not be
        larger than 20. Otherwise, an exception will be thrown.

        You must use AWS Developer credentials to call this API.

        :param source_user_identifier: User identifier for the source user.
        :param destination_user_identifier: User identifier for the destination user.
        :param developer_provider_name: The "domain" by which Cognito will refer to your users.
        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :returns: MergeDeveloperIdentitiesResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("SetIdentityPoolRoles")
    def set_identity_pool_roles(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        roles: RolesMap,
        role_mappings: RoleMappingMap = None,
    ) -> None:
        """Sets the roles for an identity pool. These roles are used when making
        calls to GetCredentialsForIdentity action.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param roles: The map of roles associated with this pool.
        :param role_mappings: How users for a specific identity provider are to mapped to roles.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("SetPrincipalTagAttributeMap")
    def set_principal_tag_attribute_map(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        identity_provider_name: IdentityProviderName,
        use_defaults: UseDefaults = None,
        principal_tags: PrincipalTags = None,
    ) -> SetPrincipalTagAttributeMapResponse:
        """You can use this operation to use default (username and clientID)
        attribute or custom attribute mappings.

        :param identity_pool_id: The ID of the Identity Pool you want to set attribute mappings for.
        :param identity_provider_name: The provider name you want to use for attribute mappings.
        :param use_defaults: You can use this operation to use default (username and clientID)
        attribute mappings.
        :param principal_tags: You can use this operation to add principal tags.
        :returns: SetPrincipalTagAttributeMapResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ARNString, tags: IdentityPoolTagsType
    ) -> TagResourceResponse:
        """Assigns a set of tags to the specified Amazon Cognito identity pool. A
        tag is a label that you can use to categorize and manage identity pools
        in different ways, such as by purpose, owner, environment, or other
        criteria.

        Each tag consists of a key and value, both of which you define. A key is
        a general category for more specific values. For example, if you have
        two versions of an identity pool, one for testing and another for
        production, you might assign an ``Environment`` tag key to both identity
        pools. The value of this key might be ``Test`` for one identity pool and
        ``Production`` for the other.

        Tags are useful for cost tracking and access control. You can activate
        your tags so that they appear on the Billing and Cost Management
        console, where you can track the costs associated with your identity
        pools. In an IAM policy, you can constrain permissions for identity
        pools based on specific tags or tag values.

        You can use this action up to 5 times per second, per account. An
        identity pool can have as many as 50 tags.

        :param resource_arn: The Amazon Resource Name (ARN) of the identity pool.
        :param tags: The tags to assign to the identity pool.
        :returns: TagResourceResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UnlinkDeveloperIdentity")
    def unlink_developer_identity(
        self,
        context: RequestContext,
        identity_id: IdentityId,
        identity_pool_id: IdentityPoolId,
        developer_provider_name: DeveloperProviderName,
        developer_user_identifier: DeveloperUserIdentifier,
    ) -> None:
        """Unlinks a ``DeveloperUserIdentifier`` from an existing identity.
        Unlinked developer users will be considered new identities next time
        they are seen. If, for a given Cognito identity, you remove all
        federated identities as well as the developer user identifier, the
        Cognito identity becomes inaccessible.

        You must use AWS Developer credentials to call this API.

        :param identity_id: A unique identifier in the format REGION:GUID.
        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param developer_provider_name: The "domain" by which Cognito will refer to your users.
        :param developer_user_identifier: A unique ID used by your backend authentication process to identify a
        user.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UnlinkIdentity")
    def unlink_identity(
        self,
        context: RequestContext,
        identity_id: IdentityId,
        logins: LoginsMap,
        logins_to_remove: LoginsList,
    ) -> None:
        """Unlinks a federated identity from an existing account. Unlinked logins
        will be considered new identities next time they are seen. Removing the
        last linked login will make this identity inaccessible.

        This is a public API. You do not need any credentials to call this API.

        :param identity_id: A unique identifier in the format REGION:GUID.
        :param logins: A set of optional name-value pairs that map provider names to provider
        tokens.
        :param logins_to_remove: Provider names to unlink from this identity.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises ExternalServiceException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ARNString, tag_keys: IdentityPoolTagsListType
    ) -> UntagResourceResponse:
        """Removes the specified tags from the specified Amazon Cognito identity
        pool. You can use this action up to 5 times per second, per account

        :param resource_arn: The Amazon Resource Name (ARN) of the identity pool.
        :param tag_keys: The keys of the tags to remove from the user pool.
        :returns: UntagResourceResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateIdentityPool")
    def update_identity_pool(
        self,
        context: RequestContext,
        identity_pool_id: IdentityPoolId,
        identity_pool_name: IdentityPoolName,
        allow_unauthenticated_identities: IdentityPoolUnauthenticated,
        allow_classic_flow: ClassicFlow = None,
        supported_login_providers: IdentityProviders = None,
        developer_provider_name: DeveloperProviderName = None,
        open_id_connect_provider_arns: OIDCProviderList = None,
        cognito_identity_providers: CognitoIdentityProviderList = None,
        saml_provider_arns: SAMLProviderList = None,
        identity_pool_tags: IdentityPoolTagsType = None,
    ) -> IdentityPool:
        """Updates an identity pool.

        You must use AWS Developer credentials to call this API.

        :param identity_pool_id: An identity pool ID in the format REGION:GUID.
        :param identity_pool_name: A string that you provide.
        :param allow_unauthenticated_identities: TRUE if the identity pool supports unauthenticated logins.
        :param allow_classic_flow: Enables or disables the Basic (Classic) authentication flow.
        :param supported_login_providers: Optional key:value pairs mapping provider names to provider app IDs.
        :param developer_provider_name: The "domain" by which Cognito will refer to your users.
        :param open_id_connect_provider_arns: The ARNs of the OpenID Connect providers.
        :param cognito_identity_providers: A list representing an Amazon Cognito user pool and its client ID.
        :param saml_provider_arns: An array of Amazon Resource Names (ARNs) of the SAML provider for your
        identity pool.
        :param identity_pool_tags: The tags that are assigned to the identity pool.
        :returns: IdentityPool
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises ResourceConflictException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises ConcurrentModificationException:
        :raises LimitExceededException:
        """
        raise NotImplementedError
