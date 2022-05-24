import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Arch = str
Arn = str
AttributeKey = str
AttributeValue = str
Author = str
Base64 = str
BaseScore = float
BatchedOperationLayerDigest = str
Epoch = int
ExceptionMessage = str
FilePath = str
FindingArn = str
FindingDescription = str
FindingName = str
ForceFlag = bool
ImageCount = int
ImageDigest = str
ImageFailureReason = str
ImageManifest = str
ImageTag = str
KmsError = str
KmsKey = str
LayerDigest = str
LayerFailureReason = str
LifecyclePolicyRulePriority = int
LifecyclePolicyText = str
LifecyclePreviewMaxResults = int
MaxResults = int
MediaType = str
Metric = str
NextToken = str
PackageManager = str
Platform = str
ProxyEndpoint = str
PullThroughCacheRuleRepositoryPrefix = str
Reason = str
RecommendationText = str
Region = str
RegistryId = str
RegistryPolicyText = str
RelatedVulnerability = str
Release = str
ReplicationError = str
RepositoryFilterValue = str
RepositoryName = str
RepositoryPolicyText = str
ResourceId = str
ScanOnPushFlag = bool
ScanStatusDescription = str
ScanningConfigurationFailureReason = str
ScanningRepositoryFilterValue = str
Score = float
ScoringVector = str
Severity = str
SeverityCount = int
Source = str
SourceLayerHash = str
Status = str
TagKey = str
TagValue = str
Title = str
Type = str
UploadId = str
Url = str
Version = str
VulnerabilityId = str
VulnerablePackageName = str


class EncryptionType(str):
    AES256 = "AES256"
    KMS = "KMS"


class FindingSeverity(str):
    INFORMATIONAL = "INFORMATIONAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNDEFINED = "UNDEFINED"


class ImageActionType(str):
    EXPIRE = "EXPIRE"


class ImageFailureCode(str):
    InvalidImageDigest = "InvalidImageDigest"
    InvalidImageTag = "InvalidImageTag"
    ImageTagDoesNotMatchDigest = "ImageTagDoesNotMatchDigest"
    ImageNotFound = "ImageNotFound"
    MissingDigestAndTag = "MissingDigestAndTag"
    ImageReferencedByManifestList = "ImageReferencedByManifestList"
    KmsError = "KmsError"


class ImageTagMutability(str):
    MUTABLE = "MUTABLE"
    IMMUTABLE = "IMMUTABLE"


class LayerAvailability(str):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class LayerFailureCode(str):
    InvalidLayerDigest = "InvalidLayerDigest"
    MissingLayerDigest = "MissingLayerDigest"


class LifecyclePolicyPreviewStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class ReplicationStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class RepositoryFilterType(str):
    PREFIX_MATCH = "PREFIX_MATCH"


class ScanFrequency(str):
    SCAN_ON_PUSH = "SCAN_ON_PUSH"
    CONTINUOUS_SCAN = "CONTINUOUS_SCAN"
    MANUAL = "MANUAL"


class ScanStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    UNSUPPORTED_IMAGE = "UNSUPPORTED_IMAGE"
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    SCAN_ELIGIBILITY_EXPIRED = "SCAN_ELIGIBILITY_EXPIRED"
    FINDINGS_UNAVAILABLE = "FINDINGS_UNAVAILABLE"


class ScanType(str):
    BASIC = "BASIC"
    ENHANCED = "ENHANCED"


class ScanningConfigurationFailureCode(str):
    REPOSITORY_NOT_FOUND = "REPOSITORY_NOT_FOUND"


class ScanningRepositoryFilterType(str):
    WILDCARD = "WILDCARD"


class TagStatus(str):
    TAGGED = "TAGGED"
    UNTAGGED = "UNTAGGED"
    ANY = "ANY"


class EmptyUploadException(ServiceException):
    """The specified layer upload does not contain any layer parts."""

    message: Optional[ExceptionMessage]


class ImageAlreadyExistsException(ServiceException):
    """The specified image has already been pushed, and there were no changes
    to the manifest or image tag after the last push.
    """

    message: Optional[ExceptionMessage]


class ImageDigestDoesNotMatchException(ServiceException):
    """The specified image digest does not match the digest that Amazon ECR
    calculated for the image.
    """

    message: Optional[ExceptionMessage]


class ImageNotFoundException(ServiceException):
    """The image requested does not exist in the specified repository."""

    message: Optional[ExceptionMessage]


class ImageTagAlreadyExistsException(ServiceException):
    """The specified image is tagged with a tag that already exists. The
    repository is configured for tag immutability.
    """

    message: Optional[ExceptionMessage]


class InvalidLayerException(ServiceException):
    """The layer digest calculation performed by Amazon ECR upon receipt of the
    image layer does not match the digest specified.
    """

    message: Optional[ExceptionMessage]


PartSize = int


class InvalidLayerPartException(ServiceException):
    """The layer part size is not valid, or the first byte specified is not
    consecutive to the last byte of a previous layer part upload.
    """

    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    uploadId: Optional[UploadId]
    lastValidByteReceived: Optional[PartSize]
    message: Optional[ExceptionMessage]


class InvalidParameterException(ServiceException):
    """The specified parameter is invalid. Review the available parameters for
    the API request.
    """

    message: Optional[ExceptionMessage]


class InvalidTagParameterException(ServiceException):
    """An invalid parameter has been specified. Tag keys can have a maximum
    character length of 128 characters, and tag values can have a maximum
    length of 256 characters.
    """

    message: Optional[ExceptionMessage]


class KmsException(ServiceException):
    """The operation failed due to a KMS exception."""

    message: Optional[ExceptionMessage]
    kmsError: Optional[KmsError]


class LayerAlreadyExistsException(ServiceException):
    """The image layer already exists in the associated repository."""

    message: Optional[ExceptionMessage]


class LayerInaccessibleException(ServiceException):
    """The specified layer is not available because it is not associated with
    an image. Unassociated image layers may be cleaned up at any time.
    """

    message: Optional[ExceptionMessage]


class LayerPartTooSmallException(ServiceException):
    """Layer parts must be at least 5 MiB in size."""

    message: Optional[ExceptionMessage]


class LayersNotFoundException(ServiceException):
    """The specified layers could not be found, or the specified layer is not
    valid for this repository.
    """

    message: Optional[ExceptionMessage]


class LifecyclePolicyNotFoundException(ServiceException):
    """The lifecycle policy could not be found, and no policy is set to the
    repository.
    """

    message: Optional[ExceptionMessage]


class LifecyclePolicyPreviewInProgressException(ServiceException):
    """The previous lifecycle policy preview request has not completed. Wait
    and try again.
    """

    message: Optional[ExceptionMessage]


class LifecyclePolicyPreviewNotFoundException(ServiceException):
    """There is no dry run for this repository."""

    message: Optional[ExceptionMessage]


class LimitExceededException(ServiceException):
    """The operation did not succeed because it would have exceeded a service
    limit for your account. For more information, see `Amazon ECR service
    quotas <https://docs.aws.amazon.com/AmazonECR/latest/userguide/service-quotas.html>`__
    in the Amazon Elastic Container Registry User Guide.
    """

    message: Optional[ExceptionMessage]


class PullThroughCacheRuleAlreadyExistsException(ServiceException):
    """A pull through cache rule with these settings already exists for the
    private registry.
    """

    message: Optional[ExceptionMessage]


class PullThroughCacheRuleNotFoundException(ServiceException):
    """The pull through cache rule was not found. Specify a valid pull through
    cache rule and try again.
    """

    message: Optional[ExceptionMessage]


class ReferencedImagesNotFoundException(ServiceException):
    """The manifest list is referencing an image that does not exist."""

    message: Optional[ExceptionMessage]


class RegistryPolicyNotFoundException(ServiceException):
    """The registry doesn't have an associated registry policy."""

    message: Optional[ExceptionMessage]


