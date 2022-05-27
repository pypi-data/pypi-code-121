import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccountArn = str
AccountId = str
AccountName = str
AwsManagedPolicy = bool
ChildId = str
CreateAccountName = str
CreateAccountRequestId = str
Email = str
ExceptionMessage = str
ExceptionType = str
GenericArn = str
HandshakeArn = str
HandshakeId = str
HandshakeNotes = str
HandshakePartyId = str
HandshakeResourceValue = str
MaxResults = int
NextToken = str
OrganizationArn = str
OrganizationId = str
OrganizationalUnitArn = str
OrganizationalUnitId = str
OrganizationalUnitName = str
ParentId = str
PolicyArn = str
PolicyContent = str
PolicyDescription = str
PolicyId = str
PolicyName = str
PolicyTargetId = str
RoleName = str
RootArn = str
RootId = str
RootName = str
ServicePrincipal = str
TagKey = str
TagValue = str
TaggableResourceId = str
TargetName = str


class AccessDeniedForDependencyExceptionReason(str):
    ACCESS_DENIED_DURING_CREATE_SERVICE_LINKED_ROLE = (
        "ACCESS_DENIED_DURING_CREATE_SERVICE_LINKED_ROLE"
    )


class AccountJoinedMethod(str):
    INVITED = "INVITED"
    CREATED = "CREATED"


class AccountStatus(str):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_CLOSURE = "PENDING_CLOSURE"


class ActionType(str):
    INVITE = "INVITE"
    ENABLE_ALL_FEATURES = "ENABLE_ALL_FEATURES"
    APPROVE_ALL_FEATURES = "APPROVE_ALL_FEATURES"
    ADD_ORGANIZATIONS_SERVICE_LINKED_ROLE = "ADD_ORGANIZATIONS_SERVICE_LINKED_ROLE"


class ChildType(str):
    ACCOUNT = "ACCOUNT"
    ORGANIZATIONAL_UNIT = "ORGANIZATIONAL_UNIT"


class ConstraintViolationExceptionReason(str):
    ACCOUNT_NUMBER_LIMIT_EXCEEDED = "ACCOUNT_NUMBER_LIMIT_EXCEEDED"
    HANDSHAKE_RATE_LIMIT_EXCEEDED = "HANDSHAKE_RATE_LIMIT_EXCEEDED"
    OU_NUMBER_LIMIT_EXCEEDED = "OU_NUMBER_LIMIT_EXCEEDED"
    OU_DEPTH_LIMIT_EXCEEDED = "OU_DEPTH_LIMIT_EXCEEDED"
    POLICY_NUMBER_LIMIT_EXCEEDED = "POLICY_NUMBER_LIMIT_EXCEEDED"
    POLICY_CONTENT_LIMIT_EXCEEDED = "POLICY_CONTENT_LIMIT_EXCEEDED"
    MAX_POLICY_TYPE_ATTACHMENT_LIMIT_EXCEEDED = "MAX_POLICY_TYPE_ATTACHMENT_LIMIT_EXCEEDED"
    MIN_POLICY_TYPE_ATTACHMENT_LIMIT_EXCEEDED = "MIN_POLICY_TYPE_ATTACHMENT_LIMIT_EXCEEDED"
    ACCOUNT_CANNOT_LEAVE_ORGANIZATION = "ACCOUNT_CANNOT_LEAVE_ORGANIZATION"
    ACCOUNT_CANNOT_LEAVE_WITHOUT_EULA = "ACCOUNT_CANNOT_LEAVE_WITHOUT_EULA"
    ACCOUNT_CANNOT_LEAVE_WITHOUT_PHONE_VERIFICATION = (
        "ACCOUNT_CANNOT_LEAVE_WITHOUT_PHONE_VERIFICATION"
    )
    MASTER_ACCOUNT_PAYMENT_INSTRUMENT_REQUIRED = "MASTER_ACCOUNT_PAYMENT_INSTRUMENT_REQUIRED"
    MEMBER_ACCOUNT_PAYMENT_INSTRUMENT_REQUIRED = "MEMBER_ACCOUNT_PAYMENT_INSTRUMENT_REQUIRED"
    ACCOUNT_CREATION_RATE_LIMIT_EXCEEDED = "ACCOUNT_CREATION_RATE_LIMIT_EXCEEDED"
    MASTER_ACCOUNT_ADDRESS_DOES_NOT_MATCH_MARKETPLACE = (
        "MASTER_ACCOUNT_ADDRESS_DOES_NOT_MATCH_MARKETPLACE"
    )
    MASTER_ACCOUNT_MISSING_CONTACT_INFO = "MASTER_ACCOUNT_MISSING_CONTACT_INFO"
    MASTER_ACCOUNT_NOT_GOVCLOUD_ENABLED = "MASTER_ACCOUNT_NOT_GOVCLOUD_ENABLED"
    ORGANIZATION_NOT_IN_ALL_FEATURES_MODE = "ORGANIZATION_NOT_IN_ALL_FEATURES_MODE"
    CREATE_ORGANIZATION_IN_BILLING_MODE_UNSUPPORTED_REGION = (
        "CREATE_ORGANIZATION_IN_BILLING_MODE_UNSUPPORTED_REGION"
    )
    EMAIL_VERIFICATION_CODE_EXPIRED = "EMAIL_VERIFICATION_CODE_EXPIRED"
    WAIT_PERIOD_ACTIVE = "WAIT_PERIOD_ACTIVE"
    MAX_TAG_LIMIT_EXCEEDED = "MAX_TAG_LIMIT_EXCEEDED"
    TAG_POLICY_VIOLATION = "TAG_POLICY_VIOLATION"
    MAX_DELEGATED_ADMINISTRATORS_FOR_SERVICE_LIMIT_EXCEEDED = (
        "MAX_DELEGATED_ADMINISTRATORS_FOR_SERVICE_LIMIT_EXCEEDED"
    )
    CANNOT_REGISTER_MASTER_AS_DELEGATED_ADMINISTRATOR = (
        "CANNOT_REGISTER_MASTER_AS_DELEGATED_ADMINISTRATOR"
    )
    CANNOT_REMOVE_DELEGATED_ADMINISTRATOR_FROM_ORG = (
        "CANNOT_REMOVE_DELEGATED_ADMINISTRATOR_FROM_ORG"
    )
    DELEGATED_ADMINISTRATOR_EXISTS_FOR_THIS_SERVICE = (
        "DELEGATED_ADMINISTRATOR_EXISTS_FOR_THIS_SERVICE"
    )
    MASTER_ACCOUNT_MISSING_BUSINESS_LICENSE = "MASTER_ACCOUNT_MISSING_BUSINESS_LICENSE"
    CANNOT_CLOSE_MANAGEMENT_ACCOUNT = "CANNOT_CLOSE_MANAGEMENT_ACCOUNT"
    CLOSE_ACCOUNT_QUOTA_EXCEEDED = "CLOSE_ACCOUNT_QUOTA_EXCEEDED"
    CLOSE_ACCOUNT_REQUESTS_LIMIT_EXCEEDED = "CLOSE_ACCOUNT_REQUESTS_LIMIT_EXCEEDED"
    SERVICE_ACCESS_NOT_ENABLED = "SERVICE_ACCESS_NOT_ENABLED"
    INVALID_PAYMENT_INSTRUMENT = "INVALID_PAYMENT_INSTRUMENT"


class CreateAccountFailureReason(str):
    ACCOUNT_LIMIT_EXCEEDED = "ACCOUNT_LIMIT_EXCEEDED"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_ADDRESS = "INVALID_ADDRESS"
    INVALID_EMAIL = "INVALID_EMAIL"
    CONCURRENT_ACCOUNT_MODIFICATION = "CONCURRENT_ACCOUNT_MODIFICATION"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"
    GOVCLOUD_ACCOUNT_ALREADY_EXISTS = "GOVCLOUD_ACCOUNT_ALREADY_EXISTS"
    MISSING_BUSINESS_VALIDATION = "MISSING_BUSINESS_VALIDATION"
    FAILED_BUSINESS_VALIDATION = "FAILED_BUSINESS_VALIDATION"
    PENDING_BUSINESS_VALIDATION = "PENDING_BUSINESS_VALIDATION"
    INVALID_IDENTITY_FOR_BUSINESS_VALIDATION = "INVALID_IDENTITY_FOR_BUSINESS_VALIDATION"
    UNKNOWN_BUSINESS_VALIDATION = "UNKNOWN_BUSINESS_VALIDATION"
    MISSING_PAYMENT_INSTRUMENT = "MISSING_PAYMENT_INSTRUMENT"
    INVALID_PAYMENT_INSTRUMENT = "INVALID_PAYMENT_INSTRUMENT"


class CreateAccountState(str):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class EffectivePolicyType(str):
    TAG_POLICY = "TAG_POLICY"
    BACKUP_POLICY = "BACKUP_POLICY"
    AISERVICES_OPT_OUT_POLICY = "AISERVICES_OPT_OUT_POLICY"


class HandshakeConstraintViolationExceptionReason(str):
    ACCOUNT_NUMBER_LIMIT_EXCEEDED = "ACCOUNT_NUMBER_LIMIT_EXCEEDED"
    HANDSHAKE_RATE_LIMIT_EXCEEDED = "HANDSHAKE_RATE_LIMIT_EXCEEDED"
    ALREADY_IN_AN_ORGANIZATION = "ALREADY_IN_AN_ORGANIZATION"
    ORGANIZATION_ALREADY_HAS_ALL_FEATURES = "ORGANIZATION_ALREADY_HAS_ALL_FEATURES"
    ORGANIZATION_IS_ALREADY_PENDING_ALL_FEATURES_MIGRATION = (
        "ORGANIZATION_IS_ALREADY_PENDING_ALL_FEATURES_MIGRATION"
    )
    INVITE_DISABLED_DURING_ENABLE_ALL_FEATURES = "INVITE_DISABLED_DURING_ENABLE_ALL_FEATURES"
    PAYMENT_INSTRUMENT_REQUIRED = "PAYMENT_INSTRUMENT_REQUIRED"
    ORGANIZATION_FROM_DIFFERENT_SELLER_OF_RECORD = "ORGANIZATION_FROM_DIFFERENT_SELLER_OF_RECORD"
    ORGANIZATION_MEMBERSHIP_CHANGE_RATE_LIMIT_EXCEEDED = (
        "ORGANIZATION_MEMBERSHIP_CHANGE_RATE_LIMIT_EXCEEDED"
    )
    MANAGEMENT_ACCOUNT_EMAIL_NOT_VERIFIED = "MANAGEMENT_ACCOUNT_EMAIL_NOT_VERIFIED"


class HandshakePartyType(str):
    ACCOUNT = "ACCOUNT"
    ORGANIZATION = "ORGANIZATION"
    EMAIL = "EMAIL"


class HandshakeResourceType(str):
    ACCOUNT = "ACCOUNT"
    ORGANIZATION = "ORGANIZATION"
    ORGANIZATION_FEATURE_SET = "ORGANIZATION_FEATURE_SET"
    EMAIL = "EMAIL"
    MASTER_EMAIL = "MASTER_EMAIL"
    MASTER_NAME = "MASTER_NAME"
    NOTES = "NOTES"
    PARENT_HANDSHAKE = "PARENT_HANDSHAKE"


class HandshakeState(str):
    REQUESTED = "REQUESTED"
    OPEN = "OPEN"
    CANCELED = "CANCELED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class IAMUserAccessToBilling(str):
    ALLOW = "ALLOW"
    DENY = "DENY"


class InvalidInputExceptionReason(str):
    INVALID_PARTY_TYPE_TARGET = "INVALID_PARTY_TYPE_TARGET"
    INVALID_SYNTAX_ORGANIZATION_ARN = "INVALID_SYNTAX_ORGANIZATION_ARN"
    INVALID_SYNTAX_POLICY_ID = "INVALID_SYNTAX_POLICY_ID"
    INVALID_ENUM = "INVALID_ENUM"
    INVALID_ENUM_POLICY_TYPE = "INVALID_ENUM_POLICY_TYPE"
    INVALID_LIST_MEMBER = "INVALID_LIST_MEMBER"
    MAX_LENGTH_EXCEEDED = "MAX_LENGTH_EXCEEDED"
    MAX_VALUE_EXCEEDED = "MAX_VALUE_EXCEEDED"
    MIN_LENGTH_EXCEEDED = "MIN_LENGTH_EXCEEDED"
    MIN_VALUE_EXCEEDED = "MIN_VALUE_EXCEEDED"
    IMMUTABLE_POLICY = "IMMUTABLE_POLICY"
    INVALID_PATTERN = "INVALID_PATTERN"
    INVALID_PATTERN_TARGET_ID = "INVALID_PATTERN_TARGET_ID"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    INVALID_NEXT_TOKEN = "INVALID_NEXT_TOKEN"
    MAX_LIMIT_EXCEEDED_FILTER = "MAX_LIMIT_EXCEEDED_FILTER"
    MOVING_ACCOUNT_BETWEEN_DIFFERENT_ROOTS = "MOVING_ACCOUNT_BETWEEN_DIFFERENT_ROOTS"
    INVALID_FULL_NAME_TARGET = "INVALID_FULL_NAME_TARGET"
    UNRECOGNIZED_SERVICE_PRINCIPAL = "UNRECOGNIZED_SERVICE_PRINCIPAL"
    INVALID_ROLE_NAME = "INVALID_ROLE_NAME"
    INVALID_SYSTEM_TAGS_PARAMETER = "INVALID_SYSTEM_TAGS_PARAMETER"
    DUPLICATE_TAG_KEY = "DUPLICATE_TAG_KEY"
    TARGET_NOT_SUPPORTED = "TARGET_NOT_SUPPORTED"
    INVALID_EMAIL_ADDRESS_TARGET = "INVALID_EMAIL_ADDRESS_TARGET"


