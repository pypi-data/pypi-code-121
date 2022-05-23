import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AWSAccountIdType = str
AccessTokenValidityType = int
AccountTakeoverActionNotifyType = bool
AdminCreateUserUnusedAccountValidityDaysType = int
ArnType = str
AttributeMappingKeyType = str
AttributeNameType = str
AttributeValueType = str
BooleanType = bool
CSSType = str
CSSVersionType = str
ClientIdType = str
ClientNameType = str
ClientPermissionType = str
ClientSecretType = str
CompletionMessageType = str
ConfirmationCodeType = str
CustomAttributeNameType = str
DescriptionType = str
DeviceKeyType = str
DeviceNameType = str
DomainType = str
DomainVersionType = str
EmailAddressType = str
EmailNotificationBodyType = str
EmailNotificationSubjectType = str
EmailVerificationMessageByLinkType = str
EmailVerificationMessageType = str
EmailVerificationSubjectByLinkType = str
EmailVerificationSubjectType = str
EventIdType = str
ForceAliasCreation = bool
GenerateSecret = bool
GroupNameType = str
HexStringType = str
IdTokenValidityType = int
IdpIdentifierType = str
ImageUrlType = str
IntegerType = int
ListProvidersLimitType = int
ListResourceServersLimitType = int
MessageType = str
PaginationKey = str
PaginationKeyType = str
PasswordPolicyMinLengthType = int
PasswordType = str
PoolQueryLimitType = int
PreSignedUrlType = str
PrecedenceType = int
PriorityType = int
ProviderNameType = str
ProviderNameTypeV1 = str
QueryLimit = int
QueryLimitType = int
RedirectUrlType = str
RefreshTokenValidityType = int
RegionCodeType = str
ResourceServerIdentifierType = str
ResourceServerNameType = str
ResourceServerScopeDescriptionType = str
ResourceServerScopeNameType = str
S3BucketType = str
SESConfigurationSet = str
ScopeType = str
SearchPaginationTokenType = str
SecretCodeType = str
SecretHashType = str
SessionType = str
SmsVerificationMessageType = str
SoftwareTokenMFAUserCodeType = str
StringType = str
TagKeysType = str
TagValueType = str
TemporaryPasswordValidityDaysType = int
TokenModelType = str
UserFilterType = str
UserImportJobIdType = str
UserImportJobNameType = str
UserPoolIdType = str
UserPoolNameType = str
UsernameType = str
WrappedBooleanType = bool


class AccountTakeoverEventActionType(str):
    BLOCK = "BLOCK"
    MFA_IF_CONFIGURED = "MFA_IF_CONFIGURED"
    MFA_REQUIRED = "MFA_REQUIRED"
    NO_ACTION = "NO_ACTION"


class AdvancedSecurityModeType(str):
    OFF = "OFF"
    AUDIT = "AUDIT"
    ENFORCED = "ENFORCED"


class AliasAttributeType(str):
    phone_number = "phone_number"
    email = "email"
    preferred_username = "preferred_username"


class AttributeDataType(str):
    String = "String"
    Number = "Number"
    DateTime = "DateTime"
    Boolean = "Boolean"


class AuthFlowType(str):
    USER_SRP_AUTH = "USER_SRP_AUTH"
    REFRESH_TOKEN_AUTH = "REFRESH_TOKEN_AUTH"
    REFRESH_TOKEN = "REFRESH_TOKEN"
    CUSTOM_AUTH = "CUSTOM_AUTH"
    ADMIN_NO_SRP_AUTH = "ADMIN_NO_SRP_AUTH"
    USER_PASSWORD_AUTH = "USER_PASSWORD_AUTH"
    ADMIN_USER_PASSWORD_AUTH = "ADMIN_USER_PASSWORD_AUTH"


class ChallengeName(str):
    Password = "Password"
    Mfa = "Mfa"


class ChallengeNameType(str):
    SMS_MFA = "SMS_MFA"
    SOFTWARE_TOKEN_MFA = "SOFTWARE_TOKEN_MFA"
    SELECT_MFA_TYPE = "SELECT_MFA_TYPE"
    MFA_SETUP = "MFA_SETUP"
    PASSWORD_VERIFIER = "PASSWORD_VERIFIER"
    CUSTOM_CHALLENGE = "CUSTOM_CHALLENGE"
    DEVICE_SRP_AUTH = "DEVICE_SRP_AUTH"
    DEVICE_PASSWORD_VERIFIER = "DEVICE_PASSWORD_VERIFIER"
    ADMIN_NO_SRP_AUTH = "ADMIN_NO_SRP_AUTH"
    NEW_PASSWORD_REQUIRED = "NEW_PASSWORD_REQUIRED"


class ChallengeResponse(str):
    Success = "Success"
    Failure = "Failure"


class CompromisedCredentialsEventActionType(str):
    BLOCK = "BLOCK"
    NO_ACTION = "NO_ACTION"


class CustomEmailSenderLambdaVersionType(str):
    V1_0 = "V1_0"


class CustomSMSSenderLambdaVersionType(str):
    V1_0 = "V1_0"


class DefaultEmailOptionType(str):
    CONFIRM_WITH_LINK = "CONFIRM_WITH_LINK"
    CONFIRM_WITH_CODE = "CONFIRM_WITH_CODE"


class DeliveryMediumType(str):
    SMS = "SMS"
    EMAIL = "EMAIL"


class DeviceRememberedStatusType(str):
    remembered = "remembered"
    not_remembered = "not_remembered"


class DomainStatusType(str):
    CREATING = "CREATING"
    DELETING = "DELETING"
    UPDATING = "UPDATING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"


class EmailSendingAccountType(str):
    COGNITO_DEFAULT = "COGNITO_DEFAULT"
    DEVELOPER = "DEVELOPER"


class EventFilterType(str):
    SIGN_IN = "SIGN_IN"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    SIGN_UP = "SIGN_UP"


class EventResponseType(str):
    Success = "Success"
    Failure = "Failure"


class EventType(str):
    SignIn = "SignIn"
    SignUp = "SignUp"
    ForgotPassword = "ForgotPassword"


class ExplicitAuthFlowsType(str):
    ADMIN_NO_SRP_AUTH = "ADMIN_NO_SRP_AUTH"
    CUSTOM_AUTH_FLOW_ONLY = "CUSTOM_AUTH_FLOW_ONLY"
    USER_PASSWORD_AUTH = "USER_PASSWORD_AUTH"
    ALLOW_ADMIN_USER_PASSWORD_AUTH = "ALLOW_ADMIN_USER_PASSWORD_AUTH"
    ALLOW_CUSTOM_AUTH = "ALLOW_CUSTOM_AUTH"
    ALLOW_USER_PASSWORD_AUTH = "ALLOW_USER_PASSWORD_AUTH"
    ALLOW_USER_SRP_AUTH = "ALLOW_USER_SRP_AUTH"
    ALLOW_REFRESH_TOKEN_AUTH = "ALLOW_REFRESH_TOKEN_AUTH"


class FeedbackValueType(str):
    Valid = "Valid"
    Invalid = "Invalid"


class IdentityProviderTypeType(str):
    SAML = "SAML"
    Facebook = "Facebook"
    Google = "Google"
    LoginWithAmazon = "LoginWithAmazon"
    SignInWithApple = "SignInWithApple"
    OIDC = "OIDC"


class MessageActionType(str):
    RESEND = "RESEND"
    SUPPRESS = "SUPPRESS"


class OAuthFlowType(str):
    code = "code"
    implicit = "implicit"
    client_credentials = "client_credentials"


class PreventUserExistenceErrorTypes(str):
    LEGACY = "LEGACY"
    ENABLED = "ENABLED"


class RecoveryOptionNameType(str):
    verified_email = "verified_email"
    verified_phone_number = "verified_phone_number"
    admin_only = "admin_only"


class RiskDecisionType(str):
    NoRisk = "NoRisk"
    AccountTakeover = "AccountTakeover"
    Block = "Block"


class RiskLevelType(str):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class StatusType(str):
    Enabled = "Enabled"
    Disabled = "Disabled"


class TimeUnitsType(str):
    seconds = "seconds"
    minutes = "minutes"
    hours = "hours"
    days = "days"


class UserImportJobStatusType(str):
    Created = "Created"
    Pending = "Pending"
    InProgress = "InProgress"
    Stopping = "Stopping"
    Expired = "Expired"
    Stopped = "Stopped"
    Failed = "Failed"
    Succeeded = "Succeeded"


class UserPoolMfaType(str):
    OFF = "OFF"
    ON = "ON"
    OPTIONAL = "OPTIONAL"


class UserStatusType(str):
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    ARCHIVED = "ARCHIVED"
    COMPROMISED = "COMPROMISED"
    UNKNOWN = "UNKNOWN"
    RESET_REQUIRED = "RESET_REQUIRED"
    FORCE_CHANGE_PASSWORD = "FORCE_CHANGE_PASSWORD"


class UsernameAttributeType(str):
    phone_number = "phone_number"
    email = "email"


class VerifiedAttributeType(str):
    phone_number = "phone_number"
    email = "email"


class VerifySoftwareTokenResponseType(str):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class AliasExistsException(ServiceException):
    """This exception is thrown when a user tries to confirm the account with
    an email or phone number that has already been supplied as an alias from
    a different account. This exception tells user that an account with this
    email or phone already exists.
    """

    message: Optional[MessageType]


class CodeDeliveryFailureException(ServiceException):
    """This exception is thrown when a verification code fails to deliver
    successfully.
    """

    message: Optional[MessageType]


class CodeMismatchException(ServiceException):
    """This exception is thrown if the provided code doesn't match what the
    server was expecting.
    """

    message: Optional[MessageType]


class ConcurrentModificationException(ServiceException):
    """This exception is thrown if two or more modifications are happening
    concurrently.
    """

    message: Optional[MessageType]


class DuplicateProviderException(ServiceException):
    """This exception is thrown when the provider is already supported by the
    user pool.
    """

    message: Optional[MessageType]


class EnableSoftwareTokenMFAException(ServiceException):
    """This exception is thrown when there is a code mismatch and the service
    fails to configure the software token TOTP multi-factor authentication
    (MFA).
    """

    message: Optional[MessageType]


class ExpiredCodeException(ServiceException):
    """This exception is thrown if a code has expired."""

    message: Optional[MessageType]


class GroupExistsException(ServiceException):
    """This exception is thrown when Amazon Cognito encounters a group that
    already exists in the user pool.
    """

    message: Optional[MessageType]


class InternalErrorException(ServiceException):
    """This exception is thrown when Amazon Cognito encounters an internal
    error.
    """

    message: Optional[MessageType]


class InvalidEmailRoleAccessPolicyException(ServiceException):
    """This exception is thrown when Amazon Cognito isn't allowed to use your
    email identity. HTTP status code: 400.
    """

    message: Optional[MessageType]


class InvalidLambdaResponseException(ServiceException):
    """This exception is thrown when Amazon Cognito encounters an invalid
    Lambda response.
    """

    message: Optional[MessageType]


class InvalidOAuthFlowException(ServiceException):
    """This exception is thrown when the specified OAuth flow is not valid."""

    message: Optional[MessageType]


class InvalidParameterException(ServiceException):
    """This exception is thrown when the Amazon Cognito service encounters an
    invalid parameter.
    """

    message: Optional[MessageType]


class InvalidPasswordException(ServiceException):
    """This exception is thrown when Amazon Cognito encounters an invalid
    password.
    """

    message: Optional[MessageType]


class InvalidSmsRoleAccessPolicyException(ServiceException):
    """This exception is returned when the role provided for SMS configuration
    doesn't have permission to publish using Amazon SNS.
    """

    message: Optional[MessageType]


class InvalidSmsRoleTrustRelationshipException(ServiceException):
    """This exception is thrown when the trust relationship is not valid for
    the role provided for SMS configuration. This can happen if you don't
    trust ``cognito-idp.amazonaws.com`` or the external ID provided in the
    role does not match what is provided in the SMS configuration for the
    user pool.
    """

    message: Optional[MessageType]


class InvalidUserPoolConfigurationException(ServiceException):
    """This exception is thrown when the user pool configuration is not valid."""

    message: Optional[MessageType]


class LimitExceededException(ServiceException):
    """This exception is thrown when a user exceeds the limit for a requested
    Amazon Web Services resource.
    """

    message: Optional[MessageType]


class MFAMethodNotFoundException(ServiceException):
    """This exception is thrown when Amazon Cognito can't find a multi-factor
    authentication (MFA) method.
    """

    message: Optional[MessageType]


class NotAuthorizedException(ServiceException):
    """This exception is thrown when a user isn't authorized."""

    message: Optional[MessageType]


class PasswordResetRequiredException(ServiceException):
    """This exception is thrown when a password reset is required."""

    message: Optional[MessageType]


class PreconditionNotMetException(ServiceException):
    """This exception is thrown when a precondition is not met."""

    message: Optional[MessageType]


class ResourceNotFoundException(ServiceException):
    """This exception is thrown when the Amazon Cognito service can't find the
    requested resource.
    """

    message: Optional[MessageType]


class ScopeDoesNotExistException(ServiceException):
    """This exception is thrown when the specified scope doesn't exist."""

    message: Optional[MessageType]


class SoftwareTokenMFANotFoundException(ServiceException):
    """This exception is thrown when the software token time-based one-time
    password (TOTP) multi-factor authentication (MFA) isn't activated for
    the user pool.
    """

    message: Optional[MessageType]


class TooManyFailedAttemptsException(ServiceException):
    """This exception is thrown when the user has made too many failed attempts
    for a given action, such as sign-in.
    """

    message: Optional[MessageType]


class TooManyRequestsException(ServiceException):
    """This exception is thrown when the user has made too many requests for a
    given operation.
    """

    message: Optional[MessageType]


class UnauthorizedException(ServiceException):
    """Exception that is thrown when the request isn't authorized. This can
    happen due to an invalid access token in the request.
    """

    message: Optional[MessageType]


class UnexpectedLambdaException(ServiceException):
    """This exception is thrown when Amazon Cognito encounters an unexpected
    exception with Lambda.
    """

    message: Optional[MessageType]


class UnsupportedIdentityProviderException(ServiceException):
    """This exception is thrown when the specified identifier isn't supported."""

    message: Optional[MessageType]


class UnsupportedOperationException(ServiceException):
    """Exception that is thrown when you attempt to perform an operation that
    isn't enabled for the user pool client.
    """

    message: Optional[MessageType]


class UnsupportedTokenTypeException(ServiceException):
    """Exception that is thrown when an unsupported token is passed to an
    operation.
    """

    message: Optional[MessageType]


class UnsupportedUserStateException(ServiceException):
    """The request failed because the user is in an unsupported state."""

    message: Optional[MessageType]


class UserImportInProgressException(ServiceException):
    """This exception is thrown when you're trying to modify a user pool while
    a user import job is in progress for that pool.
    """

    message: Optional[MessageType]


class UserLambdaValidationException(ServiceException):
    """This exception is thrown when the Amazon Cognito service encounters a
    user validation exception with the Lambda service.
    """

    message: Optional[MessageType]


class UserNotConfirmedException(ServiceException):
    """This exception is thrown when a user isn't confirmed successfully."""

    message: Optional[MessageType]


class UserNotFoundException(ServiceException):
    """This exception is thrown when a user isn't found."""

    message: Optional[MessageType]


class UserPoolAddOnNotEnabledException(ServiceException):
    """This exception is thrown when user pool add-ons aren't enabled."""

    message: Optional[MessageType]


class UserPoolTaggingException(ServiceException):
    """This exception is thrown when a user pool tag can't be set or updated."""

    message: Optional[MessageType]


class UsernameExistsException(ServiceException):
    """This exception is thrown when Amazon Cognito encounters a user name that
    already exists in the user pool.
    """

    message: Optional[MessageType]


class RecoveryOptionType(TypedDict, total=False):
    """A map containing a priority as a key, and recovery method name as a
    value.
    """

    Priority: PriorityType
    Name: RecoveryOptionNameType


RecoveryMechanismsType = List[RecoveryOptionType]


class AccountRecoverySettingType(TypedDict, total=False):
    """The data type for ``AccountRecoverySetting``."""

    RecoveryMechanisms: Optional[RecoveryMechanismsType]


class AccountTakeoverActionType(TypedDict, total=False):
    """Account takeover action type."""

    Notify: AccountTakeoverActionNotifyType
    EventAction: AccountTakeoverEventActionType


class AccountTakeoverActionsType(TypedDict, total=False):
    """Account takeover actions type."""

    LowAction: Optional[AccountTakeoverActionType]
    MediumAction: Optional[AccountTakeoverActionType]
    HighAction: Optional[AccountTakeoverActionType]


class NotifyEmailType(TypedDict, total=False):
    """The notify email type."""

    Subject: EmailNotificationSubjectType
    HtmlBody: Optional[EmailNotificationBodyType]
    TextBody: Optional[EmailNotificationBodyType]


class NotifyConfigurationType(TypedDict, total=False):
    """The notify configuration type."""

    From: Optional[StringType]
    ReplyTo: Optional[StringType]
    SourceArn: ArnType
    BlockEmail: Optional[NotifyEmailType]
    NoActionEmail: Optional[NotifyEmailType]
    MfaEmail: Optional[NotifyEmailType]


class AccountTakeoverRiskConfigurationType(TypedDict, total=False):
    """Configuration for mitigation actions and notification for different
    levels of risk detected for a potential account takeover.
    """

    NotifyConfiguration: Optional[NotifyConfigurationType]
    Actions: AccountTakeoverActionsType


class StringAttributeConstraintsType(TypedDict, total=False):
    """The constraints associated with a string attribute."""

    MinLength: Optional[StringType]
    MaxLength: Optional[StringType]


class NumberAttributeConstraintsType(TypedDict, total=False):
    """The minimum and maximum values of an attribute that is of the number
    data type.
    """

    MinValue: Optional[StringType]
    MaxValue: Optional[StringType]


class SchemaAttributeType(TypedDict, total=False):
    """Contains information about the schema attribute."""

    Name: Optional[CustomAttributeNameType]
    AttributeDataType: Optional[AttributeDataType]
    DeveloperOnlyAttribute: Optional[BooleanType]
    Mutable: Optional[BooleanType]
    Required: Optional[BooleanType]
    NumberAttributeConstraints: Optional[NumberAttributeConstraintsType]
    StringAttributeConstraints: Optional[StringAttributeConstraintsType]


CustomAttributesListType = List[SchemaAttributeType]


class AddCustomAttributesRequest(ServiceRequest):
    """Represents the request to add custom attributes."""

    UserPoolId: UserPoolIdType
    CustomAttributes: CustomAttributesListType


class AddCustomAttributesResponse(TypedDict, total=False):
    """Represents the response from the server for the request to add custom
    attributes.
    """


class AdminAddUserToGroupRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Username: UsernameType
    GroupName: GroupNameType


ClientMetadataType = Dict[StringType, StringType]


