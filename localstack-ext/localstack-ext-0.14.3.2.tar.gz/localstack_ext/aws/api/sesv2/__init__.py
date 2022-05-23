import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AdditionalContactEmailAddress = str
AmazonResourceName = str
AttributesData = str
BlacklistItemName = str
BlacklistingDescription = str
CampaignId = str
CaseId = str
Charset = str
ConfigurationSetName = str
ContactListName = str
CustomRedirectDomain = str
DefaultDimensionValue = str
DeliverabilityTestSubject = str
Description = str
DimensionName = str
DisplayName = str
DnsToken = str
Domain = str
EmailAddress = str
EmailTemplateData = str
EmailTemplateHtml = str
EmailTemplateName = str
EmailTemplateSubject = str
EmailTemplateText = str
Enabled = bool
EnabledWrapper = bool
ErrorMessage = str
Esp = str
EventDestinationName = str
FailedRecordsCount = int
FailedRecordsS3Url = str
FailureRedirectionURL = str
FeedbackId = str
GeneralEnforcementStatus = str
Identity = str
ImageUrl = str
Ip = str
IspName = str
JobId = str
MailFromDomainName = str
Max24HourSend = float
MaxItems = int
MaxSendRate = float
MessageContent = str
MessageData = str
MessageTagName = str
MessageTagValue = str
NextToken = str
OutboundMessageId = str
Percentage = float
Percentage100Wrapper = int
Policy = str
PolicyName = str
PoolName = str
PrivateKey = str
ProcessedRecordsCount = int
RblName = str
RenderedEmailTemplate = str
ReportId = str
ReportName = str
S3Url = str
Selector = str
SendingPoolName = str
SentLast24Hours = float
Subject = str
SuccessRedirectionURL = str
TagKey = str
TagValue = str
TemplateContent = str
TopicName = str
UnsubscribeAll = bool
UseCaseDescription = str
UseDefaultIfPreferenceUnavailable = bool
WebsiteURL = str


class BehaviorOnMxFailure(str):
    USE_DEFAULT_VALUE = "USE_DEFAULT_VALUE"
    REJECT_MESSAGE = "REJECT_MESSAGE"


class BulkEmailStatus(str):
    SUCCESS = "SUCCESS"
    MESSAGE_REJECTED = "MESSAGE_REJECTED"
    MAIL_FROM_DOMAIN_NOT_VERIFIED = "MAIL_FROM_DOMAIN_NOT_VERIFIED"
    CONFIGURATION_SET_NOT_FOUND = "CONFIGURATION_SET_NOT_FOUND"
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    ACCOUNT_SUSPENDED = "ACCOUNT_SUSPENDED"
    ACCOUNT_THROTTLED = "ACCOUNT_THROTTLED"
    ACCOUNT_DAILY_QUOTA_EXCEEDED = "ACCOUNT_DAILY_QUOTA_EXCEEDED"
    INVALID_SENDING_POOL_NAME = "INVALID_SENDING_POOL_NAME"
    ACCOUNT_SENDING_PAUSED = "ACCOUNT_SENDING_PAUSED"
    CONFIGURATION_SET_SENDING_PAUSED = "CONFIGURATION_SET_SENDING_PAUSED"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    FAILED = "FAILED"


class ContactLanguage(str):
    EN = "EN"
    JA = "JA"


class ContactListImportAction(str):
    DELETE = "DELETE"
    PUT = "PUT"


class DataFormat(str):
    CSV = "CSV"
    JSON = "JSON"


class DeliverabilityDashboardAccountStatus(str):
    ACTIVE = "ACTIVE"
    PENDING_EXPIRATION = "PENDING_EXPIRATION"
    DISABLED = "DISABLED"


class DeliverabilityTestStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class DimensionValueSource(str):
    MESSAGE_TAG = "MESSAGE_TAG"
    EMAIL_HEADER = "EMAIL_HEADER"
    LINK_TAG = "LINK_TAG"


class DkimSigningAttributesOrigin(str):
    AWS_SES = "AWS_SES"
    EXTERNAL = "EXTERNAL"


class DkimSigningKeyLength(str):
    RSA_1024_BIT = "RSA_1024_BIT"
    RSA_2048_BIT = "RSA_2048_BIT"


class DkimStatus(str):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TEMPORARY_FAILURE = "TEMPORARY_FAILURE"
    NOT_STARTED = "NOT_STARTED"


class EventType(str):
    SEND = "SEND"
    REJECT = "REJECT"
    BOUNCE = "BOUNCE"
    COMPLAINT = "COMPLAINT"
    DELIVERY = "DELIVERY"
    OPEN = "OPEN"
    CLICK = "CLICK"
    RENDERING_FAILURE = "RENDERING_FAILURE"
    DELIVERY_DELAY = "DELIVERY_DELAY"
    SUBSCRIPTION = "SUBSCRIPTION"


class IdentityType(str):
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    DOMAIN = "DOMAIN"
    MANAGED_DOMAIN = "MANAGED_DOMAIN"


class ImportDestinationType(str):
    SUPPRESSION_LIST = "SUPPRESSION_LIST"
    CONTACT_LIST = "CONTACT_LIST"


class JobStatus(str):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MailFromDomainStatus(str):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TEMPORARY_FAILURE = "TEMPORARY_FAILURE"


class MailType(str):
    MARKETING = "MARKETING"
    TRANSACTIONAL = "TRANSACTIONAL"


class ReviewStatus(str):
    PENDING = "PENDING"
    FAILED = "FAILED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"


class SubscriptionStatus(str):
    OPT_IN = "OPT_IN"
    OPT_OUT = "OPT_OUT"


class SuppressionListImportAction(str):
    DELETE = "DELETE"
    PUT = "PUT"


class SuppressionListReason(str):
    BOUNCE = "BOUNCE"
    COMPLAINT = "COMPLAINT"


class TlsPolicy(str):
    REQUIRE = "REQUIRE"
    OPTIONAL = "OPTIONAL"


class WarmupStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class AccountSuspendedException(ServiceException):
    """The message can't be sent because the account's ability to send email
    has been permanently restricted.
    """


class AlreadyExistsException(ServiceException):
    """The resource specified in your request already exists."""


class BadRequestException(ServiceException):
    """The input you provided is invalid."""


class ConcurrentModificationException(ServiceException):
    """The resource is being modified by another operation or thread."""


class ConflictException(ServiceException):
    """If there is already an ongoing account details update under review."""


class InvalidNextTokenException(ServiceException):
    """The specified request includes an invalid or expired token."""


class LimitExceededException(ServiceException):
    """There are too many instances of the specified resource type."""


class MailFromDomainNotVerifiedException(ServiceException):
    """The message can't be sent because the sending domain isn't verified."""


class MessageRejected(ServiceException):
    """The message can't be sent because it contains invalid content."""


class NotFoundException(ServiceException):
    """The resource you attempted to access doesn't exist."""


class SendingPausedException(ServiceException):
    """The message can't be sent because the account's ability to send email is
    currently paused.
    """


class TooManyRequestsException(ServiceException):
    """Too many requests have been made to the operation."""


class ReviewDetails(TypedDict, total=False):
    """An object that contains information about your account details review."""

    Status: Optional[ReviewStatus]
    CaseId: Optional[CaseId]


AdditionalContactEmailAddresses = List[AdditionalContactEmailAddress]


class AccountDetails(TypedDict, total=False):
    """An object that contains information about your account details."""

    MailType: Optional[MailType]
    WebsiteURL: Optional[WebsiteURL]
    ContactLanguage: Optional[ContactLanguage]
    UseCaseDescription: Optional[UseCaseDescription]
    AdditionalContactEmailAddresses: Optional[AdditionalContactEmailAddresses]
    ReviewDetails: Optional[ReviewDetails]


Timestamp = datetime


class BlacklistEntry(TypedDict, total=False):
    """An object that contains information about a blacklisting event that
    impacts one of the dedicated IP addresses that is associated with your
    account.
    """

    RblName: Optional[RblName]
    ListingTime: Optional[Timestamp]
    Description: Optional[BlacklistingDescription]


BlacklistEntries = List[BlacklistEntry]
BlacklistItemNames = List[BlacklistItemName]
BlacklistReport = Dict[BlacklistItemName, BlacklistEntries]


class Content(TypedDict, total=False):
    """An object that represents the content of the email, and optionally a
    character set specification.
    """

    Data: MessageData
    Charset: Optional[Charset]


class Body(TypedDict, total=False):
    """Represents the body of the email message."""

    Text: Optional[Content]
    Html: Optional[Content]


class Template(TypedDict, total=False):
    """An object that defines the email template to use for an email message,
    and the values to use for any message variables in that template. An
    *email template* is a type of message template that contains content
    that you want to define, save, and reuse in email messages that you
    send.
    """

    TemplateName: Optional[EmailTemplateName]
    TemplateArn: Optional[AmazonResourceName]
    TemplateData: Optional[EmailTemplateData]


class BulkEmailContent(TypedDict, total=False):
    """An object that contains the body of the message. You can specify a
    template message.
    """

    Template: Optional[Template]


class ReplacementTemplate(TypedDict, total=False):
    """An object which contains ``ReplacementTemplateData`` to be used for a
    specific ``BulkEmailEntry``.
    """

    ReplacementTemplateData: Optional[EmailTemplateData]


class ReplacementEmailContent(TypedDict, total=False):
    """The ``ReplaceEmailContent`` object to be used for a specific
    ``BulkEmailEntry``. The ``ReplacementTemplate`` can be specified within
    this object.
    """

    ReplacementTemplate: Optional[ReplacementTemplate]


class MessageTag(TypedDict, total=False):
    """Contains the name and value of a tag that you apply to an email. You can
    use message tags when you publish email sending events.
    """

    Name: MessageTagName
    Value: MessageTagValue


MessageTagList = List[MessageTag]
EmailAddressList = List[EmailAddress]


class Destination(TypedDict, total=False):
    """An object that describes the recipients for an email.

    Amazon SES does not support the SMTPUTF8 extension, as described in
    `RFC6531 <https://tools.ietf.org/html/rfc6531>`__. For this reason, the
    *local part* of a destination email address (the part of the email
    address that precedes the @ sign) may only contain `7-bit ASCII
    characters <https://en.wikipedia.org/wiki/Email_address#Local-part>`__.
    If the *domain part* of an address (the part after the @ sign) contains
    non-ASCII characters, they must be encoded using Punycode, as described
    in `RFC3492 <https://tools.ietf.org/html/rfc3492.html>`__.
    """

    ToAddresses: Optional[EmailAddressList]
    CcAddresses: Optional[EmailAddressList]
    BccAddresses: Optional[EmailAddressList]


class BulkEmailEntry(TypedDict, total=False):
    Destination: Destination
    ReplacementTags: Optional[MessageTagList]
    ReplacementEmailContent: Optional[ReplacementEmailContent]


BulkEmailEntryList = List[BulkEmailEntry]


class BulkEmailEntryResult(TypedDict, total=False):
    """The result of the ``SendBulkEmail`` operation of each specified
    ``BulkEmailEntry``.
    """

    Status: Optional[BulkEmailStatus]
    Error: Optional[ErrorMessage]
    MessageId: Optional[OutboundMessageId]


BulkEmailEntryResultList = List[BulkEmailEntryResult]


class CloudWatchDimensionConfiguration(TypedDict, total=False):
    """An object that defines the dimension configuration to use when you send
    email events to Amazon CloudWatch.
    """

    DimensionName: DimensionName
    DimensionValueSource: DimensionValueSource
    DefaultDimensionValue: DefaultDimensionValue


CloudWatchDimensionConfigurations = List[CloudWatchDimensionConfiguration]


class CloudWatchDestination(TypedDict, total=False):
    """An object that defines an Amazon CloudWatch destination for email
    events. You can use Amazon CloudWatch to monitor and gain insights on
    your email sending metrics.
    """

    DimensionConfigurations: CloudWatchDimensionConfigurations


ConfigurationSetNameList = List[ConfigurationSetName]


class TopicPreference(TypedDict, total=False):
    """The contact's preference for being opted-in to or opted-out of a topic."""

    TopicName: TopicName
    SubscriptionStatus: SubscriptionStatus


TopicPreferenceList = List[TopicPreference]


class Contact(TypedDict, total=False):
    """A contact is the end-user who is receiving the email."""

    EmailAddress: Optional[EmailAddress]
    TopicPreferences: Optional[TopicPreferenceList]
    TopicDefaultPreferences: Optional[TopicPreferenceList]
    UnsubscribeAll: Optional[UnsubscribeAll]
    LastUpdatedTimestamp: Optional[Timestamp]


class ContactList(TypedDict, total=False):
    """A list that contains contacts that have subscribed to a particular topic
    or topics.
    """

    ContactListName: Optional[ContactListName]
    LastUpdatedTimestamp: Optional[Timestamp]


class ContactListDestination(TypedDict, total=False):
    """An object that contains details about the action of a contact list."""

    ContactListName: ContactListName
    ContactListImportAction: ContactListImportAction


class PinpointDestination(TypedDict, total=False):
    """An object that defines an Amazon Pinpoint project destination for email
    events. You can send email event data to a Amazon Pinpoint project to
    view metrics using the Transactional Messaging dashboards that are built
    in to Amazon Pinpoint. For more information, see `Transactional
    Messaging
    Charts <https://docs.aws.amazon.com/pinpoint/latest/userguide/analytics-transactional-messages.html>`__
    in the *Amazon Pinpoint User Guide*.
    """

    ApplicationArn: Optional[AmazonResourceName]


class SnsDestination(TypedDict, total=False):
    """An object that defines an Amazon SNS destination for email events. You
    can use Amazon SNS to send notification when certain email events occur.
    """

    TopicArn: AmazonResourceName


class KinesisFirehoseDestination(TypedDict, total=False):
    """An object that defines an Amazon Kinesis Data Firehose destination for
    email events. You can use Amazon Kinesis Data Firehose to stream data to
    other services, such as Amazon S3 and Amazon Redshift.
    """

    IamRoleArn: AmazonResourceName
    DeliveryStreamArn: AmazonResourceName


EventTypes = List[EventType]


class EventDestinationDefinition(TypedDict, total=False):
    """An object that defines the event destination. Specifically, it defines
    which services receive events from emails sent using the configuration
    set that the event destination is associated with. Also defines the
    types of events that are sent to the event destination.
    """

    Enabled: Optional[Enabled]
    MatchingEventTypes: Optional[EventTypes]
    KinesisFirehoseDestination: Optional[KinesisFirehoseDestination]
    CloudWatchDestination: Optional[CloudWatchDestination]
    SnsDestination: Optional[SnsDestination]
    PinpointDestination: Optional[PinpointDestination]