class RepositoryAlreadyExistsException(ServiceException):
    """The specified repository already exists in the specified registry."""

    message: Optional[ExceptionMessage]


class RepositoryNotEmptyException(ServiceException):
    """The specified repository contains images. To delete a repository that
    contains images, you must force the deletion with the ``force``
    parameter.
    """

    message: Optional[ExceptionMessage]


class RepositoryNotFoundException(ServiceException):
    """The specified repository could not be found. Check the spelling of the
    specified repository and ensure that you are performing operations on
    the correct registry.
    """

    message: Optional[ExceptionMessage]


class RepositoryPolicyNotFoundException(ServiceException):
    """The specified repository and registry combination does not have an
    associated repository policy.
    """

    message: Optional[ExceptionMessage]


class ScanNotFoundException(ServiceException):
    """The specified image scan could not be found. Ensure that image scanning
    is enabled on the repository and try again.
    """

    message: Optional[ExceptionMessage]


class ServerException(ServiceException):
    """These errors are usually caused by a server-side issue."""

    message: Optional[ExceptionMessage]


class TooManyTagsException(ServiceException):
    """The list of tags on the repository is over the limit. The maximum number
    of tags that can be applied to a repository is 50.
    """

    message: Optional[ExceptionMessage]


class UnsupportedImageTypeException(ServiceException):
    """The image is of a type that cannot be scanned."""

    message: Optional[ExceptionMessage]


class UnsupportedUpstreamRegistryException(ServiceException):
    """The specified upstream registry isn't supported."""

    message: Optional[ExceptionMessage]


class UploadNotFoundException(ServiceException):
    """The upload could not be found, or the specified upload ID is not valid
    for this repository.
    """

    message: Optional[ExceptionMessage]


class ValidationException(ServiceException):
    """There was an exception validating this request."""

    message: Optional[ExceptionMessage]


class Attribute(TypedDict, total=False):
    """This data type is used in the ImageScanFinding data type."""

    key: AttributeKey
    value: Optional[AttributeValue]


AttributeList = List[Attribute]
ExpirationTimestamp = datetime


class AuthorizationData(TypedDict, total=False):
    """An object representing authorization data for an Amazon ECR registry."""

    authorizationToken: Optional[Base64]
    expiresAt: Optional[ExpirationTimestamp]
    proxyEndpoint: Optional[ProxyEndpoint]


AuthorizationDataList = List[AuthorizationData]
Date = datetime
ImageTagsList = List[ImageTag]


class AwsEcrContainerImageDetails(TypedDict, total=False):
    """The image details of the Amazon ECR container image."""

    architecture: Optional[Arch]
    author: Optional[Author]
    imageHash: Optional[ImageDigest]
    imageTags: Optional[ImageTagsList]
    platform: Optional[Platform]
    pushedAt: Optional[Date]
    registry: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]


BatchedOperationLayerDigestList = List[BatchedOperationLayerDigest]


class BatchCheckLayerAvailabilityRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    layerDigests: BatchedOperationLayerDigestList


class LayerFailure(TypedDict, total=False):
    """An object representing an Amazon ECR image layer failure."""

    layerDigest: Optional[BatchedOperationLayerDigest]
    failureCode: Optional[LayerFailureCode]
    failureReason: Optional[LayerFailureReason]


LayerFailureList = List[LayerFailure]
LayerSizeInBytes = int


class Layer(TypedDict, total=False):
    """An object representing an Amazon ECR image layer."""

    layerDigest: Optional[LayerDigest]
    layerAvailability: Optional[LayerAvailability]
    layerSize: Optional[LayerSizeInBytes]
    mediaType: Optional[MediaType]


LayerList = List[Layer]


class BatchCheckLayerAvailabilityResponse(TypedDict, total=False):
    layers: Optional[LayerList]
    failures: Optional[LayerFailureList]


class ImageIdentifier(TypedDict, total=False):
    """An object with identifying information for an image in an Amazon ECR
    repository.
    """

    imageDigest: Optional[ImageDigest]
    imageTag: Optional[ImageTag]


ImageIdentifierList = List[ImageIdentifier]


class BatchDeleteImageRequest(ServiceRequest):
    """Deletes specified images within a specified repository. Images are
    specified with either the ``imageTag`` or ``imageDigest``.
    """

    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageIds: ImageIdentifierList


class ImageFailure(TypedDict, total=False):
    """An object representing an Amazon ECR image failure."""

    imageId: Optional[ImageIdentifier]
    failureCode: Optional[ImageFailureCode]
    failureReason: Optional[ImageFailureReason]


ImageFailureList = List[ImageFailure]


class BatchDeleteImageResponse(TypedDict, total=False):
    imageIds: Optional[ImageIdentifierList]
    failures: Optional[ImageFailureList]


MediaTypeList = List[MediaType]


class BatchGetImageRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageIds: ImageIdentifierList
    acceptedMediaTypes: Optional[MediaTypeList]


class Image(TypedDict, total=False):
    """An object representing an Amazon ECR image."""

    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    imageId: Optional[ImageIdentifier]
    imageManifest: Optional[ImageManifest]
    imageManifestMediaType: Optional[MediaType]


ImageList = List[Image]


class BatchGetImageResponse(TypedDict, total=False):
    images: Optional[ImageList]
    failures: Optional[ImageFailureList]


ScanningConfigurationRepositoryNameList = List[RepositoryName]


class BatchGetRepositoryScanningConfigurationRequest(ServiceRequest):
    repositoryNames: ScanningConfigurationRepositoryNameList


class RepositoryScanningConfigurationFailure(TypedDict, total=False):
    """The details about any failures associated with the scanning
    configuration of a repository.
    """

    repositoryName: Optional[RepositoryName]
    failureCode: Optional[ScanningConfigurationFailureCode]
    failureReason: Optional[ScanningConfigurationFailureReason]


RepositoryScanningConfigurationFailureList = List[RepositoryScanningConfigurationFailure]


class ScanningRepositoryFilter(TypedDict, total=False):
    """The details of a scanning repository filter. For more information on how
    to use filters, see `Using
    filters <https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html#image-scanning-filters>`__
    in the *Amazon Elastic Container Registry User Guide*.
    """

    filter: ScanningRepositoryFilterValue
    filterType: ScanningRepositoryFilterType


ScanningRepositoryFilterList = List[ScanningRepositoryFilter]


class RepositoryScanningConfiguration(TypedDict, total=False):
    """The details of the scanning configuration for a repository."""

    repositoryArn: Optional[Arn]
    repositoryName: Optional[RepositoryName]
    scanOnPush: Optional[ScanOnPushFlag]
    scanFrequency: Optional[ScanFrequency]
    appliedScanFilters: Optional[ScanningRepositoryFilterList]


RepositoryScanningConfigurationList = List[RepositoryScanningConfiguration]


class BatchGetRepositoryScanningConfigurationResponse(TypedDict, total=False):
    scanningConfigurations: Optional[RepositoryScanningConfigurationList]
    failures: Optional[RepositoryScanningConfigurationFailureList]


LayerDigestList = List[LayerDigest]


class CompleteLayerUploadRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    uploadId: UploadId
    layerDigests: LayerDigestList


class CompleteLayerUploadResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    uploadId: Optional[UploadId]
    layerDigest: Optional[LayerDigest]


class CreatePullThroughCacheRuleRequest(ServiceRequest):
    ecrRepositoryPrefix: PullThroughCacheRuleRepositoryPrefix
    upstreamRegistryUrl: Url
    registryId: Optional[RegistryId]


CreationTimestamp = datetime


class CreatePullThroughCacheRuleResponse(TypedDict, total=False):
    ecrRepositoryPrefix: Optional[PullThroughCacheRuleRepositoryPrefix]
    upstreamRegistryUrl: Optional[Url]
    createdAt: Optional[CreationTimestamp]
    registryId: Optional[RegistryId]