class OrganizationFeatureSet(str):
    ALL = "ALL"
    CONSOLIDATED_BILLING = "CONSOLIDATED_BILLING"


class ParentType(str):
    ROOT = "ROOT"
    ORGANIZATIONAL_UNIT = "ORGANIZATIONAL_UNIT"


class PolicyType(str):
    SERVICE_CONTROL_POLICY = "SERVICE_CONTROL_POLICY"
    TAG_POLICY = "TAG_POLICY"
    BACKUP_POLICY = "BACKUP_POLICY"
    AISERVICES_OPT_OUT_POLICY = "AISERVICES_OPT_OUT_POLICY"


class PolicyTypeStatus(str):
    ENABLED = "ENABLED"
    PENDING_ENABLE = "PENDING_ENABLE"
    PENDING_DISABLE = "PENDING_DISABLE"


class TargetType(str):
    ACCOUNT = "ACCOUNT"
    ORGANIZATIONAL_UNIT = "ORGANIZATIONAL_UNIT"
    ROOT = "ROOT"


class AWSOrganizationsNotInUseException(ServiceException):
    """Your account isn't a member of an organization. To make this request,
    you must use the credentials of an account that belongs to an
    organization.
    """

    Message: Optional[ExceptionMessage]


class AccessDeniedException(ServiceException):
    """You don't have permissions to perform the requested operation. The user
    or role that is making the request must have at least one IAM
    permissions policy attached that grants the required permissions. For
    more information, see `Access
    Management <https://docs.aws.amazon.com/IAM/latest/UserGuide/access.html>`__
    in the *IAM User Guide.*
    """

    Message: Optional[ExceptionMessage]


class AccessDeniedForDependencyException(ServiceException):
    """The operation that you attempted requires you to have the
    ``iam:CreateServiceLinkedRole`` for ``organizations.amazonaws.com``
    permission so that Organizations can create the required service-linked
    role. You don't have that permission.
    """

    Message: Optional[ExceptionMessage]
    Reason: Optional[AccessDeniedForDependencyExceptionReason]


class AccountAlreadyClosedException(ServiceException):
    """You attempted to close an account that is already closed."""

    Message: Optional[ExceptionMessage]


class AccountAlreadyRegisteredException(ServiceException):
    """The specified account is already a delegated administrator for this
    Amazon Web Services service.
    """

    Message: Optional[ExceptionMessage]


class AccountNotFoundException(ServiceException):
    """We can't find an Amazon Web Services account with the ``AccountId`` that
    you specified, or the account whose credentials you used to make this
    request isn't a member of an organization.
    """

    Message: Optional[ExceptionMessage]


class AccountNotRegisteredException(ServiceException):
    """The specified account is not a delegated administrator for this Amazon
    Web Services service.
    """

    Message: Optional[ExceptionMessage]


class AccountOwnerNotVerifiedException(ServiceException):
    """You can't invite an existing account to your organization until you
    verify that you own the email address associated with the management
    account. For more information, see `Email Address
    Verification <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_create.html#about-email-verification>`__
    in the *Organizations User Guide.*
    """

    Message: Optional[ExceptionMessage]


class AlreadyInOrganizationException(ServiceException):
    """This account is already a member of an organization. An account can
    belong to only one organization at a time.
    """

    Message: Optional[ExceptionMessage]


class ChildNotFoundException(ServiceException):
    """We can't find an organizational unit (OU) or Amazon Web Services account
    with the ``ChildId`` that you specified.
    """

    Message: Optional[ExceptionMessage]


class ConcurrentModificationException(ServiceException):
    """The target of the operation is currently being modified by a different
    request. Try again later.
    """

    Message: Optional[ExceptionMessage]


class ConflictException(ServiceException):
    """The request failed because it conflicts with the current state of the
    specified resource.
    """

    Message: Optional[ExceptionMessage]


class ConstraintViolationException(ServiceException):
    """Performing this operation violates a minimum or maximum value limit. For
    example, attempting to remove the last service control policy (SCP) from
    an OU or root, inviting or creating too many accounts to the
    organization, or attaching too many policies to an account, OU, or root.
    This exception includes a reason that contains additional information
    about the violated limit:

    Some of the reasons in the following list might not be applicable to
    this specific API or operation.

    -  ACCOUNT_CANNOT_LEAVE_ORGANIZATION: You attempted to remove the
       management account from the organization. You can't remove the
       management account. Instead, after you remove all member accounts,
       delete the organization itself.

    -  ACCOUNT_CANNOT_LEAVE_WITHOUT_PHONE_VERIFICATION: You attempted to
       remove an account from the organization that doesn't yet have enough
       information to exist as a standalone account. This account requires
       you to first complete phone verification. Follow the steps at
       `Removing a member account from your
       organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#orgs_manage_accounts_remove-from-master>`__
       in the *Organizations User Guide.*

    -  ACCOUNT_CREATION_RATE_LIMIT_EXCEEDED: You attempted to exceed the
       number of accounts that you can create in one day.

    -  ACCOUNT_NUMBER_LIMIT_EXCEEDED: You attempted to exceed the limit on
       the number of accounts in an organization. If you need more accounts,
       contact `Amazon Web Services
       Support <https://docs.aws.amazon.com/support/home#/>`__ to request an
       increase in your limit.

       Or the number of invitations that you tried to send would cause you
       to exceed the limit of accounts in your organization. Send fewer
       invitations or contact Amazon Web Services Support to request an
       increase in the number of accounts.

       Deleted and closed accounts still count toward your limit.

       If you get this exception when running a command immediately after
       creating the organization, wait one hour and try again. After an
       hour, if the command continues to fail with this error, contact
       `Amazon Web Services
       Support <https://docs.aws.amazon.com/support/home#/>`__.

    -  CANNOT_REGISTER_MASTER_AS_DELEGATED_ADMINISTRATOR: You attempted to
       register the management account of the organization as a delegated
       administrator for an Amazon Web Services service integrated with
       Organizations. You can designate only a member account as a delegated
       administrator.

    -  CANNOT_CLOSE_MANAGEMENT_ACCOUNT: You attempted to close the
       management account. To close the management account for the
       organization, you must first either remove or close all member
       accounts in the organization. Follow standard account closure process
       using root credentials.​

    -  CANNOT_REMOVE_DELEGATED_ADMINISTRATOR_FROM_ORG: You attempted to
       remove an account that is registered as a delegated administrator for
       a service integrated with your organization. To complete this
       operation, you must first deregister this account as a delegated
       administrator.

    -  CLOSE_ACCOUNT_QUOTA_EXCEEDED: You have exceeded close account quota
       for the past 30 days.

    -  CLOSE_ACCOUNT_REQUESTS_LIMIT_EXCEEDED: You attempted to exceed the
       number of accounts that you can close at a time. ​

    -  CREATE_ORGANIZATION_IN_BILLING_MODE_UNSUPPORTED_REGION: To create an
       organization in the specified region, you must enable all features
       mode.

    -  DELEGATED_ADMINISTRATOR_EXISTS_FOR_THIS_SERVICE: You attempted to
       register an Amazon Web Services account as a delegated administrator
       for an Amazon Web Services service that already has a delegated
       administrator. To complete this operation, you must first deregister
       any existing delegated administrators for this service.

    -  EMAIL_VERIFICATION_CODE_EXPIRED: The email verification code is only
       valid for a limited period of time. You must resubmit the request and
       generate a new verfication code.

    -  HANDSHAKE_RATE_LIMIT_EXCEEDED: You attempted to exceed the number of
       handshakes that you can send in one day.

    -  INVALID_PAYMENT_INSTRUMENT: You cannot remove an account because no
       supported payment method is associated with the account. Amazon Web
       Services does not support cards issued by financial institutions in
       Russia or Belarus. For more information, see `Managing your Amazon
       Web Services
       payments <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/manage-general.html>`__.

    -  MASTER_ACCOUNT_ADDRESS_DOES_NOT_MATCH_MARKETPLACE: To create an
       account in this organization, you first must migrate the
       organization's management account to the marketplace that corresponds
       to the management account's address. For example, accounts with India
       addresses must be associated with the AISPL marketplace. All accounts
       in an organization must be associated with the same marketplace.

    -  MASTER_ACCOUNT_MISSING_BUSINESS_LICENSE: Applies only to the Amazon
       Web Services /> Regions in China. To create an organization, the
       master must have a valid business license. For more information,
       contact customer support.

    -  MASTER_ACCOUNT_MISSING_CONTACT_INFO: To complete this operation, you
       must first provide a valid contact address and phone number for the
       management account. Then try the operation again.

    -  MASTER_ACCOUNT_NOT_GOVCLOUD_ENABLED: To complete this operation, the
       management account must have an associated account in the Amazon Web
       Services GovCloud (US-West) Region. For more information, see
       `Organizations <https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-organizations.html>`__
       in the *Amazon Web Services GovCloud User Guide.*

    -  MASTER_ACCOUNT_PAYMENT_INSTRUMENT_REQUIRED: To create an organization
       with this management account, you first must associate a valid
       payment instrument, such as a credit card, with the account. Follow
       the steps at `To leave an organization when all required account
       information has not yet been
       provided <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#leave-without-all-info>`__
       in the *Organizations User Guide.*

    -  MAX_DELEGATED_ADMINISTRATORS_FOR_SERVICE_LIMIT_EXCEEDED: You
       attempted to register more delegated administrators than allowed for
       the service principal.

    -  MAX_POLICY_TYPE_ATTACHMENT_LIMIT_EXCEEDED: You attempted to exceed
       the number of policies of a certain type that can be attached to an
       entity at one time.

    -  MAX_TAG_LIMIT_EXCEEDED: You have exceeded the number of tags allowed
       on this resource.

    -  MEMBER_ACCOUNT_PAYMENT_INSTRUMENT_REQUIRED: To complete this
       operation with this member account, you first must associate a valid
       payment instrument, such as a credit card, with the account. Follow
       the steps at `To leave an organization when all required account
       information has not yet been
       provided <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#leave-without-all-info>`__
       in the *Organizations User Guide.*

    -  MIN_POLICY_TYPE_ATTACHMENT_LIMIT_EXCEEDED: You attempted to detach a
       policy from an entity that would cause the entity to have fewer than
       the minimum number of policies of a certain type required.

    -  ORGANIZATION_NOT_IN_ALL_FEATURES_MODE: You attempted to perform an
       operation that requires the organization to be configured to support
       all features. An organization that supports only consolidated billing
       features can't perform this operation.

    -  OU_DEPTH_LIMIT_EXCEEDED: You attempted to create an OU tree that is
       too many levels deep.

    -  OU_NUMBER_LIMIT_EXCEEDED: You attempted to exceed the number of OUs
       that you can have in an organization.

    -  POLICY_CONTENT_LIMIT_EXCEEDED: You attempted to create a policy that
       is larger than the maximum size.

    -  POLICY_NUMBER_LIMIT_EXCEEDED: You attempted to exceed the number of
       policies that you can have in an organization.

    -  SERVICE_ACCESS_NOT_ENABLED: You attempted to register a delegated
       administrator before you enabled service access. Call the
       ``EnableAWSServiceAccess`` API first.

    -  TAG_POLICY_VIOLATION: You attempted to create or update a resource
       with tags that are not compliant with the tag policy requirements for
       this account.

    -  WAIT_PERIOD_ACTIVE: After you create an Amazon Web Services account,
       there is a waiting period before you can remove it from the
       organization. If you get an error that indicates that a wait period
       is required, try again in a few days.
    """

    Message: Optional[ExceptionMessage]
    Reason: Optional[ConstraintViolationExceptionReason]


class CreateAccountStatusNotFoundException(ServiceException):
    """We can't find an create account request with the
    ``CreateAccountRequestId`` that you specified.
    """

    Message: Optional[ExceptionMessage]


class DestinationParentNotFoundException(ServiceException):
    """We can't find the destination container (a root or OU) with the
    ``ParentId`` that you specified.
    """

    Message: Optional[ExceptionMessage]


class DuplicateAccountException(ServiceException):
    """That account is already present in the specified destination."""

    Message: Optional[ExceptionMessage]


class DuplicateHandshakeException(ServiceException):
    """A handshake with the same action and target already exists. For example,
    if you invited an account to join your organization, the invited account
    might already have a pending invitation from this organization. If you
    intend to resend an invitation to an account, ensure that existing
    handshakes that might be considered duplicates are canceled or declined.
    """

    Message: Optional[ExceptionMessage]


class DuplicateOrganizationalUnitException(ServiceException):
    """An OU with the same name already exists."""

    Message: Optional[ExceptionMessage]


class DuplicatePolicyAttachmentException(ServiceException):
    """The selected policy is already attached to the specified target."""

    Message: Optional[ExceptionMessage]


class DuplicatePolicyException(ServiceException):
    """A policy with the same name already exists."""

    Message: Optional[ExceptionMessage]


class EffectivePolicyNotFoundException(ServiceException):
    """If you ran this action on the management account, this policy type is
    not enabled. If you ran the action on a member account, the account
    doesn't have an effective policy of this type. Contact the administrator
    of your organization about attaching a policy of this type to the
    account.
    """

    Message: Optional[ExceptionMessage]


class FinalizingOrganizationException(ServiceException):
    """Organizations couldn't perform the operation because your organization
    hasn't finished initializing. This can take up to an hour. Try again
    later. If after one hour you continue to receive this error, contact
    `Amazon Web Services
    Support <https://console.aws.amazon.com/support/home#/>`__.
    """

    Message: Optional[ExceptionMessage]


class HandshakeAlreadyInStateException(ServiceException):
    """The specified handshake is already in the requested state. For example,
    you can't accept a handshake that was already accepted.
    """

    Message: Optional[ExceptionMessage]