class AdminConfirmSignUpRequest(ServiceRequest):
    """Represents the request to confirm user registration."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    ClientMetadata: Optional[ClientMetadataType]


class AdminConfirmSignUpResponse(TypedDict, total=False):
    """Represents the response from the server for the request to confirm
    registration.
    """


class MessageTemplateType(TypedDict, total=False):
    """The message template structure."""

    SMSMessage: Optional[SmsVerificationMessageType]
    EmailMessage: Optional[EmailVerificationMessageType]
    EmailSubject: Optional[EmailVerificationSubjectType]


class AdminCreateUserConfigType(TypedDict, total=False):
    """The configuration for creating a new user profile."""

    AllowAdminCreateUserOnly: Optional[BooleanType]
    UnusedAccountValidityDays: Optional[AdminCreateUserUnusedAccountValidityDaysType]
    InviteMessageTemplate: Optional[MessageTemplateType]


DeliveryMediumListType = List[DeliveryMediumType]


class AttributeType(TypedDict, total=False):
    """Specifies whether the attribute is standard or custom."""

    Name: AttributeNameType
    Value: Optional[AttributeValueType]


AttributeListType = List[AttributeType]


class AdminCreateUserRequest(ServiceRequest):
    """Represents the request to create a user in the specified user pool."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    UserAttributes: Optional[AttributeListType]
    ValidationData: Optional[AttributeListType]
    TemporaryPassword: Optional[PasswordType]
    ForceAliasCreation: Optional[ForceAliasCreation]
    MessageAction: Optional[MessageActionType]
    DesiredDeliveryMediums: Optional[DeliveryMediumListType]
    ClientMetadata: Optional[ClientMetadataType]


class MFAOptionType(TypedDict, total=False):
    """*This data type is no longer supported.* Applies only to SMS
    multi-factor authentication (MFA) configurations. Does not apply to
    time-based one-time password (TOTP) software token MFA configurations.
    """

    DeliveryMedium: Optional[DeliveryMediumType]
    AttributeName: Optional[AttributeNameType]


MFAOptionListType = List[MFAOptionType]
DateType = datetime


class UserType(TypedDict, total=False):
    """The user type."""

    Username: Optional[UsernameType]
    Attributes: Optional[AttributeListType]
    UserCreateDate: Optional[DateType]
    UserLastModifiedDate: Optional[DateType]
    Enabled: Optional[BooleanType]
    UserStatus: Optional[UserStatusType]
    MFAOptions: Optional[MFAOptionListType]


class AdminCreateUserResponse(TypedDict, total=False):
    """Represents the response from the server to the request to create the
    user.
    """

    User: Optional[UserType]


AttributeNameListType = List[AttributeNameType]


class AdminDeleteUserAttributesRequest(ServiceRequest):
    """Represents the request to delete user attributes as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    UserAttributeNames: AttributeNameListType


class AdminDeleteUserAttributesResponse(TypedDict, total=False):
    """Represents the response received from the server for a request to delete
    user attributes.
    """


class AdminDeleteUserRequest(ServiceRequest):
    """Represents the request to delete a user as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType


class ProviderUserIdentifierType(TypedDict, total=False):
    """A container for information about an identity provider for a user pool."""

    ProviderName: Optional[ProviderNameType]
    ProviderAttributeName: Optional[StringType]
    ProviderAttributeValue: Optional[StringType]


class AdminDisableProviderForUserRequest(ServiceRequest):
    UserPoolId: StringType
    User: ProviderUserIdentifierType


class AdminDisableProviderForUserResponse(TypedDict, total=False):
    pass


class AdminDisableUserRequest(ServiceRequest):
    """Represents the request to disable the user as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType


class AdminDisableUserResponse(TypedDict, total=False):
    """Represents the response received from the server to disable the user as
    an administrator.
    """


class AdminEnableUserRequest(ServiceRequest):
    """Represents the request that enables the user as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType


class AdminEnableUserResponse(TypedDict, total=False):
    """Represents the response from the server for the request to enable a user
    as an administrator.
    """


class AdminForgetDeviceRequest(ServiceRequest):
    """Sends the forgot device request, as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    DeviceKey: DeviceKeyType


class AdminGetDeviceRequest(ServiceRequest):
    """Represents the request to get the device, as an administrator."""

    DeviceKey: DeviceKeyType
    UserPoolId: UserPoolIdType
    Username: UsernameType


class DeviceType(TypedDict, total=False):
    """The device type."""

    DeviceKey: Optional[DeviceKeyType]
    DeviceAttributes: Optional[AttributeListType]
    DeviceCreateDate: Optional[DateType]
    DeviceLastModifiedDate: Optional[DateType]
    DeviceLastAuthenticatedDate: Optional[DateType]


class AdminGetDeviceResponse(TypedDict, total=False):
    """Gets the device response, as an administrator."""

    Device: DeviceType


class AdminGetUserRequest(ServiceRequest):
    """Represents the request to get the specified user as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType


UserMFASettingListType = List[StringType]


class AdminGetUserResponse(TypedDict, total=False):
    """Represents the response from the server from the request to get the
    specified user as an administrator.
    """

    Username: UsernameType
    UserAttributes: Optional[AttributeListType]
    UserCreateDate: Optional[DateType]
    UserLastModifiedDate: Optional[DateType]
    Enabled: Optional[BooleanType]
    UserStatus: Optional[UserStatusType]
    MFAOptions: Optional[MFAOptionListType]
    PreferredMfaSetting: Optional[StringType]
    UserMFASettingList: Optional[UserMFASettingListType]


class HttpHeader(TypedDict, total=False):
    """The HTTP header."""

    headerName: Optional[StringType]
    headerValue: Optional[StringType]


HttpHeaderList = List[HttpHeader]


class ContextDataType(TypedDict, total=False):
    """Contextual user data type used for evaluating the risk of an unexpected
    event by Amazon Cognito advanced security.
    """

    IpAddress: StringType
    ServerName: StringType
    ServerPath: StringType
    HttpHeaders: HttpHeaderList
    EncodedData: Optional[StringType]


class AnalyticsMetadataType(TypedDict, total=False):
    """An Amazon Pinpoint analytics endpoint.

    An endpoint uniquely identifies a mobile device, email address, or phone
    number that can receive messages from Amazon Pinpoint analytics.

    Amazon Cognito user pools only support sending events to Amazon Pinpoint
    projects in the US East (N. Virginia) us-east-1 Region, regardless of
    the Region where the user pool resides.
    """

    AnalyticsEndpointId: Optional[StringType]


AuthParametersType = Dict[StringType, StringType]


class AdminInitiateAuthRequest(ServiceRequest):
    """Initiates the authorization request, as an administrator."""

    UserPoolId: UserPoolIdType
    ClientId: ClientIdType
    AuthFlow: AuthFlowType
    AuthParameters: Optional[AuthParametersType]
    ClientMetadata: Optional[ClientMetadataType]
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    ContextData: Optional[ContextDataType]


class NewDeviceMetadataType(TypedDict, total=False):
    """The new device metadata type."""

    DeviceKey: Optional[DeviceKeyType]
    DeviceGroupKey: Optional[StringType]


class AuthenticationResultType(TypedDict, total=False):
    """The authentication result."""

    AccessToken: Optional[TokenModelType]
    ExpiresIn: Optional[IntegerType]
    TokenType: Optional[StringType]
    RefreshToken: Optional[TokenModelType]
    IdToken: Optional[TokenModelType]
    NewDeviceMetadata: Optional[NewDeviceMetadataType]


ChallengeParametersType = Dict[StringType, StringType]


class AdminInitiateAuthResponse(TypedDict, total=False):
    """Initiates the authentication response, as an administrator."""

    ChallengeName: Optional[ChallengeNameType]
    Session: Optional[SessionType]
    ChallengeParameters: Optional[ChallengeParametersType]
    AuthenticationResult: Optional[AuthenticationResultType]


class AdminLinkProviderForUserRequest(ServiceRequest):
    UserPoolId: StringType
    DestinationUser: ProviderUserIdentifierType
    SourceUser: ProviderUserIdentifierType


class AdminLinkProviderForUserResponse(TypedDict, total=False):
    pass


class AdminListDevicesRequest(ServiceRequest):
    """Represents the request to list devices, as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    Limit: Optional[QueryLimitType]
    PaginationToken: Optional[SearchPaginationTokenType]


DeviceListType = List[DeviceType]


class AdminListDevicesResponse(TypedDict, total=False):
    """Lists the device's response, as an administrator."""

    Devices: Optional[DeviceListType]
    PaginationToken: Optional[SearchPaginationTokenType]


class AdminListGroupsForUserRequest(ServiceRequest):
    Username: UsernameType
    UserPoolId: UserPoolIdType
    Limit: Optional[QueryLimitType]
    NextToken: Optional[PaginationKey]


class GroupType(TypedDict, total=False):
    """The group type."""

    GroupName: Optional[GroupNameType]
    UserPoolId: Optional[UserPoolIdType]
    Description: Optional[DescriptionType]
    RoleArn: Optional[ArnType]
    Precedence: Optional[PrecedenceType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]


GroupListType = List[GroupType]


class AdminListGroupsForUserResponse(TypedDict, total=False):
    Groups: Optional[GroupListType]
    NextToken: Optional[PaginationKey]


class AdminListUserAuthEventsRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Username: UsernameType
    MaxResults: Optional[QueryLimitType]
    NextToken: Optional[PaginationKey]


class EventFeedbackType(TypedDict, total=False):
    """Specifies the event feedback type."""

    FeedbackValue: FeedbackValueType
    Provider: StringType
    FeedbackDate: Optional[DateType]


class EventContextDataType(TypedDict, total=False):
    """Specifies the user context data captured at the time of an event
    request.
    """

    IpAddress: Optional[StringType]
    DeviceName: Optional[StringType]
    Timezone: Optional[StringType]
    City: Optional[StringType]
    Country: Optional[StringType]


class ChallengeResponseType(TypedDict, total=False):
    """The challenge response type."""

    ChallengeName: Optional[ChallengeName]
    ChallengeResponse: Optional[ChallengeResponse]


ChallengeResponseListType = List[ChallengeResponseType]


class EventRiskType(TypedDict, total=False):
    """The event risk type."""

    RiskDecision: Optional[RiskDecisionType]
    RiskLevel: Optional[RiskLevelType]
    CompromisedCredentialsDetected: Optional[WrappedBooleanType]


class AuthEventType(TypedDict, total=False):
    """The authentication event type."""

    EventId: Optional[StringType]
    EventType: Optional[EventType]
    CreationDate: Optional[DateType]
    EventResponse: Optional[EventResponseType]
    EventRisk: Optional[EventRiskType]
    ChallengeResponses: Optional[ChallengeResponseListType]
    EventContextData: Optional[EventContextDataType]
    EventFeedback: Optional[EventFeedbackType]


AuthEventsType = List[AuthEventType]


class AdminListUserAuthEventsResponse(TypedDict, total=False):
    AuthEvents: Optional[AuthEventsType]
    NextToken: Optional[PaginationKey]


class AdminRemoveUserFromGroupRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Username: UsernameType
    GroupName: GroupNameType


class AdminResetUserPasswordRequest(ServiceRequest):
    """Represents the request to reset a user's password as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    ClientMetadata: Optional[ClientMetadataType]


class AdminResetUserPasswordResponse(TypedDict, total=False):
    """Represents the response from the server to reset a user password as an
    administrator.
    """


ChallengeResponsesType = Dict[StringType, StringType]


class AdminRespondToAuthChallengeRequest(ServiceRequest):
    """The request to respond to the authentication challenge, as an
    administrator.
    """

    UserPoolId: UserPoolIdType
    ClientId: ClientIdType
    ChallengeName: ChallengeNameType
    ChallengeResponses: Optional[ChallengeResponsesType]
    Session: Optional[SessionType]
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    ContextData: Optional[ContextDataType]
    ClientMetadata: Optional[ClientMetadataType]


class AdminRespondToAuthChallengeResponse(TypedDict, total=False):
    """Responds to the authentication challenge, as an administrator."""

    ChallengeName: Optional[ChallengeNameType]
    Session: Optional[SessionType]
    ChallengeParameters: Optional[ChallengeParametersType]
    AuthenticationResult: Optional[AuthenticationResultType]


class SoftwareTokenMfaSettingsType(TypedDict, total=False):
    """The type used for enabling software token MFA at the user level. If an
    MFA type is activated for a user, the user will be prompted for MFA
    during all sign-in attempts, unless device tracking is turned on and the
    device has been trusted. If you want MFA to be applied selectively based
    on the assessed risk level of sign-in attempts, deactivate MFA for users
    and turn on Adaptive Authentication for the user pool.
    """

    Enabled: Optional[BooleanType]
    PreferredMfa: Optional[BooleanType]


class SMSMfaSettingsType(TypedDict, total=False):
    """The type used for enabling SMS multi-factor authentication (MFA) at the
    user level. Phone numbers don't need to be verified to be used for SMS
    MFA. If an MFA type is activated for a user, the user will be prompted
    for MFA during all sign-in attempts, unless device tracking is turned on
    and the device has been trusted. If you would like MFA to be applied
    selectively based on the assessed risk level of sign-in attempts,
    deactivate MFA for users and turn on Adaptive Authentication for the
    user pool.
    """

    Enabled: Optional[BooleanType]
    PreferredMfa: Optional[BooleanType]


class AdminSetUserMFAPreferenceRequest(ServiceRequest):
    SMSMfaSettings: Optional[SMSMfaSettingsType]
    SoftwareTokenMfaSettings: Optional[SoftwareTokenMfaSettingsType]
    Username: UsernameType
    UserPoolId: UserPoolIdType


class AdminSetUserMFAPreferenceResponse(TypedDict, total=False):
    pass


class AdminSetUserPasswordRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Username: UsernameType
    Password: PasswordType
    Permanent: Optional[BooleanType]


class AdminSetUserPasswordResponse(TypedDict, total=False):
    pass


class AdminSetUserSettingsRequest(ServiceRequest):
    """You can use this parameter to set an MFA configuration that uses the SMS
    delivery medium.
    """

    UserPoolId: UserPoolIdType
    Username: UsernameType
    MFAOptions: MFAOptionListType


class AdminSetUserSettingsResponse(TypedDict, total=False):
    """Represents the response from the server to set user settings as an
    administrator.
    """


class AdminUpdateAuthEventFeedbackRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Username: UsernameType
    EventId: EventIdType
    FeedbackValue: FeedbackValueType


class AdminUpdateAuthEventFeedbackResponse(TypedDict, total=False):
    pass


class AdminUpdateDeviceStatusRequest(ServiceRequest):
    """The request to update the device status, as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType
    DeviceKey: DeviceKeyType
    DeviceRememberedStatus: Optional[DeviceRememberedStatusType]


class AdminUpdateDeviceStatusResponse(TypedDict, total=False):
    """The status response to the request to update the device, as an
    administrator.
    """


class AdminUpdateUserAttributesRequest(ServiceRequest):
    """Represents the request to update the user's attributes as an
    administrator.
    """

    UserPoolId: UserPoolIdType
    Username: UsernameType
    UserAttributes: AttributeListType
    ClientMetadata: Optional[ClientMetadataType]


class AdminUpdateUserAttributesResponse(TypedDict, total=False):
    """Represents the response from the server for the request to update user
    attributes as an administrator.
    """


class AdminUserGlobalSignOutRequest(ServiceRequest):
    """The request to sign out of all devices, as an administrator."""

    UserPoolId: UserPoolIdType
    Username: UsernameType


class AdminUserGlobalSignOutResponse(TypedDict, total=False):
    """The global sign-out response, as an administrator."""


AliasAttributesListType = List[AliasAttributeType]


class AnalyticsConfigurationType(TypedDict, total=False):
    """The Amazon Pinpoint analytics configuration for collecting metrics for a
    user pool.

    In Regions where Amazon Pinpointisn't available, user pools only support
    sending events to Amazon Pinpoint projects in us-east-1. In Regions
    where Amazon Pinpoint is available, user pools support sending events to
    Amazon Pinpoint projects within that same Region.
    """

    ApplicationId: Optional[HexStringType]
    ApplicationArn: Optional[ArnType]
    RoleArn: Optional[ArnType]
    ExternalId: Optional[StringType]
    UserDataShared: Optional[BooleanType]


class AssociateSoftwareTokenRequest(ServiceRequest):
    AccessToken: Optional[TokenModelType]
    Session: Optional[SessionType]


class AssociateSoftwareTokenResponse(TypedDict, total=False):
    SecretCode: Optional[SecretCodeType]
    Session: Optional[SessionType]


AttributeMappingType = Dict[AttributeMappingKeyType, StringType]
BlockedIPRangeListType = List[StringType]
CallbackURLsListType = List[RedirectUrlType]


class ChangePasswordRequest(ServiceRequest):
    """Represents the request to change a user password."""

    PreviousPassword: PasswordType
    ProposedPassword: PasswordType
    AccessToken: TokenModelType


class ChangePasswordResponse(TypedDict, total=False):
    """The response from the server to the change password request."""


ClientPermissionListType = List[ClientPermissionType]


class CodeDeliveryDetailsType(TypedDict, total=False):
    """The code delivery details being returned from the server."""

    Destination: Optional[StringType]
    DeliveryMedium: Optional[DeliveryMediumType]
    AttributeName: Optional[AttributeNameType]


CodeDeliveryDetailsListType = List[CodeDeliveryDetailsType]


class CompromisedCredentialsActionsType(TypedDict, total=False):
    """The compromised credentials actions type."""

    EventAction: CompromisedCredentialsEventActionType


EventFiltersType = List[EventFilterType]


class CompromisedCredentialsRiskConfigurationType(TypedDict, total=False):
    """The compromised credentials risk configuration type."""

    EventFilter: Optional[EventFiltersType]
    Actions: CompromisedCredentialsActionsType


class DeviceSecretVerifierConfigType(TypedDict, total=False):
    """The device verifier against which it is authenticated."""

    PasswordVerifier: Optional[StringType]
    Salt: Optional[StringType]


class ConfirmDeviceRequest(ServiceRequest):
    """Confirms the device request."""

    AccessToken: TokenModelType
    DeviceKey: DeviceKeyType
    DeviceSecretVerifierConfig: Optional[DeviceSecretVerifierConfigType]
    DeviceName: Optional[DeviceNameType]


class ConfirmDeviceResponse(TypedDict, total=False):
    """Confirms the device response."""

    UserConfirmationNecessary: Optional[BooleanType]


class UserContextDataType(TypedDict, total=False):
    """Contextual data, such as the user's device fingerprint, IP address, or
    location, used for evaluating the risk of an unexpected event by Amazon
    Cognito advanced security.
    """

    EncodedData: Optional[StringType]


class ConfirmForgotPasswordRequest(ServiceRequest):
    """The request representing the confirmation for a password reset."""

    ClientId: ClientIdType
    SecretHash: Optional[SecretHashType]
    Username: UsernameType
    ConfirmationCode: ConfirmationCodeType
    Password: PasswordType
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    UserContextData: Optional[UserContextDataType]
    ClientMetadata: Optional[ClientMetadataType]


class ConfirmForgotPasswordResponse(TypedDict, total=False):
    """The response from the server that results from a user's request to
    retrieve a forgotten password.
    """


class ConfirmSignUpRequest(ServiceRequest):
    """Represents the request to confirm registration of a user."""

    ClientId: ClientIdType
    SecretHash: Optional[SecretHashType]
    Username: UsernameType
    ConfirmationCode: ConfirmationCodeType
    ForceAliasCreation: Optional[ForceAliasCreation]
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    UserContextData: Optional[UserContextDataType]
    ClientMetadata: Optional[ClientMetadataType]


class ConfirmSignUpResponse(TypedDict, total=False):
    """Represents the response from the server for the registration
    confirmation.
    """


