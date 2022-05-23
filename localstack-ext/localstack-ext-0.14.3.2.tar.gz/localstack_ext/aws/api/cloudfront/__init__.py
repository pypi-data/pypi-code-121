import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

CommentType = str
FunctionARN = str
FunctionName = str
LambdaFunctionARN = str
OriginShieldRegion = str
ResourceARN = str
SamplingRate = float
TagKey = str
TagValue = str
aliasString = str
boolean = bool
distributionIdString = str
integer = int
listConflictingAliasesMaxItemsInteger = int
sensitiveStringType = str
string = str


class CachePolicyCookieBehavior(str):
    none = "none"
    whitelist = "whitelist"
    allExcept = "allExcept"
    all = "all"


class CachePolicyHeaderBehavior(str):
    none = "none"
    whitelist = "whitelist"


class CachePolicyQueryStringBehavior(str):
    none = "none"
    whitelist = "whitelist"
    allExcept = "allExcept"
    all = "all"


class CachePolicyType(str):
    managed = "managed"
    custom = "custom"


class CertificateSource(str):
    cloudfront = "cloudfront"
    iam = "iam"
    acm = "acm"


class EventType(str):
    viewer_request = "viewer-request"
    viewer_response = "viewer-response"
    origin_request = "origin-request"
    origin_response = "origin-response"


class Format(str):
    URLEncoded = "URLEncoded"


class FrameOptionsList(str):
    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"


class FunctionRuntime(str):
    cloudfront_js_1_0 = "cloudfront-js-1.0"


class FunctionStage(str):
    DEVELOPMENT = "DEVELOPMENT"
    LIVE = "LIVE"


class GeoRestrictionType(str):
    blacklist = "blacklist"
    whitelist = "whitelist"
    none = "none"


class HttpVersion(str):
    http1_1 = "http1.1"
    http2 = "http2"


class ICPRecordalStatus(str):
    APPROVED = "APPROVED"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


class ItemSelection(str):
    none = "none"
    whitelist = "whitelist"
    all = "all"


class Method(str):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    DELETE = "DELETE"


class MinimumProtocolVersion(str):
    SSLv3 = "SSLv3"
    TLSv1 = "TLSv1"
    TLSv1_2016 = "TLSv1_2016"
    TLSv1_1_2016 = "TLSv1.1_2016"
    TLSv1_2_2018 = "TLSv1.2_2018"
    TLSv1_2_2019 = "TLSv1.2_2019"
    TLSv1_2_2021 = "TLSv1.2_2021"


class OriginProtocolPolicy(str):
    http_only = "http-only"
    match_viewer = "match-viewer"
    https_only = "https-only"


class OriginRequestPolicyCookieBehavior(str):
    none = "none"
    whitelist = "whitelist"
    all = "all"


class OriginRequestPolicyHeaderBehavior(str):
    none = "none"
    whitelist = "whitelist"
    allViewer = "allViewer"
    allViewerAndWhitelistCloudFront = "allViewerAndWhitelistCloudFront"


class OriginRequestPolicyQueryStringBehavior(str):
    none = "none"
    whitelist = "whitelist"
    all = "all"


class OriginRequestPolicyType(str):
    managed = "managed"
    custom = "custom"


class PriceClass(str):
    PriceClass_100 = "PriceClass_100"
    PriceClass_200 = "PriceClass_200"
    PriceClass_All = "PriceClass_All"


class RealtimeMetricsSubscriptionStatus(str):
    Enabled = "Enabled"
    Disabled = "Disabled"


class ReferrerPolicyList(str):
    no_referrer = "no-referrer"
    no_referrer_when_downgrade = "no-referrer-when-downgrade"
    origin = "origin"
    origin_when_cross_origin = "origin-when-cross-origin"
    same_origin = "same-origin"
    strict_origin = "strict-origin"
    strict_origin_when_cross_origin = "strict-origin-when-cross-origin"
    unsafe_url = "unsafe-url"


class ResponseHeadersPolicyAccessControlAllowMethodsValues(str):
    GET = "GET"
    POST = "POST"
    OPTIONS = "OPTIONS"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    ALL = "ALL"


class ResponseHeadersPolicyType(str):
    managed = "managed"
    custom = "custom"


class SSLSupportMethod(str):
    sni_only = "sni-only"
    vip = "vip"
    static_ip = "static-ip"


class SslProtocol(str):
    SSLv3 = "SSLv3"
    TLSv1 = "TLSv1"
    TLSv1_1 = "TLSv1.1"
    TLSv1_2 = "TLSv1.2"


class ViewerProtocolPolicy(str):
    allow_all = "allow-all"
    https_only = "https-only"
    redirect_to_https = "redirect-to-https"


class AccessDenied(ServiceException):
    """Access denied."""

    Message: Optional[string]


class BatchTooLarge(ServiceException):
    """Invalidation batch specified is too large."""

    Message: Optional[string]


class CNAMEAlreadyExists(ServiceException):
    """The CNAME specified is already defined for CloudFront."""

    Message: Optional[string]


class CachePolicyAlreadyExists(ServiceException):
    """A cache policy with this name already exists. You must provide a unique
    name. To modify an existing cache policy, use ``UpdateCachePolicy``.
    """

    Message: Optional[string]


class CachePolicyInUse(ServiceException):
    """Cannot delete the cache policy because it is attached to one or more
    cache behaviors.
    """

    Message: Optional[string]


class CannotChangeImmutablePublicKeyFields(ServiceException):
    """You can't change the value of a public key."""

    Message: Optional[string]


class CloudFrontOriginAccessIdentityAlreadyExists(ServiceException):
    """If the ``CallerReference`` is a value you already sent in a previous
    request to create an identity but the content of the
    ``CloudFrontOriginAccessIdentityConfig`` is different from the original
    request, CloudFront returns a
    ``CloudFrontOriginAccessIdentityAlreadyExists`` error.
    """

    Message: Optional[string]


class CloudFrontOriginAccessIdentityInUse(ServiceException):
    """The Origin Access Identity specified is already in use."""

    Message: Optional[string]


class DistributionAlreadyExists(ServiceException):
    """The caller reference you attempted to create the distribution with is
    associated with another distribution.
    """

    Message: Optional[string]


class DistributionNotDisabled(ServiceException):
    """The specified CloudFront distribution is not disabled. You must disable
    the distribution before you can delete it.
    """

    Message: Optional[string]


class FieldLevelEncryptionConfigAlreadyExists(ServiceException):
    """The specified configuration for field-level encryption already exists."""

    Message: Optional[string]


class FieldLevelEncryptionConfigInUse(ServiceException):
    """The specified configuration for field-level encryption is in use."""

    Message: Optional[string]


class FieldLevelEncryptionProfileAlreadyExists(ServiceException):
    """The specified profile for field-level encryption already exists."""

    Message: Optional[string]


class FieldLevelEncryptionProfileInUse(ServiceException):
    """The specified profile for field-level encryption is in use."""

    Message: Optional[string]


class FieldLevelEncryptionProfileSizeExceeded(ServiceException):
    """The maximum size of a profile for field-level encryption was exceeded."""

    Message: Optional[string]


class FunctionAlreadyExists(ServiceException):
    """A function with the same name already exists in this Amazon Web Services
    account. To create a function, you must provide a unique name. To update
    an existing function, use ``UpdateFunction``.
    """

    Message: Optional[string]


class FunctionInUse(ServiceException):
    """Cannot delete the function because it’s attached to one or more cache
    behaviors.
    """

    Message: Optional[string]


class FunctionSizeLimitExceeded(ServiceException):
    """The function is too large. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class IllegalDelete(ServiceException):
    """You cannot delete a managed policy."""

    Message: Optional[string]


class IllegalFieldLevelEncryptionConfigAssociationWithCacheBehavior(ServiceException):
    """The specified configuration for field-level encryption can't be
    associated with the specified cache behavior.
    """

    Message: Optional[string]


class IllegalUpdate(ServiceException):
    """The update contains modifications that are not allowed."""

    Message: Optional[string]


class InconsistentQuantities(ServiceException):
    """The value of ``Quantity`` and the size of ``Items`` don't match."""

    Message: Optional[string]


class InvalidArgument(ServiceException):
    """An argument is invalid."""

    Message: Optional[string]


class InvalidDefaultRootObject(ServiceException):
    """The default root object file name is too big or contains an invalid
    character.
    """

    Message: Optional[string]


class InvalidErrorCode(ServiceException):
    """An invalid error code was specified."""

    Message: Optional[string]


class InvalidForwardCookies(ServiceException):
    """Your request contains forward cookies option which doesn't match with
    the expectation for the ``whitelisted`` list of cookie names. Either
    list of cookie names has been specified when not allowed or list of
    cookie names is missing when expected.
    """

    Message: Optional[string]


class InvalidFunctionAssociation(ServiceException):
    """A CloudFront function association is invalid."""

    Message: Optional[string]


class InvalidGeoRestrictionParameter(ServiceException):
    """The specified geo restriction parameter is not valid."""

    Message: Optional[string]


class InvalidHeadersForS3Origin(ServiceException):
    """The headers specified are not valid for an Amazon S3 origin."""

    Message: Optional[string]


class InvalidIfMatchVersion(ServiceException):
    """The ``If-Match`` version is missing or not valid."""

    Message: Optional[string]


class InvalidLambdaFunctionAssociation(ServiceException):
    """The specified Lambda@Edge function association is invalid."""

    Message: Optional[string]


class InvalidLocationCode(ServiceException):
    """The location code specified is not valid."""

    Message: Optional[string]


class InvalidMinimumProtocolVersion(ServiceException):
    """The minimum protocol version specified is not valid."""

    Message: Optional[string]


class InvalidOrigin(ServiceException):
    """The Amazon S3 origin server specified does not refer to a valid Amazon
    S3 bucket.
    """

    Message: Optional[string]


class InvalidOriginAccessIdentity(ServiceException):
    """The origin access identity is not valid or doesn't exist."""

    Message: Optional[string]


class InvalidOriginKeepaliveTimeout(ServiceException):
    """The keep alive timeout specified for the origin is not valid."""

    Message: Optional[string]


class InvalidOriginReadTimeout(ServiceException):
    """The read timeout specified for the origin is not valid."""

    Message: Optional[string]


class InvalidProtocolSettings(ServiceException):
    """You cannot specify SSLv3 as the minimum protocol version if you only
    want to support only clients that support Server Name Indication (SNI).
    """

    Message: Optional[string]


class InvalidQueryStringParameters(ServiceException):
    """The query string parameters specified are not valid."""

    Message: Optional[string]


class InvalidRelativePath(ServiceException):
    """The relative path is too big, is not URL-encoded, or does not begin with
    a slash (/).
    """

    Message: Optional[string]


class InvalidRequiredProtocol(ServiceException):
    """This operation requires the HTTPS protocol. Ensure that you specify the
    HTTPS protocol in your request, or omit the ``RequiredProtocols``
    element from your distribution configuration.
    """

    Message: Optional[string]


class InvalidResponseCode(ServiceException):
    """A response code is not valid."""

    Message: Optional[string]


class InvalidTTLOrder(ServiceException):
    """The TTL order specified is not valid."""

    Message: Optional[string]


class InvalidTagging(ServiceException):
    """The tagging specified is not valid."""

    Message: Optional[string]


class InvalidViewerCertificate(ServiceException):
    """A viewer certificate specified is not valid."""

    Message: Optional[string]


class InvalidWebACLId(ServiceException):
    """A web ACL ID specified is not valid. To specify a web ACL created using
    the latest version of WAF, use the ACL ARN, for example
    ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``.
    To specify a web ACL created using WAF Classic, use the ACL ID, for
    example ``473e64fd-f30b-4765-81a0-62ad96dd167a``.
    """

    Message: Optional[string]


class KeyGroupAlreadyExists(ServiceException):
    """A key group with this name already exists. You must provide a unique
    name. To modify an existing key group, use ``UpdateKeyGroup``.
    """

    Message: Optional[string]


class MissingBody(ServiceException):
    """This operation requires a body. Ensure that the body is present and the
    ``Content-Type`` header is set.
    """

    Message: Optional[string]


class NoSuchCachePolicy(ServiceException):
    """The cache policy does not exist."""

    Message: Optional[string]


class NoSuchCloudFrontOriginAccessIdentity(ServiceException):
    """The specified origin access identity does not exist."""

    Message: Optional[string]


class NoSuchDistribution(ServiceException):
    """The specified distribution does not exist."""

    Message: Optional[string]


class NoSuchFieldLevelEncryptionConfig(ServiceException):
    """The specified configuration for field-level encryption doesn't exist."""

    Message: Optional[string]


class NoSuchFieldLevelEncryptionProfile(ServiceException):
    """The specified profile for field-level encryption doesn't exist."""

    Message: Optional[string]


class NoSuchFunctionExists(ServiceException):
    """The function does not exist."""

    Message: Optional[string]


class NoSuchInvalidation(ServiceException):
    """The specified invalidation does not exist."""

    Message: Optional[string]


class NoSuchOrigin(ServiceException):
    """No origin exists with the specified ``Origin Id``."""

    Message: Optional[string]


class NoSuchOriginRequestPolicy(ServiceException):
    """The origin request policy does not exist."""

    Message: Optional[string]


class NoSuchPublicKey(ServiceException):
    """The specified public key doesn't exist."""

    Message: Optional[string]


class NoSuchRealtimeLogConfig(ServiceException):
    """The real-time log configuration does not exist."""

    Message: Optional[string]


class NoSuchResource(ServiceException):
    """A resource that was specified is not valid."""

    Message: Optional[string]


class NoSuchResponseHeadersPolicy(ServiceException):
    """The response headers policy does not exist."""

    Message: Optional[string]


class NoSuchStreamingDistribution(ServiceException):
    """The specified streaming distribution does not exist."""

    Message: Optional[string]


class OriginRequestPolicyAlreadyExists(ServiceException):
    """An origin request policy with this name already exists. You must provide
    a unique name. To modify an existing origin request policy, use
    ``UpdateOriginRequestPolicy``.
    """

    Message: Optional[string]


class OriginRequestPolicyInUse(ServiceException):
    """Cannot delete the origin request policy because it is attached to one or
    more cache behaviors.
    """

    Message: Optional[string]


class PreconditionFailed(ServiceException):
    """The precondition in one or more of the request fields evaluated to
    ``false``.
    """

    Message: Optional[string]


class PublicKeyAlreadyExists(ServiceException):
    """The specified public key already exists."""

    Message: Optional[string]


class PublicKeyInUse(ServiceException):
    """The specified public key is in use."""

    Message: Optional[string]


class QueryArgProfileEmpty(ServiceException):
    """No profile specified for the field-level encryption query argument."""

    Message: Optional[string]


class RealtimeLogConfigAlreadyExists(ServiceException):
    """A real-time log configuration with this name already exists. You must
    provide a unique name. To modify an existing real-time log
    configuration, use ``UpdateRealtimeLogConfig``.
    """

    Message: Optional[string]


class RealtimeLogConfigInUse(ServiceException):
    """Cannot delete the real-time log configuration because it is attached to
    one or more cache behaviors.
    """

    Message: Optional[string]


class RealtimeLogConfigOwnerMismatch(ServiceException):
    """The specified real-time log configuration belongs to a different Amazon
    Web Services account.
    """

    Message: Optional[string]


class ResourceInUse(ServiceException):
    """Cannot delete this resource because it is in use."""

    Message: Optional[string]


class ResponseHeadersPolicyAlreadyExists(ServiceException):
    """A response headers policy with this name already exists. You must
    provide a unique name. To modify an existing response headers policy,
    use ``UpdateResponseHeadersPolicy``.
    """

    Message: Optional[string]


class ResponseHeadersPolicyInUse(ServiceException):
    """Cannot delete the response headers policy because it is attached to one
    or more cache behaviors in a CloudFront distribution.
    """

    Message: Optional[string]


class StreamingDistributionAlreadyExists(ServiceException):
    """The caller reference you attempted to create the streaming distribution
    with is associated with another distribution
    """

    Message: Optional[string]


class StreamingDistributionNotDisabled(ServiceException):
    """The specified CloudFront distribution is not disabled. You must disable
    the distribution before you can delete it.
    """

    Message: Optional[string]


class TestFunctionFailed(ServiceException):
    """The CloudFront function failed."""

    Message: Optional[string]


class TooManyCacheBehaviors(ServiceException):
    """You cannot create more cache behaviors for the distribution."""

    Message: Optional[string]


class TooManyCachePolicies(ServiceException):
    """You have reached the maximum number of cache policies for this Amazon
    Web Services account. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyCertificates(ServiceException):
    """You cannot create anymore custom SSL/TLS certificates."""

    Message: Optional[string]


class TooManyCloudFrontOriginAccessIdentities(ServiceException):
    """Processing your request would cause you to exceed the maximum number of
    origin access identities allowed.
    """

    Message: Optional[string]


class TooManyCookieNamesInWhiteList(ServiceException):
    """Your request contains more cookie names in the whitelist than are
    allowed per cache behavior.
    """

    Message: Optional[string]


class TooManyCookiesInCachePolicy(ServiceException):
    """The number of cookies in the cache policy exceeds the maximum. For more
    information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyCookiesInOriginRequestPolicy(ServiceException):
    """The number of cookies in the origin request policy exceeds the maximum.
    For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyCustomHeadersInResponseHeadersPolicy(ServiceException):
    """The number of custom headers in the response headers policy exceeds the
    maximum.

    For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyDistributionCNAMEs(ServiceException):
    """Your request contains more CNAMEs than are allowed per distribution."""

    Message: Optional[string]


class TooManyDistributions(ServiceException):
    """Processing your request would cause you to exceed the maximum number of
    distributions allowed.
    """

    Message: Optional[string]


class TooManyDistributionsAssociatedToCachePolicy(ServiceException):
    """The maximum number of distributions have been associated with the
    specified cache policy. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyDistributionsAssociatedToFieldLevelEncryptionConfig(ServiceException):
    """The maximum number of distributions have been associated with the
    specified configuration for field-level encryption.
    """

    Message: Optional[string]


class TooManyDistributionsAssociatedToKeyGroup(ServiceException):
    """The number of distributions that reference this key group is more than
    the maximum allowed. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyDistributionsAssociatedToOriginRequestPolicy(ServiceException):
    """The maximum number of distributions have been associated with the
    specified origin request policy. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyDistributionsAssociatedToResponseHeadersPolicy(ServiceException):
    """The maximum number of distributions have been associated with the
    specified response headers policy.

    For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyDistributionsWithFunctionAssociations(ServiceException):
    """You have reached the maximum number of distributions that are associated
    with a CloudFront function. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyDistributionsWithLambdaAssociations(ServiceException):
    """Processing your request would cause the maximum number of distributions
    with Lambda@Edge function associations per owner to be exceeded.
    """

    Message: Optional[string]


class TooManyDistributionsWithSingleFunctionARN(ServiceException):
    """The maximum number of distributions have been associated with the
    specified Lambda@Edge function.
    """

    Message: Optional[string]


class TooManyFieldLevelEncryptionConfigs(ServiceException):
    """The maximum number of configurations for field-level encryption have
    been created.
    """

    Message: Optional[string]


class TooManyFieldLevelEncryptionContentTypeProfiles(ServiceException):
    """The maximum number of content type profiles for field-level encryption
    have been created.
    """

    Message: Optional[string]


class TooManyFieldLevelEncryptionEncryptionEntities(ServiceException):
    """The maximum number of encryption entities for field-level encryption
    have been created.
    """

    Message: Optional[string]


class TooManyFieldLevelEncryptionFieldPatterns(ServiceException):
    """The maximum number of field patterns for field-level encryption have
    been created.
    """

    Message: Optional[string]


class TooManyFieldLevelEncryptionProfiles(ServiceException):
    """The maximum number of profiles for field-level encryption have been
    created.
    """

    Message: Optional[string]


class TooManyFieldLevelEncryptionQueryArgProfiles(ServiceException):
    """The maximum number of query arg profiles for field-level encryption have
    been created.
    """

    Message: Optional[string]


class TooManyFunctionAssociations(ServiceException):
    """You have reached the maximum number of CloudFront function associations
    for this distribution. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyFunctions(ServiceException):
    """You have reached the maximum number of CloudFront functions for this
    Amazon Web Services account. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyHeadersInCachePolicy(ServiceException):
    """The number of headers in the cache policy exceeds the maximum. For more
    information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyHeadersInForwardedValues(ServiceException):
    """Your request contains too many headers in forwarded values."""

    Message: Optional[string]


class TooManyHeadersInOriginRequestPolicy(ServiceException):
    """The number of headers in the origin request policy exceeds the maximum.
    For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyInvalidationsInProgress(ServiceException):
    """You have exceeded the maximum number of allowable InProgress
    invalidation batch requests, or invalidation objects.
    """

    Message: Optional[string]


class TooManyKeyGroups(ServiceException):
    """You have reached the maximum number of key groups for this Amazon Web
    Services account. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyKeyGroupsAssociatedToDistribution(ServiceException):
    """The number of key groups referenced by this distribution is more than
    the maximum allowed. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyLambdaFunctionAssociations(ServiceException):
    """Your request contains more Lambda@Edge function associations than are
    allowed per distribution.
    """

    Message: Optional[string]


class TooManyOriginCustomHeaders(ServiceException):
    """Your request contains too many origin custom headers."""

    Message: Optional[string]


class TooManyOriginGroupsPerDistribution(ServiceException):
    """Processing your request would cause you to exceed the maximum number of
    origin groups allowed.
    """

    Message: Optional[string]


class TooManyOriginRequestPolicies(ServiceException):
    """You have reached the maximum number of origin request policies for this
    Amazon Web Services account. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyOrigins(ServiceException):
    """You cannot create more origins for the distribution."""

    Message: Optional[string]


class TooManyPublicKeys(ServiceException):
    """The maximum number of public keys for field-level encryption have been
    created. To create a new public key, delete one of the existing keys.
    """

    Message: Optional[string]


class TooManyPublicKeysInKeyGroup(ServiceException):
    """The number of public keys in this key group is more than the maximum
    allowed. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyQueryStringParameters(ServiceException):
    """Your request contains too many query string parameters."""

    Message: Optional[string]


class TooManyQueryStringsInCachePolicy(ServiceException):
    """The number of query strings in the cache policy exceeds the maximum. For
    more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyQueryStringsInOriginRequestPolicy(ServiceException):
    """The number of query strings in the origin request policy exceeds the
    maximum. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyRealtimeLogConfigs(ServiceException):
    """You have reached the maximum number of real-time log configurations for
    this Amazon Web Services account. For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyResponseHeadersPolicies(ServiceException):
    """You have reached the maximum number of response headers policies for
    this Amazon Web Services account.

    For more information, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    (formerly known as limits) in the *Amazon CloudFront Developer Guide*.
    """

    Message: Optional[string]


class TooManyStreamingDistributionCNAMEs(ServiceException):
    """Your request contains more CNAMEs than are allowed per distribution."""

    Message: Optional[string]


class TooManyStreamingDistributions(ServiceException):
    """Processing your request would cause you to exceed the maximum number of
    streaming distributions allowed.
    """

    Message: Optional[string]