class HandshakeConstraintViolationException(ServiceException):
    """The requested operation would violate the constraint identified in the
    reason code.

    Some of the reasons in the following list might not be applicable to
    this specific API or operation:

    -  ACCOUNT_NUMBER_LIMIT_EXCEEDED: You attempted to exceed the limit on
       the number of accounts in an organization. Note that deleted and
       closed accounts still count toward your limit.

       If you get this exception immediately after creating the
       organization, wait one hour and try again. If after an hour it
       continues to fail with this error, contact `Amazon Web Services
       Support <https://docs.aws.amazon.com/support/home#/>`__.

    -  ALREADY_IN_AN_ORGANIZATION: The handshake request is invalid because
       the invited account is already a member of an organization.

    -  HANDSHAKE_RATE_LIMIT_EXCEEDED: You attempted to exceed the number of
       handshakes that you can send in one day.

    -  INVITE_DISABLED_DURING_ENABLE_ALL_FEATURES: You can't issue new
       invitations to join an organization while it's in the process of
       enabling all features. You can resume inviting accounts after you
       finalize the process when all accounts have agreed to the change.

    -  ORGANIZATION_ALREADY_HAS_ALL_FEATURES: The handshake request is
       invalid because the organization has already enabled all features.

    -  ORGANIZATION_IS_ALREADY_PENDING_ALL_FEATURES_MIGRATION: The handshake
       request is invalid because the organization has already started the
       process to enable all features.

    -  ORGANIZATION_FROM_DIFFERENT_SELLER_OF_RECORD: The request failed
       because the account is from a different marketplace than the accounts
       in the organization. For example, accounts with India addresses must
       be associated with the AISPL marketplace. All accounts in an
       organization must be from the same marketplace.

    -  ORGANIZATION_MEMBERSHIP_CHANGE_RATE_LIMIT_EXCEEDED: You attempted to
       change the membership of an account too quickly after its previous
       change.

    -  PAYMENT_INSTRUMENT_REQUIRED: You can't complete the operation with an
       account that doesn't have a payment instrument, such as a credit
       card, associated with it.
    """

    Message: Optional[ExceptionMessage]
    Reason: Optional[HandshakeConstraintViolationExceptionReason]


class HandshakeNotFoundException(ServiceException):
    """We can't find a handshake with the ``HandshakeId`` that you specified."""

    Message: Optional[ExceptionMessage]


class InvalidHandshakeTransitionException(ServiceException):
    """You can't perform the operation on the handshake in its current state.
    For example, you can't cancel a handshake that was already accepted or
    accept a handshake that was already declined.
    """

    Message: Optional[ExceptionMessage]


class InvalidInputException(ServiceException):
    """The requested operation failed because you provided invalid values for
    one or more of the request parameters. This exception includes a reason
    that contains additional information about the violated limit:

    Some of the reasons in the following list might not be applicable to
    this specific API or operation.

    -  DUPLICATE_TAG_KEY: Tag keys must be unique among the tags attached to
       the same entity.

    -  IMMUTABLE_POLICY: You specified a policy that is managed by Amazon
       Web Services and can't be modified.

    -  INPUT_REQUIRED: You must include a value for all required parameters.

    -  INVALID_EMAIL_ADDRESS_TARGET: You specified an invalid email address
       for the invited account owner.

    -  INVALID_ENUM: You specified an invalid value.

    -  INVALID_ENUM_POLICY_TYPE: You specified an invalid policy type
       string.

    -  INVALID_FULL_NAME_TARGET: You specified a full name that contains
       invalid characters.

    -  INVALID_LIST_MEMBER: You provided a list to a parameter that contains
       at least one invalid value.

    -  INVALID_PAGINATION_TOKEN: Get the value for the ``NextToken``
       parameter from the response to a previous call of the operation.

    -  INVALID_PARTY_TYPE_TARGET: You specified the wrong type of entity
       (account, organization, or email) as a party.

    -  INVALID_PATTERN: You provided a value that doesn't match the required
       pattern.

    -  INVALID_PATTERN_TARGET_ID: You specified a policy target ID that
       doesn't match the required pattern.

    -  INVALID_ROLE_NAME: You provided a role name that isn't valid. A role
       name can't begin with the reserved prefix ``AWSServiceRoleFor``.

    -  INVALID_SYNTAX_ORGANIZATION_ARN: You specified an invalid Amazon
       Resource Name (ARN) for the organization.

    -  INVALID_SYNTAX_POLICY_ID: You specified an invalid policy ID.

    -  INVALID_SYSTEM_TAGS_PARAMETER: You specified a tag key that is a
       system tag. You can’t add, edit, or delete system tag keys because
       they're reserved for Amazon Web Services use. System tags don’t count
       against your tags per resource limit.

    -  MAX_FILTER_LIMIT_EXCEEDED: You can specify only one filter parameter
       for the operation.

    -  MAX_LENGTH_EXCEEDED: You provided a string parameter that is longer
       than allowed.

    -  MAX_VALUE_EXCEEDED: You provided a numeric parameter that has a
       larger value than allowed.

    -  MIN_LENGTH_EXCEEDED: You provided a string parameter that is shorter
       than allowed.

    -  MIN_VALUE_EXCEEDED: You provided a numeric parameter that has a
       smaller value than allowed.

    -  MOVING_ACCOUNT_BETWEEN_DIFFERENT_ROOTS: You can move an account only
       between entities in the same root.

    -  TARGET_NOT_SUPPORTED: You can't perform the specified operation on
       that target entity.

    -  UNRECOGNIZED_SERVICE_PRINCIPAL: You specified a service principal
       that isn't recognized.
    """

    Message: Optional[ExceptionMessage]
    Reason: Optional[InvalidInputExceptionReason]


class MalformedPolicyDocumentException(ServiceException):
    """The provided policy document doesn't meet the requirements of the
    specified policy type. For example, the syntax might be incorrect. For
    details about service control policy syntax, see `Service Control Policy
    Syntax <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_reference_scp-syntax.html>`__
    in the *Organizations User Guide.*
    """

    Message: Optional[ExceptionMessage]


class MasterCannotLeaveOrganizationException(ServiceException):
    """You can't remove a management account from an organization. If you want
    the management account to become a member account in another
    organization, you must first delete the current organization of the
    management account.
    """

    Message: Optional[ExceptionMessage]


class OrganizationNotEmptyException(ServiceException):
    """The organization isn't empty. To delete an organization, you must first
    remove all accounts except the management account, delete all OUs, and
    delete all policies.
    """

    Message: Optional[ExceptionMessage]


class OrganizationalUnitNotEmptyException(ServiceException):
    """The specified OU is not empty. Move all accounts to another root or to
    other OUs, remove all child OUs, and try the operation again.
    """

    Message: Optional[ExceptionMessage]


class OrganizationalUnitNotFoundException(ServiceException):
    """We can't find an OU with the ``OrganizationalUnitId`` that you
    specified.
    """

    Message: Optional[ExceptionMessage]


class ParentNotFoundException(ServiceException):
    """We can't find a root or OU with the ``ParentId`` that you specified."""

    Message: Optional[ExceptionMessage]


class PolicyChangesInProgressException(ServiceException):
    """Changes to the effective policy are in progress, and its contents can't
    be returned. Try the operation again later.
    """

    Message: Optional[ExceptionMessage]


class PolicyInUseException(ServiceException):
    """The policy is attached to one or more entities. You must detach it from
    all roots, OUs, and accounts before performing this operation.
    """

    Message: Optional[ExceptionMessage]


class PolicyNotAttachedException(ServiceException):
    """The policy isn't attached to the specified target in the specified root."""

    Message: Optional[ExceptionMessage]


class PolicyNotFoundException(ServiceException):
    """We can't find a policy with the ``PolicyId`` that you specified."""

    Message: Optional[ExceptionMessage]


class PolicyTypeAlreadyEnabledException(ServiceException):
    """The specified policy type is already enabled in the specified root."""

    Message: Optional[ExceptionMessage]


class PolicyTypeNotAvailableForOrganizationException(ServiceException):
    """You can't use the specified policy type with the feature set currently
    enabled for this organization. For example, you can enable SCPs only
    after you enable all features in the organization. For more information,
    see `Managing Organizations
    Policies <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#enable_policies_on_root>`__ in
    the *Organizations User Guide.*
    """

    Message: Optional[ExceptionMessage]


class PolicyTypeNotEnabledException(ServiceException):
    """The specified policy type isn't currently enabled in this root. You
    can't attach policies of the specified type to entities in a root until
    you enable that type in the root. For more information, see `Enabling
    All Features in Your
    Organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html>`__
    in the *Organizations User Guide.*
    """

    Message: Optional[ExceptionMessage]


class RootNotFoundException(ServiceException):
    """We can't find a root with the ``RootId`` that you specified."""

    Message: Optional[ExceptionMessage]


class ServiceException(ServiceException):
    """Organizations can't complete your request because of an internal service
    error. Try again later.
    """

    Message: Optional[ExceptionMessage]


class SourceParentNotFoundException(ServiceException):
    """We can't find a source root or OU with the ``ParentId`` that you
    specified.
    """

    Message: Optional[ExceptionMessage]


class TargetNotFoundException(ServiceException):
    """We can't find a root, OU, account, or policy with the ``TargetId`` that
    you specified.
    """

    Message: Optional[ExceptionMessage]


class TooManyRequestsException(ServiceException):
    """You have sent too many requests in too short a period of time. The quota
    helps protect against denial-of-service attacks. Try again later.

    For information about quotas that affect Organizations, see `Quotas for
    Organizations <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_reference_limits.html>`__ in
    the *Organizations User Guide.*
    """

    Type: Optional[ExceptionType]
    Message: Optional[ExceptionMessage]


class UnsupportedAPIEndpointException(ServiceException):
    """This action isn't available in the current Amazon Web Services Region."""

    Message: Optional[ExceptionMessage]


class AcceptHandshakeRequest(ServiceRequest):
    HandshakeId: HandshakeId


HandshakeResources = List["HandshakeResource"]


class HandshakeResource(TypedDict, total=False):
    """Contains additional data that is needed to process a handshake."""

    Value: Optional[HandshakeResourceValue]
    Type: Optional[HandshakeResourceType]
    Resources: Optional[HandshakeResources]


Timestamp = datetime


class HandshakeParty(TypedDict, total=False):
    """Identifies a participant in a handshake."""

    Id: HandshakePartyId
    Type: HandshakePartyType


HandshakeParties = List[HandshakeParty]


class Handshake(TypedDict, total=False):
    """Contains information that must be exchanged to securely establish a
    relationship between two accounts (an *originator* and a *recipient*).
    For example, when a management account (the originator) invites another
    account (the recipient) to join its organization, the two accounts
    exchange information as a series of handshake requests and responses.

    **Note:** Handshakes that are ``CANCELED``, ``ACCEPTED``, ``DECLINED``,
    or ``EXPIRED`` show up in lists for only 30 days after entering that
    state After that they are deleted.
    """

    Id: Optional[HandshakeId]
    Arn: Optional[HandshakeArn]
    Parties: Optional[HandshakeParties]
    State: Optional[HandshakeState]
    RequestedTimestamp: Optional[Timestamp]
    ExpirationTimestamp: Optional[Timestamp]
    Action: Optional[ActionType]
    Resources: Optional[HandshakeResources]


class AcceptHandshakeResponse(TypedDict, total=False):
    Handshake: Optional[Handshake]


class Account(TypedDict, total=False):
    """Contains information about an Amazon Web Services account that is a
    member of an organization.
    """

    Id: Optional[AccountId]
    Arn: Optional[AccountArn]
    Email: Optional[Email]
    Name: Optional[AccountName]
    Status: Optional[AccountStatus]
    JoinedMethod: Optional[AccountJoinedMethod]
    JoinedTimestamp: Optional[Timestamp]


Accounts = List[Account]


class AttachPolicyRequest(ServiceRequest):
    PolicyId: PolicyId
    TargetId: PolicyTargetId


class CancelHandshakeRequest(ServiceRequest):
    HandshakeId: HandshakeId


class CancelHandshakeResponse(TypedDict, total=False):
    Handshake: Optional[Handshake]


class Child(TypedDict, total=False):
    """Contains a list of child entities, either OUs or accounts."""

    Id: Optional[ChildId]
    Type: Optional[ChildType]


Children = List[Child]


class CloseAccountRequest(ServiceRequest):
    AccountId: AccountId


class Tag(TypedDict, total=False):
    """A custom key-value pair associated with a resource within your
    organization.

    You can attach tags to any of the following organization resources.

    -  Amazon Web Services account

    -  Organizational unit (OU)

    -  Organization root

    -  Policy
    """

    Key: TagKey
    Value: TagValue


Tags = List[Tag]


class CreateAccountRequest(ServiceRequest):
    Email: Email
    AccountName: CreateAccountName
    RoleName: Optional[RoleName]
    IamUserAccessToBilling: Optional[IAMUserAccessToBilling]
    Tags: Optional[Tags]


class CreateAccountStatus(TypedDict, total=False):
    """Contains the status about a CreateAccount or CreateGovCloudAccount
    request to create an Amazon Web Services account or an Amazon Web
    Services GovCloud (US) account in an organization.
    """

    Id: Optional[CreateAccountRequestId]
    AccountName: Optional[CreateAccountName]
    State: Optional[CreateAccountState]
    RequestedTimestamp: Optional[Timestamp]
    CompletedTimestamp: Optional[Timestamp]
    AccountId: Optional[AccountId]
    GovCloudAccountId: Optional[AccountId]
    FailureReason: Optional[CreateAccountFailureReason]


class CreateAccountResponse(TypedDict, total=False):
    CreateAccountStatus: Optional[CreateAccountStatus]