class CreateGroupRequest(ServiceRequest):
    GroupName: GroupNameType
    UserPoolId: UserPoolIdType
    Description: Optional[DescriptionType]
    RoleArn: Optional[ArnType]
    Precedence: Optional[PrecedenceType]


class CreateGroupResponse(TypedDict, total=False):
    Group: Optional[GroupType]


IdpIdentifiersListType = List[IdpIdentifierType]
ProviderDetailsType = Dict[StringType, StringType]


class CreateIdentityProviderRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ProviderName: ProviderNameTypeV1
    ProviderType: IdentityProviderTypeType
    ProviderDetails: ProviderDetailsType
    AttributeMapping: Optional[AttributeMappingType]
    IdpIdentifiers: Optional[IdpIdentifiersListType]


class IdentityProviderType(TypedDict, total=False):
    """A container for information about an identity provider."""

    UserPoolId: Optional[UserPoolIdType]
    ProviderName: Optional[ProviderNameType]
    ProviderType: Optional[IdentityProviderTypeType]
    ProviderDetails: Optional[ProviderDetailsType]
    AttributeMapping: Optional[AttributeMappingType]
    IdpIdentifiers: Optional[IdpIdentifiersListType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]


class CreateIdentityProviderResponse(TypedDict, total=False):
    IdentityProvider: IdentityProviderType


class ResourceServerScopeType(TypedDict, total=False):
    """A resource server scope."""

    ScopeName: ResourceServerScopeNameType
    ScopeDescription: ResourceServerScopeDescriptionType


ResourceServerScopeListType = List[ResourceServerScopeType]


class CreateResourceServerRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Identifier: ResourceServerIdentifierType
    Name: ResourceServerNameType
    Scopes: Optional[ResourceServerScopeListType]


class ResourceServerType(TypedDict, total=False):
    """A container for information about a resource server for a user pool."""

    UserPoolId: Optional[UserPoolIdType]
    Identifier: Optional[ResourceServerIdentifierType]
    Name: Optional[ResourceServerNameType]
    Scopes: Optional[ResourceServerScopeListType]


class CreateResourceServerResponse(TypedDict, total=False):
    ResourceServer: ResourceServerType


class CreateUserImportJobRequest(ServiceRequest):
    """Represents the request to create the user import job."""

    JobName: UserImportJobNameType
    UserPoolId: UserPoolIdType
    CloudWatchLogsRoleArn: ArnType


LongType = int


class UserImportJobType(TypedDict, total=False):
    """The user import job type."""

    JobName: Optional[UserImportJobNameType]
    JobId: Optional[UserImportJobIdType]
    UserPoolId: Optional[UserPoolIdType]
    PreSignedUrl: Optional[PreSignedUrlType]
    CreationDate: Optional[DateType]
    StartDate: Optional[DateType]
    CompletionDate: Optional[DateType]
    Status: Optional[UserImportJobStatusType]
    CloudWatchLogsRoleArn: Optional[ArnType]
    ImportedUsers: Optional[LongType]
    SkippedUsers: Optional[LongType]
    FailedUsers: Optional[LongType]
    CompletionMessage: Optional[CompletionMessageType]


class CreateUserImportJobResponse(TypedDict, total=False):
    """Represents the response from the server to the request to create the
    user import job.
    """

    UserImportJob: Optional[UserImportJobType]


ScopeListType = List[ScopeType]
OAuthFlowsType = List[OAuthFlowType]
LogoutURLsListType = List[RedirectUrlType]
SupportedIdentityProvidersListType = List[ProviderNameType]
ExplicitAuthFlowsListType = List[ExplicitAuthFlowsType]


class TokenValidityUnitsType(TypedDict, total=False):
    """The data type for TokenValidityUnits that specifics the time
    measurements for token validity.
    """

    AccessToken: Optional[TimeUnitsType]
    IdToken: Optional[TimeUnitsType]
    RefreshToken: Optional[TimeUnitsType]


class CreateUserPoolClientRequest(ServiceRequest):
    """Represents the request to create a user pool client."""

    UserPoolId: UserPoolIdType
    ClientName: ClientNameType
    GenerateSecret: Optional[GenerateSecret]
    RefreshTokenValidity: Optional[RefreshTokenValidityType]
    AccessTokenValidity: Optional[AccessTokenValidityType]
    IdTokenValidity: Optional[IdTokenValidityType]
    TokenValidityUnits: Optional[TokenValidityUnitsType]
    ReadAttributes: Optional[ClientPermissionListType]
    WriteAttributes: Optional[ClientPermissionListType]
    ExplicitAuthFlows: Optional[ExplicitAuthFlowsListType]
    SupportedIdentityProviders: Optional[SupportedIdentityProvidersListType]
    CallbackURLs: Optional[CallbackURLsListType]
    LogoutURLs: Optional[LogoutURLsListType]
    DefaultRedirectURI: Optional[RedirectUrlType]
    AllowedOAuthFlows: Optional[OAuthFlowsType]
    AllowedOAuthScopes: Optional[ScopeListType]
    AllowedOAuthFlowsUserPoolClient: Optional[BooleanType]
    AnalyticsConfiguration: Optional[AnalyticsConfigurationType]
    PreventUserExistenceErrors: Optional[PreventUserExistenceErrorTypes]
    EnableTokenRevocation: Optional[WrappedBooleanType]


class UserPoolClientType(TypedDict, total=False):
    """Contains information about a user pool client."""

    UserPoolId: Optional[UserPoolIdType]
    ClientName: Optional[ClientNameType]
    ClientId: Optional[ClientIdType]
    ClientSecret: Optional[ClientSecretType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]
    RefreshTokenValidity: Optional[RefreshTokenValidityType]
    AccessTokenValidity: Optional[AccessTokenValidityType]
    IdTokenValidity: Optional[IdTokenValidityType]
    TokenValidityUnits: Optional[TokenValidityUnitsType]
    ReadAttributes: Optional[ClientPermissionListType]
    WriteAttributes: Optional[ClientPermissionListType]
    ExplicitAuthFlows: Optional[ExplicitAuthFlowsListType]
    SupportedIdentityProviders: Optional[SupportedIdentityProvidersListType]
    CallbackURLs: Optional[CallbackURLsListType]
    LogoutURLs: Optional[LogoutURLsListType]
    DefaultRedirectURI: Optional[RedirectUrlType]
    AllowedOAuthFlows: Optional[OAuthFlowsType]
    AllowedOAuthScopes: Optional[ScopeListType]
    AllowedOAuthFlowsUserPoolClient: Optional[BooleanType]
    AnalyticsConfiguration: Optional[AnalyticsConfigurationType]
    PreventUserExistenceErrors: Optional[PreventUserExistenceErrorTypes]
    EnableTokenRevocation: Optional[WrappedBooleanType]


class CreateUserPoolClientResponse(TypedDict, total=False):
    """Represents the response from the server to create a user pool client."""

    UserPoolClient: Optional[UserPoolClientType]


class CustomDomainConfigType(TypedDict, total=False):
    """The configuration for a custom domain that hosts the sign-up and sign-in
    webpages for your application.
    """

    CertificateArn: ArnType


class CreateUserPoolDomainRequest(ServiceRequest):
    Domain: DomainType
    UserPoolId: UserPoolIdType
    CustomDomainConfig: Optional[CustomDomainConfigType]


class CreateUserPoolDomainResponse(TypedDict, total=False):
    CloudFrontDomain: Optional[DomainType]


class UsernameConfigurationType(TypedDict, total=False):
    """The username configuration type."""

    CaseSensitive: WrappedBooleanType


class UserPoolAddOnsType(TypedDict, total=False):
    """The user pool add-ons type."""

    AdvancedSecurityMode: AdvancedSecurityModeType


SchemaAttributesListType = List[SchemaAttributeType]
UserPoolTagsType = Dict[TagKeysType, TagValueType]


class SmsConfigurationType(TypedDict, total=False):
    """The SMS configuration type is the settings that your Amazon Cognito user
    pool must use to send an SMS message from your Amazon Web Services
    account through Amazon Simple Notification Service. To send SMS messages
    with Amazon SNS in the Amazon Web Services Region that you want, the
    Amazon Cognito user pool uses an Identity and Access Management (IAM)
    role in your Amazon Web Services account.
    """

    SnsCallerArn: ArnType
    ExternalId: Optional[StringType]
    SnsRegion: Optional[RegionCodeType]


class EmailConfigurationType(TypedDict, total=False):
    """The email configuration of your user pool. The email configuration type
    sets your preferred sending method, Amazon Web Services Region, and
    sender for messages from your user pool.

    Amazon Cognito can send email messages with Amazon Simple Email Service
    resources in the Amazon Web Services Region where you created your user
    pool, and in alternate Regions in some cases. For more information on
    the supported Regions, see `Email settings for Amazon Cognito user
    pools <https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-email.html>`__.
    """

    SourceArn: Optional[ArnType]
    ReplyToEmailAddress: Optional[EmailAddressType]
    EmailSendingAccount: Optional[EmailSendingAccountType]
    From: Optional[StringType]
    ConfigurationSet: Optional[SESConfigurationSet]


class DeviceConfigurationType(TypedDict, total=False):
    """The device tracking configuration for a user pool. A user pool with
    device tracking deactivated returns a null value.

    When you provide values for any DeviceConfiguration field, you activate
    device tracking.
    """

    ChallengeRequiredOnNewDevice: Optional[BooleanType]
    DeviceOnlyRememberedOnUserPrompt: Optional[BooleanType]


class VerificationMessageTemplateType(TypedDict, total=False):
    """The template for verification messages."""

    SmsMessage: Optional[SmsVerificationMessageType]
    EmailMessage: Optional[EmailVerificationMessageType]
    EmailSubject: Optional[EmailVerificationSubjectType]
    EmailMessageByLink: Optional[EmailVerificationMessageByLinkType]
    EmailSubjectByLink: Optional[EmailVerificationSubjectByLinkType]
    DefaultEmailOption: Optional[DefaultEmailOptionType]


UsernameAttributesListType = List[UsernameAttributeType]
VerifiedAttributesListType = List[VerifiedAttributeType]


class CustomEmailLambdaVersionConfigType(TypedDict, total=False):
    """A custom email sender Lambda configuration type."""

    LambdaVersion: CustomEmailSenderLambdaVersionType
    LambdaArn: ArnType


class CustomSMSLambdaVersionConfigType(TypedDict, total=False):
    """A custom SMS sender Lambda configuration type."""

    LambdaVersion: CustomSMSSenderLambdaVersionType
    LambdaArn: ArnType


class LambdaConfigType(TypedDict, total=False):
    """Specifies the configuration for Lambda triggers."""

    PreSignUp: Optional[ArnType]
    CustomMessage: Optional[ArnType]
    PostConfirmation: Optional[ArnType]
    PreAuthentication: Optional[ArnType]
    PostAuthentication: Optional[ArnType]
    DefineAuthChallenge: Optional[ArnType]
    CreateAuthChallenge: Optional[ArnType]
    VerifyAuthChallengeResponse: Optional[ArnType]
    PreTokenGeneration: Optional[ArnType]
    UserMigration: Optional[ArnType]
    CustomSMSSender: Optional[CustomSMSLambdaVersionConfigType]
    CustomEmailSender: Optional[CustomEmailLambdaVersionConfigType]
    KMSKeyID: Optional[ArnType]


class PasswordPolicyType(TypedDict, total=False):
    """The password policy type."""

    MinimumLength: Optional[PasswordPolicyMinLengthType]
    RequireUppercase: Optional[BooleanType]
    RequireLowercase: Optional[BooleanType]
    RequireNumbers: Optional[BooleanType]
    RequireSymbols: Optional[BooleanType]
    TemporaryPasswordValidityDays: Optional[TemporaryPasswordValidityDaysType]


class UserPoolPolicyType(TypedDict, total=False):
    """The policy associated with a user pool."""

    PasswordPolicy: Optional[PasswordPolicyType]


class CreateUserPoolRequest(ServiceRequest):
    """Represents the request to create a user pool."""

    PoolName: UserPoolNameType
    Policies: Optional[UserPoolPolicyType]
    LambdaConfig: Optional[LambdaConfigType]
    AutoVerifiedAttributes: Optional[VerifiedAttributesListType]
    AliasAttributes: Optional[AliasAttributesListType]
    UsernameAttributes: Optional[UsernameAttributesListType]
    SmsVerificationMessage: Optional[SmsVerificationMessageType]
    EmailVerificationMessage: Optional[EmailVerificationMessageType]
    EmailVerificationSubject: Optional[EmailVerificationSubjectType]
    VerificationMessageTemplate: Optional[VerificationMessageTemplateType]
    SmsAuthenticationMessage: Optional[SmsVerificationMessageType]
    MfaConfiguration: Optional[UserPoolMfaType]
    DeviceConfiguration: Optional[DeviceConfigurationType]
    EmailConfiguration: Optional[EmailConfigurationType]
    SmsConfiguration: Optional[SmsConfigurationType]
    UserPoolTags: Optional[UserPoolTagsType]
    AdminCreateUserConfig: Optional[AdminCreateUserConfigType]
    Schema: Optional[SchemaAttributesListType]
    UserPoolAddOns: Optional[UserPoolAddOnsType]
    UsernameConfiguration: Optional[UsernameConfigurationType]
    AccountRecoverySetting: Optional[AccountRecoverySettingType]


class UserPoolType(TypedDict, total=False):
    """A container for information about the user pool."""

    Id: Optional[UserPoolIdType]
    Name: Optional[UserPoolNameType]
    Policies: Optional[UserPoolPolicyType]
    LambdaConfig: Optional[LambdaConfigType]
    Status: Optional[StatusType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]
    SchemaAttributes: Optional[SchemaAttributesListType]
    AutoVerifiedAttributes: Optional[VerifiedAttributesListType]
    AliasAttributes: Optional[AliasAttributesListType]
    UsernameAttributes: Optional[UsernameAttributesListType]
    SmsVerificationMessage: Optional[SmsVerificationMessageType]
    EmailVerificationMessage: Optional[EmailVerificationMessageType]
    EmailVerificationSubject: Optional[EmailVerificationSubjectType]
    VerificationMessageTemplate: Optional[VerificationMessageTemplateType]
    SmsAuthenticationMessage: Optional[SmsVerificationMessageType]
    MfaConfiguration: Optional[UserPoolMfaType]
    DeviceConfiguration: Optional[DeviceConfigurationType]
    EstimatedNumberOfUsers: Optional[IntegerType]
    EmailConfiguration: Optional[EmailConfigurationType]
    SmsConfiguration: Optional[SmsConfigurationType]
    UserPoolTags: Optional[UserPoolTagsType]
    SmsConfigurationFailure: Optional[StringType]
    EmailConfigurationFailure: Optional[StringType]
    Domain: Optional[DomainType]
    CustomDomain: Optional[DomainType]
    AdminCreateUserConfig: Optional[AdminCreateUserConfigType]
    UserPoolAddOns: Optional[UserPoolAddOnsType]
    UsernameConfiguration: Optional[UsernameConfigurationType]
    Arn: Optional[ArnType]
    AccountRecoverySetting: Optional[AccountRecoverySettingType]


class CreateUserPoolResponse(TypedDict, total=False):
    """Represents the response from the server for the request to create a user
    pool.
    """

    UserPool: Optional[UserPoolType]


class DeleteGroupRequest(ServiceRequest):
    GroupName: GroupNameType
    UserPoolId: UserPoolIdType


class DeleteIdentityProviderRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ProviderName: ProviderNameType


class DeleteResourceServerRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Identifier: ResourceServerIdentifierType


class DeleteUserAttributesRequest(ServiceRequest):
    """Represents the request to delete user attributes."""

    UserAttributeNames: AttributeNameListType
    AccessToken: TokenModelType


class DeleteUserAttributesResponse(TypedDict, total=False):
    """Represents the response from the server to delete user attributes."""


class DeleteUserPoolClientRequest(ServiceRequest):
    """Represents the request to delete a user pool client."""

    UserPoolId: UserPoolIdType
    ClientId: ClientIdType


class DeleteUserPoolDomainRequest(ServiceRequest):
    Domain: DomainType
    UserPoolId: UserPoolIdType


class DeleteUserPoolDomainResponse(TypedDict, total=False):
    pass


class DeleteUserPoolRequest(ServiceRequest):
    """Represents the request to delete a user pool."""

    UserPoolId: UserPoolIdType


class DeleteUserRequest(ServiceRequest):
    """Represents the request to delete a user."""

    AccessToken: TokenModelType


class DescribeIdentityProviderRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ProviderName: ProviderNameType


class DescribeIdentityProviderResponse(TypedDict, total=False):
    IdentityProvider: IdentityProviderType


class DescribeResourceServerRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Identifier: ResourceServerIdentifierType


class DescribeResourceServerResponse(TypedDict, total=False):
    ResourceServer: ResourceServerType


class DescribeRiskConfigurationRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ClientId: Optional[ClientIdType]


SkippedIPRangeListType = List[StringType]


class RiskExceptionConfigurationType(TypedDict, total=False):
    """The type of the configuration to override the risk decision."""

    BlockedIPRangeList: Optional[BlockedIPRangeListType]
    SkippedIPRangeList: Optional[SkippedIPRangeListType]


class RiskConfigurationType(TypedDict, total=False):
    """The risk configuration type."""

    UserPoolId: Optional[UserPoolIdType]
    ClientId: Optional[ClientIdType]
    CompromisedCredentialsRiskConfiguration: Optional[CompromisedCredentialsRiskConfigurationType]
    AccountTakeoverRiskConfiguration: Optional[AccountTakeoverRiskConfigurationType]
    RiskExceptionConfiguration: Optional[RiskExceptionConfigurationType]
    LastModifiedDate: Optional[DateType]


class DescribeRiskConfigurationResponse(TypedDict, total=False):
    RiskConfiguration: RiskConfigurationType


class DescribeUserImportJobRequest(ServiceRequest):
    """Represents the request to describe the user import job."""

    UserPoolId: UserPoolIdType
    JobId: UserImportJobIdType


class DescribeUserImportJobResponse(TypedDict, total=False):
    """Represents the response from the server to the request to describe the
    user import job.
    """

    UserImportJob: Optional[UserImportJobType]


class DescribeUserPoolClientRequest(ServiceRequest):
    """Represents the request to describe a user pool client."""

    UserPoolId: UserPoolIdType
    ClientId: ClientIdType


class DescribeUserPoolClientResponse(TypedDict, total=False):
    """Represents the response from the server from a request to describe the
    user pool client.
    """

    UserPoolClient: Optional[UserPoolClientType]


class DescribeUserPoolDomainRequest(ServiceRequest):
    Domain: DomainType


class DomainDescriptionType(TypedDict, total=False):
    """A container for information about a domain."""

    UserPoolId: Optional[UserPoolIdType]
    AWSAccountId: Optional[AWSAccountIdType]
    Domain: Optional[DomainType]
    S3Bucket: Optional[S3BucketType]
    CloudFrontDistribution: Optional[StringType]
    Version: Optional[DomainVersionType]
    Status: Optional[DomainStatusType]
    CustomDomainConfig: Optional[CustomDomainConfigType]


class DescribeUserPoolDomainResponse(TypedDict, total=False):
    DomainDescription: Optional[DomainDescriptionType]


class DescribeUserPoolRequest(ServiceRequest):
    """Represents the request to describe the user pool."""

    UserPoolId: UserPoolIdType