class TooManyTrustedSigners(ServiceException):
    """Your request contains more trusted signers than are allowed per
    distribution.
    """

    Message: Optional[string]


class TrustedKeyGroupDoesNotExist(ServiceException):
    """The specified key group does not exist."""

    Message: Optional[string]


class TrustedSignerDoesNotExist(ServiceException):
    """One or more of your trusted signers don't exist."""

    Message: Optional[string]


class UnsupportedOperation(ServiceException):
    """This operation is not supported in this region."""

    Message: Optional[string]


AccessControlAllowHeadersList = List[string]
AccessControlAllowMethodsList = List[ResponseHeadersPolicyAccessControlAllowMethodsValues]
AccessControlAllowOriginsList = List[string]
AccessControlExposeHeadersList = List[string]
KeyPairIdList = List[string]


class KeyPairIds(TypedDict, total=False):
    """A list of CloudFront key pair identifiers."""

    Quantity: integer
    Items: Optional[KeyPairIdList]


class KGKeyPairIds(TypedDict, total=False):
    """A list of identifiers for the public keys that CloudFront can use to
    verify the signatures of signed URLs and signed cookies.
    """

    KeyGroupId: Optional[string]
    KeyPairIds: Optional[KeyPairIds]


KGKeyPairIdsList = List[KGKeyPairIds]


class ActiveTrustedKeyGroups(TypedDict, total=False):
    """A list of key groups, and the public keys in each key group, that
    CloudFront can use to verify the signatures of signed URLs and signed
    cookies.
    """

    Enabled: boolean
    Quantity: integer
    Items: Optional[KGKeyPairIdsList]


class Signer(TypedDict, total=False):
    """A list of Amazon Web Services accounts and the active CloudFront key
    pairs in each account that CloudFront can use to verify the signatures
    of signed URLs and signed cookies.
    """

    AwsAccountNumber: Optional[string]
    KeyPairIds: Optional[KeyPairIds]


SignerList = List[Signer]


class ActiveTrustedSigners(TypedDict, total=False):
    """A list of Amazon Web Services accounts and the active CloudFront key
    pairs in each account that CloudFront can use to verify the signatures
    of signed URLs and signed cookies.
    """

    Enabled: boolean
    Quantity: integer
    Items: Optional[SignerList]


class AliasICPRecordal(TypedDict, total=False):
    """Amazon Web Services services in China customers must file for an
    Internet Content Provider (ICP) recordal if they want to serve content
    publicly on an alternate domain name, also known as a CNAME, that
    they've added to CloudFront. AliasICPRecordal provides the ICP recordal
    status for CNAMEs associated with distributions. The status is returned
    in the CloudFront response; you can't configure it yourself.

    For more information about ICP recordals, see `Signup, Accounts, and
    Credentials <https://docs.amazonaws.cn/en_us/aws/latest/userguide/accounts-and-credentials.html>`__
    in *Getting Started with Amazon Web Services services in China*.
    """

    CNAME: Optional[string]
    ICPRecordalStatus: Optional[ICPRecordalStatus]


AliasICPRecordals = List[AliasICPRecordal]
AliasList = List[string]


class Aliases(TypedDict, total=False):
    """A complex type that contains information about CNAMEs (alternate domain
    names), if any, for this distribution.
    """

    Quantity: integer
    Items: Optional[AliasList]


MethodsList = List[Method]


class CachedMethods(TypedDict, total=False):
    """A complex type that controls whether CloudFront caches the response to
    requests using the specified HTTP methods. There are two choices:

    -  CloudFront caches responses to ``GET`` and ``HEAD`` requests.

    -  CloudFront caches responses to ``GET``, ``HEAD``, and ``OPTIONS``
       requests.

    If you pick the second choice for your Amazon S3 Origin, you may need to
    forward Access-Control-Request-Method, Access-Control-Request-Headers,
    and Origin headers for the responses to be cached correctly.
    """

    Quantity: integer
    Items: MethodsList


class AllowedMethods(TypedDict, total=False):
    """A complex type that controls which HTTP methods CloudFront processes and
    forwards to your Amazon S3 bucket or your custom origin. There are three
    choices:

    -  CloudFront forwards only ``GET`` and ``HEAD`` requests.

    -  CloudFront forwards only ``GET``, ``HEAD``, and ``OPTIONS`` requests.

    -  CloudFront forwards ``GET, HEAD, OPTIONS, PUT, PATCH, POST``, and
       ``DELETE`` requests.

    If you pick the third choice, you may need to restrict access to your
    Amazon S3 bucket or to your custom origin so users can't perform
    operations that you don't want them to. For example, you might not want
    users to have permissions to delete objects from your origin.
    """

    Quantity: integer
    Items: MethodsList
    CachedMethods: Optional[CachedMethods]


class AssociateAliasRequest(ServiceRequest):
    TargetDistributionId: string
    Alias: string


AwsAccountNumberList = List[string]
long = int
QueryStringCacheKeysList = List[string]


class QueryStringCacheKeys(TypedDict, total=False):
    """This field is deprecated. We recommend that you use a cache policy or an
    origin request policy instead of this field.

    If you want to include query strings in the cache key, use
    ``QueryStringsConfig`` in a cache policy. See ``CachePolicy``.

    If you want to send query strings to the origin but not include them in
    the cache key, use ``QueryStringsConfig`` in an origin request policy.
    See ``OriginRequestPolicy``.

    A complex type that contains information about the query string
    parameters that you want CloudFront to use for caching for a cache
    behavior.
    """

    Quantity: integer
    Items: Optional[QueryStringCacheKeysList]


HeaderList = List[string]


class Headers(TypedDict, total=False):
    """Contains a list of HTTP header names."""

    Quantity: integer
    Items: Optional[HeaderList]


CookieNameList = List[string]


class CookieNames(TypedDict, total=False):
    """Contains a list of cookie names."""

    Quantity: integer
    Items: Optional[CookieNameList]


class CookiePreference(TypedDict, total=False):
    """This field is deprecated. We recommend that you use a cache policy or an
    origin request policy instead of this field.

    If you want to include cookies in the cache key, use ``CookiesConfig``
    in a cache policy. See ``CachePolicy``.

    If you want to send cookies to the origin but not include them in the
    cache key, use ``CookiesConfig`` in an origin request policy. See
    ``OriginRequestPolicy``.

    A complex type that specifies whether you want CloudFront to forward
    cookies to the origin and, if so, which ones. For more information about
    forwarding cookies to the origin, see `Caching Content Based on
    Cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Cookies.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Forward: ItemSelection
    WhitelistedNames: Optional[CookieNames]


class ForwardedValues(TypedDict, total=False):
    """This field is deprecated. We recommend that you use a cache policy or an
    origin request policy instead of this field.

    If you want to include values in the cache key, use a cache policy. For
    more information, see `Creating cache
    policies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html#cache-key-create-cache-policy>`__
    in the *Amazon CloudFront Developer Guide*.

    If you want to send values to the origin but not include them in the
    cache key, use an origin request policy. For more information, see
    `Creating origin request
    policies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html#origin-request-create-origin-request-policy>`__
    in the *Amazon CloudFront Developer Guide*.

    A complex type that specifies how CloudFront handles query strings,
    cookies, and HTTP headers.
    """

    QueryString: boolean
    Cookies: CookiePreference
    Headers: Optional[Headers]
    QueryStringCacheKeys: Optional[QueryStringCacheKeys]


class FunctionAssociation(TypedDict, total=False):
    """A CloudFront function that is associated with a cache behavior in a
    CloudFront distribution.
    """

    FunctionARN: FunctionARN
    EventType: EventType


FunctionAssociationList = List[FunctionAssociation]


class FunctionAssociations(TypedDict, total=False):
    """A list of CloudFront functions that are associated with a cache behavior
    in a CloudFront distribution. CloudFront functions must be published to
    the ``LIVE`` stage to associate them with a cache behavior.
    """

    Quantity: integer
    Items: Optional[FunctionAssociationList]


class LambdaFunctionAssociation(TypedDict, total=False):
    """A complex type that contains a Lambda@Edge function association."""

    LambdaFunctionARN: LambdaFunctionARN
    EventType: EventType
    IncludeBody: Optional[boolean]


LambdaFunctionAssociationList = List[LambdaFunctionAssociation]


class LambdaFunctionAssociations(TypedDict, total=False):
    """A complex type that specifies a list of Lambda@Edge functions
    associations for a cache behavior.

    If you want to invoke one or more Lambda@Edge functions triggered by
    requests that match the ``PathPattern`` of the cache behavior, specify
    the applicable values for ``Quantity`` and ``Items``. Note that there
    can be up to 4 ``LambdaFunctionAssociation`` items in this list (one for
    each possible value of ``EventType``) and each ``EventType`` can be
    associated with only one function.

    If you don't want to invoke any Lambda@Edge functions for the requests
    that match ``PathPattern``, specify ``0`` for ``Quantity`` and omit
    ``Items``.
    """

    Quantity: integer
    Items: Optional[LambdaFunctionAssociationList]


TrustedKeyGroupIdList = List[string]


class TrustedKeyGroups(TypedDict, total=False):
    """A list of key groups whose public keys CloudFront can use to verify the
    signatures of signed URLs and signed cookies.
    """

    Enabled: boolean
    Quantity: integer
    Items: Optional[TrustedKeyGroupIdList]


class TrustedSigners(TypedDict, total=False):
    """A list of Amazon Web Services accounts whose public keys CloudFront can
    use to verify the signatures of signed URLs and signed cookies.
    """

    Enabled: boolean
    Quantity: integer
    Items: Optional[AwsAccountNumberList]


class CacheBehavior(TypedDict, total=False):
    """A complex type that describes how CloudFront processes requests.

    You must create at least as many cache behaviors (including the default
    cache behavior) as you have origins if you want CloudFront to serve
    objects from all of the origins. Each cache behavior specifies the one
    origin from which you want CloudFront to get objects. If you have two
    origins and only the default cache behavior, the default cache behavior
    will cause CloudFront to get objects from one of the origins, but the
    other origin is never used.

    For the current quota (formerly known as limit) on the number of cache
    behaviors that you can add to a distribution, see
    `Quotas <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html>`__
    in the *Amazon CloudFront Developer Guide*.

    If you don’t want to specify any cache behaviors, include only an empty
    ``CacheBehaviors`` element. Don’t include an empty ``CacheBehavior``
    element because this is invalid.

    To delete all cache behaviors in an existing distribution, update the
    distribution configuration and include only an empty ``CacheBehaviors``
    element.

    To add, change, or remove one or more cache behaviors, update the
    distribution configuration and specify all of the cache behaviors that
    you want to include in the updated distribution.

    For more information about cache behaviors, see `Cache Behavior
    Settings <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html#DownloadDistValuesCacheBehavior>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    PathPattern: string
    TargetOriginId: string
    TrustedSigners: Optional[TrustedSigners]
    TrustedKeyGroups: Optional[TrustedKeyGroups]
    ViewerProtocolPolicy: ViewerProtocolPolicy
    AllowedMethods: Optional[AllowedMethods]
    SmoothStreaming: Optional[boolean]
    Compress: Optional[boolean]
    LambdaFunctionAssociations: Optional[LambdaFunctionAssociations]
    FunctionAssociations: Optional[FunctionAssociations]
    FieldLevelEncryptionId: Optional[string]
    RealtimeLogConfigArn: Optional[string]
    CachePolicyId: Optional[string]
    OriginRequestPolicyId: Optional[string]
    ResponseHeadersPolicyId: Optional[string]
    ForwardedValues: Optional[ForwardedValues]
    MinTTL: Optional[long]
    DefaultTTL: Optional[long]
    MaxTTL: Optional[long]


CacheBehaviorList = List[CacheBehavior]


class CacheBehaviors(TypedDict, total=False):
    """A complex type that contains zero or more ``CacheBehavior`` elements."""

    Quantity: integer
    Items: Optional[CacheBehaviorList]


QueryStringNamesList = List[string]


class QueryStringNames(TypedDict, total=False):
    """Contains a list of query string names."""

    Quantity: integer
    Items: Optional[QueryStringNamesList]


class CachePolicyQueryStringsConfig(TypedDict, total=False):
    """An object that determines whether any URL query strings in viewer
    requests (and if so, which query strings) are included in the cache key
    and automatically included in requests that CloudFront sends to the
    origin.
    """

    QueryStringBehavior: CachePolicyQueryStringBehavior
    QueryStrings: Optional[QueryStringNames]


class CachePolicyCookiesConfig(TypedDict, total=False):
    """An object that determines whether any cookies in viewer requests (and if
    so, which cookies) are included in the cache key and automatically
    included in requests that CloudFront sends to the origin.
    """

    CookieBehavior: CachePolicyCookieBehavior
    Cookies: Optional[CookieNames]


class CachePolicyHeadersConfig(TypedDict, total=False):
    """An object that determines whether any HTTP headers (and if so, which
    headers) are included in the cache key and automatically included in
    requests that CloudFront sends to the origin.
    """

    HeaderBehavior: CachePolicyHeaderBehavior
    Headers: Optional[Headers]


class ParametersInCacheKeyAndForwardedToOrigin(TypedDict, total=False):
    """This object determines the values that CloudFront includes in the cache
    key. These values can include HTTP headers, cookies, and URL query
    strings. CloudFront uses the cache key to find an object in its cache
    that it can return to the viewer.

    The headers, cookies, and query strings that are included in the cache
    key are automatically included in requests that CloudFront sends to the
    origin. CloudFront sends a request when it can’t find an object in its
    cache that matches the request’s cache key. If you want to send values
    to the origin but *not* include them in the cache key, use
    ``OriginRequestPolicy``.
    """

    EnableAcceptEncodingGzip: boolean
    EnableAcceptEncodingBrotli: Optional[boolean]
    HeadersConfig: CachePolicyHeadersConfig
    CookiesConfig: CachePolicyCookiesConfig
    QueryStringsConfig: CachePolicyQueryStringsConfig


class CachePolicyConfig(TypedDict, total=False):
    """A cache policy configuration.

    This configuration determines the following:

    -  The values that CloudFront includes in the cache key. These values
       can include HTTP headers, cookies, and URL query strings. CloudFront
       uses the cache key to find an object in its cache that it can return
       to the viewer.

    -  The default, minimum, and maximum time to live (TTL) values that you
       want objects to stay in the CloudFront cache.

    The headers, cookies, and query strings that are included in the cache
    key are automatically included in requests that CloudFront sends to the
    origin. CloudFront sends a request when it can’t find a valid object in
    its cache that matches the request’s cache key. If you want to send
    values to the origin but *not* include them in the cache key, use
    ``OriginRequestPolicy``.
    """

    Comment: Optional[string]
    Name: string
    DefaultTTL: Optional[long]
    MaxTTL: Optional[long]
    MinTTL: long
    ParametersInCacheKeyAndForwardedToOrigin: Optional[ParametersInCacheKeyAndForwardedToOrigin]


timestamp = datetime


class CachePolicy(TypedDict, total=False):
    """A cache policy.

    When it’s attached to a cache behavior, the cache policy determines the
    following:

    -  The values that CloudFront includes in the cache key. These values
       can include HTTP headers, cookies, and URL query strings. CloudFront
       uses the cache key to find an object in its cache that it can return
       to the viewer.

    -  The default, minimum, and maximum time to live (TTL) values that you
       want objects to stay in the CloudFront cache.

    The headers, cookies, and query strings that are included in the cache
    key are automatically included in requests that CloudFront sends to the
    origin. CloudFront sends a request when it can’t find a valid object in
    its cache that matches the request’s cache key. If you want to send
    values to the origin but *not* include them in the cache key, use
    ``OriginRequestPolicy``.
    """

    Id: string
    LastModifiedTime: timestamp
    CachePolicyConfig: CachePolicyConfig


class CachePolicySummary(TypedDict, total=False):
    """Contains a cache policy."""

    Type: CachePolicyType
    CachePolicy: CachePolicy


CachePolicySummaryList = List[CachePolicySummary]


class CachePolicyList(TypedDict, total=False):
    """A list of cache policies."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[CachePolicySummaryList]


class CloudFrontOriginAccessIdentityConfig(TypedDict, total=False):
    """Origin access identity configuration. Send a ``GET`` request to the
    ``/CloudFront API version/CloudFront/identity ID/config`` resource.
    """

    CallerReference: string
    Comment: string


class CloudFrontOriginAccessIdentity(TypedDict, total=False):
    """CloudFront origin access identity."""

    Id: string
    S3CanonicalUserId: string
    CloudFrontOriginAccessIdentityConfig: Optional[CloudFrontOriginAccessIdentityConfig]


class CloudFrontOriginAccessIdentitySummary(TypedDict, total=False):
    """Summary of the information about a CloudFront origin access identity."""

    Id: string
    S3CanonicalUserId: string
    Comment: string


CloudFrontOriginAccessIdentitySummaryList = List[CloudFrontOriginAccessIdentitySummary]


class CloudFrontOriginAccessIdentityList(TypedDict, total=False):
    """Lists the origin access identities for CloudFront.Send a ``GET`` request
    to the ``/CloudFront API version/origin-access-identity/cloudfront``
    resource. The response includes a ``CloudFrontOriginAccessIdentityList``
    element with zero or more ``CloudFrontOriginAccessIdentitySummary``
    child elements. By default, your entire list of origin access identities
    is returned in one single page. If the list is long, you can paginate it
    using the ``MaxItems`` and ``Marker`` parameters.
    """

    Marker: string
    NextMarker: Optional[string]
    MaxItems: integer
    IsTruncated: boolean
    Quantity: integer
    Items: Optional[CloudFrontOriginAccessIdentitySummaryList]


class ConflictingAlias(TypedDict, total=False):
    """An alias (also called a CNAME) and the CloudFront distribution and
    Amazon Web Services account ID that it’s associated with. The
    distribution and account IDs are partially hidden, which allows you to
    identify the distributions and accounts that you own, but helps to
    protect the information of ones that you don’t own.
    """

    Alias: Optional[string]
    DistributionId: Optional[string]
    AccountId: Optional[string]


ConflictingAliases = List[ConflictingAlias]


class ConflictingAliasesList(TypedDict, total=False):
    """A list of aliases (also called CNAMEs) and the CloudFront distributions
    and Amazon Web Services accounts that they are associated with. In the
    list, the distribution and account IDs are partially hidden, which
    allows you to identify the distributions and accounts that you own, but
    helps to protect the information of ones that you don’t own.
    """

    NextMarker: Optional[string]
    MaxItems: Optional[integer]
    Quantity: Optional[integer]
    Items: Optional[ConflictingAliases]


class ContentTypeProfile(TypedDict, total=False):
    """A field-level encryption content type profile."""

    Format: Format
    ProfileId: Optional[string]
    ContentType: string


ContentTypeProfileList = List[ContentTypeProfile]


class ContentTypeProfiles(TypedDict, total=False):
    """Field-level encryption content type-profile."""

    Quantity: integer
    Items: Optional[ContentTypeProfileList]


class ContentTypeProfileConfig(TypedDict, total=False):
    """The configuration for a field-level encryption content type-profile
    mapping.
    """

    ForwardWhenContentTypeIsUnknown: boolean
    ContentTypeProfiles: Optional[ContentTypeProfiles]


class CreateCachePolicyRequest(ServiceRequest):
    CachePolicyConfig: CachePolicyConfig


class CreateCachePolicyResult(TypedDict, total=False):
    CachePolicy: Optional[CachePolicy]
    Location: Optional[string]
    ETag: Optional[string]


class CreateCloudFrontOriginAccessIdentityRequest(ServiceRequest):
    """The request to create a new origin access identity (OAI). An origin
    access identity is a special CloudFront user that you can associate with
    Amazon S3 origins, so that you can secure all or just some of your
    Amazon S3 content. For more information, see `Restricting Access to
    Amazon S3 Content by Using an Origin Access
    Identity <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    CloudFrontOriginAccessIdentityConfig: CloudFrontOriginAccessIdentityConfig


class CreateCloudFrontOriginAccessIdentityResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    CloudFrontOriginAccessIdentity: Optional[CloudFrontOriginAccessIdentity]
    Location: Optional[string]
    ETag: Optional[string]


LocationList = List[string]


class GeoRestriction(TypedDict, total=False):
    """A complex type that controls the countries in which your content is
    distributed. CloudFront determines the location of your users using
    ``MaxMind`` GeoIP databases.
    """

    RestrictionType: GeoRestrictionType
    Quantity: integer
    Items: Optional[LocationList]


class Restrictions(TypedDict, total=False):
    """A complex type that identifies ways in which you want to restrict
    distribution of your content.
    """

    GeoRestriction: GeoRestriction


class ViewerCertificate(TypedDict, total=False):
    """A complex type that determines the distribution’s SSL/TLS configuration
    for communicating with viewers.

    If the distribution doesn’t use ``Aliases`` (also known as alternate
    domain names or CNAMEs)—that is, if the distribution uses the CloudFront
    domain name such as ``d111111abcdef8.cloudfront.net``—set
    ``CloudFrontDefaultCertificate`` to ``true`` and leave all other fields
    empty.

    If the distribution uses ``Aliases`` (alternate domain names or CNAMEs),
    use the fields in this type to specify the following settings:

    -  Which viewers the distribution accepts HTTPS connections from: only
       viewers that support `server name indication
       (SNI) <https://en.wikipedia.org/wiki/Server_Name_Indication>`__
       (recommended), or all viewers including those that don’t support SNI.

       -  To accept HTTPS connections from only viewers that support SNI,
          set ``SSLSupportMethod`` to ``sni-only``. This is recommended.
          Most browsers and clients support SNI.

       -  To accept HTTPS connections from all viewers, including those that
          don’t support SNI, set ``SSLSupportMethod`` to ``vip``. This is
          not recommended, and results in additional monthly charges from
          CloudFront.

    -  The minimum SSL/TLS protocol version that the distribution can use to
       communicate with viewers. To specify a minimum version, choose a
       value for ``MinimumProtocolVersion``. For more information, see
       `Security
       Policy <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html#DownloadDistValues-security-policy>`__
       in the *Amazon CloudFront Developer Guide*.

    -  The location of the SSL/TLS certificate, `Certificate Manager
       (ACM) <https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html>`__
       (recommended) or `Identity and Access Management
       (IAM) <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_server-certs.html>`__.
       You specify the location by setting a value in one of the following
       fields (not both):

       -  ``ACMCertificateArn``

       -  ``IAMCertificateId``

    All distributions support HTTPS connections from viewers. To require
    viewers to use HTTPS only, or to redirect them from HTTP to HTTPS, use
    ``ViewerProtocolPolicy`` in the ``CacheBehavior`` or
    ``DefaultCacheBehavior``. To specify how CloudFront should use SSL/TLS
    to communicate with your custom origin, use ``CustomOriginConfig``.

    For more information, see `Using HTTPS with
    CloudFront <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https.html>`__
    and `Using Alternate Domain Names and
    HTTPS <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https-alternate-domain-names.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    CloudFrontDefaultCertificate: Optional[boolean]
    IAMCertificateId: Optional[string]
    ACMCertificateArn: Optional[string]
    SSLSupportMethod: Optional[SSLSupportMethod]
    MinimumProtocolVersion: Optional[MinimumProtocolVersion]
    Certificate: Optional[string]
    CertificateSource: Optional[CertificateSource]


class LoggingConfig(TypedDict, total=False):
    """A complex type that controls whether access logs are written for the
    distribution.
    """

    Enabled: boolean
    IncludeCookies: boolean
    Bucket: string
    Prefix: string


class CustomErrorResponse(TypedDict, total=False):
    """A complex type that controls:

    -  Whether CloudFront replaces HTTP status codes in the 4xx and 5xx
       range with custom error messages before returning the response to the
       viewer.

    -  How long CloudFront caches HTTP status codes in the 4xx and 5xx
       range.

    For more information about custom error pages, see `Customizing Error
    Responses <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/custom-error-pages.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    ErrorCode: integer
    ResponsePagePath: Optional[string]
    ResponseCode: Optional[string]
    ErrorCachingMinTTL: Optional[long]


CustomErrorResponseList = List[CustomErrorResponse]


class CustomErrorResponses(TypedDict, total=False):
    """A complex type that controls:

    -  Whether CloudFront replaces HTTP status codes in the 4xx and 5xx
       range with custom error messages before returning the response to the
       viewer.

    -  How long CloudFront caches HTTP status codes in the 4xx and 5xx
       range.

    For more information about custom error pages, see `Customizing Error
    Responses <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/custom-error-pages.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Quantity: integer
    Items: Optional[CustomErrorResponseList]