CreateAccountStates = List[CreateAccountState]
CreateAccountStatuses = List[CreateAccountStatus]


class CreateGovCloudAccountRequest(ServiceRequest):
    Email: Email
    AccountName: CreateAccountName
    RoleName: Optional[RoleName]
    IamUserAccessToBilling: Optional[IAMUserAccessToBilling]
    Tags: Optional[Tags]


class CreateGovCloudAccountResponse(TypedDict, total=False):
    CreateAccountStatus: Optional[CreateAccountStatus]


class CreateOrganizationRequest(ServiceRequest):
    FeatureSet: Optional[OrganizationFeatureSet]


class PolicyTypeSummary(TypedDict, total=False):
    """Contains information about a policy type and its status in the
    associated root.
    """

    Type: Optional[PolicyType]
    Status: Optional[PolicyTypeStatus]


PolicyTypes = List[PolicyTypeSummary]


class Organization(TypedDict, total=False):
    """Contains details about an organization. An organization is a collection
    of accounts that are centrally managed together using consolidated
    billing, organized hierarchically with organizational units (OUs), and
    controlled with policies .
    """

    Id: Optional[OrganizationId]
    Arn: Optional[OrganizationArn]
    FeatureSet: Optional[OrganizationFeatureSet]
    MasterAccountArn: Optional[AccountArn]
    MasterAccountId: Optional[AccountId]
    MasterAccountEmail: Optional[Email]
    AvailablePolicyTypes: Optional[PolicyTypes]


class CreateOrganizationResponse(TypedDict, total=False):
    Organization: Optional[Organization]


class CreateOrganizationalUnitRequest(ServiceRequest):
    ParentId: ParentId
    Name: OrganizationalUnitName
    Tags: Optional[Tags]


class OrganizationalUnit(TypedDict, total=False):
    """Contains details about an organizational unit (OU). An OU is a container
    of Amazon Web Services accounts within a root of an organization.
    Policies that are attached to an OU apply to all accounts contained in
    that OU and in any child OUs.
    """

    Id: Optional[OrganizationalUnitId]
    Arn: Optional[OrganizationalUnitArn]
    Name: Optional[OrganizationalUnitName]


class CreateOrganizationalUnitResponse(TypedDict, total=False):
    OrganizationalUnit: Optional[OrganizationalUnit]


class CreatePolicyRequest(ServiceRequest):
    Content: PolicyContent
    Description: PolicyDescription
    Name: PolicyName
    Type: PolicyType
    Tags: Optional[Tags]


class PolicySummary(TypedDict, total=False):
    """Contains information about a policy, but does not include the content.
    To see the content of a policy, see DescribePolicy.
    """

    Id: Optional[PolicyId]
    Arn: Optional[PolicyArn]
    Name: Optional[PolicyName]
    Description: Optional[PolicyDescription]
    Type: Optional[PolicyType]
    AwsManaged: Optional[AwsManagedPolicy]


class Policy(TypedDict, total=False):
    """Contains rules to be applied to the affected accounts. Policies can be
    attached directly to accounts, or to roots and OUs to affect all
    accounts in those hierarchies.
    """

    PolicySummary: Optional[PolicySummary]
    Content: Optional[PolicyContent]


class CreatePolicyResponse(TypedDict, total=False):
    Policy: Optional[Policy]


class DeclineHandshakeRequest(ServiceRequest):
    HandshakeId: HandshakeId


class DeclineHandshakeResponse(TypedDict, total=False):
    Handshake: Optional[Handshake]


class DelegatedAdministrator(TypedDict, total=False):
    """Contains information about the delegated administrator."""

    Id: Optional[AccountId]
    Arn: Optional[AccountArn]
    Email: Optional[Email]
    Name: Optional[AccountName]
    Status: Optional[AccountStatus]
    JoinedMethod: Optional[AccountJoinedMethod]
    JoinedTimestamp: Optional[Timestamp]
    DelegationEnabledDate: Optional[Timestamp]


DelegatedAdministrators = List[DelegatedAdministrator]


class DelegatedService(TypedDict, total=False):
    """Contains information about the Amazon Web Services service for which the
    account is a delegated administrator.
    """

    ServicePrincipal: Optional[ServicePrincipal]
    DelegationEnabledDate: Optional[Timestamp]


DelegatedServices = List[DelegatedService]


class DeleteOrganizationalUnitRequest(ServiceRequest):
    OrganizationalUnitId: OrganizationalUnitId


class DeletePolicyRequest(ServiceRequest):
    PolicyId: PolicyId


class DeregisterDelegatedAdministratorRequest(ServiceRequest):
    AccountId: AccountId
    ServicePrincipal: ServicePrincipal


class DescribeAccountRequest(ServiceRequest):
    AccountId: AccountId


class DescribeAccountResponse(TypedDict, total=False):
    Account: Optional[Account]


class DescribeCreateAccountStatusRequest(ServiceRequest):
    CreateAccountRequestId: CreateAccountRequestId


class DescribeCreateAccountStatusResponse(TypedDict, total=False):
    CreateAccountStatus: Optional[CreateAccountStatus]


class DescribeEffectivePolicyRequest(ServiceRequest):
    PolicyType: EffectivePolicyType
    TargetId: Optional[PolicyTargetId]


class EffectivePolicy(TypedDict, total=False):
    """Contains rules to be applied to the affected accounts. The effective
    policy is the aggregation of any policies the account inherits, plus any
    policy directly attached to the account.
    """

    PolicyContent: Optional[PolicyContent]
    LastUpdatedTimestamp: Optional[Timestamp]
    TargetId: Optional[PolicyTargetId]
    PolicyType: Optional[EffectivePolicyType]


class DescribeEffectivePolicyResponse(TypedDict, total=False):
    EffectivePolicy: Optional[EffectivePolicy]


class DescribeHandshakeRequest(ServiceRequest):
    HandshakeId: HandshakeId


class DescribeHandshakeResponse(TypedDict, total=False):
    Handshake: Optional[Handshake]


class DescribeOrganizationResponse(TypedDict, total=False):
    Organization: Optional[Organization]


class DescribeOrganizationalUnitRequest(ServiceRequest):
    OrganizationalUnitId: OrganizationalUnitId


class DescribeOrganizationalUnitResponse(TypedDict, total=False):
    OrganizationalUnit: Optional[OrganizationalUnit]


class DescribePolicyRequest(ServiceRequest):
    PolicyId: PolicyId


class DescribePolicyResponse(TypedDict, total=False):
    Policy: Optional[Policy]


class DetachPolicyRequest(ServiceRequest):
    PolicyId: PolicyId
    TargetId: PolicyTargetId


class DisableAWSServiceAccessRequest(ServiceRequest):
    ServicePrincipal: ServicePrincipal


class DisablePolicyTypeRequest(ServiceRequest):
    RootId: RootId
    PolicyType: PolicyType


class Root(TypedDict, total=False):
    """Contains details about a root. A root is a top-level parent node in the
    hierarchy of an organization that can contain organizational units (OUs)
    and accounts. The root contains every Amazon Web Services account in the
    organization.
    """

    Id: Optional[RootId]
    Arn: Optional[RootArn]
    Name: Optional[RootName]
    PolicyTypes: Optional[PolicyTypes]


class DisablePolicyTypeResponse(TypedDict, total=False):
    Root: Optional[Root]


class EnableAWSServiceAccessRequest(ServiceRequest):
    ServicePrincipal: ServicePrincipal


class EnableAllFeaturesRequest(ServiceRequest):
    pass


class EnableAllFeaturesResponse(TypedDict, total=False):
    Handshake: Optional[Handshake]


class EnablePolicyTypeRequest(ServiceRequest):
    RootId: RootId
    PolicyType: PolicyType


class EnablePolicyTypeResponse(TypedDict, total=False):
    Root: Optional[Root]


class EnabledServicePrincipal(TypedDict, total=False):
    """A structure that contains details of a service principal that represents
    an Amazon Web Services service that is enabled to integrate with
    Organizations.
    """

    ServicePrincipal: Optional[ServicePrincipal]
    DateEnabled: Optional[Timestamp]


EnabledServicePrincipals = List[EnabledServicePrincipal]


class HandshakeFilter(TypedDict, total=False):
    """Specifies the criteria that are used to select the handshakes for the
    operation.
    """

    ActionType: Optional[ActionType]
    ParentHandshakeId: Optional[HandshakeId]


Handshakes = List[Handshake]


class InviteAccountToOrganizationRequest(ServiceRequest):
    Target: HandshakeParty
    Notes: Optional[HandshakeNotes]
    Tags: Optional[Tags]


class InviteAccountToOrganizationResponse(TypedDict, total=False):
    Handshake: Optional[Handshake]


class ListAWSServiceAccessForOrganizationRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListAWSServiceAccessForOrganizationResponse(TypedDict, total=False):
    EnabledServicePrincipals: Optional[EnabledServicePrincipals]
    NextToken: Optional[NextToken]


class ListAccountsForParentRequest(ServiceRequest):
    ParentId: ParentId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListAccountsForParentResponse(TypedDict, total=False):
    Accounts: Optional[Accounts]
    NextToken: Optional[NextToken]


class ListAccountsRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListAccountsResponse(TypedDict, total=False):
    Accounts: Optional[Accounts]
    NextToken: Optional[NextToken]


class ListChildrenRequest(ServiceRequest):
    ParentId: ParentId
    ChildType: ChildType
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListChildrenResponse(TypedDict, total=False):
    Children: Optional[Children]
    NextToken: Optional[NextToken]


class ListCreateAccountStatusRequest(ServiceRequest):
    States: Optional[CreateAccountStates]
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListCreateAccountStatusResponse(TypedDict, total=False):
    CreateAccountStatuses: Optional[CreateAccountStatuses]
    NextToken: Optional[NextToken]


class ListDelegatedAdministratorsRequest(ServiceRequest):
    ServicePrincipal: Optional[ServicePrincipal]
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListDelegatedAdministratorsResponse(TypedDict, total=False):
    DelegatedAdministrators: Optional[DelegatedAdministrators]
    NextToken: Optional[NextToken]


class ListDelegatedServicesForAccountRequest(ServiceRequest):
    AccountId: AccountId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListDelegatedServicesForAccountResponse(TypedDict, total=False):
    DelegatedServices: Optional[DelegatedServices]
    NextToken: Optional[NextToken]


class ListHandshakesForAccountRequest(ServiceRequest):
    Filter: Optional[HandshakeFilter]
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListHandshakesForAccountResponse(TypedDict, total=False):
    Handshakes: Optional[Handshakes]
    NextToken: Optional[NextToken]


class ListHandshakesForOrganizationRequest(ServiceRequest):
    Filter: Optional[HandshakeFilter]
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListHandshakesForOrganizationResponse(TypedDict, total=False):
    Handshakes: Optional[Handshakes]
    NextToken: Optional[NextToken]


class ListOrganizationalUnitsForParentRequest(ServiceRequest):
    ParentId: ParentId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


OrganizationalUnits = List[OrganizationalUnit]


class ListOrganizationalUnitsForParentResponse(TypedDict, total=False):
    OrganizationalUnits: Optional[OrganizationalUnits]
    NextToken: Optional[NextToken]


class ListParentsRequest(ServiceRequest):
    ChildId: ChildId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class Parent(TypedDict, total=False):
    """Contains information about either a root or an organizational unit (OU)
    that can contain OUs or accounts in an organization.
    """

    Id: Optional[ParentId]
    Type: Optional[ParentType]


Parents = List[Parent]


class ListParentsResponse(TypedDict, total=False):
    Parents: Optional[Parents]
    NextToken: Optional[NextToken]


class ListPoliciesForTargetRequest(ServiceRequest):
    TargetId: PolicyTargetId
    Filter: PolicyType
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


Policies = List[PolicySummary]


class ListPoliciesForTargetResponse(TypedDict, total=False):
    Policies: Optional[Policies]
    NextToken: Optional[NextToken]


class ListPoliciesRequest(ServiceRequest):
    Filter: PolicyType
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class ListPoliciesResponse(TypedDict, total=False):
    Policies: Optional[Policies]
    NextToken: Optional[NextToken]


class ListRootsRequest(ServiceRequest):
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


Roots = List[Root]


class ListRootsResponse(TypedDict, total=False):
    Roots: Optional[Roots]
    NextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceId: TaggableResourceId
    NextToken: Optional[NextToken]


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[Tags]
    NextToken: Optional[NextToken]


class ListTargetsForPolicyRequest(ServiceRequest):
    PolicyId: PolicyId
    NextToken: Optional[NextToken]
    MaxResults: Optional[MaxResults]


class PolicyTargetSummary(TypedDict, total=False):
    """Contains information about a root, OU, or account that a policy is
    attached to.
    """

    TargetId: Optional[PolicyTargetId]
    Arn: Optional[GenericArn]
    Name: Optional[TargetName]
    Type: Optional[TargetType]


PolicyTargets = List[PolicyTargetSummary]


class ListTargetsForPolicyResponse(TypedDict, total=False):
    Targets: Optional[PolicyTargets]
    NextToken: Optional[NextToken]


class MoveAccountRequest(ServiceRequest):
    AccountId: AccountId
    SourceParentId: ParentId
    DestinationParentId: ParentId


class RegisterDelegatedAdministratorRequest(ServiceRequest):
    AccountId: AccountId
    ServicePrincipal: ServicePrincipal


class RemoveAccountFromOrganizationRequest(ServiceRequest):
    AccountId: AccountId


TagKeys = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceId: TaggableResourceId
    Tags: Tags


class UntagResourceRequest(ServiceRequest):
    ResourceId: TaggableResourceId
    TagKeys: TagKeys


class UpdateOrganizationalUnitRequest(ServiceRequest):
    OrganizationalUnitId: OrganizationalUnitId
    Name: Optional[OrganizationalUnitName]