class EncryptionConfiguration(TypedDict, total=False):
    """The encryption configuration for the repository. This determines how the
    contents of your repository are encrypted at rest.

    By default, when no encryption configuration is set or the ``AES256``
    encryption type is used, Amazon ECR uses server-side encryption with
    Amazon S3-managed encryption keys which encrypts your data at rest using
    an AES-256 encryption algorithm. This does not require any action on
    your part.

    For more control over the encryption of the contents of your repository,
    you can use server-side encryption with Key Management Service key
    stored in Key Management Service (KMS) to encrypt your images. For more
    information, see `Amazon ECR encryption at
    rest <https://docs.aws.amazon.com/AmazonECR/latest/userguide/encryption-at-rest.html>`__
    in the *Amazon Elastic Container Registry User Guide*.
    """

    encryptionType: EncryptionType
    kmsKey: Optional[KmsKey]


class ImageScanningConfiguration(TypedDict, total=False):
    """The image scanning configuration for a repository."""

    scanOnPush: Optional[ScanOnPushFlag]


class Tag(TypedDict, total=False):
    """The metadata to apply to a resource to help you categorize and organize
    them. Each tag consists of a key and a value, both of which you define.
    Tag keys can have a maximum character length of 128 characters, and tag
    values can have a maximum length of 256 characters.
    """

    Key: Optional[TagKey]
    Value: Optional[TagValue]


TagList = List[Tag]


class CreateRepositoryRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    tags: Optional[TagList]
    imageTagMutability: Optional[ImageTagMutability]
    imageScanningConfiguration: Optional[ImageScanningConfiguration]
    encryptionConfiguration: Optional[EncryptionConfiguration]


class Repository(TypedDict, total=False):
    """An object representing a repository."""

    repositoryArn: Optional[Arn]
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    repositoryUri: Optional[Url]
    createdAt: Optional[CreationTimestamp]
    imageTagMutability: Optional[ImageTagMutability]
    imageScanningConfiguration: Optional[ImageScanningConfiguration]
    encryptionConfiguration: Optional[EncryptionConfiguration]


class CreateRepositoryResponse(TypedDict, total=False):
    repository: Optional[Repository]


class CvssScore(TypedDict, total=False):
    """The CVSS score for a finding."""

    baseScore: Optional[BaseScore]
    scoringVector: Optional[ScoringVector]
    source: Optional[Source]
    version: Optional[Version]


class CvssScoreAdjustment(TypedDict, total=False):
    """Details on adjustments Amazon Inspector made to the CVSS score for a
    finding.
    """

    metric: Optional[Metric]
    reason: Optional[Reason]


CvssScoreAdjustmentList = List[CvssScoreAdjustment]


class CvssScoreDetails(TypedDict, total=False):
    """Information about the CVSS score."""

    adjustments: Optional[CvssScoreAdjustmentList]
    score: Optional[Score]
    scoreSource: Optional[Source]
    scoringVector: Optional[ScoringVector]
    version: Optional[Version]


CvssScoreList = List[CvssScore]


class DeleteLifecyclePolicyRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName


EvaluationTimestamp = datetime


class DeleteLifecyclePolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    lifecyclePolicyText: Optional[LifecyclePolicyText]
    lastEvaluatedAt: Optional[EvaluationTimestamp]


class DeletePullThroughCacheRuleRequest(ServiceRequest):
    ecrRepositoryPrefix: PullThroughCacheRuleRepositoryPrefix
    registryId: Optional[RegistryId]


class DeletePullThroughCacheRuleResponse(TypedDict, total=False):
    ecrRepositoryPrefix: Optional[PullThroughCacheRuleRepositoryPrefix]
    upstreamRegistryUrl: Optional[Url]
    createdAt: Optional[CreationTimestamp]
    registryId: Optional[RegistryId]


class DeleteRegistryPolicyRequest(ServiceRequest):
    pass


class DeleteRegistryPolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    policyText: Optional[RegistryPolicyText]


class DeleteRepositoryPolicyRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName


class DeleteRepositoryPolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    policyText: Optional[RepositoryPolicyText]


class DeleteRepositoryRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    force: Optional[ForceFlag]


class DeleteRepositoryResponse(TypedDict, total=False):
    repository: Optional[Repository]


class DescribeImageReplicationStatusRequest(ServiceRequest):
    repositoryName: RepositoryName
    imageId: ImageIdentifier
    registryId: Optional[RegistryId]


class ImageReplicationStatus(TypedDict, total=False):
    """The status of the replication process for an image."""

    region: Optional[Region]
    registryId: Optional[RegistryId]
    status: Optional[ReplicationStatus]
    failureCode: Optional[ReplicationError]


ImageReplicationStatusList = List[ImageReplicationStatus]


class DescribeImageReplicationStatusResponse(TypedDict, total=False):
    repositoryName: Optional[RepositoryName]
    imageId: Optional[ImageIdentifier]
    replicationStatuses: Optional[ImageReplicationStatusList]


class DescribeImageScanFindingsRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageId: ImageIdentifier
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ScoreDetails(TypedDict, total=False):
    """Information about the Amazon Inspector score given to a finding."""

    cvss: Optional[CvssScoreDetails]


Tags = Dict[TagKey, TagValue]


class ResourceDetails(TypedDict, total=False):
    """Contains details about the resource involved in the finding."""

    awsEcrContainerImage: Optional[AwsEcrContainerImageDetails]


Resource = TypedDict(
    "Resource",
    {
        "details": Optional[ResourceDetails],
        "id": Optional[ResourceId],
        "tags": Optional[Tags],
        "type": Optional[Type],
    },
    total=False,
)
ResourceList = List[Resource]


class Recommendation(TypedDict, total=False):
    """Details about the recommended course of action to remediate the finding."""

    url: Optional[Url]
    text: Optional[RecommendationText]


class Remediation(TypedDict, total=False):
    """Information on how to remediate a finding."""

    recommendation: Optional[Recommendation]


class VulnerablePackage(TypedDict, total=False):
    """Information on the vulnerable package identified by a finding."""

    arch: Optional[Arch]
    epoch: Optional[Epoch]
    filePath: Optional[FilePath]
    name: Optional[VulnerablePackageName]
    packageManager: Optional[PackageManager]
    release: Optional[Release]
    sourceLayerHash: Optional[SourceLayerHash]
    version: Optional[Version]


VulnerablePackagesList = List[VulnerablePackage]
RelatedVulnerabilitiesList = List[RelatedVulnerability]
ReferenceUrlsList = List[Url]


class PackageVulnerabilityDetails(TypedDict, total=False):
    """Information about a package vulnerability finding."""

    cvss: Optional[CvssScoreList]
    referenceUrls: Optional[ReferenceUrlsList]
    relatedVulnerabilities: Optional[RelatedVulnerabilitiesList]
    source: Optional[Source]
    sourceUrl: Optional[Url]
    vendorCreatedAt: Optional[Date]
    vendorSeverity: Optional[Severity]
    vendorUpdatedAt: Optional[Date]
    vulnerabilityId: Optional[VulnerabilityId]
    vulnerablePackages: Optional[VulnerablePackagesList]


EnhancedImageScanFinding = TypedDict(
    "EnhancedImageScanFinding",
    {
        "awsAccountId": Optional[RegistryId],
        "description": Optional[FindingDescription],
        "findingArn": Optional[FindingArn],
        "firstObservedAt": Optional[Date],
        "lastObservedAt": Optional[Date],
        "packageVulnerabilityDetails": Optional[PackageVulnerabilityDetails],
        "remediation": Optional[Remediation],
        "resources": Optional[ResourceList],
        "score": Optional[Score],
        "scoreDetails": Optional[ScoreDetails],
        "severity": Optional[Severity],
        "status": Optional[Status],
        "title": Optional[Title],
        "type": Optional[Type],
        "updatedAt": Optional[Date],
    },
    total=False,
)
EnhancedImageScanFindingList = List[EnhancedImageScanFinding]