class DefaultCacheBehavior(TypedDict, total=False):
    """A complex type that describes the default cache behavior if you don’t
    specify a ``CacheBehavior`` element or if request URLs don’t match any
    of the values of ``PathPattern`` in ``CacheBehavior`` elements. You must
    create exactly one default cache behavior.
    """

    TargetOriginId: string
    TrustedSigners: Optional[TrustedSigners]
    TrustedKeyGroups: Optional[TrustedKeyGroups]
    ViewerProtocolPolicy: ViewerProtocolPolicy
    AllowedMethods: Optional[AllowedMethods]
    SmoothStreaming: Optional[boolean]
    Compress: Optional[boolean]
    LambdaFunctionAssociations: Optional[LambdaFunctionAssociations]
    FunctionAssociations: Optional[FunctionAssociations]
    FieldLevelEncryptionId: Optional[string]
    RealtimeLogConfigArn: Optional[string]
    CachePolicyId: Optional[string]
    OriginRequestPolicyId: Optional[string]
    ResponseHeadersPolicyId: Optional[string]
    ForwardedValues: Optional[ForwardedValues]
    MinTTL: Optional[long]
    DefaultTTL: Optional[long]
    MaxTTL: Optional[long]


class OriginGroupMember(TypedDict, total=False):
    """An origin in an origin group."""

    OriginId: string


OriginGroupMemberList = List[OriginGroupMember]


class OriginGroupMembers(TypedDict, total=False):
    """A complex data type for the origins included in an origin group."""

    Quantity: integer
    Items: OriginGroupMemberList


StatusCodeList = List[integer]


class StatusCodes(TypedDict, total=False):
    """A complex data type for the status codes that you specify that, when
    returned by a primary origin, trigger CloudFront to failover to a second
    origin.
    """

    Quantity: integer
    Items: StatusCodeList


class OriginGroupFailoverCriteria(TypedDict, total=False):
    """A complex data type that includes information about the failover
    criteria for an origin group, including the status codes for which
    CloudFront will failover from the primary origin to the second origin.
    """

    StatusCodes: StatusCodes


class OriginGroup(TypedDict, total=False):
    """An origin group includes two origins (a primary origin and a second
    origin to failover to) and a failover criteria that you specify. You
    create an origin group to support origin failover in CloudFront. When
    you create or update a distribution, you can specifiy the origin group
    instead of a single origin, and CloudFront will failover from the
    primary origin to the second origin under the failover conditions that
    you've chosen.
    """

    Id: string
    FailoverCriteria: OriginGroupFailoverCriteria
    Members: OriginGroupMembers


OriginGroupList = List[OriginGroup]


class OriginGroups(TypedDict, total=False):
    """A complex data type for the origin groups specified for a distribution."""

    Quantity: integer
    Items: Optional[OriginGroupList]


class OriginShield(TypedDict, total=False):
    """CloudFront Origin Shield.

    Using Origin Shield can help reduce the load on your origin. For more
    information, see `Using Origin
    Shield <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Enabled: boolean
    OriginShieldRegion: Optional[OriginShieldRegion]


SslProtocolsList = List[SslProtocol]


class OriginSslProtocols(TypedDict, total=False):
    """A complex type that contains information about the SSL/TLS protocols
    that CloudFront can use when establishing an HTTPS connection with your
    origin.
    """

    Quantity: integer
    Items: SslProtocolsList


class CustomOriginConfig(TypedDict, total=False):
    """A custom origin. A custom origin is any origin that is *not* an Amazon
    S3 bucket, with one exception. An Amazon S3 bucket that is `configured
    with static website
    hosting <https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html>`__
    *is* a custom origin.
    """

    HTTPPort: integer
    HTTPSPort: integer
    OriginProtocolPolicy: OriginProtocolPolicy
    OriginSslProtocols: Optional[OriginSslProtocols]
    OriginReadTimeout: Optional[integer]
    OriginKeepaliveTimeout: Optional[integer]


class S3OriginConfig(TypedDict, total=False):
    """A complex type that contains information about the Amazon S3 origin. If
    the origin is a custom origin or an S3 bucket that is configured as a
    website endpoint, use the ``CustomOriginConfig`` element instead.
    """

    OriginAccessIdentity: string


class OriginCustomHeader(TypedDict, total=False):
    """A complex type that contains ``HeaderName`` and ``HeaderValue``
    elements, if any, for this distribution.
    """

    HeaderName: string
    HeaderValue: sensitiveStringType


OriginCustomHeadersList = List[OriginCustomHeader]


class CustomHeaders(TypedDict, total=False):
    """A complex type that contains the list of Custom Headers for each origin."""

    Quantity: integer
    Items: Optional[OriginCustomHeadersList]


class Origin(TypedDict, total=False):
    """An origin.

    An origin is the location where content is stored, and from which
    CloudFront gets content to serve to viewers. To specify an origin:

    -  Use ``S3OriginConfig`` to specify an Amazon S3 bucket that is not
       configured with static website hosting.

    -  Use ``CustomOriginConfig`` to specify all other kinds of origins,
       including:

       -  An Amazon S3 bucket that is configured with static website hosting

       -  An Elastic Load Balancing load balancer

       -  An AWS Elemental MediaPackage endpoint

       -  An AWS Elemental MediaStore container

       -  Any other HTTP server, running on an Amazon EC2 instance or any
          other kind of host

    For the current maximum number of origins that you can specify per
    distribution, see `General Quotas on Web
    Distributions <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html#limits-web-distributions>`__
    in the *Amazon CloudFront Developer Guide* (quotas were formerly
    referred to as limits).
    """

    Id: string
    DomainName: string
    OriginPath: Optional[string]
    CustomHeaders: Optional[CustomHeaders]
    S3OriginConfig: Optional[S3OriginConfig]
    CustomOriginConfig: Optional[CustomOriginConfig]
    ConnectionAttempts: Optional[integer]
    ConnectionTimeout: Optional[integer]
    OriginShield: Optional[OriginShield]


OriginList = List[Origin]


class Origins(TypedDict, total=False):
    """Contains information about the origins for this distribution."""

    Quantity: integer
    Items: OriginList


class DistributionConfig(TypedDict, total=False):
    """A distribution configuration."""

    CallerReference: string
    Aliases: Optional[Aliases]
    DefaultRootObject: Optional[string]
    Origins: Origins
    OriginGroups: Optional[OriginGroups]
    DefaultCacheBehavior: DefaultCacheBehavior
    CacheBehaviors: Optional[CacheBehaviors]
    CustomErrorResponses: Optional[CustomErrorResponses]
    Comment: CommentType
    Logging: Optional[LoggingConfig]
    PriceClass: Optional[PriceClass]
    Enabled: boolean
    ViewerCertificate: Optional[ViewerCertificate]
    Restrictions: Optional[Restrictions]
    WebACLId: Optional[string]
    HttpVersion: Optional[HttpVersion]
    IsIPV6Enabled: Optional[boolean]


class CreateDistributionRequest(ServiceRequest):
    """The request to create a new distribution."""

    DistributionConfig: DistributionConfig


class Distribution(TypedDict, total=False):
    """A distribution tells CloudFront where you want content to be delivered
    from, and the details about how to track and manage content delivery.
    """

    Id: string
    ARN: string
    Status: string
    LastModifiedTime: timestamp
    InProgressInvalidationBatches: integer
    DomainName: string
    ActiveTrustedSigners: Optional[ActiveTrustedSigners]
    ActiveTrustedKeyGroups: Optional[ActiveTrustedKeyGroups]
    DistributionConfig: DistributionConfig
    AliasICPRecordals: Optional[AliasICPRecordals]


class CreateDistributionResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Distribution: Optional[Distribution]
    Location: Optional[string]
    ETag: Optional[string]


class Tag(TypedDict, total=False):
    """A complex type that contains ``Tag`` key and ``Tag`` value."""

    Key: TagKey
    Value: Optional[TagValue]


TagList = List[Tag]


class Tags(TypedDict, total=False):
    """A complex type that contains zero or more ``Tag`` elements."""

    Items: Optional[TagList]


class DistributionConfigWithTags(TypedDict, total=False):
    """A distribution Configuration and a list of tags to be associated with
    the distribution.
    """

    DistributionConfig: DistributionConfig
    Tags: Tags


class CreateDistributionWithTagsRequest(ServiceRequest):
    """The request to create a new distribution with tags."""

    DistributionConfigWithTags: DistributionConfigWithTags


class CreateDistributionWithTagsResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Distribution: Optional[Distribution]
    Location: Optional[string]
    ETag: Optional[string]


class QueryArgProfile(TypedDict, total=False):
    """Query argument-profile mapping for field-level encryption."""

    QueryArg: string
    ProfileId: string


QueryArgProfileList = List[QueryArgProfile]


class QueryArgProfiles(TypedDict, total=False):
    """Query argument-profile mapping for field-level encryption."""

    Quantity: integer
    Items: Optional[QueryArgProfileList]


class QueryArgProfileConfig(TypedDict, total=False):
    """Configuration for query argument-profile mapping for field-level
    encryption.
    """

    ForwardWhenQueryArgProfileIsUnknown: boolean
    QueryArgProfiles: Optional[QueryArgProfiles]


class FieldLevelEncryptionConfig(TypedDict, total=False):
    """A complex data type that includes the profile configurations specified
    for field-level encryption.
    """

    CallerReference: string
    Comment: Optional[string]
    QueryArgProfileConfig: Optional[QueryArgProfileConfig]
    ContentTypeProfileConfig: Optional[ContentTypeProfileConfig]


class CreateFieldLevelEncryptionConfigRequest(ServiceRequest):
    FieldLevelEncryptionConfig: FieldLevelEncryptionConfig


class FieldLevelEncryption(TypedDict, total=False):
    """A complex data type that includes the profile configurations and other
    options specified for field-level encryption.
    """

    Id: string
    LastModifiedTime: timestamp
    FieldLevelEncryptionConfig: FieldLevelEncryptionConfig


class CreateFieldLevelEncryptionConfigResult(TypedDict, total=False):
    FieldLevelEncryption: Optional[FieldLevelEncryption]
    Location: Optional[string]
    ETag: Optional[string]


FieldPatternList = List[string]


class FieldPatterns(TypedDict, total=False):
    """A complex data type that includes the field patterns to match for
    field-level encryption.
    """

    Quantity: integer
    Items: Optional[FieldPatternList]


class EncryptionEntity(TypedDict, total=False):
    """Complex data type for field-level encryption profiles that includes the
    encryption key and field pattern specifications.
    """

    PublicKeyId: string
    ProviderId: string
    FieldPatterns: FieldPatterns


EncryptionEntityList = List[EncryptionEntity]


class EncryptionEntities(TypedDict, total=False):
    """Complex data type for field-level encryption profiles that includes all
    of the encryption entities.
    """

    Quantity: integer
    Items: Optional[EncryptionEntityList]


class FieldLevelEncryptionProfileConfig(TypedDict, total=False):
    """A complex data type of profiles for the field-level encryption."""

    Name: string
    CallerReference: string
    Comment: Optional[string]
    EncryptionEntities: EncryptionEntities


class CreateFieldLevelEncryptionProfileRequest(ServiceRequest):
    FieldLevelEncryptionProfileConfig: FieldLevelEncryptionProfileConfig


class FieldLevelEncryptionProfile(TypedDict, total=False):
    """A complex data type for field-level encryption profiles."""

    Id: string
    LastModifiedTime: timestamp
    FieldLevelEncryptionProfileConfig: FieldLevelEncryptionProfileConfig


class CreateFieldLevelEncryptionProfileResult(TypedDict, total=False):
    FieldLevelEncryptionProfile: Optional[FieldLevelEncryptionProfile]
    Location: Optional[string]
    ETag: Optional[string]


FunctionBlob = bytes


class FunctionConfig(TypedDict, total=False):
    """Contains configuration information about a CloudFront function."""

    Comment: string
    Runtime: FunctionRuntime


class CreateFunctionRequest(ServiceRequest):
    Name: FunctionName
    FunctionConfig: FunctionConfig
    FunctionCode: FunctionBlob


class FunctionMetadata(TypedDict, total=False):
    """Contains metadata about a CloudFront function."""

    FunctionARN: string
    Stage: Optional[FunctionStage]
    CreatedTime: Optional[timestamp]
    LastModifiedTime: timestamp


class FunctionSummary(TypedDict, total=False):
    """Contains configuration information and metadata about a CloudFront
    function.
    """

    Name: FunctionName
    Status: Optional[string]
    FunctionConfig: FunctionConfig
    FunctionMetadata: FunctionMetadata


class CreateFunctionResult(TypedDict, total=False):
    FunctionSummary: Optional[FunctionSummary]
    Location: Optional[string]
    ETag: Optional[string]


PathList = List[string]


class Paths(TypedDict, total=False):
    """A complex type that contains information about the objects that you want
    to invalidate. For more information, see `Specifying the Objects to
    Invalidate <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html#invalidation-specifying-objects>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Quantity: integer
    Items: Optional[PathList]


class InvalidationBatch(TypedDict, total=False):
    """An invalidation batch."""

    Paths: Paths
    CallerReference: string


class CreateInvalidationRequest(ServiceRequest):
    """The request to create an invalidation."""

    DistributionId: string
    InvalidationBatch: InvalidationBatch


class Invalidation(TypedDict, total=False):
    """An invalidation."""

    Id: string
    Status: string
    CreateTime: timestamp
    InvalidationBatch: InvalidationBatch


class CreateInvalidationResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Location: Optional[string]
    Invalidation: Optional[Invalidation]


PublicKeyIdList = List[string]


class KeyGroupConfig(TypedDict, total=False):
    """A key group configuration.

    A key group contains a list of public keys that you can use with
    `CloudFront signed URLs and signed
    cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__.
    """

    Name: string
    Items: PublicKeyIdList
    Comment: Optional[string]


class CreateKeyGroupRequest(ServiceRequest):
    KeyGroupConfig: KeyGroupConfig


class KeyGroup(TypedDict, total=False):
    """A key group.

    A key group contains a list of public keys that you can use with
    `CloudFront signed URLs and signed
    cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__.
    """

    Id: string
    LastModifiedTime: timestamp
    KeyGroupConfig: KeyGroupConfig


class CreateKeyGroupResult(TypedDict, total=False):
    KeyGroup: Optional[KeyGroup]
    Location: Optional[string]
    ETag: Optional[string]


class RealtimeMetricsSubscriptionConfig(TypedDict, total=False):
    """A subscription configuration for additional CloudWatch metrics."""

    RealtimeMetricsSubscriptionStatus: RealtimeMetricsSubscriptionStatus


class MonitoringSubscription(TypedDict, total=False):
    """A monitoring subscription. This structure contains information about
    whether additional CloudWatch metrics are enabled for a given CloudFront
    distribution.
    """

    RealtimeMetricsSubscriptionConfig: Optional[RealtimeMetricsSubscriptionConfig]


class CreateMonitoringSubscriptionRequest(ServiceRequest):
    DistributionId: string
    MonitoringSubscription: MonitoringSubscription


class CreateMonitoringSubscriptionResult(TypedDict, total=False):
    MonitoringSubscription: Optional[MonitoringSubscription]


class OriginRequestPolicyQueryStringsConfig(TypedDict, total=False):
    """An object that determines whether any URL query strings in viewer
    requests (and if so, which query strings) are included in requests that
    CloudFront sends to the origin.
    """

    QueryStringBehavior: OriginRequestPolicyQueryStringBehavior
    QueryStrings: Optional[QueryStringNames]


class OriginRequestPolicyCookiesConfig(TypedDict, total=False):
    """An object that determines whether any cookies in viewer requests (and if
    so, which cookies) are included in requests that CloudFront sends to the
    origin.
    """

    CookieBehavior: OriginRequestPolicyCookieBehavior
    Cookies: Optional[CookieNames]


class OriginRequestPolicyHeadersConfig(TypedDict, total=False):
    """An object that determines whether any HTTP headers (and if so, which
    headers) are included in requests that CloudFront sends to the origin.
    """

    HeaderBehavior: OriginRequestPolicyHeaderBehavior
    Headers: Optional[Headers]


class OriginRequestPolicyConfig(TypedDict, total=False):
    """An origin request policy configuration.

    This configuration determines the values that CloudFront includes in
    requests that it sends to the origin. Each request that CloudFront sends
    to the origin includes the following:

    -  The request body and the URL path (without the domain name) from the
       viewer request.

    -  The headers that CloudFront automatically includes in every origin
       request, including ``Host``, ``User-Agent``, and ``X-Amz-Cf-Id``.

    -  All HTTP headers, cookies, and URL query strings that are specified
       in the cache policy or the origin request policy. These can include
       items from the viewer request and, in the case of headers, additional
       ones that are added by CloudFront.

    CloudFront sends a request when it can’t find an object in its cache
    that matches the request. If you want to send values to the origin and
    also include them in the cache key, use ``CachePolicy``.
    """

    Comment: Optional[string]
    Name: string
    HeadersConfig: OriginRequestPolicyHeadersConfig
    CookiesConfig: OriginRequestPolicyCookiesConfig
    QueryStringsConfig: OriginRequestPolicyQueryStringsConfig


class CreateOriginRequestPolicyRequest(ServiceRequest):
    OriginRequestPolicyConfig: OriginRequestPolicyConfig


class OriginRequestPolicy(TypedDict, total=False):
    """An origin request policy.

    When it’s attached to a cache behavior, the origin request policy
    determines the values that CloudFront includes in requests that it sends
    to the origin. Each request that CloudFront sends to the origin includes
    the following:

    -  The request body and the URL path (without the domain name) from the
       viewer request.

    -  The headers that CloudFront automatically includes in every origin
       request, including ``Host``, ``User-Agent``, and ``X-Amz-Cf-Id``.

    -  All HTTP headers, cookies, and URL query strings that are specified
       in the cache policy or the origin request policy. These can include
       items from the viewer request and, in the case of headers, additional
       ones that are added by CloudFront.

    CloudFront sends a request when it can’t find an object in its cache
    that matches the request. If you want to send values to the origin and
    also include them in the cache key, use ``CachePolicy``.
    """

    Id: string
    LastModifiedTime: timestamp
    OriginRequestPolicyConfig: OriginRequestPolicyConfig


class CreateOriginRequestPolicyResult(TypedDict, total=False):
    OriginRequestPolicy: Optional[OriginRequestPolicy]
    Location: Optional[string]
    ETag: Optional[string]


class PublicKeyConfig(TypedDict, total=False):
    """Configuration information about a public key that you can use with
    `signed URLs and signed
    cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__,
    or with `field-level
    encryption <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/field-level-encryption.html>`__.
    """

    CallerReference: string
    Name: string
    EncodedKey: string
    Comment: Optional[string]


class CreatePublicKeyRequest(ServiceRequest):
    PublicKeyConfig: PublicKeyConfig


class PublicKey(TypedDict, total=False):
    """A public key that you can use with `signed URLs and signed
    cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__,
    or with `field-level
    encryption <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/field-level-encryption.html>`__.
    """

    Id: string
    CreatedTime: timestamp
    PublicKeyConfig: PublicKeyConfig


class CreatePublicKeyResult(TypedDict, total=False):
    PublicKey: Optional[PublicKey]
    Location: Optional[string]
    ETag: Optional[string]


FieldList = List[string]


class KinesisStreamConfig(TypedDict, total=False):
    """Contains information about the Amazon Kinesis data stream where you are
    sending real-time log data.
    """

    RoleARN: string
    StreamARN: string


class EndPoint(TypedDict, total=False):
    """Contains information about the Amazon Kinesis data stream where you are
    sending real-time log data in a real-time log configuration.
    """

    StreamType: string
    KinesisStreamConfig: Optional[KinesisStreamConfig]


EndPointList = List[EndPoint]


class CreateRealtimeLogConfigRequest(ServiceRequest):
    EndPoints: EndPointList
    Fields: FieldList
    Name: string
    SamplingRate: long


class RealtimeLogConfig(TypedDict, total=False):
    """A real-time log configuration."""

    ARN: string
    Name: string
    SamplingRate: long
    EndPoints: EndPointList
    Fields: FieldList


class CreateRealtimeLogConfigResult(TypedDict, total=False):
    RealtimeLogConfig: Optional[RealtimeLogConfig]


class ResponseHeadersPolicyServerTimingHeadersConfig(TypedDict, total=False):
    """A configuration for enabling the ``Server-Timing`` header in HTTP
    responses sent from CloudFront. CloudFront adds this header to HTTP
    responses that it sends in response to requests that match a cache
    behavior that's associated with this response headers policy.

    You can use the ``Server-Timing`` header to view metrics that can help
    you gain insights about the behavior and performance of CloudFront. For
    example, you can see which cache layer served a cache hit, or the first
    byte latency from the origin when there was a cache miss. You can use
    the metrics in the ``Server-Timing`` header to troubleshoot issues or
    test the efficiency of your CloudFront configuration. For more
    information, see `Server-Timing
    header <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-response-headers-policies.html#server-timing-header>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Enabled: boolean
    SamplingRate: Optional[SamplingRate]


class ResponseHeadersPolicyCustomHeader(TypedDict, total=False):
    """An HTTP response header name and its value. CloudFront includes this
    header in HTTP responses that it sends for requests that match a cache
    behavior that’s associated with this response headers policy.
    """

    Header: string
    Value: string
    Override: boolean


ResponseHeadersPolicyCustomHeaderList = List[ResponseHeadersPolicyCustomHeader]


class ResponseHeadersPolicyCustomHeadersConfig(TypedDict, total=False):
    """A list of HTTP response header names and their values. CloudFront
    includes these headers in HTTP responses that it sends for requests that
    match a cache behavior that’s associated with this response headers
    policy.
    """

    Quantity: integer
    Items: Optional[ResponseHeadersPolicyCustomHeaderList]