class UpdateOrganizationalUnitResponse(TypedDict, total=False):
    OrganizationalUnit: Optional[OrganizationalUnit]


class UpdatePolicyRequest(ServiceRequest):
    PolicyId: PolicyId
    Name: Optional[PolicyName]
    Description: Optional[PolicyDescription]
    Content: Optional[PolicyContent]


class UpdatePolicyResponse(TypedDict, total=False):
    Policy: Optional[Policy]


class OrganizationsApi:

    service = "organizations"
    version = "2016-11-28"

    @handler("AcceptHandshake")
    def accept_handshake(
        self, context: RequestContext, handshake_id: HandshakeId
    ) -> AcceptHandshakeResponse:
        """Sends a response to the originator of a handshake agreeing to the action
        proposed by the handshake request.

        This operation can be called only by the following principals when they
        also have the relevant IAM permissions:

        -  **Invitation to join** or **Approve all features request**
           handshakes: only a principal from the member account.

           The user who calls the API for an invitation to join must have the
           ``organizations:AcceptHandshake`` permission. If you enabled all
           features in the organization, the user must also have the
           ``iam:CreateServiceLinkedRole`` permission so that Organizations can
           create the required service-linked role named
           ``AWSServiceRoleForOrganizations``. For more information, see
           `Organizations and Service-Linked
           Roles <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integration_services.html#orgs_integration_service-linked-roles>`__
           in the *Organizations User Guide*.

        -  **Enable all features final confirmation** handshake: only a
           principal from the management account.

           For more information about invitations, see `Inviting an Amazon Web
           Services account to join your
           organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_invites.html>`__
           in the *Organizations User Guide.* For more information about
           requests to enable all features in the organization, see `Enabling
           all features in your
           organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html>`__
           in the *Organizations User Guide.*

        After you accept a handshake, it continues to appear in the results of
        relevant APIs for only 30 days. After that, it's deleted.

        :param handshake_id: The unique identifier (ID) of the handshake that you want to accept.
        :returns: AcceptHandshakeResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises HandshakeConstraintViolationException:
        :raises HandshakeNotFoundException:
        :raises InvalidHandshakeTransitionException:
        :raises HandshakeAlreadyInStateException:
        :raises InvalidInputException:
        :raises ConcurrentModificationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises AccessDeniedForDependencyException:
        """
        raise NotImplementedError

    @handler("AttachPolicy")
    def attach_policy(
        self, context: RequestContext, policy_id: PolicyId, target_id: PolicyTargetId
    ) -> None:
        """Attaches a policy to a root, an organizational unit (OU), or an
        individual account. How the policy affects accounts depends on the type
        of policy. Refer to the *Organizations User Guide* for information about
        each policy type:

        -  `AISERVICES_OPT_OUT_POLICY <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out.html>`__

        -  `BACKUP_POLICY <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_backup.html>`__

        -  `SERVICE_CONTROL_POLICY <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scp.html>`__

        -  `TAG_POLICY <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_tag-policies.html>`__

        This operation can be called only from the organization's management
        account.

        :param policy_id: The unique identifier (ID) of the policy that you want to attach to the
        target.
        :param target_id: The unique identifier (ID) of the root, OU, or account that you want to
        attach the policy to.
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises DuplicatePolicyAttachmentException:
        :raises InvalidInputException:
        :raises PolicyNotFoundException:
        :raises PolicyTypeNotEnabledException:
        :raises ServiceException:
        :raises TargetNotFoundException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        :raises PolicyChangesInProgressException:
        """
        raise NotImplementedError

    @handler("CancelHandshake")
    def cancel_handshake(
        self, context: RequestContext, handshake_id: HandshakeId
    ) -> CancelHandshakeResponse:
        """Cancels a handshake. Canceling a handshake sets the handshake state to
        ``CANCELED``.

        This operation can be called only from the account that originated the
        handshake. The recipient of the handshake can't cancel it, but can use
        DeclineHandshake instead. After a handshake is canceled, the recipient
        can no longer respond to that handshake.

        After you cancel a handshake, it continues to appear in the results of
        relevant APIs for only 30 days. After that, it's deleted.

        :param handshake_id: The unique identifier (ID) of the handshake that you want to cancel.
        :returns: CancelHandshakeResponse
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        :raises HandshakeNotFoundException:
        :raises InvalidHandshakeTransitionException:
        :raises HandshakeAlreadyInStateException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("CloseAccount")
    def close_account(self, context: RequestContext, account_id: AccountId) -> None:
        """Closes an Amazon Web Services member account within an organization. You
        can't close the management account with this API. This is an
        asynchronous request that Amazon Web Services performs in the
        background. Because ``CloseAccount`` operates asynchronously, it can
        return a successful completion message even though account closure might
        still be in progress. You need to wait a few minutes before the account
        is fully closed. To check the status of the request, do one of the
        following:

        -  Use the ``AccountId`` that you sent in the ``CloseAccount`` request
           to provide as a parameter to the DescribeAccount operation.

           While the close account request is in progress, Account status will
           indicate PENDING_CLOSURE. When the close account request completes,
           the status will change to SUSPENDED.

        -  Check the CloudTrail log for the ``CloseAccountResult`` event that
           gets published after the account closes successfully. For information
           on using CloudTrail with Organizations, see `Logging and monitoring
           in
           Organizations <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_security_incident-response.html#orgs_cloudtrail-integration>`__
           in the *Organizations User Guide.*

        -  You can only close 10% of active member accounts within a rolling 30
           day period. This quota is not bound by a calendar month, but starts
           when you close an account. Within 30 days of that initial account
           closure, you can't exceed the 10% account closure limit.

        -  To reinstate a closed account, contact Amazon Web Services Support
           within the 90-day grace period while the account is in SUSPENDED
           status.

        -  If the Amazon Web Services account you attempt to close is linked to
           an Amazon Web Services GovCloud (US) account, the ``CloseAccount``
           request will close both accounts. To learn important pre-closure
           details, see `Closing an Amazon Web Services GovCloud (US)
           account <https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/Closing-govcloud-account.html>`__
           in the *Amazon Web Services GovCloud User Guide*.

        For more information about closing accounts, see `Closing an Amazon Web
        Services
        account <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_close.html>`__
        in the *Organizations User Guide.*

        :param account_id: Retrieves the Amazon Web Services account Id for the current
        ``CloseAccount`` API request.
        :raises AccessDeniedException:
        :raises AccountAlreadyClosedException:
        :raises AccountNotFoundException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConflictException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("CreateAccount")
    def create_account(
        self,
        context: RequestContext,
        email: Email,
        account_name: CreateAccountName,
        role_name: RoleName = None,
        iam_user_access_to_billing: IAMUserAccessToBilling = None,
        tags: Tags = None,
    ) -> CreateAccountResponse:
        """Creates an Amazon Web Services account that is automatically a member of
        the organization whose credentials made the request. This is an
        asynchronous request that Amazon Web Services performs in the
        background. Because ``CreateAccount`` operates asynchronously, it can
        return a successful completion message even though account
        initialization might still be in progress. You might need to wait a few
        minutes before you can successfully access the account. To check the
        status of the request, do one of the following:

        -  Use the ``Id`` member of the ``CreateAccountStatus`` response element
           from this operation to provide as a parameter to the
           DescribeCreateAccountStatus operation.

        -  Check the CloudTrail log for the ``CreateAccountResult`` event. For
           information on using CloudTrail with Organizations, see `Logging and
           monitoring in
           Organizations <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_security_incident-response.html#orgs_cloudtrail-integration>`__
           in the *Organizations User Guide.*

        The user who calls the API to create an account must have the
        ``organizations:CreateAccount`` permission. If you enabled all features
        in the organization, Organizations creates the required service-linked
        role named ``AWSServiceRoleForOrganizations``. For more information, see
        `Organizations and Service-Linked
        Roles <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html#orgs_integrate_services-using_slrs>`__
        in the *Organizations User Guide*.

        If the request includes tags, then the requester must have the
        ``organizations:TagResource`` permission.

        Organizations preconfigures the new member account with a role (named
        ``OrganizationAccountAccessRole`` by default) that grants users in the
        management account administrator permissions in the new member account.
        Principals in the management account can assume the role. Organizations
        clones the company name and address information for the new account from
        the organization's management account.

        This operation can be called only from the organization's management
        account.

        For more information about creating accounts, see `Creating an Amazon
        Web Services account in Your
        Organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_create.html>`__
        in the *Organizations User Guide.*

        -  When you create an account in an organization using the Organizations
           console, API, or CLI commands, the information required for the
           account to operate as a standalone account, such as a payment method
           and signing the end user license agreement (EULA) is *not*
           automatically collected. If you must remove an account from your
           organization later, you can do so only after you provide the missing
           information. Follow the steps at `To leave an organization as a
           member
           account <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#leave-without-all-info>`__
           in the *Organizations User Guide*.

        -  If you get an exception that indicates that you exceeded your account
           limits for the organization, contact `Amazon Web Services
           Support <https://console.aws.amazon.com/support/home#/>`__.

        -  If you get an exception that indicates that the operation failed
           because your organization is still initializing, wait one hour and
           then try again. If the error persists, contact `Amazon Web Services
           Support <https://console.aws.amazon.com/support/home#/>`__.

        -  Using ``CreateAccount`` to create multiple temporary accounts isn't
           recommended. You can only close an account from the Billing and Cost
           Management console, and you must be signed in as the root user. For
           information on the requirements and process for closing an account,
           see `Closing an Amazon Web Services
           account <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_close.html>`__
           in the *Organizations User Guide*.

        When you create a member account with this operation, you can choose
        whether to create the account with the **IAM User and Role Access to
        Billing Information** switch enabled. If you enable it, IAM users and
        roles that have appropriate permissions can view billing information for
        the account. If you disable it, only the account root user can access
        billing information. For information about how to disable this switch
        for an account, see `Granting Access to Your Billing Information and
        Tools <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/grantaccess.html>`__.

        :param email: The email address of the owner to assign to the new member account.
        :param account_name: The friendly name of the member account.
        :param role_name: (Optional)

        The name of an IAM role that Organizations automatically preconfigures
        in the new member account.
        :param iam_user_access_to_billing: If set to ``ALLOW``, the new account enables IAM users to access account
        billing information *if* they have the required permissions.
        :param tags: A list of tags that you want to attach to the newly created account.
        :returns: CreateAccountResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises FinalizingOrganizationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("CreateGovCloudAccount")
    def create_gov_cloud_account(
        self,
        context: RequestContext,
        email: Email,
        account_name: CreateAccountName,
        role_name: RoleName = None,
        iam_user_access_to_billing: IAMUserAccessToBilling = None,
        tags: Tags = None,
    ) -> CreateGovCloudAccountResponse:
        """This action is available if all of the following are true:

        -  You're authorized to create accounts in the Amazon Web Services
           GovCloud (US) Region. For more information on the Amazon Web Services
           GovCloud (US) Region, see the `Amazon Web Services GovCloud User
           Guide. <https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/welcome.html>`__

        -  You already have an account in the Amazon Web Services GovCloud (US)
           Region that is paired with a management account of an organization in
           the commercial Region.

        -  You call this action from the management account of your organization
           in the commercial Region.

        -  You have the ``organizations:CreateGovCloudAccount`` permission.

        Organizations automatically creates the required service-linked role
        named ``AWSServiceRoleForOrganizations``. For more information, see
        `Organizations and Service-Linked
        Roles <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html#orgs_integrate_services-using_slrs>`__
        in the *Organizations User Guide.*

        Amazon Web Services automatically enables CloudTrail for Amazon Web
        Services GovCloud (US) accounts, but you should also do the following:

        -  Verify that CloudTrail is enabled to store logs.

        -  Create an Amazon S3 bucket for CloudTrail log storage.

           For more information, see `Verifying CloudTrail Is
           Enabled <https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/verifying-cloudtrail.html>`__
           in the *Amazon Web Services GovCloud User Guide*.

        If the request includes tags, then the requester must have the
        ``organizations:TagResource`` permission. The tags are attached to the
        commercial account associated with the GovCloud account, rather than the
        GovCloud account itself. To add tags to the GovCloud account, call the
        TagResource operation in the GovCloud Region after the new GovCloud
        account exists.

        You call this action from the management account of your organization in
        the commercial Region to create a standalone Amazon Web Services account
        in the Amazon Web Services GovCloud (US) Region. After the account is
        created, the management account of an organization in the Amazon Web
        Services GovCloud (US) Region can invite it to that organization. For
        more information on inviting standalone accounts in the Amazon Web
        Services GovCloud (US) to join an organization, see
        `Organizations <https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-organizations.html>`__
        in the *Amazon Web Services GovCloud User Guide.*

        Calling ``CreateGovCloudAccount`` is an asynchronous request that Amazon
        Web Services performs in the background. Because
        ``CreateGovCloudAccount`` operates asynchronously, it can return a
        successful completion message even though account initialization might
        still be in progress. You might need to wait a few minutes before you
        can successfully access the account. To check the status of the request,
        do one of the following:

        -  Use the ``OperationId`` response element from this operation to
           provide as a parameter to the DescribeCreateAccountStatus operation.

        -  Check the CloudTrail log for the ``CreateAccountResult`` event. For
           information on using CloudTrail with Organizations, see `Monitoring
           the Activity in Your
           Organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_monitoring.html>`__
           in the *Organizations User Guide.*

        When you call the ``CreateGovCloudAccount`` action, you create two
        accounts: a standalone account in the Amazon Web Services GovCloud (US)
        Region and an associated account in the commercial Region for billing
        and support purposes. The account in the commercial Region is
        automatically a member of the organization whose credentials made the
        request. Both accounts are associated with the same email address.

        A role is created in the new account in the commercial Region that
        allows the management account in the organization in the commercial
        Region to assume it. An Amazon Web Services GovCloud (US) account is
        then created and associated with the commercial account that you just
        created. A role is also created in the new Amazon Web Services GovCloud
        (US) account that can be assumed by the Amazon Web Services GovCloud
        (US) account that is associated with the management account of the
        commercial organization. For more information and to view a diagram that
        explains how account access works, see
        `Organizations <https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-organizations.html>`__
        in the *Amazon Web Services GovCloud User Guide.*

        For more information about creating accounts, see `Creating an Amazon
        Web Services account in Your
        Organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_create.html>`__
        in the *Organizations User Guide.*

        -  When you create an account in an organization using the Organizations
           console, API, or CLI commands, the information required for the
           account to operate as a standalone account is *not* automatically
           collected. This includes a payment method and signing the end user
           license agreement (EULA). If you must remove an account from your
           organization later, you can do so only after you provide the missing
           information. Follow the steps at `To leave an organization as a
           member
           account <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#leave-without-all-info>`__
           in the *Organizations User Guide.*

        -  If you get an exception that indicates that you exceeded your account
           limits for the organization, contact `Amazon Web Services
           Support <https://console.aws.amazon.com/support/home#/>`__.

        -  If you get an exception that indicates that the operation failed
           because your organization is still initializing, wait one hour and
           then try again. If the error persists, contact `Amazon Web Services
           Support <https://console.aws.amazon.com/support/home#/>`__.

        -  Using ``CreateGovCloudAccount`` to create multiple temporary accounts
           isn't recommended. You can only close an account from the Amazon Web
           Services Billing and Cost Management console, and you must be signed
           in as the root user. For information on the requirements and process
           for closing an account, see `Closing an Amazon Web Services
           account <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_close.html>`__
           in the *Organizations User Guide*.

        When you create a member account with this operation, you can choose
        whether to create the account with the **IAM User and Role Access to
        Billing Information** switch enabled. If you enable it, IAM users and
        roles that have appropriate permissions can view billing information for
        the account. If you disable it, only the account root user can access
        billing information. For information about how to disable this switch
        for an account, see `Granting Access to Your Billing Information and
        Tools <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/grantaccess.html>`__.

        :param email: Specifies the email address of the owner to assign to the new member
        account in the commercial Region.
        :param account_name: The friendly name of the member account.
        :param role_name: (Optional)

        The name of an IAM role that Organizations automatically preconfigures
        in the new member accounts in both the Amazon Web Services GovCloud (US)
        Region and in the commercial Region.
        :param iam_user_access_to_billing: If set to ``ALLOW``, the new linked account in the commercial Region
        enables IAM users to access account billing information *if* they have
        the required permissions.
        :param tags: A list of tags that you want to attach to the newly created account.
        :returns: CreateGovCloudAccountResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises FinalizingOrganizationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("CreateOrganization")
    def create_organization(
        self, context: RequestContext, feature_set: OrganizationFeatureSet = None
    ) -> CreateOrganizationResponse:
        """Creates an Amazon Web Services organization. The account whose user is
        calling the ``CreateOrganization`` operation automatically becomes the
        `management
        account <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#account>`__
        of the new organization.

        This operation must be called using credentials from the account that is
        to become the new organization's management account. The principal must
        also have the relevant IAM permissions.

        By default (or if you set the ``FeatureSet`` parameter to ``ALL``), the
        new organization is created with all features enabled and service
        control policies automatically enabled in the root. If you instead
        choose to create the organization supporting only the consolidated
        billing features by setting the ``FeatureSet`` parameter to
        ``CONSOLIDATED_BILLING"``, no policy types are enabled by default, and
        you can't use organization policies

        :param feature_set: Specifies the feature set supported by the new organization.
        :returns: CreateOrganizationResponse
        :raises AccessDeniedException:
        :raises AlreadyInOrganizationException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises AccessDeniedForDependencyException:
        """
        raise NotImplementedError

    @handler("CreateOrganizationalUnit")
    def create_organizational_unit(
        self,
        context: RequestContext,
        parent_id: ParentId,
        name: OrganizationalUnitName,
        tags: Tags = None,
    ) -> CreateOrganizationalUnitResponse:
        """Creates an organizational unit (OU) within a root or parent OU. An OU is
        a container for accounts that enables you to organize your accounts to
        apply policies according to your business requirements. The number of
        levels deep that you can nest OUs is dependent upon the policy types
        enabled for that root. For service control policies, the limit is five.

        For more information about OUs, see `Managing Organizational
        Units <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html>`__
        in the *Organizations User Guide.*

        If the request includes tags, then the requester must have the
        ``organizations:TagResource`` permission.

        This operation can be called only from the organization's management
        account.

        :param parent_id: The unique identifier (ID) of the parent root or OU that you want to
        create the new OU in.
        :param name: The friendly name to assign to the new OU.
        :param tags: A list of tags that you want to attach to the newly created OU.
        :returns: CreateOrganizationalUnitResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises DuplicateOrganizationalUnitException:
        :raises InvalidInputException:
        :raises ParentNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("CreatePolicy", expand=False)
    def create_policy(
        self, context: RequestContext, request: CreatePolicyRequest
    ) -> CreatePolicyResponse:
        """Creates a policy of a specified type that you can attach to a root, an
        organizational unit (OU), or an individual Amazon Web Services account.

        For more information about policies and their use, see `Managing
        Organization
        Policies <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html>`__.

        If the request includes tags, then the requester must have the
        ``organizations:TagResource`` permission.

        This operation can be called only from the organization's management
        account.

        :param content: The policy text content to add to the new policy.
        :param description: An optional description to assign to the policy.
        :param name: The friendly name to assign to the policy.
        :param type: The type of policy to create.
        :param tags: A list of tags that you want to attach to the newly created policy.
        :returns: CreatePolicyResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises DuplicatePolicyException:
        :raises InvalidInputException:
        :raises MalformedPolicyDocumentException:
        :raises PolicyTypeNotAvailableForOrganizationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DeclineHandshake")
    def decline_handshake(
        self, context: RequestContext, handshake_id: HandshakeId
    ) -> DeclineHandshakeResponse:
        """Declines a handshake request. This sets the handshake state to
        ``DECLINED`` and effectively deactivates the request.

        This operation can be called only from the account that received the
        handshake. The originator of the handshake can use CancelHandshake
        instead. The originator can't reactivate a declined request, but can
        reinitiate the process with a new handshake request.

        After you decline a handshake, it continues to appear in the results of
        relevant APIs for only 30 days. After that, it's deleted.

        :param handshake_id: The unique identifier (ID) of the handshake that you want to decline.
        :returns: DeclineHandshakeResponse
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        :raises HandshakeNotFoundException:
        :raises InvalidHandshakeTransitionException:
        :raises HandshakeAlreadyInStateException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteOrganization")
    def delete_organization(
        self,
        context: RequestContext,
    ) -> None:
        """Deletes the organization. You can delete an organization only by using
        credentials from the management account. The organization must be empty
        of member accounts.

        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises InvalidInputException:
        :raises OrganizationNotEmptyException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteOrganizationalUnit")
    def delete_organizational_unit(
        self, context: RequestContext, organizational_unit_id: OrganizationalUnitId
    ) -> None:
        """Deletes an organizational unit (OU) from a root or another OU. You must
        first remove all accounts and child OUs from the OU that you want to
        delete.

        This operation can be called only from the organization's management
        account.

        :param organizational_unit_id: The unique identifier (ID) of the organizational unit that you want to
        delete.
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises InvalidInputException:
        :raises OrganizationalUnitNotEmptyException:
        :raises OrganizationalUnitNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeletePolicy")
    def delete_policy(self, context: RequestContext, policy_id: PolicyId) -> None:
        """Deletes the specified policy from your organization. Before you perform
        this operation, you must first detach the policy from all organizational
        units (OUs), roots, and accounts.

        This operation can be called only from the organization's management
        account.

        :param policy_id: The unique identifier (ID) of the policy that you want to delete.
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises InvalidInputException:
        :raises PolicyInUseException:
        :raises PolicyNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DeregisterDelegatedAdministrator")
    def deregister_delegated_administrator(
        self, context: RequestContext, account_id: AccountId, service_principal: ServicePrincipal
    ) -> None:
        """Removes the specified member Amazon Web Services account as a delegated
        administrator for the specified Amazon Web Services service.

        Deregistering a delegated administrator can have unintended impacts on
        the functionality of the enabled Amazon Web Services service. See the
        documentation for the enabled service before you deregister a delegated
        administrator so that you understand any potential impacts.

        You can run this action only for Amazon Web Services services that
        support this feature. For a current list of services that support it,
        see the column *Supports Delegated Administrator* in the table at
        `Amazon Web Services Services that you can use with
        Organizations <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html>`__
        in the *Organizations User Guide.*

        This operation can be called only from the organization's management
        account.

        :param account_id: The account ID number of the member account in the organization that you
        want to deregister as a delegated administrator.
        :param service_principal: The service principal name of an Amazon Web Services service for which
        the account is a delegated administrator.
        :raises AccessDeniedException:
        :raises AccountNotFoundException:
        :raises AccountNotRegisteredException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises TooManyRequestsException:
        :raises ServiceException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DescribeAccount")
    def describe_account(
        self, context: RequestContext, account_id: AccountId
    ) -> DescribeAccountResponse:
        """Retrieves Organizations-related information about the specified account.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param account_id: The unique identifier (ID) of the Amazon Web Services account that you
        want information about.
        :returns: DescribeAccountResponse
        :raises AccessDeniedException:
        :raises AccountNotFoundException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DescribeCreateAccountStatus")
    def describe_create_account_status(
        self, context: RequestContext, create_account_request_id: CreateAccountRequestId
    ) -> DescribeCreateAccountStatusResponse:
        """Retrieves the current status of an asynchronous request to create an
        account.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param create_account_request_id: Specifies the ``Id`` value that uniquely identifies the
        ``CreateAccount`` request.
        :returns: DescribeCreateAccountStatusResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises CreateAccountStatusNotFoundException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DescribeEffectivePolicy")
    def describe_effective_policy(
        self,
        context: RequestContext,
        policy_type: EffectivePolicyType,
        target_id: PolicyTargetId = None,
    ) -> DescribeEffectivePolicyResponse:
        """Returns the contents of the effective policy for specified policy type
        and account. The effective policy is the aggregation of any policies of
        the specified type that the account inherits, plus any policy of that
        type that is directly attached to the account.

        This operation applies only to policy types *other* than service control
        policies (SCPs).

        For more information about policy inheritance, see `How Policy
        Inheritance
        Works <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies-inheritance.html>`__
        in the *Organizations User Guide*.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param policy_type: The type of policy that you want information about.
        :param target_id: When you're signed in as the management account, specify the ID of the
        account that you want details about.
        :returns: DescribeEffectivePolicyResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConstraintViolationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises TargetNotFoundException:
        :raises EffectivePolicyNotFoundException:
        :raises InvalidInputException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DescribeHandshake")
    def describe_handshake(
        self, context: RequestContext, handshake_id: HandshakeId
    ) -> DescribeHandshakeResponse:
        """Retrieves information about a previously requested handshake. The
        handshake ID comes from the response to the original
        InviteAccountToOrganization operation that generated the handshake.

        You can access handshakes that are ``ACCEPTED``, ``DECLINED``, or
        ``CANCELED`` for only 30 days after they change to that state. They're
        then deleted and no longer accessible.

        This operation can be called from any account in the organization.

        :param handshake_id: The unique identifier (ID) of the handshake that you want information
        about.
        :returns: DescribeHandshakeResponse
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        :raises HandshakeNotFoundException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DescribeOrganization")
    def describe_organization(
        self,
        context: RequestContext,
    ) -> DescribeOrganizationResponse:
        """Retrieves information about the organization that the user's account
        belongs to.

        This operation can be called from any account in the organization.

        Even if a policy type is shown as available in the organization, you can
        disable it separately at the root level with DisablePolicyType. Use
        ListRoots to see the status of policy types for a specified root.

        :returns: DescribeOrganizationResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DescribeOrganizationalUnit")
    def describe_organizational_unit(
        self, context: RequestContext, organizational_unit_id: OrganizationalUnitId
    ) -> DescribeOrganizationalUnitResponse:
        """Retrieves information about an organizational unit (OU).

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param organizational_unit_id: The unique identifier (ID) of the organizational unit that you want
        details about.
        :returns: DescribeOrganizationalUnitResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises OrganizationalUnitNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DescribePolicy")
    def describe_policy(
        self, context: RequestContext, policy_id: PolicyId
    ) -> DescribePolicyResponse:
        """Retrieves information about a policy.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param policy_id: The unique identifier (ID) of the policy that you want details about.
        :returns: DescribePolicyResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises PolicyNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DetachPolicy")
    def detach_policy(
        self, context: RequestContext, policy_id: PolicyId, target_id: PolicyTargetId
    ) -> None:
        """Detaches a policy from a target root, organizational unit (OU), or
        account.

        If the policy being detached is a service control policy (SCP), the
        changes to permissions for Identity and Access Management (IAM) users
        and roles in affected accounts are immediate.

        Every root, OU, and account must have at least one SCP attached. If you
        want to replace the default ``FullAWSAccess`` policy with an SCP that
        limits the permissions that can be delegated, you must attach the
        replacement SCP before you can remove the default SCP. This is the
        authorization strategy of an "`allow
        list <https://docs.aws.amazon.com/organizations/latest/userguide/SCP_strategies.html#orgs_policies_allowlist>`__".
        If you instead attach a second SCP and leave the ``FullAWSAccess`` SCP
        still attached, and specify ``"Effect": "Deny"`` in the second SCP to
        override the ``"Effect": "Allow"`` in the ``FullAWSAccess`` policy (or
        any other attached SCP), you're using the authorization strategy of a
        "`deny
        list <https://docs.aws.amazon.com/organizations/latest/userguide/SCP_strategies.html#orgs_policies_denylist>`__".

        This operation can be called only from the organization's management
        account.

        :param policy_id: The unique identifier (ID) of the policy you want to detach.
        :param target_id: The unique identifier (ID) of the root, OU, or account that you want to
        detach the policy from.
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises PolicyNotAttachedException:
        :raises PolicyNotFoundException:
        :raises ServiceException:
        :raises TargetNotFoundException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        :raises PolicyChangesInProgressException:
        """
        raise NotImplementedError

    @handler("DisableAWSServiceAccess")
    def disable_aws_service_access(
        self, context: RequestContext, service_principal: ServicePrincipal
    ) -> None:
        """Disables the integration of an Amazon Web Services service (the service
        that is specified by ``ServicePrincipal``) with Organizations. When you
        disable integration, the specified service no longer can create a
        `service-linked
        role <https://docs.aws.amazon.com/IAM/latest/UserGuide/using-service-linked-roles.html>`__
        in *new* accounts in your organization. This means the service can't
        perform operations on your behalf on any new accounts in your
        organization. The service can still perform operations in older accounts
        until the service completes its clean-up from Organizations.

        We **strongly recommend** that you don't use this command to disable
        integration between Organizations and the specified Amazon Web Services
        service. Instead, use the console or commands that are provided by the
        specified service. This lets the trusted service perform any required
        initialization when enabling trusted access, such as creating any
        required resources and any required clean up of resources when disabling
        trusted access.

        For information about how to disable trusted service access to your
        organization using the trusted service, see the **Learn more** link
        under the **Supports Trusted Access** column at `Amazon Web Services
        services that you can use with
        Organizations <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html>`__.
        on this page.

        If you disable access by using this command, it causes the following
        actions to occur:

        -  The service can no longer create a service-linked role in the
           accounts in your organization. This means that the service can't
           perform operations on your behalf on any new accounts in your
           organization. The service can still perform operations in older
           accounts until the service completes its clean-up from Organizations.

        -  The service can no longer perform tasks in the member accounts in the
           organization, unless those operations are explicitly permitted by the
           IAM policies that are attached to your roles. This includes any data
           aggregation from the member accounts to the management account, or to
           a delegated administrator account, where relevant.

        -  Some services detect this and clean up any remaining data or
           resources related to the integration, while other services stop
           accessing the organization but leave any historical data and
           configuration in place to support a possible re-enabling of the
           integration.

        Using the other service's console or commands to disable the integration
        ensures that the other service is aware that it can clean up any
        resources that are required only for the integration. How the service
        cleans up its resources in the organization's accounts depends on that
        service. For more information, see the documentation for the other
        Amazon Web Services service.

        After you perform the ``DisableAWSServiceAccess`` operation, the
        specified service can no longer perform operations in your
        organization's accounts

        For more information about integrating other services with
        Organizations, including the list of services that work with
        Organizations, see `Integrating Organizations with Other Amazon Web
        Services
        Services <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html>`__
        in the *Organizations User Guide.*

        This operation can be called only from the organization's management
        account.

        :param service_principal: The service principal name of the Amazon Web Services service for which
        you want to disable integration with your organization.
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("DisablePolicyType")
    def disable_policy_type(
        self, context: RequestContext, root_id: RootId, policy_type: PolicyType
    ) -> DisablePolicyTypeResponse:
        """Disables an organizational policy type in a root. A policy of a certain
        type can be attached to entities in a root only if that type is enabled
        in the root. After you perform this operation, you no longer can attach
        policies of the specified type to that root or to any organizational
        unit (OU) or account in that root. You can undo this by using the
        EnablePolicyType operation.

        This is an asynchronous request that Amazon Web Services performs in the
        background. If you disable a policy type for a root, it still appears
        enabled for the organization if `all
        features <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html>`__
        are enabled for the organization. Amazon Web Services recommends that
        you first use ListRoots to see the status of policy types for a
        specified root, and then use this operation.

        This operation can be called only from the organization's management
        account.

        To view the status of available policy types in the organization, use
        DescribeOrganization.

        :param root_id: The unique identifier (ID) of the root in which you want to disable a
        policy type.
        :param policy_type: The policy type that you want to disable in this root.
        :returns: DisablePolicyTypeResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises PolicyTypeNotEnabledException:
        :raises RootNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        :raises PolicyChangesInProgressException:
        """
        raise NotImplementedError

    @handler("EnableAWSServiceAccess")
    def enable_aws_service_access(
        self, context: RequestContext, service_principal: ServicePrincipal
    ) -> None:
        """Enables the integration of an Amazon Web Services service (the service
        that is specified by ``ServicePrincipal``) with Organizations. When you
        enable integration, you allow the specified service to create a
        `service-linked
        role <https://docs.aws.amazon.com/IAM/latest/UserGuide/using-service-linked-roles.html>`__
        in all the accounts in your organization. This allows the service to
        perform operations on your behalf in your organization and its accounts.

        We recommend that you enable integration between Organizations and the
        specified Amazon Web Services service by using the console or commands
        that are provided by the specified service. Doing so ensures that the
        service is aware that it can create the resources that are required for
        the integration. How the service creates those resources in the
        organization's accounts depends on that service. For more information,
        see the documentation for the other Amazon Web Services service.

        For more information about enabling services to integrate with
        Organizations, see `Integrating Organizations with Other Amazon Web
        Services
        Services <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html>`__
        in the *Organizations User Guide.*

        This operation can be called only from the organization's management
        account and only if the organization has `enabled all
        features <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html>`__.

        :param service_principal: The service principal name of the Amazon Web Services service for which
        you want to enable integration with your organization.
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("EnableAllFeatures")
    def enable_all_features(
        self,
        context: RequestContext,
    ) -> EnableAllFeaturesResponse:
        """Enables all features in an organization. This enables the use of
        organization policies that can restrict the services and actions that
        can be called in each account. Until you enable all features, you have
        access only to consolidated billing, and you can't use any of the
        advanced account administration features that Organizations supports.
        For more information, see `Enabling All Features in Your
        Organization <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html>`__
        in the *Organizations User Guide.*

        This operation is required only for organizations that were created
        explicitly with only the consolidated billing features enabled. Calling
        this operation sends a handshake to every invited account in the
        organization. The feature set change can be finalized and the additional
        features enabled only after all administrators in the invited accounts
        approve the change by accepting the handshake.

        After you enable all features, you can separately enable or disable
        individual policy types in a root using EnablePolicyType and
        DisablePolicyType. To see the status of policy types in a root, use
        ListRoots.

        After all invited member accounts accept the handshake, you finalize the
        feature set change by accepting the handshake that contains
        ``"Action": "ENABLE_ALL_FEATURES"``. This completes the change.

        After you enable all features in your organization, the management
        account in the organization can apply policies on all member accounts.
        These policies can restrict what users and even administrators in those
        accounts can do. The management account can apply policies that prevent
        accounts from leaving the organization. Ensure that your account
        administrators are aware of this.

        This operation can be called only from the organization's management
        account.

        :returns: EnableAllFeaturesResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises HandshakeConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("EnablePolicyType")
    def enable_policy_type(
        self, context: RequestContext, root_id: RootId, policy_type: PolicyType
    ) -> EnablePolicyTypeResponse:
        """Enables a policy type in a root. After you enable a policy type in a
        root, you can attach policies of that type to the root, any
        organizational unit (OU), or account in that root. You can undo this by
        using the DisablePolicyType operation.

        This is an asynchronous request that Amazon Web Services performs in the
        background. Amazon Web Services recommends that you first use ListRoots
        to see the status of policy types for a specified root, and then use
        this operation.

        This operation can be called only from the organization's management
        account.

        You can enable a policy type in a root only if that policy type is
        available in the organization. To view the status of available policy
        types in the organization, use DescribeOrganization.

        :param root_id: The unique identifier (ID) of the root in which you want to enable a
        policy type.
        :param policy_type: The policy type that you want to enable.
        :returns: EnablePolicyTypeResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises PolicyTypeAlreadyEnabledException:
        :raises RootNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises PolicyTypeNotAvailableForOrganizationException:
        :raises UnsupportedAPIEndpointException:
        :raises PolicyChangesInProgressException:
        """
        raise NotImplementedError

    @handler("InviteAccountToOrganization")
    def invite_account_to_organization(
        self,
        context: RequestContext,
        target: HandshakeParty,
        notes: HandshakeNotes = None,
        tags: Tags = None,
    ) -> InviteAccountToOrganizationResponse:
        """Sends an invitation to another account to join your organization as a
        member account. Organizations sends email on your behalf to the email
        address that is associated with the other account's owner. The
        invitation is implemented as a Handshake whose details are in the
        response.

        -  You can invite Amazon Web Services accounts only from the same seller
           as the management account. For example, if your organization's
           management account was created by Amazon Internet Services Pvt. Ltd
           (AISPL), an Amazon Web Services seller in India, you can invite only
           other AISPL accounts to your organization. You can't combine accounts
           from AISPL and Amazon Web Services or from any other Amazon Web
           Services seller. For more information, see `Consolidated Billing in
           India <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/useconsolidatedbilliing-India.html>`__.

        -  If you receive an exception that indicates that you exceeded your
           account limits for the organization or that the operation failed
           because your organization is still initializing, wait one hour and
           then try again. If the error persists after an hour, contact `Amazon
           Web Services
           Support <https://console.aws.amazon.com/support/home#/>`__.

        If the request includes tags, then the requester must have the
        ``organizations:TagResource`` permission.

        This operation can be called only from the organization's management
        account.

        :param target: The identifier (ID) of the Amazon Web Services account that you want to
        invite to join your organization.
        :param notes: Additional information that you want to include in the generated email
        to the recipient account owner.
        :param tags: A list of tags that you want to attach to the account when it becomes a
        member of the organization.
        :returns: InviteAccountToOrganizationResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises AccountOwnerNotVerifiedException:
        :raises ConcurrentModificationException:
        :raises HandshakeConstraintViolationException:
        :raises DuplicateHandshakeException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises FinalizingOrganizationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("LeaveOrganization")
    def leave_organization(
        self,
        context: RequestContext,
    ) -> None:
        """Removes a member account from its parent organization. This version of
        the operation is performed by the account that wants to leave. To remove
        a member account as a user in the management account, use
        RemoveAccountFromOrganization instead.

        This operation can be called only from a member account in the
        organization.

        -  The management account in an organization with all features enabled
           can set service control policies (SCPs) that can restrict what
           administrators of member accounts can do. This includes preventing
           them from successfully calling ``LeaveOrganization`` and leaving the
           organization.

        -  You can leave an organization as a member account only if the account
           is configured with the information required to operate as a
           standalone account. When you create an account in an organization
           using the Organizations console, API, or CLI commands, the
           information required of standalone accounts is *not* automatically
           collected. For each account that you want to make standalone, you
           must perform the following steps. If any of the steps are already
           completed for this account, that step doesn't appear.

           -  Choose a support plan

           -  Provide and verify the required contact information

           -  Provide a current payment method

           Amazon Web Services uses the payment method to charge for any
           billable (not free tier) Amazon Web Services activity that occurs
           while the account isn't attached to an organization. Follow the steps
           at `To leave an organization when all required account information
           has not yet been
           provided <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#leave-without-all-info>`__
           in the *Organizations User Guide.*

        -  The account that you want to leave must not be a delegated
           administrator account for any Amazon Web Services service enabled for
           your organization. If the account is a delegated administrator, you
           must first change the delegated administrator account to another
           account that is remaining in the organization.

        -  You can leave an organization only after you enable IAM user access
           to billing in your account. For more information, see `Activating
           Access to the Billing and Cost Management
           Console <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/grantaccess.html#ControllingAccessWebsite-Activate>`__
           in the *Amazon Web Services Billing and Cost Management User Guide.*

        -  After the account leaves the organization, all tags that were
           attached to the account object in the organization are deleted.
           Amazon Web Services accounts outside of an organization do not
           support tags.

        -  A newly created account has a waiting period before it can be removed
           from its organization. If you get an error that indicates that a wait
           period is required, then try again in a few days.

        :raises AccessDeniedException:
        :raises AccountNotFoundException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises MasterCannotLeaveOrganizationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListAWSServiceAccessForOrganization")
    def list_aws_service_access_for_organization(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListAWSServiceAccessForOrganizationResponse:
        """Returns a list of the Amazon Web Services services that you enabled to
        integrate with your organization. After a service on this list creates
        the resources that it requires for the integration, it can perform
        operations on your organization and its accounts.

        For more information about integrating other services with
        Organizations, including the list of services that currently work with
        Organizations, see `Integrating Organizations with Other Amazon Web
        Services
        Services <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html>`__
        in the *Organizations User Guide.*

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListAWSServiceAccessForOrganizationResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("ListAccounts")
    def list_accounts(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListAccountsResponse:
        """Lists all the accounts in the organization. To request only the accounts
        in a specified root or organizational unit (OU), use the
        ListAccountsForParent operation instead.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListAccountsResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListAccountsForParent")
    def list_accounts_for_parent(
        self,
        context: RequestContext,
        parent_id: ParentId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListAccountsForParentResponse:
        """Lists the accounts in an organization that are contained by the
        specified target root or organizational unit (OU). If you specify the
        root, you get a list of all the accounts that aren't in any OU. If you
        specify an OU, you get a list of all the accounts in only that OU and
        not in any child OUs. To get a list of all accounts in the organization,
        use the ListAccounts operation.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param parent_id: The unique identifier (ID) for the parent root or organization unit (OU)
        whose accounts you want to list.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListAccountsForParentResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ParentNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListChildren")
    def list_children(
        self,
        context: RequestContext,
        parent_id: ParentId,
        child_type: ChildType,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListChildrenResponse:
        """Lists all of the organizational units (OUs) or accounts that are
        contained in the specified parent OU or root. This operation, along with
        ListParents enables you to traverse the tree structure that makes up
        this root.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param parent_id: The unique identifier (ID) for the parent root or OU whose children you
        want to list.
        :param child_type: Filters the output to include only the specified child type.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListChildrenResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ParentNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListCreateAccountStatus")
    def list_create_account_status(
        self,
        context: RequestContext,
        states: CreateAccountStates = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListCreateAccountStatusResponse:
        """Lists the account creation requests that match the specified status that
        is currently being tracked for the organization.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param states: A list of one or more states that you want included in the response.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListCreateAccountStatusResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("ListDelegatedAdministrators")
    def list_delegated_administrators(
        self,
        context: RequestContext,
        service_principal: ServicePrincipal = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListDelegatedAdministratorsResponse:
        """Lists the Amazon Web Services accounts that are designated as delegated
        administrators in this organization.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param service_principal: Specifies a service principal name.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListDelegatedAdministratorsResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises TooManyRequestsException:
        :raises ServiceException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("ListDelegatedServicesForAccount")
    def list_delegated_services_for_account(
        self,
        context: RequestContext,
        account_id: AccountId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListDelegatedServicesForAccountResponse:
        """List the Amazon Web Services services for which the specified account is
        a delegated administrator.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param account_id: The account ID number of a delegated administrator account in the
        organization.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListDelegatedServicesForAccountResponse
        :raises AccessDeniedException:
        :raises AccountNotFoundException:
        :raises AccountNotRegisteredException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises TooManyRequestsException:
        :raises ServiceException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("ListHandshakesForAccount")
    def list_handshakes_for_account(
        self,
        context: RequestContext,
        filter: HandshakeFilter = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListHandshakesForAccountResponse:
        """Lists the current handshakes that are associated with the account of the
        requesting user.

        Handshakes that are ``ACCEPTED``, ``DECLINED``, ``CANCELED``, or
        ``EXPIRED`` appear in the results of this API for only 30 days after
        changing to that state. After that, they're deleted and no longer
        accessible.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called from any account in the organization.

        :param filter: Filters the handshakes that you want included in the response.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListHandshakesForAccountResponse
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListHandshakesForOrganization")
    def list_handshakes_for_organization(
        self,
        context: RequestContext,
        filter: HandshakeFilter = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListHandshakesForOrganizationResponse:
        """Lists the handshakes that are associated with the organization that the
        requesting user is part of. The ``ListHandshakesForOrganization``
        operation returns a list of handshake structures. Each structure
        contains details and status about a handshake.

        Handshakes that are ``ACCEPTED``, ``DECLINED``, ``CANCELED``, or
        ``EXPIRED`` appear in the results of this API for only 30 days after
        changing to that state. After that, they're deleted and no longer
        accessible.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param filter: A filter of the handshakes that you want included in the response.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListHandshakesForOrganizationResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListOrganizationalUnitsForParent")
    def list_organizational_units_for_parent(
        self,
        context: RequestContext,
        parent_id: ParentId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListOrganizationalUnitsForParentResponse:
        """Lists the organizational units (OUs) in a parent organizational unit or
        root.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param parent_id: The unique identifier (ID) of the root or OU whose child OUs you want to
        list.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListOrganizationalUnitsForParentResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ParentNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListParents")
    def list_parents(
        self,
        context: RequestContext,
        child_id: ChildId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListParentsResponse:
        """Lists the root or organizational units (OUs) that serve as the immediate
        parent of the specified child OU or account. This operation, along with
        ListChildren enables you to traverse the tree structure that makes up
        this root.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        In the current release, a child can have only a single parent.

        :param child_id: The unique identifier (ID) of the OU or account whose parent containers
        you want to list.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListParentsResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ChildNotFoundException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListPolicies")
    def list_policies(
        self,
        context: RequestContext,
        filter: PolicyType,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListPoliciesResponse:
        """Retrieves the list of all policies in an organization of a specified
        type.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param filter: Specifies the type of policy that you want to include in the response.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListPoliciesResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("ListPoliciesForTarget")
    def list_policies_for_target(
        self,
        context: RequestContext,
        target_id: PolicyTargetId,
        filter: PolicyType,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListPoliciesForTargetResponse:
        """Lists the policies that are directly attached to the specified target
        root, organizational unit (OU), or account. You must specify the policy
        type that you want included in the returned list.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param target_id: The unique identifier (ID) of the root, organizational unit, or account
        whose policies you want to list.
        :param filter: The type of policy that you want to include in the returned list.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListPoliciesForTargetResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TargetNotFoundException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("ListRoots")
    def list_roots(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListRootsResponse:
        """Lists the roots that are defined in the current organization.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        Policy types can be enabled and disabled in roots. This is distinct from
        whether they're available in the organization. When you enable all
        features, you make policy types available for use in that organization.
        Individual policy types can then be enabled and disabled in a root. To
        see the availability of a policy type in an organization, use
        DescribeOrganization.

        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListRootsResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_id: TaggableResourceId, next_token: NextToken = None
    ) -> ListTagsForResourceResponse:
        """Lists tags that are attached to the specified resource.

        You can attach tags to the following resources in Organizations.

        -  Amazon Web Services account

        -  Organization root

        -  Organizational unit (OU)

        -  Policy (any type)

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param resource_id: The ID of the resource with the tags to list.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :returns: ListTagsForResourceResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises TargetNotFoundException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListTargetsForPolicy")
    def list_targets_for_policy(
        self,
        context: RequestContext,
        policy_id: PolicyId,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListTargetsForPolicyResponse:
        """Lists all the roots, organizational units (OUs), and accounts that the
        specified policy is attached to.

        Always check the ``NextToken`` response parameter for a ``null`` value
        when calling a ``List*`` operation. These operations can occasionally
        return an empty set of results even when there are more results
        available. The ``NextToken`` response parameter value is ``null`` *only*
        when there are no more results to display.

        This operation can be called only from the organization's management
        account or by a member account that is a delegated administrator for an
        Amazon Web Services service.

        :param policy_id: The unique identifier (ID) of the policy whose attachments you want to
        know.
        :param next_token: The parameter for receiving additional results if you receive a
        ``NextToken`` response in a previous request.
        :param max_results: The total number of results that you want included on each page of the
        response.
        :returns: ListTargetsForPolicyResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises InvalidInputException:
        :raises PolicyNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("MoveAccount")
    def move_account(
        self,
        context: RequestContext,
        account_id: AccountId,
        source_parent_id: ParentId,
        destination_parent_id: ParentId,
    ) -> None:
        """Moves an account from its current source parent root or organizational
        unit (OU) to the specified destination parent root or OU.

        This operation can be called only from the organization's management
        account.

        :param account_id: The unique identifier (ID) of the account that you want to move.
        :param source_parent_id: The unique identifier (ID) of the root or organizational unit that you
        want to move the account from.
        :param destination_parent_id: The unique identifier (ID) of the root or organizational unit that you
        want to move the account to.
        :raises AccessDeniedException:
        :raises InvalidInputException:
        :raises SourceParentNotFoundException:
        :raises DestinationParentNotFoundException:
        :raises DuplicateAccountException:
        :raises AccountNotFoundException:
        :raises TooManyRequestsException:
        :raises ConcurrentModificationException:
        :raises AWSOrganizationsNotInUseException:
        :raises ServiceException:
        """
        raise NotImplementedError

    @handler("RegisterDelegatedAdministrator")
    def register_delegated_administrator(
        self, context: RequestContext, account_id: AccountId, service_principal: ServicePrincipal
    ) -> None:
        """Enables the specified member account to administer the Organizations
        features of the specified Amazon Web Services service. It grants
        read-only access to Organizations service data. The account still
        requires IAM permissions to access and administer the Amazon Web
        Services service.

        You can run this action only for Amazon Web Services services that
        support this feature. For a current list of services that support it,
        see the column *Supports Delegated Administrator* in the table at
        `Amazon Web Services Services that you can use with
        Organizations <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html>`__
        in the *Organizations User Guide.*

        This operation can be called only from the organization's management
        account.

        :param account_id: The account ID number of the member account in the organization to
        register as a delegated administrator.
        :param service_principal: The service principal of the Amazon Web Services service for which you
        want to make the member account a delegated administrator.
        :raises AccessDeniedException:
        :raises AccountAlreadyRegisteredException:
        :raises AccountNotFoundException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises TooManyRequestsException:
        :raises ServiceException:
        :raises UnsupportedAPIEndpointException:
        """
        raise NotImplementedError

    @handler("RemoveAccountFromOrganization")
    def remove_account_from_organization(
        self, context: RequestContext, account_id: AccountId
    ) -> None:
        """Removes the specified account from the organization.

        The removed account becomes a standalone account that isn't a member of
        any organization. It's no longer subject to any policies and is
        responsible for its own bill payments. The organization's management
        account is no longer charged for any expenses accrued by the member
        account after it's removed from the organization.

        This operation can be called only from the organization's management
        account. Member accounts can remove themselves with LeaveOrganization
        instead.

        -  You can remove an account from your organization only if the account
           is configured with the information required to operate as a
           standalone account. When you create an account in an organization
           using the Organizations console, API, or CLI commands, the
           information required of standalone accounts is *not* automatically
           collected. For an account that you want to make standalone, you must
           choose a support plan, provide and verify the required contact
           information, and provide a current payment method. Amazon Web
           Services uses the payment method to charge for any billable (not free
           tier) Amazon Web Services activity that occurs while the account
           isn't attached to an organization. To remove an account that doesn't
           yet have this information, you must sign in as the member account and
           follow the steps at `To leave an organization when all required
           account information has not yet been
           provided <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html#leave-without-all-info>`__
           in the *Organizations User Guide.*

        -  The account that you want to leave must not be a delegated
           administrator account for any Amazon Web Services service enabled for
           your organization. If the account is a delegated administrator, you
           must first change the delegated administrator account to another
           account that is remaining in the organization.

        -  After the account leaves the organization, all tags that were
           attached to the account object in the organization are deleted.
           Amazon Web Services accounts outside of an organization do not
           support tags.

        :param account_id: The unique identifier (ID) of the member account that you want to remove
        from the organization.
        :raises AccessDeniedException:
        :raises AccountNotFoundException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises MasterCannotLeaveOrganizationException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_id: TaggableResourceId, tags: Tags
    ) -> None:
        """Adds one or more tags to the specified resource.

        Currently, you can attach tags to the following resources in
        Organizations.

        -  Amazon Web Services account

        -  Organization root

        -  Organizational unit (OU)

        -  Policy (any type)

        This operation can be called only from the organization's management
        account.

        :param resource_id: The ID of the resource to add a tag to.
        :param tags: A list of tags to add to the specified resource.
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        :raises AWSOrganizationsNotInUseException:
        :raises TargetNotFoundException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_id: TaggableResourceId, tag_keys: TagKeys
    ) -> None:
        """Removes any tags with the specified keys from the specified resource.

        You can attach tags to the following resources in Organizations.

        -  Amazon Web Services account

        -  Organization root

        -  Organizational unit (OU)

        -  Policy (any type)

        This operation can be called only from the organization's management
        account.

        :param resource_id: The ID of the resource to remove a tag from.
        :param tag_keys: The list of keys for tags to remove from the specified resource.
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        :raises AWSOrganizationsNotInUseException:
        :raises TargetNotFoundException:
        :raises ConstraintViolationException:
        :raises InvalidInputException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("UpdateOrganizationalUnit")
    def update_organizational_unit(
        self,
        context: RequestContext,
        organizational_unit_id: OrganizationalUnitId,
        name: OrganizationalUnitName = None,
    ) -> UpdateOrganizationalUnitResponse:
        """Renames the specified organizational unit (OU). The ID and ARN don't
        change. The child OUs and accounts remain in place, and any attached
        policies of the OU remain attached.

        This operation can be called only from the organization's management
        account.

        :param organizational_unit_id: The unique identifier (ID) of the OU that you want to rename.
        :param name: The new name that you want to assign to the OU.
        :returns: UpdateOrganizationalUnitResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises DuplicateOrganizationalUnitException:
        :raises InvalidInputException:
        :raises OrganizationalUnitNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("UpdatePolicy")
    def update_policy(
        self,
        context: RequestContext,
        policy_id: PolicyId,
        name: PolicyName = None,
        description: PolicyDescription = None,
        content: PolicyContent = None,
    ) -> UpdatePolicyResponse:
        """Updates an existing policy with a new name, description, or content. If
        you don't supply any parameter, that value remains unchanged. You can't
        change a policy's type.

        This operation can be called only from the organization's management
        account.

        :param policy_id: The unique identifier (ID) of the policy that you want to update.
        :param name: If provided, the new name for the policy.
        :param description: If provided, the new description for the policy.
        :param content: If provided, the new content for the policy.
        :returns: UpdatePolicyResponse
        :raises AccessDeniedException:
        :raises AWSOrganizationsNotInUseException:
        :raises ConcurrentModificationException:
        :raises ConstraintViolationException:
        :raises DuplicatePolicyException:
        :raises InvalidInputException:
        :raises MalformedPolicyDocumentException:
        :raises PolicyNotFoundException:
        :raises ServiceException:
        :raises TooManyRequestsException:
        :raises UnsupportedAPIEndpointException:
        :raises PolicyChangesInProgressException:
        """
        raise NotImplementedError