class DescribeUserPoolResponse(TypedDict, total=False):
    """Represents the response to describe the user pool."""

    UserPool: Optional[UserPoolType]


class ForgetDeviceRequest(ServiceRequest):
    """Represents the request to forget the device."""

    AccessToken: Optional[TokenModelType]
    DeviceKey: DeviceKeyType


class ForgotPasswordRequest(ServiceRequest):
    """Represents the request to reset a user's password."""

    ClientId: ClientIdType
    SecretHash: Optional[SecretHashType]
    UserContextData: Optional[UserContextDataType]
    Username: UsernameType
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    ClientMetadata: Optional[ClientMetadataType]


class ForgotPasswordResponse(TypedDict, total=False):
    """Respresents the response from the server regarding the request to reset
    a password.
    """

    CodeDeliveryDetails: Optional[CodeDeliveryDetailsType]


class GetCSVHeaderRequest(ServiceRequest):
    """Represents the request to get the header information of the CSV file for
    the user import job.
    """

    UserPoolId: UserPoolIdType


ListOfStringTypes = List[StringType]


class GetCSVHeaderResponse(TypedDict, total=False):
    """Represents the response from the server to the request to get the header
    information of the CSV file for the user import job.
    """

    UserPoolId: Optional[UserPoolIdType]
    CSVHeader: Optional[ListOfStringTypes]


class GetDeviceRequest(ServiceRequest):
    """Represents the request to get the device."""

    DeviceKey: DeviceKeyType
    AccessToken: Optional[TokenModelType]


class GetDeviceResponse(TypedDict, total=False):
    """Gets the device response."""

    Device: DeviceType


class GetGroupRequest(ServiceRequest):
    GroupName: GroupNameType
    UserPoolId: UserPoolIdType


class GetGroupResponse(TypedDict, total=False):
    Group: Optional[GroupType]


class GetIdentityProviderByIdentifierRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    IdpIdentifier: IdpIdentifierType


class GetIdentityProviderByIdentifierResponse(TypedDict, total=False):
    IdentityProvider: IdentityProviderType


class GetSigningCertificateRequest(ServiceRequest):
    """Request to get a signing certificate from Amazon Cognito."""

    UserPoolId: UserPoolIdType


class GetSigningCertificateResponse(TypedDict, total=False):
    """Response from Amazon Cognito for a signing certificate request."""

    Certificate: Optional[StringType]


class GetUICustomizationRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ClientId: Optional[ClientIdType]


class UICustomizationType(TypedDict, total=False):
    """A container for the UI customization information for a user pool's
    built-in app UI.
    """

    UserPoolId: Optional[UserPoolIdType]
    ClientId: Optional[ClientIdType]
    ImageUrl: Optional[ImageUrlType]
    CSS: Optional[CSSType]
    CSSVersion: Optional[CSSVersionType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]


class GetUICustomizationResponse(TypedDict, total=False):
    UICustomization: UICustomizationType


class GetUserAttributeVerificationCodeRequest(ServiceRequest):
    """Represents the request to get user attribute verification."""

    AccessToken: TokenModelType
    AttributeName: AttributeNameType
    ClientMetadata: Optional[ClientMetadataType]


class GetUserAttributeVerificationCodeResponse(TypedDict, total=False):
    """The verification code response returned by the server response to get
    the user attribute verification code.
    """

    CodeDeliveryDetails: Optional[CodeDeliveryDetailsType]


class GetUserPoolMfaConfigRequest(ServiceRequest):
    UserPoolId: UserPoolIdType


class SoftwareTokenMfaConfigType(TypedDict, total=False):
    """The type used for enabling software token MFA at the user pool level."""

    Enabled: Optional[BooleanType]


class SmsMfaConfigType(TypedDict, total=False):
    """The SMS text message multi-factor authentication (MFA) configuration
    type.
    """

    SmsAuthenticationMessage: Optional[SmsVerificationMessageType]
    SmsConfiguration: Optional[SmsConfigurationType]


class GetUserPoolMfaConfigResponse(TypedDict, total=False):
    SmsMfaConfiguration: Optional[SmsMfaConfigType]
    SoftwareTokenMfaConfiguration: Optional[SoftwareTokenMfaConfigType]
    MfaConfiguration: Optional[UserPoolMfaType]


class GetUserRequest(ServiceRequest):
    """Represents the request to get information about the user."""

    AccessToken: TokenModelType


class GetUserResponse(TypedDict, total=False):
    """Represents the response from the server from the request to get
    information about the user.
    """

    Username: UsernameType
    UserAttributes: AttributeListType
    MFAOptions: Optional[MFAOptionListType]
    PreferredMfaSetting: Optional[StringType]
    UserMFASettingList: Optional[UserMFASettingListType]


class GlobalSignOutRequest(ServiceRequest):
    """Represents the request to sign out all devices."""

    AccessToken: TokenModelType


class GlobalSignOutResponse(TypedDict, total=False):
    """The response to the request to sign out all devices."""


ImageFileType = bytes


class InitiateAuthRequest(ServiceRequest):
    """Initiates the authentication request."""

    AuthFlow: AuthFlowType
    AuthParameters: Optional[AuthParametersType]
    ClientMetadata: Optional[ClientMetadataType]
    ClientId: ClientIdType
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    UserContextData: Optional[UserContextDataType]


class InitiateAuthResponse(TypedDict, total=False):
    """Initiates the authentication response."""

    ChallengeName: Optional[ChallengeNameType]
    Session: Optional[SessionType]
    ChallengeParameters: Optional[ChallengeParametersType]
    AuthenticationResult: Optional[AuthenticationResultType]


class ListDevicesRequest(ServiceRequest):
    """Represents the request to list the devices."""

    AccessToken: TokenModelType
    Limit: Optional[QueryLimitType]
    PaginationToken: Optional[SearchPaginationTokenType]


class ListDevicesResponse(TypedDict, total=False):
    """Represents the response to list devices."""

    Devices: Optional[DeviceListType]
    PaginationToken: Optional[SearchPaginationTokenType]


class ListGroupsRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Limit: Optional[QueryLimitType]
    NextToken: Optional[PaginationKey]


class ListGroupsResponse(TypedDict, total=False):
    Groups: Optional[GroupListType]
    NextToken: Optional[PaginationKey]


class ListIdentityProvidersRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    MaxResults: Optional[ListProvidersLimitType]
    NextToken: Optional[PaginationKeyType]


class ProviderDescription(TypedDict, total=False):
    """A container for identity provider details."""

    ProviderName: Optional[ProviderNameType]
    ProviderType: Optional[IdentityProviderTypeType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]


ProvidersListType = List[ProviderDescription]


class ListIdentityProvidersResponse(TypedDict, total=False):
    Providers: ProvidersListType
    NextToken: Optional[PaginationKeyType]


class ListResourceServersRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    MaxResults: Optional[ListResourceServersLimitType]
    NextToken: Optional[PaginationKeyType]


ResourceServersListType = List[ResourceServerType]


class ListResourceServersResponse(TypedDict, total=False):
    ResourceServers: ResourceServersListType
    NextToken: Optional[PaginationKeyType]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceArn: ArnType


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[UserPoolTagsType]


class ListUserImportJobsRequest(ServiceRequest):
    """Represents the request to list the user import jobs."""

    UserPoolId: UserPoolIdType
    MaxResults: PoolQueryLimitType
    PaginationToken: Optional[PaginationKeyType]


UserImportJobsListType = List[UserImportJobType]


class ListUserImportJobsResponse(TypedDict, total=False):
    """Represents the response from the server to the request to list the user
    import jobs.
    """

    UserImportJobs: Optional[UserImportJobsListType]
    PaginationToken: Optional[PaginationKeyType]


class ListUserPoolClientsRequest(ServiceRequest):
    """Represents the request to list the user pool clients."""

    UserPoolId: UserPoolIdType
    MaxResults: Optional[QueryLimit]
    NextToken: Optional[PaginationKey]


class UserPoolClientDescription(TypedDict, total=False):
    """The description of the user pool client."""

    ClientId: Optional[ClientIdType]
    UserPoolId: Optional[UserPoolIdType]
    ClientName: Optional[ClientNameType]


UserPoolClientListType = List[UserPoolClientDescription]


class ListUserPoolClientsResponse(TypedDict, total=False):
    """Represents the response from the server that lists user pool clients."""

    UserPoolClients: Optional[UserPoolClientListType]
    NextToken: Optional[PaginationKey]


class ListUserPoolsRequest(ServiceRequest):
    """Represents the request to list user pools."""

    NextToken: Optional[PaginationKeyType]
    MaxResults: PoolQueryLimitType


class UserPoolDescriptionType(TypedDict, total=False):
    """A user pool description."""

    Id: Optional[UserPoolIdType]
    Name: Optional[UserPoolNameType]
    LambdaConfig: Optional[LambdaConfigType]
    Status: Optional[StatusType]
    LastModifiedDate: Optional[DateType]
    CreationDate: Optional[DateType]


UserPoolListType = List[UserPoolDescriptionType]


class ListUserPoolsResponse(TypedDict, total=False):
    """Represents the response to list user pools."""

    UserPools: Optional[UserPoolListType]
    NextToken: Optional[PaginationKeyType]


class ListUsersInGroupRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    GroupName: GroupNameType
    Limit: Optional[QueryLimitType]
    NextToken: Optional[PaginationKey]


UsersListType = List[UserType]


class ListUsersInGroupResponse(TypedDict, total=False):
    Users: Optional[UsersListType]
    NextToken: Optional[PaginationKey]


SearchedAttributeNamesListType = List[AttributeNameType]


class ListUsersRequest(ServiceRequest):
    """Represents the request to list users."""

    UserPoolId: UserPoolIdType
    AttributesToGet: Optional[SearchedAttributeNamesListType]
    Limit: Optional[QueryLimitType]
    PaginationToken: Optional[SearchPaginationTokenType]
    Filter: Optional[UserFilterType]


class ListUsersResponse(TypedDict, total=False):
    """The response from the request to list users."""

    Users: Optional[UsersListType]
    PaginationToken: Optional[SearchPaginationTokenType]


class ResendConfirmationCodeRequest(ServiceRequest):
    """Represents the request to resend the confirmation code."""

    ClientId: ClientIdType
    SecretHash: Optional[SecretHashType]
    UserContextData: Optional[UserContextDataType]
    Username: UsernameType
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    ClientMetadata: Optional[ClientMetadataType]


class ResendConfirmationCodeResponse(TypedDict, total=False):
    """The response from the server when Amazon Cognito makes the request to
    resend a confirmation code.
    """

    CodeDeliveryDetails: Optional[CodeDeliveryDetailsType]


class RespondToAuthChallengeRequest(ServiceRequest):
    """The request to respond to an authentication challenge."""

    ClientId: ClientIdType
    ChallengeName: ChallengeNameType
    Session: Optional[SessionType]
    ChallengeResponses: Optional[ChallengeResponsesType]
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    UserContextData: Optional[UserContextDataType]
    ClientMetadata: Optional[ClientMetadataType]


class RespondToAuthChallengeResponse(TypedDict, total=False):
    """The response to respond to the authentication challenge."""

    ChallengeName: Optional[ChallengeNameType]
    Session: Optional[SessionType]
    ChallengeParameters: Optional[ChallengeParametersType]
    AuthenticationResult: Optional[AuthenticationResultType]


class RevokeTokenRequest(ServiceRequest):
    Token: TokenModelType
    ClientId: ClientIdType
    ClientSecret: Optional[ClientSecretType]


class RevokeTokenResponse(TypedDict, total=False):
    pass


class SetRiskConfigurationRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ClientId: Optional[ClientIdType]
    CompromisedCredentialsRiskConfiguration: Optional[CompromisedCredentialsRiskConfigurationType]
    AccountTakeoverRiskConfiguration: Optional[AccountTakeoverRiskConfigurationType]
    RiskExceptionConfiguration: Optional[RiskExceptionConfigurationType]


class SetRiskConfigurationResponse(TypedDict, total=False):
    RiskConfiguration: RiskConfigurationType


class SetUICustomizationRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ClientId: Optional[ClientIdType]
    CSS: Optional[CSSType]
    ImageFile: Optional[ImageFileType]


class SetUICustomizationResponse(TypedDict, total=False):
    UICustomization: UICustomizationType


class SetUserMFAPreferenceRequest(ServiceRequest):
    SMSMfaSettings: Optional[SMSMfaSettingsType]
    SoftwareTokenMfaSettings: Optional[SoftwareTokenMfaSettingsType]
    AccessToken: TokenModelType


class SetUserMFAPreferenceResponse(TypedDict, total=False):
    pass


class SetUserPoolMfaConfigRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    SmsMfaConfiguration: Optional[SmsMfaConfigType]
    SoftwareTokenMfaConfiguration: Optional[SoftwareTokenMfaConfigType]
    MfaConfiguration: Optional[UserPoolMfaType]


class SetUserPoolMfaConfigResponse(TypedDict, total=False):
    SmsMfaConfiguration: Optional[SmsMfaConfigType]
    SoftwareTokenMfaConfiguration: Optional[SoftwareTokenMfaConfigType]
    MfaConfiguration: Optional[UserPoolMfaType]


class SetUserSettingsRequest(ServiceRequest):
    """Represents the request to set user settings."""

    AccessToken: TokenModelType
    MFAOptions: MFAOptionListType


class SetUserSettingsResponse(TypedDict, total=False):
    """The response from the server for a set user settings request."""


class SignUpRequest(ServiceRequest):
    """Represents the request to register a user."""

    ClientId: ClientIdType
    SecretHash: Optional[SecretHashType]
    Username: UsernameType
    Password: PasswordType
    UserAttributes: Optional[AttributeListType]
    ValidationData: Optional[AttributeListType]
    AnalyticsMetadata: Optional[AnalyticsMetadataType]
    UserContextData: Optional[UserContextDataType]
    ClientMetadata: Optional[ClientMetadataType]


class SignUpResponse(TypedDict, total=False):
    """The response from the server for a registration request."""

    UserConfirmed: BooleanType
    CodeDeliveryDetails: Optional[CodeDeliveryDetailsType]
    UserSub: StringType


class StartUserImportJobRequest(ServiceRequest):
    """Represents the request to start the user import job."""

    UserPoolId: UserPoolIdType
    JobId: UserImportJobIdType


class StartUserImportJobResponse(TypedDict, total=False):
    """Represents the response from the server to the request to start the user
    import job.
    """

    UserImportJob: Optional[UserImportJobType]


class StopUserImportJobRequest(ServiceRequest):
    """Represents the request to stop the user import job."""

    UserPoolId: UserPoolIdType
    JobId: UserImportJobIdType


class StopUserImportJobResponse(TypedDict, total=False):
    """Represents the response from the server to the request to stop the user
    import job.
    """

    UserImportJob: Optional[UserImportJobType]


class TagResourceRequest(ServiceRequest):
    ResourceArn: ArnType
    Tags: UserPoolTagsType


class TagResourceResponse(TypedDict, total=False):
    pass


UserPoolTagsListType = List[TagKeysType]


class UntagResourceRequest(ServiceRequest):
    ResourceArn: ArnType
    TagKeys: UserPoolTagsListType


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateAuthEventFeedbackRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Username: UsernameType
    EventId: EventIdType
    FeedbackToken: TokenModelType
    FeedbackValue: FeedbackValueType


class UpdateAuthEventFeedbackResponse(TypedDict, total=False):
    pass


class UpdateDeviceStatusRequest(ServiceRequest):
    """Represents the request to update the device status."""

    AccessToken: TokenModelType
    DeviceKey: DeviceKeyType
    DeviceRememberedStatus: Optional[DeviceRememberedStatusType]


class UpdateDeviceStatusResponse(TypedDict, total=False):
    """The response to the request to update the device status."""


class UpdateGroupRequest(ServiceRequest):
    GroupName: GroupNameType
    UserPoolId: UserPoolIdType
    Description: Optional[DescriptionType]
    RoleArn: Optional[ArnType]
    Precedence: Optional[PrecedenceType]


class UpdateGroupResponse(TypedDict, total=False):
    Group: Optional[GroupType]


class UpdateIdentityProviderRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    ProviderName: ProviderNameType
    ProviderDetails: Optional[ProviderDetailsType]
    AttributeMapping: Optional[AttributeMappingType]
    IdpIdentifiers: Optional[IdpIdentifiersListType]


class UpdateIdentityProviderResponse(TypedDict, total=False):
    IdentityProvider: IdentityProviderType


class UpdateResourceServerRequest(ServiceRequest):
    UserPoolId: UserPoolIdType
    Identifier: ResourceServerIdentifierType
    Name: ResourceServerNameType
    Scopes: Optional[ResourceServerScopeListType]


class UpdateResourceServerResponse(TypedDict, total=False):
    ResourceServer: ResourceServerType


class UpdateUserAttributesRequest(ServiceRequest):
    """Represents the request to update user attributes."""

    UserAttributes: AttributeListType
    AccessToken: TokenModelType
    ClientMetadata: Optional[ClientMetadataType]


class UpdateUserAttributesResponse(TypedDict, total=False):
    """Represents the response from the server for the request to update user
    attributes.
    """

    CodeDeliveryDetailsList: Optional[CodeDeliveryDetailsListType]


class UpdateUserPoolClientRequest(ServiceRequest):
    """Represents the request to update the user pool client."""

    UserPoolId: UserPoolIdType
    ClientId: ClientIdType
    ClientName: Optional[ClientNameType]
    RefreshTokenValidity: Optional[RefreshTokenValidityType]
    AccessTokenValidity: Optional[AccessTokenValidityType]
    IdTokenValidity: Optional[IdTokenValidityType]
    TokenValidityUnits: Optional[TokenValidityUnitsType]
    ReadAttributes: Optional[ClientPermissionListType]
    WriteAttributes: Optional[ClientPermissionListType]
    ExplicitAuthFlows: Optional[ExplicitAuthFlowsListType]
    SupportedIdentityProviders: Optional[SupportedIdentityProvidersListType]
    CallbackURLs: Optional[CallbackURLsListType]
    LogoutURLs: Optional[LogoutURLsListType]
    DefaultRedirectURI: Optional[RedirectUrlType]
    AllowedOAuthFlows: Optional[OAuthFlowsType]
    AllowedOAuthScopes: Optional[ScopeListType]
    AllowedOAuthFlowsUserPoolClient: Optional[BooleanType]
    AnalyticsConfiguration: Optional[AnalyticsConfigurationType]
    PreventUserExistenceErrors: Optional[PreventUserExistenceErrorTypes]
    EnableTokenRevocation: Optional[WrappedBooleanType]


class UpdateUserPoolClientResponse(TypedDict, total=False):
    """Represents the response from the server to the request to update the
    user pool client.
    """

    UserPoolClient: Optional[UserPoolClientType]


class UpdateUserPoolDomainRequest(ServiceRequest):
    """The UpdateUserPoolDomain request input."""

    Domain: DomainType
    UserPoolId: UserPoolIdType
    CustomDomainConfig: CustomDomainConfigType


class UpdateUserPoolDomainResponse(TypedDict, total=False):
    """The UpdateUserPoolDomain response output."""

    CloudFrontDomain: Optional[DomainType]