class ResponseHeadersPolicyStrictTransportSecurity(TypedDict, total=False):
    """Determines whether CloudFront includes the ``Strict-Transport-Security``
    HTTP response header and the header’s value.

    For more information about the ``Strict-Transport-Security`` HTTP
    response header, see
    `Strict-Transport-Security <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security>`__
    in the MDN Web Docs.
    """

    Override: boolean
    IncludeSubdomains: Optional[boolean]
    Preload: Optional[boolean]
    AccessControlMaxAgeSec: integer


class ResponseHeadersPolicyContentTypeOptions(TypedDict, total=False):
    """Determines whether CloudFront includes the ``X-Content-Type-Options``
    HTTP response header with its value set to ``nosniff``.

    For more information about the ``X-Content-Type-Options`` HTTP response
    header, see
    `X-Content-Type-Options <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options>`__
    in the MDN Web Docs.
    """

    Override: boolean


class ResponseHeadersPolicyContentSecurityPolicy(TypedDict, total=False):
    """The policy directives and their values that CloudFront includes as
    values for the ``Content-Security-Policy`` HTTP response header.

    For more information about the ``Content-Security-Policy`` HTTP response
    header, see
    `Content-Security-Policy <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy>`__
    in the MDN Web Docs.
    """

    Override: boolean
    ContentSecurityPolicy: string


class ResponseHeadersPolicyReferrerPolicy(TypedDict, total=False):
    """Determines whether CloudFront includes the ``Referrer-Policy`` HTTP
    response header and the header’s value.

    For more information about the ``Referrer-Policy`` HTTP response header,
    see
    `Referrer-Policy <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy>`__
    in the MDN Web Docs.
    """

    Override: boolean
    ReferrerPolicy: ReferrerPolicyList


class ResponseHeadersPolicyFrameOptions(TypedDict, total=False):
    """Determines whether CloudFront includes the ``X-Frame-Options`` HTTP
    response header and the header’s value.

    For more information about the ``X-Frame-Options`` HTTP response header,
    see
    `X-Frame-Options <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options>`__
    in the MDN Web Docs.
    """

    Override: boolean
    FrameOption: FrameOptionsList


class ResponseHeadersPolicyXSSProtection(TypedDict, total=False):
    """Determines whether CloudFront includes the ``X-XSS-Protection`` HTTP
    response header and the header’s value.

    For more information about the ``X-XSS-Protection`` HTTP response
    header, see
    `X-XSS-Protection <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection>`__
    in the MDN Web Docs.
    """

    Override: boolean
    Protection: boolean
    ModeBlock: Optional[boolean]
    ReportUri: Optional[string]


class ResponseHeadersPolicySecurityHeadersConfig(TypedDict, total=False):
    """A configuration for a set of security-related HTTP response headers.
    CloudFront adds these headers to HTTP responses that it sends for
    requests that match a cache behavior associated with this response
    headers policy.
    """

    XSSProtection: Optional[ResponseHeadersPolicyXSSProtection]
    FrameOptions: Optional[ResponseHeadersPolicyFrameOptions]
    ReferrerPolicy: Optional[ResponseHeadersPolicyReferrerPolicy]
    ContentSecurityPolicy: Optional[ResponseHeadersPolicyContentSecurityPolicy]
    ContentTypeOptions: Optional[ResponseHeadersPolicyContentTypeOptions]
    StrictTransportSecurity: Optional[ResponseHeadersPolicyStrictTransportSecurity]


class ResponseHeadersPolicyAccessControlExposeHeaders(TypedDict, total=False):
    """A list of HTTP headers that CloudFront includes as values for the
    ``Access-Control-Expose-Headers`` HTTP response header.

    For more information about the ``Access-Control-Expose-Headers`` HTTP
    response header, see
    `Access-Control-Expose-Headers <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers>`__
    in the MDN Web Docs.
    """

    Quantity: integer
    Items: Optional[AccessControlExposeHeadersList]


class ResponseHeadersPolicyAccessControlAllowMethods(TypedDict, total=False):
    """A list of HTTP methods that CloudFront includes as values for the
    ``Access-Control-Allow-Methods`` HTTP response header.

    For more information about the ``Access-Control-Allow-Methods`` HTTP
    response header, see
    `Access-Control-Allow-Methods <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Methods>`__
    in the MDN Web Docs.
    """

    Quantity: integer
    Items: AccessControlAllowMethodsList


class ResponseHeadersPolicyAccessControlAllowHeaders(TypedDict, total=False):
    """A list of HTTP header names that CloudFront includes as values for the
    ``Access-Control-Allow-Headers`` HTTP response header.

    For more information about the ``Access-Control-Allow-Headers`` HTTP
    response header, see
    `Access-Control-Allow-Headers <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers>`__
    in the MDN Web Docs.
    """

    Quantity: integer
    Items: AccessControlAllowHeadersList


class ResponseHeadersPolicyAccessControlAllowOrigins(TypedDict, total=False):
    """A list of origins (domain names) that CloudFront can use as the value
    for the ``Access-Control-Allow-Origin`` HTTP response header.

    For more information about the ``Access-Control-Allow-Origin`` HTTP
    response header, see
    `Access-Control-Allow-Origin <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin>`__
    in the MDN Web Docs.
    """

    Quantity: integer
    Items: AccessControlAllowOriginsList


class ResponseHeadersPolicyCorsConfig(TypedDict, total=False):
    """A configuration for a set of HTTP response headers that are used for
    cross-origin resource sharing (CORS). CloudFront adds these headers to
    HTTP responses that it sends for CORS requests that match a cache
    behavior associated with this response headers policy.

    For more information about CORS, see `Cross-Origin Resource Sharing
    (CORS) <https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`__ in
    the MDN Web Docs.
    """

    AccessControlAllowOrigins: ResponseHeadersPolicyAccessControlAllowOrigins
    AccessControlAllowHeaders: ResponseHeadersPolicyAccessControlAllowHeaders
    AccessControlAllowMethods: ResponseHeadersPolicyAccessControlAllowMethods
    AccessControlAllowCredentials: boolean
    AccessControlExposeHeaders: Optional[ResponseHeadersPolicyAccessControlExposeHeaders]
    AccessControlMaxAgeSec: Optional[integer]
    OriginOverride: boolean


class ResponseHeadersPolicyConfig(TypedDict, total=False):
    """A response headers policy configuration.

    A response headers policy configuration contains metadata about the
    response headers policy, and configurations for sets of HTTP response
    headers and their values. CloudFront adds the headers in the policy to
    HTTP responses that it sends for requests that match a cache behavior
    associated with the policy.
    """

    Comment: Optional[string]
    Name: string
    CorsConfig: Optional[ResponseHeadersPolicyCorsConfig]
    SecurityHeadersConfig: Optional[ResponseHeadersPolicySecurityHeadersConfig]
    CustomHeadersConfig: Optional[ResponseHeadersPolicyCustomHeadersConfig]
    ServerTimingHeadersConfig: Optional[ResponseHeadersPolicyServerTimingHeadersConfig]


class CreateResponseHeadersPolicyRequest(ServiceRequest):
    ResponseHeadersPolicyConfig: ResponseHeadersPolicyConfig


class ResponseHeadersPolicy(TypedDict, total=False):
    """A response headers policy.

    A response headers policy contains information about a set of HTTP
    response headers and their values.

    After you create a response headers policy, you can use its ID to attach
    it to one or more cache behaviors in a CloudFront distribution. When
    it’s attached to a cache behavior, CloudFront adds the headers in the
    policy to HTTP responses that it sends for requests that match the cache
    behavior.

    For more information, see `Adding HTTP headers to CloudFront
    responses <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/adding-response-headers.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Id: string
    LastModifiedTime: timestamp
    ResponseHeadersPolicyConfig: ResponseHeadersPolicyConfig


class CreateResponseHeadersPolicyResult(TypedDict, total=False):
    ResponseHeadersPolicy: Optional[ResponseHeadersPolicy]
    Location: Optional[string]
    ETag: Optional[string]


class StreamingLoggingConfig(TypedDict, total=False):
    """A complex type that controls whether access logs are written for this
    streaming distribution.
    """

    Enabled: boolean
    Bucket: string
    Prefix: string


class S3Origin(TypedDict, total=False):
    """A complex type that contains information about the Amazon S3 bucket from
    which you want CloudFront to get your media files for distribution.
    """

    DomainName: string
    OriginAccessIdentity: string


class StreamingDistributionConfig(TypedDict, total=False):
    """The RTMP distribution's configuration information."""

    CallerReference: string
    S3Origin: S3Origin
    Aliases: Optional[Aliases]
    Comment: string
    Logging: Optional[StreamingLoggingConfig]
    TrustedSigners: TrustedSigners
    PriceClass: Optional[PriceClass]
    Enabled: boolean


class CreateStreamingDistributionRequest(ServiceRequest):
    """The request to create a new streaming distribution."""

    StreamingDistributionConfig: StreamingDistributionConfig


class StreamingDistribution(TypedDict, total=False):
    """A streaming distribution tells CloudFront where you want RTMP content to
    be delivered from, and the details about how to track and manage content
    delivery.
    """

    Id: string
    ARN: string
    Status: string
    LastModifiedTime: Optional[timestamp]
    DomainName: string
    ActiveTrustedSigners: ActiveTrustedSigners
    StreamingDistributionConfig: StreamingDistributionConfig


class CreateStreamingDistributionResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    StreamingDistribution: Optional[StreamingDistribution]
    Location: Optional[string]
    ETag: Optional[string]


class StreamingDistributionConfigWithTags(TypedDict, total=False):
    """A streaming distribution Configuration and a list of tags to be
    associated with the streaming distribution.
    """

    StreamingDistributionConfig: StreamingDistributionConfig
    Tags: Tags


class CreateStreamingDistributionWithTagsRequest(ServiceRequest):
    """The request to create a new streaming distribution with tags."""

    StreamingDistributionConfigWithTags: StreamingDistributionConfigWithTags


class CreateStreamingDistributionWithTagsResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    StreamingDistribution: Optional[StreamingDistribution]
    Location: Optional[string]
    ETag: Optional[string]


class DeleteCachePolicyRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeleteCloudFrontOriginAccessIdentityRequest(ServiceRequest):
    """Deletes a origin access identity."""

    Id: string
    IfMatch: Optional[string]


class DeleteDistributionRequest(ServiceRequest):
    """This action deletes a web distribution. To delete a web distribution
    using the CloudFront API, perform the following steps.

    **To delete a web distribution using the CloudFront API:**

    #. Disable the web distribution

    #. Submit a ``GET Distribution Config`` request to get the current
       configuration and the ``Etag`` header for the distribution.

    #. Update the XML document that was returned in the response to your
       ``GET Distribution Config`` request to change the value of
       ``Enabled`` to ``false``.

    #. Submit a ``PUT Distribution Config`` request to update the
       configuration for your distribution. In the request body, include the
       XML document that you updated in Step 3. Set the value of the HTTP
       ``If-Match`` header to the value of the ``ETag`` header that
       CloudFront returned when you submitted the
       ``GET Distribution Config`` request in Step 2.

    #. Review the response to the ``PUT Distribution Config`` request to
       confirm that the distribution was successfully disabled.

    #. Submit a ``GET Distribution`` request to confirm that your changes
       have propagated. When propagation is complete, the value of
       ``Status`` is ``Deployed``.

    #. Submit a ``DELETE Distribution`` request. Set the value of the HTTP
       ``If-Match`` header to the value of the ``ETag`` header that
       CloudFront returned when you submitted the
       ``GET Distribution Config`` request in Step 6.

    #. Review the response to your ``DELETE Distribution`` request to
       confirm that the distribution was successfully deleted.

    For information about deleting a distribution using the CloudFront
    console, see `Deleting a
    Distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HowToDeleteDistribution.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Id: string
    IfMatch: Optional[string]


class DeleteFieldLevelEncryptionConfigRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeleteFieldLevelEncryptionProfileRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeleteFunctionRequest(ServiceRequest):
    Name: string
    IfMatch: string


class DeleteKeyGroupRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeleteMonitoringSubscriptionRequest(ServiceRequest):
    DistributionId: string


class DeleteMonitoringSubscriptionResult(TypedDict, total=False):
    pass


class DeleteOriginRequestPolicyRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeletePublicKeyRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeleteRealtimeLogConfigRequest(ServiceRequest):
    Name: Optional[string]
    ARN: Optional[string]


class DeleteResponseHeadersPolicyRequest(ServiceRequest):
    Id: string
    IfMatch: Optional[string]


class DeleteStreamingDistributionRequest(ServiceRequest):
    """The request to delete a streaming distribution."""

    Id: string
    IfMatch: Optional[string]


class DescribeFunctionRequest(ServiceRequest):
    Name: string
    Stage: Optional[FunctionStage]


class DescribeFunctionResult(TypedDict, total=False):
    FunctionSummary: Optional[FunctionSummary]
    ETag: Optional[string]


DistributionIdListSummary = List[string]


class DistributionIdList(TypedDict, total=False):
    """A list of distribution IDs."""

    Marker: string
    NextMarker: Optional[string]
    MaxItems: integer
    IsTruncated: boolean
    Quantity: integer
    Items: Optional[DistributionIdListSummary]


class DistributionSummary(TypedDict, total=False):
    """A summary of the information about a CloudFront distribution."""

    Id: string
    ARN: string
    Status: string
    LastModifiedTime: timestamp
    DomainName: string
    Aliases: Aliases
    Origins: Origins
    OriginGroups: Optional[OriginGroups]
    DefaultCacheBehavior: DefaultCacheBehavior
    CacheBehaviors: CacheBehaviors
    CustomErrorResponses: CustomErrorResponses
    Comment: string
    PriceClass: PriceClass
    Enabled: boolean
    ViewerCertificate: ViewerCertificate
    Restrictions: Restrictions
    WebACLId: string
    HttpVersion: HttpVersion
    IsIPV6Enabled: boolean
    AliasICPRecordals: Optional[AliasICPRecordals]


DistributionSummaryList = List[DistributionSummary]


class DistributionList(TypedDict, total=False):
    """A distribution list."""

    Marker: string
    NextMarker: Optional[string]
    MaxItems: integer
    IsTruncated: boolean
    Quantity: integer
    Items: Optional[DistributionSummaryList]


class FieldLevelEncryptionSummary(TypedDict, total=False):
    """A summary of a field-level encryption item."""

    Id: string
    LastModifiedTime: timestamp
    Comment: Optional[string]
    QueryArgProfileConfig: Optional[QueryArgProfileConfig]
    ContentTypeProfileConfig: Optional[ContentTypeProfileConfig]


FieldLevelEncryptionSummaryList = List[FieldLevelEncryptionSummary]


class FieldLevelEncryptionList(TypedDict, total=False):
    """List of field-level encrpytion configurations."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[FieldLevelEncryptionSummaryList]


class FieldLevelEncryptionProfileSummary(TypedDict, total=False):
    """The field-level encryption profile summary."""

    Id: string
    LastModifiedTime: timestamp
    Name: string
    EncryptionEntities: EncryptionEntities
    Comment: Optional[string]


FieldLevelEncryptionProfileSummaryList = List[FieldLevelEncryptionProfileSummary]


class FieldLevelEncryptionProfileList(TypedDict, total=False):
    """List of field-level encryption profiles."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[FieldLevelEncryptionProfileSummaryList]


FunctionEventObject = bytes
FunctionExecutionLogList = List[string]
FunctionSummaryList = List[FunctionSummary]


class FunctionList(TypedDict, total=False):
    """A list of CloudFront functions."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[FunctionSummaryList]


class GetCachePolicyConfigRequest(ServiceRequest):
    Id: string


class GetCachePolicyConfigResult(TypedDict, total=False):
    CachePolicyConfig: Optional[CachePolicyConfig]
    ETag: Optional[string]


class GetCachePolicyRequest(ServiceRequest):
    Id: string


class GetCachePolicyResult(TypedDict, total=False):
    CachePolicy: Optional[CachePolicy]
    ETag: Optional[string]


class GetCloudFrontOriginAccessIdentityConfigRequest(ServiceRequest):
    """The origin access identity's configuration information. For more
    information, see
    `CloudFrontOriginAccessIdentityConfig <https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CloudFrontOriginAccessIdentityConfig.html>`__.
    """

    Id: string


class GetCloudFrontOriginAccessIdentityConfigResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    CloudFrontOriginAccessIdentityConfig: Optional[CloudFrontOriginAccessIdentityConfig]
    ETag: Optional[string]


class GetCloudFrontOriginAccessIdentityRequest(ServiceRequest):
    """The request to get an origin access identity's information."""

    Id: string


class GetCloudFrontOriginAccessIdentityResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    CloudFrontOriginAccessIdentity: Optional[CloudFrontOriginAccessIdentity]
    ETag: Optional[string]


class GetDistributionConfigRequest(ServiceRequest):
    """The request to get a distribution configuration."""

    Id: string


class GetDistributionConfigResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    DistributionConfig: Optional[DistributionConfig]
    ETag: Optional[string]


class GetDistributionRequest(ServiceRequest):
    """The request to get a distribution's information."""

    Id: string


class GetDistributionResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Distribution: Optional[Distribution]
    ETag: Optional[string]


class GetFieldLevelEncryptionConfigRequest(ServiceRequest):
    Id: string


class GetFieldLevelEncryptionConfigResult(TypedDict, total=False):
    FieldLevelEncryptionConfig: Optional[FieldLevelEncryptionConfig]
    ETag: Optional[string]


class GetFieldLevelEncryptionProfileConfigRequest(ServiceRequest):
    Id: string


class GetFieldLevelEncryptionProfileConfigResult(TypedDict, total=False):
    FieldLevelEncryptionProfileConfig: Optional[FieldLevelEncryptionProfileConfig]
    ETag: Optional[string]


class GetFieldLevelEncryptionProfileRequest(ServiceRequest):
    Id: string


class GetFieldLevelEncryptionProfileResult(TypedDict, total=False):
    FieldLevelEncryptionProfile: Optional[FieldLevelEncryptionProfile]
    ETag: Optional[string]


class GetFieldLevelEncryptionRequest(ServiceRequest):
    Id: string


class GetFieldLevelEncryptionResult(TypedDict, total=False):
    FieldLevelEncryption: Optional[FieldLevelEncryption]
    ETag: Optional[string]


class GetFunctionRequest(ServiceRequest):
    Name: string
    Stage: Optional[FunctionStage]


class GetFunctionResult(TypedDict, total=False):
    FunctionCode: Optional[FunctionBlob]
    ETag: Optional[string]
    ContentType: Optional[string]


class GetInvalidationRequest(ServiceRequest):
    """The request to get an invalidation's information."""

    DistributionId: string
    Id: string


class GetInvalidationResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Invalidation: Optional[Invalidation]


class GetKeyGroupConfigRequest(ServiceRequest):
    Id: string


class GetKeyGroupConfigResult(TypedDict, total=False):
    KeyGroupConfig: Optional[KeyGroupConfig]
    ETag: Optional[string]


class GetKeyGroupRequest(ServiceRequest):
    Id: string


class GetKeyGroupResult(TypedDict, total=False):
    KeyGroup: Optional[KeyGroup]
    ETag: Optional[string]


class GetMonitoringSubscriptionRequest(ServiceRequest):
    DistributionId: string


class GetMonitoringSubscriptionResult(TypedDict, total=False):
    MonitoringSubscription: Optional[MonitoringSubscription]


class GetOriginRequestPolicyConfigRequest(ServiceRequest):
    Id: string


class GetOriginRequestPolicyConfigResult(TypedDict, total=False):
    OriginRequestPolicyConfig: Optional[OriginRequestPolicyConfig]
    ETag: Optional[string]


class GetOriginRequestPolicyRequest(ServiceRequest):
    Id: string


class GetOriginRequestPolicyResult(TypedDict, total=False):
    OriginRequestPolicy: Optional[OriginRequestPolicy]
    ETag: Optional[string]


class GetPublicKeyConfigRequest(ServiceRequest):
    Id: string


class GetPublicKeyConfigResult(TypedDict, total=False):
    PublicKeyConfig: Optional[PublicKeyConfig]
    ETag: Optional[string]


class GetPublicKeyRequest(ServiceRequest):
    Id: string


class GetPublicKeyResult(TypedDict, total=False):
    PublicKey: Optional[PublicKey]
    ETag: Optional[string]


class GetRealtimeLogConfigRequest(ServiceRequest):
    Name: Optional[string]
    ARN: Optional[string]


class GetRealtimeLogConfigResult(TypedDict, total=False):
    RealtimeLogConfig: Optional[RealtimeLogConfig]


class GetResponseHeadersPolicyConfigRequest(ServiceRequest):
    Id: string


class GetResponseHeadersPolicyConfigResult(TypedDict, total=False):
    ResponseHeadersPolicyConfig: Optional[ResponseHeadersPolicyConfig]
    ETag: Optional[string]


class GetResponseHeadersPolicyRequest(ServiceRequest):
    Id: string


class GetResponseHeadersPolicyResult(TypedDict, total=False):
    ResponseHeadersPolicy: Optional[ResponseHeadersPolicy]
    ETag: Optional[string]


class GetStreamingDistributionConfigRequest(ServiceRequest):
    """To request to get a streaming distribution configuration."""

    Id: string


class GetStreamingDistributionConfigResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    StreamingDistributionConfig: Optional[StreamingDistributionConfig]
    ETag: Optional[string]


class GetStreamingDistributionRequest(ServiceRequest):
    """The request to get a streaming distribution's information."""

    Id: string


class GetStreamingDistributionResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    StreamingDistribution: Optional[StreamingDistribution]
    ETag: Optional[string]


class InvalidationSummary(TypedDict, total=False):
    """A summary of an invalidation request."""

    Id: string
    CreateTime: timestamp
    Status: string


InvalidationSummaryList = List[InvalidationSummary]


class InvalidationList(TypedDict, total=False):
    """The ``InvalidationList`` complex type describes the list of invalidation
    objects. For more information about invalidation, see `Invalidating
    Objects (Web Distributions
    Only) <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html>`__
    in the *Amazon CloudFront Developer Guide*.
    """

    Marker: string
    NextMarker: Optional[string]
    MaxItems: integer
    IsTruncated: boolean
    Quantity: integer
    Items: Optional[InvalidationSummaryList]


class KeyGroupSummary(TypedDict, total=False):
    """Contains information about a key group."""

    KeyGroup: KeyGroup


KeyGroupSummaryList = List[KeyGroupSummary]


