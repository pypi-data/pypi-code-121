"""
Type annotations for comprehend service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/type_defs/)

Usage::

    ```python
    from mypy_boto3_comprehend.type_defs import AugmentedManifestsListItemTypeDef

    data: AugmentedManifestsListItemTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    AugmentedManifestsDocumentTypeFormatType,
    DocumentClassifierDataFormatType,
    DocumentClassifierModeType,
    DocumentReadActionType,
    DocumentReadFeatureTypesType,
    DocumentReadModeType,
    EndpointStatusType,
    EntityRecognizerDataFormatType,
    EntityTypeType,
    InputFormatType,
    JobStatusType,
    LanguageCodeType,
    ModelStatusType,
    PartOfSpeechTagTypeType,
    PiiEntitiesDetectionMaskModeType,
    PiiEntitiesDetectionModeType,
    PiiEntityTypeType,
    SentimentTypeType,
    SplitType,
    SyntaxLanguageCodeType,
)

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AugmentedManifestsListItemTypeDef",
    "DominantLanguageTypeDef",
    "BatchDetectDominantLanguageRequestRequestTypeDef",
    "BatchItemErrorTypeDef",
    "ResponseMetadataTypeDef",
    "EntityTypeDef",
    "BatchDetectEntitiesRequestRequestTypeDef",
    "KeyPhraseTypeDef",
    "BatchDetectKeyPhrasesRequestRequestTypeDef",
    "SentimentScoreTypeDef",
    "BatchDetectSentimentRequestRequestTypeDef",
    "BatchDetectSyntaxRequestRequestTypeDef",
    "ClassifierEvaluationMetricsTypeDef",
    "ClassifyDocumentRequestRequestTypeDef",
    "DocumentClassTypeDef",
    "DocumentLabelTypeDef",
    "ContainsPiiEntitiesRequestRequestTypeDef",
    "EntityLabelTypeDef",
    "DocumentClassifierOutputDataConfigTypeDef",
    "TagTypeDef",
    "VpcConfigTypeDef",
    "DeleteDocumentClassifierRequestRequestTypeDef",
    "DeleteEndpointRequestRequestTypeDef",
    "DeleteEntityRecognizerRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DescribeDocumentClassificationJobRequestRequestTypeDef",
    "DescribeDocumentClassifierRequestRequestTypeDef",
    "DescribeDominantLanguageDetectionJobRequestRequestTypeDef",
    "DescribeEndpointRequestRequestTypeDef",
    "EndpointPropertiesTypeDef",
    "DescribeEntitiesDetectionJobRequestRequestTypeDef",
    "DescribeEntityRecognizerRequestRequestTypeDef",
    "DescribeEventsDetectionJobRequestRequestTypeDef",
    "DescribeKeyPhrasesDetectionJobRequestRequestTypeDef",
    "DescribePiiEntitiesDetectionJobRequestRequestTypeDef",
    "DescribeResourcePolicyRequestRequestTypeDef",
    "DescribeSentimentDetectionJobRequestRequestTypeDef",
    "DescribeTargetedSentimentDetectionJobRequestRequestTypeDef",
    "DescribeTopicsDetectionJobRequestRequestTypeDef",
    "DetectDominantLanguageRequestRequestTypeDef",
    "DetectEntitiesRequestRequestTypeDef",
    "DetectKeyPhrasesRequestRequestTypeDef",
    "DetectPiiEntitiesRequestRequestTypeDef",
    "PiiEntityTypeDef",
    "DetectSentimentRequestRequestTypeDef",
    "DetectSyntaxRequestRequestTypeDef",
    "DocumentClassificationJobFilterTypeDef",
    "OutputDataConfigTypeDef",
    "DocumentClassifierFilterTypeDef",
    "DocumentClassifierSummaryTypeDef",
    "DocumentReaderConfigTypeDef",
    "DominantLanguageDetectionJobFilterTypeDef",
    "EndpointFilterTypeDef",
    "EntitiesDetectionJobFilterTypeDef",
    "EntityRecognizerAnnotationsTypeDef",
    "EntityRecognizerDocumentsTypeDef",
    "EntityRecognizerEntityListTypeDef",
    "EntityRecognizerEvaluationMetricsTypeDef",
    "EntityRecognizerFilterTypeDef",
    "EntityTypesListItemTypeDef",
    "EntityTypesEvaluationMetricsTypeDef",
    "EntityRecognizerSummaryTypeDef",
    "EventsDetectionJobFilterTypeDef",
    "KeyPhrasesDetectionJobFilterTypeDef",
    "PaginatorConfigTypeDef",
    "ListDocumentClassifierSummariesRequestRequestTypeDef",
    "ListEntityRecognizerSummariesRequestRequestTypeDef",
    "PiiEntitiesDetectionJobFilterTypeDef",
    "SentimentDetectionJobFilterTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "TargetedSentimentDetectionJobFilterTypeDef",
    "TopicsDetectionJobFilterTypeDef",
    "PartOfSpeechTagTypeDef",
    "PiiOutputDataConfigTypeDef",
    "RedactionConfigTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "StopDominantLanguageDetectionJobRequestRequestTypeDef",
    "StopEntitiesDetectionJobRequestRequestTypeDef",
    "StopEventsDetectionJobRequestRequestTypeDef",
    "StopKeyPhrasesDetectionJobRequestRequestTypeDef",
    "StopPiiEntitiesDetectionJobRequestRequestTypeDef",
    "StopSentimentDetectionJobRequestRequestTypeDef",
    "StopTargetedSentimentDetectionJobRequestRequestTypeDef",
    "StopTrainingDocumentClassifierRequestRequestTypeDef",
    "StopTrainingEntityRecognizerRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateEndpointRequestRequestTypeDef",
    "DocumentClassifierInputDataConfigTypeDef",
    "BatchDetectDominantLanguageItemResultTypeDef",
    "CreateDocumentClassifierResponseTypeDef",
    "CreateEndpointResponseTypeDef",
    "CreateEntityRecognizerResponseTypeDef",
    "DescribeResourcePolicyResponseTypeDef",
    "DetectDominantLanguageResponseTypeDef",
    "ImportModelResponseTypeDef",
    "PutResourcePolicyResponseTypeDef",
    "StartDocumentClassificationJobResponseTypeDef",
    "StartDominantLanguageDetectionJobResponseTypeDef",
    "StartEntitiesDetectionJobResponseTypeDef",
    "StartEventsDetectionJobResponseTypeDef",
    "StartKeyPhrasesDetectionJobResponseTypeDef",
    "StartPiiEntitiesDetectionJobResponseTypeDef",
    "StartSentimentDetectionJobResponseTypeDef",
    "StartTargetedSentimentDetectionJobResponseTypeDef",
    "StartTopicsDetectionJobResponseTypeDef",
    "StopDominantLanguageDetectionJobResponseTypeDef",
    "StopEntitiesDetectionJobResponseTypeDef",
    "StopEventsDetectionJobResponseTypeDef",
    "StopKeyPhrasesDetectionJobResponseTypeDef",
    "StopPiiEntitiesDetectionJobResponseTypeDef",
    "StopSentimentDetectionJobResponseTypeDef",
    "StopTargetedSentimentDetectionJobResponseTypeDef",
    "BatchDetectEntitiesItemResultTypeDef",
    "DetectEntitiesResponseTypeDef",
    "BatchDetectKeyPhrasesItemResultTypeDef",
    "DetectKeyPhrasesResponseTypeDef",
    "BatchDetectSentimentItemResultTypeDef",
    "DetectSentimentResponseTypeDef",
    "ClassifierMetadataTypeDef",
    "ClassifyDocumentResponseTypeDef",
    "ContainsPiiEntitiesResponseTypeDef",
    "CreateEndpointRequestRequestTypeDef",
    "ImportModelRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "DescribeEndpointResponseTypeDef",
    "ListEndpointsResponseTypeDef",
    "DetectPiiEntitiesResponseTypeDef",
    "ListDocumentClassificationJobsRequestRequestTypeDef",
    "ListDocumentClassifiersRequestRequestTypeDef",
    "ListDocumentClassifierSummariesResponseTypeDef",
    "InputDataConfigTypeDef",
    "ListDominantLanguageDetectionJobsRequestRequestTypeDef",
    "ListEndpointsRequestRequestTypeDef",
    "ListEntitiesDetectionJobsRequestRequestTypeDef",
    "ListEntityRecognizersRequestRequestTypeDef",
    "EntityRecognizerInputDataConfigTypeDef",
    "EntityRecognizerMetadataEntityTypesListItemTypeDef",
    "ListEntityRecognizerSummariesResponseTypeDef",
    "ListEventsDetectionJobsRequestRequestTypeDef",
    "ListKeyPhrasesDetectionJobsRequestRequestTypeDef",
    "ListDocumentClassificationJobsRequestListDocumentClassificationJobsPaginateTypeDef",
    "ListDocumentClassifiersRequestListDocumentClassifiersPaginateTypeDef",
    "ListDominantLanguageDetectionJobsRequestListDominantLanguageDetectionJobsPaginateTypeDef",
    "ListEntitiesDetectionJobsRequestListEntitiesDetectionJobsPaginateTypeDef",
    "ListEntityRecognizersRequestListEntityRecognizersPaginateTypeDef",
    "ListKeyPhrasesDetectionJobsRequestListKeyPhrasesDetectionJobsPaginateTypeDef",
    "ListPiiEntitiesDetectionJobsRequestRequestTypeDef",
    "ListSentimentDetectionJobsRequestListSentimentDetectionJobsPaginateTypeDef",
    "ListSentimentDetectionJobsRequestRequestTypeDef",
    "ListTargetedSentimentDetectionJobsRequestRequestTypeDef",
    "ListTopicsDetectionJobsRequestListTopicsDetectionJobsPaginateTypeDef",
    "ListTopicsDetectionJobsRequestRequestTypeDef",
    "SyntaxTokenTypeDef",
    "CreateDocumentClassifierRequestRequestTypeDef",
    "BatchDetectDominantLanguageResponseTypeDef",
    "BatchDetectEntitiesResponseTypeDef",
    "BatchDetectKeyPhrasesResponseTypeDef",
    "BatchDetectSentimentResponseTypeDef",
    "DocumentClassifierPropertiesTypeDef",
    "DocumentClassificationJobPropertiesTypeDef",
    "DominantLanguageDetectionJobPropertiesTypeDef",
    "EntitiesDetectionJobPropertiesTypeDef",
    "EventsDetectionJobPropertiesTypeDef",
    "KeyPhrasesDetectionJobPropertiesTypeDef",
    "PiiEntitiesDetectionJobPropertiesTypeDef",
    "SentimentDetectionJobPropertiesTypeDef",
    "StartDocumentClassificationJobRequestRequestTypeDef",
    "StartDominantLanguageDetectionJobRequestRequestTypeDef",
    "StartEntitiesDetectionJobRequestRequestTypeDef",
    "StartEventsDetectionJobRequestRequestTypeDef",
    "StartKeyPhrasesDetectionJobRequestRequestTypeDef",
    "StartPiiEntitiesDetectionJobRequestRequestTypeDef",
    "StartSentimentDetectionJobRequestRequestTypeDef",
    "StartTargetedSentimentDetectionJobRequestRequestTypeDef",
    "StartTopicsDetectionJobRequestRequestTypeDef",
    "TargetedSentimentDetectionJobPropertiesTypeDef",
    "TopicsDetectionJobPropertiesTypeDef",
    "CreateEntityRecognizerRequestRequestTypeDef",
    "EntityRecognizerMetadataTypeDef",
    "BatchDetectSyntaxItemResultTypeDef",
    "DetectSyntaxResponseTypeDef",
    "DescribeDocumentClassifierResponseTypeDef",
    "ListDocumentClassifiersResponseTypeDef",
    "DescribeDocumentClassificationJobResponseTypeDef",
    "ListDocumentClassificationJobsResponseTypeDef",
    "DescribeDominantLanguageDetectionJobResponseTypeDef",
    "ListDominantLanguageDetectionJobsResponseTypeDef",
    "DescribeEntitiesDetectionJobResponseTypeDef",
    "ListEntitiesDetectionJobsResponseTypeDef",
    "DescribeEventsDetectionJobResponseTypeDef",
    "ListEventsDetectionJobsResponseTypeDef",
    "DescribeKeyPhrasesDetectionJobResponseTypeDef",
    "ListKeyPhrasesDetectionJobsResponseTypeDef",
    "DescribePiiEntitiesDetectionJobResponseTypeDef",
    "ListPiiEntitiesDetectionJobsResponseTypeDef",
    "DescribeSentimentDetectionJobResponseTypeDef",
    "ListSentimentDetectionJobsResponseTypeDef",
    "DescribeTargetedSentimentDetectionJobResponseTypeDef",
    "ListTargetedSentimentDetectionJobsResponseTypeDef",
    "DescribeTopicsDetectionJobResponseTypeDef",
    "ListTopicsDetectionJobsResponseTypeDef",
    "EntityRecognizerPropertiesTypeDef",
    "BatchDetectSyntaxResponseTypeDef",
    "DescribeEntityRecognizerResponseTypeDef",
    "ListEntityRecognizersResponseTypeDef",
)

_RequiredAugmentedManifestsListItemTypeDef = TypedDict(
    "_RequiredAugmentedManifestsListItemTypeDef",
    {
        "S3Uri": str,
        "AttributeNames": Sequence[str],
    },
)
_OptionalAugmentedManifestsListItemTypeDef = TypedDict(
    "_OptionalAugmentedManifestsListItemTypeDef",
    {
        "Split": SplitType,
        "AnnotationDataS3Uri": str,
        "SourceDocumentsS3Uri": str,
        "DocumentType": AugmentedManifestsDocumentTypeFormatType,
    },
    total=False,
)


class AugmentedManifestsListItemTypeDef(
    _RequiredAugmentedManifestsListItemTypeDef, _OptionalAugmentedManifestsListItemTypeDef
):
    pass


DominantLanguageTypeDef = TypedDict(
    "DominantLanguageTypeDef",
    {
        "LanguageCode": str,
        "Score": float,
    },
    total=False,
)

BatchDetectDominantLanguageRequestRequestTypeDef = TypedDict(
    "BatchDetectDominantLanguageRequestRequestTypeDef",
    {
        "TextList": Sequence[str],
    },
)

BatchItemErrorTypeDef = TypedDict(
    "BatchItemErrorTypeDef",
    {
        "Index": int,
        "ErrorCode": str,
        "ErrorMessage": str,
    },
    total=False,
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

EntityTypeDef = TypedDict(
    "EntityTypeDef",
    {
        "Score": float,
        "Type": EntityTypeType,
        "Text": str,
        "BeginOffset": int,
        "EndOffset": int,
    },
    total=False,
)

BatchDetectEntitiesRequestRequestTypeDef = TypedDict(
    "BatchDetectEntitiesRequestRequestTypeDef",
    {
        "TextList": Sequence[str],
        "LanguageCode": LanguageCodeType,
    },
)

KeyPhraseTypeDef = TypedDict(
    "KeyPhraseTypeDef",
    {
        "Score": float,
        "Text": str,
        "BeginOffset": int,
        "EndOffset": int,
    },
    total=False,
)

BatchDetectKeyPhrasesRequestRequestTypeDef = TypedDict(
    "BatchDetectKeyPhrasesRequestRequestTypeDef",
    {
        "TextList": Sequence[str],
        "LanguageCode": LanguageCodeType,
    },
)

SentimentScoreTypeDef = TypedDict(
    "SentimentScoreTypeDef",
    {
        "Positive": float,
        "Negative": float,
        "Neutral": float,
        "Mixed": float,
    },
    total=False,
)

BatchDetectSentimentRequestRequestTypeDef = TypedDict(
    "BatchDetectSentimentRequestRequestTypeDef",
    {
        "TextList": Sequence[str],
        "LanguageCode": LanguageCodeType,
    },
)

BatchDetectSyntaxRequestRequestTypeDef = TypedDict(
    "BatchDetectSyntaxRequestRequestTypeDef",
    {
        "TextList": Sequence[str],
        "LanguageCode": SyntaxLanguageCodeType,
    },
)

ClassifierEvaluationMetricsTypeDef = TypedDict(
    "ClassifierEvaluationMetricsTypeDef",
    {
        "Accuracy": float,
        "Precision": float,
        "Recall": float,
        "F1Score": float,
        "MicroPrecision": float,
        "MicroRecall": float,
        "MicroF1Score": float,
        "HammingLoss": float,
    },
    total=False,
)

ClassifyDocumentRequestRequestTypeDef = TypedDict(
    "ClassifyDocumentRequestRequestTypeDef",
    {
        "Text": str,
        "EndpointArn": str,
    },
)

DocumentClassTypeDef = TypedDict(
    "DocumentClassTypeDef",
    {
        "Name": str,
        "Score": float,
    },
    total=False,
)

DocumentLabelTypeDef = TypedDict(
    "DocumentLabelTypeDef",
    {
        "Name": str,
        "Score": float,
    },
    total=False,
)

ContainsPiiEntitiesRequestRequestTypeDef = TypedDict(
    "ContainsPiiEntitiesRequestRequestTypeDef",
    {
        "Text": str,
        "LanguageCode": LanguageCodeType,
    },
)

EntityLabelTypeDef = TypedDict(
    "EntityLabelTypeDef",
    {
        "Name": PiiEntityTypeType,
        "Score": float,
    },
    total=False,
)

DocumentClassifierOutputDataConfigTypeDef = TypedDict(
    "DocumentClassifierOutputDataConfigTypeDef",
    {
        "S3Uri": str,
        "KmsKeyId": str,
    },
    total=False,
)

_RequiredTagTypeDef = TypedDict(
    "_RequiredTagTypeDef",
    {
        "Key": str,
    },
)
_OptionalTagTypeDef = TypedDict(
    "_OptionalTagTypeDef",
    {
        "Value": str,
    },
    total=False,
)


class TagTypeDef(_RequiredTagTypeDef, _OptionalTagTypeDef):
    pass


VpcConfigTypeDef = TypedDict(
    "VpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)

DeleteDocumentClassifierRequestRequestTypeDef = TypedDict(
    "DeleteDocumentClassifierRequestRequestTypeDef",
    {
        "DocumentClassifierArn": str,
    },
)

DeleteEndpointRequestRequestTypeDef = TypedDict(
    "DeleteEndpointRequestRequestTypeDef",
    {
        "EndpointArn": str,
    },
)

DeleteEntityRecognizerRequestRequestTypeDef = TypedDict(
    "DeleteEntityRecognizerRequestRequestTypeDef",
    {
        "EntityRecognizerArn": str,
    },
)

_RequiredDeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
_OptionalDeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteResourcePolicyRequestRequestTypeDef",
    {
        "PolicyRevisionId": str,
    },
    total=False,
)


class DeleteResourcePolicyRequestRequestTypeDef(
    _RequiredDeleteResourcePolicyRequestRequestTypeDef,
    _OptionalDeleteResourcePolicyRequestRequestTypeDef,
):
    pass


DescribeDocumentClassificationJobRequestRequestTypeDef = TypedDict(
    "DescribeDocumentClassificationJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeDocumentClassifierRequestRequestTypeDef = TypedDict(
    "DescribeDocumentClassifierRequestRequestTypeDef",
    {
        "DocumentClassifierArn": str,
    },
)

DescribeDominantLanguageDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeDominantLanguageDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeEndpointRequestRequestTypeDef = TypedDict(
    "DescribeEndpointRequestRequestTypeDef",
    {
        "EndpointArn": str,
    },
)

EndpointPropertiesTypeDef = TypedDict(
    "EndpointPropertiesTypeDef",
    {
        "EndpointArn": str,
        "Status": EndpointStatusType,
        "Message": str,
        "ModelArn": str,
        "DesiredModelArn": str,
        "DesiredInferenceUnits": int,
        "CurrentInferenceUnits": int,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "DataAccessRoleArn": str,
        "DesiredDataAccessRoleArn": str,
    },
    total=False,
)

DescribeEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeEntitiesDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeEntityRecognizerRequestRequestTypeDef = TypedDict(
    "DescribeEntityRecognizerRequestRequestTypeDef",
    {
        "EntityRecognizerArn": str,
    },
)

DescribeEventsDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeEventsDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeKeyPhrasesDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeKeyPhrasesDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribePiiEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribePiiEntitiesDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeResourcePolicyRequestRequestTypeDef = TypedDict(
    "DescribeResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

DescribeSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeSentimentDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeTargetedSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeTargetedSentimentDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeTopicsDetectionJobRequestRequestTypeDef = TypedDict(
    "DescribeTopicsDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DetectDominantLanguageRequestRequestTypeDef = TypedDict(
    "DetectDominantLanguageRequestRequestTypeDef",
    {
        "Text": str,
    },
)

_RequiredDetectEntitiesRequestRequestTypeDef = TypedDict(
    "_RequiredDetectEntitiesRequestRequestTypeDef",
    {
        "Text": str,
    },
)
_OptionalDetectEntitiesRequestRequestTypeDef = TypedDict(
    "_OptionalDetectEntitiesRequestRequestTypeDef",
    {
        "LanguageCode": LanguageCodeType,
        "EndpointArn": str,
    },
    total=False,
)


class DetectEntitiesRequestRequestTypeDef(
    _RequiredDetectEntitiesRequestRequestTypeDef, _OptionalDetectEntitiesRequestRequestTypeDef
):
    pass


DetectKeyPhrasesRequestRequestTypeDef = TypedDict(
    "DetectKeyPhrasesRequestRequestTypeDef",
    {
        "Text": str,
        "LanguageCode": LanguageCodeType,
    },
)

DetectPiiEntitiesRequestRequestTypeDef = TypedDict(
    "DetectPiiEntitiesRequestRequestTypeDef",
    {
        "Text": str,
        "LanguageCode": LanguageCodeType,
    },
)

PiiEntityTypeDef = TypedDict(
    "PiiEntityTypeDef",
    {
        "Score": float,
        "Type": PiiEntityTypeType,
        "BeginOffset": int,
        "EndOffset": int,
    },
    total=False,
)

DetectSentimentRequestRequestTypeDef = TypedDict(
    "DetectSentimentRequestRequestTypeDef",
    {
        "Text": str,
        "LanguageCode": LanguageCodeType,
    },
)

DetectSyntaxRequestRequestTypeDef = TypedDict(
    "DetectSyntaxRequestRequestTypeDef",
    {
        "Text": str,
        "LanguageCode": SyntaxLanguageCodeType,
    },
)

DocumentClassificationJobFilterTypeDef = TypedDict(
    "DocumentClassificationJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
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


DocumentClassifierFilterTypeDef = TypedDict(
    "DocumentClassifierFilterTypeDef",
    {
        "Status": ModelStatusType,
        "DocumentClassifierName": str,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

DocumentClassifierSummaryTypeDef = TypedDict(
    "DocumentClassifierSummaryTypeDef",
    {
        "DocumentClassifierName": str,
        "NumberOfVersions": int,
        "LatestVersionCreatedAt": datetime,
        "LatestVersionName": str,
        "LatestVersionStatus": ModelStatusType,
    },
    total=False,
)

_RequiredDocumentReaderConfigTypeDef = TypedDict(
    "_RequiredDocumentReaderConfigTypeDef",
    {
        "DocumentReadAction": DocumentReadActionType,
    },
)
_OptionalDocumentReaderConfigTypeDef = TypedDict(
    "_OptionalDocumentReaderConfigTypeDef",
    {
        "DocumentReadMode": DocumentReadModeType,
        "FeatureTypes": List[DocumentReadFeatureTypesType],
    },
    total=False,
)


class DocumentReaderConfigTypeDef(
    _RequiredDocumentReaderConfigTypeDef, _OptionalDocumentReaderConfigTypeDef
):
    pass


DominantLanguageDetectionJobFilterTypeDef = TypedDict(
    "DominantLanguageDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

EndpointFilterTypeDef = TypedDict(
    "EndpointFilterTypeDef",
    {
        "ModelArn": str,
        "Status": EndpointStatusType,
        "CreationTimeBefore": Union[datetime, str],
        "CreationTimeAfter": Union[datetime, str],
    },
    total=False,
)

EntitiesDetectionJobFilterTypeDef = TypedDict(
    "EntitiesDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

_RequiredEntityRecognizerAnnotationsTypeDef = TypedDict(
    "_RequiredEntityRecognizerAnnotationsTypeDef",
    {
        "S3Uri": str,
    },
)
_OptionalEntityRecognizerAnnotationsTypeDef = TypedDict(
    "_OptionalEntityRecognizerAnnotationsTypeDef",
    {
        "TestS3Uri": str,
    },
    total=False,
)


class EntityRecognizerAnnotationsTypeDef(
    _RequiredEntityRecognizerAnnotationsTypeDef, _OptionalEntityRecognizerAnnotationsTypeDef
):
    pass


_RequiredEntityRecognizerDocumentsTypeDef = TypedDict(
    "_RequiredEntityRecognizerDocumentsTypeDef",
    {
        "S3Uri": str,
    },
)
_OptionalEntityRecognizerDocumentsTypeDef = TypedDict(
    "_OptionalEntityRecognizerDocumentsTypeDef",
    {
        "TestS3Uri": str,
        "InputFormat": InputFormatType,
    },
    total=False,
)


class EntityRecognizerDocumentsTypeDef(
    _RequiredEntityRecognizerDocumentsTypeDef, _OptionalEntityRecognizerDocumentsTypeDef
):
    pass


EntityRecognizerEntityListTypeDef = TypedDict(
    "EntityRecognizerEntityListTypeDef",
    {
        "S3Uri": str,
    },
)

EntityRecognizerEvaluationMetricsTypeDef = TypedDict(
    "EntityRecognizerEvaluationMetricsTypeDef",
    {
        "Precision": float,
        "Recall": float,
        "F1Score": float,
    },
    total=False,
)

EntityRecognizerFilterTypeDef = TypedDict(
    "EntityRecognizerFilterTypeDef",
    {
        "Status": ModelStatusType,
        "RecognizerName": str,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

EntityTypesListItemTypeDef = TypedDict(
    "EntityTypesListItemTypeDef",
    {
        "Type": str,
    },
)

EntityTypesEvaluationMetricsTypeDef = TypedDict(
    "EntityTypesEvaluationMetricsTypeDef",
    {
        "Precision": float,
        "Recall": float,
        "F1Score": float,
    },
    total=False,
)

EntityRecognizerSummaryTypeDef = TypedDict(
    "EntityRecognizerSummaryTypeDef",
    {
        "RecognizerName": str,
        "NumberOfVersions": int,
        "LatestVersionCreatedAt": datetime,
        "LatestVersionName": str,
        "LatestVersionStatus": ModelStatusType,
    },
    total=False,
)

EventsDetectionJobFilterTypeDef = TypedDict(
    "EventsDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

KeyPhrasesDetectionJobFilterTypeDef = TypedDict(
    "KeyPhrasesDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
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

ListDocumentClassifierSummariesRequestRequestTypeDef = TypedDict(
    "ListDocumentClassifierSummariesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListEntityRecognizerSummariesRequestRequestTypeDef = TypedDict(
    "ListEntityRecognizerSummariesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

PiiEntitiesDetectionJobFilterTypeDef = TypedDict(
    "PiiEntitiesDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

SentimentDetectionJobFilterTypeDef = TypedDict(
    "SentimentDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

TargetedSentimentDetectionJobFilterTypeDef = TypedDict(
    "TargetedSentimentDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

TopicsDetectionJobFilterTypeDef = TypedDict(
    "TopicsDetectionJobFilterTypeDef",
    {
        "JobName": str,
        "JobStatus": JobStatusType,
        "SubmitTimeBefore": Union[datetime, str],
        "SubmitTimeAfter": Union[datetime, str],
    },
    total=False,
)

PartOfSpeechTagTypeDef = TypedDict(
    "PartOfSpeechTagTypeDef",
    {
        "Tag": PartOfSpeechTagTypeType,
        "Score": float,
    },
    total=False,
)

_RequiredPiiOutputDataConfigTypeDef = TypedDict(
    "_RequiredPiiOutputDataConfigTypeDef",
    {
        "S3Uri": str,
    },
)
_OptionalPiiOutputDataConfigTypeDef = TypedDict(
    "_OptionalPiiOutputDataConfigTypeDef",
    {
        "KmsKeyId": str,
    },
    total=False,
)


class PiiOutputDataConfigTypeDef(
    _RequiredPiiOutputDataConfigTypeDef, _OptionalPiiOutputDataConfigTypeDef
):
    pass


RedactionConfigTypeDef = TypedDict(
    "RedactionConfigTypeDef",
    {
        "PiiEntityTypes": List[PiiEntityTypeType],
        "MaskMode": PiiEntitiesDetectionMaskModeType,
        "MaskCharacter": str,
    },
    total=False,
)

_RequiredPutResourcePolicyRequestRequestTypeDef = TypedDict(
    "_RequiredPutResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "ResourcePolicy": str,
    },
)
_OptionalPutResourcePolicyRequestRequestTypeDef = TypedDict(
    "_OptionalPutResourcePolicyRequestRequestTypeDef",
    {
        "PolicyRevisionId": str,
    },
    total=False,
)


class PutResourcePolicyRequestRequestTypeDef(
    _RequiredPutResourcePolicyRequestRequestTypeDef, _OptionalPutResourcePolicyRequestRequestTypeDef
):
    pass


StopDominantLanguageDetectionJobRequestRequestTypeDef = TypedDict(
    "StopDominantLanguageDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "StopEntitiesDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopEventsDetectionJobRequestRequestTypeDef = TypedDict(
    "StopEventsDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopKeyPhrasesDetectionJobRequestRequestTypeDef = TypedDict(
    "StopKeyPhrasesDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopPiiEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "StopPiiEntitiesDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "StopSentimentDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopTargetedSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "StopTargetedSentimentDetectionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

StopTrainingDocumentClassifierRequestRequestTypeDef = TypedDict(
    "StopTrainingDocumentClassifierRequestRequestTypeDef",
    {
        "DocumentClassifierArn": str,
    },
)

StopTrainingEntityRecognizerRequestRequestTypeDef = TypedDict(
    "StopTrainingEntityRecognizerRequestRequestTypeDef",
    {
        "EntityRecognizerArn": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

_RequiredUpdateEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateEndpointRequestRequestTypeDef",
    {
        "EndpointArn": str,
    },
)
_OptionalUpdateEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateEndpointRequestRequestTypeDef",
    {
        "DesiredModelArn": str,
        "DesiredInferenceUnits": int,
        "DesiredDataAccessRoleArn": str,
    },
    total=False,
)


class UpdateEndpointRequestRequestTypeDef(
    _RequiredUpdateEndpointRequestRequestTypeDef, _OptionalUpdateEndpointRequestRequestTypeDef
):
    pass


DocumentClassifierInputDataConfigTypeDef = TypedDict(
    "DocumentClassifierInputDataConfigTypeDef",
    {
        "DataFormat": DocumentClassifierDataFormatType,
        "S3Uri": str,
        "TestS3Uri": str,
        "LabelDelimiter": str,
        "AugmentedManifests": Sequence[AugmentedManifestsListItemTypeDef],
    },
    total=False,
)

BatchDetectDominantLanguageItemResultTypeDef = TypedDict(
    "BatchDetectDominantLanguageItemResultTypeDef",
    {
        "Index": int,
        "Languages": List[DominantLanguageTypeDef],
    },
    total=False,
)

CreateDocumentClassifierResponseTypeDef = TypedDict(
    "CreateDocumentClassifierResponseTypeDef",
    {
        "DocumentClassifierArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEndpointResponseTypeDef = TypedDict(
    "CreateEndpointResponseTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEntityRecognizerResponseTypeDef = TypedDict(
    "CreateEntityRecognizerResponseTypeDef",
    {
        "EntityRecognizerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeResourcePolicyResponseTypeDef = TypedDict(
    "DescribeResourcePolicyResponseTypeDef",
    {
        "ResourcePolicy": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "PolicyRevisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetectDominantLanguageResponseTypeDef = TypedDict(
    "DetectDominantLanguageResponseTypeDef",
    {
        "Languages": List[DominantLanguageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportModelResponseTypeDef = TypedDict(
    "ImportModelResponseTypeDef",
    {
        "ModelArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutResourcePolicyResponseTypeDef = TypedDict(
    "PutResourcePolicyResponseTypeDef",
    {
        "PolicyRevisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartDocumentClassificationJobResponseTypeDef = TypedDict(
    "StartDocumentClassificationJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartDominantLanguageDetectionJobResponseTypeDef = TypedDict(
    "StartDominantLanguageDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartEntitiesDetectionJobResponseTypeDef = TypedDict(
    "StartEntitiesDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartEventsDetectionJobResponseTypeDef = TypedDict(
    "StartEventsDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartKeyPhrasesDetectionJobResponseTypeDef = TypedDict(
    "StartKeyPhrasesDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartPiiEntitiesDetectionJobResponseTypeDef = TypedDict(
    "StartPiiEntitiesDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartSentimentDetectionJobResponseTypeDef = TypedDict(
    "StartSentimentDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartTargetedSentimentDetectionJobResponseTypeDef = TypedDict(
    "StartTargetedSentimentDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartTopicsDetectionJobResponseTypeDef = TypedDict(
    "StartTopicsDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopDominantLanguageDetectionJobResponseTypeDef = TypedDict(
    "StopDominantLanguageDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopEntitiesDetectionJobResponseTypeDef = TypedDict(
    "StopEntitiesDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopEventsDetectionJobResponseTypeDef = TypedDict(
    "StopEventsDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopKeyPhrasesDetectionJobResponseTypeDef = TypedDict(
    "StopKeyPhrasesDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopPiiEntitiesDetectionJobResponseTypeDef = TypedDict(
    "StopPiiEntitiesDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopSentimentDetectionJobResponseTypeDef = TypedDict(
    "StopSentimentDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopTargetedSentimentDetectionJobResponseTypeDef = TypedDict(
    "StopTargetedSentimentDetectionJobResponseTypeDef",
    {
        "JobId": str,
        "JobStatus": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDetectEntitiesItemResultTypeDef = TypedDict(
    "BatchDetectEntitiesItemResultTypeDef",
    {
        "Index": int,
        "Entities": List[EntityTypeDef],
    },
    total=False,
)

DetectEntitiesResponseTypeDef = TypedDict(
    "DetectEntitiesResponseTypeDef",
    {
        "Entities": List[EntityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDetectKeyPhrasesItemResultTypeDef = TypedDict(
    "BatchDetectKeyPhrasesItemResultTypeDef",
    {
        "Index": int,
        "KeyPhrases": List[KeyPhraseTypeDef],
    },
    total=False,
)

DetectKeyPhrasesResponseTypeDef = TypedDict(
    "DetectKeyPhrasesResponseTypeDef",
    {
        "KeyPhrases": List[KeyPhraseTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDetectSentimentItemResultTypeDef = TypedDict(
    "BatchDetectSentimentItemResultTypeDef",
    {
        "Index": int,
        "Sentiment": SentimentTypeType,
        "SentimentScore": SentimentScoreTypeDef,
    },
    total=False,
)

DetectSentimentResponseTypeDef = TypedDict(
    "DetectSentimentResponseTypeDef",
    {
        "Sentiment": SentimentTypeType,
        "SentimentScore": SentimentScoreTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ClassifierMetadataTypeDef = TypedDict(
    "ClassifierMetadataTypeDef",
    {
        "NumberOfLabels": int,
        "NumberOfTrainedDocuments": int,
        "NumberOfTestDocuments": int,
        "EvaluationMetrics": ClassifierEvaluationMetricsTypeDef,
    },
    total=False,
)

ClassifyDocumentResponseTypeDef = TypedDict(
    "ClassifyDocumentResponseTypeDef",
    {
        "Classes": List[DocumentClassTypeDef],
        "Labels": List[DocumentLabelTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ContainsPiiEntitiesResponseTypeDef = TypedDict(
    "ContainsPiiEntitiesResponseTypeDef",
    {
        "Labels": List[EntityLabelTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredCreateEndpointRequestRequestTypeDef",
    {
        "EndpointName": str,
        "ModelArn": str,
        "DesiredInferenceUnits": int,
    },
)
_OptionalCreateEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalCreateEndpointRequestRequestTypeDef",
    {
        "ClientRequestToken": str,
        "Tags": Sequence[TagTypeDef],
        "DataAccessRoleArn": str,
    },
    total=False,
)


class CreateEndpointRequestRequestTypeDef(
    _RequiredCreateEndpointRequestRequestTypeDef, _OptionalCreateEndpointRequestRequestTypeDef
):
    pass


_RequiredImportModelRequestRequestTypeDef = TypedDict(
    "_RequiredImportModelRequestRequestTypeDef",
    {
        "SourceModelArn": str,
    },
)
_OptionalImportModelRequestRequestTypeDef = TypedDict(
    "_OptionalImportModelRequestRequestTypeDef",
    {
        "ModelName": str,
        "VersionName": str,
        "ModelKmsKeyId": str,
        "DataAccessRoleArn": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class ImportModelRequestRequestTypeDef(
    _RequiredImportModelRequestRequestTypeDef, _OptionalImportModelRequestRequestTypeDef
):
    pass


ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "ResourceArn": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

DescribeEndpointResponseTypeDef = TypedDict(
    "DescribeEndpointResponseTypeDef",
    {
        "EndpointProperties": EndpointPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEndpointsResponseTypeDef = TypedDict(
    "ListEndpointsResponseTypeDef",
    {
        "EndpointPropertiesList": List[EndpointPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetectPiiEntitiesResponseTypeDef = TypedDict(
    "DetectPiiEntitiesResponseTypeDef",
    {
        "Entities": List[PiiEntityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDocumentClassificationJobsRequestRequestTypeDef = TypedDict(
    "ListDocumentClassificationJobsRequestRequestTypeDef",
    {
        "Filter": DocumentClassificationJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListDocumentClassifiersRequestRequestTypeDef = TypedDict(
    "ListDocumentClassifiersRequestRequestTypeDef",
    {
        "Filter": DocumentClassifierFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListDocumentClassifierSummariesResponseTypeDef = TypedDict(
    "ListDocumentClassifierSummariesResponseTypeDef",
    {
        "DocumentClassifierSummariesList": List[DocumentClassifierSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredInputDataConfigTypeDef = TypedDict(
    "_RequiredInputDataConfigTypeDef",
    {
        "S3Uri": str,
    },
)
_OptionalInputDataConfigTypeDef = TypedDict(
    "_OptionalInputDataConfigTypeDef",
    {
        "InputFormat": InputFormatType,
        "DocumentReaderConfig": DocumentReaderConfigTypeDef,
    },
    total=False,
)


class InputDataConfigTypeDef(_RequiredInputDataConfigTypeDef, _OptionalInputDataConfigTypeDef):
    pass


ListDominantLanguageDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListDominantLanguageDetectionJobsRequestRequestTypeDef",
    {
        "Filter": DominantLanguageDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListEndpointsRequestRequestTypeDef = TypedDict(
    "ListEndpointsRequestRequestTypeDef",
    {
        "Filter": EndpointFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListEntitiesDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListEntitiesDetectionJobsRequestRequestTypeDef",
    {
        "Filter": EntitiesDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListEntityRecognizersRequestRequestTypeDef = TypedDict(
    "ListEntityRecognizersRequestRequestTypeDef",
    {
        "Filter": EntityRecognizerFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

_RequiredEntityRecognizerInputDataConfigTypeDef = TypedDict(
    "_RequiredEntityRecognizerInputDataConfigTypeDef",
    {
        "EntityTypes": Sequence[EntityTypesListItemTypeDef],
    },
)
_OptionalEntityRecognizerInputDataConfigTypeDef = TypedDict(
    "_OptionalEntityRecognizerInputDataConfigTypeDef",
    {
        "DataFormat": EntityRecognizerDataFormatType,
        "Documents": EntityRecognizerDocumentsTypeDef,
        "Annotations": EntityRecognizerAnnotationsTypeDef,
        "EntityList": EntityRecognizerEntityListTypeDef,
        "AugmentedManifests": Sequence[AugmentedManifestsListItemTypeDef],
    },
    total=False,
)


class EntityRecognizerInputDataConfigTypeDef(
    _RequiredEntityRecognizerInputDataConfigTypeDef, _OptionalEntityRecognizerInputDataConfigTypeDef
):
    pass


EntityRecognizerMetadataEntityTypesListItemTypeDef = TypedDict(
    "EntityRecognizerMetadataEntityTypesListItemTypeDef",
    {
        "Type": str,
        "EvaluationMetrics": EntityTypesEvaluationMetricsTypeDef,
        "NumberOfTrainMentions": int,
    },
    total=False,
)

ListEntityRecognizerSummariesResponseTypeDef = TypedDict(
    "ListEntityRecognizerSummariesResponseTypeDef",
    {
        "EntityRecognizerSummariesList": List[EntityRecognizerSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEventsDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListEventsDetectionJobsRequestRequestTypeDef",
    {
        "Filter": EventsDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListKeyPhrasesDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListKeyPhrasesDetectionJobsRequestRequestTypeDef",
    {
        "Filter": KeyPhrasesDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListDocumentClassificationJobsRequestListDocumentClassificationJobsPaginateTypeDef = TypedDict(
    "ListDocumentClassificationJobsRequestListDocumentClassificationJobsPaginateTypeDef",
    {
        "Filter": DocumentClassificationJobFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListDocumentClassifiersRequestListDocumentClassifiersPaginateTypeDef = TypedDict(
    "ListDocumentClassifiersRequestListDocumentClassifiersPaginateTypeDef",
    {
        "Filter": DocumentClassifierFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListDominantLanguageDetectionJobsRequestListDominantLanguageDetectionJobsPaginateTypeDef = (
    TypedDict(
        "ListDominantLanguageDetectionJobsRequestListDominantLanguageDetectionJobsPaginateTypeDef",
        {
            "Filter": DominantLanguageDetectionJobFilterTypeDef,
            "PaginationConfig": PaginatorConfigTypeDef,
        },
        total=False,
    )
)

ListEntitiesDetectionJobsRequestListEntitiesDetectionJobsPaginateTypeDef = TypedDict(
    "ListEntitiesDetectionJobsRequestListEntitiesDetectionJobsPaginateTypeDef",
    {
        "Filter": EntitiesDetectionJobFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListEntityRecognizersRequestListEntityRecognizersPaginateTypeDef = TypedDict(
    "ListEntityRecognizersRequestListEntityRecognizersPaginateTypeDef",
    {
        "Filter": EntityRecognizerFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListKeyPhrasesDetectionJobsRequestListKeyPhrasesDetectionJobsPaginateTypeDef = TypedDict(
    "ListKeyPhrasesDetectionJobsRequestListKeyPhrasesDetectionJobsPaginateTypeDef",
    {
        "Filter": KeyPhrasesDetectionJobFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListPiiEntitiesDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListPiiEntitiesDetectionJobsRequestRequestTypeDef",
    {
        "Filter": PiiEntitiesDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListSentimentDetectionJobsRequestListSentimentDetectionJobsPaginateTypeDef = TypedDict(
    "ListSentimentDetectionJobsRequestListSentimentDetectionJobsPaginateTypeDef",
    {
        "Filter": SentimentDetectionJobFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSentimentDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListSentimentDetectionJobsRequestRequestTypeDef",
    {
        "Filter": SentimentDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListTargetedSentimentDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListTargetedSentimentDetectionJobsRequestRequestTypeDef",
    {
        "Filter": TargetedSentimentDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListTopicsDetectionJobsRequestListTopicsDetectionJobsPaginateTypeDef = TypedDict(
    "ListTopicsDetectionJobsRequestListTopicsDetectionJobsPaginateTypeDef",
    {
        "Filter": TopicsDetectionJobFilterTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListTopicsDetectionJobsRequestRequestTypeDef = TypedDict(
    "ListTopicsDetectionJobsRequestRequestTypeDef",
    {
        "Filter": TopicsDetectionJobFilterTypeDef,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

SyntaxTokenTypeDef = TypedDict(
    "SyntaxTokenTypeDef",
    {
        "TokenId": int,
        "Text": str,
        "BeginOffset": int,
        "EndOffset": int,
        "PartOfSpeech": PartOfSpeechTagTypeDef,
    },
    total=False,
)

_RequiredCreateDocumentClassifierRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDocumentClassifierRequestRequestTypeDef",
    {
        "DocumentClassifierName": str,
        "DataAccessRoleArn": str,
        "InputDataConfig": DocumentClassifierInputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalCreateDocumentClassifierRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDocumentClassifierRequestRequestTypeDef",
    {
        "VersionName": str,
        "Tags": Sequence[TagTypeDef],
        "OutputDataConfig": DocumentClassifierOutputDataConfigTypeDef,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Mode": DocumentClassifierModeType,
        "ModelKmsKeyId": str,
        "ModelPolicy": str,
    },
    total=False,
)


class CreateDocumentClassifierRequestRequestTypeDef(
    _RequiredCreateDocumentClassifierRequestRequestTypeDef,
    _OptionalCreateDocumentClassifierRequestRequestTypeDef,
):
    pass


BatchDetectDominantLanguageResponseTypeDef = TypedDict(
    "BatchDetectDominantLanguageResponseTypeDef",
    {
        "ResultList": List[BatchDetectDominantLanguageItemResultTypeDef],
        "ErrorList": List[BatchItemErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDetectEntitiesResponseTypeDef = TypedDict(
    "BatchDetectEntitiesResponseTypeDef",
    {
        "ResultList": List[BatchDetectEntitiesItemResultTypeDef],
        "ErrorList": List[BatchItemErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDetectKeyPhrasesResponseTypeDef = TypedDict(
    "BatchDetectKeyPhrasesResponseTypeDef",
    {
        "ResultList": List[BatchDetectKeyPhrasesItemResultTypeDef],
        "ErrorList": List[BatchItemErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDetectSentimentResponseTypeDef = TypedDict(
    "BatchDetectSentimentResponseTypeDef",
    {
        "ResultList": List[BatchDetectSentimentItemResultTypeDef],
        "ErrorList": List[BatchItemErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DocumentClassifierPropertiesTypeDef = TypedDict(
    "DocumentClassifierPropertiesTypeDef",
    {
        "DocumentClassifierArn": str,
        "LanguageCode": LanguageCodeType,
        "Status": ModelStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "TrainingStartTime": datetime,
        "TrainingEndTime": datetime,
        "InputDataConfig": DocumentClassifierInputDataConfigTypeDef,
        "OutputDataConfig": DocumentClassifierOutputDataConfigTypeDef,
        "ClassifierMetadata": ClassifierMetadataTypeDef,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Mode": DocumentClassifierModeType,
        "ModelKmsKeyId": str,
        "VersionName": str,
        "SourceModelArn": str,
    },
    total=False,
)

DocumentClassificationJobPropertiesTypeDef = TypedDict(
    "DocumentClassificationJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "DocumentClassifierArn": str,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

DominantLanguageDetectionJobPropertiesTypeDef = TypedDict(
    "DominantLanguageDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

EntitiesDetectionJobPropertiesTypeDef = TypedDict(
    "EntitiesDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "EntityRecognizerArn": str,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

EventsDetectionJobPropertiesTypeDef = TypedDict(
    "EventsDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
        "DataAccessRoleArn": str,
        "TargetEventTypes": List[str],
    },
    total=False,
)

KeyPhrasesDetectionJobPropertiesTypeDef = TypedDict(
    "KeyPhrasesDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

PiiEntitiesDetectionJobPropertiesTypeDef = TypedDict(
    "PiiEntitiesDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": PiiOutputDataConfigTypeDef,
        "RedactionConfig": RedactionConfigTypeDef,
        "LanguageCode": LanguageCodeType,
        "DataAccessRoleArn": str,
        "Mode": PiiEntitiesDetectionModeType,
    },
    total=False,
)

SentimentDetectionJobPropertiesTypeDef = TypedDict(
    "SentimentDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

_RequiredStartDocumentClassificationJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartDocumentClassificationJobRequestRequestTypeDef",
    {
        "DocumentClassifierArn": str,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
    },
)
_OptionalStartDocumentClassificationJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartDocumentClassificationJobRequestRequestTypeDef",
    {
        "JobName": str,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartDocumentClassificationJobRequestRequestTypeDef(
    _RequiredStartDocumentClassificationJobRequestRequestTypeDef,
    _OptionalStartDocumentClassificationJobRequestRequestTypeDef,
):
    pass


_RequiredStartDominantLanguageDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartDominantLanguageDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
    },
)
_OptionalStartDominantLanguageDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartDominantLanguageDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartDominantLanguageDetectionJobRequestRequestTypeDef(
    _RequiredStartDominantLanguageDetectionJobRequestRequestTypeDef,
    _OptionalStartDominantLanguageDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartEntitiesDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalStartEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartEntitiesDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "EntityRecognizerArn": str,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartEntitiesDetectionJobRequestRequestTypeDef(
    _RequiredStartEntitiesDetectionJobRequestRequestTypeDef,
    _OptionalStartEntitiesDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartEventsDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartEventsDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "LanguageCode": LanguageCodeType,
        "TargetEventTypes": Sequence[str],
    },
)
_OptionalStartEventsDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartEventsDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "ClientRequestToken": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartEventsDetectionJobRequestRequestTypeDef(
    _RequiredStartEventsDetectionJobRequestRequestTypeDef,
    _OptionalStartEventsDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartKeyPhrasesDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartKeyPhrasesDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalStartKeyPhrasesDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartKeyPhrasesDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartKeyPhrasesDetectionJobRequestRequestTypeDef(
    _RequiredStartKeyPhrasesDetectionJobRequestRequestTypeDef,
    _OptionalStartKeyPhrasesDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartPiiEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartPiiEntitiesDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "Mode": PiiEntitiesDetectionModeType,
        "DataAccessRoleArn": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalStartPiiEntitiesDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartPiiEntitiesDetectionJobRequestRequestTypeDef",
    {
        "RedactionConfig": RedactionConfigTypeDef,
        "JobName": str,
        "ClientRequestToken": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartPiiEntitiesDetectionJobRequestRequestTypeDef(
    _RequiredStartPiiEntitiesDetectionJobRequestRequestTypeDef,
    _OptionalStartPiiEntitiesDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartSentimentDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalStartSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartSentimentDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartSentimentDetectionJobRequestRequestTypeDef(
    _RequiredStartSentimentDetectionJobRequestRequestTypeDef,
    _OptionalStartSentimentDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartTargetedSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartTargetedSentimentDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalStartTargetedSentimentDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartTargetedSentimentDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartTargetedSentimentDetectionJobRequestRequestTypeDef(
    _RequiredStartTargetedSentimentDetectionJobRequestRequestTypeDef,
    _OptionalStartTargetedSentimentDetectionJobRequestRequestTypeDef,
):
    pass


_RequiredStartTopicsDetectionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartTopicsDetectionJobRequestRequestTypeDef",
    {
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "DataAccessRoleArn": str,
    },
)
_OptionalStartTopicsDetectionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartTopicsDetectionJobRequestRequestTypeDef",
    {
        "JobName": str,
        "NumberOfTopics": int,
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class StartTopicsDetectionJobRequestRequestTypeDef(
    _RequiredStartTopicsDetectionJobRequestRequestTypeDef,
    _OptionalStartTopicsDetectionJobRequestRequestTypeDef,
):
    pass


TargetedSentimentDetectionJobPropertiesTypeDef = TypedDict(
    "TargetedSentimentDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

TopicsDetectionJobPropertiesTypeDef = TypedDict(
    "TopicsDetectionJobPropertiesTypeDef",
    {
        "JobId": str,
        "JobArn": str,
        "JobName": str,
        "JobStatus": JobStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "InputDataConfig": InputDataConfigTypeDef,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "NumberOfTopics": int,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
    },
    total=False,
)

_RequiredCreateEntityRecognizerRequestRequestTypeDef = TypedDict(
    "_RequiredCreateEntityRecognizerRequestRequestTypeDef",
    {
        "RecognizerName": str,
        "DataAccessRoleArn": str,
        "InputDataConfig": EntityRecognizerInputDataConfigTypeDef,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalCreateEntityRecognizerRequestRequestTypeDef = TypedDict(
    "_OptionalCreateEntityRecognizerRequestRequestTypeDef",
    {
        "VersionName": str,
        "Tags": Sequence[TagTypeDef],
        "ClientRequestToken": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "ModelKmsKeyId": str,
        "ModelPolicy": str,
    },
    total=False,
)


class CreateEntityRecognizerRequestRequestTypeDef(
    _RequiredCreateEntityRecognizerRequestRequestTypeDef,
    _OptionalCreateEntityRecognizerRequestRequestTypeDef,
):
    pass


EntityRecognizerMetadataTypeDef = TypedDict(
    "EntityRecognizerMetadataTypeDef",
    {
        "NumberOfTrainedDocuments": int,
        "NumberOfTestDocuments": int,
        "EvaluationMetrics": EntityRecognizerEvaluationMetricsTypeDef,
        "EntityTypes": List[EntityRecognizerMetadataEntityTypesListItemTypeDef],
    },
    total=False,
)

BatchDetectSyntaxItemResultTypeDef = TypedDict(
    "BatchDetectSyntaxItemResultTypeDef",
    {
        "Index": int,
        "SyntaxTokens": List[SyntaxTokenTypeDef],
    },
    total=False,
)

DetectSyntaxResponseTypeDef = TypedDict(
    "DetectSyntaxResponseTypeDef",
    {
        "SyntaxTokens": List[SyntaxTokenTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDocumentClassifierResponseTypeDef = TypedDict(
    "DescribeDocumentClassifierResponseTypeDef",
    {
        "DocumentClassifierProperties": DocumentClassifierPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDocumentClassifiersResponseTypeDef = TypedDict(
    "ListDocumentClassifiersResponseTypeDef",
    {
        "DocumentClassifierPropertiesList": List[DocumentClassifierPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDocumentClassificationJobResponseTypeDef = TypedDict(
    "DescribeDocumentClassificationJobResponseTypeDef",
    {
        "DocumentClassificationJobProperties": DocumentClassificationJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDocumentClassificationJobsResponseTypeDef = TypedDict(
    "ListDocumentClassificationJobsResponseTypeDef",
    {
        "DocumentClassificationJobPropertiesList": List[DocumentClassificationJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDominantLanguageDetectionJobResponseTypeDef = TypedDict(
    "DescribeDominantLanguageDetectionJobResponseTypeDef",
    {
        "DominantLanguageDetectionJobProperties": DominantLanguageDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDominantLanguageDetectionJobsResponseTypeDef = TypedDict(
    "ListDominantLanguageDetectionJobsResponseTypeDef",
    {
        "DominantLanguageDetectionJobPropertiesList": List[
            DominantLanguageDetectionJobPropertiesTypeDef
        ],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEntitiesDetectionJobResponseTypeDef = TypedDict(
    "DescribeEntitiesDetectionJobResponseTypeDef",
    {
        "EntitiesDetectionJobProperties": EntitiesDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEntitiesDetectionJobsResponseTypeDef = TypedDict(
    "ListEntitiesDetectionJobsResponseTypeDef",
    {
        "EntitiesDetectionJobPropertiesList": List[EntitiesDetectionJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEventsDetectionJobResponseTypeDef = TypedDict(
    "DescribeEventsDetectionJobResponseTypeDef",
    {
        "EventsDetectionJobProperties": EventsDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEventsDetectionJobsResponseTypeDef = TypedDict(
    "ListEventsDetectionJobsResponseTypeDef",
    {
        "EventsDetectionJobPropertiesList": List[EventsDetectionJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeKeyPhrasesDetectionJobResponseTypeDef = TypedDict(
    "DescribeKeyPhrasesDetectionJobResponseTypeDef",
    {
        "KeyPhrasesDetectionJobProperties": KeyPhrasesDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListKeyPhrasesDetectionJobsResponseTypeDef = TypedDict(
    "ListKeyPhrasesDetectionJobsResponseTypeDef",
    {
        "KeyPhrasesDetectionJobPropertiesList": List[KeyPhrasesDetectionJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePiiEntitiesDetectionJobResponseTypeDef = TypedDict(
    "DescribePiiEntitiesDetectionJobResponseTypeDef",
    {
        "PiiEntitiesDetectionJobProperties": PiiEntitiesDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPiiEntitiesDetectionJobsResponseTypeDef = TypedDict(
    "ListPiiEntitiesDetectionJobsResponseTypeDef",
    {
        "PiiEntitiesDetectionJobPropertiesList": List[PiiEntitiesDetectionJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSentimentDetectionJobResponseTypeDef = TypedDict(
    "DescribeSentimentDetectionJobResponseTypeDef",
    {
        "SentimentDetectionJobProperties": SentimentDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSentimentDetectionJobsResponseTypeDef = TypedDict(
    "ListSentimentDetectionJobsResponseTypeDef",
    {
        "SentimentDetectionJobPropertiesList": List[SentimentDetectionJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTargetedSentimentDetectionJobResponseTypeDef = TypedDict(
    "DescribeTargetedSentimentDetectionJobResponseTypeDef",
    {
        "TargetedSentimentDetectionJobProperties": TargetedSentimentDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTargetedSentimentDetectionJobsResponseTypeDef = TypedDict(
    "ListTargetedSentimentDetectionJobsResponseTypeDef",
    {
        "TargetedSentimentDetectionJobPropertiesList": List[
            TargetedSentimentDetectionJobPropertiesTypeDef
        ],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTopicsDetectionJobResponseTypeDef = TypedDict(
    "DescribeTopicsDetectionJobResponseTypeDef",
    {
        "TopicsDetectionJobProperties": TopicsDetectionJobPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTopicsDetectionJobsResponseTypeDef = TypedDict(
    "ListTopicsDetectionJobsResponseTypeDef",
    {
        "TopicsDetectionJobPropertiesList": List[TopicsDetectionJobPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EntityRecognizerPropertiesTypeDef = TypedDict(
    "EntityRecognizerPropertiesTypeDef",
    {
        "EntityRecognizerArn": str,
        "LanguageCode": LanguageCodeType,
        "Status": ModelStatusType,
        "Message": str,
        "SubmitTime": datetime,
        "EndTime": datetime,
        "TrainingStartTime": datetime,
        "TrainingEndTime": datetime,
        "InputDataConfig": EntityRecognizerInputDataConfigTypeDef,
        "RecognizerMetadata": EntityRecognizerMetadataTypeDef,
        "DataAccessRoleArn": str,
        "VolumeKmsKeyId": str,
        "VpcConfig": VpcConfigTypeDef,
        "ModelKmsKeyId": str,
        "VersionName": str,
        "SourceModelArn": str,
    },
    total=False,
)

BatchDetectSyntaxResponseTypeDef = TypedDict(
    "BatchDetectSyntaxResponseTypeDef",
    {
        "ResultList": List[BatchDetectSyntaxItemResultTypeDef],
        "ErrorList": List[BatchItemErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEntityRecognizerResponseTypeDef = TypedDict(
    "DescribeEntityRecognizerResponseTypeDef",
    {
        "EntityRecognizerProperties": EntityRecognizerPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEntityRecognizersResponseTypeDef = TypedDict(
    "ListEntityRecognizersResponseTypeDef",
    {
        "EntityRecognizerPropertiesList": List[EntityRecognizerPropertiesTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