class ImageScanFinding(TypedDict, total=False):
    """Contains information about an image scan finding."""

    name: Optional[FindingName]
    description: Optional[FindingDescription]
    uri: Optional[Url]
    severity: Optional[FindingSeverity]
    attributes: Optional[AttributeList]


ImageScanFindingList = List[ImageScanFinding]
FindingSeverityCounts = Dict[FindingSeverity, SeverityCount]
VulnerabilitySourceUpdateTimestamp = datetime
ScanTimestamp = datetime


class ImageScanFindings(TypedDict, total=False):
    """The details of an image scan."""

    imageScanCompletedAt: Optional[ScanTimestamp]
    vulnerabilitySourceUpdatedAt: Optional[VulnerabilitySourceUpdateTimestamp]
    findingSeverityCounts: Optional[FindingSeverityCounts]
    findings: Optional[ImageScanFindingList]
    enhancedFindings: Optional[EnhancedImageScanFindingList]


class ImageScanStatus(TypedDict, total=False):
    """The current status of an image scan."""

    status: Optional[ScanStatus]
    description: Optional[ScanStatusDescription]


class DescribeImageScanFindingsResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    imageId: Optional[ImageIdentifier]
    imageScanStatus: Optional[ImageScanStatus]
    imageScanFindings: Optional[ImageScanFindings]
    nextToken: Optional[NextToken]


class DescribeImagesFilter(TypedDict, total=False):
    """An object representing a filter on a DescribeImages operation."""

    tagStatus: Optional[TagStatus]


class DescribeImagesRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageIds: Optional[ImageIdentifierList]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]
    filter: Optional[DescribeImagesFilter]


RecordedPullTimestamp = datetime


class ImageScanFindingsSummary(TypedDict, total=False):
    """A summary of the last completed image scan."""

    imageScanCompletedAt: Optional[ScanTimestamp]
    vulnerabilitySourceUpdatedAt: Optional[VulnerabilitySourceUpdateTimestamp]
    findingSeverityCounts: Optional[FindingSeverityCounts]


PushTimestamp = datetime
ImageSizeInBytes = int
ImageTagList = List[ImageTag]


class ImageDetail(TypedDict, total=False):
    """An object that describes an image returned by a DescribeImages
    operation.
    """

    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    imageDigest: Optional[ImageDigest]
    imageTags: Optional[ImageTagList]
    imageSizeInBytes: Optional[ImageSizeInBytes]
    imagePushedAt: Optional[PushTimestamp]
    imageScanStatus: Optional[ImageScanStatus]
    imageScanFindingsSummary: Optional[ImageScanFindingsSummary]
    imageManifestMediaType: Optional[MediaType]
    artifactMediaType: Optional[MediaType]
    lastRecordedPullTime: Optional[RecordedPullTimestamp]


ImageDetailList = List[ImageDetail]


class DescribeImagesResponse(TypedDict, total=False):
    imageDetails: Optional[ImageDetailList]
    nextToken: Optional[NextToken]


PullThroughCacheRuleRepositoryPrefixList = List[PullThroughCacheRuleRepositoryPrefix]


class DescribePullThroughCacheRulesRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    ecrRepositoryPrefixes: Optional[PullThroughCacheRuleRepositoryPrefixList]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class PullThroughCacheRule(TypedDict, total=False):
    """The details of a pull through cache rule."""

    ecrRepositoryPrefix: Optional[PullThroughCacheRuleRepositoryPrefix]
    upstreamRegistryUrl: Optional[Url]
    createdAt: Optional[CreationTimestamp]
    registryId: Optional[RegistryId]


PullThroughCacheRuleList = List[PullThroughCacheRule]


class DescribePullThroughCacheRulesResponse(TypedDict, total=False):
    pullThroughCacheRules: Optional[PullThroughCacheRuleList]
    nextToken: Optional[NextToken]


class DescribeRegistryRequest(ServiceRequest):
    pass


class RepositoryFilter(TypedDict, total=False):
    """The filter settings used with image replication. Specifying a repository
    filter to a replication rule provides a method for controlling which
    repositories in a private registry are replicated. If no repository
    filter is specified, all images in the repository are replicated.
    """

    filter: RepositoryFilterValue
    filterType: RepositoryFilterType


RepositoryFilterList = List[RepositoryFilter]


class ReplicationDestination(TypedDict, total=False):
    """An array of objects representing the destination for a replication rule."""

    region: Region
    registryId: RegistryId


ReplicationDestinationList = List[ReplicationDestination]


class ReplicationRule(TypedDict, total=False):
    """An array of objects representing the replication destinations and
    repository filters for a replication configuration.
    """

    destinations: ReplicationDestinationList
    repositoryFilters: Optional[RepositoryFilterList]


ReplicationRuleList = List[ReplicationRule]


class ReplicationConfiguration(TypedDict, total=False):
    """The replication configuration for a registry."""

    rules: ReplicationRuleList


class DescribeRegistryResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    replicationConfiguration: Optional[ReplicationConfiguration]


RepositoryNameList = List[RepositoryName]


class DescribeRepositoriesRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryNames: Optional[RepositoryNameList]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


RepositoryList = List[Repository]


class DescribeRepositoriesResponse(TypedDict, total=False):
    repositories: Optional[RepositoryList]
    nextToken: Optional[NextToken]


GetAuthorizationTokenRegistryIdList = List[RegistryId]


class GetAuthorizationTokenRequest(ServiceRequest):
    registryIds: Optional[GetAuthorizationTokenRegistryIdList]


class GetAuthorizationTokenResponse(TypedDict, total=False):
    authorizationData: Optional[AuthorizationDataList]


class GetDownloadUrlForLayerRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    layerDigest: LayerDigest


class GetDownloadUrlForLayerResponse(TypedDict, total=False):
    downloadUrl: Optional[Url]
    layerDigest: Optional[LayerDigest]


class LifecyclePolicyPreviewFilter(TypedDict, total=False):
    """The filter for the lifecycle policy preview."""

    tagStatus: Optional[TagStatus]


class GetLifecyclePolicyPreviewRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageIds: Optional[ImageIdentifierList]
    nextToken: Optional[NextToken]
    maxResults: Optional[LifecyclePreviewMaxResults]
    filter: Optional[LifecyclePolicyPreviewFilter]


class LifecyclePolicyPreviewSummary(TypedDict, total=False):
    """The summary of the lifecycle policy preview request."""

    expiringImageTotalCount: Optional[ImageCount]


LifecyclePolicyRuleAction = TypedDict(
    "LifecyclePolicyRuleAction",
    {
        "type": Optional[ImageActionType],
    },
    total=False,
)


class LifecyclePolicyPreviewResult(TypedDict, total=False):
    """The result of the lifecycle policy preview."""

    imageTags: Optional[ImageTagList]
    imageDigest: Optional[ImageDigest]
    imagePushedAt: Optional[PushTimestamp]
    action: Optional[LifecyclePolicyRuleAction]
    appliedRulePriority: Optional[LifecyclePolicyRulePriority]


LifecyclePolicyPreviewResultList = List[LifecyclePolicyPreviewResult]


class GetLifecyclePolicyPreviewResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    lifecyclePolicyText: Optional[LifecyclePolicyText]
    status: Optional[LifecyclePolicyPreviewStatus]
    nextToken: Optional[NextToken]
    previewResults: Optional[LifecyclePolicyPreviewResultList]
    summary: Optional[LifecyclePolicyPreviewSummary]


class GetLifecyclePolicyRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName


class GetLifecyclePolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    lifecyclePolicyText: Optional[LifecyclePolicyText]
    lastEvaluatedAt: Optional[EvaluationTimestamp]


class GetRegistryPolicyRequest(ServiceRequest):
    pass


class GetRegistryPolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    policyText: Optional[RegistryPolicyText]


class GetRegistryScanningConfigurationRequest(ServiceRequest):
    pass


class RegistryScanningRule(TypedDict, total=False):
    """The details of a scanning rule for a private registry."""

    scanFrequency: ScanFrequency
    repositoryFilters: ScanningRepositoryFilterList