class KeyGroupList(TypedDict, total=False):
    """A list of key groups."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[KeyGroupSummaryList]


class ListCachePoliciesRequest(ServiceRequest):
    Type: Optional[CachePolicyType]
    Marker: Optional[string]
    MaxItems: Optional[string]


class ListCachePoliciesResult(TypedDict, total=False):
    CachePolicyList: Optional[CachePolicyList]


class ListCloudFrontOriginAccessIdentitiesRequest(ServiceRequest):
    """The request to list origin access identities."""

    Marker: Optional[string]
    MaxItems: Optional[string]


class ListCloudFrontOriginAccessIdentitiesResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    CloudFrontOriginAccessIdentityList: Optional[CloudFrontOriginAccessIdentityList]


class ListConflictingAliasesRequest(ServiceRequest):
    DistributionId: distributionIdString
    Alias: aliasString
    Marker: Optional[string]
    MaxItems: Optional[listConflictingAliasesMaxItemsInteger]


class ListConflictingAliasesResult(TypedDict, total=False):
    ConflictingAliasesList: Optional[ConflictingAliasesList]


class ListDistributionsByCachePolicyIdRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]
    CachePolicyId: string


class ListDistributionsByCachePolicyIdResult(TypedDict, total=False):
    DistributionIdList: Optional[DistributionIdList]


class ListDistributionsByKeyGroupRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]
    KeyGroupId: string


class ListDistributionsByKeyGroupResult(TypedDict, total=False):
    DistributionIdList: Optional[DistributionIdList]


class ListDistributionsByOriginRequestPolicyIdRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]
    OriginRequestPolicyId: string


class ListDistributionsByOriginRequestPolicyIdResult(TypedDict, total=False):
    DistributionIdList: Optional[DistributionIdList]


class ListDistributionsByRealtimeLogConfigRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]
    RealtimeLogConfigName: Optional[string]
    RealtimeLogConfigArn: Optional[string]


class ListDistributionsByRealtimeLogConfigResult(TypedDict, total=False):
    DistributionList: Optional[DistributionList]


class ListDistributionsByResponseHeadersPolicyIdRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]
    ResponseHeadersPolicyId: string


class ListDistributionsByResponseHeadersPolicyIdResult(TypedDict, total=False):
    DistributionIdList: Optional[DistributionIdList]


class ListDistributionsByWebACLIdRequest(ServiceRequest):
    """The request to list distributions that are associated with a specified
    WAF web ACL.
    """

    Marker: Optional[string]
    MaxItems: Optional[string]
    WebACLId: string


class ListDistributionsByWebACLIdResult(TypedDict, total=False):
    """The response to a request to list the distributions that are associated
    with a specified WAF web ACL.
    """

    DistributionList: Optional[DistributionList]


class ListDistributionsRequest(ServiceRequest):
    """The request to list your distributions."""

    Marker: Optional[string]
    MaxItems: Optional[string]


class ListDistributionsResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    DistributionList: Optional[DistributionList]


class ListFieldLevelEncryptionConfigsRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]


class ListFieldLevelEncryptionConfigsResult(TypedDict, total=False):
    FieldLevelEncryptionList: Optional[FieldLevelEncryptionList]


class ListFieldLevelEncryptionProfilesRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]


class ListFieldLevelEncryptionProfilesResult(TypedDict, total=False):
    FieldLevelEncryptionProfileList: Optional[FieldLevelEncryptionProfileList]


class ListFunctionsRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]
    Stage: Optional[FunctionStage]


class ListFunctionsResult(TypedDict, total=False):
    FunctionList: Optional[FunctionList]


class ListInvalidationsRequest(ServiceRequest):
    """The request to list invalidations."""

    DistributionId: string
    Marker: Optional[string]
    MaxItems: Optional[string]


class ListInvalidationsResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    InvalidationList: Optional[InvalidationList]


class ListKeyGroupsRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]


class ListKeyGroupsResult(TypedDict, total=False):
    KeyGroupList: Optional[KeyGroupList]


class ListOriginRequestPoliciesRequest(ServiceRequest):
    Type: Optional[OriginRequestPolicyType]
    Marker: Optional[string]
    MaxItems: Optional[string]


class OriginRequestPolicySummary(TypedDict, total=False):
    """Contains an origin request policy."""

    Type: OriginRequestPolicyType
    OriginRequestPolicy: OriginRequestPolicy


OriginRequestPolicySummaryList = List[OriginRequestPolicySummary]


class OriginRequestPolicyList(TypedDict, total=False):
    """A list of origin request policies."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[OriginRequestPolicySummaryList]


class ListOriginRequestPoliciesResult(TypedDict, total=False):
    OriginRequestPolicyList: Optional[OriginRequestPolicyList]


class ListPublicKeysRequest(ServiceRequest):
    Marker: Optional[string]
    MaxItems: Optional[string]


class PublicKeySummary(TypedDict, total=False):
    """Contains information about a public key."""

    Id: string
    Name: string
    CreatedTime: timestamp
    EncodedKey: string
    Comment: Optional[string]


PublicKeySummaryList = List[PublicKeySummary]


class PublicKeyList(TypedDict, total=False):
    """A list of public keys that you can use with `signed URLs and signed
    cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__,
    or with `field-level
    encryption <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/field-level-encryption.html>`__.
    """

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[PublicKeySummaryList]


class ListPublicKeysResult(TypedDict, total=False):
    PublicKeyList: Optional[PublicKeyList]


class ListRealtimeLogConfigsRequest(ServiceRequest):
    MaxItems: Optional[string]
    Marker: Optional[string]


RealtimeLogConfigList = List[RealtimeLogConfig]


class RealtimeLogConfigs(TypedDict, total=False):
    """A list of real-time log configurations."""

    MaxItems: integer
    Items: Optional[RealtimeLogConfigList]
    IsTruncated: boolean
    Marker: string
    NextMarker: Optional[string]


class ListRealtimeLogConfigsResult(TypedDict, total=False):
    RealtimeLogConfigs: Optional[RealtimeLogConfigs]


class ListResponseHeadersPoliciesRequest(ServiceRequest):
    Type: Optional[ResponseHeadersPolicyType]
    Marker: Optional[string]
    MaxItems: Optional[string]


class ResponseHeadersPolicySummary(TypedDict, total=False):
    """Contains a response headers policy."""

    Type: ResponseHeadersPolicyType
    ResponseHeadersPolicy: ResponseHeadersPolicy


ResponseHeadersPolicySummaryList = List[ResponseHeadersPolicySummary]


class ResponseHeadersPolicyList(TypedDict, total=False):
    """A list of response headers policies."""

    NextMarker: Optional[string]
    MaxItems: integer
    Quantity: integer
    Items: Optional[ResponseHeadersPolicySummaryList]


class ListResponseHeadersPoliciesResult(TypedDict, total=False):
    ResponseHeadersPolicyList: Optional[ResponseHeadersPolicyList]


class ListStreamingDistributionsRequest(ServiceRequest):
    """The request to list your streaming distributions."""

    Marker: Optional[string]
    MaxItems: Optional[string]


class StreamingDistributionSummary(TypedDict, total=False):
    """A summary of the information for a CloudFront streaming distribution."""

    Id: string
    ARN: string
    Status: string
    LastModifiedTime: timestamp
    DomainName: string
    S3Origin: S3Origin
    Aliases: Aliases
    TrustedSigners: TrustedSigners
    Comment: string
    PriceClass: PriceClass
    Enabled: boolean


StreamingDistributionSummaryList = List[StreamingDistributionSummary]


class StreamingDistributionList(TypedDict, total=False):
    """A streaming distribution list."""

    Marker: string
    NextMarker: Optional[string]
    MaxItems: integer
    IsTruncated: boolean
    Quantity: integer
    Items: Optional[StreamingDistributionSummaryList]


class ListStreamingDistributionsResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    StreamingDistributionList: Optional[StreamingDistributionList]


class ListTagsForResourceRequest(ServiceRequest):
    """The request to list tags for a CloudFront resource."""

    Resource: ResourceARN


class ListTagsForResourceResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Tags: Tags


class PublishFunctionRequest(ServiceRequest):
    Name: string
    IfMatch: string


class PublishFunctionResult(TypedDict, total=False):
    FunctionSummary: Optional[FunctionSummary]


TagKeyList = List[TagKey]


class TagKeys(TypedDict, total=False):
    """A complex type that contains zero or more ``Tag`` elements."""

    Items: Optional[TagKeyList]


class TagResourceRequest(ServiceRequest):
    """The request to add tags to a CloudFront resource."""

    Resource: ResourceARN
    Tags: Tags


class TestFunctionRequest(ServiceRequest):
    Name: string
    IfMatch: string
    Stage: Optional[FunctionStage]
    EventObject: FunctionEventObject


class TestResult(TypedDict, total=False):
    """Contains the result of testing a CloudFront function with
    ``TestFunction``.
    """

    FunctionSummary: Optional[FunctionSummary]
    ComputeUtilization: Optional[string]
    FunctionExecutionLogs: Optional[FunctionExecutionLogList]
    FunctionErrorMessage: Optional[sensitiveStringType]
    FunctionOutput: Optional[sensitiveStringType]


class TestFunctionResult(TypedDict, total=False):
    TestResult: Optional[TestResult]


class UntagResourceRequest(ServiceRequest):
    """The request to remove tags from a CloudFront resource."""

    Resource: ResourceARN
    TagKeys: TagKeys


class UpdateCachePolicyRequest(ServiceRequest):
    CachePolicyConfig: CachePolicyConfig
    Id: string
    IfMatch: Optional[string]


class UpdateCachePolicyResult(TypedDict, total=False):
    CachePolicy: Optional[CachePolicy]
    ETag: Optional[string]


class UpdateCloudFrontOriginAccessIdentityRequest(ServiceRequest):
    """The request to update an origin access identity."""

    CloudFrontOriginAccessIdentityConfig: CloudFrontOriginAccessIdentityConfig
    Id: string
    IfMatch: Optional[string]


class UpdateCloudFrontOriginAccessIdentityResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    CloudFrontOriginAccessIdentity: Optional[CloudFrontOriginAccessIdentity]
    ETag: Optional[string]


class UpdateDistributionRequest(ServiceRequest):
    """The request to update a distribution."""

    DistributionConfig: DistributionConfig
    Id: string
    IfMatch: Optional[string]


class UpdateDistributionResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    Distribution: Optional[Distribution]
    ETag: Optional[string]


class UpdateFieldLevelEncryptionConfigRequest(ServiceRequest):
    FieldLevelEncryptionConfig: FieldLevelEncryptionConfig
    Id: string
    IfMatch: Optional[string]


class UpdateFieldLevelEncryptionConfigResult(TypedDict, total=False):
    FieldLevelEncryption: Optional[FieldLevelEncryption]
    ETag: Optional[string]


class UpdateFieldLevelEncryptionProfileRequest(ServiceRequest):
    FieldLevelEncryptionProfileConfig: FieldLevelEncryptionProfileConfig
    Id: string
    IfMatch: Optional[string]


class UpdateFieldLevelEncryptionProfileResult(TypedDict, total=False):
    FieldLevelEncryptionProfile: Optional[FieldLevelEncryptionProfile]
    ETag: Optional[string]


class UpdateFunctionRequest(ServiceRequest):
    Name: string
    IfMatch: string
    FunctionConfig: FunctionConfig
    FunctionCode: FunctionBlob


class UpdateFunctionResult(TypedDict, total=False):
    FunctionSummary: Optional[FunctionSummary]
    ETag: Optional[string]


class UpdateKeyGroupRequest(ServiceRequest):
    KeyGroupConfig: KeyGroupConfig
    Id: string
    IfMatch: Optional[string]


class UpdateKeyGroupResult(TypedDict, total=False):
    KeyGroup: Optional[KeyGroup]
    ETag: Optional[string]


class UpdateOriginRequestPolicyRequest(ServiceRequest):
    OriginRequestPolicyConfig: OriginRequestPolicyConfig
    Id: string
    IfMatch: Optional[string]


class UpdateOriginRequestPolicyResult(TypedDict, total=False):
    OriginRequestPolicy: Optional[OriginRequestPolicy]
    ETag: Optional[string]


class UpdatePublicKeyRequest(ServiceRequest):
    PublicKeyConfig: PublicKeyConfig
    Id: string
    IfMatch: Optional[string]


class UpdatePublicKeyResult(TypedDict, total=False):
    PublicKey: Optional[PublicKey]
    ETag: Optional[string]


class UpdateRealtimeLogConfigRequest(ServiceRequest):
    EndPoints: Optional[EndPointList]
    Fields: Optional[FieldList]
    Name: Optional[string]
    ARN: Optional[string]
    SamplingRate: Optional[long]


class UpdateRealtimeLogConfigResult(TypedDict, total=False):
    RealtimeLogConfig: Optional[RealtimeLogConfig]


class UpdateResponseHeadersPolicyRequest(ServiceRequest):
    ResponseHeadersPolicyConfig: ResponseHeadersPolicyConfig
    Id: string
    IfMatch: Optional[string]


class UpdateResponseHeadersPolicyResult(TypedDict, total=False):
    ResponseHeadersPolicy: Optional[ResponseHeadersPolicy]
    ETag: Optional[string]


class UpdateStreamingDistributionRequest(ServiceRequest):
    """The request to update a streaming distribution."""

    StreamingDistributionConfig: StreamingDistributionConfig
    Id: string
    IfMatch: Optional[string]


class UpdateStreamingDistributionResult(TypedDict, total=False):
    """The returned result of the corresponding request."""

    StreamingDistribution: Optional[StreamingDistribution]
    ETag: Optional[string]


