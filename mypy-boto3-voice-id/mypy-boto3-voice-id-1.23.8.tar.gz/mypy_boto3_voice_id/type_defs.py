"""
Type annotations for voice-id service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_voice_id/type_defs/)

Usage::

    ```python
    from mypy_boto3_voice_id.type_defs import AuthenticationConfigurationTypeDef

    data: AuthenticationConfigurationTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence

from .literals import (
    AuthenticationDecisionType,
    DomainStatusType,
    DuplicateRegistrationActionType,
    ExistingEnrollmentActionType,
    FraudDetectionActionType,
    FraudDetectionDecisionType,
    FraudsterRegistrationJobStatusType,
    SpeakerEnrollmentJobStatusType,
    SpeakerStatusType,
    StreamingStatusType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AuthenticationConfigurationTypeDef",
    "ServerSideEncryptionConfigurationTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "DeleteFraudsterRequestRequestTypeDef",
    "DeleteSpeakerRequestRequestTypeDef",
    "DescribeDomainRequestRequestTypeDef",
    "DescribeFraudsterRegistrationJobRequestRequestTypeDef",
    "DescribeFraudsterRequestRequestTypeDef",
    "FraudsterTypeDef",
    "DescribeSpeakerEnrollmentJobRequestRequestTypeDef",
    "DescribeSpeakerRequestRequestTypeDef",
    "SpeakerTypeDef",
    "EnrollmentJobFraudDetectionConfigTypeDef",
    "EvaluateSessionRequestRequestTypeDef",
    "FailureDetailsTypeDef",
    "FraudDetectionConfigurationTypeDef",
    "KnownFraudsterRiskTypeDef",
    "JobProgressTypeDef",
    "InputDataConfigTypeDef",
    "OutputDataConfigTypeDef",
    "RegistrationConfigTypeDef",
    "PaginatorConfigTypeDef",
    "ListDomainsRequestRequestTypeDef",
    "ListFraudsterRegistrationJobsRequestRequestTypeDef",
    "ListSpeakerEnrollmentJobsRequestRequestTypeDef",
    "ListSpeakersRequestRequestTypeDef",
    "SpeakerSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "OptOutSpeakerRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "AuthenticationResultTypeDef",
    "DomainSummaryTypeDef",
    "DomainTypeDef",
    "UpdateDomainRequestRequestTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "DescribeFraudsterResponseTypeDef",
    "DescribeSpeakerResponseTypeDef",
    "OptOutSpeakerResponseTypeDef",
    "EnrollmentConfigTypeDef",
    "FraudRiskDetailsTypeDef",
    "FraudsterRegistrationJobSummaryTypeDef",
    "SpeakerEnrollmentJobSummaryTypeDef",
    "FraudsterRegistrationJobTypeDef",
    "StartFraudsterRegistrationJobRequestRequestTypeDef",
    "ListDomainsRequestListDomainsPaginateTypeDef",
    "ListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef",
    "ListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef",
    "ListSpeakersRequestListSpeakersPaginateTypeDef",
    "ListSpeakersResponseTypeDef",
    "ListDomainsResponseTypeDef",
    "CreateDomainResponseTypeDef",
    "DescribeDomainResponseTypeDef",
    "UpdateDomainResponseTypeDef",
    "SpeakerEnrollmentJobTypeDef",
    "StartSpeakerEnrollmentJobRequestRequestTypeDef",
    "FraudDetectionResultTypeDef",
    "ListFraudsterRegistrationJobsResponseTypeDef",
    "ListSpeakerEnrollmentJobsResponseTypeDef",
    "DescribeFraudsterRegistrationJobResponseTypeDef",
    "StartFraudsterRegistrationJobResponseTypeDef",
    "DescribeSpeakerEnrollmentJobResponseTypeDef",
    "StartSpeakerEnrollmentJobResponseTypeDef",
    "EvaluateSessionResponseTypeDef",
)

AuthenticationConfigurationTypeDef = TypedDict(
    "AuthenticationConfigurationTypeDef",
    {
        "AcceptanceThreshold": int,
    },
)

ServerSideEncryptionConfigurationTypeDef = TypedDict(
    "ServerSideEncryptionConfigurationTypeDef",
    {
        "KmsKeyId": str,
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)

DeleteFraudsterRequestRequestTypeDef = TypedDict(
    "DeleteFraudsterRequestRequestTypeDef",
    {
        "DomainId": str,
        "FraudsterId": str,
    },
)

DeleteSpeakerRequestRequestTypeDef = TypedDict(
    "DeleteSpeakerRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpeakerId": str,
    },
)

DescribeDomainRequestRequestTypeDef = TypedDict(
    "DescribeDomainRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)

DescribeFraudsterRegistrationJobRequestRequestTypeDef = TypedDict(
    "DescribeFraudsterRegistrationJobRequestRequestTypeDef",
    {
        "DomainId": str,
        "JobId": str,
    },
)

DescribeFraudsterRequestRequestTypeDef = TypedDict(
    "DescribeFraudsterRequestRequestTypeDef",
    {
        "DomainId": str,
        "FraudsterId": str,
    },
)

FraudsterTypeDef = TypedDict(
    "FraudsterTypeDef",
    {
        "CreatedAt": datetime,
        "DomainId": str,
        "GeneratedFraudsterId": str,
    },
    total=False,
)

DescribeSpeakerEnrollmentJobRequestRequestTypeDef = TypedDict(
    "DescribeSpeakerEnrollmentJobRequestRequestTypeDef",
    {
        "DomainId": str,
        "JobId": str,
    },
)

DescribeSpeakerRequestRequestTypeDef = TypedDict(
    "DescribeSpeakerRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpeakerId": str,
    },
)

SpeakerTypeDef = TypedDict(
    "SpeakerTypeDef",
    {
        "CreatedAt": datetime,
        "CustomerSpeakerId": str,
        "DomainId": str,
        "GeneratedSpeakerId": str,
        "LastAccessedAt": datetime,
        "Status": SpeakerStatusType,
        "UpdatedAt": datetime,
    },
    total=False,
)

EnrollmentJobFraudDetectionConfigTypeDef = TypedDict(
    "EnrollmentJobFraudDetectionConfigTypeDef",
    {
        "FraudDetectionAction": FraudDetectionActionType,
        "RiskThreshold": int,
    },
    total=False,
)

EvaluateSessionRequestRequestTypeDef = TypedDict(
    "EvaluateSessionRequestRequestTypeDef",
    {
        "DomainId": str,
        "SessionNameOrId": str,
    },
)

FailureDetailsTypeDef = TypedDict(
    "FailureDetailsTypeDef",
    {
        "Message": str,
        "StatusCode": int,
    },
    total=False,
)

FraudDetectionConfigurationTypeDef = TypedDict(
    "FraudDetectionConfigurationTypeDef",
    {
        "RiskThreshold": int,
    },
)

_RequiredKnownFraudsterRiskTypeDef = TypedDict(
    "_RequiredKnownFraudsterRiskTypeDef",
    {
        "RiskScore": int,
    },
)
_OptionalKnownFraudsterRiskTypeDef = TypedDict(
    "_OptionalKnownFraudsterRiskTypeDef",
    {
        "GeneratedFraudsterId": str,
    },
    total=False,
)


class KnownFraudsterRiskTypeDef(
    _RequiredKnownFraudsterRiskTypeDef, _OptionalKnownFraudsterRiskTypeDef
):
    pass


JobProgressTypeDef = TypedDict(
    "JobProgressTypeDef",
    {
        "PercentComplete": int,
    },
    total=False,
)

InputDataConfigTypeDef = TypedDict(
    "InputDataConfigTypeDef",
    {
        "S3Uri": str,
    },
)

_RequiredOutputDataConfigTypeDef = TypedDict(
    "_RequiredOutputDataConfigTypeDef",
    {
        "S3Uri": str,
    },
)
_OptionalOutputDataConfigTypeDef = TypedDict(
    "_OptionalOutputDataConfigTypeDef",
    {
        "KmsKeyId": str,
    },
    total=False,
)


class OutputDataConfigTypeDef(_RequiredOutputDataConfigTypeDef, _OptionalOutputDataConfigTypeDef):
    pass


RegistrationConfigTypeDef = TypedDict(
    "RegistrationConfigTypeDef",
    {
        "DuplicateRegistrationAction": DuplicateRegistrationActionType,
        "FraudsterSimilarityThreshold": int,
    },
    total=False,
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

ListDomainsRequestRequestTypeDef = TypedDict(
    "ListDomainsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

_RequiredListFraudsterRegistrationJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListFraudsterRegistrationJobsRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)
_OptionalListFraudsterRegistrationJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListFraudsterRegistrationJobsRequestRequestTypeDef",
    {
        "JobStatus": FraudsterRegistrationJobStatusType,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListFraudsterRegistrationJobsRequestRequestTypeDef(
    _RequiredListFraudsterRegistrationJobsRequestRequestTypeDef,
    _OptionalListFraudsterRegistrationJobsRequestRequestTypeDef,
):
    pass


_RequiredListSpeakerEnrollmentJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListSpeakerEnrollmentJobsRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)
_OptionalListSpeakerEnrollmentJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListSpeakerEnrollmentJobsRequestRequestTypeDef",
    {
        "JobStatus": SpeakerEnrollmentJobStatusType,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListSpeakerEnrollmentJobsRequestRequestTypeDef(
    _RequiredListSpeakerEnrollmentJobsRequestRequestTypeDef,
    _OptionalListSpeakerEnrollmentJobsRequestRequestTypeDef,
):
    pass


_RequiredListSpeakersRequestRequestTypeDef = TypedDict(
    "_RequiredListSpeakersRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)
_OptionalListSpeakersRequestRequestTypeDef = TypedDict(
    "_OptionalListSpeakersRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListSpeakersRequestRequestTypeDef(
    _RequiredListSpeakersRequestRequestTypeDef, _OptionalListSpeakersRequestRequestTypeDef
):
    pass


SpeakerSummaryTypeDef = TypedDict(
    "SpeakerSummaryTypeDef",
    {
        "CreatedAt": datetime,
        "CustomerSpeakerId": str,
        "DomainId": str,
        "GeneratedSpeakerId": str,
        "LastAccessedAt": datetime,
        "Status": SpeakerStatusType,
        "UpdatedAt": datetime,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

OptOutSpeakerRequestRequestTypeDef = TypedDict(
    "OptOutSpeakerRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpeakerId": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

AuthenticationResultTypeDef = TypedDict(
    "AuthenticationResultTypeDef",
    {
        "AudioAggregationEndedAt": datetime,
        "AudioAggregationStartedAt": datetime,
        "AuthenticationResultId": str,
        "Configuration": AuthenticationConfigurationTypeDef,
        "CustomerSpeakerId": str,
        "Decision": AuthenticationDecisionType,
        "GeneratedSpeakerId": str,
        "Score": int,
    },
    total=False,
)

DomainSummaryTypeDef = TypedDict(
    "DomainSummaryTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "DomainId": str,
        "DomainStatus": DomainStatusType,
        "Name": str,
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationTypeDef,
        "UpdatedAt": datetime,
    },
    total=False,
)

DomainTypeDef = TypedDict(
    "DomainTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "DomainId": str,
        "DomainStatus": DomainStatusType,
        "Name": str,
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationTypeDef,
        "UpdatedAt": datetime,
    },
    total=False,
)

_RequiredUpdateDomainRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDomainRequestRequestTypeDef",
    {
        "DomainId": str,
        "Name": str,
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationTypeDef,
    },
)
_OptionalUpdateDomainRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDomainRequestRequestTypeDef",
    {
        "Description": str,
    },
    total=False,
)


class UpdateDomainRequestRequestTypeDef(
    _RequiredUpdateDomainRequestRequestTypeDef, _OptionalUpdateDomainRequestRequestTypeDef
):
    pass


_RequiredCreateDomainRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDomainRequestRequestTypeDef",
    {
        "Name": str,
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationTypeDef,
    },
)
_OptionalCreateDomainRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDomainRequestRequestTypeDef",
    {
        "ClientToken": str,
        "Description": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDomainRequestRequestTypeDef(
    _RequiredCreateDomainRequestRequestTypeDef, _OptionalCreateDomainRequestRequestTypeDef
):
    pass


TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFraudsterResponseTypeDef = TypedDict(
    "DescribeFraudsterResponseTypeDef",
    {
        "Fraudster": FraudsterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpeakerResponseTypeDef = TypedDict(
    "DescribeSpeakerResponseTypeDef",
    {
        "Speaker": SpeakerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

OptOutSpeakerResponseTypeDef = TypedDict(
    "OptOutSpeakerResponseTypeDef",
    {
        "Speaker": SpeakerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnrollmentConfigTypeDef = TypedDict(
    "EnrollmentConfigTypeDef",
    {
        "ExistingEnrollmentAction": ExistingEnrollmentActionType,
        "FraudDetectionConfig": EnrollmentJobFraudDetectionConfigTypeDef,
    },
    total=False,
)

FraudRiskDetailsTypeDef = TypedDict(
    "FraudRiskDetailsTypeDef",
    {
        "KnownFraudsterRisk": KnownFraudsterRiskTypeDef,
    },
)

FraudsterRegistrationJobSummaryTypeDef = TypedDict(
    "FraudsterRegistrationJobSummaryTypeDef",
    {
        "CreatedAt": datetime,
        "DomainId": str,
        "EndedAt": datetime,
        "FailureDetails": FailureDetailsTypeDef,
        "JobId": str,
        "JobName": str,
        "JobProgress": JobProgressTypeDef,
        "JobStatus": FraudsterRegistrationJobStatusType,
    },
    total=False,
)

SpeakerEnrollmentJobSummaryTypeDef = TypedDict(
    "SpeakerEnrollmentJobSummaryTypeDef",
    {
        "CreatedAt": datetime,
        "DomainId": str,
        "EndedAt": datetime,
        "FailureDetails": FailureDetailsTypeDef,
        "JobId": str,
        "JobName": str,
        "JobProgress": JobProgressTypeDef,
        "JobStatus": SpeakerEnrollmentJobStatusType,
    },
    total=False,
)

FraudsterRegistrationJobTypeDef = TypedDict(
    "FraudsterRegistrationJobTypeDef",
    {
        "CreatedAt": datetime,
        "DataAccessRoleArn": str,
        "DomainId": str,
        "EndedAt": datetime,
        "FailureDetails": FailureDetailsTypeDef,
        "InputDataConfig": InputDataConfigTypeDef,
        "JobId": str,
        "JobName": str,
        "JobProgress": JobProgressTypeDef,
        "JobStatus": FraudsterRegistrationJobStatusType,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "RegistrationConfig": RegistrationConfigTypeDef,
    },
    total=False,
)

_RequiredStartFraudsterRegistrationJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartFraudsterRegistrationJobRequestRequestTypeDef",
    {
        "DataAccessRoleArn": str,
        "DomainId": str,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
    },
)
_OptionalStartFraudsterRegistrationJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartFraudsterRegistrationJobRequestRequestTypeDef",
    {
        "ClientToken": str,
        "JobName": str,
        "RegistrationConfig": RegistrationConfigTypeDef,
    },
    total=False,
)


class StartFraudsterRegistrationJobRequestRequestTypeDef(
    _RequiredStartFraudsterRegistrationJobRequestRequestTypeDef,
    _OptionalStartFraudsterRegistrationJobRequestRequestTypeDef,
):
    pass


ListDomainsRequestListDomainsPaginateTypeDef = TypedDict(
    "ListDomainsRequestListDomainsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef = (
    TypedDict(
        "_RequiredListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef",
        {
            "DomainId": str,
        },
    )
)
_OptionalListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef = (
    TypedDict(
        "_OptionalListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef",
        {
            "JobStatus": FraudsterRegistrationJobStatusType,
            "PaginationConfig": PaginatorConfigTypeDef,
        },
        total=False,
    )
)


class ListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef(
    _RequiredListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef,
    _OptionalListFraudsterRegistrationJobsRequestListFraudsterRegistrationJobsPaginateTypeDef,
):
    pass


_RequiredListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef = TypedDict(
    "_RequiredListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef",
    {
        "DomainId": str,
    },
)
_OptionalListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef = TypedDict(
    "_OptionalListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef",
    {
        "JobStatus": SpeakerEnrollmentJobStatusType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef(
    _RequiredListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef,
    _OptionalListSpeakerEnrollmentJobsRequestListSpeakerEnrollmentJobsPaginateTypeDef,
):
    pass


_RequiredListSpeakersRequestListSpeakersPaginateTypeDef = TypedDict(
    "_RequiredListSpeakersRequestListSpeakersPaginateTypeDef",
    {
        "DomainId": str,
    },
)
_OptionalListSpeakersRequestListSpeakersPaginateTypeDef = TypedDict(
    "_OptionalListSpeakersRequestListSpeakersPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListSpeakersRequestListSpeakersPaginateTypeDef(
    _RequiredListSpeakersRequestListSpeakersPaginateTypeDef,
    _OptionalListSpeakersRequestListSpeakersPaginateTypeDef,
):
    pass


ListSpeakersResponseTypeDef = TypedDict(
    "ListSpeakersResponseTypeDef",
    {
        "NextToken": str,
        "SpeakerSummaries": List[SpeakerSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDomainsResponseTypeDef = TypedDict(
    "ListDomainsResponseTypeDef",
    {
        "DomainSummaries": List[DomainSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDomainResponseTypeDef = TypedDict(
    "CreateDomainResponseTypeDef",
    {
        "Domain": DomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDomainResponseTypeDef = TypedDict(
    "DescribeDomainResponseTypeDef",
    {
        "Domain": DomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDomainResponseTypeDef = TypedDict(
    "UpdateDomainResponseTypeDef",
    {
        "Domain": DomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SpeakerEnrollmentJobTypeDef = TypedDict(
    "SpeakerEnrollmentJobTypeDef",
    {
        "CreatedAt": datetime,
        "DataAccessRoleArn": str,
        "DomainId": str,
        "EndedAt": datetime,
        "EnrollmentConfig": EnrollmentConfigTypeDef,
        "FailureDetails": FailureDetailsTypeDef,
        "InputDataConfig": InputDataConfigTypeDef,
        "JobId": str,
        "JobName": str,
        "JobProgress": JobProgressTypeDef,
        "JobStatus": SpeakerEnrollmentJobStatusType,
        "OutputDataConfig": OutputDataConfigTypeDef,
    },
    total=False,
)

_RequiredStartSpeakerEnrollmentJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartSpeakerEnrollmentJobRequestRequestTypeDef",
    {
        "DataAccessRoleArn": str,
        "DomainId": str,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
    },
)
_OptionalStartSpeakerEnrollmentJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartSpeakerEnrollmentJobRequestRequestTypeDef",
    {
        "ClientToken": str,
        "EnrollmentConfig": EnrollmentConfigTypeDef,
        "JobName": str,
    },
    total=False,
)


class StartSpeakerEnrollmentJobRequestRequestTypeDef(
    _RequiredStartSpeakerEnrollmentJobRequestRequestTypeDef,
    _OptionalStartSpeakerEnrollmentJobRequestRequestTypeDef,
):
    pass


FraudDetectionResultTypeDef = TypedDict(
    "FraudDetectionResultTypeDef",
    {
        "AudioAggregationEndedAt": datetime,
        "AudioAggregationStartedAt": datetime,
        "Configuration": FraudDetectionConfigurationTypeDef,
        "Decision": FraudDetectionDecisionType,
        "FraudDetectionResultId": str,
        "Reasons": List[Literal["KNOWN_FRAUDSTER"]],
        "RiskDetails": FraudRiskDetailsTypeDef,
    },
    total=False,
)

ListFraudsterRegistrationJobsResponseTypeDef = TypedDict(
    "ListFraudsterRegistrationJobsResponseTypeDef",
    {
        "JobSummaries": List[FraudsterRegistrationJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSpeakerEnrollmentJobsResponseTypeDef = TypedDict(
    "ListSpeakerEnrollmentJobsResponseTypeDef",
    {
        "JobSummaries": List[SpeakerEnrollmentJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFraudsterRegistrationJobResponseTypeDef = TypedDict(
    "DescribeFraudsterRegistrationJobResponseTypeDef",
    {
        "Job": FraudsterRegistrationJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartFraudsterRegistrationJobResponseTypeDef = TypedDict(
    "StartFraudsterRegistrationJobResponseTypeDef",
    {
        "Job": FraudsterRegistrationJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSpeakerEnrollmentJobResponseTypeDef = TypedDict(
    "DescribeSpeakerEnrollmentJobResponseTypeDef",
    {
        "Job": SpeakerEnrollmentJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartSpeakerEnrollmentJobResponseTypeDef = TypedDict(
    "StartSpeakerEnrollmentJobResponseTypeDef",
    {
        "Job": SpeakerEnrollmentJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EvaluateSessionResponseTypeDef = TypedDict(
    "EvaluateSessionResponseTypeDef",
    {
        "AuthenticationResult": AuthenticationResultTypeDef,
        "DomainId": str,
        "FraudDetectionResult": FraudDetectionResultTypeDef,
        "SessionId": str,
        "SessionName": str,
        "StreamingStatus": StreamingStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