RegistryScanningRuleList = List[RegistryScanningRule]


class RegistryScanningConfiguration(TypedDict, total=False):
    """The scanning configuration for a private registry."""

    scanType: Optional[ScanType]
    rules: Optional[RegistryScanningRuleList]


class GetRegistryScanningConfigurationResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    scanningConfiguration: Optional[RegistryScanningConfiguration]


class GetRepositoryPolicyRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName


class GetRepositoryPolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    policyText: Optional[RepositoryPolicyText]


class InitiateLayerUploadRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName


class InitiateLayerUploadResponse(TypedDict, total=False):
    uploadId: Optional[UploadId]
    partSize: Optional[PartSize]


LayerPartBlob = bytes


class ListImagesFilter(TypedDict, total=False):
    """An object representing a filter on a ListImages operation."""

    tagStatus: Optional[TagStatus]


class ListImagesRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]
    filter: Optional[ListImagesFilter]


class ListImagesResponse(TypedDict, total=False):
    imageIds: Optional[ImageIdentifierList]
    nextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    resourceArn: Arn


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[TagList]


class PutImageRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageManifest: ImageManifest
    imageManifestMediaType: Optional[MediaType]
    imageTag: Optional[ImageTag]
    imageDigest: Optional[ImageDigest]


class PutImageResponse(TypedDict, total=False):
    image: Optional[Image]


class PutImageScanningConfigurationRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageScanningConfiguration: ImageScanningConfiguration


class PutImageScanningConfigurationResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    imageScanningConfiguration: Optional[ImageScanningConfiguration]


class PutImageTagMutabilityRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageTagMutability: ImageTagMutability


class PutImageTagMutabilityResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    imageTagMutability: Optional[ImageTagMutability]


class PutLifecyclePolicyRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    lifecyclePolicyText: LifecyclePolicyText


class PutLifecyclePolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    lifecyclePolicyText: Optional[LifecyclePolicyText]


class PutRegistryPolicyRequest(ServiceRequest):
    policyText: RegistryPolicyText


class PutRegistryPolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    policyText: Optional[RegistryPolicyText]


class PutRegistryScanningConfigurationRequest(ServiceRequest):
    scanType: Optional[ScanType]
    rules: Optional[RegistryScanningRuleList]


class PutRegistryScanningConfigurationResponse(TypedDict, total=False):
    registryScanningConfiguration: Optional[RegistryScanningConfiguration]


class PutReplicationConfigurationRequest(ServiceRequest):
    replicationConfiguration: ReplicationConfiguration


class PutReplicationConfigurationResponse(TypedDict, total=False):
    replicationConfiguration: Optional[ReplicationConfiguration]


class SetRepositoryPolicyRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    policyText: RepositoryPolicyText
    force: Optional[ForceFlag]


class SetRepositoryPolicyResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    policyText: Optional[RepositoryPolicyText]


class StartImageScanRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    imageId: ImageIdentifier


class StartImageScanResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    imageId: Optional[ImageIdentifier]
    imageScanStatus: Optional[ImageScanStatus]


class StartLifecyclePolicyPreviewRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    lifecyclePolicyText: Optional[LifecyclePolicyText]


class StartLifecyclePolicyPreviewResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    lifecyclePolicyText: Optional[LifecyclePolicyText]
    status: Optional[LifecyclePolicyPreviewStatus]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    resourceArn: Arn
    tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    resourceArn: Arn
    tagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UploadLayerPartRequest(ServiceRequest):
    registryId: Optional[RegistryId]
    repositoryName: RepositoryName
    uploadId: UploadId
    partFirstByte: PartSize
    partLastByte: PartSize
    layerPartBlob: LayerPartBlob


class UploadLayerPartResponse(TypedDict, total=False):
    registryId: Optional[RegistryId]
    repositoryName: Optional[RepositoryName]
    uploadId: Optional[UploadId]
    lastByteReceived: Optional[PartSize]