class CloudfrontApi:

    service = "cloudfront"
    version = "2020-05-31"

    @handler("AssociateAlias")
    def associate_alias(
        self, context: RequestContext, target_distribution_id: string, alias: string
    ) -> None:
        """Associates an alias (also known as a CNAME or an alternate domain name)
        with a CloudFront distribution.

        With this operation you can move an alias that’s already in use on a
        CloudFront distribution to a different distribution in one step. This
        prevents the downtime that could occur if you first remove the alias
        from one distribution and then separately add the alias to another
        distribution.

        To use this operation to associate an alias with a distribution, you
        provide the alias and the ID of the target distribution for the alias.
        For more information, including how to set up the target distribution,
        prerequisites that you must complete, and other restrictions, see
        `Moving an alternate domain name to a different
        distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html#alternate-domain-names-move>`__
        in the *Amazon CloudFront Developer Guide*.

        :param target_distribution_id: The ID of the distribution that you’re associating the alias with.
        :param alias: The alias (also known as a CNAME) to add to the target distribution.
        :raises InvalidArgument:
        :raises NoSuchDistribution:
        :raises TooManyDistributionCNAMEs:
        :raises IllegalUpdate:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("CreateCachePolicy")
    def create_cache_policy(
        self, context: RequestContext, cache_policy_config: CachePolicyConfig
    ) -> CreateCachePolicyResult:
        """Creates a cache policy.

        After you create a cache policy, you can attach it to one or more cache
        behaviors. When it’s attached to a cache behavior, the cache policy
        determines the following:

        -  The values that CloudFront includes in the *cache key*. These values
           can include HTTP headers, cookies, and URL query strings. CloudFront
           uses the cache key to find an object in its cache that it can return
           to the viewer.

        -  The default, minimum, and maximum time to live (TTL) values that you
           want objects to stay in the CloudFront cache.

        The headers, cookies, and query strings that are included in the cache
        key are automatically included in requests that CloudFront sends to the
        origin. CloudFront sends a request when it can’t find an object in its
        cache that matches the request’s cache key. If you want to send values
        to the origin but *not* include them in the cache key, use
        ``OriginRequestPolicy``.

        For more information about cache policies, see `Controlling the cache
        key <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param cache_policy_config: A cache policy configuration.
        :returns: CreateCachePolicyResult
        :raises AccessDenied:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises CachePolicyAlreadyExists:
        :raises TooManyCachePolicies:
        :raises TooManyHeadersInCachePolicy:
        :raises TooManyCookiesInCachePolicy:
        :raises TooManyQueryStringsInCachePolicy:
        """
        raise NotImplementedError

    @handler("CreateCloudFrontOriginAccessIdentity")
    def create_cloud_front_origin_access_identity(
        self,
        context: RequestContext,
        cloud_front_origin_access_identity_config: CloudFrontOriginAccessIdentityConfig,
    ) -> CreateCloudFrontOriginAccessIdentityResult:
        """Creates a new origin access identity. If you're using Amazon S3 for your
        origin, you can use an origin access identity to require users to access
        your content using a CloudFront URL instead of the Amazon S3 URL. For
        more information about how to use origin access identities, see `Serving
        Private Content through
        CloudFront <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param cloud_front_origin_access_identity_config: The current configuration information for the identity.
        :returns: CreateCloudFrontOriginAccessIdentityResult
        :raises CloudFrontOriginAccessIdentityAlreadyExists:
        :raises MissingBody:
        :raises TooManyCloudFrontOriginAccessIdentities:
        :raises InvalidArgument:
        :raises InconsistentQuantities:
        """
        raise NotImplementedError

    @handler("CreateDistribution")
    def create_distribution(
        self, context: RequestContext, distribution_config: DistributionConfig
    ) -> CreateDistributionResult:
        """Creates a new web distribution. You create a CloudFront distribution to
        tell CloudFront where you want content to be delivered from, and the
        details about how to track and manage content delivery. Send a ``POST``
        request to the
        ``/CloudFront API version/distribution``/``distribution ID`` resource.

        When you update a distribution, there are more required fields than when
        you create a distribution. When you update your distribution by using
        `UpdateDistribution <https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_UpdateDistribution.html>`__,
        follow the steps included in the documentation to get the current
        configuration and then make your updates. This helps to make sure that
        you include all of the required fields. To view a summary, see `Required
        Fields for Create Distribution and Update
        Distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-overview-required-fields.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param distribution_config: The distribution's configuration information.
        :returns: CreateDistributionResult
        :raises CNAMEAlreadyExists:
        :raises DistributionAlreadyExists:
        :raises InvalidOrigin:
        :raises InvalidOriginAccessIdentity:
        :raises AccessDenied:
        :raises TooManyTrustedSigners:
        :raises TrustedSignerDoesNotExist:
        :raises InvalidViewerCertificate:
        :raises InvalidMinimumProtocolVersion:
        :raises MissingBody:
        :raises TooManyDistributionCNAMEs:
        :raises TooManyDistributions:
        :raises InvalidDefaultRootObject:
        :raises InvalidRelativePath:
        :raises InvalidErrorCode:
        :raises InvalidResponseCode:
        :raises InvalidArgument:
        :raises InvalidRequiredProtocol:
        :raises NoSuchOrigin:
        :raises TooManyOrigins:
        :raises TooManyOriginGroupsPerDistribution:
        :raises TooManyCacheBehaviors:
        :raises TooManyCookieNamesInWhiteList:
        :raises InvalidForwardCookies:
        :raises TooManyHeadersInForwardedValues:
        :raises InvalidHeadersForS3Origin:
        :raises InconsistentQuantities:
        :raises TooManyCertificates:
        :raises InvalidLocationCode:
        :raises InvalidGeoRestrictionParameter:
        :raises InvalidProtocolSettings:
        :raises InvalidTTLOrder:
        :raises InvalidWebACLId:
        :raises TooManyOriginCustomHeaders:
        :raises TooManyQueryStringParameters:
        :raises InvalidQueryStringParameters:
        :raises TooManyDistributionsWithLambdaAssociations:
        :raises TooManyDistributionsWithSingleFunctionARN:
        :raises TooManyLambdaFunctionAssociations:
        :raises InvalidLambdaFunctionAssociation:
        :raises TooManyDistributionsWithFunctionAssociations:
        :raises TooManyFunctionAssociations:
        :raises InvalidFunctionAssociation:
        :raises InvalidOriginReadTimeout:
        :raises InvalidOriginKeepaliveTimeout:
        :raises NoSuchFieldLevelEncryptionConfig:
        :raises IllegalFieldLevelEncryptionConfigAssociationWithCacheBehavior:
        :raises TooManyDistributionsAssociatedToFieldLevelEncryptionConfig:
        :raises NoSuchCachePolicy:
        :raises TooManyDistributionsAssociatedToCachePolicy:
        :raises NoSuchResponseHeadersPolicy:
        :raises TooManyDistributionsAssociatedToResponseHeadersPolicy:
        :raises NoSuchOriginRequestPolicy:
        :raises TooManyDistributionsAssociatedToOriginRequestPolicy:
        :raises TooManyDistributionsAssociatedToKeyGroup:
        :raises TooManyKeyGroupsAssociatedToDistribution:
        :raises TrustedKeyGroupDoesNotExist:
        :raises NoSuchRealtimeLogConfig:
        :raises RealtimeLogConfigOwnerMismatch:
        """
        raise NotImplementedError

    @handler("CreateDistributionWithTags")
    def create_distribution_with_tags(
        self, context: RequestContext, distribution_config_with_tags: DistributionConfigWithTags
    ) -> CreateDistributionWithTagsResult:
        """Create a new distribution with tags.

        :param distribution_config_with_tags: The distribution's configuration information.
        :returns: CreateDistributionWithTagsResult
        :raises CNAMEAlreadyExists:
        :raises DistributionAlreadyExists:
        :raises InvalidOrigin:
        :raises InvalidOriginAccessIdentity:
        :raises AccessDenied:
        :raises TooManyTrustedSigners:
        :raises TrustedSignerDoesNotExist:
        :raises InvalidViewerCertificate:
        :raises InvalidMinimumProtocolVersion:
        :raises MissingBody:
        :raises TooManyDistributionCNAMEs:
        :raises TooManyDistributions:
        :raises InvalidDefaultRootObject:
        :raises InvalidRelativePath:
        :raises InvalidErrorCode:
        :raises InvalidResponseCode:
        :raises InvalidArgument:
        :raises InvalidRequiredProtocol:
        :raises NoSuchOrigin:
        :raises TooManyOrigins:
        :raises TooManyOriginGroupsPerDistribution:
        :raises TooManyCacheBehaviors:
        :raises TooManyCookieNamesInWhiteList:
        :raises InvalidForwardCookies:
        :raises TooManyHeadersInForwardedValues:
        :raises InvalidHeadersForS3Origin:
        :raises InconsistentQuantities:
        :raises TooManyCertificates:
        :raises InvalidLocationCode:
        :raises InvalidGeoRestrictionParameter:
        :raises InvalidProtocolSettings:
        :raises InvalidTTLOrder:
        :raises InvalidWebACLId:
        :raises TooManyOriginCustomHeaders:
        :raises InvalidTagging:
        :raises TooManyQueryStringParameters:
        :raises InvalidQueryStringParameters:
        :raises TooManyDistributionsWithLambdaAssociations:
        :raises TooManyDistributionsWithSingleFunctionARN:
        :raises TooManyLambdaFunctionAssociations:
        :raises InvalidLambdaFunctionAssociation:
        :raises TooManyDistributionsWithFunctionAssociations:
        :raises TooManyFunctionAssociations:
        :raises InvalidFunctionAssociation:
        :raises InvalidOriginReadTimeout:
        :raises InvalidOriginKeepaliveTimeout:
        :raises NoSuchFieldLevelEncryptionConfig:
        :raises IllegalFieldLevelEncryptionConfigAssociationWithCacheBehavior:
        :raises TooManyDistributionsAssociatedToFieldLevelEncryptionConfig:
        :raises NoSuchCachePolicy:
        :raises TooManyDistributionsAssociatedToCachePolicy:
        :raises NoSuchResponseHeadersPolicy:
        :raises TooManyDistributionsAssociatedToResponseHeadersPolicy:
        :raises NoSuchOriginRequestPolicy:
        :raises TooManyDistributionsAssociatedToOriginRequestPolicy:
        :raises TooManyDistributionsAssociatedToKeyGroup:
        :raises TooManyKeyGroupsAssociatedToDistribution:
        :raises TrustedKeyGroupDoesNotExist:
        :raises NoSuchRealtimeLogConfig:
        :raises RealtimeLogConfigOwnerMismatch:
        """
        raise NotImplementedError

    @handler("CreateFieldLevelEncryptionConfig")
    def create_field_level_encryption_config(
        self, context: RequestContext, field_level_encryption_config: FieldLevelEncryptionConfig
    ) -> CreateFieldLevelEncryptionConfigResult:
        """Create a new field-level encryption configuration.

        :param field_level_encryption_config: The request to create a new field-level encryption configuration.
        :returns: CreateFieldLevelEncryptionConfigResult
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises NoSuchFieldLevelEncryptionProfile:
        :raises FieldLevelEncryptionConfigAlreadyExists:
        :raises TooManyFieldLevelEncryptionConfigs:
        :raises TooManyFieldLevelEncryptionQueryArgProfiles:
        :raises TooManyFieldLevelEncryptionContentTypeProfiles:
        :raises QueryArgProfileEmpty:
        """
        raise NotImplementedError

    @handler("CreateFieldLevelEncryptionProfile")
    def create_field_level_encryption_profile(
        self,
        context: RequestContext,
        field_level_encryption_profile_config: FieldLevelEncryptionProfileConfig,
    ) -> CreateFieldLevelEncryptionProfileResult:
        """Create a field-level encryption profile.

        :param field_level_encryption_profile_config: The request to create a field-level encryption profile.
        :returns: CreateFieldLevelEncryptionProfileResult
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises NoSuchPublicKey:
        :raises FieldLevelEncryptionProfileAlreadyExists:
        :raises FieldLevelEncryptionProfileSizeExceeded:
        :raises TooManyFieldLevelEncryptionProfiles:
        :raises TooManyFieldLevelEncryptionEncryptionEntities:
        :raises TooManyFieldLevelEncryptionFieldPatterns:
        """
        raise NotImplementedError

    @handler("CreateFunction")
    def create_function(
        self,
        context: RequestContext,
        name: FunctionName,
        function_config: FunctionConfig,
        function_code: FunctionBlob,
    ) -> CreateFunctionResult:
        """Creates a CloudFront function.

        To create a function, you provide the function code and some
        configuration information about the function. The response contains an
        Amazon Resource Name (ARN) that uniquely identifies the function.

        When you create a function, it’s in the ``DEVELOPMENT`` stage. In this
        stage, you can test the function with ``TestFunction``, and update it
        with ``UpdateFunction``.

        When you’re ready to use your function with a CloudFront distribution,
        use ``PublishFunction`` to copy the function from the ``DEVELOPMENT``
        stage to ``LIVE``. When it’s live, you can attach the function to a
        distribution’s cache behavior, using the function’s ARN.

        :param name: A name to identify the function.
        :param function_config: Configuration information about the function, including an optional
        comment and the function’s runtime.
        :param function_code: The function code.
        :returns: CreateFunctionResult
        :raises TooManyFunctions:
        :raises FunctionAlreadyExists:
        :raises FunctionSizeLimitExceeded:
        :raises InvalidArgument:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("CreateInvalidation")
    def create_invalidation(
        self,
        context: RequestContext,
        distribution_id: string,
        invalidation_batch: InvalidationBatch,
    ) -> CreateInvalidationResult:
        """Create a new invalidation.

        :param distribution_id: The distribution's id.
        :param invalidation_batch: The batch information for the invalidation.
        :returns: CreateInvalidationResult
        :raises AccessDenied:
        :raises MissingBody:
        :raises InvalidArgument:
        :raises NoSuchDistribution:
        :raises BatchTooLarge:
        :raises TooManyInvalidationsInProgress:
        :raises InconsistentQuantities:
        """
        raise NotImplementedError

    @handler("CreateKeyGroup")
    def create_key_group(
        self, context: RequestContext, key_group_config: KeyGroupConfig
    ) -> CreateKeyGroupResult:
        """Creates a key group that you can use with `CloudFront signed URLs and
        signed
        cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__.

        To create a key group, you must specify at least one public key for the
        key group. After you create a key group, you can reference it from one
        or more cache behaviors. When you reference a key group in a cache
        behavior, CloudFront requires signed URLs or signed cookies for all
        requests that match the cache behavior. The URLs or cookies must be
        signed with a private key whose corresponding public key is in the key
        group. The signed URL or cookie contains information about which public
        key CloudFront should use to verify the signature. For more information,
        see `Serving private
        content <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param key_group_config: A key group configuration.
        :returns: CreateKeyGroupResult
        :raises InvalidArgument:
        :raises KeyGroupAlreadyExists:
        :raises TooManyKeyGroups:
        :raises TooManyPublicKeysInKeyGroup:
        """
        raise NotImplementedError

    @handler("CreateMonitoringSubscription")
    def create_monitoring_subscription(
        self,
        context: RequestContext,
        monitoring_subscription: MonitoringSubscription,
        distribution_id: string,
    ) -> CreateMonitoringSubscriptionResult:
        """Enables additional CloudWatch metrics for the specified CloudFront
        distribution. The additional metrics incur an additional cost.

        For more information, see `Viewing additional CloudFront distribution
        metrics <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/viewing-cloudfront-metrics.html#monitoring-console.distributions-additional>`__
        in the *Amazon CloudFront Developer Guide*.

        :param monitoring_subscription: A monitoring subscription.
        :param distribution_id: The ID of the distribution that you are enabling metrics for.
        :returns: CreateMonitoringSubscriptionResult
        :raises AccessDenied:
        :raises NoSuchDistribution:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("CreateOriginRequestPolicy")
    def create_origin_request_policy(
        self, context: RequestContext, origin_request_policy_config: OriginRequestPolicyConfig
    ) -> CreateOriginRequestPolicyResult:
        """Creates an origin request policy.

        After you create an origin request policy, you can attach it to one or
        more cache behaviors. When it’s attached to a cache behavior, the origin
        request policy determines the values that CloudFront includes in
        requests that it sends to the origin. Each request that CloudFront sends
        to the origin includes the following:

        -  The request body and the URL path (without the domain name) from the
           viewer request.

        -  The headers that CloudFront automatically includes in every origin
           request, including ``Host``, ``User-Agent``, and ``X-Amz-Cf-Id``.

        -  All HTTP headers, cookies, and URL query strings that are specified
           in the cache policy or the origin request policy. These can include
           items from the viewer request and, in the case of headers, additional
           ones that are added by CloudFront.

        CloudFront sends a request when it can’t find a valid object in its
        cache that matches the request. If you want to send values to the origin
        and also include them in the cache key, use ``CachePolicy``.

        For more information about origin request policies, see `Controlling
        origin
        requests <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param origin_request_policy_config: An origin request policy configuration.
        :returns: CreateOriginRequestPolicyResult
        :raises AccessDenied:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises OriginRequestPolicyAlreadyExists:
        :raises TooManyOriginRequestPolicies:
        :raises TooManyHeadersInOriginRequestPolicy:
        :raises TooManyCookiesInOriginRequestPolicy:
        :raises TooManyQueryStringsInOriginRequestPolicy:
        """
        raise NotImplementedError

    @handler("CreatePublicKey")
    def create_public_key(
        self, context: RequestContext, public_key_config: PublicKeyConfig
    ) -> CreatePublicKeyResult:
        """Uploads a public key to CloudFront that you can use with `signed URLs
        and signed
        cookies <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html>`__,
        or with `field-level
        encryption <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/field-level-encryption.html>`__.

        :param public_key_config: A CloudFront public key configuration.
        :returns: CreatePublicKeyResult
        :raises PublicKeyAlreadyExists:
        :raises InvalidArgument:
        :raises TooManyPublicKeys:
        """
        raise NotImplementedError

    @handler("CreateRealtimeLogConfig")
    def create_realtime_log_config(
        self,
        context: RequestContext,
        end_points: EndPointList,
        fields: FieldList,
        name: string,
        sampling_rate: long,
    ) -> CreateRealtimeLogConfigResult:
        """Creates a real-time log configuration.

        After you create a real-time log configuration, you can attach it to one
        or more cache behaviors to send real-time log data to the specified
        Amazon Kinesis data stream.

        For more information about real-time log configurations, see `Real-time
        logs <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/real-time-logs.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param end_points: Contains information about the Amazon Kinesis data stream where you are
        sending real-time log data.
        :param fields: A list of fields to include in each real-time log record.
        :param name: A unique name to identify this real-time log configuration.
        :param sampling_rate: The sampling rate for this real-time log configuration.
        :returns: CreateRealtimeLogConfigResult
        :raises RealtimeLogConfigAlreadyExists:
        :raises TooManyRealtimeLogConfigs:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("CreateResponseHeadersPolicy")
    def create_response_headers_policy(
        self, context: RequestContext, response_headers_policy_config: ResponseHeadersPolicyConfig
    ) -> CreateResponseHeadersPolicyResult:
        """Creates a response headers policy.

        A response headers policy contains information about a set of HTTP
        response headers and their values. To create a response headers policy,
        you provide some metadata about the policy, and a set of configurations
        that specify the response headers.

        After you create a response headers policy, you can use its ID to attach
        it to one or more cache behaviors in a CloudFront distribution. When
        it’s attached to a cache behavior, CloudFront adds the headers in the
        policy to HTTP responses that it sends for requests that match the cache
        behavior.

        :param response_headers_policy_config: Contains metadata about the response headers policy, and a set of
        configurations that specify the response headers.
        :returns: CreateResponseHeadersPolicyResult
        :raises AccessDenied:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises ResponseHeadersPolicyAlreadyExists:
        :raises TooManyResponseHeadersPolicies:
        :raises TooManyCustomHeadersInResponseHeadersPolicy:
        """
        raise NotImplementedError

    @handler("CreateStreamingDistribution")
    def create_streaming_distribution(
        self, context: RequestContext, streaming_distribution_config: StreamingDistributionConfig
    ) -> CreateStreamingDistributionResult:
        """This API is deprecated. Amazon CloudFront is deprecating real-time
        messaging protocol (RTMP) distributions on December 31, 2020. For more
        information, `read the
        announcement <http://forums.aws.amazon.com/ann.jspa?annID=7356>`__ on
        the Amazon CloudFront discussion forum.

        :param streaming_distribution_config: The streaming distribution's configuration information.
        :returns: CreateStreamingDistributionResult
        :raises CNAMEAlreadyExists:
        :raises StreamingDistributionAlreadyExists:
        :raises InvalidOrigin:
        :raises InvalidOriginAccessIdentity:
        :raises AccessDenied:
        :raises TooManyTrustedSigners:
        :raises TrustedSignerDoesNotExist:
        :raises MissingBody:
        :raises TooManyStreamingDistributionCNAMEs:
        :raises TooManyStreamingDistributions:
        :raises InvalidArgument:
        :raises InconsistentQuantities:
        """
        raise NotImplementedError

    @handler("CreateStreamingDistributionWithTags")
    def create_streaming_distribution_with_tags(
        self,
        context: RequestContext,
        streaming_distribution_config_with_tags: StreamingDistributionConfigWithTags,
    ) -> CreateStreamingDistributionWithTagsResult:
        """This API is deprecated. Amazon CloudFront is deprecating real-time
        messaging protocol (RTMP) distributions on December 31, 2020. For more
        information, `read the
        announcement <http://forums.aws.amazon.com/ann.jspa?annID=7356>`__ on
        the Amazon CloudFront discussion forum.

        :param streaming_distribution_config_with_tags: The streaming distribution's configuration information.
        :returns: CreateStreamingDistributionWithTagsResult
        :raises CNAMEAlreadyExists:
        :raises StreamingDistributionAlreadyExists:
        :raises InvalidOrigin:
        :raises InvalidOriginAccessIdentity:
        :raises AccessDenied:
        :raises TooManyTrustedSigners:
        :raises TrustedSignerDoesNotExist:
        :raises MissingBody:
        :raises TooManyStreamingDistributionCNAMEs:
        :raises TooManyStreamingDistributions:
        :raises InvalidArgument:
        :raises InconsistentQuantities:
        :raises InvalidTagging:
        """
        raise NotImplementedError

    @handler("DeleteCachePolicy")
    def delete_cache_policy(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Deletes a cache policy.

        You cannot delete a cache policy if it’s attached to a cache behavior.
        First update your distributions to remove the cache policy from all
        cache behaviors, then delete the cache policy.

        To delete a cache policy, you must provide the policy’s identifier and
        version. To get these values, you can use ``ListCachePolicies`` or
        ``GetCachePolicy``.

        :param id: The unique identifier for the cache policy that you are deleting.
        :param if_match: The version of the cache policy that you are deleting.
        :raises AccessDenied:
        :raises InvalidIfMatchVersion:
        :raises NoSuchCachePolicy:
        :raises PreconditionFailed:
        :raises IllegalDelete:
        :raises CachePolicyInUse:
        """
        raise NotImplementedError

    @handler("DeleteCloudFrontOriginAccessIdentity")
    def delete_cloud_front_origin_access_identity(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Delete an origin access identity.

        :param id: The origin access identity's ID.
        :param if_match: The value of the ``ETag`` header you received from a previous ``GET`` or
        ``PUT`` request.
        :raises AccessDenied:
        :raises InvalidIfMatchVersion:
        :raises NoSuchCloudFrontOriginAccessIdentity:
        :raises PreconditionFailed:
        :raises CloudFrontOriginAccessIdentityInUse:
        """
        raise NotImplementedError

    @handler("DeleteDistribution")
    def delete_distribution(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Delete a distribution.

        :param id: The distribution ID.
        :param if_match: The value of the ``ETag`` header that you received when you disabled the
        distribution.
        :raises AccessDenied:
        :raises DistributionNotDisabled:
        :raises InvalidIfMatchVersion:
        :raises NoSuchDistribution:
        :raises PreconditionFailed:
        """
        raise NotImplementedError

    @handler("DeleteFieldLevelEncryptionConfig")
    def delete_field_level_encryption_config(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Remove a field-level encryption configuration.

        :param id: The ID of the configuration you want to delete from CloudFront.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        configuration identity to delete.
        :raises AccessDenied:
        :raises InvalidIfMatchVersion:
        :raises NoSuchFieldLevelEncryptionConfig:
        :raises PreconditionFailed:
        :raises FieldLevelEncryptionConfigInUse:
        """
        raise NotImplementedError

    @handler("DeleteFieldLevelEncryptionProfile")
    def delete_field_level_encryption_profile(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Remove a field-level encryption profile.

        :param id: Request the ID of the profile you want to delete from CloudFront.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        profile to delete.
        :raises AccessDenied:
        :raises InvalidIfMatchVersion:
        :raises NoSuchFieldLevelEncryptionProfile:
        :raises PreconditionFailed:
        :raises FieldLevelEncryptionProfileInUse:
        """
        raise NotImplementedError

    @handler("DeleteFunction")
    def delete_function(self, context: RequestContext, if_match: string, name: string) -> None:
        """Deletes a CloudFront function.

        You cannot delete a function if it’s associated with a cache behavior.
        First, update your distributions to remove the function association from
        all cache behaviors, then delete the function.

        To delete a function, you must provide the function’s name and version
        (``ETag`` value). To get these values, you can use ``ListFunctions`` and
        ``DescribeFunction``.

        :param if_match: The current version (``ETag`` value) of the function that you are
        deleting, which you can get using ``DescribeFunction``.
        :param name: The name of the function that you are deleting.
        :raises InvalidIfMatchVersion:
        :raises NoSuchFunctionExists:
        :raises FunctionInUse:
        :raises PreconditionFailed:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("DeleteKeyGroup")
    def delete_key_group(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Deletes a key group.

        You cannot delete a key group that is referenced in a cache behavior.
        First update your distributions to remove the key group from all cache
        behaviors, then delete the key group.

        To delete a key group, you must provide the key group’s identifier and
        version. To get these values, use ``ListKeyGroups`` followed by
        ``GetKeyGroup`` or ``GetKeyGroupConfig``.

        :param id: The identifier of the key group that you are deleting.
        :param if_match: The version of the key group that you are deleting.
        :raises InvalidIfMatchVersion:
        :raises NoSuchResource:
        :raises PreconditionFailed:
        :raises ResourceInUse:
        """
        raise NotImplementedError

    @handler("DeleteMonitoringSubscription")
    def delete_monitoring_subscription(
        self, context: RequestContext, distribution_id: string
    ) -> DeleteMonitoringSubscriptionResult:
        """Disables additional CloudWatch metrics for the specified CloudFront
        distribution.

        :param distribution_id: The ID of the distribution that you are disabling metrics for.
        :returns: DeleteMonitoringSubscriptionResult
        :raises AccessDenied:
        :raises NoSuchDistribution:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("DeleteOriginRequestPolicy")
    def delete_origin_request_policy(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Deletes an origin request policy.

        You cannot delete an origin request policy if it’s attached to any cache
        behaviors. First update your distributions to remove the origin request
        policy from all cache behaviors, then delete the origin request policy.

        To delete an origin request policy, you must provide the policy’s
        identifier and version. To get the identifier, you can use
        ``ListOriginRequestPolicies`` or ``GetOriginRequestPolicy``.

        :param id: The unique identifier for the origin request policy that you are
        deleting.
        :param if_match: The version of the origin request policy that you are deleting.
        :raises AccessDenied:
        :raises InvalidIfMatchVersion:
        :raises NoSuchOriginRequestPolicy:
        :raises PreconditionFailed:
        :raises IllegalDelete:
        :raises OriginRequestPolicyInUse:
        """
        raise NotImplementedError

    @handler("DeletePublicKey")
    def delete_public_key(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Remove a public key you previously added to CloudFront.

        :param id: The ID of the public key you want to remove from CloudFront.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        public key identity to delete.
        :raises AccessDenied:
        :raises PublicKeyInUse:
        :raises InvalidIfMatchVersion:
        :raises NoSuchPublicKey:
        :raises PreconditionFailed:
        """
        raise NotImplementedError

    @handler("DeleteRealtimeLogConfig")
    def delete_realtime_log_config(
        self, context: RequestContext, name: string = None, arn: string = None
    ) -> None:
        """Deletes a real-time log configuration.

        You cannot delete a real-time log configuration if it’s attached to a
        cache behavior. First update your distributions to remove the real-time
        log configuration from all cache behaviors, then delete the real-time
        log configuration.

        To delete a real-time log configuration, you can provide the
        configuration’s name or its Amazon Resource Name (ARN). You must provide
        at least one. If you provide both, CloudFront uses the name to identify
        the real-time log configuration to delete.

        :param name: The name of the real-time log configuration to delete.
        :param arn: The Amazon Resource Name (ARN) of the real-time log configuration to
        delete.
        :raises NoSuchRealtimeLogConfig:
        :raises RealtimeLogConfigInUse:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("DeleteResponseHeadersPolicy")
    def delete_response_headers_policy(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Deletes a response headers policy.

        You cannot delete a response headers policy if it’s attached to a cache
        behavior. First update your distributions to remove the response headers
        policy from all cache behaviors, then delete the response headers
        policy.

        To delete a response headers policy, you must provide the policy’s
        identifier and version. To get these values, you can use
        ``ListResponseHeadersPolicies`` or ``GetResponseHeadersPolicy``.

        :param id: The identifier for the response headers policy that you are deleting.
        :param if_match: The version of the response headers policy that you are deleting.
        :raises AccessDenied:
        :raises InvalidIfMatchVersion:
        :raises NoSuchResponseHeadersPolicy:
        :raises PreconditionFailed:
        :raises IllegalDelete:
        :raises ResponseHeadersPolicyInUse:
        """
        raise NotImplementedError

    @handler("DeleteStreamingDistribution")
    def delete_streaming_distribution(
        self, context: RequestContext, id: string, if_match: string = None
    ) -> None:
        """Delete a streaming distribution. To delete an RTMP distribution using
        the CloudFront API, perform the following steps.

        **To delete an RTMP distribution using the CloudFront API**:

        #. Disable the RTMP distribution.

        #. Submit a ``GET Streaming Distribution Config`` request to get the
           current configuration and the ``Etag`` header for the distribution.

        #. Update the XML document that was returned in the response to your
           ``GET Streaming Distribution Config`` request to change the value of
           ``Enabled`` to ``false``.

        #. Submit a ``PUT Streaming Distribution Config`` request to update the
           configuration for your distribution. In the request body, include the
           XML document that you updated in Step 3. Then set the value of the
           HTTP ``If-Match`` header to the value of the ``ETag`` header that
           CloudFront returned when you submitted the
           ``GET Streaming Distribution Config`` request in Step 2.

        #. Review the response to the ``PUT Streaming Distribution Config``
           request to confirm that the distribution was successfully disabled.

        #. Submit a ``GET Streaming Distribution Config`` request to confirm
           that your changes have propagated. When propagation is complete, the
           value of ``Status`` is ``Deployed``.

        #. Submit a ``DELETE Streaming Distribution`` request. Set the value of
           the HTTP ``If-Match`` header to the value of the ``ETag`` header that
           CloudFront returned when you submitted the
           ``GET Streaming Distribution Config`` request in Step 2.

        #. Review the response to your ``DELETE Streaming Distribution`` request
           to confirm that the distribution was successfully deleted.

        For information about deleting a distribution using the CloudFront
        console, see `Deleting a
        Distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HowToDeleteDistribution.html>`__
        in the *Amazon CloudFront Developer Guide*.

        :param id: The distribution ID.
        :param if_match: The value of the ``ETag`` header that you received when you disabled the
        streaming distribution.
        :raises AccessDenied:
        :raises StreamingDistributionNotDisabled:
        :raises InvalidIfMatchVersion:
        :raises NoSuchStreamingDistribution:
        :raises PreconditionFailed:
        """
        raise NotImplementedError

    @handler("DescribeFunction")
    def describe_function(
        self, context: RequestContext, name: string, stage: FunctionStage = None
    ) -> DescribeFunctionResult:
        """Gets configuration information and metadata about a CloudFront function,
        but not the function’s code. To get a function’s code, use
        ``GetFunction``.

        To get configuration information and metadata about a function, you must
        provide the function’s name and stage. To get these values, you can use
        ``ListFunctions``.

        :param name: The name of the function that you are getting information about.
        :param stage: The function’s stage, either ``DEVELOPMENT`` or ``LIVE``.
        :returns: DescribeFunctionResult
        :raises NoSuchFunctionExists:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("GetCachePolicy")
    def get_cache_policy(self, context: RequestContext, id: string) -> GetCachePolicyResult:
        """Gets a cache policy, including the following metadata:

        -  The policy’s identifier.

        -  The date and time when the policy was last modified.

        To get a cache policy, you must provide the policy’s identifier. If the
        cache policy is attached to a distribution’s cache behavior, you can get
        the policy’s identifier using ``ListDistributions`` or
        ``GetDistribution``. If the cache policy is not attached to a cache
        behavior, you can get the identifier using ``ListCachePolicies``.

        :param id: The unique identifier for the cache policy.
        :returns: GetCachePolicyResult
        :raises AccessDenied:
        :raises NoSuchCachePolicy:
        """
        raise NotImplementedError

    @handler("GetCachePolicyConfig")
    def get_cache_policy_config(
        self, context: RequestContext, id: string
    ) -> GetCachePolicyConfigResult:
        """Gets a cache policy configuration.

        To get a cache policy configuration, you must provide the policy’s
        identifier. If the cache policy is attached to a distribution’s cache
        behavior, you can get the policy’s identifier using
        ``ListDistributions`` or ``GetDistribution``. If the cache policy is not
        attached to a cache behavior, you can get the identifier using
        ``ListCachePolicies``.

        :param id: The unique identifier for the cache policy.
        :returns: GetCachePolicyConfigResult
        :raises AccessDenied:
        :raises NoSuchCachePolicy:
        """
        raise NotImplementedError

    @handler("GetCloudFrontOriginAccessIdentity")
    def get_cloud_front_origin_access_identity(
        self, context: RequestContext, id: string
    ) -> GetCloudFrontOriginAccessIdentityResult:
        """Get the information about an origin access identity.

        :param id: The identity's ID.
        :returns: GetCloudFrontOriginAccessIdentityResult
        :raises NoSuchCloudFrontOriginAccessIdentity:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetCloudFrontOriginAccessIdentityConfig")
    def get_cloud_front_origin_access_identity_config(
        self, context: RequestContext, id: string
    ) -> GetCloudFrontOriginAccessIdentityConfigResult:
        """Get the configuration information about an origin access identity.

        :param id: The identity's ID.
        :returns: GetCloudFrontOriginAccessIdentityConfigResult
        :raises NoSuchCloudFrontOriginAccessIdentity:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetDistribution")
    def get_distribution(self, context: RequestContext, id: string) -> GetDistributionResult:
        """Get the information about a distribution.

        :param id: The distribution's ID.
        :returns: GetDistributionResult
        :raises NoSuchDistribution:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetDistributionConfig")
    def get_distribution_config(
        self, context: RequestContext, id: string
    ) -> GetDistributionConfigResult:
        """Get the configuration information about a distribution.

        :param id: The distribution's ID.
        :returns: GetDistributionConfigResult
        :raises NoSuchDistribution:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetFieldLevelEncryption")
    def get_field_level_encryption(
        self, context: RequestContext, id: string
    ) -> GetFieldLevelEncryptionResult:
        """Get the field-level encryption configuration information.

        :param id: Request the ID for the field-level encryption configuration information.
        :returns: GetFieldLevelEncryptionResult
        :raises AccessDenied:
        :raises NoSuchFieldLevelEncryptionConfig:
        """
        raise NotImplementedError

    @handler("GetFieldLevelEncryptionConfig")
    def get_field_level_encryption_config(
        self, context: RequestContext, id: string
    ) -> GetFieldLevelEncryptionConfigResult:
        """Get the field-level encryption configuration information.

        :param id: Request the ID for the field-level encryption configuration information.
        :returns: GetFieldLevelEncryptionConfigResult
        :raises AccessDenied:
        :raises NoSuchFieldLevelEncryptionConfig:
        """
        raise NotImplementedError

    @handler("GetFieldLevelEncryptionProfile")
    def get_field_level_encryption_profile(
        self, context: RequestContext, id: string
    ) -> GetFieldLevelEncryptionProfileResult:
        """Get the field-level encryption profile information.

        :param id: Get the ID for the field-level encryption profile information.
        :returns: GetFieldLevelEncryptionProfileResult
        :raises AccessDenied:
        :raises NoSuchFieldLevelEncryptionProfile:
        """
        raise NotImplementedError

    @handler("GetFieldLevelEncryptionProfileConfig")
    def get_field_level_encryption_profile_config(
        self, context: RequestContext, id: string
    ) -> GetFieldLevelEncryptionProfileConfigResult:
        """Get the field-level encryption profile configuration information.

        :param id: Get the ID for the field-level encryption profile configuration
        information.
        :returns: GetFieldLevelEncryptionProfileConfigResult
        :raises AccessDenied:
        :raises NoSuchFieldLevelEncryptionProfile:
        """
        raise NotImplementedError

    @handler("GetFunction")
    def get_function(
        self, context: RequestContext, name: string, stage: FunctionStage = None
    ) -> GetFunctionResult:
        """Gets the code of a CloudFront function. To get configuration information
        and metadata about a function, use ``DescribeFunction``.

        To get a function’s code, you must provide the function’s name and
        stage. To get these values, you can use ``ListFunctions``.

        :param name: The name of the function whose code you are getting.
        :param stage: The function’s stage, either ``DEVELOPMENT`` or ``LIVE``.
        :returns: GetFunctionResult
        :raises NoSuchFunctionExists:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("GetInvalidation")
    def get_invalidation(
        self, context: RequestContext, distribution_id: string, id: string
    ) -> GetInvalidationResult:
        """Get the information about an invalidation.

        :param distribution_id: The distribution's ID.
        :param id: The identifier for the invalidation request, for example,
        ``IDFDVBD632BHDS5``.
        :returns: GetInvalidationResult
        :raises NoSuchInvalidation:
        :raises NoSuchDistribution:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetKeyGroup")
    def get_key_group(self, context: RequestContext, id: string) -> GetKeyGroupResult:
        """Gets a key group, including the date and time when the key group was
        last modified.

        To get a key group, you must provide the key group’s identifier. If the
        key group is referenced in a distribution’s cache behavior, you can get
        the key group’s identifier using ``ListDistributions`` or
        ``GetDistribution``. If the key group is not referenced in a cache
        behavior, you can get the identifier using ``ListKeyGroups``.

        :param id: The identifier of the key group that you are getting.
        :returns: GetKeyGroupResult
        :raises NoSuchResource:
        """
        raise NotImplementedError

    @handler("GetKeyGroupConfig")
    def get_key_group_config(self, context: RequestContext, id: string) -> GetKeyGroupConfigResult:
        """Gets a key group configuration.

        To get a key group configuration, you must provide the key group’s
        identifier. If the key group is referenced in a distribution’s cache
        behavior, you can get the key group’s identifier using
        ``ListDistributions`` or ``GetDistribution``. If the key group is not
        referenced in a cache behavior, you can get the identifier using
        ``ListKeyGroups``.

        :param id: The identifier of the key group whose configuration you are getting.
        :returns: GetKeyGroupConfigResult
        :raises NoSuchResource:
        """
        raise NotImplementedError

    @handler("GetMonitoringSubscription")
    def get_monitoring_subscription(
        self, context: RequestContext, distribution_id: string
    ) -> GetMonitoringSubscriptionResult:
        """Gets information about whether additional CloudWatch metrics are enabled
        for the specified CloudFront distribution.

        :param distribution_id: The ID of the distribution that you are getting metrics information for.
        :returns: GetMonitoringSubscriptionResult
        :raises AccessDenied:
        :raises NoSuchDistribution:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("GetOriginRequestPolicy")
    def get_origin_request_policy(
        self, context: RequestContext, id: string
    ) -> GetOriginRequestPolicyResult:
        """Gets an origin request policy, including the following metadata:

        -  The policy’s identifier.

        -  The date and time when the policy was last modified.

        To get an origin request policy, you must provide the policy’s
        identifier. If the origin request policy is attached to a distribution’s
        cache behavior, you can get the policy’s identifier using
        ``ListDistributions`` or ``GetDistribution``. If the origin request
        policy is not attached to a cache behavior, you can get the identifier
        using ``ListOriginRequestPolicies``.

        :param id: The unique identifier for the origin request policy.
        :returns: GetOriginRequestPolicyResult
        :raises AccessDenied:
        :raises NoSuchOriginRequestPolicy:
        """
        raise NotImplementedError

    @handler("GetOriginRequestPolicyConfig")
    def get_origin_request_policy_config(
        self, context: RequestContext, id: string
    ) -> GetOriginRequestPolicyConfigResult:
        """Gets an origin request policy configuration.

        To get an origin request policy configuration, you must provide the
        policy’s identifier. If the origin request policy is attached to a
        distribution’s cache behavior, you can get the policy’s identifier using
        ``ListDistributions`` or ``GetDistribution``. If the origin request
        policy is not attached to a cache behavior, you can get the identifier
        using ``ListOriginRequestPolicies``.

        :param id: The unique identifier for the origin request policy.
        :returns: GetOriginRequestPolicyConfigResult
        :raises AccessDenied:
        :raises NoSuchOriginRequestPolicy:
        """
        raise NotImplementedError

    @handler("GetPublicKey")
    def get_public_key(self, context: RequestContext, id: string) -> GetPublicKeyResult:
        """Gets a public key.

        :param id: The identifier of the public key you are getting.
        :returns: GetPublicKeyResult
        :raises AccessDenied:
        :raises NoSuchPublicKey:
        """
        raise NotImplementedError

    @handler("GetPublicKeyConfig")
    def get_public_key_config(
        self, context: RequestContext, id: string
    ) -> GetPublicKeyConfigResult:
        """Gets a public key configuration.

        :param id: The identifier of the public key whose configuration you are getting.
        :returns: GetPublicKeyConfigResult
        :raises AccessDenied:
        :raises NoSuchPublicKey:
        """
        raise NotImplementedError

    @handler("GetRealtimeLogConfig")
    def get_realtime_log_config(
        self, context: RequestContext, name: string = None, arn: string = None
    ) -> GetRealtimeLogConfigResult:
        """Gets a real-time log configuration.

        To get a real-time log configuration, you can provide the
        configuration’s name or its Amazon Resource Name (ARN). You must provide
        at least one. If you provide both, CloudFront uses the name to identify
        the real-time log configuration to get.

        :param name: The name of the real-time log configuration to get.
        :param arn: The Amazon Resource Name (ARN) of the real-time log configuration to
        get.
        :returns: GetRealtimeLogConfigResult
        :raises NoSuchRealtimeLogConfig:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetResponseHeadersPolicy")
    def get_response_headers_policy(
        self, context: RequestContext, id: string
    ) -> GetResponseHeadersPolicyResult:
        """Gets a response headers policy, including metadata (the policy’s
        identifier and the date and time when the policy was last modified).

        To get a response headers policy, you must provide the policy’s
        identifier. If the response headers policy is attached to a
        distribution’s cache behavior, you can get the policy’s identifier using
        ``ListDistributions`` or ``GetDistribution``. If the response headers
        policy is not attached to a cache behavior, you can get the identifier
        using ``ListResponseHeadersPolicies``.

        :param id: The identifier for the response headers policy.
        :returns: GetResponseHeadersPolicyResult
        :raises AccessDenied:
        :raises NoSuchResponseHeadersPolicy:
        """
        raise NotImplementedError

    @handler("GetResponseHeadersPolicyConfig")
    def get_response_headers_policy_config(
        self, context: RequestContext, id: string
    ) -> GetResponseHeadersPolicyConfigResult:
        """Gets a response headers policy configuration.

        To get a response headers policy configuration, you must provide the
        policy’s identifier. If the response headers policy is attached to a
        distribution’s cache behavior, you can get the policy’s identifier using
        ``ListDistributions`` or ``GetDistribution``. If the response headers
        policy is not attached to a cache behavior, you can get the identifier
        using ``ListResponseHeadersPolicies``.

        :param id: The identifier for the response headers policy.
        :returns: GetResponseHeadersPolicyConfigResult
        :raises AccessDenied:
        :raises NoSuchResponseHeadersPolicy:
        """
        raise NotImplementedError

    @handler("GetStreamingDistribution")
    def get_streaming_distribution(
        self, context: RequestContext, id: string
    ) -> GetStreamingDistributionResult:
        """Gets information about a specified RTMP distribution, including the
        distribution configuration.

        :param id: The streaming distribution's ID.
        :returns: GetStreamingDistributionResult
        :raises NoSuchStreamingDistribution:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("GetStreamingDistributionConfig")
    def get_streaming_distribution_config(
        self, context: RequestContext, id: string
    ) -> GetStreamingDistributionConfigResult:
        """Get the configuration information about a streaming distribution.

        :param id: The streaming distribution's ID.
        :returns: GetStreamingDistributionConfigResult
        :raises NoSuchStreamingDistribution:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("ListCachePolicies", expand=False)
    def list_cache_policies(
        self, context: RequestContext, request: ListCachePoliciesRequest
    ) -> ListCachePoliciesResult:
        """Gets a list of cache policies.

        You can optionally apply a filter to return only the managed policies
        created by Amazon Web Services, or only the custom policies created in
        your Amazon Web Services account.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param type: A filter to return only the specified kinds of cache policies.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of cache policies.
        :param max_items: The maximum number of cache policies that you want in the response.
        :returns: ListCachePoliciesResult
        :raises AccessDenied:
        :raises NoSuchCachePolicy:
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListCloudFrontOriginAccessIdentities")
    def list_cloud_front_origin_access_identities(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListCloudFrontOriginAccessIdentitiesResult:
        """Lists origin access identities.

        :param marker: Use this when paginating results to indicate where to begin in your list
        of origin access identities.
        :param max_items: The maximum number of origin access identities you want in the response
        body.
        :returns: ListCloudFrontOriginAccessIdentitiesResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListConflictingAliases")
    def list_conflicting_aliases(
        self,
        context: RequestContext,
        distribution_id: distributionIdString,
        alias: aliasString,
        marker: string = None,
        max_items: listConflictingAliasesMaxItemsInteger = None,
    ) -> ListConflictingAliasesResult:
        """Gets a list of aliases (also called CNAMEs or alternate domain names)
        that conflict or overlap with the provided alias, and the associated
        CloudFront distributions and Amazon Web Services accounts for each
        conflicting alias. In the returned list, the distribution and account
        IDs are partially hidden, which allows you to identify the distributions
        and accounts that you own, but helps to protect the information of ones
        that you don’t own.

        Use this operation to find aliases that are in use in CloudFront that
        conflict or overlap with the provided alias. For example, if you provide
        ``www.example.com`` as input, the returned list can include
        ``www.example.com`` and the overlapping wildcard alternate domain name
        (``*.example.com``), if they exist. If you provide ``*.example.com`` as
        input, the returned list can include ``*.example.com`` and any alternate
        domain names covered by that wildcard (for example, ``www.example.com``,
        ``test.example.com``, ``dev.example.com``, and so on), if they exist.

        To list conflicting aliases, you provide the alias to search and the ID
        of a distribution in your account that has an attached SSL/TLS
        certificate that includes the provided alias. For more information,
        including how to set up the distribution and certificate, see `Moving an
        alternate domain name to a different
        distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html#alternate-domain-names-move>`__
        in the *Amazon CloudFront Developer Guide*.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param distribution_id: The ID of a distribution in your account that has an attached SSL/TLS
        certificate that includes the provided alias.
        :param alias: The alias (also called a CNAME) to search for conflicting aliases.
        :param marker: Use this field when paginating results to indicate where to begin in the
        list of conflicting aliases.
        :param max_items: The maximum number of conflicting aliases that you want in the response.
        :returns: ListConflictingAliasesResult
        :raises InvalidArgument:
        :raises NoSuchDistribution:
        """
        raise NotImplementedError

    @handler("ListDistributions")
    def list_distributions(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListDistributionsResult:
        """List CloudFront distributions.

        :param marker: Use this when paginating results to indicate where to begin in your list
        of distributions.
        :param max_items: The maximum number of distributions you want in the response body.
        :returns: ListDistributionsResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListDistributionsByCachePolicyId")
    def list_distributions_by_cache_policy_id(
        self,
        context: RequestContext,
        cache_policy_id: string,
        marker: string = None,
        max_items: string = None,
    ) -> ListDistributionsByCachePolicyIdResult:
        """Gets a list of distribution IDs for distributions that have a cache
        behavior that’s associated with the specified cache policy.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param cache_policy_id: The ID of the cache policy whose associated distribution IDs you want to
        list.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of distribution IDs.
        :param max_items: The maximum number of distribution IDs that you want in the response.
        :returns: ListDistributionsByCachePolicyIdResult
        :raises NoSuchCachePolicy:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("ListDistributionsByKeyGroup")
    def list_distributions_by_key_group(
        self,
        context: RequestContext,
        key_group_id: string,
        marker: string = None,
        max_items: string = None,
    ) -> ListDistributionsByKeyGroupResult:
        """Gets a list of distribution IDs for distributions that have a cache
        behavior that references the specified key group.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param key_group_id: The ID of the key group whose associated distribution IDs you are
        listing.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of distribution IDs.
        :param max_items: The maximum number of distribution IDs that you want in the response.
        :returns: ListDistributionsByKeyGroupResult
        :raises NoSuchResource:
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListDistributionsByOriginRequestPolicyId")
    def list_distributions_by_origin_request_policy_id(
        self,
        context: RequestContext,
        origin_request_policy_id: string,
        marker: string = None,
        max_items: string = None,
    ) -> ListDistributionsByOriginRequestPolicyIdResult:
        """Gets a list of distribution IDs for distributions that have a cache
        behavior that’s associated with the specified origin request policy.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param origin_request_policy_id: The ID of the origin request policy whose associated distribution IDs
        you want to list.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of distribution IDs.
        :param max_items: The maximum number of distribution IDs that you want in the response.
        :returns: ListDistributionsByOriginRequestPolicyIdResult
        :raises NoSuchOriginRequestPolicy:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("ListDistributionsByRealtimeLogConfig")
    def list_distributions_by_realtime_log_config(
        self,
        context: RequestContext,
        marker: string = None,
        max_items: string = None,
        realtime_log_config_name: string = None,
        realtime_log_config_arn: string = None,
    ) -> ListDistributionsByRealtimeLogConfigResult:
        """Gets a list of distributions that have a cache behavior that’s
        associated with the specified real-time log configuration.

        You can specify the real-time log configuration by its name or its
        Amazon Resource Name (ARN). You must provide at least one. If you
        provide both, CloudFront uses the name to identify the real-time log
        configuration to list distributions for.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param marker: Use this field when paginating results to indicate where to begin in
        your list of distributions.
        :param max_items: The maximum number of distributions that you want in the response.
        :param realtime_log_config_name: The name of the real-time log configuration whose associated
        distributions you want to list.
        :param realtime_log_config_arn: The Amazon Resource Name (ARN) of the real-time log configuration whose
        associated distributions you want to list.
        :returns: ListDistributionsByRealtimeLogConfigResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListDistributionsByResponseHeadersPolicyId")
    def list_distributions_by_response_headers_policy_id(
        self,
        context: RequestContext,
        response_headers_policy_id: string,
        marker: string = None,
        max_items: string = None,
    ) -> ListDistributionsByResponseHeadersPolicyIdResult:
        """Gets a list of distribution IDs for distributions that have a cache
        behavior that’s associated with the specified response headers policy.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param response_headers_policy_id: The ID of the response headers policy whose associated distribution IDs
        you want to list.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of distribution IDs.
        :param max_items: The maximum number of distribution IDs that you want to get in the
        response.
        :returns: ListDistributionsByResponseHeadersPolicyIdResult
        :raises NoSuchResponseHeadersPolicy:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("ListDistributionsByWebACLId")
    def list_distributions_by_web_acl_id(
        self,
        context: RequestContext,
        web_acl_id: string,
        marker: string = None,
        max_items: string = None,
    ) -> ListDistributionsByWebACLIdResult:
        """List the distributions that are associated with a specified WAF web ACL.

        :param web_acl_id: The ID of the WAF web ACL that you want to list the associated
        distributions.
        :param marker: Use ``Marker`` and ``MaxItems`` to control pagination of results.
        :param max_items: The maximum number of distributions that you want CloudFront to return
        in the response body.
        :returns: ListDistributionsByWebACLIdResult
        :raises InvalidArgument:
        :raises InvalidWebACLId:
        """
        raise NotImplementedError

    @handler("ListFieldLevelEncryptionConfigs")
    def list_field_level_encryption_configs(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListFieldLevelEncryptionConfigsResult:
        """List all field-level encryption configurations that have been created in
        CloudFront for this account.

        :param marker: Use this when paginating results to indicate where to begin in your list
        of configurations.
        :param max_items: The maximum number of field-level encryption configurations you want in
        the response body.
        :returns: ListFieldLevelEncryptionConfigsResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListFieldLevelEncryptionProfiles")
    def list_field_level_encryption_profiles(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListFieldLevelEncryptionProfilesResult:
        """Request a list of field-level encryption profiles that have been created
        in CloudFront for this account.

        :param marker: Use this when paginating results to indicate where to begin in your list
        of profiles.
        :param max_items: The maximum number of field-level encryption profiles you want in the
        response body.
        :returns: ListFieldLevelEncryptionProfilesResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListFunctions")
    def list_functions(
        self,
        context: RequestContext,
        marker: string = None,
        max_items: string = None,
        stage: FunctionStage = None,
    ) -> ListFunctionsResult:
        """Gets a list of all CloudFront functions in your Amazon Web Services
        account.

        You can optionally apply a filter to return only the functions that are
        in the specified stage, either ``DEVELOPMENT`` or ``LIVE``.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param marker: Use this field when paginating results to indicate where to begin in
        your list of functions.
        :param max_items: The maximum number of functions that you want in the response.
        :param stage: An optional filter to return only the functions that are in the
        specified stage, either ``DEVELOPMENT`` or ``LIVE``.
        :returns: ListFunctionsResult
        :raises InvalidArgument:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("ListInvalidations")
    def list_invalidations(
        self,
        context: RequestContext,
        distribution_id: string,
        marker: string = None,
        max_items: string = None,
    ) -> ListInvalidationsResult:
        """Lists invalidation batches.

        :param distribution_id: The distribution's ID.
        :param marker: Use this parameter when paginating results to indicate where to begin in
        your list of invalidation batches.
        :param max_items: The maximum number of invalidation batches that you want in the response
        body.
        :returns: ListInvalidationsResult
        :raises InvalidArgument:
        :raises NoSuchDistribution:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("ListKeyGroups")
    def list_key_groups(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListKeyGroupsResult:
        """Gets a list of key groups.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param marker: Use this field when paginating results to indicate where to begin in
        your list of key groups.
        :param max_items: The maximum number of key groups that you want in the response.
        :returns: ListKeyGroupsResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListOriginRequestPolicies", expand=False)
    def list_origin_request_policies(
        self, context: RequestContext, request: ListOriginRequestPoliciesRequest
    ) -> ListOriginRequestPoliciesResult:
        """Gets a list of origin request policies.

        You can optionally apply a filter to return only the managed policies
        created by Amazon Web Services, or only the custom policies created in
        your Amazon Web Services account.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param type: A filter to return only the specified kinds of origin request policies.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of origin request policies.
        :param max_items: The maximum number of origin request policies that you want in the
        response.
        :returns: ListOriginRequestPoliciesResult
        :raises AccessDenied:
        :raises NoSuchOriginRequestPolicy:
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListPublicKeys")
    def list_public_keys(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListPublicKeysResult:
        """List all public keys that have been added to CloudFront for this
        account.

        :param marker: Use this when paginating results to indicate where to begin in your list
        of public keys.
        :param max_items: The maximum number of public keys you want in the response body.
        :returns: ListPublicKeysResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListRealtimeLogConfigs")
    def list_realtime_log_configs(
        self, context: RequestContext, max_items: string = None, marker: string = None
    ) -> ListRealtimeLogConfigsResult:
        """Gets a list of real-time log configurations.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param max_items: The maximum number of real-time log configurations that you want in the
        response.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of real-time log configurations.
        :returns: ListRealtimeLogConfigsResult
        :raises InvalidArgument:
        :raises AccessDenied:
        :raises NoSuchRealtimeLogConfig:
        """
        raise NotImplementedError

    @handler("ListResponseHeadersPolicies", expand=False)
    def list_response_headers_policies(
        self, context: RequestContext, request: ListResponseHeadersPoliciesRequest
    ) -> ListResponseHeadersPoliciesResult:
        """Gets a list of response headers policies.

        You can optionally apply a filter to get only the managed policies
        created by Amazon Web Services, or only the custom policies created in
        your Amazon Web Services account.

        You can optionally specify the maximum number of items to receive in the
        response. If the total number of items in the list exceeds the maximum
        that you specify, or the default maximum, the response is paginated. To
        get the next page of items, send a subsequent request that specifies the
        ``NextMarker`` value from the current response as the ``Marker`` value
        in the subsequent request.

        :param type: A filter to get only the specified kind of response headers policies.
        :param marker: Use this field when paginating results to indicate where to begin in
        your list of response headers policies.
        :param max_items: The maximum number of response headers policies that you want to get in
        the response.
        :returns: ListResponseHeadersPoliciesResult
        :raises AccessDenied:
        :raises NoSuchResponseHeadersPolicy:
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListStreamingDistributions")
    def list_streaming_distributions(
        self, context: RequestContext, marker: string = None, max_items: string = None
    ) -> ListStreamingDistributionsResult:
        """List streaming distributions.

        :param marker: The value that you provided for the ``Marker`` request parameter.
        :param max_items: The value that you provided for the ``MaxItems`` request parameter.
        :returns: ListStreamingDistributionsResult
        :raises InvalidArgument:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource: ResourceARN
    ) -> ListTagsForResourceResult:
        """List tags for a CloudFront resource.

        :param resource: An ARN of a CloudFront resource.
        :returns: ListTagsForResourceResult
        :raises AccessDenied:
        :raises InvalidArgument:
        :raises InvalidTagging:
        :raises NoSuchResource:
        """
        raise NotImplementedError

    @handler("PublishFunction")
    def publish_function(
        self, context: RequestContext, name: string, if_match: string
    ) -> PublishFunctionResult:
        """Publishes a CloudFront function by copying the function code from the
        ``DEVELOPMENT`` stage to ``LIVE``. This automatically updates all cache
        behaviors that are using this function to use the newly published copy
        in the ``LIVE`` stage.

        When a function is published to the ``LIVE`` stage, you can attach the
        function to a distribution’s cache behavior, using the function’s Amazon
        Resource Name (ARN).

        To publish a function, you must provide the function’s name and version
        (``ETag`` value). To get these values, you can use ``ListFunctions`` and
        ``DescribeFunction``.

        :param name: The name of the function that you are publishing.
        :param if_match: The current version (``ETag`` value) of the function that you are
        publishing, which you can get using ``DescribeFunction``.
        :returns: PublishFunctionResult
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchFunctionExists:
        :raises PreconditionFailed:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(self, context: RequestContext, resource: ResourceARN, tags: Tags) -> None:
        """Add tags to a CloudFront resource.

        :param resource: An ARN of a CloudFront resource.
        :param tags: A complex type that contains zero or more ``Tag`` elements.
        :raises AccessDenied:
        :raises InvalidArgument:
        :raises InvalidTagging:
        :raises NoSuchResource:
        """
        raise NotImplementedError

    @handler("TestFunction")
    def test_function(
        self,
        context: RequestContext,
        name: string,
        if_match: string,
        event_object: FunctionEventObject,
        stage: FunctionStage = None,
    ) -> TestFunctionResult:
        """Tests a CloudFront function.

        To test a function, you provide an *event object* that represents an
        HTTP request or response that your CloudFront distribution could receive
        in production. CloudFront runs the function, passing it the event object
        that you provided, and returns the function’s result (the modified event
        object) in the response. The response also contains function logs and
        error messages, if any exist. For more information about testing
        functions, see `Testing
        functions <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/managing-functions.html#test-function>`__
        in the *Amazon CloudFront Developer Guide*.

        To test a function, you provide the function’s name and version
        (``ETag`` value) along with the event object. To get the function’s name
        and version, you can use ``ListFunctions`` and ``DescribeFunction``.

        :param name: The name of the function that you are testing.
        :param if_match: The current version (``ETag`` value) of the function that you are
        testing, which you can get using ``DescribeFunction``.
        :param event_object: The event object to test the function with.
        :param stage: The stage of the function that you are testing, either ``DEVELOPMENT``
        or ``LIVE``.
        :returns: TestFunctionResult
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchFunctionExists:
        :raises TestFunctionFailed:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource: ResourceARN, tag_keys: TagKeys
    ) -> None:
        """Remove tags from a CloudFront resource.

        :param resource: An ARN of a CloudFront resource.
        :param tag_keys: A complex type that contains zero or more ``Tag`` key elements.
        :raises AccessDenied:
        :raises InvalidArgument:
        :raises InvalidTagging:
        :raises NoSuchResource:
        """
        raise NotImplementedError

    @handler("UpdateCachePolicy")
    def update_cache_policy(
        self,
        context: RequestContext,
        cache_policy_config: CachePolicyConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateCachePolicyResult:
        """Updates a cache policy configuration.

        When you update a cache policy configuration, all the fields are updated
        with the values provided in the request. You cannot update some fields
        independent of others. To update a cache policy configuration:

        #. Use ``GetCachePolicyConfig`` to get the current configuration.

        #. Locally modify the fields in the cache policy configuration that you
           want to update.

        #. Call ``UpdateCachePolicy`` by providing the entire cache policy
           configuration, including the fields that you modified and those that
           you didn’t.

        :param cache_policy_config: A cache policy configuration.
        :param id: The unique identifier for the cache policy that you are updating.
        :param if_match: The version of the cache policy that you are updating.
        :returns: UpdateCachePolicyResult
        :raises AccessDenied:
        :raises IllegalUpdate:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchCachePolicy:
        :raises PreconditionFailed:
        :raises CachePolicyAlreadyExists:
        :raises TooManyHeadersInCachePolicy:
        :raises TooManyCookiesInCachePolicy:
        :raises TooManyQueryStringsInCachePolicy:
        """
        raise NotImplementedError

    @handler("UpdateCloudFrontOriginAccessIdentity")
    def update_cloud_front_origin_access_identity(
        self,
        context: RequestContext,
        cloud_front_origin_access_identity_config: CloudFrontOriginAccessIdentityConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateCloudFrontOriginAccessIdentityResult:
        """Update an origin access identity.

        :param cloud_front_origin_access_identity_config: The identity's configuration information.
        :param id: The identity's id.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        identity's configuration.
        :returns: UpdateCloudFrontOriginAccessIdentityResult
        :raises AccessDenied:
        :raises IllegalUpdate:
        :raises InvalidIfMatchVersion:
        :raises MissingBody:
        :raises NoSuchCloudFrontOriginAccessIdentity:
        :raises PreconditionFailed:
        :raises InvalidArgument:
        :raises InconsistentQuantities:
        """
        raise NotImplementedError

    @handler("UpdateDistribution")
    def update_distribution(
        self,
        context: RequestContext,
        distribution_config: DistributionConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateDistributionResult:
        """Updates the configuration for a web distribution.

        When you update a distribution, there are more required fields than when
        you create a distribution. When you update your distribution by using
        this API action, follow the steps here to get the current configuration
        and then make your updates, to make sure that you include all of the
        required fields. To view a summary, see `Required Fields for Create
        Distribution and Update
        Distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-overview-required-fields.html>`__
        in the *Amazon CloudFront Developer Guide*.

        The update process includes getting the current distribution
        configuration, updating the XML document that is returned to make your
        changes, and then submitting an ``UpdateDistribution`` request to make
        the updates.

        For information about updating a distribution using the CloudFront
        console instead, see `Creating a
        Distribution <https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-creating-console.html>`__
        in the *Amazon CloudFront Developer Guide*.

        **To update a web distribution using the CloudFront API**

        #. Submit a
           `GetDistributionConfig <https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_GetDistributionConfig.html>`__
           request to get the current configuration and an ``Etag`` header for
           the distribution.

           If you update the distribution again, you must get a new ``Etag``
           header.

        #. Update the XML document that was returned in the response to your
           ``GetDistributionConfig`` request to include your changes.

           When you edit the XML file, be aware of the following:

           -  You must strip out the ETag parameter that is returned.

           -  Additional fields are required when you update a distribution.
              There may be fields included in the XML file for features that you
              haven't configured for your distribution. This is expected and
              required to successfully update the distribution.

           -  You can't change the value of ``CallerReference``. If you try to
              change this value, CloudFront returns an ``IllegalUpdate`` error.

           -  The new configuration replaces the existing configuration; the
              values that you specify in an ``UpdateDistribution`` request are
              not merged into your existing configuration. When you add, delete,
              or replace values in an element that allows multiple values (for
              example, ``CNAME``), you must specify all of the values that you
              want to appear in the updated distribution. In addition, you must
              update the corresponding ``Quantity`` element.

        #. Submit an ``UpdateDistribution`` request to update the configuration
           for your distribution:

           -  In the request body, include the XML document that you updated in
              Step 2. The request body must include an XML document with a
              ``DistributionConfig`` element.

           -  Set the value of the HTTP ``If-Match`` header to the value of the
              ``ETag`` header that CloudFront returned when you submitted the
              ``GetDistributionConfig`` request in Step 1.

        #. Review the response to the ``UpdateDistribution`` request to confirm
           that the configuration was successfully updated.

        #. Optional: Submit a
           `GetDistribution <https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_GetDistribution.html>`__
           request to confirm that your changes have propagated. When
           propagation is complete, the value of ``Status`` is ``Deployed``.

        :param distribution_config: The distribution's configuration information.
        :param id: The distribution's id.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        distribution's configuration.
        :returns: UpdateDistributionResult
        :raises AccessDenied:
        :raises CNAMEAlreadyExists:
        :raises IllegalUpdate:
        :raises InvalidIfMatchVersion:
        :raises MissingBody:
        :raises NoSuchDistribution:
        :raises PreconditionFailed:
        :raises TooManyDistributionCNAMEs:
        :raises InvalidDefaultRootObject:
        :raises InvalidRelativePath:
        :raises InvalidErrorCode:
        :raises InvalidResponseCode:
        :raises InvalidArgument:
        :raises InvalidOriginAccessIdentity:
        :raises TooManyTrustedSigners:
        :raises TrustedSignerDoesNotExist:
        :raises InvalidViewerCertificate:
        :raises InvalidMinimumProtocolVersion:
        :raises InvalidRequiredProtocol:
        :raises NoSuchOrigin:
        :raises TooManyOrigins:
        :raises TooManyOriginGroupsPerDistribution:
        :raises TooManyCacheBehaviors:
        :raises TooManyCookieNamesInWhiteList:
        :raises InvalidForwardCookies:
        :raises TooManyHeadersInForwardedValues:
        :raises InvalidHeadersForS3Origin:
        :raises InconsistentQuantities:
        :raises TooManyCertificates:
        :raises InvalidLocationCode:
        :raises InvalidGeoRestrictionParameter:
        :raises InvalidTTLOrder:
        :raises InvalidWebACLId:
        :raises TooManyOriginCustomHeaders:
        :raises TooManyQueryStringParameters:
        :raises InvalidQueryStringParameters:
        :raises TooManyDistributionsWithLambdaAssociations:
        :raises TooManyDistributionsWithSingleFunctionARN:
        :raises TooManyLambdaFunctionAssociations:
        :raises InvalidLambdaFunctionAssociation:
        :raises TooManyDistributionsWithFunctionAssociations:
        :raises TooManyFunctionAssociations:
        :raises InvalidFunctionAssociation:
        :raises InvalidOriginReadTimeout:
        :raises InvalidOriginKeepaliveTimeout:
        :raises NoSuchFieldLevelEncryptionConfig:
        :raises IllegalFieldLevelEncryptionConfigAssociationWithCacheBehavior:
        :raises TooManyDistributionsAssociatedToFieldLevelEncryptionConfig:
        :raises NoSuchCachePolicy:
        :raises TooManyDistributionsAssociatedToCachePolicy:
        :raises NoSuchResponseHeadersPolicy:
        :raises TooManyDistributionsAssociatedToResponseHeadersPolicy:
        :raises NoSuchOriginRequestPolicy:
        :raises TooManyDistributionsAssociatedToOriginRequestPolicy:
        :raises TooManyDistributionsAssociatedToKeyGroup:
        :raises TooManyKeyGroupsAssociatedToDistribution:
        :raises TrustedKeyGroupDoesNotExist:
        :raises NoSuchRealtimeLogConfig:
        :raises RealtimeLogConfigOwnerMismatch:
        """
        raise NotImplementedError

    @handler("UpdateFieldLevelEncryptionConfig")
    def update_field_level_encryption_config(
        self,
        context: RequestContext,
        field_level_encryption_config: FieldLevelEncryptionConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateFieldLevelEncryptionConfigResult:
        """Update a field-level encryption configuration.

        :param field_level_encryption_config: Request to update a field-level encryption configuration.
        :param id: The ID of the configuration you want to update.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        configuration identity to update.
        :returns: UpdateFieldLevelEncryptionConfigResult
        :raises AccessDenied:
        :raises IllegalUpdate:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchFieldLevelEncryptionProfile:
        :raises NoSuchFieldLevelEncryptionConfig:
        :raises PreconditionFailed:
        :raises TooManyFieldLevelEncryptionQueryArgProfiles:
        :raises TooManyFieldLevelEncryptionContentTypeProfiles:
        :raises QueryArgProfileEmpty:
        """
        raise NotImplementedError

    @handler("UpdateFieldLevelEncryptionProfile")
    def update_field_level_encryption_profile(
        self,
        context: RequestContext,
        field_level_encryption_profile_config: FieldLevelEncryptionProfileConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateFieldLevelEncryptionProfileResult:
        """Update a field-level encryption profile.

        :param field_level_encryption_profile_config: Request to update a field-level encryption profile.
        :param id: The ID of the field-level encryption profile request.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        profile identity to update.
        :returns: UpdateFieldLevelEncryptionProfileResult
        :raises AccessDenied:
        :raises FieldLevelEncryptionProfileAlreadyExists:
        :raises IllegalUpdate:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchPublicKey:
        :raises NoSuchFieldLevelEncryptionProfile:
        :raises PreconditionFailed:
        :raises FieldLevelEncryptionProfileSizeExceeded:
        :raises TooManyFieldLevelEncryptionEncryptionEntities:
        :raises TooManyFieldLevelEncryptionFieldPatterns:
        """
        raise NotImplementedError

    @handler("UpdateFunction")
    def update_function(
        self,
        context: RequestContext,
        if_match: string,
        function_config: FunctionConfig,
        function_code: FunctionBlob,
        name: string,
    ) -> UpdateFunctionResult:
        """Updates a CloudFront function.

        You can update a function’s code or the comment that describes the
        function. You cannot update a function’s name.

        To update a function, you provide the function’s name and version
        (``ETag`` value) along with the updated function code. To get the name
        and version, you can use ``ListFunctions`` and ``DescribeFunction``.

        :param if_match: The current version (``ETag`` value) of the function that you are
        updating, which you can get using ``DescribeFunction``.
        :param function_config: Configuration information about the function.
        :param function_code: The function code.
        :param name: The name of the function that you are updating.
        :returns: UpdateFunctionResult
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchFunctionExists:
        :raises PreconditionFailed:
        :raises FunctionSizeLimitExceeded:
        :raises UnsupportedOperation:
        """
        raise NotImplementedError

    @handler("UpdateKeyGroup")
    def update_key_group(
        self,
        context: RequestContext,
        key_group_config: KeyGroupConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateKeyGroupResult:
        """Updates a key group.

        When you update a key group, all the fields are updated with the values
        provided in the request. You cannot update some fields independent of
        others. To update a key group:

        #. Get the current key group with ``GetKeyGroup`` or
           ``GetKeyGroupConfig``.

        #. Locally modify the fields in the key group that you want to update.
           For example, add or remove public key IDs.

        #. Call ``UpdateKeyGroup`` with the entire key group object, including
           the fields that you modified and those that you didn’t.

        :param key_group_config: The key group configuration.
        :param id: The identifier of the key group that you are updating.
        :param if_match: The version of the key group that you are updating.
        :returns: UpdateKeyGroupResult
        :raises InvalidIfMatchVersion:
        :raises NoSuchResource:
        :raises PreconditionFailed:
        :raises KeyGroupAlreadyExists:
        :raises InvalidArgument:
        :raises TooManyPublicKeysInKeyGroup:
        """
        raise NotImplementedError

    @handler("UpdateOriginRequestPolicy")
    def update_origin_request_policy(
        self,
        context: RequestContext,
        origin_request_policy_config: OriginRequestPolicyConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateOriginRequestPolicyResult:
        """Updates an origin request policy configuration.

        When you update an origin request policy configuration, all the fields
        are updated with the values provided in the request. You cannot update
        some fields independent of others. To update an origin request policy
        configuration:

        #. Use ``GetOriginRequestPolicyConfig`` to get the current
           configuration.

        #. Locally modify the fields in the origin request policy configuration
           that you want to update.

        #. Call ``UpdateOriginRequestPolicy`` by providing the entire origin
           request policy configuration, including the fields that you modified
           and those that you didn’t.

        :param origin_request_policy_config: An origin request policy configuration.
        :param id: The unique identifier for the origin request policy that you are
        updating.
        :param if_match: The version of the origin request policy that you are updating.
        :returns: UpdateOriginRequestPolicyResult
        :raises AccessDenied:
        :raises IllegalUpdate:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchOriginRequestPolicy:
        :raises PreconditionFailed:
        :raises OriginRequestPolicyAlreadyExists:
        :raises TooManyHeadersInOriginRequestPolicy:
        :raises TooManyCookiesInOriginRequestPolicy:
        :raises TooManyQueryStringsInOriginRequestPolicy:
        """
        raise NotImplementedError

    @handler("UpdatePublicKey")
    def update_public_key(
        self,
        context: RequestContext,
        public_key_config: PublicKeyConfig,
        id: string,
        if_match: string = None,
    ) -> UpdatePublicKeyResult:
        """Update public key information. Note that the only value you can change
        is the comment.

        :param public_key_config: A public key configuration.
        :param id: The identifier of the public key that you are updating.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        public key to update.
        :returns: UpdatePublicKeyResult
        :raises AccessDenied:
        :raises CannotChangeImmutablePublicKeyFields:
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises IllegalUpdate:
        :raises NoSuchPublicKey:
        :raises PreconditionFailed:
        """
        raise NotImplementedError

    @handler("UpdateRealtimeLogConfig")
    def update_realtime_log_config(
        self,
        context: RequestContext,
        end_points: EndPointList = None,
        fields: FieldList = None,
        name: string = None,
        arn: string = None,
        sampling_rate: long = None,
    ) -> UpdateRealtimeLogConfigResult:
        """Updates a real-time log configuration.

        When you update a real-time log configuration, all the parameters are
        updated with the values provided in the request. You cannot update some
        parameters independent of others. To update a real-time log
        configuration:

        #. Call ``GetRealtimeLogConfig`` to get the current real-time log
           configuration.

        #. Locally modify the parameters in the real-time log configuration that
           you want to update.

        #. Call this API (``UpdateRealtimeLogConfig``) by providing the entire
           real-time log configuration, including the parameters that you
           modified and those that you didn’t.

        You cannot update a real-time log configuration’s ``Name`` or ``ARN``.

        :param end_points: Contains information about the Amazon Kinesis data stream where you are
        sending real-time log data.
        :param fields: A list of fields to include in each real-time log record.
        :param name: The name for this real-time log configuration.
        :param arn: The Amazon Resource Name (ARN) for this real-time log configuration.
        :param sampling_rate: The sampling rate for this real-time log configuration.
        :returns: UpdateRealtimeLogConfigResult
        :raises NoSuchRealtimeLogConfig:
        :raises InvalidArgument:
        :raises AccessDenied:
        """
        raise NotImplementedError

    @handler("UpdateResponseHeadersPolicy")
    def update_response_headers_policy(
        self,
        context: RequestContext,
        response_headers_policy_config: ResponseHeadersPolicyConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateResponseHeadersPolicyResult:
        """Updates a response headers policy.

        When you update a response headers policy, the entire policy is
        replaced. You cannot update some policy fields independent of others. To
        update a response headers policy configuration:

        #. Use ``GetResponseHeadersPolicyConfig`` to get the current policy’s
           configuration.

        #. Modify the fields in the response headers policy configuration that
           you want to update.

        #. Call ``UpdateResponseHeadersPolicy``, providing the entire response
           headers policy configuration, including the fields that you modified
           and those that you didn’t.

        :param response_headers_policy_config: A response headers policy configuration.
        :param id: The identifier for the response headers policy that you are updating.
        :param if_match: The version of the response headers policy that you are updating.
        :returns: UpdateResponseHeadersPolicyResult
        :raises AccessDenied:
        :raises IllegalUpdate:
        :raises InconsistentQuantities:
        :raises InvalidArgument:
        :raises InvalidIfMatchVersion:
        :raises NoSuchResponseHeadersPolicy:
        :raises PreconditionFailed:
        :raises ResponseHeadersPolicyAlreadyExists:
        :raises TooManyCustomHeadersInResponseHeadersPolicy:
        """
        raise NotImplementedError

    @handler("UpdateStreamingDistribution")
    def update_streaming_distribution(
        self,
        context: RequestContext,
        streaming_distribution_config: StreamingDistributionConfig,
        id: string,
        if_match: string = None,
    ) -> UpdateStreamingDistributionResult:
        """Update a streaming distribution.

        :param streaming_distribution_config: The streaming distribution's configuration information.
        :param id: The streaming distribution's id.
        :param if_match: The value of the ``ETag`` header that you received when retrieving the
        streaming distribution's configuration.
        :returns: UpdateStreamingDistributionResult
        :raises AccessDenied:
        :raises CNAMEAlreadyExists:
        :raises IllegalUpdate:
        :raises InvalidIfMatchVersion:
        :raises MissingBody:
        :raises NoSuchStreamingDistribution:
        :raises PreconditionFailed:
        :raises TooManyStreamingDistributionCNAMEs:
        :raises InvalidArgument:
        :raises InvalidOriginAccessIdentity:
        :raises TooManyTrustedSigners:
        :raises TrustedSignerDoesNotExist:
        :raises InconsistentQuantities:
        """
        raise NotImplementedError