class CreateConfigurationSetEventDestinationRequest(ServiceRequest):
    """A request to add an event destination to a configuration set."""

    ConfigurationSetName: ConfigurationSetName
    EventDestinationName: EventDestinationName
    EventDestination: EventDestinationDefinition


class CreateConfigurationSetEventDestinationResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


SuppressionListReasons = List[SuppressionListReason]


class SuppressionOptions(TypedDict, total=False):
    """An object that contains information about the suppression list
    preferences for your account.
    """

    SuppressedReasons: Optional[SuppressionListReasons]


class Tag(TypedDict, total=False):
    """An object that defines the tags that are associated with a resource.
    A  *tag* is a label that you optionally define and associate with a
    resource. Tags can help you categorize and manage resources in different
    ways, such as by purpose, owner, environment, or other criteria. A
    resource can have as many as 50 tags.

    Each tag consists of a required  *tag key* and an associated  *tag
    value*, both of which you define. A tag key is a general label that acts
    as a category for a more specific tag value. A tag value acts as a
    descriptor within a tag key. A tag key can contain as many as 128
    characters. A tag value can contain as many as 256 characters. The
    characters can be Unicode letters, digits, white space, or one of the
    following symbols: _ . : / = + -. The following additional restrictions
    apply to tags:

    -  Tag keys and values are case sensitive.

    -  For each associated resource, each tag key must be unique and it can
       have only one value.

    -  The  ``aws:`` prefix is reserved for use by Amazon Web Services; you
       can’t use it in any tag keys or values that you define. In addition,
       you can't edit or remove tag keys or values that use this prefix.
       Tags that use this prefix don’t count against the limit of 50 tags
       per resource.

    -  You can associate tags with public or shared resources, but the tags
       are available only for your Amazon Web Services account, not any
       other accounts that share the resource. In addition, the tags are
       available only for resources that are located in the specified Amazon
       Web Services Region for your Amazon Web Services account.
    """

    Key: TagKey
    Value: TagValue


TagList = List[Tag]


class SendingOptions(TypedDict, total=False):
    """Used to enable or disable email sending for messages that use this
    configuration set in the current Amazon Web Services Region.
    """

    SendingEnabled: Optional[Enabled]


LastFreshStart = datetime


class ReputationOptions(TypedDict, total=False):
    """Enable or disable collection of reputation metrics for emails that you
    send using this configuration set in the current Amazon Web Services
    Region.
    """

    ReputationMetricsEnabled: Optional[Enabled]
    LastFreshStart: Optional[LastFreshStart]


class DeliveryOptions(TypedDict, total=False):
    """Used to associate a configuration set with a dedicated IP pool."""

    TlsPolicy: Optional[TlsPolicy]
    SendingPoolName: Optional[PoolName]


class TrackingOptions(TypedDict, total=False):
    """An object that defines the tracking options for a configuration set.
    When you use the Amazon SES API v2 to send an email, it contains an
    invisible image that's used to track when recipients open your email. If
    your email contains links, those links are changed slightly in order to
    track when recipients click them.

    These images and links include references to a domain operated by Amazon
    Web Services. You can optionally configure the Amazon SES to use a
    domain that you operate for these images and links.
    """

    CustomRedirectDomain: CustomRedirectDomain


class CreateConfigurationSetRequest(ServiceRequest):
    """A request to create a configuration set."""

    ConfigurationSetName: ConfigurationSetName
    TrackingOptions: Optional[TrackingOptions]
    DeliveryOptions: Optional[DeliveryOptions]
    ReputationOptions: Optional[ReputationOptions]
    SendingOptions: Optional[SendingOptions]
    Tags: Optional[TagList]
    SuppressionOptions: Optional[SuppressionOptions]


class CreateConfigurationSetResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class Topic(TypedDict, total=False):
    """An interest group, theme, or label within a list. Lists can have
    multiple topics.
    """

    TopicName: TopicName
    DisplayName: DisplayName
    Description: Optional[Description]
    DefaultSubscriptionStatus: SubscriptionStatus


Topics = List[Topic]


class CreateContactListRequest(ServiceRequest):
    ContactListName: ContactListName
    Topics: Optional[Topics]
    Description: Optional[Description]
    Tags: Optional[TagList]


class CreateContactListResponse(TypedDict, total=False):
    pass


class CreateContactRequest(ServiceRequest):
    ContactListName: ContactListName
    EmailAddress: EmailAddress
    TopicPreferences: Optional[TopicPreferenceList]
    UnsubscribeAll: Optional[UnsubscribeAll]
    AttributesData: Optional[AttributesData]


class CreateContactResponse(TypedDict, total=False):
    pass


class CreateCustomVerificationEmailTemplateRequest(ServiceRequest):
    """Represents a request to create a custom verification email template."""

    TemplateName: EmailTemplateName
    FromEmailAddress: EmailAddress
    TemplateSubject: EmailTemplateSubject
    TemplateContent: TemplateContent
    SuccessRedirectionURL: SuccessRedirectionURL
    FailureRedirectionURL: FailureRedirectionURL


class CreateCustomVerificationEmailTemplateResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class CreateDedicatedIpPoolRequest(ServiceRequest):
    """A request to create a new dedicated IP pool."""

    PoolName: PoolName
    Tags: Optional[TagList]


class CreateDedicatedIpPoolResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


RawMessageData = bytes


class RawMessage(TypedDict, total=False):
    """Represents the raw content of an email message."""

    Data: RawMessageData


class Message(TypedDict, total=False):
    """Represents the email message that you're sending. The ``Message`` object
    consists of a subject line and a message body.
    """

    Subject: Content
    Body: Body


class EmailContent(TypedDict, total=False):
    """An object that defines the entire content of the email, including the
    message headers and the body content. You can create a simple email
    message, in which you specify the subject and the text and HTML versions
    of the message body. You can also create raw messages, in which you
    specify a complete MIME-formatted message. Raw messages can include
    attachments and custom headers.
    """

    Simple: Optional[Message]
    Raw: Optional[RawMessage]
    Template: Optional[Template]


class CreateDeliverabilityTestReportRequest(ServiceRequest):
    """A request to perform a predictive inbox placement test. Predictive inbox
    placement tests can help you predict how your messages will be handled
    by various email providers around the world. When you perform a
    predictive inbox placement test, you provide a sample message that
    contains the content that you plan to send to your customers. We send
    that message to special email addresses spread across several major
    email providers around the world. The test takes about 24 hours to
    complete. When the test is complete, you can use the
    ``GetDeliverabilityTestReport`` operation to view the results of the
    test.
    """

    ReportName: Optional[ReportName]
    FromEmailAddress: EmailAddress
    Content: EmailContent
    Tags: Optional[TagList]


class CreateDeliverabilityTestReportResponse(TypedDict, total=False):
    """Information about the predictive inbox placement test that you created."""

    ReportId: ReportId
    DeliverabilityTestStatus: DeliverabilityTestStatus


class CreateEmailIdentityPolicyRequest(ServiceRequest):
    """Represents a request to create a sending authorization policy for an
    identity. Sending authorization is an Amazon SES feature that enables
    you to authorize other senders to use your identities. For information,
    see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-identity-owner-tasks-management.html>`__.
    """

    EmailIdentity: Identity
    PolicyName: PolicyName
    Policy: Policy


class CreateEmailIdentityPolicyResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DkimSigningAttributes(TypedDict, total=False):
    """An object that contains configuration for Bring Your Own DKIM (BYODKIM),
    or, for Easy DKIM
    """

    DomainSigningSelector: Optional[Selector]
    DomainSigningPrivateKey: Optional[PrivateKey]
    NextSigningKeyLength: Optional[DkimSigningKeyLength]


class CreateEmailIdentityRequest(ServiceRequest):
    """A request to begin the verification process for an email identity (an
    email address or domain).
    """

    EmailIdentity: Identity
    Tags: Optional[TagList]
    DkimSigningAttributes: Optional[DkimSigningAttributes]
    ConfigurationSetName: Optional[ConfigurationSetName]


DnsTokenList = List[DnsToken]


class DkimAttributes(TypedDict, total=False):
    """An object that contains information about the DKIM authentication status
    for an email identity.

    Amazon SES determines the authentication status by searching for
    specific records in the DNS configuration for the domain. If you used
    `Easy
    DKIM <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/easy-dkim.html>`__
    to set up DKIM authentication, Amazon SES tries to find three unique
    CNAME records in the DNS configuration for your domain. If you provided
    a public key to perform DKIM authentication, Amazon SES tries to find a
    TXT record that uses the selector that you specified. The value of the
    TXT record must be a public key that's paired with the private key that
    you specified in the process of creating the identity
    """

    SigningEnabled: Optional[Enabled]
    Status: Optional[DkimStatus]
    Tokens: Optional[DnsTokenList]
    SigningAttributesOrigin: Optional[DkimSigningAttributesOrigin]
    NextSigningKeyLength: Optional[DkimSigningKeyLength]
    CurrentSigningKeyLength: Optional[DkimSigningKeyLength]
    LastKeyGenerationTimestamp: Optional[Timestamp]


class CreateEmailIdentityResponse(TypedDict, total=False):
    """If the email identity is a domain, this object contains information
    about the DKIM verification status for the domain.

    If the email identity is an email address, this object is empty.
    """

    IdentityType: Optional[IdentityType]
    VerifiedForSendingStatus: Optional[Enabled]
    DkimAttributes: Optional[DkimAttributes]


class EmailTemplateContent(TypedDict, total=False):
    """The content of the email, composed of a subject line, an HTML part, and
    a text-only part.
    """

    Subject: Optional[EmailTemplateSubject]
    Text: Optional[EmailTemplateText]
    Html: Optional[EmailTemplateHtml]


class CreateEmailTemplateRequest(ServiceRequest):
    """Represents a request to create an email template. For more information,
    see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.
    """

    TemplateName: EmailTemplateName
    TemplateContent: EmailTemplateContent


class CreateEmailTemplateResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class ImportDataSource(TypedDict, total=False):
    """An object that contains details about the data source of the import job."""

    S3Url: S3Url
    DataFormat: DataFormat


class SuppressionListDestination(TypedDict, total=False):
    """An object that contains details about the action of suppression list."""

    SuppressionListImportAction: SuppressionListImportAction


class ImportDestination(TypedDict, total=False):
    """An object that contains details about the resource destination the
    import job is going to target.
    """

    SuppressionListDestination: Optional[SuppressionListDestination]
    ContactListDestination: Optional[ContactListDestination]


class CreateImportJobRequest(ServiceRequest):
    """Represents a request to create an import job from a data source for a
    data destination.
    """

    ImportDestination: ImportDestination
    ImportDataSource: ImportDataSource


class CreateImportJobResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """

    JobId: Optional[JobId]


class CustomVerificationEmailTemplateMetadata(TypedDict, total=False):
    """Contains information about a custom verification email template."""

    TemplateName: Optional[EmailTemplateName]
    FromEmailAddress: Optional[EmailAddress]
    TemplateSubject: Optional[EmailTemplateSubject]
    SuccessRedirectionURL: Optional[SuccessRedirectionURL]
    FailureRedirectionURL: Optional[FailureRedirectionURL]


CustomVerificationEmailTemplatesList = List[CustomVerificationEmailTemplateMetadata]
Volume = int


class DomainIspPlacement(TypedDict, total=False):
    """An object that contains inbox placement data for email sent from one of
    your email domains to a specific email provider.
    """

    IspName: Optional[IspName]
    InboxRawCount: Optional[Volume]
    SpamRawCount: Optional[Volume]
    InboxPercentage: Optional[Percentage]
    SpamPercentage: Optional[Percentage]


DomainIspPlacements = List[DomainIspPlacement]


class VolumeStatistics(TypedDict, total=False):
    """An object that contains information about the amount of email that was
    delivered to recipients.
    """

    InboxRawCount: Optional[Volume]
    SpamRawCount: Optional[Volume]
    ProjectedInbox: Optional[Volume]
    ProjectedSpam: Optional[Volume]


class DailyVolume(TypedDict, total=False):
    """An object that contains information about the volume of email sent on
    each day of the analysis period.
    """

    StartDate: Optional[Timestamp]
    VolumeStatistics: Optional[VolumeStatistics]
    DomainIspPlacements: Optional[DomainIspPlacements]


DailyVolumes = List[DailyVolume]


class DedicatedIp(TypedDict, total=False):
    """Contains information about a dedicated IP address that is associated
    with your Amazon SES account.

    To learn more about requesting dedicated IP addresses, see `Requesting
    and Relinquishing Dedicated IP
    Addresses <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/dedicated-ip-case.html>`__
    in the *Amazon SES Developer Guide*.
    """

    Ip: Ip
    WarmupStatus: WarmupStatus
    WarmupPercentage: Percentage100Wrapper
    PoolName: Optional[PoolName]


DedicatedIpList = List[DedicatedIp]


class DeleteConfigurationSetEventDestinationRequest(ServiceRequest):
    """A request to delete an event destination from a configuration set."""

    ConfigurationSetName: ConfigurationSetName
    EventDestinationName: EventDestinationName


class DeleteConfigurationSetEventDestinationResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DeleteConfigurationSetRequest(ServiceRequest):
    """A request to delete a configuration set."""

    ConfigurationSetName: ConfigurationSetName


class DeleteConfigurationSetResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DeleteContactListRequest(ServiceRequest):
    ContactListName: ContactListName


class DeleteContactListResponse(TypedDict, total=False):
    pass


class DeleteContactRequest(ServiceRequest):
    ContactListName: ContactListName
    EmailAddress: EmailAddress


class DeleteContactResponse(TypedDict, total=False):
    pass


class DeleteCustomVerificationEmailTemplateRequest(ServiceRequest):
    """Represents a request to delete an existing custom verification email
    template.
    """

    TemplateName: EmailTemplateName


class DeleteCustomVerificationEmailTemplateResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class DeleteDedicatedIpPoolRequest(ServiceRequest):
    """A request to delete a dedicated IP pool."""

    PoolName: PoolName


class DeleteDedicatedIpPoolResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DeleteEmailIdentityPolicyRequest(ServiceRequest):
    """Represents a request to delete a sending authorization policy for an
    identity. Sending authorization is an Amazon SES feature that enables
    you to authorize other senders to use your identities. For information,
    see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-identity-owner-tasks-management.html>`__.
    """

    EmailIdentity: Identity
    PolicyName: PolicyName


class DeleteEmailIdentityPolicyResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DeleteEmailIdentityRequest(ServiceRequest):
    """A request to delete an existing email identity. When you delete an
    identity, you lose the ability to send email from that identity. You can
    restore your ability to send email by completing the verification
    process for the identity again.
    """

    EmailIdentity: Identity


class DeleteEmailIdentityResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DeleteEmailTemplateRequest(ServiceRequest):
    """Represents a request to delete an email template. For more information,
    see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.
    """

    TemplateName: EmailTemplateName


class DeleteEmailTemplateResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class DeleteSuppressedDestinationRequest(ServiceRequest):
    """A request to remove an email address from the suppression list for your
    account.
    """

    EmailAddress: EmailAddress


class DeleteSuppressedDestinationResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class DeliverabilityTestReport(TypedDict, total=False):
    """An object that contains metadata related to a predictive inbox placement
    test.
    """

    ReportId: Optional[ReportId]
    ReportName: Optional[ReportName]
    Subject: Optional[DeliverabilityTestSubject]
    FromEmailAddress: Optional[EmailAddress]
    CreateDate: Optional[Timestamp]
    DeliverabilityTestStatus: Optional[DeliverabilityTestStatus]


DeliverabilityTestReports = List[DeliverabilityTestReport]
Esps = List[Esp]
IpList = List[Ip]


class DomainDeliverabilityCampaign(TypedDict, total=False):
    """An object that contains the deliverability data for a specific campaign.
    This data is available for a campaign only if the campaign sent email by
    using a domain that the Deliverability dashboard is enabled for
    (``PutDeliverabilityDashboardOption`` operation).
    """

    CampaignId: Optional[CampaignId]
    ImageUrl: Optional[ImageUrl]
    Subject: Optional[Subject]
    FromAddress: Optional[Identity]
    SendingIps: Optional[IpList]
    FirstSeenDateTime: Optional[Timestamp]
    LastSeenDateTime: Optional[Timestamp]
    InboxCount: Optional[Volume]
    SpamCount: Optional[Volume]
    ReadRate: Optional[Percentage]
    DeleteRate: Optional[Percentage]
    ReadDeleteRate: Optional[Percentage]
    ProjectedVolume: Optional[Volume]
    Esps: Optional[Esps]


DomainDeliverabilityCampaignList = List[DomainDeliverabilityCampaign]
IspNameList = List[IspName]


class InboxPlacementTrackingOption(TypedDict, total=False):
    """An object that contains information about the inbox placement data
    settings for a verified domain that’s associated with your Amazon Web
    Services account. This data is available only if you enabled the
    Deliverability dashboard for the domain.
    """

    Global: Optional[Enabled]
    TrackedIsps: Optional[IspNameList]


class DomainDeliverabilityTrackingOption(TypedDict, total=False):
    """An object that contains information about the Deliverability dashboard
    subscription for a verified domain that you use to send email and
    currently has an active Deliverability dashboard subscription. If a
    Deliverability dashboard subscription is active for a domain, you gain
    access to reputation, inbox placement, and other metrics for the domain.
    """

    Domain: Optional[Domain]
    SubscriptionStartDate: Optional[Timestamp]
    InboxPlacementTrackingOption: Optional[InboxPlacementTrackingOption]


DomainDeliverabilityTrackingOptions = List[DomainDeliverabilityTrackingOption]


class EmailTemplateMetadata(TypedDict, total=False):
    """Contains information about an email template."""

    TemplateName: Optional[EmailTemplateName]
    CreatedTimestamp: Optional[Timestamp]


EmailTemplateMetadataList = List[EmailTemplateMetadata]


class EventDestination(TypedDict, total=False):
    """In the Amazon SES API v2, *events* include message sends, deliveries,
    opens, clicks, bounces, complaints and delivery delays. *Event
    destinations* are places that you can send information about these
    events to. For example, you can send event data to Amazon SNS to receive
    notifications when you receive bounces or complaints, or you can use
    Amazon Kinesis Data Firehose to stream data to Amazon S3 for long-term
    storage.
    """

    Name: EventDestinationName
    Enabled: Optional[Enabled]
    MatchingEventTypes: EventTypes
    KinesisFirehoseDestination: Optional[KinesisFirehoseDestination]
    CloudWatchDestination: Optional[CloudWatchDestination]
    SnsDestination: Optional[SnsDestination]
    PinpointDestination: Optional[PinpointDestination]


EventDestinations = List[EventDestination]


class FailureInfo(TypedDict, total=False):
    """An object that contains the failure details about an import job."""

    FailedRecordsS3Url: Optional[FailedRecordsS3Url]
    ErrorMessage: Optional[ErrorMessage]


class GetAccountRequest(ServiceRequest):
    """A request to obtain information about the email-sending capabilities of
    your Amazon SES account.
    """


class SuppressionAttributes(TypedDict, total=False):
    """An object that contains information about the email address suppression
    preferences for your account in the current Amazon Web Services Region.
    """

    SuppressedReasons: Optional[SuppressionListReasons]


class SendQuota(TypedDict, total=False):
    """An object that contains information about the per-day and per-second
    sending limits for your Amazon SES account in the current Amazon Web
    Services Region.
    """

    Max24HourSend: Optional[Max24HourSend]
    MaxSendRate: Optional[MaxSendRate]
    SentLast24Hours: Optional[SentLast24Hours]


class GetAccountResponse(TypedDict, total=False):
    """A list of details about the email-sending capabilities of your Amazon
    SES account in the current Amazon Web Services Region.
    """

    DedicatedIpAutoWarmupEnabled: Optional[Enabled]
    EnforcementStatus: Optional[GeneralEnforcementStatus]
    ProductionAccessEnabled: Optional[Enabled]
    SendQuota: Optional[SendQuota]
    SendingEnabled: Optional[Enabled]
    SuppressionAttributes: Optional[SuppressionAttributes]
    Details: Optional[AccountDetails]


class GetBlacklistReportsRequest(ServiceRequest):
    """A request to retrieve a list of the blacklists that your dedicated IP
    addresses appear on.
    """

    BlacklistItemNames: BlacklistItemNames


class GetBlacklistReportsResponse(TypedDict, total=False):
    """An object that contains information about blacklist events."""

    BlacklistReport: BlacklistReport


class GetConfigurationSetEventDestinationsRequest(ServiceRequest):
    """A request to obtain information about the event destinations for a
    configuration set.
    """

    ConfigurationSetName: ConfigurationSetName


class GetConfigurationSetEventDestinationsResponse(TypedDict, total=False):
    """Information about an event destination for a configuration set."""

    EventDestinations: Optional[EventDestinations]


class GetConfigurationSetRequest(ServiceRequest):
    """A request to obtain information about a configuration set."""

    ConfigurationSetName: ConfigurationSetName


class GetConfigurationSetResponse(TypedDict, total=False):
    """Information about a configuration set."""

    ConfigurationSetName: Optional[ConfigurationSetName]
    TrackingOptions: Optional[TrackingOptions]
    DeliveryOptions: Optional[DeliveryOptions]
    ReputationOptions: Optional[ReputationOptions]
    SendingOptions: Optional[SendingOptions]
    Tags: Optional[TagList]
    SuppressionOptions: Optional[SuppressionOptions]


class GetContactListRequest(ServiceRequest):
    ContactListName: ContactListName


class GetContactListResponse(TypedDict, total=False):
    ContactListName: Optional[ContactListName]
    Topics: Optional[Topics]
    Description: Optional[Description]
    CreatedTimestamp: Optional[Timestamp]
    LastUpdatedTimestamp: Optional[Timestamp]
    Tags: Optional[TagList]


class GetContactRequest(ServiceRequest):
    ContactListName: ContactListName
    EmailAddress: EmailAddress


class GetContactResponse(TypedDict, total=False):
    ContactListName: Optional[ContactListName]
    EmailAddress: Optional[EmailAddress]
    TopicPreferences: Optional[TopicPreferenceList]
    TopicDefaultPreferences: Optional[TopicPreferenceList]
    UnsubscribeAll: Optional[UnsubscribeAll]
    AttributesData: Optional[AttributesData]
    CreatedTimestamp: Optional[Timestamp]
    LastUpdatedTimestamp: Optional[Timestamp]


class GetCustomVerificationEmailTemplateRequest(ServiceRequest):
    """Represents a request to retrieve an existing custom verification email
    template.
    """

    TemplateName: EmailTemplateName


class GetCustomVerificationEmailTemplateResponse(TypedDict, total=False):
    """The following elements are returned by the service."""

    TemplateName: Optional[EmailTemplateName]
    FromEmailAddress: Optional[EmailAddress]
    TemplateSubject: Optional[EmailTemplateSubject]
    TemplateContent: Optional[TemplateContent]
    SuccessRedirectionURL: Optional[SuccessRedirectionURL]
    FailureRedirectionURL: Optional[FailureRedirectionURL]


class GetDedicatedIpRequest(ServiceRequest):
    """A request to obtain more information about a dedicated IP address."""

    Ip: Ip


class GetDedicatedIpResponse(TypedDict, total=False):
    """Information about a dedicated IP address."""

    DedicatedIp: Optional[DedicatedIp]


class GetDedicatedIpsRequest(ServiceRequest):
    """A request to obtain more information about dedicated IP pools."""

    PoolName: Optional[PoolName]
    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class GetDedicatedIpsResponse(TypedDict, total=False):
    """Information about the dedicated IP addresses that are associated with
    your Amazon Web Services account.
    """

    DedicatedIps: Optional[DedicatedIpList]
    NextToken: Optional[NextToken]


class GetDeliverabilityDashboardOptionsRequest(ServiceRequest):
    """Retrieve information about the status of the Deliverability dashboard
    for your Amazon Web Services account. When the Deliverability dashboard
    is enabled, you gain access to reputation, deliverability, and other
    metrics for your domains. You also gain the ability to perform
    predictive inbox placement tests.

    When you use the Deliverability dashboard, you pay a monthly
    subscription charge, in addition to any other fees that you accrue by
    using Amazon SES and other Amazon Web Services services. For more
    information about the features and cost of a Deliverability dashboard
    subscription, see `Amazon Pinpoint
    Pricing <http://aws.amazon.com/pinpoint/pricing/>`__.
    """


class GetDeliverabilityDashboardOptionsResponse(TypedDict, total=False):
    """An object that shows the status of the Deliverability dashboard."""

    DashboardEnabled: Enabled
    SubscriptionExpiryDate: Optional[Timestamp]
    AccountStatus: Optional[DeliverabilityDashboardAccountStatus]
    ActiveSubscribedDomains: Optional[DomainDeliverabilityTrackingOptions]
    PendingExpirationSubscribedDomains: Optional[DomainDeliverabilityTrackingOptions]


class GetDeliverabilityTestReportRequest(ServiceRequest):
    """A request to retrieve the results of a predictive inbox placement test."""

    ReportId: ReportId


class PlacementStatistics(TypedDict, total=False):
    """An object that contains inbox placement data for an email provider."""

    InboxPercentage: Optional[Percentage]
    SpamPercentage: Optional[Percentage]
    MissingPercentage: Optional[Percentage]
    SpfPercentage: Optional[Percentage]
    DkimPercentage: Optional[Percentage]


class IspPlacement(TypedDict, total=False):
    """An object that describes how email sent during the predictive inbox
    placement test was handled by a certain email provider.
    """

    IspName: Optional[IspName]
    PlacementStatistics: Optional[PlacementStatistics]


IspPlacements = List[IspPlacement]


class GetDeliverabilityTestReportResponse(TypedDict, total=False):
    """The results of the predictive inbox placement test."""

    DeliverabilityTestReport: DeliverabilityTestReport
    OverallPlacement: PlacementStatistics
    IspPlacements: IspPlacements
    Message: Optional[MessageContent]
    Tags: Optional[TagList]


class GetDomainDeliverabilityCampaignRequest(ServiceRequest):
    """Retrieve all the deliverability data for a specific campaign. This data
    is available for a campaign only if the campaign sent email by using a
    domain that the Deliverability dashboard is enabled for
    (``PutDeliverabilityDashboardOption`` operation).
    """

    CampaignId: CampaignId


class GetDomainDeliverabilityCampaignResponse(TypedDict, total=False):
    """An object that contains all the deliverability data for a specific
    campaign. This data is available for a campaign only if the campaign
    sent email by using a domain that the Deliverability dashboard is
    enabled for.
    """

    DomainDeliverabilityCampaign: DomainDeliverabilityCampaign


class GetDomainStatisticsReportRequest(ServiceRequest):
    """A request to obtain deliverability metrics for a domain."""

    Domain: Identity
    StartDate: Timestamp
    EndDate: Timestamp


class OverallVolume(TypedDict, total=False):
    """An object that contains information about email that was sent from the
    selected domain.
    """

    VolumeStatistics: Optional[VolumeStatistics]
    ReadRatePercent: Optional[Percentage]
    DomainIspPlacements: Optional[DomainIspPlacements]


class GetDomainStatisticsReportResponse(TypedDict, total=False):
    """An object that includes statistics that are related to the domain that
    you specified.
    """

    OverallVolume: OverallVolume
    DailyVolumes: DailyVolumes


class GetEmailIdentityPoliciesRequest(ServiceRequest):
    """A request to return the policies of an email identity."""

    EmailIdentity: Identity


PolicyMap = Dict[PolicyName, Policy]


class GetEmailIdentityPoliciesResponse(TypedDict, total=False):
    """Identity policies associated with email identity."""

    Policies: Optional[PolicyMap]


class GetEmailIdentityRequest(ServiceRequest):
    """A request to return details about an email identity."""

    EmailIdentity: Identity


class MailFromAttributes(TypedDict, total=False):
    """A list of attributes that are associated with a MAIL FROM domain."""

    MailFromDomain: MailFromDomainName
    MailFromDomainStatus: MailFromDomainStatus
    BehaviorOnMxFailure: BehaviorOnMxFailure


class GetEmailIdentityResponse(TypedDict, total=False):
    """Details about an email identity."""

    IdentityType: Optional[IdentityType]
    FeedbackForwardingStatus: Optional[Enabled]
    VerifiedForSendingStatus: Optional[Enabled]
    DkimAttributes: Optional[DkimAttributes]
    MailFromAttributes: Optional[MailFromAttributes]
    Policies: Optional[PolicyMap]
    Tags: Optional[TagList]
    ConfigurationSetName: Optional[ConfigurationSetName]


class GetEmailTemplateRequest(ServiceRequest):
    """Represents a request to display the template object (which includes the
    subject line, HTML part and text part) for the template you specify.
    """

    TemplateName: EmailTemplateName


class GetEmailTemplateResponse(TypedDict, total=False):
    """The following element is returned by the service."""

    TemplateName: EmailTemplateName
    TemplateContent: EmailTemplateContent


class GetImportJobRequest(ServiceRequest):
    """Represents a request for information about an import job using the
    import job ID.
    """

    JobId: JobId


class GetImportJobResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """

    JobId: Optional[JobId]
    ImportDestination: Optional[ImportDestination]
    ImportDataSource: Optional[ImportDataSource]
    FailureInfo: Optional[FailureInfo]
    JobStatus: Optional[JobStatus]
    CreatedTimestamp: Optional[Timestamp]
    CompletedTimestamp: Optional[Timestamp]
    ProcessedRecordsCount: Optional[ProcessedRecordsCount]
    FailedRecordsCount: Optional[FailedRecordsCount]