class UpdateUserPoolRequest(ServiceRequest):
    """Represents the request to update the user pool."""

    UserPoolId: UserPoolIdType
    Policies: Optional[UserPoolPolicyType]
    LambdaConfig: Optional[LambdaConfigType]
    AutoVerifiedAttributes: Optional[VerifiedAttributesListType]
    SmsVerificationMessage: Optional[SmsVerificationMessageType]
    EmailVerificationMessage: Optional[EmailVerificationMessageType]
    EmailVerificationSubject: Optional[EmailVerificationSubjectType]
    VerificationMessageTemplate: Optional[VerificationMessageTemplateType]
    SmsAuthenticationMessage: Optional[SmsVerificationMessageType]
    MfaConfiguration: Optional[UserPoolMfaType]
    DeviceConfiguration: Optional[DeviceConfigurationType]
    EmailConfiguration: Optional[EmailConfigurationType]
    SmsConfiguration: Optional[SmsConfigurationType]
    UserPoolTags: Optional[UserPoolTagsType]
    AdminCreateUserConfig: Optional[AdminCreateUserConfigType]
    UserPoolAddOns: Optional[UserPoolAddOnsType]
    AccountRecoverySetting: Optional[AccountRecoverySettingType]


class UpdateUserPoolResponse(TypedDict, total=False):
    """Represents the response from the server when you make a request to
    update the user pool.
    """


class VerifySoftwareTokenRequest(ServiceRequest):
    AccessToken: Optional[TokenModelType]
    Session: Optional[SessionType]
    UserCode: SoftwareTokenMFAUserCodeType
    FriendlyDeviceName: Optional[StringType]


class VerifySoftwareTokenResponse(TypedDict, total=False):
    Status: Optional[VerifySoftwareTokenResponseType]
    Session: Optional[SessionType]


class VerifyUserAttributeRequest(ServiceRequest):
    """Represents the request to verify user attributes."""

    AccessToken: TokenModelType
    AttributeName: AttributeNameType
    Code: ConfirmationCodeType


class VerifyUserAttributeResponse(TypedDict, total=False):
    """A container representing the response from the server from the request
    to verify user attributes.
    """