class EcrApi:

    service = "ecr"
    version = "2015-09-21"

    @handler("BatchCheckLayerAvailability")
    def batch_check_layer_availability(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        layer_digests: BatchedOperationLayerDigestList,
        registry_id: RegistryId = None,
    ) -> BatchCheckLayerAvailabilityResponse:
        """Checks the availability of one or more image layers in a repository.

        When an image is pushed to a repository, each image layer is checked to
        verify if it has been uploaded before. If it has been uploaded, then the
        image layer is skipped.

        This operation is used by the Amazon ECR proxy and is not generally used
        by customers for pulling and pushing images. In most cases, you should
        use the ``docker`` CLI to pull, tag, and push images.

        :param repository_name: The name of the repository that is associated with the image layers to
        check.
        :param layer_digests: The digests of the image layers to check.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the image layers to check.
        :returns: BatchCheckLayerAvailabilityResponse
        :raises RepositoryNotFoundException:
        :raises InvalidParameterException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("BatchDeleteImage")
    def batch_delete_image(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_ids: ImageIdentifierList,
        registry_id: RegistryId = None,
    ) -> BatchDeleteImageResponse:
        """Deletes a list of specified images within a repository. Images are
        specified with either an ``imageTag`` or ``imageDigest``.

        You can remove a tag from an image by specifying the image's tag in your
        request. When you remove the last tag from an image, the image is
        deleted from your repository.

        You can completely delete an image (and all of its tags) by specifying
        the image's digest in your request.

        :param repository_name: The repository that contains the image to delete.
        :param image_ids: A list of image ID references that correspond to images to delete.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the image to delete.
        :returns: BatchDeleteImageResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("BatchGetImage")
    def batch_get_image(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_ids: ImageIdentifierList,
        registry_id: RegistryId = None,
        accepted_media_types: MediaTypeList = None,
    ) -> BatchGetImageResponse:
        """Gets detailed information for an image. Images are specified with either
        an ``imageTag`` or ``imageDigest``.

        When an image is pulled, the BatchGetImage API is called once to
        retrieve the image manifest.

        :param repository_name: The repository that contains the images to describe.
        :param image_ids: A list of image ID references that correspond to images to describe.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the images to describe.
        :param accepted_media_types: The accepted media types for the request.
        :returns: BatchGetImageResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("BatchGetRepositoryScanningConfiguration")
    def batch_get_repository_scanning_configuration(
        self, context: RequestContext, repository_names: ScanningConfigurationRepositoryNameList
    ) -> BatchGetRepositoryScanningConfigurationResponse:
        """Gets the scanning configuration for one or more repositories.

        :param repository_names: One or more repository names to get the scanning configuration for.
        :returns: BatchGetRepositoryScanningConfigurationResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("CompleteLayerUpload")
    def complete_layer_upload(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        upload_id: UploadId,
        layer_digests: LayerDigestList,
        registry_id: RegistryId = None,
    ) -> CompleteLayerUploadResponse:
        """Informs Amazon ECR that the image layer upload has completed for a
        specified registry, repository name, and upload ID. You can optionally
        provide a ``sha256`` digest of the image layer for data validation
        purposes.

        When an image is pushed, the CompleteLayerUpload API is called once per
        each new image layer to verify that the upload has completed.

        This operation is used by the Amazon ECR proxy and is not generally used
        by customers for pulling and pushing images. In most cases, you should
        use the ``docker`` CLI to pull, tag, and push images.

        :param repository_name: The name of the repository to associate with the image layer.
        :param upload_id: The upload ID from a previous InitiateLayerUpload operation to associate
        with the image layer.
        :param layer_digests: The ``sha256`` digest of the image layer.
        :param registry_id: The Amazon Web Services account ID associated with the registry to which
        to upload layers.
        :returns: CompleteLayerUploadResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises UploadNotFoundException:
        :raises InvalidLayerException:
        :raises LayerPartTooSmallException:
        :raises LayerAlreadyExistsException:
        :raises EmptyUploadException:
        :raises KmsException:
        """
        raise NotImplementedError

    @handler("CreatePullThroughCacheRule")
    def create_pull_through_cache_rule(
        self,
        context: RequestContext,
        ecr_repository_prefix: PullThroughCacheRuleRepositoryPrefix,
        upstream_registry_url: Url,
        registry_id: RegistryId = None,
    ) -> CreatePullThroughCacheRuleResponse:
        """Creates a pull through cache rule. A pull through cache rule provides a
        way to cache images from an external public registry in your Amazon ECR
        private registry.

        :param ecr_repository_prefix: The repository name prefix to use when caching images from the source
        registry.
        :param upstream_registry_url: The registry URL of the upstream public registry to use as the source
        for the pull through cache rule.
        :param registry_id: The Amazon Web Services account ID associated with the registry to
        create the pull through cache rule for.
        :returns: CreatePullThroughCacheRuleResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        :raises PullThroughCacheRuleAlreadyExistsException:
        :raises UnsupportedUpstreamRegistryException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateRepository")
    def create_repository(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
        tags: TagList = None,
        image_tag_mutability: ImageTagMutability = None,
        image_scanning_configuration: ImageScanningConfiguration = None,
        encryption_configuration: EncryptionConfiguration = None,
    ) -> CreateRepositoryResponse:
        """Creates a repository. For more information, see `Amazon ECR
        repositories <https://docs.aws.amazon.com/AmazonECR/latest/userguide/Repositories.html>`__
        in the *Amazon Elastic Container Registry User Guide*.

        :param repository_name: The name to use for the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry to
        create the repository.
        :param tags: The metadata that you apply to the repository to help you categorize and
        organize them.
        :param image_tag_mutability: The tag mutability setting for the repository.
        :param image_scanning_configuration: The image scanning configuration for the repository.
        :param encryption_configuration: The encryption configuration for the repository.
        :returns: CreateRepositoryResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises InvalidTagParameterException:
        :raises TooManyTagsException:
        :raises RepositoryAlreadyExistsException:
        :raises LimitExceededException:
        :raises KmsException:
        """
        raise NotImplementedError

    @handler("DeleteLifecyclePolicy")
    def delete_lifecycle_policy(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
    ) -> DeleteLifecyclePolicyResponse:
        """Deletes the lifecycle policy associated with the specified repository.

        :param repository_name: The name of the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :returns: DeleteLifecyclePolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises LifecyclePolicyNotFoundException:
        """
        raise NotImplementedError

    @handler("DeletePullThroughCacheRule")
    def delete_pull_through_cache_rule(
        self,
        context: RequestContext,
        ecr_repository_prefix: PullThroughCacheRuleRepositoryPrefix,
        registry_id: RegistryId = None,
    ) -> DeletePullThroughCacheRuleResponse:
        """Deletes a pull through cache rule.

        :param ecr_repository_prefix: The Amazon ECR repository prefix associated with the pull through cache
        rule to delete.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the pull through cache rule.
        :returns: DeletePullThroughCacheRuleResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        :raises PullThroughCacheRuleNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteRegistryPolicy")
    def delete_registry_policy(
        self,
        context: RequestContext,
    ) -> DeleteRegistryPolicyResponse:
        """Deletes the registry permissions policy.

        :returns: DeleteRegistryPolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RegistryPolicyNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("DeleteRepository")
    def delete_repository(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
        force: ForceFlag = None,
    ) -> DeleteRepositoryResponse:
        """Deletes a repository. If the repository contains images, you must either
        delete all images in the repository or use the ``force`` option to
        delete the repository.

        :param repository_name: The name of the repository to delete.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository to delete.
        :param force: If a repository contains images, forces the deletion.
        :returns: DeleteRepositoryResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises RepositoryNotEmptyException:
        :raises KmsException:
        """
        raise NotImplementedError

    @handler("DeleteRepositoryPolicy")
    def delete_repository_policy(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
    ) -> DeleteRepositoryPolicyResponse:
        """Deletes the repository policy associated with the specified repository.

        :param repository_name: The name of the repository that is associated with the repository policy
        to delete.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository policy to delete.
        :returns: DeleteRepositoryPolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises RepositoryPolicyNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeImageReplicationStatus")
    def describe_image_replication_status(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_id: ImageIdentifier,
        registry_id: RegistryId = None,
    ) -> DescribeImageReplicationStatusResponse:
        """Returns the replication status for a specified image.

        :param repository_name: The name of the repository that the image is in.
        :param image_id: An object with identifying information for an image in an Amazon ECR
        repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry.
        :returns: DescribeImageReplicationStatusResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ImageNotFoundException:
        :raises RepositoryNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("DescribeImageScanFindings")
    def describe_image_scan_findings(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_id: ImageIdentifier,
        registry_id: RegistryId = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> DescribeImageScanFindingsResponse:
        """Returns the scan findings for the specified image.

        :param repository_name: The repository for the image for which to describe the scan findings.
        :param image_id: An object with identifying information for an image in an Amazon ECR
        repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to describe the image scan findings
        for.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeImageScanFindings`` request where ``maxResults`` was used and
        the results exceeded the value of that parameter.
        :param max_results: The maximum number of image scan results returned by
        ``DescribeImageScanFindings`` in paginated output.
        :returns: DescribeImageScanFindingsResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises ImageNotFoundException:
        :raises ScanNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("DescribeImages")
    def describe_images(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
        image_ids: ImageIdentifierList = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        filter: DescribeImagesFilter = None,
    ) -> DescribeImagesResponse:
        """Returns metadata about the images in a repository.

        Beginning with Docker version 1.9, the Docker client compresses image
        layers before pushing them to a V2 Docker registry. The output of the
        ``docker images`` command shows the uncompressed image size, so it may
        return a larger image size than the image sizes returned by
        DescribeImages.

        :param repository_name: The repository that contains the images to describe.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to describe images.
        :param image_ids: The list of image IDs for the requested repository.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeImages`` request where ``maxResults`` was used and the results
        exceeded the value of that parameter.
        :param max_results: The maximum number of repository results returned by ``DescribeImages``
        in paginated output.
        :param filter: The filter key and value with which to filter your ``DescribeImages``
        results.
        :returns: DescribeImagesResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises ImageNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribePullThroughCacheRules")
    def describe_pull_through_cache_rules(
        self,
        context: RequestContext,
        registry_id: RegistryId = None,
        ecr_repository_prefixes: PullThroughCacheRuleRepositoryPrefixList = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> DescribePullThroughCacheRulesResponse:
        """Returns the pull through cache rules for a registry.

        :param registry_id: The Amazon Web Services account ID associated with the registry to
        return the pull through cache rules for.
        :param ecr_repository_prefixes: The Amazon ECR repository prefixes associated with the pull through
        cache rules to return.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribePullThroughCacheRulesRequest`` request where ``maxResults``
        was used and the results exceeded the value of that parameter.
        :param max_results: The maximum number of pull through cache rules returned by
        ``DescribePullThroughCacheRulesRequest`` in paginated output.
        :returns: DescribePullThroughCacheRulesResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        :raises PullThroughCacheRuleNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeRegistry")
    def describe_registry(
        self,
        context: RequestContext,
    ) -> DescribeRegistryResponse:
        """Describes the settings for a registry. The replication configuration for
        a repository can be created or updated with the
        PutReplicationConfiguration API action.

        :returns: DescribeRegistryResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("DescribeRepositories")
    def describe_repositories(
        self,
        context: RequestContext,
        registry_id: RegistryId = None,
        repository_names: RepositoryNameList = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> DescribeRepositoriesResponse:
        """Describes image repositories in a registry.

        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repositories to be described.
        :param repository_names: A list of repositories to describe.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeRepositories`` request where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :param max_results: The maximum number of repository results returned by
        ``DescribeRepositories`` in paginated output.
        :returns: DescribeRepositoriesResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("GetAuthorizationToken")
    def get_authorization_token(
        self, context: RequestContext, registry_ids: GetAuthorizationTokenRegistryIdList = None
    ) -> GetAuthorizationTokenResponse:
        """Retrieves an authorization token. An authorization token represents your
        IAM authentication credentials and can be used to access any Amazon ECR
        registry that your IAM principal has access to. The authorization token
        is valid for 12 hours.

        The ``authorizationToken`` returned is a base64 encoded string that can
        be decoded and used in a ``docker login`` command to authenticate to a
        registry. The CLI offers an ``get-login-password`` command that
        simplifies the login process. For more information, see `Registry
        authentication <https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html#registry_auth>`__
        in the *Amazon Elastic Container Registry User Guide*.

        :param registry_ids: A list of Amazon Web Services account IDs that are associated with the
        registries for which to get AuthorizationData objects.
        :returns: GetAuthorizationTokenResponse
        :raises ServerException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("GetDownloadUrlForLayer")
    def get_download_url_for_layer(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        layer_digest: LayerDigest,
        registry_id: RegistryId = None,
    ) -> GetDownloadUrlForLayerResponse:
        """Retrieves the pre-signed Amazon S3 download URL corresponding to an
        image layer. You can only get URLs for image layers that are referenced
        in an image.

        When an image is pulled, the GetDownloadUrlForLayer API is called once
        per image layer that is not already cached.

        This operation is used by the Amazon ECR proxy and is not generally used
        by customers for pulling and pushing images. In most cases, you should
        use the ``docker`` CLI to pull, tag, and push images.

        :param repository_name: The name of the repository that is associated with the image layer to
        download.
        :param layer_digest: The digest of the image layer to download.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the image layer to download.
        :returns: GetDownloadUrlForLayerResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises LayersNotFoundException:
        :raises LayerInaccessibleException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("GetLifecyclePolicy")
    def get_lifecycle_policy(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
    ) -> GetLifecyclePolicyResponse:
        """Retrieves the lifecycle policy for the specified repository.

        :param repository_name: The name of the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :returns: GetLifecyclePolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises LifecyclePolicyNotFoundException:
        """
        raise NotImplementedError

    @handler("GetLifecyclePolicyPreview")
    def get_lifecycle_policy_preview(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
        image_ids: ImageIdentifierList = None,
        next_token: NextToken = None,
        max_results: LifecyclePreviewMaxResults = None,
        filter: LifecyclePolicyPreviewFilter = None,
    ) -> GetLifecyclePolicyPreviewResponse:
        """Retrieves the results of the lifecycle policy preview request for the
        specified repository.

        :param repository_name: The name of the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :param image_ids: The list of imageIDs to be included.
        :param next_token: The ``nextToken`` value returned from a previous paginated

        ``GetLifecyclePolicyPreviewRequest`` request where ``maxResults`` was
        used and the
         results exceeded the value of that parameter.
        :param max_results: The maximum number of repository results returned by
        ``GetLifecyclePolicyPreviewRequest`` in
         paginated output.
        :param filter: An optional parameter that filters results based on image tag status and
        all tags, if tagged.
        :returns: GetLifecyclePolicyPreviewResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises LifecyclePolicyPreviewNotFoundException:
        """
        raise NotImplementedError

    @handler("GetRegistryPolicy")
    def get_registry_policy(
        self,
        context: RequestContext,
    ) -> GetRegistryPolicyResponse:
        """Retrieves the permissions policy for a registry.

        :returns: GetRegistryPolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RegistryPolicyNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("GetRegistryScanningConfiguration")
    def get_registry_scanning_configuration(
        self,
        context: RequestContext,
    ) -> GetRegistryScanningConfigurationResponse:
        """Retrieves the scanning configuration for a registry.

        :returns: GetRegistryScanningConfigurationResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("GetRepositoryPolicy")
    def get_repository_policy(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
    ) -> GetRepositoryPolicyResponse:
        """Retrieves the repository policy for the specified repository.

        :param repository_name: The name of the repository with the policy to retrieve.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :returns: GetRepositoryPolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises RepositoryPolicyNotFoundException:
        """
        raise NotImplementedError

    @handler("InitiateLayerUpload")
    def initiate_layer_upload(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
    ) -> InitiateLayerUploadResponse:
        """Notifies Amazon ECR that you intend to upload an image layer.

        When an image is pushed, the InitiateLayerUpload API is called once per
        image layer that has not already been uploaded. Whether or not an image
        layer has been uploaded is determined by the BatchCheckLayerAvailability
        API action.

        This operation is used by the Amazon ECR proxy and is not generally used
        by customers for pulling and pushing images. In most cases, you should
        use the ``docker`` CLI to pull, tag, and push images.

        :param repository_name: The name of the repository to which you intend to upload layers.
        :param registry_id: The Amazon Web Services account ID associated with the registry to which
        you intend to upload layers.
        :returns: InitiateLayerUploadResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises KmsException:
        """
        raise NotImplementedError

    @handler("ListImages")
    def list_images(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        filter: ListImagesFilter = None,
    ) -> ListImagesResponse:
        """Lists all the image IDs for the specified repository.

        You can filter images based on whether or not they are tagged by using
        the ``tagStatus`` filter and specifying either ``TAGGED``, ``UNTAGGED``
        or ``ANY``. For example, you can filter your results to return only
        ``UNTAGGED`` images and then pipe that result to a BatchDeleteImage
        operation to delete them. Or, you can filter your results to return only
        ``TAGGED`` images to list all of the tags in your repository.

        :param repository_name: The repository with image IDs to be listed.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to list images.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``ListImages`` request where ``maxResults`` was used and the results
        exceeded the value of that parameter.
        :param max_results: The maximum number of image results returned by ``ListImages`` in
        paginated output.
        :param filter: The filter key and value with which to filter your ``ListImages``
        results.
        :returns: ListImagesResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: Arn
    ) -> ListTagsForResourceResponse:
        """List the tags for an Amazon ECR resource.

        :param resource_arn: The Amazon Resource Name (ARN) that identifies the resource for which to
        list the tags.
        :returns: ListTagsForResourceResponse
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("PutImage")
    def put_image(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_manifest: ImageManifest,
        registry_id: RegistryId = None,
        image_manifest_media_type: MediaType = None,
        image_tag: ImageTag = None,
        image_digest: ImageDigest = None,
    ) -> PutImageResponse:
        """Creates or updates the image manifest and tags associated with an image.

        When an image is pushed and all new image layers have been uploaded, the
        PutImage API is called once to create or update the image manifest and
        the tags associated with the image.

        This operation is used by the Amazon ECR proxy and is not generally used
        by customers for pulling and pushing images. In most cases, you should
        use the ``docker`` CLI to pull, tag, and push images.

        :param repository_name: The name of the repository in which to put the image.
        :param image_manifest: The image manifest corresponding to the image to be uploaded.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to put the image.
        :param image_manifest_media_type: The media type of the image manifest.
        :param image_tag: The tag to associate with the image.
        :param image_digest: The image digest of the image manifest corresponding to the image.
        :returns: PutImageResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises ImageAlreadyExistsException:
        :raises LayersNotFoundException:
        :raises ReferencedImagesNotFoundException:
        :raises LimitExceededException:
        :raises ImageTagAlreadyExistsException:
        :raises ImageDigestDoesNotMatchException:
        :raises KmsException:
        """
        raise NotImplementedError

    @handler("PutImageScanningConfiguration")
    def put_image_scanning_configuration(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_scanning_configuration: ImageScanningConfiguration,
        registry_id: RegistryId = None,
    ) -> PutImageScanningConfigurationResponse:
        """The ``PutImageScanningConfiguration`` API is being deprecated, in favor
        of specifying the image scanning configuration at the registry level.
        For more information, see PutRegistryScanningConfiguration.

        Updates the image scanning configuration for the specified repository.

        :param repository_name: The name of the repository in which to update the image scanning
        configuration setting.
        :param image_scanning_configuration: The image scanning configuration for the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to update the image scanning
        configuration setting.
        :returns: PutImageScanningConfigurationResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("PutImageTagMutability")
    def put_image_tag_mutability(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_tag_mutability: ImageTagMutability,
        registry_id: RegistryId = None,
    ) -> PutImageTagMutabilityResponse:
        """Updates the image tag mutability settings for the specified repository.
        For more information, see `Image tag
        mutability <https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html>`__
        in the *Amazon Elastic Container Registry User Guide*.

        :param repository_name: The name of the repository in which to update the image tag mutability
        settings.
        :param image_tag_mutability: The tag mutability setting for the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to update the image tag mutability
        settings.
        :returns: PutImageTagMutabilityResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("PutLifecyclePolicy")
    def put_lifecycle_policy(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        lifecycle_policy_text: LifecyclePolicyText,
        registry_id: RegistryId = None,
    ) -> PutLifecyclePolicyResponse:
        """Creates or updates the lifecycle policy for the specified repository.
        For more information, see `Lifecycle policy
        template <https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html>`__.

        :param repository_name: The name of the repository to receive the policy.
        :param lifecycle_policy_text: The JSON repository policy text to apply to the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :returns: PutLifecyclePolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("PutRegistryPolicy")
    def put_registry_policy(
        self, context: RequestContext, policy_text: RegistryPolicyText
    ) -> PutRegistryPolicyResponse:
        """Creates or updates the permissions policy for your registry.

        A registry policy is used to specify permissions for another Amazon Web
        Services account and is used when configuring cross-account replication.
        For more information, see `Registry
        permissions <https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry-permissions.html>`__
        in the *Amazon Elastic Container Registry User Guide*.

        :param policy_text: The JSON policy text to apply to your registry.
        :returns: PutRegistryPolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("PutRegistryScanningConfiguration")
    def put_registry_scanning_configuration(
        self,
        context: RequestContext,
        scan_type: ScanType = None,
        rules: RegistryScanningRuleList = None,
    ) -> PutRegistryScanningConfigurationResponse:
        """Creates or updates the scanning configuration for your private registry.

        :param scan_type: The scanning type to set for the registry.
        :param rules: The scanning rules to use for the registry.
        :returns: PutRegistryScanningConfigurationResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("PutReplicationConfiguration")
    def put_replication_configuration(
        self, context: RequestContext, replication_configuration: ReplicationConfiguration
    ) -> PutReplicationConfigurationResponse:
        """Creates or updates the replication configuration for a registry. The
        existing replication configuration for a repository can be retrieved
        with the DescribeRegistry API action. The first time the
        PutReplicationConfiguration API is called, a service-linked IAM role is
        created in your account for the replication process. For more
        information, see `Using service-linked roles for Amazon
        ECR <https://docs.aws.amazon.com/AmazonECR/latest/userguide/using-service-linked-roles.html>`__
        in the *Amazon Elastic Container Registry User Guide*.

        When configuring cross-account replication, the destination account must
        grant the source account permission to replicate. This permission is
        controlled using a registry permissions policy. For more information,
        see PutRegistryPolicy.

        :param replication_configuration: An object representing the replication configuration for a registry.
        :returns: PutReplicationConfigurationResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("SetRepositoryPolicy")
    def set_repository_policy(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        policy_text: RepositoryPolicyText,
        registry_id: RegistryId = None,
        force: ForceFlag = None,
    ) -> SetRepositoryPolicyResponse:
        """Applies a repository policy to the specified repository to control
        access permissions. For more information, see `Amazon ECR Repository
        policies <https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policies.html>`__
        in the *Amazon Elastic Container Registry User Guide*.

        :param repository_name: The name of the repository to receive the policy.
        :param policy_text: The JSON repository policy text to apply to the repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :param force: If the policy you are attempting to set on a repository policy would
        prevent you from setting another policy in the future, you must force
        the SetRepositoryPolicy operation.
        :returns: SetRepositoryPolicyResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        """
        raise NotImplementedError

    @handler("StartImageScan")
    def start_image_scan(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        image_id: ImageIdentifier,
        registry_id: RegistryId = None,
    ) -> StartImageScanResponse:
        """Starts an image vulnerability scan. An image scan can only be started
        once per 24 hours on an individual image. This limit includes if an
        image was scanned on initial push. For more information, see `Image
        scanning <https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html>`__
        in the *Amazon Elastic Container Registry User Guide*.

        :param repository_name: The name of the repository that contains the images to scan.
        :param image_id: An object with identifying information for an image in an Amazon ECR
        repository.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository in which to start an image scan request.
        :returns: StartImageScanResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises UnsupportedImageTypeException:
        :raises LimitExceededException:
        :raises RepositoryNotFoundException:
        :raises ImageNotFoundException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("StartLifecyclePolicyPreview")
    def start_lifecycle_policy_preview(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        registry_id: RegistryId = None,
        lifecycle_policy_text: LifecyclePolicyText = None,
    ) -> StartLifecyclePolicyPreviewResponse:
        """Starts a preview of a lifecycle policy for the specified repository.
        This allows you to see the results before associating the lifecycle
        policy with the repository.

        :param repository_name: The name of the repository to be evaluated.
        :param registry_id: The Amazon Web Services account ID associated with the registry that
        contains the repository.
        :param lifecycle_policy_text: The policy to be evaluated against.
        :returns: StartLifecyclePolicyPreviewResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises RepositoryNotFoundException:
        :raises LifecyclePolicyNotFoundException:
        :raises LifecyclePolicyPreviewInProgressException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: Arn, tags: TagList
    ) -> TagResourceResponse:
        """Adds specified tags to a resource with the specified ARN. Existing tags
        on a resource are not changed if they are not specified in the request
        parameters.

        :param resource_arn: The Amazon Resource Name (ARN) of the the resource to which to add tags.
        :param tags: The tags to add to the resource.
        :returns: TagResourceResponse
        :raises InvalidParameterException:
        :raises InvalidTagParameterException:
        :raises TooManyTagsException:
        :raises RepositoryNotFoundException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: Arn, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Deletes specified tags from a resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource from which to remove
        tags.
        :param tag_keys: The keys of the tags to be removed.
        :returns: UntagResourceResponse
        :raises InvalidParameterException:
        :raises InvalidTagParameterException:
        :raises TooManyTagsException:
        :raises RepositoryNotFoundException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UploadLayerPart")
    def upload_layer_part(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        upload_id: UploadId,
        part_first_byte: PartSize,
        part_last_byte: PartSize,
        layer_part_blob: LayerPartBlob,
        registry_id: RegistryId = None,
    ) -> UploadLayerPartResponse:
        """Uploads an image layer part to Amazon ECR.

        When an image is pushed, each new image layer is uploaded in parts. The
        maximum size of each image layer part can be 20971520 bytes (or about
        20MB). The UploadLayerPart API is called once per each new image layer
        part.

        This operation is used by the Amazon ECR proxy and is not generally used
        by customers for pulling and pushing images. In most cases, you should
        use the ``docker`` CLI to pull, tag, and push images.

        :param repository_name: The name of the repository to which you are uploading layer parts.
        :param upload_id: The upload ID from a previous InitiateLayerUpload operation to associate
        with the layer part upload.
        :param part_first_byte: The position of the first byte of the layer part witin the overall image
        layer.
        :param part_last_byte: The position of the last byte of the layer part within the overall image
        layer.
        :param layer_part_blob: The base64-encoded layer part payload.
        :param registry_id: The Amazon Web Services account ID associated with the registry to which
        you are uploading layer parts.
        :returns: UploadLayerPartResponse
        :raises ServerException:
        :raises InvalidParameterException:
        :raises InvalidLayerPartException:
        :raises RepositoryNotFoundException:
        :raises UploadNotFoundException:
        :raises LimitExceededException:
        :raises KmsException:
        """
        raise NotImplementedError