class GetSuppressedDestinationRequest(ServiceRequest):
    """A request to retrieve information about an email address that's on the
    suppression list for your account.
    """

    EmailAddress: EmailAddress


class SuppressedDestinationAttributes(TypedDict, total=False):
    """An object that contains additional attributes that are related an email
    address that is on the suppression list for your account.
    """

    MessageId: Optional[OutboundMessageId]
    FeedbackId: Optional[FeedbackId]


class SuppressedDestination(TypedDict, total=False):
    """An object that contains information about an email address that is on
    the suppression list for your account.
    """

    EmailAddress: EmailAddress
    Reason: SuppressionListReason
    LastUpdateTime: Timestamp
    Attributes: Optional[SuppressedDestinationAttributes]


class GetSuppressedDestinationResponse(TypedDict, total=False):
    """Information about the suppressed email address."""

    SuppressedDestination: SuppressedDestination


class IdentityInfo(TypedDict, total=False):
    """Information about an email identity."""

    IdentityType: Optional[IdentityType]
    IdentityName: Optional[Identity]
    SendingEnabled: Optional[Enabled]


IdentityInfoList = List[IdentityInfo]


class ImportJobSummary(TypedDict, total=False):
    """A summary of the import job."""

    JobId: Optional[JobId]
    ImportDestination: Optional[ImportDestination]
    JobStatus: Optional[JobStatus]
    CreatedTimestamp: Optional[Timestamp]


ImportJobSummaryList = List[ImportJobSummary]


class ListConfigurationSetsRequest(ServiceRequest):
    """A request to obtain a list of configuration sets for your Amazon SES
    account in the current Amazon Web Services Region.
    """

    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListConfigurationSetsResponse(TypedDict, total=False):
    """A list of configuration sets in your Amazon SES account in the current
    Amazon Web Services Region.
    """

    ConfigurationSets: Optional[ConfigurationSetNameList]
    NextToken: Optional[NextToken]


class ListContactListsRequest(ServiceRequest):
    PageSize: Optional[MaxItems]
    NextToken: Optional[NextToken]


ListOfContactLists = List[ContactList]


class ListContactListsResponse(TypedDict, total=False):
    ContactLists: Optional[ListOfContactLists]
    NextToken: Optional[NextToken]


class TopicFilter(TypedDict, total=False):
    """Used for filtering by a specific topic preference."""

    TopicName: Optional[TopicName]
    UseDefaultIfPreferenceUnavailable: Optional[UseDefaultIfPreferenceUnavailable]


class ListContactsFilter(TypedDict, total=False):
    """A filter that can be applied to a list of contacts."""

    FilteredStatus: Optional[SubscriptionStatus]
    TopicFilter: Optional[TopicFilter]


class ListContactsRequest(ServiceRequest):
    ContactListName: ContactListName
    Filter: Optional[ListContactsFilter]
    PageSize: Optional[MaxItems]
    NextToken: Optional[NextToken]


ListOfContacts = List[Contact]


class ListContactsResponse(TypedDict, total=False):
    Contacts: Optional[ListOfContacts]
    NextToken: Optional[NextToken]


class ListCustomVerificationEmailTemplatesRequest(ServiceRequest):
    """Represents a request to list the existing custom verification email
    templates for your account.
    """

    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListCustomVerificationEmailTemplatesResponse(TypedDict, total=False):
    """The following elements are returned by the service."""

    CustomVerificationEmailTemplates: Optional[CustomVerificationEmailTemplatesList]
    NextToken: Optional[NextToken]


class ListDedicatedIpPoolsRequest(ServiceRequest):
    """A request to obtain a list of dedicated IP pools."""

    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


ListOfDedicatedIpPools = List[PoolName]


class ListDedicatedIpPoolsResponse(TypedDict, total=False):
    """A list of dedicated IP pools."""

    DedicatedIpPools: Optional[ListOfDedicatedIpPools]
    NextToken: Optional[NextToken]


class ListDeliverabilityTestReportsRequest(ServiceRequest):
    """A request to list all of the predictive inbox placement tests that
    you've performed.
    """

    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListDeliverabilityTestReportsResponse(TypedDict, total=False):
    """A list of the predictive inbox placement test reports that are available
    for your account, regardless of whether or not those tests are complete.
    """

    DeliverabilityTestReports: DeliverabilityTestReports
    NextToken: Optional[NextToken]


class ListDomainDeliverabilityCampaignsRequest(ServiceRequest):
    """Retrieve deliverability data for all the campaigns that used a specific
    domain to send email during a specified time range. This data is
    available for a domain only if you enabled the Deliverability dashboard.
    """

    StartDate: Timestamp
    EndDate: Timestamp
    SubscribedDomain: Domain
    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListDomainDeliverabilityCampaignsResponse(TypedDict, total=False):
    """An array of objects that provide deliverability data for all the
    campaigns that used a specific domain to send email during a specified
    time range. This data is available for a domain only if you enabled the
    Deliverability dashboard for the domain.
    """

    DomainDeliverabilityCampaigns: DomainDeliverabilityCampaignList
    NextToken: Optional[NextToken]


class ListEmailIdentitiesRequest(ServiceRequest):
    """A request to list all of the email identities associated with your
    Amazon Web Services account. This list includes identities that you've
    already verified, identities that are unverified, and identities that
    were verified in the past, but are no longer verified.
    """

    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListEmailIdentitiesResponse(TypedDict, total=False):
    """A list of all of the identities that you've attempted to verify,
    regardless of whether or not those identities were successfully
    verified.
    """

    EmailIdentities: Optional[IdentityInfoList]
    NextToken: Optional[NextToken]


class ListEmailTemplatesRequest(ServiceRequest):
    """Represents a request to list the email templates present in your Amazon
    SES account in the current Amazon Web Services Region. For more
    information, see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.
    """

    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListEmailTemplatesResponse(TypedDict, total=False):
    """The following elements are returned by the service."""

    TemplatesMetadata: Optional[EmailTemplateMetadataList]
    NextToken: Optional[NextToken]


class ListImportJobsRequest(ServiceRequest):
    """Represents a request to list all of the import jobs for a data
    destination within the specified maximum number of import jobs.
    """

    ImportDestinationType: Optional[ImportDestinationType]
    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class ListImportJobsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """

    ImportJobs: Optional[ImportJobSummaryList]
    NextToken: Optional[NextToken]


class ListManagementOptions(TypedDict, total=False):
    """An object used to specify a list or topic to which an email belongs,
    which will be used when a contact chooses to unsubscribe.
    """

    ContactListName: ContactListName
    TopicName: Optional[TopicName]


class ListSuppressedDestinationsRequest(ServiceRequest):
    """A request to obtain a list of email destinations that are on the
    suppression list for your account.
    """

    Reasons: Optional[SuppressionListReasons]
    StartDate: Optional[Timestamp]
    EndDate: Optional[Timestamp]
    NextToken: Optional[NextToken]
    PageSize: Optional[MaxItems]


class SuppressedDestinationSummary(TypedDict, total=False):
    """A summary that describes the suppressed email address."""

    EmailAddress: EmailAddress
    Reason: SuppressionListReason
    LastUpdateTime: Timestamp


SuppressedDestinationSummaries = List[SuppressedDestinationSummary]


class ListSuppressedDestinationsResponse(TypedDict, total=False):
    """A list of suppressed email addresses."""

    SuppressedDestinationSummaries: Optional[SuppressedDestinationSummaries]
    NextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceArn: AmazonResourceName


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: TagList


class PutAccountDedicatedIpWarmupAttributesRequest(ServiceRequest):
    """A request to enable or disable the automatic IP address warm-up feature."""

    AutoWarmupEnabled: Optional[Enabled]


class PutAccountDedicatedIpWarmupAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutAccountDetailsRequest(ServiceRequest):
    """A request to submit new account details."""

    MailType: MailType
    WebsiteURL: WebsiteURL
    ContactLanguage: Optional[ContactLanguage]
    UseCaseDescription: UseCaseDescription
    AdditionalContactEmailAddresses: Optional[AdditionalContactEmailAddresses]
    ProductionAccessEnabled: Optional[EnabledWrapper]


class PutAccountDetailsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutAccountSendingAttributesRequest(ServiceRequest):
    """A request to change the ability of your account to send email."""

    SendingEnabled: Optional[Enabled]


class PutAccountSendingAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutAccountSuppressionAttributesRequest(ServiceRequest):
    """A request to change your account's suppression preferences."""

    SuppressedReasons: Optional[SuppressionListReasons]


class PutAccountSuppressionAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutConfigurationSetDeliveryOptionsRequest(ServiceRequest):
    """A request to associate a configuration set with a dedicated IP pool."""

    ConfigurationSetName: ConfigurationSetName
    TlsPolicy: Optional[TlsPolicy]
    SendingPoolName: Optional[SendingPoolName]


class PutConfigurationSetDeliveryOptionsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutConfigurationSetReputationOptionsRequest(ServiceRequest):
    """A request to enable or disable tracking of reputation metrics for a
    configuration set.
    """

    ConfigurationSetName: ConfigurationSetName
    ReputationMetricsEnabled: Optional[Enabled]


class PutConfigurationSetReputationOptionsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutConfigurationSetSendingOptionsRequest(ServiceRequest):
    """A request to enable or disable the ability of Amazon SES to send emails
    that use a specific configuration set.
    """

    ConfigurationSetName: ConfigurationSetName
    SendingEnabled: Optional[Enabled]


class PutConfigurationSetSendingOptionsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutConfigurationSetSuppressionOptionsRequest(ServiceRequest):
    """A request to change the account suppression list preferences for a
    specific configuration set.
    """

    ConfigurationSetName: ConfigurationSetName
    SuppressedReasons: Optional[SuppressionListReasons]


class PutConfigurationSetSuppressionOptionsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutConfigurationSetTrackingOptionsRequest(ServiceRequest):
    """A request to add a custom domain for tracking open and click events to a
    configuration set.
    """

    ConfigurationSetName: ConfigurationSetName
    CustomRedirectDomain: Optional[CustomRedirectDomain]


class PutConfigurationSetTrackingOptionsResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutDedicatedIpInPoolRequest(ServiceRequest):
    """A request to move a dedicated IP address to a dedicated IP pool."""

    Ip: Ip
    DestinationPoolName: PoolName


class PutDedicatedIpInPoolResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutDedicatedIpWarmupAttributesRequest(ServiceRequest):
    """A request to change the warm-up attributes for a dedicated IP address.
    This operation is useful when you want to resume the warm-up process for
    an existing IP address.
    """

    Ip: Ip
    WarmupPercentage: Percentage100Wrapper


class PutDedicatedIpWarmupAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutDeliverabilityDashboardOptionRequest(ServiceRequest):
    """Enable or disable the Deliverability dashboard. When you enable the
    Deliverability dashboard, you gain access to reputation, deliverability,
    and other metrics for the domains that you use to send email using
    Amazon SES API v2. You also gain the ability to perform predictive inbox
    placement tests.

    When you use the Deliverability dashboard, you pay a monthly
    subscription charge, in addition to any other fees that you accrue by
    using Amazon SES and other Amazon Web Services services. For more
    information about the features and cost of a Deliverability dashboard
    subscription, see `Amazon Pinpoint
    Pricing <http://aws.amazon.com/pinpoint/pricing/>`__.
    """

    DashboardEnabled: Enabled
    SubscribedDomains: Optional[DomainDeliverabilityTrackingOptions]


class PutDeliverabilityDashboardOptionResponse(TypedDict, total=False):
    """A response that indicates whether the Deliverability dashboard is
    enabled.
    """


class PutEmailIdentityConfigurationSetAttributesRequest(ServiceRequest):
    """A request to associate a configuration set with an email identity."""

    EmailIdentity: Identity
    ConfigurationSetName: Optional[ConfigurationSetName]


class PutEmailIdentityConfigurationSetAttributesResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class PutEmailIdentityDkimAttributesRequest(ServiceRequest):
    """A request to enable or disable DKIM signing of email that you send from
    an email identity.
    """

    EmailIdentity: Identity
    SigningEnabled: Optional[Enabled]


class PutEmailIdentityDkimAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutEmailIdentityDkimSigningAttributesRequest(ServiceRequest):
    """A request to change the DKIM attributes for an email identity."""

    EmailIdentity: Identity
    SigningAttributesOrigin: DkimSigningAttributesOrigin
    SigningAttributes: Optional[DkimSigningAttributes]


class PutEmailIdentityDkimSigningAttributesResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200
    response.

    The following data is returned in JSON format by the service.
    """

    DkimStatus: Optional[DkimStatus]
    DkimTokens: Optional[DnsTokenList]


class PutEmailIdentityFeedbackAttributesRequest(ServiceRequest):
    """A request to set the attributes that control how bounce and complaint
    events are processed.
    """

    EmailIdentity: Identity
    EmailForwardingEnabled: Optional[Enabled]


class PutEmailIdentityFeedbackAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutEmailIdentityMailFromAttributesRequest(ServiceRequest):
    """A request to configure the custom MAIL FROM domain for a verified
    identity.
    """

    EmailIdentity: Identity
    MailFromDomain: Optional[MailFromDomainName]
    BehaviorOnMxFailure: Optional[BehaviorOnMxFailure]


class PutEmailIdentityMailFromAttributesResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class PutSuppressedDestinationRequest(ServiceRequest):
    """A request to add an email destination to the suppression list for your
    account.
    """

    EmailAddress: EmailAddress
    Reason: SuppressionListReason


class PutSuppressedDestinationResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class SendBulkEmailRequest(ServiceRequest):
    """Represents a request to send email messages to multiple destinations
    using Amazon SES. For more information, see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.
    """

    FromEmailAddress: Optional[EmailAddress]
    FromEmailAddressIdentityArn: Optional[AmazonResourceName]
    ReplyToAddresses: Optional[EmailAddressList]
    FeedbackForwardingEmailAddress: Optional[EmailAddress]
    FeedbackForwardingEmailAddressIdentityArn: Optional[AmazonResourceName]
    DefaultEmailTags: Optional[MessageTagList]
    DefaultContent: BulkEmailContent
    BulkEmailEntries: BulkEmailEntryList
    ConfigurationSetName: Optional[ConfigurationSetName]


class SendBulkEmailResponse(TypedDict, total=False):
    """The following data is returned in JSON format by the service."""

    BulkEmailEntryResults: BulkEmailEntryResultList


class SendCustomVerificationEmailRequest(ServiceRequest):
    """Represents a request to send a custom verification email to a specified
    recipient.
    """

    EmailAddress: EmailAddress
    TemplateName: EmailTemplateName
    ConfigurationSetName: Optional[ConfigurationSetName]


class SendCustomVerificationEmailResponse(TypedDict, total=False):
    """The following element is returned by the service."""

    MessageId: Optional[OutboundMessageId]


class SendEmailRequest(ServiceRequest):
    """Represents a request to send a single formatted email using Amazon SES.
    For more information, see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-formatted.html>`__.
    """

    FromEmailAddress: Optional[EmailAddress]
    FromEmailAddressIdentityArn: Optional[AmazonResourceName]
    Destination: Optional[Destination]
    ReplyToAddresses: Optional[EmailAddressList]
    FeedbackForwardingEmailAddress: Optional[EmailAddress]
    FeedbackForwardingEmailAddressIdentityArn: Optional[AmazonResourceName]
    Content: EmailContent
    EmailTags: Optional[MessageTagList]
    ConfigurationSetName: Optional[ConfigurationSetName]
    ListManagementOptions: Optional[ListManagementOptions]


class SendEmailResponse(TypedDict, total=False):
    """A unique message ID that you receive when an email is accepted for
    sending.
    """

    MessageId: Optional[OutboundMessageId]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceArn: AmazonResourceName
    Tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class TestRenderEmailTemplateRequest(ServiceRequest):
    """>Represents a request to create a preview of the MIME content of an
    email when provided with a template and a set of replacement data.
    """

    TemplateName: EmailTemplateName
    TemplateData: EmailTemplateData


class TestRenderEmailTemplateResponse(TypedDict, total=False):
    """The following element is returned by the service."""

    RenderedTemplate: RenderedEmailTemplate


class UntagResourceRequest(ServiceRequest):
    ResourceArn: AmazonResourceName
    TagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateConfigurationSetEventDestinationRequest(ServiceRequest):
    """A request to change the settings for an event destination for a
    configuration set.
    """

    ConfigurationSetName: ConfigurationSetName
    EventDestinationName: EventDestinationName
    EventDestination: EventDestinationDefinition


class UpdateConfigurationSetEventDestinationResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class UpdateContactListRequest(ServiceRequest):
    ContactListName: ContactListName
    Topics: Optional[Topics]
    Description: Optional[Description]


class UpdateContactListResponse(TypedDict, total=False):
    pass


class UpdateContactRequest(ServiceRequest):
    ContactListName: ContactListName
    EmailAddress: EmailAddress
    TopicPreferences: Optional[TopicPreferenceList]
    UnsubscribeAll: Optional[UnsubscribeAll]
    AttributesData: Optional[AttributesData]


class UpdateContactResponse(TypedDict, total=False):
    pass


class UpdateCustomVerificationEmailTemplateRequest(ServiceRequest):
    """Represents a request to update an existing custom verification email
    template.
    """

    TemplateName: EmailTemplateName
    FromEmailAddress: EmailAddress
    TemplateSubject: EmailTemplateSubject
    TemplateContent: TemplateContent
    SuccessRedirectionURL: SuccessRedirectionURL
    FailureRedirectionURL: FailureRedirectionURL


class UpdateCustomVerificationEmailTemplateResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class UpdateEmailIdentityPolicyRequest(ServiceRequest):
    """Represents a request to update a sending authorization policy for an
    identity. Sending authorization is an Amazon SES feature that enables
    you to authorize other senders to use your identities. For information,
    see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-identity-owner-tasks-management.html>`__.
    """

    EmailIdentity: Identity
    PolicyName: PolicyName
    Policy: Policy


class UpdateEmailIdentityPolicyResponse(TypedDict, total=False):
    """An HTTP 200 response if the request succeeds, or an error message if the
    request fails.
    """


class UpdateEmailTemplateRequest(ServiceRequest):
    """Represents a request to update an email template. For more information,
    see the `Amazon SES Developer
    Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.
    """

    TemplateName: EmailTemplateName
    TemplateContent: EmailTemplateContent


class UpdateEmailTemplateResponse(TypedDict, total=False):
    """If the action is successful, the service sends back an HTTP 200 response
    with an empty HTTP body.
    """


class Sesv2Api:

    service = "sesv2"
    version = "2019-09-27"

    @handler("CreateConfigurationSet")
    def create_configuration_set(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        tracking_options: TrackingOptions = None,
        delivery_options: DeliveryOptions = None,
        reputation_options: ReputationOptions = None,
        sending_options: SendingOptions = None,
        tags: TagList = None,
        suppression_options: SuppressionOptions = None,
    ) -> CreateConfigurationSetResponse:
        """Create a configuration set. *Configuration sets* are groups of rules
        that you can apply to the emails that you send. You apply a
        configuration set to an email by specifying the name of the
        configuration set when you call the Amazon SES API v2. When you apply a
        configuration set to an email, all of the rules in that configuration
        set are applied to the email.

        :param configuration_set_name: The name of the configuration set.
        :param tracking_options: An object that defines the open and click tracking options for emails
        that you send using the configuration set.
        :param delivery_options: An object that defines the dedicated IP pool that is used to send emails
        that you send using the configuration set.
        :param reputation_options: An object that defines whether or not Amazon SES collects reputation
        metrics for the emails that you send that use the configuration set.
        :param sending_options: An object that defines whether or not Amazon SES can send email that you
        send using the configuration set.
        :param tags: An array of objects that define the tags (keys and values) to associate
        with the configuration set.
        :param suppression_options: An object that contains information about the suppression list
        preferences for your account.
        :returns: CreateConfigurationSetResponse
        :raises AlreadyExistsException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateConfigurationSetEventDestination")
    def create_configuration_set_event_destination(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        event_destination_name: EventDestinationName,
        event_destination: EventDestinationDefinition,
    ) -> CreateConfigurationSetEventDestinationResponse:
        """Create an event destination. *Events* include message sends, deliveries,
        opens, clicks, bounces, and complaints. *Event destinations* are places
        that you can send information about these events to. For example, you
        can send event data to Amazon SNS to receive notifications when you
        receive bounces or complaints, or you can use Amazon Kinesis Data
        Firehose to stream data to Amazon S3 for long-term storage.

        A single configuration set can include more than one event destination.

        :param configuration_set_name: The name of the configuration set .
        :param event_destination_name: A name that identifies the event destination within the configuration
        set.
        :param event_destination: An object that defines the event destination.
        :returns: CreateConfigurationSetEventDestinationResponse
        :raises NotFoundException:
        :raises AlreadyExistsException:
        :raises LimitExceededException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("CreateContact")
    def create_contact(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        email_address: EmailAddress,
        topic_preferences: TopicPreferenceList = None,
        unsubscribe_all: UnsubscribeAll = None,
        attributes_data: AttributesData = None,
    ) -> CreateContactResponse:
        """Creates a contact, which is an end-user who is receiving the email, and
        adds them to a contact list.

        :param contact_list_name: The name of the contact list to which the contact should be added.
        :param email_address: The contact's email address.
        :param topic_preferences: The contact's preferences for being opted-in to or opted-out of topics.
        :param unsubscribe_all: A boolean value status noting if the contact is unsubscribed from all
        contact list topics.
        :param attributes_data: The attribute data attached to a contact.
        :returns: CreateContactResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises AlreadyExistsException:
        """
        raise NotImplementedError

    @handler("CreateContactList")
    def create_contact_list(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        topics: Topics = None,
        description: Description = None,
        tags: TagList = None,
    ) -> CreateContactListResponse:
        """Creates a contact list.

        :param contact_list_name: The name of the contact list.
        :param topics: An interest group, theme, or label within a list.
        :param description: A description of what the contact list is about.
        :param tags: The tags associated with a contact list.
        :returns: CreateContactListResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises AlreadyExistsException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateCustomVerificationEmailTemplate")
    def create_custom_verification_email_template(
        self,
        context: RequestContext,
        template_name: EmailTemplateName,
        from_email_address: EmailAddress,
        template_subject: EmailTemplateSubject,
        template_content: TemplateContent,
        success_redirection_url: SuccessRedirectionURL,
        failure_redirection_url: FailureRedirectionURL,
    ) -> CreateCustomVerificationEmailTemplateResponse:
        """Creates a new custom verification email template.

        For more information about custom verification email templates, see
        `Using Custom Verification Email
        Templates <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-verify-address-custom.html>`__
        in the *Amazon SES Developer Guide*.

        You can execute this operation no more than once per second.

        :param template_name: The name of the custom verification email template.
        :param from_email_address: The email address that the custom verification email is sent from.
        :param template_subject: The subject line of the custom verification email.
        :param template_content: The content of the custom verification email.
        :param success_redirection_url: The URL that the recipient of the verification email is sent to if his
        or her address is successfully verified.
        :param failure_redirection_url: The URL that the recipient of the verification email is sent to if his
        or her address is not successfully verified.
        :returns: CreateCustomVerificationEmailTemplateResponse
        :raises BadRequestException:
        :raises AlreadyExistsException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateDedicatedIpPool")
    def create_dedicated_ip_pool(
        self, context: RequestContext, pool_name: PoolName, tags: TagList = None
    ) -> CreateDedicatedIpPoolResponse:
        """Create a new pool of dedicated IP addresses. A pool can include one or
        more dedicated IP addresses that are associated with your Amazon Web
        Services account. You can associate a pool with a configuration set.
        When you send an email that uses that configuration set, the message is
        sent from one of the addresses in the associated pool.

        :param pool_name: The name of the dedicated IP pool.
        :param tags: An object that defines the tags (keys and values) that you want to
        associate with the pool.
        :returns: CreateDedicatedIpPoolResponse
        :raises AlreadyExistsException:
        :raises LimitExceededException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateDeliverabilityTestReport")
    def create_deliverability_test_report(
        self,
        context: RequestContext,
        from_email_address: EmailAddress,
        content: EmailContent,
        report_name: ReportName = None,
        tags: TagList = None,
    ) -> CreateDeliverabilityTestReportResponse:
        """Create a new predictive inbox placement test. Predictive inbox placement
        tests can help you predict how your messages will be handled by various
        email providers around the world. When you perform a predictive inbox
        placement test, you provide a sample message that contains the content
        that you plan to send to your customers. Amazon SES then sends that
        message to special email addresses spread across several major email
        providers. After about 24 hours, the test is complete, and you can use
        the ``GetDeliverabilityTestReport`` operation to view the results of the
        test.

        :param from_email_address: The email address that the predictive inbox placement test email was
        sent from.
        :param content: The HTML body of the message that you sent when you performed the
        predictive inbox placement test.
        :param report_name: A unique name that helps you to identify the predictive inbox placement
        test when you retrieve the results.
        :param tags: An array of objects that define the tags (keys and values) that you want
        to associate with the predictive inbox placement test.
        :returns: CreateDeliverabilityTestReportResponse
        :raises AccountSuspendedException:
        :raises SendingPausedException:
        :raises MessageRejected:
        :raises MailFromDomainNotVerifiedException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateEmailIdentity")
    def create_email_identity(
        self,
        context: RequestContext,
        email_identity: Identity,
        tags: TagList = None,
        dkim_signing_attributes: DkimSigningAttributes = None,
        configuration_set_name: ConfigurationSetName = None,
    ) -> CreateEmailIdentityResponse:
        """Starts the process of verifying an email identity. An *identity* is an
        email address or domain that you use when you send email. Before you can
        use an identity to send email, you first have to verify it. By verifying
        an identity, you demonstrate that you're the owner of the identity, and
        that you've given Amazon SES API v2 permission to send email from the
        identity.

        When you verify an email address, Amazon SES sends an email to the
        address. Your email address is verified as soon as you follow the link
        in the verification email.

        When you verify a domain without specifying the
        ``DkimSigningAttributes`` object, this operation provides a set of DKIM
        tokens. You can convert these tokens into CNAME records, which you then
        add to the DNS configuration for your domain. Your domain is verified
        when Amazon SES detects these records in the DNS configuration for your
        domain. This verification method is known as `Easy
        DKIM <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/easy-dkim.html>`__.

        Alternatively, you can perform the verification process by providing
        your own public-private key pair. This verification method is known as
        Bring Your Own DKIM (BYODKIM). To use BYODKIM, your call to the
        ``CreateEmailIdentity`` operation has to include the
        ``DkimSigningAttributes`` object. When you specify this object, you
        provide a selector (a component of the DNS record name that identifies
        the public key to use for DKIM authentication) and a private key.

        When you verify a domain, this operation provides a set of DKIM tokens,
        which you can convert into CNAME tokens. You add these CNAME tokens to
        the DNS configuration for your domain. Your domain is verified when
        Amazon SES detects these records in the DNS configuration for your
        domain. For some DNS providers, it can take 72 hours or more to complete
        the domain verification process.

        Additionally, you can associate an existing configuration set with the
        email identity that you're verifying.

        :param email_identity: The email address or domain to verify.
        :param tags: An array of objects that define the tags (keys and values) to associate
        with the email identity.
        :param dkim_signing_attributes: If your request includes this object, Amazon SES configures the identity
        to use Bring Your Own DKIM (BYODKIM) for DKIM authentication purposes,
        or, configures the key length to be used for `Easy
        DKIM <https://docs.
        :param configuration_set_name: The configuration set to use by default when sending from this identity.
        :returns: CreateEmailIdentityResponse
        :raises AlreadyExistsException:
        :raises LimitExceededException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("CreateEmailIdentityPolicy")
    def create_email_identity_policy(
        self,
        context: RequestContext,
        email_identity: Identity,
        policy_name: PolicyName,
        policy: Policy,
    ) -> CreateEmailIdentityPolicyResponse:
        """Creates the specified sending authorization policy for the given
        identity (an email address or a domain).

        This API is for the identity owner only. If you have not verified the
        identity, this API will return an error.

        Sending authorization is a feature that enables an identity owner to
        authorize other senders to use its identities. For information about
        using sending authorization, see the `Amazon SES Developer
        Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization.html>`__.

        You can execute this operation no more than once per second.

        :param email_identity: The email identity.
        :param policy_name: The name of the policy.
        :param policy: The text of the policy in JSON format.
        :returns: CreateEmailIdentityPolicyResponse
        :raises NotFoundException:
        :raises AlreadyExistsException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("CreateEmailTemplate")
    def create_email_template(
        self,
        context: RequestContext,
        template_name: EmailTemplateName,
        template_content: EmailTemplateContent,
    ) -> CreateEmailTemplateResponse:
        """Creates an email template. Email templates enable you to send
        personalized email to one or more destinations in a single API
        operation. For more information, see the `Amazon SES Developer
        Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.

        You can execute this operation no more than once per second.

        :param template_name: The name of the template.
        :param template_content: The content of the email template, composed of a subject line, an HTML
        part, and a text-only part.
        :returns: CreateEmailTemplateResponse
        :raises AlreadyExistsException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateImportJob")
    def create_import_job(
        self,
        context: RequestContext,
        import_destination: ImportDestination,
        import_data_source: ImportDataSource,
    ) -> CreateImportJobResponse:
        """Creates an import job for a data destination.

        :param import_destination: The destination for the import job.
        :param import_data_source: The data source for the import job.
        :returns: CreateImportJobResponse
        :raises BadRequestException:
        :raises LimitExceededException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("DeleteConfigurationSet")
    def delete_configuration_set(
        self, context: RequestContext, configuration_set_name: ConfigurationSetName
    ) -> DeleteConfigurationSetResponse:
        """Delete an existing configuration set.

        *Configuration sets* are groups of rules that you can apply to the
        emails you send. You apply a configuration set to an email by including
        a reference to the configuration set in the headers of the email. When
        you apply a configuration set to an email, all of the rules in that
        configuration set are applied to the email.

        :param configuration_set_name: The name of the configuration set.
        :returns: DeleteConfigurationSetResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteConfigurationSetEventDestination")
    def delete_configuration_set_event_destination(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        event_destination_name: EventDestinationName,
    ) -> DeleteConfigurationSetEventDestinationResponse:
        """Delete an event destination.

        *Events* include message sends, deliveries, opens, clicks, bounces, and
        complaints. *Event destinations* are places that you can send
        information about these events to. For example, you can send event data
        to Amazon SNS to receive notifications when you receive bounces or
        complaints, or you can use Amazon Kinesis Data Firehose to stream data
        to Amazon S3 for long-term storage.

        :param configuration_set_name: The name of the configuration set that contains the event destination to
        delete.
        :param event_destination_name: The name of the event destination to delete.
        :returns: DeleteConfigurationSetEventDestinationResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteContact")
    def delete_contact(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        email_address: EmailAddress,
    ) -> DeleteContactResponse:
        """Removes a contact from a contact list.

        :param contact_list_name: The name of the contact list from which the contact should be removed.
        :param email_address: The contact's email address.
        :returns: DeleteContactResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteContactList")
    def delete_contact_list(
        self, context: RequestContext, contact_list_name: ContactListName
    ) -> DeleteContactListResponse:
        """Deletes a contact list and all of the contacts on that list.

        :param contact_list_name: The name of the contact list.
        :returns: DeleteContactListResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteCustomVerificationEmailTemplate")
    def delete_custom_verification_email_template(
        self, context: RequestContext, template_name: EmailTemplateName
    ) -> DeleteCustomVerificationEmailTemplateResponse:
        """Deletes an existing custom verification email template.

        For more information about custom verification email templates, see
        `Using Custom Verification Email
        Templates <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-verify-address-custom.html>`__
        in the *Amazon SES Developer Guide*.

        You can execute this operation no more than once per second.

        :param template_name: The name of the custom verification email template that you want to
        delete.
        :returns: DeleteCustomVerificationEmailTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteDedicatedIpPool")
    def delete_dedicated_ip_pool(
        self, context: RequestContext, pool_name: PoolName
    ) -> DeleteDedicatedIpPoolResponse:
        """Delete a dedicated IP pool.

        :param pool_name: The name of the dedicated IP pool that you want to delete.
        :returns: DeleteDedicatedIpPoolResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteEmailIdentity")
    def delete_email_identity(
        self, context: RequestContext, email_identity: Identity
    ) -> DeleteEmailIdentityResponse:
        """Deletes an email identity. An identity can be either an email address or
        a domain name.

        :param email_identity: The identity (that is, the email address or domain) to delete.
        :returns: DeleteEmailIdentityResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteEmailIdentityPolicy")
    def delete_email_identity_policy(
        self, context: RequestContext, email_identity: Identity, policy_name: PolicyName
    ) -> DeleteEmailIdentityPolicyResponse:
        """Deletes the specified sending authorization policy for the given
        identity (an email address or a domain). This API returns successfully
        even if a policy with the specified name does not exist.

        This API is for the identity owner only. If you have not verified the
        identity, this API will return an error.

        Sending authorization is a feature that enables an identity owner to
        authorize other senders to use its identities. For information about
        using sending authorization, see the `Amazon SES Developer
        Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization.html>`__.

        You can execute this operation no more than once per second.

        :param email_identity: The email identity.
        :param policy_name: The name of the policy.
        :returns: DeleteEmailIdentityPolicyResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteEmailTemplate")
    def delete_email_template(
        self, context: RequestContext, template_name: EmailTemplateName
    ) -> DeleteEmailTemplateResponse:
        """Deletes an email template.

        You can execute this operation no more than once per second.

        :param template_name: The name of the template to be deleted.
        :returns: DeleteEmailTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("DeleteSuppressedDestination")
    def delete_suppressed_destination(
        self, context: RequestContext, email_address: EmailAddress
    ) -> DeleteSuppressedDestinationResponse:
        """Removes an email address from the suppression list for your account.

        :param email_address: The suppressed email destination to remove from the account suppression
        list.
        :returns: DeleteSuppressedDestinationResponse
        :raises NotFoundException:
        :raises BadRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetAccount")
    def get_account(
        self,
        context: RequestContext,
    ) -> GetAccountResponse:
        """Obtain information about the email-sending status and capabilities of
        your Amazon SES account in the current Amazon Web Services Region.

        :returns: GetAccountResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetBlacklistReports")
    def get_blacklist_reports(
        self, context: RequestContext, blacklist_item_names: BlacklistItemNames
    ) -> GetBlacklistReportsResponse:
        """Retrieve a list of the blacklists that your dedicated IP addresses
        appear on.

        :param blacklist_item_names: A list of IP addresses that you want to retrieve blacklist information
        about.
        :returns: GetBlacklistReportsResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetConfigurationSet")
    def get_configuration_set(
        self, context: RequestContext, configuration_set_name: ConfigurationSetName
    ) -> GetConfigurationSetResponse:
        """Get information about an existing configuration set, including the
        dedicated IP pool that it's associated with, whether or not it's enabled
        for sending email, and more.

        *Configuration sets* are groups of rules that you can apply to the
        emails you send. You apply a configuration set to an email by including
        a reference to the configuration set in the headers of the email. When
        you apply a configuration set to an email, all of the rules in that
        configuration set are applied to the email.

        :param configuration_set_name: The name of the configuration set.
        :returns: GetConfigurationSetResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetConfigurationSetEventDestinations")
    def get_configuration_set_event_destinations(
        self, context: RequestContext, configuration_set_name: ConfigurationSetName
    ) -> GetConfigurationSetEventDestinationsResponse:
        """Retrieve a list of event destinations that are associated with a
        configuration set.

        *Events* include message sends, deliveries, opens, clicks, bounces, and
        complaints. *Event destinations* are places that you can send
        information about these events to. For example, you can send event data
        to Amazon SNS to receive notifications when you receive bounces or
        complaints, or you can use Amazon Kinesis Data Firehose to stream data
        to Amazon S3 for long-term storage.

        :param configuration_set_name: The name of the configuration set that contains the event destination.
        :returns: GetConfigurationSetEventDestinationsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetContact")
    def get_contact(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        email_address: EmailAddress,
    ) -> GetContactResponse:
        """Returns a contact from a contact list.

        :param contact_list_name: The name of the contact list to which the contact belongs.
        :param email_address: The contact's email addres.
        :returns: GetContactResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("GetContactList")
    def get_contact_list(
        self, context: RequestContext, contact_list_name: ContactListName
    ) -> GetContactListResponse:
        """Returns contact list metadata. It does not return any information about
        the contacts present in the list.

        :param contact_list_name: The name of the contact list.
        :returns: GetContactListResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetCustomVerificationEmailTemplate")
    def get_custom_verification_email_template(
        self, context: RequestContext, template_name: EmailTemplateName
    ) -> GetCustomVerificationEmailTemplateResponse:
        """Returns the custom email verification template for the template name you
        specify.

        For more information about custom verification email templates, see
        `Using Custom Verification Email
        Templates <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-verify-address-custom.html>`__
        in the *Amazon SES Developer Guide*.

        You can execute this operation no more than once per second.

        :param template_name: The name of the custom verification email template that you want to
        retrieve.
        :returns: GetCustomVerificationEmailTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDedicatedIp")
    def get_dedicated_ip(self, context: RequestContext, ip: Ip) -> GetDedicatedIpResponse:
        """Get information about a dedicated IP address, including the name of the
        dedicated IP pool that it's associated with, as well information about
        the automatic warm-up process for the address.

        :param ip: The IP address that you want to obtain more information about.
        :returns: GetDedicatedIpResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDedicatedIps")
    def get_dedicated_ips(
        self,
        context: RequestContext,
        pool_name: PoolName = None,
        next_token: NextToken = None,
        page_size: MaxItems = None,
    ) -> GetDedicatedIpsResponse:
        """List the dedicated IP addresses that are associated with your Amazon Web
        Services account.

        :param pool_name: The name of the IP pool that the dedicated IP address is associated
        with.
        :param next_token: A token returned from a previous call to ``GetDedicatedIps`` to indicate
        the position of the dedicated IP pool in the list of IP pools.
        :param page_size: The number of results to show in a single call to
        ``GetDedicatedIpsRequest``.
        :returns: GetDedicatedIpsResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDeliverabilityDashboardOptions")
    def get_deliverability_dashboard_options(
        self,
        context: RequestContext,
    ) -> GetDeliverabilityDashboardOptionsResponse:
        """Retrieve information about the status of the Deliverability dashboard
        for your account. When the Deliverability dashboard is enabled, you gain
        access to reputation, deliverability, and other metrics for the domains
        that you use to send email. You also gain the ability to perform
        predictive inbox placement tests.

        When you use the Deliverability dashboard, you pay a monthly
        subscription charge, in addition to any other fees that you accrue by
        using Amazon SES and other Amazon Web Services services. For more
        information about the features and cost of a Deliverability dashboard
        subscription, see `Amazon SES
        Pricing <http://aws.amazon.com/ses/pricing/>`__.

        :returns: GetDeliverabilityDashboardOptionsResponse
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDeliverabilityTestReport")
    def get_deliverability_test_report(
        self, context: RequestContext, report_id: ReportId
    ) -> GetDeliverabilityTestReportResponse:
        """Retrieve the results of a predictive inbox placement test.

        :param report_id: A unique string that identifies the predictive inbox placement test.
        :returns: GetDeliverabilityTestReportResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetDomainDeliverabilityCampaign")
    def get_domain_deliverability_campaign(
        self, context: RequestContext, campaign_id: CampaignId
    ) -> GetDomainDeliverabilityCampaignResponse:
        """Retrieve all the deliverability data for a specific campaign. This data
        is available for a campaign only if the campaign sent email by using a
        domain that the Deliverability dashboard is enabled for.

        :param campaign_id: The unique identifier for the campaign.
        :returns: GetDomainDeliverabilityCampaignResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("GetDomainStatisticsReport")
    def get_domain_statistics_report(
        self, context: RequestContext, domain: Identity, start_date: Timestamp, end_date: Timestamp
    ) -> GetDomainStatisticsReportResponse:
        """Retrieve inbox placement and engagement rates for the domains that you
        use to send email.

        :param domain: The domain that you want to obtain deliverability metrics for.
        :param start_date: The first day (in Unix time) that you want to obtain domain
        deliverability metrics for.
        :param end_date: The last day (in Unix time) that you want to obtain domain
        deliverability metrics for.
        :returns: GetDomainStatisticsReportResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetEmailIdentity")
    def get_email_identity(
        self, context: RequestContext, email_identity: Identity
    ) -> GetEmailIdentityResponse:
        """Provides information about a specific identity, including the identity's
        verification status, sending authorization policies, its DKIM
        authentication status, and its custom Mail-From settings.

        :param email_identity: The email identity.
        :returns: GetEmailIdentityResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetEmailIdentityPolicies")
    def get_email_identity_policies(
        self, context: RequestContext, email_identity: Identity
    ) -> GetEmailIdentityPoliciesResponse:
        """Returns the requested sending authorization policies for the given
        identity (an email address or a domain). The policies are returned as a
        map of policy names to policy contents. You can retrieve a maximum of 20
        policies at a time.

        This API is for the identity owner only. If you have not verified the
        identity, this API will return an error.

        Sending authorization is a feature that enables an identity owner to
        authorize other senders to use its identities. For information about
        using sending authorization, see the `Amazon SES Developer
        Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization.html>`__.

        You can execute this operation no more than once per second.

        :param email_identity: The email identity.
        :returns: GetEmailIdentityPoliciesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetEmailTemplate")
    def get_email_template(
        self, context: RequestContext, template_name: EmailTemplateName
    ) -> GetEmailTemplateResponse:
        """Displays the template object (which includes the subject line, HTML part
        and text part) for the template you specify.

        You can execute this operation no more than once per second.

        :param template_name: The name of the template.
        :returns: GetEmailTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("GetImportJob")
    def get_import_job(self, context: RequestContext, job_id: JobId) -> GetImportJobResponse:
        """Provides information about an import job.

        :param job_id: The ID of the import job.
        :returns: GetImportJobResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("GetSuppressedDestination")
    def get_suppressed_destination(
        self, context: RequestContext, email_address: EmailAddress
    ) -> GetSuppressedDestinationResponse:
        """Retrieves information about a specific email address that's on the
        suppression list for your account.

        :param email_address: The email address that's on the account suppression list.
        :returns: GetSuppressedDestinationResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("ListConfigurationSets")
    def list_configuration_sets(
        self, context: RequestContext, next_token: NextToken = None, page_size: MaxItems = None
    ) -> ListConfigurationSetsResponse:
        """List all of the configuration sets associated with your account in the
        current region.

        *Configuration sets* are groups of rules that you can apply to the
        emails you send. You apply a configuration set to an email by including
        a reference to the configuration set in the headers of the email. When
        you apply a configuration set to an email, all of the rules in that
        configuration set are applied to the email.

        :param next_token: A token returned from a previous call to ``ListConfigurationSets`` to
        indicate the position in the list of configuration sets.
        :param page_size: The number of results to show in a single call to
        ``ListConfigurationSets``.
        :returns: ListConfigurationSetsResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListContactLists")
    def list_contact_lists(
        self, context: RequestContext, page_size: MaxItems = None, next_token: NextToken = None
    ) -> ListContactListsResponse:
        """Lists all of the contact lists available.

        :param page_size: Maximum number of contact lists to return at once.
        :param next_token: A string token indicating that there might be additional contact lists
        available to be listed.
        :returns: ListContactListsResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("ListContacts")
    def list_contacts(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        filter: ListContactsFilter = None,
        page_size: MaxItems = None,
        next_token: NextToken = None,
    ) -> ListContactsResponse:
        """Lists the contacts present in a specific contact list.

        :param contact_list_name: The name of the contact list.
        :param filter: A filter that can be applied to a list of contacts.
        :param page_size: The number of contacts that may be returned at once, which is dependent
        on if there are more or less contacts than the value of the PageSize.
        :param next_token: A string token indicating that there might be additional contacts
        available to be listed.
        :returns: ListContactsResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("ListCustomVerificationEmailTemplates")
    def list_custom_verification_email_templates(
        self, context: RequestContext, next_token: NextToken = None, page_size: MaxItems = None
    ) -> ListCustomVerificationEmailTemplatesResponse:
        """Lists the existing custom verification email templates for your account
        in the current Amazon Web Services Region.

        For more information about custom verification email templates, see
        `Using Custom Verification Email
        Templates <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-verify-address-custom.html>`__
        in the *Amazon SES Developer Guide*.

        You can execute this operation no more than once per second.

        :param next_token: A token returned from a previous call to
        ``ListCustomVerificationEmailTemplates`` to indicate the position in the
        list of custom verification email templates.
        :param page_size: The number of results to show in a single call to
        ``ListCustomVerificationEmailTemplates``.
        :returns: ListCustomVerificationEmailTemplatesResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListDedicatedIpPools")
    def list_dedicated_ip_pools(
        self, context: RequestContext, next_token: NextToken = None, page_size: MaxItems = None
    ) -> ListDedicatedIpPoolsResponse:
        """List all of the dedicated IP pools that exist in your Amazon Web
        Services account in the current Region.

        :param next_token: A token returned from a previous call to ``ListDedicatedIpPools`` to
        indicate the position in the list of dedicated IP pools.
        :param page_size: The number of results to show in a single call to
        ``ListDedicatedIpPools``.
        :returns: ListDedicatedIpPoolsResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListDeliverabilityTestReports")
    def list_deliverability_test_reports(
        self, context: RequestContext, next_token: NextToken = None, page_size: MaxItems = None
    ) -> ListDeliverabilityTestReportsResponse:
        """Show a list of the predictive inbox placement tests that you've
        performed, regardless of their statuses. For predictive inbox placement
        tests that are complete, you can use the ``GetDeliverabilityTestReport``
        operation to view the results.

        :param next_token: A token returned from a previous call to
        ``ListDeliverabilityTestReports`` to indicate the position in the list
        of predictive inbox placement tests.
        :param page_size: The number of results to show in a single call to
        ``ListDeliverabilityTestReports``.
        :returns: ListDeliverabilityTestReportsResponse
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListDomainDeliverabilityCampaigns")
    def list_domain_deliverability_campaigns(
        self,
        context: RequestContext,
        start_date: Timestamp,
        end_date: Timestamp,
        subscribed_domain: Domain,
        next_token: NextToken = None,
        page_size: MaxItems = None,
    ) -> ListDomainDeliverabilityCampaignsResponse:
        """Retrieve deliverability data for all the campaigns that used a specific
        domain to send email during a specified time range. This data is
        available for a domain only if you enabled the Deliverability dashboard
        for the domain.

        :param start_date: The first day, in Unix time format, that you want to obtain
        deliverability data for.
        :param end_date: The last day, in Unix time format, that you want to obtain
        deliverability data for.
        :param subscribed_domain: The domain to obtain deliverability data for.
        :param next_token: A token that’s returned from a previous call to the
        ``ListDomainDeliverabilityCampaigns`` operation.
        :param page_size: The maximum number of results to include in response to a single call to
        the ``ListDomainDeliverabilityCampaigns`` operation.
        :returns: ListDomainDeliverabilityCampaignsResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("ListEmailIdentities")
    def list_email_identities(
        self, context: RequestContext, next_token: NextToken = None, page_size: MaxItems = None
    ) -> ListEmailIdentitiesResponse:
        """Returns a list of all of the email identities that are associated with
        your Amazon Web Services account. An identity can be either an email
        address or a domain. This operation returns identities that are verified
        as well as those that aren't. This operation returns identities that are
        associated with Amazon SES and Amazon Pinpoint.

        :param next_token: A token returned from a previous call to ``ListEmailIdentities`` to
        indicate the position in the list of identities.
        :param page_size: The number of results to show in a single call to
        ``ListEmailIdentities``.
        :returns: ListEmailIdentitiesResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListEmailTemplates")
    def list_email_templates(
        self, context: RequestContext, next_token: NextToken = None, page_size: MaxItems = None
    ) -> ListEmailTemplatesResponse:
        """Lists the email templates present in your Amazon SES account in the
        current Amazon Web Services Region.

        You can execute this operation no more than once per second.

        :param next_token: A token returned from a previous call to ``ListEmailTemplates`` to
        indicate the position in the list of email templates.
        :param page_size: The number of results to show in a single call to
        ``ListEmailTemplates``.
        :returns: ListEmailTemplatesResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListImportJobs")
    def list_import_jobs(
        self,
        context: RequestContext,
        import_destination_type: ImportDestinationType = None,
        next_token: NextToken = None,
        page_size: MaxItems = None,
    ) -> ListImportJobsResponse:
        """Lists all of the import jobs.

        :param import_destination_type: The destination of the import job, which can be used to list import jobs
        that have a certain ``ImportDestinationType``.
        :param next_token: A string token indicating that there might be additional import jobs
        available to be listed.
        :param page_size: Maximum number of import jobs to return at once.
        :returns: ListImportJobsResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("ListSuppressedDestinations")
    def list_suppressed_destinations(
        self,
        context: RequestContext,
        reasons: SuppressionListReasons = None,
        start_date: Timestamp = None,
        end_date: Timestamp = None,
        next_token: NextToken = None,
        page_size: MaxItems = None,
    ) -> ListSuppressedDestinationsResponse:
        """Retrieves a list of email addresses that are on the suppression list for
        your account.

        :param reasons: The factors that caused the email address to be added to .
        :param start_date: Used to filter the list of suppressed email destinations so that it only
        includes addresses that were added to the list after a specific date.
        :param end_date: Used to filter the list of suppressed email destinations so that it only
        includes addresses that were added to the list before a specific date.
        :param next_token: A token returned from a previous call to ``ListSuppressedDestinations``
        to indicate the position in the list of suppressed email addresses.
        :param page_size: The number of results to show in a single call to
        ``ListSuppressedDestinations``.
        :returns: ListSuppressedDestinationsResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName
    ) -> ListTagsForResourceResponse:
        """Retrieve a list of the tags (keys and values) that are associated with a
        specified resource. A  *tag* is a label that you optionally define and
        associate with a resource. Each tag consists of a required  *tag
        key* and an optional associated  *tag value*. A tag key is a general
        label that acts as a category for more specific tag values. A tag value
        acts as a descriptor within a tag key.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to retrieve
        tag information for.
        :returns: ListTagsForResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("PutAccountDedicatedIpWarmupAttributes")
    def put_account_dedicated_ip_warmup_attributes(
        self, context: RequestContext, auto_warmup_enabled: Enabled = None
    ) -> PutAccountDedicatedIpWarmupAttributesResponse:
        """Enable or disable the automatic warm-up feature for dedicated IP
        addresses.

        :param auto_warmup_enabled: Enables or disables the automatic warm-up feature for dedicated IP
        addresses that are associated with your Amazon SES account in the
        current Amazon Web Services Region.
        :returns: PutAccountDedicatedIpWarmupAttributesResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutAccountDetails")
    def put_account_details(
        self,
        context: RequestContext,
        mail_type: MailType,
        website_url: WebsiteURL,
        use_case_description: UseCaseDescription,
        contact_language: ContactLanguage = None,
        additional_contact_email_addresses: AdditionalContactEmailAddresses = None,
        production_access_enabled: EnabledWrapper = None,
    ) -> PutAccountDetailsResponse:
        """Update your Amazon SES account details.

        :param mail_type: The type of email your account will send.
        :param website_url: The URL of your website.
        :param use_case_description: A description of the types of email that you plan to send.
        :param contact_language: The language you would prefer to be contacted with.
        :param additional_contact_email_addresses: Additional email addresses that you would like to be notified regarding
        Amazon SES matters.
        :param production_access_enabled: Indicates whether or not your account should have production access in
        the current Amazon Web Services Region.
        :returns: PutAccountDetailsResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("PutAccountSendingAttributes")
    def put_account_sending_attributes(
        self, context: RequestContext, sending_enabled: Enabled = None
    ) -> PutAccountSendingAttributesResponse:
        """Enable or disable the ability of your account to send email.

        :param sending_enabled: Enables or disables your account's ability to send email.
        :returns: PutAccountSendingAttributesResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutAccountSuppressionAttributes")
    def put_account_suppression_attributes(
        self, context: RequestContext, suppressed_reasons: SuppressionListReasons = None
    ) -> PutAccountSuppressionAttributesResponse:
        """Change the settings for the account-level suppression list.

        :param suppressed_reasons: A list that contains the reasons that email addresses will be
        automatically added to the suppression list for your account.
        :returns: PutAccountSuppressionAttributesResponse
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutConfigurationSetDeliveryOptions")
    def put_configuration_set_delivery_options(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        tls_policy: TlsPolicy = None,
        sending_pool_name: SendingPoolName = None,
    ) -> PutConfigurationSetDeliveryOptionsResponse:
        """Associate a configuration set with a dedicated IP pool. You can use
        dedicated IP pools to create groups of dedicated IP addresses for
        sending specific types of email.

        :param configuration_set_name: The name of the configuration set to associate with a dedicated IP pool.
        :param tls_policy: Specifies whether messages that use the configuration set are required
        to use Transport Layer Security (TLS).
        :param sending_pool_name: The name of the dedicated IP pool to associate with the configuration
        set.
        :returns: PutConfigurationSetDeliveryOptionsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutConfigurationSetReputationOptions")
    def put_configuration_set_reputation_options(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        reputation_metrics_enabled: Enabled = None,
    ) -> PutConfigurationSetReputationOptionsResponse:
        """Enable or disable collection of reputation metrics for emails that you
        send using a particular configuration set in a specific Amazon Web
        Services Region.

        :param configuration_set_name: The name of the configuration set.
        :param reputation_metrics_enabled: If ``true``, tracking of reputation metrics is enabled for the
        configuration set.
        :returns: PutConfigurationSetReputationOptionsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutConfigurationSetSendingOptions")
    def put_configuration_set_sending_options(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        sending_enabled: Enabled = None,
    ) -> PutConfigurationSetSendingOptionsResponse:
        """Enable or disable email sending for messages that use a particular
        configuration set in a specific Amazon Web Services Region.

        :param configuration_set_name: The name of the configuration set to enable or disable email sending
        for.
        :param sending_enabled: If ``true``, email sending is enabled for the configuration set.
        :returns: PutConfigurationSetSendingOptionsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutConfigurationSetSuppressionOptions")
    def put_configuration_set_suppression_options(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        suppressed_reasons: SuppressionListReasons = None,
    ) -> PutConfigurationSetSuppressionOptionsResponse:
        """Specify the account suppression list preferences for a configuration
        set.

        :param configuration_set_name: The name of the configuration set to change the suppression list
        preferences for.
        :param suppressed_reasons: A list that contains the reasons that email addresses are automatically
        added to the suppression list for your account.
        :returns: PutConfigurationSetSuppressionOptionsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutConfigurationSetTrackingOptions")
    def put_configuration_set_tracking_options(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        custom_redirect_domain: CustomRedirectDomain = None,
    ) -> PutConfigurationSetTrackingOptionsResponse:
        """Specify a custom domain to use for open and click tracking elements in
        email that you send.

        :param configuration_set_name: The name of the configuration set.
        :param custom_redirect_domain: The domain to use to track open and click events.
        :returns: PutConfigurationSetTrackingOptionsResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutDedicatedIpInPool")
    def put_dedicated_ip_in_pool(
        self, context: RequestContext, ip: Ip, destination_pool_name: PoolName
    ) -> PutDedicatedIpInPoolResponse:
        """Move a dedicated IP address to an existing dedicated IP pool.

        The dedicated IP address that you specify must already exist, and must
        be associated with your Amazon Web Services account.

        The dedicated IP pool you specify must already exist. You can create a
        new pool by using the ``CreateDedicatedIpPool`` operation.

        :param ip: The IP address that you want to move to the dedicated IP pool.
        :param destination_pool_name: The name of the IP pool that you want to add the dedicated IP address
        to.
        :returns: PutDedicatedIpInPoolResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutDedicatedIpWarmupAttributes")
    def put_dedicated_ip_warmup_attributes(
        self, context: RequestContext, ip: Ip, warmup_percentage: Percentage100Wrapper
    ) -> PutDedicatedIpWarmupAttributesResponse:
        """

        :param ip: The dedicated IP address that you want to update the warm-up attributes
        for.
        :param warmup_percentage: The warm-up percentage that you want to associate with the dedicated IP
        address.
        :returns: PutDedicatedIpWarmupAttributesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutDeliverabilityDashboardOption")
    def put_deliverability_dashboard_option(
        self,
        context: RequestContext,
        dashboard_enabled: Enabled,
        subscribed_domains: DomainDeliverabilityTrackingOptions = None,
    ) -> PutDeliverabilityDashboardOptionResponse:
        """Enable or disable the Deliverability dashboard. When you enable the
        Deliverability dashboard, you gain access to reputation, deliverability,
        and other metrics for the domains that you use to send email. You also
        gain the ability to perform predictive inbox placement tests.

        When you use the Deliverability dashboard, you pay a monthly
        subscription charge, in addition to any other fees that you accrue by
        using Amazon SES and other Amazon Web Services services. For more
        information about the features and cost of a Deliverability dashboard
        subscription, see `Amazon SES
        Pricing <http://aws.amazon.com/ses/pricing/>`__.

        :param dashboard_enabled: Specifies whether to enable the Deliverability dashboard.
        :param subscribed_domains: An array of objects, one for each verified domain that you use to send
        email and enabled the Deliverability dashboard for.
        :returns: PutDeliverabilityDashboardOptionResponse
        :raises AlreadyExistsException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutEmailIdentityConfigurationSetAttributes")
    def put_email_identity_configuration_set_attributes(
        self,
        context: RequestContext,
        email_identity: Identity,
        configuration_set_name: ConfigurationSetName = None,
    ) -> PutEmailIdentityConfigurationSetAttributesResponse:
        """Used to associate a configuration set with an email identity.

        :param email_identity: The email address or domain to associate with a configuration set.
        :param configuration_set_name: The configuration set to associate with an email identity.
        :returns: PutEmailIdentityConfigurationSetAttributesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutEmailIdentityDkimAttributes")
    def put_email_identity_dkim_attributes(
        self, context: RequestContext, email_identity: Identity, signing_enabled: Enabled = None
    ) -> PutEmailIdentityDkimAttributesResponse:
        """Used to enable or disable DKIM authentication for an email identity.

        :param email_identity: The email identity.
        :param signing_enabled: Sets the DKIM signing configuration for the identity.
        :returns: PutEmailIdentityDkimAttributesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutEmailIdentityDkimSigningAttributes")
    def put_email_identity_dkim_signing_attributes(
        self,
        context: RequestContext,
        email_identity: Identity,
        signing_attributes_origin: DkimSigningAttributesOrigin,
        signing_attributes: DkimSigningAttributes = None,
    ) -> PutEmailIdentityDkimSigningAttributesResponse:
        """Used to configure or change the DKIM authentication settings for an
        email domain identity. You can use this operation to do any of the
        following:

        -  Update the signing attributes for an identity that uses Bring Your
           Own DKIM (BYODKIM).

        -  Update the key length that should be used for Easy DKIM.

        -  Change from using no DKIM authentication to using Easy DKIM.

        -  Change from using no DKIM authentication to using BYODKIM.

        -  Change from using Easy DKIM to using BYODKIM.

        -  Change from using BYODKIM to using Easy DKIM.

        :param email_identity: The email identity.
        :param signing_attributes_origin: The method to use to configure DKIM for the identity.
        :param signing_attributes: An object that contains information about the private key and selector
        that you want to use to configure DKIM for the identity for Bring Your
        Own DKIM (BYODKIM) for the identity, or, configures the key length to be
        used for `Easy
        DKIM <https://docs.
        :returns: PutEmailIdentityDkimSigningAttributesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutEmailIdentityFeedbackAttributes")
    def put_email_identity_feedback_attributes(
        self,
        context: RequestContext,
        email_identity: Identity,
        email_forwarding_enabled: Enabled = None,
    ) -> PutEmailIdentityFeedbackAttributesResponse:
        """Used to enable or disable feedback forwarding for an identity. This
        setting determines what happens when an identity is used to send an
        email that results in a bounce or complaint event.

        If the value is ``true``, you receive email notifications when bounce or
        complaint events occur. These notifications are sent to the address that
        you specified in the ``Return-Path`` header of the original email.

        You're required to have a method of tracking bounces and complaints. If
        you haven't set up another mechanism for receiving bounce or complaint
        notifications (for example, by setting up an event destination), you
        receive an email notification when these events occur (even if this
        setting is disabled).

        :param email_identity: The email identity.
        :param email_forwarding_enabled: Sets the feedback forwarding configuration for the identity.
        :returns: PutEmailIdentityFeedbackAttributesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutEmailIdentityMailFromAttributes")
    def put_email_identity_mail_from_attributes(
        self,
        context: RequestContext,
        email_identity: Identity,
        mail_from_domain: MailFromDomainName = None,
        behavior_on_mx_failure: BehaviorOnMxFailure = None,
    ) -> PutEmailIdentityMailFromAttributesResponse:
        """Used to enable or disable the custom Mail-From domain configuration for
        an email identity.

        :param email_identity: The verified email identity.
        :param mail_from_domain: The custom MAIL FROM domain that you want the verified identity to use.
        :param behavior_on_mx_failure: The action to take if the required MX record isn't found when you send
        an email.
        :returns: PutEmailIdentityMailFromAttributesResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("PutSuppressedDestination")
    def put_suppressed_destination(
        self, context: RequestContext, email_address: EmailAddress, reason: SuppressionListReason
    ) -> PutSuppressedDestinationResponse:
        """Adds an email address to the suppression list for your account.

        :param email_address: The email address that should be added to the suppression list for your
        account.
        :param reason: The factors that should cause the email address to be added to the
        suppression list for your account.
        :returns: PutSuppressedDestinationResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("SendBulkEmail")
    def send_bulk_email(
        self,
        context: RequestContext,
        default_content: BulkEmailContent,
        bulk_email_entries: BulkEmailEntryList,
        from_email_address: EmailAddress = None,
        from_email_address_identity_arn: AmazonResourceName = None,
        reply_to_addresses: EmailAddressList = None,
        feedback_forwarding_email_address: EmailAddress = None,
        feedback_forwarding_email_address_identity_arn: AmazonResourceName = None,
        default_email_tags: MessageTagList = None,
        configuration_set_name: ConfigurationSetName = None,
    ) -> SendBulkEmailResponse:
        """Composes an email message to multiple destinations.

        :param default_content: An object that contains the body of the message.
        :param bulk_email_entries: The list of bulk email entry objects.
        :param from_email_address: The email address to use as the "From" address for the email.
        :param from_email_address_identity_arn: This parameter is used only for sending authorization.
        :param reply_to_addresses: The "Reply-to" email addresses for the message.
        :param feedback_forwarding_email_address: The address that you want bounce and complaint notifications to be sent
        to.
        :param feedback_forwarding_email_address_identity_arn: This parameter is used only for sending authorization.
        :param default_email_tags: A list of tags, in the form of name/value pairs, to apply to an email
        that you send using the ``SendEmail`` operation.
        :param configuration_set_name: The name of the configuration set to use when sending the email.
        :returns: SendBulkEmailResponse
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises AccountSuspendedException:
        :raises SendingPausedException:
        :raises MessageRejected:
        :raises MailFromDomainNotVerifiedException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("SendCustomVerificationEmail")
    def send_custom_verification_email(
        self,
        context: RequestContext,
        email_address: EmailAddress,
        template_name: EmailTemplateName,
        configuration_set_name: ConfigurationSetName = None,
    ) -> SendCustomVerificationEmailResponse:
        """Adds an email address to the list of identities for your Amazon SES
        account in the current Amazon Web Services Region and attempts to verify
        it. As a result of executing this operation, a customized verification
        email is sent to the specified address.

        To use this operation, you must first create a custom verification email
        template. For more information about creating and using custom
        verification email templates, see `Using Custom Verification Email
        Templates <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-verify-address-custom.html>`__
        in the *Amazon SES Developer Guide*.

        You can execute this operation no more than once per second.

        :param email_address: The email address to verify.
        :param template_name: The name of the custom verification email template to use when sending
        the verification email.
        :param configuration_set_name: Name of a configuration set to use when sending the verification email.
        :returns: SendCustomVerificationEmailResponse
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises MessageRejected:
        :raises SendingPausedException:
        :raises MailFromDomainNotVerifiedException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("SendEmail")
    def send_email(
        self,
        context: RequestContext,
        content: EmailContent,
        from_email_address: EmailAddress = None,
        from_email_address_identity_arn: AmazonResourceName = None,
        destination: Destination = None,
        reply_to_addresses: EmailAddressList = None,
        feedback_forwarding_email_address: EmailAddress = None,
        feedback_forwarding_email_address_identity_arn: AmazonResourceName = None,
        email_tags: MessageTagList = None,
        configuration_set_name: ConfigurationSetName = None,
        list_management_options: ListManagementOptions = None,
    ) -> SendEmailResponse:
        """Sends an email message. You can use the Amazon SES API v2 to send the
        following types of messages:

        -  **Simple** – A standard email message. When you create this type of
           message, you specify the sender, the recipient, and the message body,
           and Amazon SES assembles the message for you.

        -  **Raw** – A raw, MIME-formatted email message. When you send this
           type of email, you have to specify all of the message headers, as
           well as the message body. You can use this message type to send
           messages that contain attachments. The message that you specify has
           to be a valid MIME message.

        -  **Templated** – A message that contains personalization tags. When
           you send this type of email, Amazon SES API v2 automatically replaces
           the tags with values that you specify.

        :param content: An object that contains the body of the message.
        :param from_email_address: The email address to use as the "From" address for the email.
        :param from_email_address_identity_arn: This parameter is used only for sending authorization.
        :param destination: An object that contains the recipients of the email message.
        :param reply_to_addresses: The "Reply-to" email addresses for the message.
        :param feedback_forwarding_email_address: The address that you want bounce and complaint notifications to be sent
        to.
        :param feedback_forwarding_email_address_identity_arn: This parameter is used only for sending authorization.
        :param email_tags: A list of tags, in the form of name/value pairs, to apply to an email
        that you send using the ``SendEmail`` operation.
        :param configuration_set_name: The name of the configuration set to use when sending the email.
        :param list_management_options: An object used to specify a list or topic to which an email belongs,
        which will be used when a contact chooses to unsubscribe.
        :returns: SendEmailResponse
        :raises TooManyRequestsException:
        :raises LimitExceededException:
        :raises AccountSuspendedException:
        :raises SendingPausedException:
        :raises MessageRejected:
        :raises MailFromDomainNotVerifiedException:
        :raises NotFoundException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceResponse:
        """Add one or more tags (keys and values) to a specified resource. A
        *tag* is a label that you optionally define and associate with a
        resource. Tags can help you categorize and manage resources in different
        ways, such as by purpose, owner, environment, or other criteria. A
        resource can have as many as 50 tags.

        Each tag consists of a required  *tag key* and an associated  *tag
        value*, both of which you define. A tag key is a general label that acts
        as a category for more specific tag values. A tag value acts as a
        descriptor within a tag key.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to add one
        or more tags to.
        :param tags: A list of the tags that you want to add to the resource.
        :returns: TagResourceResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("TestRenderEmailTemplate")
    def test_render_email_template(
        self,
        context: RequestContext,
        template_name: EmailTemplateName,
        template_data: EmailTemplateData,
    ) -> TestRenderEmailTemplateResponse:
        """Creates a preview of the MIME content of an email when provided with a
        template and a set of replacement data.

        You can execute this operation no more than once per second.

        :param template_name: The name of the template.
        :param template_data: A list of replacement values to apply to the template.
        :returns: TestRenderEmailTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Remove one or more tags (keys and values) from a specified resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to remove
        one or more tags from.
        :param tag_keys: The tags (tag keys) that you want to remove from the resource.
        :returns: UntagResourceResponse
        :raises BadRequestException:
        :raises ConcurrentModificationException:
        :raises NotFoundException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("UpdateConfigurationSetEventDestination")
    def update_configuration_set_event_destination(
        self,
        context: RequestContext,
        configuration_set_name: ConfigurationSetName,
        event_destination_name: EventDestinationName,
        event_destination: EventDestinationDefinition,
    ) -> UpdateConfigurationSetEventDestinationResponse:
        """Update the configuration of an event destination for a configuration
        set.

        *Events* include message sends, deliveries, opens, clicks, bounces, and
        complaints. *Event destinations* are places that you can send
        information about these events to. For example, you can send event data
        to Amazon SNS to receive notifications when you receive bounces or
        complaints, or you can use Amazon Kinesis Data Firehose to stream data
        to Amazon S3 for long-term storage.

        :param configuration_set_name: The name of the configuration set that contains the event destination to
        modify.
        :param event_destination_name: The name of the event destination.
        :param event_destination: An object that defines the event destination.
        :returns: UpdateConfigurationSetEventDestinationResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("UpdateContact")
    def update_contact(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        email_address: EmailAddress,
        topic_preferences: TopicPreferenceList = None,
        unsubscribe_all: UnsubscribeAll = None,
        attributes_data: AttributesData = None,
    ) -> UpdateContactResponse:
        """Updates a contact's preferences for a list. It is not necessary to
        specify all existing topic preferences in the TopicPreferences object,
        just the ones that need updating.

        :param contact_list_name: The name of the contact list.
        :param email_address: The contact's email addres.
        :param topic_preferences: The contact's preference for being opted-in to or opted-out of a topic.
        :param unsubscribe_all: A boolean value status noting if the contact is unsubscribed from all
        contact list topics.
        :param attributes_data: The attribute data attached to a contact.
        :returns: UpdateContactResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("UpdateContactList")
    def update_contact_list(
        self,
        context: RequestContext,
        contact_list_name: ContactListName,
        topics: Topics = None,
        description: Description = None,
    ) -> UpdateContactListResponse:
        """Updates contact list metadata. This operation does a complete
        replacement.

        :param contact_list_name: The name of the contact list.
        :param topics: An interest group, theme, or label within a list.
        :param description: A description of what the contact list is about.
        :returns: UpdateContactListResponse
        :raises BadRequestException:
        :raises TooManyRequestsException:
        :raises NotFoundException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("UpdateCustomVerificationEmailTemplate")
    def update_custom_verification_email_template(
        self,
        context: RequestContext,
        template_name: EmailTemplateName,
        from_email_address: EmailAddress,
        template_subject: EmailTemplateSubject,
        template_content: TemplateContent,
        success_redirection_url: SuccessRedirectionURL,
        failure_redirection_url: FailureRedirectionURL,
    ) -> UpdateCustomVerificationEmailTemplateResponse:
        """Updates an existing custom verification email template.

        For more information about custom verification email templates, see
        `Using Custom Verification Email
        Templates <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-verify-address-custom.html>`__
        in the *Amazon SES Developer Guide*.

        You can execute this operation no more than once per second.

        :param template_name: The name of the custom verification email template that you want to
        update.
        :param from_email_address: The email address that the custom verification email is sent from.
        :param template_subject: The subject line of the custom verification email.
        :param template_content: The content of the custom verification email.
        :param success_redirection_url: The URL that the recipient of the verification email is sent to if his
        or her address is successfully verified.
        :param failure_redirection_url: The URL that the recipient of the verification email is sent to if his
        or her address is not successfully verified.
        :returns: UpdateCustomVerificationEmailTemplateResponse
        :raises NotFoundException:
        :raises BadRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("UpdateEmailIdentityPolicy")
    def update_email_identity_policy(
        self,
        context: RequestContext,
        email_identity: Identity,
        policy_name: PolicyName,
        policy: Policy,
    ) -> UpdateEmailIdentityPolicyResponse:
        """Updates the specified sending authorization policy for the given
        identity (an email address or a domain). This API returns successfully
        even if a policy with the specified name does not exist.

        This API is for the identity owner only. If you have not verified the
        identity, this API will return an error.

        Sending authorization is a feature that enables an identity owner to
        authorize other senders to use its identities. For information about
        using sending authorization, see the `Amazon SES Developer
        Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization.html>`__.

        You can execute this operation no more than once per second.

        :param email_identity: The email identity.
        :param policy_name: The name of the policy.
        :param policy: The text of the policy in JSON format.
        :returns: UpdateEmailIdentityPolicyResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError

    @handler("UpdateEmailTemplate")
    def update_email_template(
        self,
        context: RequestContext,
        template_name: EmailTemplateName,
        template_content: EmailTemplateContent,
    ) -> UpdateEmailTemplateResponse:
        """Updates an email template. Email templates enable you to send
        personalized email to one or more destinations in a single API
        operation. For more information, see the `Amazon SES Developer
        Guide <https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html>`__.

        You can execute this operation no more than once per second.

        :param template_name: The name of the template.
        :param template_content: The content of the email template, composed of a subject line, an HTML
        part, and a text-only part.
        :returns: UpdateEmailTemplateResponse
        :raises NotFoundException:
        :raises TooManyRequestsException:
        :raises BadRequestException:
        """
        raise NotImplementedError