class CognitoIdpApi:

    service = "cognito-idp"
    version = "2016-04-18"

    @handler("AddCustomAttributes")
    def add_custom_attributes(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        custom_attributes: CustomAttributesListType,
    ) -> AddCustomAttributesResponse:
        """Adds additional user attributes to the user pool schema.

        :param user_pool_id: The user pool ID for the user pool where you want to add custom
        attributes.
        :param custom_attributes: An array of custom attributes, such as Mutable and Name.
        :returns: AddCustomAttributesResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserImportInProgressException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminAddUserToGroup")
    def admin_add_user_to_group(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        group_name: GroupNameType,
    ) -> None:
        """Adds the specified user to the specified group.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool.
        :param username: The username for the user.
        :param group_name: The group name.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminConfirmSignUp")
    def admin_confirm_sign_up(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        client_metadata: ClientMetadataType = None,
    ) -> AdminConfirmSignUpResponse:
        """Confirms user registration as an admin without using a confirmation
        code. Works on any user.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for which you want to confirm user registration.
        :param username: The user name for which you want to confirm user registration.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: AdminConfirmSignUpResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises NotAuthorizedException:
        :raises TooManyFailedAttemptsException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminCreateUser")
    def admin_create_user(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        user_attributes: AttributeListType = None,
        validation_data: AttributeListType = None,
        temporary_password: PasswordType = None,
        force_alias_creation: ForceAliasCreation = None,
        message_action: MessageActionType = None,
        desired_delivery_mediums: DeliveryMediumListType = None,
        client_metadata: ClientMetadataType = None,
    ) -> AdminCreateUserResponse:
        """Creates a new user in the specified user pool.

        If ``MessageAction`` isn't set, the default is to send a welcome message
        via email or phone (SMS).

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        This message is based on a template that you configured in your call to
        create or update a user pool. This template includes your custom sign-up
        instructions and placeholders for user name and temporary password.

        Alternatively, you can call ``AdminCreateUser`` with ``SUPPRESS`` for
        the ``MessageAction`` parameter, and Amazon Cognito won't send any
        email.

        In either case, the user will be in the ``FORCE_CHANGE_PASSWORD`` state
        until they sign in and change their password.

        ``AdminCreateUser`` requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where the user will be created.
        :param username: The username for the user.
        :param user_attributes: An array of name-value pairs that contain user attributes and attribute
        values to be set for the user to be created.
        :param validation_data: The user's validation data.
        :param temporary_password: The user's temporary password.
        :param force_alias_creation: This parameter is used only if the ``phone_number_verified`` or
        ``email_verified`` attribute is set to ``True``.
        :param message_action: Set to ``RESEND`` to resend the invitation message to a user that
        already exists and reset the expiration limit on the user's account.
        :param desired_delivery_mediums: Specify ``"EMAIL"`` if email will be used to send the welcome message.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: AdminCreateUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UserNotFoundException:
        :raises UsernameExistsException:
        :raises InvalidPasswordException:
        :raises CodeDeliveryFailureException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises PreconditionNotMetException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UnsupportedUserStateException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminDeleteUser")
    def admin_delete_user(
        self, context: RequestContext, user_pool_id: UserPoolIdType, username: UsernameType
    ) -> None:
        """Deletes a user as an administrator. Works on any user.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to delete the user.
        :param username: The user name of the user you want to delete.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminDeleteUserAttributes")
    def admin_delete_user_attributes(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        user_attribute_names: AttributeNameListType,
    ) -> AdminDeleteUserAttributesResponse:
        """Deletes the user attributes in a user pool as an administrator. Works on
        any user.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to delete user
        attributes.
        :param username: The user name of the user from which you would like to delete
        attributes.
        :param user_attribute_names: An array of strings representing the user attribute names you want to
        delete.
        :returns: AdminDeleteUserAttributesResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminDisableProviderForUser")
    def admin_disable_provider_for_user(
        self, context: RequestContext, user_pool_id: StringType, user: ProviderUserIdentifierType
    ) -> AdminDisableProviderForUserResponse:
        """Prevents the user from signing in with the specified external (SAML or
        social) identity provider. If the user that you want to deactivate is a
        Amazon Cognito user pools native username + password user, they can't
        use their password to sign in. If the user to deactivate is a linked
        external identity provider (IdP) user, any link between that user and an
        existing user is removed. When the external user signs in again, and the
        user is no longer attached to the previously linked ``DestinationUser``,
        the user must create a new user account. See
        `AdminLinkProviderForUser <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminLinkProviderForUser.html>`__.

        This action is enabled only for admin access and requires developer
        credentials.

        The ``ProviderName`` must match the value specified when creating an IdP
        for the pool.

        To deactivate a native username + password user, the ``ProviderName``
        value must be ``Cognito`` and the ``ProviderAttributeName`` must be
        ``Cognito_Subject``. The ``ProviderAttributeValue`` must be the name
        that is used in the user pool for the user.

        The ``ProviderAttributeName`` must always be ``Cognito_Subject`` for
        social identity providers. The ``ProviderAttributeValue`` must always be
        the exact subject that was used when the user was originally linked as a
        source user.

        For de-linking a SAML identity, there are two scenarios. If the linked
        identity has not yet been used to sign in, the ``ProviderAttributeName``
        and ``ProviderAttributeValue`` must be the same values that were used
        for the ``SourceUser`` when the identities were originally linked using
        ``AdminLinkProviderForUser`` call. (If the linking was done with
        ``ProviderAttributeName`` set to ``Cognito_Subject``, the same applies
        here). However, if the user has already signed in, the
        ``ProviderAttributeName`` must be ``Cognito_Subject`` and
        ``ProviderAttributeValue`` must be the subject of the SAML assertion.

        :param user_pool_id: The user pool ID for the user pool.
        :param user: The user to be disabled.
        :returns: AdminDisableProviderForUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises AliasExistsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminDisableUser")
    def admin_disable_user(
        self, context: RequestContext, user_pool_id: UserPoolIdType, username: UsernameType
    ) -> AdminDisableUserResponse:
        """Disables the specified user.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to disable the user.
        :param username: The user name of the user you want to disable.
        :returns: AdminDisableUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminEnableUser")
    def admin_enable_user(
        self, context: RequestContext, user_pool_id: UserPoolIdType, username: UsernameType
    ) -> AdminEnableUserResponse:
        """Enables the specified user as an administrator. Works on any user.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to enable the user.
        :param username: The user name of the user you want to enable.
        :returns: AdminEnableUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminForgetDevice")
    def admin_forget_device(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        device_key: DeviceKeyType,
    ) -> None:
        """Forgets the device, as an administrator.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID.
        :param username: The user name.
        :param device_key: The device key.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminGetDevice")
    def admin_get_device(
        self,
        context: RequestContext,
        device_key: DeviceKeyType,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
    ) -> AdminGetDeviceResponse:
        """Gets the device, as an administrator.

        Calling this action requires developer credentials.

        :param device_key: The device key.
        :param user_pool_id: The user pool ID.
        :param username: The user name.
        :returns: AdminGetDeviceResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises NotAuthorizedException:
        """
        raise NotImplementedError

    @handler("AdminGetUser")
    def admin_get_user(
        self, context: RequestContext, user_pool_id: UserPoolIdType, username: UsernameType
    ) -> AdminGetUserResponse:
        """Gets the specified user by user name in a user pool as an administrator.
        Works on any user.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to get information
        about the user.
        :param username: The user name of the user you want to retrieve.
        :returns: AdminGetUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminInitiateAuth")
    def admin_initiate_auth(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        client_id: ClientIdType,
        auth_flow: AuthFlowType,
        auth_parameters: AuthParametersType = None,
        client_metadata: ClientMetadataType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        context_data: ContextDataType = None,
    ) -> AdminInitiateAuthResponse:
        """Initiates the authentication flow, as an administrator.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        Calling this action requires developer credentials.

        :param user_pool_id: The ID of the Amazon Cognito user pool.
        :param client_id: The app client ID.
        :param auth_flow: The authentication flow for this call to run.
        :param auth_parameters: The authentication parameters.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for
        certain custom workflows that this action triggers.
        :param analytics_metadata: The analytics metadata for collecting Amazon Pinpoint metrics for
        ``AdminInitiateAuth`` calls.
        :param context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :returns: AdminInitiateAuthResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises UnexpectedLambdaException:
        :raises InvalidUserPoolConfigurationException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises MFAMethodNotFoundException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        """
        raise NotImplementedError

    @handler("AdminLinkProviderForUser")
    def admin_link_provider_for_user(
        self,
        context: RequestContext,
        user_pool_id: StringType,
        destination_user: ProviderUserIdentifierType,
        source_user: ProviderUserIdentifierType,
    ) -> AdminLinkProviderForUserResponse:
        """Links an existing user account in a user pool (``DestinationUser``) to
        an identity from an external identity provider (``SourceUser``) based on
        a specified attribute name and value from the external identity
        provider. This allows you to create a link from the existing user
        account to an external federated user identity that has not yet been
        used to sign in. You can then use the federated user identity to sign in
        as the existing user account.

        For example, if there is an existing user with a username and password,
        this API links that user to a federated user identity. When the user
        signs in with a federated user identity, they sign in as the existing
        user account.

        The maximum number of federated identities linked to a user is 5.

        Because this API allows a user with an external federated identity to
        sign in as an existing user in the user pool, it is critical that it
        only be used with external identity providers and provider attributes
        that have been trusted by the application owner.

        This action is administrative and requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool.
        :param destination_user: The existing user in the user pool that you want to assign to the
        external identity provider user account.
        :param source_user: An external identity provider account for a user who doesn't exist yet
        in the user pool.
        :returns: AdminLinkProviderForUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises AliasExistsException:
        :raises LimitExceededException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminListDevices")
    def admin_list_devices(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        limit: QueryLimitType = None,
        pagination_token: SearchPaginationTokenType = None,
    ) -> AdminListDevicesResponse:
        """Lists devices, as an administrator.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID.
        :param username: The user name.
        :param limit: The limit of the devices request.
        :param pagination_token: The pagination token.
        :returns: AdminListDevicesResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises NotAuthorizedException:
        """
        raise NotImplementedError

    @handler("AdminListGroupsForUser")
    def admin_list_groups_for_user(
        self,
        context: RequestContext,
        username: UsernameType,
        user_pool_id: UserPoolIdType,
        limit: QueryLimitType = None,
        next_token: PaginationKey = None,
    ) -> AdminListGroupsForUserResponse:
        """Lists the groups that the user belongs to.

        Calling this action requires developer credentials.

        :param username: The username for the user.
        :param user_pool_id: The user pool ID for the user pool.
        :param limit: The limit of the request to list groups.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: AdminListGroupsForUserResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminListUserAuthEvents")
    def admin_list_user_auth_events(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        max_results: QueryLimitType = None,
        next_token: PaginationKey = None,
    ) -> AdminListUserAuthEventsResponse:
        """A history of user activity and any risks detected as part of Amazon
        Cognito advanced security.

        :param user_pool_id: The user pool ID.
        :param username: The user pool username or an alias.
        :param max_results: The maximum number of authentication events to return.
        :param next_token: A pagination token.
        :returns: AdminListUserAuthEventsResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises UserPoolAddOnNotEnabledException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminRemoveUserFromGroup")
    def admin_remove_user_from_group(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        group_name: GroupNameType,
    ) -> None:
        """Removes the specified user from the specified group.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool.
        :param username: The username for the user.
        :param group_name: The group name.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminResetUserPassword")
    def admin_reset_user_password(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        client_metadata: ClientMetadataType = None,
    ) -> AdminResetUserPasswordResponse:
        """Resets the specified user's password in a user pool as an administrator.
        Works on any user.

        When a developer calls this API, the current password is invalidated, so
        it must be changed. If a user tries to sign in after the API is called,
        the app will get a PasswordResetRequiredException exception back and
        should direct the user down the flow to reset the password, which is the
        same as the forgot password flow. In addition, if the user pool has
        phone verification selected and a verified phone number exists for the
        user, or if email verification is selected and a verified email exists
        for the user, calling this API will also result in sending a message to
        the end user with the code to change their password.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to reset the user's
        password.
        :param username: The user name of the user whose password you want to reset.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: AdminResetUserPasswordResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises NotAuthorizedException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises UserNotFoundException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminRespondToAuthChallenge")
    def admin_respond_to_auth_challenge(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        client_id: ClientIdType,
        challenge_name: ChallengeNameType,
        challenge_responses: ChallengeResponsesType = None,
        session: SessionType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        context_data: ContextDataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> AdminRespondToAuthChallengeResponse:
        """Responds to an authentication challenge, as an administrator.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        Calling this action requires developer credentials.

        :param user_pool_id: The ID of the Amazon Cognito user pool.
        :param client_id: The app client ID.
        :param challenge_name: The challenge name.
        :param challenge_responses: The challenge responses.
        :param session: The session that should be passed both ways in challenge-response calls
        to the service.
        :param analytics_metadata: The analytics metadata for collecting Amazon Pinpoint metrics for
        ``AdminRespondToAuthChallenge`` calls.
        :param context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: AdminRespondToAuthChallengeResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises CodeMismatchException:
        :raises ExpiredCodeException:
        :raises UnexpectedLambdaException:
        :raises InvalidPasswordException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises InvalidUserPoolConfigurationException:
        :raises InternalErrorException:
        :raises MFAMethodNotFoundException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises AliasExistsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises SoftwareTokenMFANotFoundException:
        """
        raise NotImplementedError

    @handler("AdminSetUserMFAPreference")
    def admin_set_user_mfa_preference(
        self,
        context: RequestContext,
        username: UsernameType,
        user_pool_id: UserPoolIdType,
        sms_mfa_settings: SMSMfaSettingsType = None,
        software_token_mfa_settings: SoftwareTokenMfaSettingsType = None,
    ) -> AdminSetUserMFAPreferenceResponse:
        """The user's multi-factor authentication (MFA) preference, including which
        MFA options are activated, and if any are preferred. Only one factor can
        be set as preferred. The preferred MFA factor will be used to
        authenticate a user if multiple factors are activated. If multiple
        options are activated and no preference is set, a challenge to choose an
        MFA option will be returned during sign-in.

        :param username: The user pool username or alias.
        :param user_pool_id: The user pool ID.
        :param sms_mfa_settings: The SMS text message MFA settings.
        :param software_token_mfa_settings: The time-based one-time password software token MFA settings.
        :returns: AdminSetUserMFAPreferenceResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminSetUserPassword")
    def admin_set_user_password(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        password: PasswordType,
        permanent: BooleanType = None,
    ) -> AdminSetUserPasswordResponse:
        """Sets the specified user's password in a user pool as an administrator.
        Works on any user.

        The password can be temporary or permanent. If it is temporary, the user
        status enters the ``FORCE_CHANGE_PASSWORD`` state. When the user next
        tries to sign in, the InitiateAuth/AdminInitiateAuth response will
        contain the ``NEW_PASSWORD_REQUIRED`` challenge. If the user doesn't
        sign in before it expires, the user won't be able to sign in, and an
        administrator must reset their password.

        Once the user has set a new password, or the password is permanent, the
        user status is set to ``Confirmed``.

        :param user_pool_id: The user pool ID for the user pool where you want to set the user's
        password.
        :param username: The user name of the user whose password you want to set.
        :param password: The password for the user.
        :param permanent: ``True`` if the password is permanent, ``False`` if it is temporary.
        :returns: AdminSetUserPasswordResponse
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        :raises TooManyRequestsException:
        :raises InvalidParameterException:
        :raises InvalidPasswordException:
        """
        raise NotImplementedError

    @handler("AdminSetUserSettings")
    def admin_set_user_settings(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        mfa_options: MFAOptionListType,
    ) -> AdminSetUserSettingsResponse:
        """*This action is no longer supported.* You can use it to configure only
        SMS MFA. You can't use it to configure time-based one-time password
        (TOTP) software token MFA. To configure either type of MFA, use
        `AdminSetUserMFAPreference <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminSetUserMFAPreference.html>`__
        instead.

        :param user_pool_id: The ID of the user pool that contains the user whose options you're
        setting.
        :param username: The user name of the user whose options you're setting.
        :param mfa_options: You can use this parameter only to set an SMS configuration that uses
        SMS for delivery.
        :returns: AdminSetUserSettingsResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminUpdateAuthEventFeedback")
    def admin_update_auth_event_feedback(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        event_id: EventIdType,
        feedback_value: FeedbackValueType,
    ) -> AdminUpdateAuthEventFeedbackResponse:
        """Provides feedback for an authentication event indicating if it was from
        a valid user. This feedback is used for improving the risk evaluation
        decision for the user pool as part of Amazon Cognito advanced security.

        :param user_pool_id: The user pool ID.
        :param username: The user pool username.
        :param event_id: The authentication event ID.
        :param feedback_value: The authentication event feedback value.
        :returns: AdminUpdateAuthEventFeedbackResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises UserPoolAddOnNotEnabledException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminUpdateDeviceStatus")
    def admin_update_device_status(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        device_key: DeviceKeyType,
        device_remembered_status: DeviceRememberedStatusType = None,
    ) -> AdminUpdateDeviceStatusResponse:
        """Updates the device status as an administrator.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID.
        :param username: The user name.
        :param device_key: The device key.
        :param device_remembered_status: The status indicating whether a device has been remembered or not.
        :returns: AdminUpdateDeviceStatusResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AdminUpdateUserAttributes")
    def admin_update_user_attributes(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        user_attributes: AttributeListType,
        client_metadata: ClientMetadataType = None,
    ) -> AdminUpdateUserAttributesResponse:
        """Updates the specified user's attributes, including developer attributes,
        as an administrator. Works on any user.

        For custom attributes, you must prepend the ``custom:`` prefix to the
        attribute name.

        In addition to updating user attributes, this API can also be used to
        mark phone and email as verified.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool where you want to update user
        attributes.
        :param username: The user name of the user for whom you want to update user attributes.
        :param user_attributes: An array of name-value pairs representing user attributes.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: AdminUpdateUserAttributesResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises AliasExistsException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        """
        raise NotImplementedError

    @handler("AdminUserGlobalSignOut")
    def admin_user_global_sign_out(
        self, context: RequestContext, user_pool_id: UserPoolIdType, username: UsernameType
    ) -> AdminUserGlobalSignOutResponse:
        """Signs out users from all devices, as an administrator. It also
        invalidates all refresh tokens issued to a user. The user's current
        access and Id tokens remain valid until their expiry. Access and Id
        tokens expire one hour after they're issued.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID.
        :param username: The user name.
        :returns: AdminUserGlobalSignOutResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("AssociateSoftwareToken")
    def associate_software_token(
        self,
        context: RequestContext,
        access_token: TokenModelType = None,
        session: SessionType = None,
    ) -> AssociateSoftwareTokenResponse:
        """Returns a unique generated shared secret key code for the user account.
        The request takes an access token or a session string, but not both.

        Calling AssociateSoftwareToken immediately disassociates the existing
        software token from the user account. If the user doesn't subsequently
        verify the software token, their account is set up to authenticate
        without MFA. If MFA config is set to Optional at the user pool level,
        the user can then log in without MFA. However, if MFA is set to Required
        for the user pool, the user is asked to set up a new software token MFA
        during sign-in.

        :param access_token: The access token.
        :param session: The session that should be passed both ways in challenge-response calls
        to the service.
        :returns: AssociateSoftwareTokenResponse
        :raises ConcurrentModificationException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises ResourceNotFoundException:
        :raises InternalErrorException:
        :raises SoftwareTokenMFANotFoundException:
        """
        raise NotImplementedError

    @handler("ChangePassword")
    def change_password(
        self,
        context: RequestContext,
        previous_password: PasswordType,
        proposed_password: PasswordType,
        access_token: TokenModelType,
    ) -> ChangePasswordResponse:
        """Changes the password for a specified user in a user pool.

        :param previous_password: The old password.
        :param proposed_password: The new password.
        :param access_token: The access token.
        :returns: ChangePasswordResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises InvalidPasswordException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ConfirmDevice")
    def confirm_device(
        self,
        context: RequestContext,
        access_token: TokenModelType,
        device_key: DeviceKeyType,
        device_secret_verifier_config: DeviceSecretVerifierConfigType = None,
        device_name: DeviceNameType = None,
    ) -> ConfirmDeviceResponse:
        """Confirms tracking of the device. This API call is the call that begins
        device tracking.

        :param access_token: The access token.
        :param device_key: The device key.
        :param device_secret_verifier_config: The configuration of the device secret verifier.
        :param device_name: The device name.
        :returns: ConfirmDeviceResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises InvalidPasswordException:
        :raises InvalidLambdaResponseException:
        :raises UsernameExistsException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ConfirmForgotPassword")
    def confirm_forgot_password(
        self,
        context: RequestContext,
        client_id: ClientIdType,
        username: UsernameType,
        confirmation_code: ConfirmationCodeType,
        password: PasswordType,
        secret_hash: SecretHashType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        user_context_data: UserContextDataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> ConfirmForgotPasswordResponse:
        """Allows a user to enter a confirmation code to reset a forgotten
        password.

        :param client_id: The app client ID of the app associated with the user pool.
        :param username: The user name of the user for whom you want to enter a code to retrieve
        a forgotten password.
        :param confirmation_code: The confirmation code sent by a user's request to retrieve a forgotten
        password.
        :param password: The password sent by a user's request to retrieve a forgotten password.
        :param secret_hash: A keyed-hash message authentication code (HMAC) calculated using the
        secret key of a user pool client and username plus the client ID in the
        message.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``ConfirmForgotPassword`` calls.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: ConfirmForgotPasswordResponse
        :raises ResourceNotFoundException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises InvalidParameterException:
        :raises InvalidPasswordException:
        :raises NotAuthorizedException:
        :raises CodeMismatchException:
        :raises ExpiredCodeException:
        :raises TooManyFailedAttemptsException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ConfirmSignUp")
    def confirm_sign_up(
        self,
        context: RequestContext,
        client_id: ClientIdType,
        username: UsernameType,
        confirmation_code: ConfirmationCodeType,
        secret_hash: SecretHashType = None,
        force_alias_creation: ForceAliasCreation = None,
        analytics_metadata: AnalyticsMetadataType = None,
        user_context_data: UserContextDataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> ConfirmSignUpResponse:
        """Confirms registration of a user and handles the existing alias from a
        previous user.

        :param client_id: The ID of the app client associated with the user pool.
        :param username: The user name of the user whose registration you want to confirm.
        :param confirmation_code: The confirmation code sent by a user's request to confirm registration.
        :param secret_hash: A keyed-hash message authentication code (HMAC) calculated using the
        secret key of a user pool client and username plus the client ID in the
        message.
        :param force_alias_creation: Boolean to be specified to force user confirmation irrespective of
        existing alias.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``ConfirmSignUp`` calls.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: ConfirmSignUpResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises NotAuthorizedException:
        :raises TooManyFailedAttemptsException:
        :raises CodeMismatchException:
        :raises ExpiredCodeException:
        :raises InvalidLambdaResponseException:
        :raises AliasExistsException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateGroup")
    def create_group(
        self,
        context: RequestContext,
        group_name: GroupNameType,
        user_pool_id: UserPoolIdType,
        description: DescriptionType = None,
        role_arn: ArnType = None,
        precedence: PrecedenceType = None,
    ) -> CreateGroupResponse:
        """Creates a new group in the specified user pool.

        Calling this action requires developer credentials.

        :param group_name: The name of the group.
        :param user_pool_id: The user pool ID for the user pool.
        :param description: A string containing the description of the group.
        :param role_arn: The role Amazon Resource Name (ARN) for the group.
        :param precedence: A non-negative integer value that specifies the precedence of this group
        relative to the other groups that a user can belong to in the user pool.
        :returns: CreateGroupResponse
        :raises InvalidParameterException:
        :raises GroupExistsException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateIdentityProvider")
    def create_identity_provider(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        provider_name: ProviderNameTypeV1,
        provider_type: IdentityProviderTypeType,
        provider_details: ProviderDetailsType,
        attribute_mapping: AttributeMappingType = None,
        idp_identifiers: IdpIdentifiersListType = None,
    ) -> CreateIdentityProviderResponse:
        """Creates an identity provider for a user pool.

        :param user_pool_id: The user pool ID.
        :param provider_name: The identity provider name.
        :param provider_type: The identity provider type.
        :param provider_details: The identity provider details.
        :param attribute_mapping: A mapping of identity provider attributes to standard and custom user
        pool attributes.
        :param idp_identifiers: A list of identity provider identifiers.
        :returns: CreateIdentityProviderResponse
        :raises InvalidParameterException:
        :raises DuplicateProviderException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateResourceServer")
    def create_resource_server(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        identifier: ResourceServerIdentifierType,
        name: ResourceServerNameType,
        scopes: ResourceServerScopeListType = None,
    ) -> CreateResourceServerResponse:
        """Creates a new OAuth2.0 resource server and defines custom scopes within
        it.

        :param user_pool_id: The user pool ID for the user pool.
        :param identifier: A unique resource server identifier for the resource server.
        :param name: A friendly name for the resource server.
        :param scopes: A list of scopes.
        :returns: CreateResourceServerResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateUserImportJob")
    def create_user_import_job(
        self,
        context: RequestContext,
        job_name: UserImportJobNameType,
        user_pool_id: UserPoolIdType,
        cloud_watch_logs_role_arn: ArnType,
    ) -> CreateUserImportJobResponse:
        """Creates the user import job.

        :param job_name: The job name for the user import job.
        :param user_pool_id: The user pool ID for the user pool that the users are being imported
        into.
        :param cloud_watch_logs_role_arn: The role ARN for the Amazon CloudWatch Logs Logging role for the user
        import job.
        :returns: CreateUserImportJobResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises PreconditionNotMetException:
        :raises NotAuthorizedException:
        :raises LimitExceededException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateUserPool")
    def create_user_pool(
        self,
        context: RequestContext,
        pool_name: UserPoolNameType,
        policies: UserPoolPolicyType = None,
        lambda_config: LambdaConfigType = None,
        auto_verified_attributes: VerifiedAttributesListType = None,
        alias_attributes: AliasAttributesListType = None,
        username_attributes: UsernameAttributesListType = None,
        sms_verification_message: SmsVerificationMessageType = None,
        email_verification_message: EmailVerificationMessageType = None,
        email_verification_subject: EmailVerificationSubjectType = None,
        verification_message_template: VerificationMessageTemplateType = None,
        sms_authentication_message: SmsVerificationMessageType = None,
        mfa_configuration: UserPoolMfaType = None,
        device_configuration: DeviceConfigurationType = None,
        email_configuration: EmailConfigurationType = None,
        sms_configuration: SmsConfigurationType = None,
        user_pool_tags: UserPoolTagsType = None,
        admin_create_user_config: AdminCreateUserConfigType = None,
        schema: SchemaAttributesListType = None,
        user_pool_add_ons: UserPoolAddOnsType = None,
        username_configuration: UsernameConfigurationType = None,
        account_recovery_setting: AccountRecoverySettingType = None,
    ) -> CreateUserPoolResponse:
        """Creates a new Amazon Cognito user pool and sets the password policy for
        the pool.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param pool_name: A string used to name the user pool.
        :param policies: The policies associated with the new user pool.
        :param lambda_config: The Lambda trigger configuration information for the new user pool.
        :param auto_verified_attributes: The attributes to be auto-verified.
        :param alias_attributes: Attributes supported as an alias for this user pool.
        :param username_attributes: Specifies whether a user can use an email address or phone number as a
        username when they sign up.
        :param sms_verification_message: A string representing the SMS verification message.
        :param email_verification_message: A string representing the email verification message.
        :param email_verification_subject: A string representing the email verification subject.
        :param verification_message_template: The template for the verification message that the user sees when the
        app requests permission to access the user's information.
        :param sms_authentication_message: A string representing the SMS authentication message.
        :param mfa_configuration: Specifies MFA configuration details.
        :param device_configuration: The device configuration.
        :param email_configuration: The email configuration of your user pool.
        :param sms_configuration: The SMS configuration with the settings that your Amazon Cognito user
        pool must use to send an SMS message from your Amazon Web Services
        account through Amazon Simple Notification Service.
        :param user_pool_tags: The tag keys and values to assign to the user pool.
        :param admin_create_user_config: The configuration for ``AdminCreateUser`` requests.
        :param schema: An array of schema attributes for the new user pool.
        :param user_pool_add_ons: Enables advanced security risk detection.
        :param username_configuration: Case sensitivity on the username input for the selected sign-in option.
        :param account_recovery_setting: The available verified method a user can use to recover their password
        when they call ``ForgotPassword``.
        :returns: CreateUserPoolResponse
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises NotAuthorizedException:
        :raises UserPoolTaggingException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateUserPoolClient")
    def create_user_pool_client(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        client_name: ClientNameType,
        generate_secret: GenerateSecret = None,
        refresh_token_validity: RefreshTokenValidityType = None,
        access_token_validity: AccessTokenValidityType = None,
        id_token_validity: IdTokenValidityType = None,
        token_validity_units: TokenValidityUnitsType = None,
        read_attributes: ClientPermissionListType = None,
        write_attributes: ClientPermissionListType = None,
        explicit_auth_flows: ExplicitAuthFlowsListType = None,
        supported_identity_providers: SupportedIdentityProvidersListType = None,
        callback_urls: CallbackURLsListType = None,
        logout_urls: LogoutURLsListType = None,
        default_redirect_uri: RedirectUrlType = None,
        allowed_o_auth_flows: OAuthFlowsType = None,
        allowed_o_auth_scopes: ScopeListType = None,
        allowed_o_auth_flows_user_pool_client: BooleanType = None,
        analytics_configuration: AnalyticsConfigurationType = None,
        prevent_user_existence_errors: PreventUserExistenceErrorTypes = None,
        enable_token_revocation: WrappedBooleanType = None,
    ) -> CreateUserPoolClientResponse:
        """Creates the user pool client.

        When you create a new user pool client, token revocation is
        automatically activated. For more information about revoking tokens, see
        `RevokeToken <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_RevokeToken.html>`__.

        :param user_pool_id: The user pool ID for the user pool where you want to create a user pool
        client.
        :param client_name: The client name for the user pool client you would like to create.
        :param generate_secret: Boolean to specify whether you want to generate a secret for the user
        pool client being created.
        :param refresh_token_validity: The time limit, in days, after which the refresh token is no longer
        valid and can't be used.
        :param access_token_validity: The time limit, between 5 minutes and 1 day, after which the access
        token is no longer valid and can't be used.
        :param id_token_validity: The time limit, between 5 minutes and 1 day, after which the access
        token is no longer valid and can't be used.
        :param token_validity_units: The units in which the validity times are represented.
        :param read_attributes: The read attributes.
        :param write_attributes: The user pool attributes that the app client can write to.
        :param explicit_auth_flows: The authentication flows that are supported by the user pool clients.
        :param supported_identity_providers: A list of provider names for the identity providers that are supported
        on this client.
        :param callback_urls: A list of allowed redirect (callback) URLs for the identity providers.
        :param logout_urls: A list of allowed logout URLs for the identity providers.
        :param default_redirect_uri: The default redirect URI.
        :param allowed_o_auth_flows: The allowed OAuth flows.
        :param allowed_o_auth_scopes: The allowed OAuth scopes.
        :param allowed_o_auth_flows_user_pool_client: Set to true if the client is allowed to follow the OAuth protocol when
        interacting with Amazon Cognito user pools.
        :param analytics_configuration: The user pool analytics configuration for collecting metrics and sending
        them to your Amazon Pinpoint campaign.
        :param prevent_user_existence_errors: Errors and responses that you want Amazon Cognito APIs to return during
        authentication, account confirmation, and password recovery when the
        user doesn't exist in the user pool.
        :param enable_token_revocation: Activates or deactivates token revocation.
        :returns: CreateUserPoolClientResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises NotAuthorizedException:
        :raises ScopeDoesNotExistException:
        :raises InvalidOAuthFlowException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("CreateUserPoolDomain")
    def create_user_pool_domain(
        self,
        context: RequestContext,
        domain: DomainType,
        user_pool_id: UserPoolIdType,
        custom_domain_config: CustomDomainConfigType = None,
    ) -> CreateUserPoolDomainResponse:
        """Creates a new domain for a user pool.

        :param domain: The domain string.
        :param user_pool_id: The user pool ID.
        :param custom_domain_config: The configuration for a custom domain that hosts the sign-up and sign-in
        webpages for your application.
        :returns: CreateUserPoolDomainResponse
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteGroup")
    def delete_group(
        self, context: RequestContext, group_name: GroupNameType, user_pool_id: UserPoolIdType
    ) -> None:
        """Deletes a group.

        Calling this action requires developer credentials.

        :param group_name: The name of the group.
        :param user_pool_id: The user pool ID for the user pool.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteIdentityProvider")
    def delete_identity_provider(
        self, context: RequestContext, user_pool_id: UserPoolIdType, provider_name: ProviderNameType
    ) -> None:
        """Deletes an identity provider for a user pool.

        :param user_pool_id: The user pool ID.
        :param provider_name: The identity provider name.
        :raises InvalidParameterException:
        :raises UnsupportedIdentityProviderException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteResourceServer")
    def delete_resource_server(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        identifier: ResourceServerIdentifierType,
    ) -> None:
        """Deletes a resource server.

        :param user_pool_id: The user pool ID for the user pool that hosts the resource server.
        :param identifier: The identifier for the resource server.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteUser")
    def delete_user(self, context: RequestContext, access_token: TokenModelType) -> None:
        """Allows a user to delete himself or herself.

        :param access_token: The access token from a request to delete a user.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteUserAttributes")
    def delete_user_attributes(
        self,
        context: RequestContext,
        user_attribute_names: AttributeNameListType,
        access_token: TokenModelType,
    ) -> DeleteUserAttributesResponse:
        """Deletes the attributes for a user.

        :param user_attribute_names: An array of strings representing the user attribute names you want to
        delete.
        :param access_token: The access token used in the request to delete user attributes.
        :returns: DeleteUserAttributesResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteUserPool")
    def delete_user_pool(self, context: RequestContext, user_pool_id: UserPoolIdType) -> None:
        """Deletes the specified Amazon Cognito user pool.

        :param user_pool_id: The user pool ID for the user pool you want to delete.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserImportInProgressException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteUserPoolClient")
    def delete_user_pool_client(
        self, context: RequestContext, user_pool_id: UserPoolIdType, client_id: ClientIdType
    ) -> None:
        """Allows the developer to delete the user pool client.

        :param user_pool_id: The user pool ID for the user pool where you want to delete the client.
        :param client_id: The app client ID of the app associated with the user pool.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DeleteUserPoolDomain")
    def delete_user_pool_domain(
        self, context: RequestContext, domain: DomainType, user_pool_id: UserPoolIdType
    ) -> DeleteUserPoolDomainResponse:
        """Deletes a domain for a user pool.

        :param domain: The domain string.
        :param user_pool_id: The user pool ID.
        :returns: DeleteUserPoolDomainResponse
        :raises NotAuthorizedException:
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeIdentityProvider")
    def describe_identity_provider(
        self, context: RequestContext, user_pool_id: UserPoolIdType, provider_name: ProviderNameType
    ) -> DescribeIdentityProviderResponse:
        """Gets information about a specific identity provider.

        :param user_pool_id: The user pool ID.
        :param provider_name: The identity provider name.
        :returns: DescribeIdentityProviderResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeResourceServer")
    def describe_resource_server(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        identifier: ResourceServerIdentifierType,
    ) -> DescribeResourceServerResponse:
        """Describes a resource server.

        :param user_pool_id: The user pool ID for the user pool that hosts the resource server.
        :param identifier: The identifier for the resource server.
        :returns: DescribeResourceServerResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeRiskConfiguration")
    def describe_risk_configuration(
        self, context: RequestContext, user_pool_id: UserPoolIdType, client_id: ClientIdType = None
    ) -> DescribeRiskConfigurationResponse:
        """Describes the risk configuration.

        :param user_pool_id: The user pool ID.
        :param client_id: The app client ID.
        :returns: DescribeRiskConfigurationResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserPoolAddOnNotEnabledException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeUserImportJob")
    def describe_user_import_job(
        self, context: RequestContext, user_pool_id: UserPoolIdType, job_id: UserImportJobIdType
    ) -> DescribeUserImportJobResponse:
        """Describes the user import job.

        :param user_pool_id: The user pool ID for the user pool that the users are being imported
        into.
        :param job_id: The job ID for the user import job.
        :returns: DescribeUserImportJobResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeUserPool")
    def describe_user_pool(
        self, context: RequestContext, user_pool_id: UserPoolIdType
    ) -> DescribeUserPoolResponse:
        """Returns the configuration information and metadata of the specified user
        pool.

        :param user_pool_id: The user pool ID for the user pool you want to describe.
        :returns: DescribeUserPoolResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserPoolTaggingException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeUserPoolClient")
    def describe_user_pool_client(
        self, context: RequestContext, user_pool_id: UserPoolIdType, client_id: ClientIdType
    ) -> DescribeUserPoolClientResponse:
        """Client method for returning the configuration information and metadata
        of the specified user pool app client.

        :param user_pool_id: The user pool ID for the user pool you want to describe.
        :param client_id: The app client ID of the app associated with the user pool.
        :returns: DescribeUserPoolClientResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("DescribeUserPoolDomain")
    def describe_user_pool_domain(
        self, context: RequestContext, domain: DomainType
    ) -> DescribeUserPoolDomainResponse:
        """Gets information about a domain.

        :param domain: The domain string.
        :returns: DescribeUserPoolDomainResponse
        :raises NotAuthorizedException:
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ForgetDevice")
    def forget_device(
        self,
        context: RequestContext,
        device_key: DeviceKeyType,
        access_token: TokenModelType = None,
    ) -> None:
        """Forgets the specified device.

        :param device_key: The device key.
        :param access_token: The access token for the forgotten device request.
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InvalidUserPoolConfigurationException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ForgotPassword")
    def forgot_password(
        self,
        context: RequestContext,
        client_id: ClientIdType,
        username: UsernameType,
        secret_hash: SecretHashType = None,
        user_context_data: UserContextDataType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> ForgotPasswordResponse:
        """Calling this API causes a message to be sent to the end user with a
        confirmation code that is required to change the user's password. For
        the ``Username`` parameter, you can use the username or user alias. The
        method used to send the confirmation code is sent according to the
        specified AccountRecoverySetting. For more information, see `Recovering
        User
        Accounts <https://docs.aws.amazon.com/cognito/latest/developerguide/how-to-recover-a-user-account.html>`__
        in the *Amazon Cognito Developer Guide*. If neither a verified phone
        number nor a verified email exists, an ``InvalidParameterException`` is
        thrown. To use the confirmation code for resetting the password, call
        `ConfirmForgotPassword <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_ConfirmForgotPassword.html>`__.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param client_id: The ID of the client associated with the user pool.
        :param username: The user name of the user for whom you want to enter a code to reset a
        forgotten password.
        :param secret_hash: A keyed-hash message authentication code (HMAC) calculated using the
        secret key of a user pool client and username plus the client ID in the
        message.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``ForgotPassword`` calls.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: ForgotPasswordResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises NotAuthorizedException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises CodeDeliveryFailureException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetCSVHeader")
    def get_csv_header(
        self, context: RequestContext, user_pool_id: UserPoolIdType
    ) -> GetCSVHeaderResponse:
        """Gets the header information for the comma-separated value (CSV) file to
        be used as input for the user import job.

        :param user_pool_id: The user pool ID for the user pool that the users are to be imported
        into.
        :returns: GetCSVHeaderResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetDevice")
    def get_device(
        self,
        context: RequestContext,
        device_key: DeviceKeyType,
        access_token: TokenModelType = None,
    ) -> GetDeviceResponse:
        """Gets the device.

        :param device_key: The device key.
        :param access_token: The access token.
        :returns: GetDeviceResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises InvalidUserPoolConfigurationException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetGroup")
    def get_group(
        self, context: RequestContext, group_name: GroupNameType, user_pool_id: UserPoolIdType
    ) -> GetGroupResponse:
        """Gets a group.

        Calling this action requires developer credentials.

        :param group_name: The name of the group.
        :param user_pool_id: The user pool ID for the user pool.
        :returns: GetGroupResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetIdentityProviderByIdentifier")
    def get_identity_provider_by_identifier(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        idp_identifier: IdpIdentifierType,
    ) -> GetIdentityProviderByIdentifierResponse:
        """Gets the specified identity provider.

        :param user_pool_id: The user pool ID.
        :param idp_identifier: The identity provider ID.
        :returns: GetIdentityProviderByIdentifierResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetSigningCertificate")
    def get_signing_certificate(
        self, context: RequestContext, user_pool_id: UserPoolIdType
    ) -> GetSigningCertificateResponse:
        """This method takes a user pool ID, and returns the signing certificate.

        :param user_pool_id: The user pool ID.
        :returns: GetSigningCertificateResponse
        :raises InternalErrorException:
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("GetUICustomization")
    def get_ui_customization(
        self, context: RequestContext, user_pool_id: UserPoolIdType, client_id: ClientIdType = None
    ) -> GetUICustomizationResponse:
        """Gets the user interface (UI) Customization information for a particular
        app client's app UI, if any such information exists for the client. If
        nothing is set for the particular client, but there is an existing pool
        level customization (the app ``clientId`` is ``ALL``), then that
        information is returned. If nothing is present, then an empty shape is
        returned.

        :param user_pool_id: The user pool ID for the user pool.
        :param client_id: The client ID for the client app.
        :returns: GetUICustomizationResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetUser")
    def get_user(self, context: RequestContext, access_token: TokenModelType) -> GetUserResponse:
        """Gets the user attributes and metadata for a user.

        :param access_token: The access token returned by the server response to get information
        about the user.
        :returns: GetUserResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetUserAttributeVerificationCode")
    def get_user_attribute_verification_code(
        self,
        context: RequestContext,
        access_token: TokenModelType,
        attribute_name: AttributeNameType,
        client_metadata: ClientMetadataType = None,
    ) -> GetUserAttributeVerificationCodeResponse:
        """Gets the user attribute verification code for the specified attribute
        name.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param access_token: The access token returned by the server response to get the user
        attribute verification code.
        :param attribute_name: The attribute name returned by the server response to get the user
        attribute verification code.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: GetUserAttributeVerificationCodeResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises CodeDeliveryFailureException:
        :raises LimitExceededException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GetUserPoolMfaConfig")
    def get_user_pool_mfa_config(
        self, context: RequestContext, user_pool_id: UserPoolIdType
    ) -> GetUserPoolMfaConfigResponse:
        """Gets the user pool multi-factor authentication (MFA) configuration.

        :param user_pool_id: The user pool ID.
        :returns: GetUserPoolMfaConfigResponse
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("GlobalSignOut")
    def global_sign_out(
        self, context: RequestContext, access_token: TokenModelType
    ) -> GlobalSignOutResponse:
        """Signs out users from all devices. It also invalidates all refresh tokens
        issued to a user. The user's current access and ID tokens remain valid
        until their expiry. Access and Id tokens expire one hour after they're
        issued.

        :param access_token: The access token.
        :returns: GlobalSignOutResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("InitiateAuth")
    def initiate_auth(
        self,
        context: RequestContext,
        auth_flow: AuthFlowType,
        client_id: ClientIdType,
        auth_parameters: AuthParametersType = None,
        client_metadata: ClientMetadataType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        user_context_data: UserContextDataType = None,
    ) -> InitiateAuthResponse:
        """Initiates the authentication flow.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param auth_flow: The authentication flow for this call to run.
        :param client_id: The app client ID.
        :param auth_parameters: The authentication parameters.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for
        certain custom workflows that this action triggers.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``InitiateAuth`` calls.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :returns: InitiateAuthResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises UnexpectedLambdaException:
        :raises InvalidUserPoolConfigurationException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        """
        raise NotImplementedError

    @handler("ListDevices")
    def list_devices(
        self,
        context: RequestContext,
        access_token: TokenModelType,
        limit: QueryLimitType = None,
        pagination_token: SearchPaginationTokenType = None,
    ) -> ListDevicesResponse:
        """Lists the devices.

        :param access_token: The access tokens for the request to list devices.
        :param limit: The limit of the device request.
        :param pagination_token: The pagination token for the list request.
        :returns: ListDevicesResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListGroups")
    def list_groups(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        limit: QueryLimitType = None,
        next_token: PaginationKey = None,
    ) -> ListGroupsResponse:
        """Lists the groups associated with a user pool.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool.
        :param limit: The limit of the request to list groups.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListGroupsResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListIdentityProviders")
    def list_identity_providers(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        max_results: ListProvidersLimitType = None,
        next_token: PaginationKeyType = None,
    ) -> ListIdentityProvidersResponse:
        """Lists information about all identity providers for a user pool.

        :param user_pool_id: The user pool ID.
        :param max_results: The maximum number of identity providers to return.
        :param next_token: A pagination token.
        :returns: ListIdentityProvidersResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListResourceServers")
    def list_resource_servers(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        max_results: ListResourceServersLimitType = None,
        next_token: PaginationKeyType = None,
    ) -> ListResourceServersResponse:
        """Lists the resource servers for a user pool.

        :param user_pool_id: The user pool ID for the user pool.
        :param max_results: The maximum number of resource servers to return.
        :param next_token: A pagination token.
        :returns: ListResourceServersResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ArnType
    ) -> ListTagsForResourceResponse:
        """Lists the tags that are assigned to an Amazon Cognito user pool.

        A tag is a label that you can apply to user pools to categorize and
        manage them in different ways, such as by purpose, owner, environment,
        or other criteria.

        You can use this action up to 10 times per second, per account.

        :param resource_arn: The Amazon Resource Name (ARN) of the user pool that the tags are
        assigned to.
        :returns: ListTagsForResourceResponse
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InvalidParameterException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListUserImportJobs")
    def list_user_import_jobs(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        max_results: PoolQueryLimitType,
        pagination_token: PaginationKeyType = None,
    ) -> ListUserImportJobsResponse:
        """Lists the user import jobs.

        :param user_pool_id: The user pool ID for the user pool that the users are being imported
        into.
        :param max_results: The maximum number of import jobs you want the request to return.
        :param pagination_token: An identifier that was returned from the previous call to
        ``ListUserImportJobs``, which can be used to return the next set of
        import jobs in the list.
        :returns: ListUserImportJobsResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListUserPoolClients")
    def list_user_pool_clients(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        max_results: QueryLimit = None,
        next_token: PaginationKey = None,
    ) -> ListUserPoolClientsResponse:
        """Lists the clients that have been created for the specified user pool.

        :param user_pool_id: The user pool ID for the user pool where you want to list user pool
        clients.
        :param max_results: The maximum number of results you want the request to return when
        listing the user pool clients.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListUserPoolClientsResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListUserPools")
    def list_user_pools(
        self,
        context: RequestContext,
        max_results: PoolQueryLimitType,
        next_token: PaginationKeyType = None,
    ) -> ListUserPoolsResponse:
        """Lists the user pools associated with an Amazon Web Services account.

        :param max_results: The maximum number of results you want the request to return when
        listing the user pools.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListUserPoolsResponse
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListUsers")
    def list_users(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        attributes_to_get: SearchedAttributeNamesListType = None,
        limit: QueryLimitType = None,
        pagination_token: SearchPaginationTokenType = None,
        filter: UserFilterType = None,
    ) -> ListUsersResponse:
        """Lists the users in the Amazon Cognito user pool.

        :param user_pool_id: The user pool ID for the user pool on which the search should be
        performed.
        :param attributes_to_get: An array of strings, where each string is the name of a user attribute
        to be returned for each user in the search results.
        :param limit: Maximum number of users to be returned.
        :param pagination_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :param filter: A filter string of the form "*AttributeName* *Filter-Type*
        "*AttributeValue*"".
        :returns: ListUsersResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ListUsersInGroup")
    def list_users_in_group(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        group_name: GroupNameType,
        limit: QueryLimitType = None,
        next_token: PaginationKey = None,
    ) -> ListUsersInGroupResponse:
        """Lists the users in the specified group.

        Calling this action requires developer credentials.

        :param user_pool_id: The user pool ID for the user pool.
        :param group_name: The name of the group.
        :param limit: The limit of the request to list users.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListUsersInGroupResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("ResendConfirmationCode")
    def resend_confirmation_code(
        self,
        context: RequestContext,
        client_id: ClientIdType,
        username: UsernameType,
        secret_hash: SecretHashType = None,
        user_context_data: UserContextDataType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> ResendConfirmationCodeResponse:
        """Resends the confirmation (for confirmation of registration) to a
        specific user in the user pool.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param client_id: The ID of the client associated with the user pool.
        :param username: The ``username`` attribute of the user to whom you want to resend a
        confirmation code.
        :param secret_hash: A keyed-hash message authentication code (HMAC) calculated using the
        secret key of a user pool client and username plus the client ID in the
        message.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``ResendConfirmationCode`` calls.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: ResendConfirmationCodeResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises NotAuthorizedException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises CodeDeliveryFailureException:
        :raises UserNotFoundException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("RespondToAuthChallenge")
    def respond_to_auth_challenge(
        self,
        context: RequestContext,
        client_id: ClientIdType,
        challenge_name: ChallengeNameType,
        session: SessionType = None,
        challenge_responses: ChallengeResponsesType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        user_context_data: UserContextDataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> RespondToAuthChallengeResponse:
        """Responds to the authentication challenge.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param client_id: The app client ID.
        :param challenge_name: The challenge name.
        :param session: The session that should be passed both ways in challenge-response calls
        to the service.
        :param challenge_responses: The challenge responses.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``RespondToAuthChallenge`` calls.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: RespondToAuthChallengeResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises CodeMismatchException:
        :raises ExpiredCodeException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises InvalidPasswordException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises InvalidUserPoolConfigurationException:
        :raises MFAMethodNotFoundException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises AliasExistsException:
        :raises InternalErrorException:
        :raises SoftwareTokenMFANotFoundException:
        """
        raise NotImplementedError

    @handler("RevokeToken")
    def revoke_token(
        self,
        context: RequestContext,
        token: TokenModelType,
        client_id: ClientIdType,
        client_secret: ClientSecretType = None,
    ) -> RevokeTokenResponse:
        """Revokes all of the access tokens generated by the specified refresh
        token. After the token is revoked, you can't use the revoked token to
        access Amazon Cognito authenticated APIs.

        :param token: The refresh token that you want to revoke.
        :param client_id: The client ID for the token that you want to revoke.
        :param client_secret: The secret for the client ID.
        :returns: RevokeTokenResponse
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises UnauthorizedException:
        :raises InvalidParameterException:
        :raises UnsupportedOperationException:
        :raises UnsupportedTokenTypeException:
        """
        raise NotImplementedError

    @handler("SetRiskConfiguration")
    def set_risk_configuration(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        client_id: ClientIdType = None,
        compromised_credentials_risk_configuration: CompromisedCredentialsRiskConfigurationType = None,
        account_takeover_risk_configuration: AccountTakeoverRiskConfigurationType = None,
        risk_exception_configuration: RiskExceptionConfigurationType = None,
    ) -> SetRiskConfigurationResponse:
        """Configures actions on detected risks. To delete the risk configuration
        for ``UserPoolId`` or ``ClientId``, pass null values for all four
        configuration types.

        To activate Amazon Cognito advanced security features, update the user
        pool to include the ``UserPoolAddOns`` key ``AdvancedSecurityMode``.

        :param user_pool_id: The user pool ID.
        :param client_id: The app client ID.
        :param compromised_credentials_risk_configuration: The compromised credentials risk configuration.
        :param account_takeover_risk_configuration: The account takeover risk configuration.
        :param risk_exception_configuration: The configuration to override the risk decision.
        :returns: SetRiskConfigurationResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserPoolAddOnNotEnabledException:
        :raises CodeDeliveryFailureException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("SetUICustomization")
    def set_ui_customization(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        client_id: ClientIdType = None,
        css: CSSType = None,
        image_file: ImageFileType = None,
    ) -> SetUICustomizationResponse:
        """Sets the user interface (UI) customization information for a user pool's
        built-in app UI.

        You can specify app UI customization settings for a single client (with
        a specific ``clientId``) or for all clients (by setting the ``clientId``
        to ``ALL``). If you specify ``ALL``, the default configuration is used
        for every client that has no previously set UI customization. If you
        specify UI customization settings for a particular client, it will no
        longer return to the ``ALL`` configuration.

        To use this API, your user pool must have a domain associated with it.
        Otherwise, there is no place to host the app's pages, and the service
        will throw an error.

        :param user_pool_id: The user pool ID for the user pool.
        :param client_id: The client ID for the client app.
        :param css: The CSS values in the UI customization.
        :param image_file: The uploaded logo image for the UI customization.
        :returns: SetUICustomizationResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("SetUserMFAPreference")
    def set_user_mfa_preference(
        self,
        context: RequestContext,
        access_token: TokenModelType,
        sms_mfa_settings: SMSMfaSettingsType = None,
        software_token_mfa_settings: SoftwareTokenMfaSettingsType = None,
    ) -> SetUserMFAPreferenceResponse:
        """Set the user's multi-factor authentication (MFA) method preference,
        including which MFA factors are activated and if any are preferred. Only
        one factor can be set as preferred. The preferred MFA factor will be
        used to authenticate a user if multiple factors are activated. If
        multiple options are activated and no preference is set, a challenge to
        choose an MFA option will be returned during sign-in. If an MFA type is
        activated for a user, the user will be prompted for MFA during all
        sign-in attempts unless device tracking is turned on and the device has
        been trusted. If you want MFA to be applied selectively based on the
        assessed risk level of sign-in attempts, deactivate MFA for users and
        turn on Adaptive Authentication for the user pool.

        :param access_token: The access token for the user.
        :param sms_mfa_settings: The SMS text message multi-factor authentication (MFA) settings.
        :param software_token_mfa_settings: The time-based one-time password software token MFA settings.
        :returns: SetUserMFAPreferenceResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("SetUserPoolMfaConfig")
    def set_user_pool_mfa_config(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        sms_mfa_configuration: SmsMfaConfigType = None,
        software_token_mfa_configuration: SoftwareTokenMfaConfigType = None,
        mfa_configuration: UserPoolMfaType = None,
    ) -> SetUserPoolMfaConfigResponse:
        """Sets the user pool multi-factor authentication (MFA) configuration.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param user_pool_id: The user pool ID.
        :param sms_mfa_configuration: The SMS text message MFA configuration.
        :param software_token_mfa_configuration: The software token MFA configuration.
        :param mfa_configuration: The MFA configuration.
        :returns: SetUserPoolMfaConfigResponse
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises ResourceNotFoundException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("SetUserSettings")
    def set_user_settings(
        self, context: RequestContext, access_token: TokenModelType, mfa_options: MFAOptionListType
    ) -> SetUserSettingsResponse:
        """*This action is no longer supported.* You can use it to configure only
        SMS MFA. You can't use it to configure time-based one-time password
        (TOTP) software token MFA. To configure either type of MFA, use
        `SetUserMFAPreference <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_SetUserMFAPreference.html>`__
        instead.

        :param access_token: The access token for the set user settings request.
        :param mfa_options: You can use this parameter only to set an SMS configuration that uses
        SMS for delivery.
        :returns: SetUserSettingsResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("SignUp")
    def sign_up(
        self,
        context: RequestContext,
        client_id: ClientIdType,
        username: UsernameType,
        password: PasswordType,
        secret_hash: SecretHashType = None,
        user_attributes: AttributeListType = None,
        validation_data: AttributeListType = None,
        analytics_metadata: AnalyticsMetadataType = None,
        user_context_data: UserContextDataType = None,
        client_metadata: ClientMetadataType = None,
    ) -> SignUpResponse:
        """Registers the user in the specified user pool and creates a user name,
        password, and user attributes.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param client_id: The ID of the client associated with the user pool.
        :param username: The user name of the user you want to register.
        :param password: The password of the user you want to register.
        :param secret_hash: A keyed-hash message authentication code (HMAC) calculated using the
        secret key of a user pool client and username plus the client ID in the
        message.
        :param user_attributes: An array of name-value pairs representing user attributes.
        :param validation_data: The validation data in the request to register a user.
        :param analytics_metadata: The Amazon Pinpoint analytics metadata for collecting metrics for
        ``SignUp`` calls.
        :param user_context_data: Contextual data such as the user's device fingerprint, IP address, or
        location used for evaluating the risk of an unexpected event by Amazon
        Cognito advanced security.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action triggers.
        :returns: SignUpResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises NotAuthorizedException:
        :raises InvalidPasswordException:
        :raises InvalidLambdaResponseException:
        :raises UsernameExistsException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises CodeDeliveryFailureException:
        """
        raise NotImplementedError

    @handler("StartUserImportJob")
    def start_user_import_job(
        self, context: RequestContext, user_pool_id: UserPoolIdType, job_id: UserImportJobIdType
    ) -> StartUserImportJobResponse:
        """Starts the user import.

        :param user_pool_id: The user pool ID for the user pool that the users are being imported
        into.
        :param job_id: The job ID for the user import job.
        :returns: StartUserImportJobResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises PreconditionNotMetException:
        :raises NotAuthorizedException:
        """
        raise NotImplementedError

    @handler("StopUserImportJob")
    def stop_user_import_job(
        self, context: RequestContext, user_pool_id: UserPoolIdType, job_id: UserImportJobIdType
    ) -> StopUserImportJobResponse:
        """Stops the user import job.

        :param user_pool_id: The user pool ID for the user pool that the users are being imported
        into.
        :param job_id: The job ID for the user import job.
        :returns: StopUserImportJobResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        :raises PreconditionNotMetException:
        :raises NotAuthorizedException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ArnType, tags: UserPoolTagsType
    ) -> TagResourceResponse:
        """Assigns a set of tags to an Amazon Cognito user pool. A tag is a label
        that you can use to categorize and manage user pools in different ways,
        such as by purpose, owner, environment, or other criteria.

        Each tag consists of a key and value, both of which you define. A key is
        a general category for more specific values. For example, if you have
        two versions of a user pool, one for testing and another for production,
        you might assign an ``Environment`` tag key to both user pools. The
        value of this key might be ``Test`` for one user pool, and
        ``Production`` for the other.

        Tags are useful for cost tracking and access control. You can activate
        your tags so that they appear on the Billing and Cost Management
        console, where you can track the costs associated with your user pools.
        In an Identity and Access Management policy, you can constrain
        permissions for user pools based on specific tags or tag values.

        You can use this action up to 5 times per second, per account. A user
        pool can have as many as 50 tags.

        :param resource_arn: The Amazon Resource Name (ARN) of the user pool to assign the tags to.
        :param tags: The tags to assign to the user pool.
        :returns: TagResourceResponse
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InvalidParameterException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ArnType, tag_keys: UserPoolTagsListType
    ) -> UntagResourceResponse:
        """Removes the specified tags from an Amazon Cognito user pool. You can use
        this action up to 5 times per second, per account.

        :param resource_arn: The Amazon Resource Name (ARN) of the user pool that the tags are
        assigned to.
        :param tag_keys: The keys of the tags to remove from the user pool.
        :returns: UntagResourceResponse
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InvalidParameterException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateAuthEventFeedback")
    def update_auth_event_feedback(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        username: UsernameType,
        event_id: EventIdType,
        feedback_token: TokenModelType,
        feedback_value: FeedbackValueType,
    ) -> UpdateAuthEventFeedbackResponse:
        """Provides the feedback for an authentication event, whether it was from a
        valid user or not. This feedback is used for improving the risk
        evaluation decision for the user pool as part of Amazon Cognito advanced
        security.

        :param user_pool_id: The user pool ID.
        :param username: The user pool username.
        :param event_id: The event ID.
        :param feedback_token: The feedback token.
        :param feedback_value: The authentication event feedback value.
        :returns: UpdateAuthEventFeedbackResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserNotFoundException:
        :raises UserPoolAddOnNotEnabledException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateDeviceStatus")
    def update_device_status(
        self,
        context: RequestContext,
        access_token: TokenModelType,
        device_key: DeviceKeyType,
        device_remembered_status: DeviceRememberedStatusType = None,
    ) -> UpdateDeviceStatusResponse:
        """Updates the device status.

        :param access_token: The access token.
        :param device_key: The device key.
        :param device_remembered_status: The status of whether a device is remembered.
        :returns: UpdateDeviceStatusResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises InvalidUserPoolConfigurationException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateGroup")
    def update_group(
        self,
        context: RequestContext,
        group_name: GroupNameType,
        user_pool_id: UserPoolIdType,
        description: DescriptionType = None,
        role_arn: ArnType = None,
        precedence: PrecedenceType = None,
    ) -> UpdateGroupResponse:
        """Updates the specified group with the specified attributes.

        Calling this action requires developer credentials.

        :param group_name: The name of the group.
        :param user_pool_id: The user pool ID for the user pool.
        :param description: A string containing the new description of the group.
        :param role_arn: The new role Amazon Resource Name (ARN) for the group.
        :param precedence: The new precedence value for the group.
        :returns: UpdateGroupResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateIdentityProvider")
    def update_identity_provider(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        provider_name: ProviderNameType,
        provider_details: ProviderDetailsType = None,
        attribute_mapping: AttributeMappingType = None,
        idp_identifiers: IdpIdentifiersListType = None,
    ) -> UpdateIdentityProviderResponse:
        """Updates identity provider information for a user pool.

        :param user_pool_id: The user pool ID.
        :param provider_name: The identity provider name.
        :param provider_details: The identity provider details to be updated, such as ``MetadataURL`` and
        ``MetadataFile``.
        :param attribute_mapping: The identity provider attribute mapping to be changed.
        :param idp_identifiers: A list of identity provider identifiers.
        :returns: UpdateIdentityProviderResponse
        :raises InvalidParameterException:
        :raises UnsupportedIdentityProviderException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateResourceServer")
    def update_resource_server(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        identifier: ResourceServerIdentifierType,
        name: ResourceServerNameType,
        scopes: ResourceServerScopeListType = None,
    ) -> UpdateResourceServerResponse:
        """Updates the name and scopes of resource server. All other fields are
        read-only.

        If you don't provide a value for an attribute, it is set to the default
        value.

        :param user_pool_id: The user pool ID for the user pool.
        :param identifier: The identifier for the resource server.
        :param name: The name of the resource server.
        :param scopes: The scope values to be set for the resource server.
        :returns: UpdateResourceServerResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateUserAttributes")
    def update_user_attributes(
        self,
        context: RequestContext,
        user_attributes: AttributeListType,
        access_token: TokenModelType,
        client_metadata: ClientMetadataType = None,
    ) -> UpdateUserAttributesResponse:
        """Allows a user to update a specific attribute (one at a time).

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param user_attributes: An array of name-value pairs representing user attributes.
        :param access_token: The access token for the request to update user attributes.
        :param client_metadata: A map of custom key-value pairs that you can provide as input for any
        custom workflows that this action initiates.
        :returns: UpdateUserAttributesResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises CodeMismatchException:
        :raises ExpiredCodeException:
        :raises NotAuthorizedException:
        :raises UnexpectedLambdaException:
        :raises UserLambdaValidationException:
        :raises InvalidLambdaResponseException:
        :raises TooManyRequestsException:
        :raises AliasExistsException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises InvalidEmailRoleAccessPolicyException:
        :raises CodeDeliveryFailureException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateUserPool")
    def update_user_pool(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        policies: UserPoolPolicyType = None,
        lambda_config: LambdaConfigType = None,
        auto_verified_attributes: VerifiedAttributesListType = None,
        sms_verification_message: SmsVerificationMessageType = None,
        email_verification_message: EmailVerificationMessageType = None,
        email_verification_subject: EmailVerificationSubjectType = None,
        verification_message_template: VerificationMessageTemplateType = None,
        sms_authentication_message: SmsVerificationMessageType = None,
        mfa_configuration: UserPoolMfaType = None,
        device_configuration: DeviceConfigurationType = None,
        email_configuration: EmailConfigurationType = None,
        sms_configuration: SmsConfigurationType = None,
        user_pool_tags: UserPoolTagsType = None,
        admin_create_user_config: AdminCreateUserConfigType = None,
        user_pool_add_ons: UserPoolAddOnsType = None,
        account_recovery_setting: AccountRecoverySettingType = None,
    ) -> UpdateUserPoolResponse:
        """Updates the specified user pool with the specified attributes. You can
        get a list of the current user pool settings using
        `DescribeUserPool <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeUserPool.html>`__.
        If you don't provide a value for an attribute, it will be set to the
        default value.

        This action might generate an SMS text message. Starting June 1, 2021,
        US telecom carriers require you to register an origination phone number
        before you can send SMS messages to US phone numbers. If you use SMS
        text messages in Amazon Cognito, you must register a phone number with
        `Amazon Pinpoint <https://console.aws.amazon.com/pinpoint/home/>`__.
        Amazon Cognito uses the registered number automatically. Otherwise,
        Amazon Cognito users who must receive SMS messages might not be able to
        sign up, activate their accounts, or sign in.

        If you have never used SMS text messages with Amazon Cognito or any
        other Amazon Web Service, Amazon Simple Notification Service might place
        your account in the SMS sandbox. In `sandbox
        mode <https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html>`__
        , you can send messages only to verified phone numbers. After you test
        your app while in the sandbox environment, you can move out of the
        sandbox and into production. For more information, see `SMS message
        settings for Amazon Cognito user
        pools <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-sms-userpool-settings.html>`__
        in the *Amazon Cognito Developer Guide*.

        :param user_pool_id: The user pool ID for the user pool you want to update.
        :param policies: A container with the policies you want to update in a user pool.
        :param lambda_config: The Lambda configuration information from the request to update the user
        pool.
        :param auto_verified_attributes: The attributes that are automatically verified when Amazon Cognito
        requests to update user pools.
        :param sms_verification_message: A container with information about the SMS verification message.
        :param email_verification_message: The contents of the email verification message.
        :param email_verification_subject: The subject of the email verification message.
        :param verification_message_template: The template for verification messages.
        :param sms_authentication_message: The contents of the SMS authentication message.
        :param mfa_configuration: Can be one of the following values:

        -  ``OFF`` - MFA tokens aren't required and can't be specified during
           user registration.
        :param device_configuration: Device configuration.
        :param email_configuration: The email configuration of your user pool.
        :param sms_configuration: The SMS configuration with the settings that your Amazon Cognito user
        pool must use to send an SMS message from your Amazon Web Services
        account through Amazon Simple Notification Service.
        :param user_pool_tags: The tag keys and values to assign to the user pool.
        :param admin_create_user_config: The configuration for ``AdminCreateUser`` requests.
        :param user_pool_add_ons: Enables advanced security risk detection.
        :param account_recovery_setting: The available verified method a user can use to recover their password
        when they call ``ForgotPassword``.
        :returns: UpdateUserPoolResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises ConcurrentModificationException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises UserImportInProgressException:
        :raises InternalErrorException:
        :raises InvalidSmsRoleAccessPolicyException:
        :raises InvalidSmsRoleTrustRelationshipException:
        :raises UserPoolTaggingException:
        :raises InvalidEmailRoleAccessPolicyException:
        """
        raise NotImplementedError

    @handler("UpdateUserPoolClient")
    def update_user_pool_client(
        self,
        context: RequestContext,
        user_pool_id: UserPoolIdType,
        client_id: ClientIdType,
        client_name: ClientNameType = None,
        refresh_token_validity: RefreshTokenValidityType = None,
        access_token_validity: AccessTokenValidityType = None,
        id_token_validity: IdTokenValidityType = None,
        token_validity_units: TokenValidityUnitsType = None,
        read_attributes: ClientPermissionListType = None,
        write_attributes: ClientPermissionListType = None,
        explicit_auth_flows: ExplicitAuthFlowsListType = None,
        supported_identity_providers: SupportedIdentityProvidersListType = None,
        callback_urls: CallbackURLsListType = None,
        logout_urls: LogoutURLsListType = None,
        default_redirect_uri: RedirectUrlType = None,
        allowed_o_auth_flows: OAuthFlowsType = None,
        allowed_o_auth_scopes: ScopeListType = None,
        allowed_o_auth_flows_user_pool_client: BooleanType = None,
        analytics_configuration: AnalyticsConfigurationType = None,
        prevent_user_existence_errors: PreventUserExistenceErrorTypes = None,
        enable_token_revocation: WrappedBooleanType = None,
    ) -> UpdateUserPoolClientResponse:
        """Updates the specified user pool app client with the specified
        attributes. You can get a list of the current user pool app client
        settings using
        `DescribeUserPoolClient <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeUserPoolClient.html>`__.

        If you don't provide a value for an attribute, it will be set to the
        default value.

        You can also use this operation to enable token revocation for user pool
        clients. For more information about revoking tokens, see
        `RevokeToken <https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_RevokeToken.html>`__.

        :param user_pool_id: The user pool ID for the user pool where you want to update the user
        pool client.
        :param client_id: The ID of the client associated with the user pool.
        :param client_name: The client name from the update user pool client request.
        :param refresh_token_validity: The time limit, in days, after which the refresh token is no longer
        valid and can't be used.
        :param access_token_validity: The time limit after which the access token is no longer valid and can't
        be used.
        :param id_token_validity: The time limit after which the ID token is no longer valid and can't be
        used.
        :param token_validity_units: The units in which the validity times are represented.
        :param read_attributes: The read-only attributes of the user pool.
        :param write_attributes: The writeable attributes of the user pool.
        :param explicit_auth_flows: The authentication flows that are supported by the user pool clients.
        :param supported_identity_providers: A list of provider names for the identity providers that are supported
        on this client.
        :param callback_urls: A list of allowed redirect (callback) URLs for the identity providers.
        :param logout_urls: A list of allowed logout URLs for the identity providers.
        :param default_redirect_uri: The default redirect URI.
        :param allowed_o_auth_flows: The allowed OAuth flows.
        :param allowed_o_auth_scopes: The allowed OAuth scopes.
        :param allowed_o_auth_flows_user_pool_client: Set to true if the client is allowed to follow the OAuth protocol when
        interacting with Amazon Cognito user pools.
        :param analytics_configuration: The Amazon Pinpoint analytics configuration for collecting metrics for
        this user pool.
        :param prevent_user_existence_errors: Errors and responses that you want Amazon Cognito APIs to return during
        authentication, account confirmation, and password recovery when the
        user doesn't exist in the user pool.
        :param enable_token_revocation: Activates or deactivates token revocation.
        :returns: UpdateUserPoolClientResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises ConcurrentModificationException:
        :raises TooManyRequestsException:
        :raises NotAuthorizedException:
        :raises ScopeDoesNotExistException:
        :raises InvalidOAuthFlowException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("UpdateUserPoolDomain")
    def update_user_pool_domain(
        self,
        context: RequestContext,
        domain: DomainType,
        user_pool_id: UserPoolIdType,
        custom_domain_config: CustomDomainConfigType,
    ) -> UpdateUserPoolDomainResponse:
        """Updates the Secure Sockets Layer (SSL) certificate for the custom domain
        for your user pool.

        You can use this operation to provide the Amazon Resource Name (ARN) of
        a new certificate to Amazon Cognito. You can't use it to change the
        domain for a user pool.

        A custom domain is used to host the Amazon Cognito hosted UI, which
        provides sign-up and sign-in pages for your application. When you set up
        a custom domain, you provide a certificate that you manage with
        Certificate Manager (ACM). When necessary, you can use this operation to
        change the certificate that you applied to your custom domain.

        Usually, this is unnecessary following routine certificate renewal with
        ACM. When you renew your existing certificate in ACM, the ARN for your
        certificate remains the same, and your custom domain uses the new
        certificate automatically.

        However, if you replace your existing certificate with a new one, ACM
        gives the new certificate a new ARN. To apply the new certificate to
        your custom domain, you must provide this ARN to Amazon Cognito.

        When you add your new certificate in ACM, you must choose US East (N.
        Virginia) as the Amazon Web Services Region.

        After you submit your request, Amazon Cognito requires up to 1 hour to
        distribute your new certificate to your custom domain.

        For more information about adding a custom domain to your user pool, see
        `Using Your Own Domain for the Hosted
        UI <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-add-custom-domain.html>`__.

        :param domain: The domain name for the custom domain that hosts the sign-up and sign-in
        pages for your application.
        :param user_pool_id: The ID of the user pool that is associated with the custom domain whose
        certificate you're updating.
        :param custom_domain_config: The configuration for a custom domain that hosts the sign-up and sign-in
        pages for your application.
        :returns: UpdateUserPoolDomainResponse
        :raises InvalidParameterException:
        :raises NotAuthorizedException:
        :raises ResourceNotFoundException:
        :raises TooManyRequestsException:
        :raises InternalErrorException:
        """
        raise NotImplementedError

    @handler("VerifySoftwareToken")
    def verify_software_token(
        self,
        context: RequestContext,
        user_code: SoftwareTokenMFAUserCodeType,
        access_token: TokenModelType = None,
        session: SessionType = None,
        friendly_device_name: StringType = None,
    ) -> VerifySoftwareTokenResponse:
        """Use this API to register a user's entered time-based one-time password
        (TOTP) code and mark the user's software token MFA status as "verified"
        if successful. The request takes an access token or a session string,
        but not both.

        :param user_code: The one- time password computed using the secret code returned by
        `AssociateSoftwareToken <https://docs.
        :param access_token: The access token.
        :param session: The session that should be passed both ways in challenge-response calls
        to the service.
        :param friendly_device_name: The friendly device name.
        :returns: VerifySoftwareTokenResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises InvalidUserPoolConfigurationException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        :raises EnableSoftwareTokenMFAException:
        :raises NotAuthorizedException:
        :raises SoftwareTokenMFANotFoundException:
        :raises CodeMismatchException:
        """
        raise NotImplementedError

    @handler("VerifyUserAttribute")
    def verify_user_attribute(
        self,
        context: RequestContext,
        access_token: TokenModelType,
        attribute_name: AttributeNameType,
        code: ConfirmationCodeType,
    ) -> VerifyUserAttributeResponse:
        """Verifies the specified user attributes in the user pool.

        :param access_token: The access token of the request to verify user attributes.
        :param attribute_name: The attribute name in the request to verify user attributes.
        :param code: The verification code in the request to verify user attributes.
        :returns: VerifyUserAttributeResponse
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises CodeMismatchException:
        :raises ExpiredCodeException:
        :raises NotAuthorizedException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises PasswordResetRequiredException:
        :raises UserNotFoundException:
        :raises UserNotConfirmedException:
        :raises InternalErrorException:
        """
        raise NotImplementedError
