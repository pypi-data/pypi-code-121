"""
Type annotations for comprehend service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_comprehend.client import ComprehendClient

    session = Session()
    client: ComprehendClient = session.client("comprehend")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    DocumentClassifierModeType,
    LanguageCodeType,
    PiiEntitiesDetectionModeType,
    SyntaxLanguageCodeType,
)
from .paginator import (
    ListDocumentClassificationJobsPaginator,
    ListDocumentClassifiersPaginator,
    ListDominantLanguageDetectionJobsPaginator,
    ListEntitiesDetectionJobsPaginator,
    ListEntityRecognizersPaginator,
    ListKeyPhrasesDetectionJobsPaginator,
    ListSentimentDetectionJobsPaginator,
    ListTopicsDetectionJobsPaginator,
)
from .type_defs import (
    BatchDetectDominantLanguageResponseTypeDef,
    BatchDetectEntitiesResponseTypeDef,
    BatchDetectKeyPhrasesResponseTypeDef,
    BatchDetectSentimentResponseTypeDef,
    BatchDetectSyntaxResponseTypeDef,
    ClassifyDocumentResponseTypeDef,
    ContainsPiiEntitiesResponseTypeDef,
    CreateDocumentClassifierResponseTypeDef,
    CreateEndpointResponseTypeDef,
    CreateEntityRecognizerResponseTypeDef,
    DescribeDocumentClassificationJobResponseTypeDef,
    DescribeDocumentClassifierResponseTypeDef,
    DescribeDominantLanguageDetectionJobResponseTypeDef,
    DescribeEndpointResponseTypeDef,
    DescribeEntitiesDetectionJobResponseTypeDef,
    DescribeEntityRecognizerResponseTypeDef,
    DescribeEventsDetectionJobResponseTypeDef,
    DescribeKeyPhrasesDetectionJobResponseTypeDef,
    DescribePiiEntitiesDetectionJobResponseTypeDef,
    DescribeResourcePolicyResponseTypeDef,
    DescribeSentimentDetectionJobResponseTypeDef,
    DescribeTargetedSentimentDetectionJobResponseTypeDef,
    DescribeTopicsDetectionJobResponseTypeDef,
    DetectDominantLanguageResponseTypeDef,
    DetectEntitiesResponseTypeDef,
    DetectKeyPhrasesResponseTypeDef,
    DetectPiiEntitiesResponseTypeDef,
    DetectSentimentResponseTypeDef,
    DetectSyntaxResponseTypeDef,
    DocumentClassificationJobFilterTypeDef,
    DocumentClassifierFilterTypeDef,
    DocumentClassifierInputDataConfigTypeDef,
    DocumentClassifierOutputDataConfigTypeDef,
    DominantLanguageDetectionJobFilterTypeDef,
    EndpointFilterTypeDef,
    EntitiesDetectionJobFilterTypeDef,
    EntityRecognizerFilterTypeDef,
    EntityRecognizerInputDataConfigTypeDef,
    EventsDetectionJobFilterTypeDef,
    ImportModelResponseTypeDef,
    InputDataConfigTypeDef,
    KeyPhrasesDetectionJobFilterTypeDef,
    ListDocumentClassificationJobsResponseTypeDef,
    ListDocumentClassifiersResponseTypeDef,
    ListDocumentClassifierSummariesResponseTypeDef,
    ListDominantLanguageDetectionJobsResponseTypeDef,
    ListEndpointsResponseTypeDef,
    ListEntitiesDetectionJobsResponseTypeDef,
    ListEntityRecognizersResponseTypeDef,
    ListEntityRecognizerSummariesResponseTypeDef,
    ListEventsDetectionJobsResponseTypeDef,
    ListKeyPhrasesDetectionJobsResponseTypeDef,
    ListPiiEntitiesDetectionJobsResponseTypeDef,
    ListSentimentDetectionJobsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListTargetedSentimentDetectionJobsResponseTypeDef,
    ListTopicsDetectionJobsResponseTypeDef,
    OutputDataConfigTypeDef,
    PiiEntitiesDetectionJobFilterTypeDef,
    PutResourcePolicyResponseTypeDef,
    RedactionConfigTypeDef,
    SentimentDetectionJobFilterTypeDef,
    StartDocumentClassificationJobResponseTypeDef,
    StartDominantLanguageDetectionJobResponseTypeDef,
    StartEntitiesDetectionJobResponseTypeDef,
    StartEventsDetectionJobResponseTypeDef,
    StartKeyPhrasesDetectionJobResponseTypeDef,
    StartPiiEntitiesDetectionJobResponseTypeDef,
    StartSentimentDetectionJobResponseTypeDef,
    StartTargetedSentimentDetectionJobResponseTypeDef,
    StartTopicsDetectionJobResponseTypeDef,
    StopDominantLanguageDetectionJobResponseTypeDef,
    StopEntitiesDetectionJobResponseTypeDef,
    StopEventsDetectionJobResponseTypeDef,
    StopKeyPhrasesDetectionJobResponseTypeDef,
    StopPiiEntitiesDetectionJobResponseTypeDef,
    StopSentimentDetectionJobResponseTypeDef,
    StopTargetedSentimentDetectionJobResponseTypeDef,
    TagTypeDef,
    TargetedSentimentDetectionJobFilterTypeDef,
    TopicsDetectionJobFilterTypeDef,
    VpcConfigTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("ComprehendClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    BatchSizeLimitExceededException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConcurrentModificationException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    InvalidFilterException: Type[BotocoreClientError]
    InvalidRequestException: Type[BotocoreClientError]
    JobNotFoundException: Type[BotocoreClientError]
    KmsKeyValidationException: Type[BotocoreClientError]
    ResourceInUseException: Type[BotocoreClientError]
    ResourceLimitExceededException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ResourceUnavailableException: Type[BotocoreClientError]
    TextSizeLimitExceededException: Type[BotocoreClientError]
    TooManyRequestsException: Type[BotocoreClientError]
    TooManyTagKeysException: Type[BotocoreClientError]
    TooManyTagsException: Type[BotocoreClientError]
    UnsupportedLanguageException: Type[BotocoreClientError]


class ComprehendClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        ComprehendClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#exceptions)
        """

    def batch_detect_dominant_language(
        self, *, TextList: Sequence[str]
    ) -> BatchDetectDominantLanguageResponseTypeDef:
        """
        Determines the dominant language of the input text for a batch of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.batch_detect_dominant_language)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#batch_detect_dominant_language)
        """

    def batch_detect_entities(
        self, *, TextList: Sequence[str], LanguageCode: LanguageCodeType
    ) -> BatchDetectEntitiesResponseTypeDef:
        """
        Inspects the text of a batch of documents for named entities and returns
        information about them.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.batch_detect_entities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#batch_detect_entities)
        """

    def batch_detect_key_phrases(
        self, *, TextList: Sequence[str], LanguageCode: LanguageCodeType
    ) -> BatchDetectKeyPhrasesResponseTypeDef:
        """
        Detects the key noun phrases found in a batch of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.batch_detect_key_phrases)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#batch_detect_key_phrases)
        """

    def batch_detect_sentiment(
        self, *, TextList: Sequence[str], LanguageCode: LanguageCodeType
    ) -> BatchDetectSentimentResponseTypeDef:
        """
        Inspects a batch of documents and returns an inference of the prevailing
        sentiment, `POSITIVE` , `NEUTRAL` , `MIXED` , or `NEGATIVE` , in each one.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.batch_detect_sentiment)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#batch_detect_sentiment)
        """

    def batch_detect_syntax(
        self, *, TextList: Sequence[str], LanguageCode: SyntaxLanguageCodeType
    ) -> BatchDetectSyntaxResponseTypeDef:
        """
        Inspects the text of a batch of documents for the syntax and part of speech of
        the words in the document and returns information about them.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.batch_detect_syntax)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#batch_detect_syntax)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#can_paginate)
        """

    def classify_document(self, *, Text: str, EndpointArn: str) -> ClassifyDocumentResponseTypeDef:
        """
        Creates a new document classification request to analyze a single document in
        real-time, using a previously created and trained custom model and an endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.classify_document)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#classify_document)
        """

    def contains_pii_entities(
        self, *, Text: str, LanguageCode: LanguageCodeType
    ) -> ContainsPiiEntitiesResponseTypeDef:
        """
        Analyzes input text for the presence of personally identifiable information
        (PII) and returns the labels of identified PII entity types such as name,
        address, bank account number, or phone number.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.contains_pii_entities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#contains_pii_entities)
        """

    def create_document_classifier(
        self,
        *,
        DocumentClassifierName: str,
        DataAccessRoleArn: str,
        InputDataConfig: DocumentClassifierInputDataConfigTypeDef,
        LanguageCode: LanguageCodeType,
        VersionName: str = ...,
        Tags: Sequence[TagTypeDef] = ...,
        OutputDataConfig: DocumentClassifierOutputDataConfigTypeDef = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Mode: DocumentClassifierModeType = ...,
        ModelKmsKeyId: str = ...,
        ModelPolicy: str = ...
    ) -> CreateDocumentClassifierResponseTypeDef:
        """
        Creates a new document classifier that you can use to categorize documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.create_document_classifier)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#create_document_classifier)
        """

    def create_endpoint(
        self,
        *,
        EndpointName: str,
        ModelArn: str,
        DesiredInferenceUnits: int,
        ClientRequestToken: str = ...,
        Tags: Sequence[TagTypeDef] = ...,
        DataAccessRoleArn: str = ...
    ) -> CreateEndpointResponseTypeDef:
        """
        Creates a model-specific endpoint for synchronous inference for a previously
        trained custom model For information about endpoints, see [Managing
        endpoints](https://docs.aws.amazon.com/comprehend/latest/dg/manage-
        endpoints.html)_ .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.create_endpoint)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#create_endpoint)
        """

    def create_entity_recognizer(
        self,
        *,
        RecognizerName: str,
        DataAccessRoleArn: str,
        InputDataConfig: EntityRecognizerInputDataConfigTypeDef,
        LanguageCode: LanguageCodeType,
        VersionName: str = ...,
        Tags: Sequence[TagTypeDef] = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        ModelKmsKeyId: str = ...,
        ModelPolicy: str = ...
    ) -> CreateEntityRecognizerResponseTypeDef:
        """
        Creates an entity recognizer using submitted files.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.create_entity_recognizer)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#create_entity_recognizer)
        """

    def delete_document_classifier(self, *, DocumentClassifierArn: str) -> Dict[str, Any]:
        """
        Deletes a previously created document classifier Only those classifiers that are
        in terminated states (IN_ERROR, TRAINED) will be deleted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.delete_document_classifier)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#delete_document_classifier)
        """

    def delete_endpoint(self, *, EndpointArn: str) -> Dict[str, Any]:
        """
        Deletes a model-specific endpoint for a previously-trained custom model.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.delete_endpoint)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#delete_endpoint)
        """

    def delete_entity_recognizer(self, *, EntityRecognizerArn: str) -> Dict[str, Any]:
        """
        Deletes an entity recognizer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.delete_entity_recognizer)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#delete_entity_recognizer)
        """

    def delete_resource_policy(
        self, *, ResourceArn: str, PolicyRevisionId: str = ...
    ) -> Dict[str, Any]:
        """
        Deletes a resource-based policy that is attached to a custom model.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.delete_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#delete_resource_policy)
        """

    def describe_document_classification_job(
        self, *, JobId: str
    ) -> DescribeDocumentClassificationJobResponseTypeDef:
        """
        Gets the properties associated with a document classification job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_document_classification_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_document_classification_job)
        """

    def describe_document_classifier(
        self, *, DocumentClassifierArn: str
    ) -> DescribeDocumentClassifierResponseTypeDef:
        """
        Gets the properties associated with a document classifier.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_document_classifier)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_document_classifier)
        """

    def describe_dominant_language_detection_job(
        self, *, JobId: str
    ) -> DescribeDominantLanguageDetectionJobResponseTypeDef:
        """
        Gets the properties associated with a dominant language detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_dominant_language_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_dominant_language_detection_job)
        """

    def describe_endpoint(self, *, EndpointArn: str) -> DescribeEndpointResponseTypeDef:
        """
        Gets the properties associated with a specific endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_endpoint)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_endpoint)
        """

    def describe_entities_detection_job(
        self, *, JobId: str
    ) -> DescribeEntitiesDetectionJobResponseTypeDef:
        """
        Gets the properties associated with an entities detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_entities_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_entities_detection_job)
        """

    def describe_entity_recognizer(
        self, *, EntityRecognizerArn: str
    ) -> DescribeEntityRecognizerResponseTypeDef:
        """
        Provides details about an entity recognizer including status, S3 buckets
        containing training data, recognizer metadata, metrics, and so on.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_entity_recognizer)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_entity_recognizer)
        """

    def describe_events_detection_job(
        self, *, JobId: str
    ) -> DescribeEventsDetectionJobResponseTypeDef:
        """
        Gets the status and details of an events detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_events_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_events_detection_job)
        """

    def describe_key_phrases_detection_job(
        self, *, JobId: str
    ) -> DescribeKeyPhrasesDetectionJobResponseTypeDef:
        """
        Gets the properties associated with a key phrases detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_key_phrases_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_key_phrases_detection_job)
        """

    def describe_pii_entities_detection_job(
        self, *, JobId: str
    ) -> DescribePiiEntitiesDetectionJobResponseTypeDef:
        """
        Gets the properties associated with a PII entities detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_pii_entities_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_pii_entities_detection_job)
        """

    def describe_resource_policy(
        self, *, ResourceArn: str
    ) -> DescribeResourcePolicyResponseTypeDef:
        """
        Gets the details of a resource-based policy that is attached to a custom model,
        including the JSON body of the policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_resource_policy)
        """

    def describe_sentiment_detection_job(
        self, *, JobId: str
    ) -> DescribeSentimentDetectionJobResponseTypeDef:
        """
        Gets the properties associated with a sentiment detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_sentiment_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_sentiment_detection_job)
        """

    def describe_targeted_sentiment_detection_job(
        self, *, JobId: str
    ) -> DescribeTargetedSentimentDetectionJobResponseTypeDef:
        """
        Gets the properties associated with a targeted sentiment detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_targeted_sentiment_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_targeted_sentiment_detection_job)
        """

    def describe_topics_detection_job(
        self, *, JobId: str
    ) -> DescribeTopicsDetectionJobResponseTypeDef:
        """
        Gets the properties associated with a topic detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_topics_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#describe_topics_detection_job)
        """

    def detect_dominant_language(self, *, Text: str) -> DetectDominantLanguageResponseTypeDef:
        """
        Determines the dominant language of the input text.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.detect_dominant_language)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#detect_dominant_language)
        """

    def detect_entities(
        self, *, Text: str, LanguageCode: LanguageCodeType = ..., EndpointArn: str = ...
    ) -> DetectEntitiesResponseTypeDef:
        """
        Inspects text for named entities, and returns information about them.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.detect_entities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#detect_entities)
        """

    def detect_key_phrases(
        self, *, Text: str, LanguageCode: LanguageCodeType
    ) -> DetectKeyPhrasesResponseTypeDef:
        """
        Detects the key noun phrases found in the text.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.detect_key_phrases)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#detect_key_phrases)
        """

    def detect_pii_entities(
        self, *, Text: str, LanguageCode: LanguageCodeType
    ) -> DetectPiiEntitiesResponseTypeDef:
        """
        Inspects the input text for entities that contain personally identifiable
        information (PII) and returns information about them.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.detect_pii_entities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#detect_pii_entities)
        """

    def detect_sentiment(
        self, *, Text: str, LanguageCode: LanguageCodeType
    ) -> DetectSentimentResponseTypeDef:
        """
        Inspects text and returns an inference of the prevailing sentiment (`POSITIVE` ,
        `NEUTRAL` , `MIXED` , or `NEGATIVE` ).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.detect_sentiment)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#detect_sentiment)
        """

    def detect_syntax(
        self, *, Text: str, LanguageCode: SyntaxLanguageCodeType
    ) -> DetectSyntaxResponseTypeDef:
        """
        Inspects text for syntax and the part of speech of words in the document.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.detect_syntax)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#detect_syntax)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#generate_presigned_url)
        """

    def import_model(
        self,
        *,
        SourceModelArn: str,
        ModelName: str = ...,
        VersionName: str = ...,
        ModelKmsKeyId: str = ...,
        DataAccessRoleArn: str = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> ImportModelResponseTypeDef:
        """
        Creates a new custom model that replicates a source custom model that you
        import.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.import_model)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#import_model)
        """

    def list_document_classification_jobs(
        self,
        *,
        Filter: DocumentClassificationJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListDocumentClassificationJobsResponseTypeDef:
        """
        Gets a list of the documentation classification jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_document_classification_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_document_classification_jobs)
        """

    def list_document_classifier_summaries(
        self, *, NextToken: str = ..., MaxResults: int = ...
    ) -> ListDocumentClassifierSummariesResponseTypeDef:
        """
        Gets a list of summaries of the document classifiers that you have created See
        also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/comprehend-2017-11-27/ListDocumentClassifierSummaries).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_document_classifier_summaries)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_document_classifier_summaries)
        """

    def list_document_classifiers(
        self,
        *,
        Filter: DocumentClassifierFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListDocumentClassifiersResponseTypeDef:
        """
        Gets a list of the document classifiers that you have created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_document_classifiers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_document_classifiers)
        """

    def list_dominant_language_detection_jobs(
        self,
        *,
        Filter: DominantLanguageDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListDominantLanguageDetectionJobsResponseTypeDef:
        """
        Gets a list of the dominant language detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_dominant_language_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_dominant_language_detection_jobs)
        """

    def list_endpoints(
        self, *, Filter: EndpointFilterTypeDef = ..., NextToken: str = ..., MaxResults: int = ...
    ) -> ListEndpointsResponseTypeDef:
        """
        Gets a list of all existing endpoints that you've created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_endpoints)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_endpoints)
        """

    def list_entities_detection_jobs(
        self,
        *,
        Filter: EntitiesDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListEntitiesDetectionJobsResponseTypeDef:
        """
        Gets a list of the entity detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_entities_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_entities_detection_jobs)
        """

    def list_entity_recognizer_summaries(
        self, *, NextToken: str = ..., MaxResults: int = ...
    ) -> ListEntityRecognizerSummariesResponseTypeDef:
        """
        Gets a list of summaries for the entity recognizers that you have created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_entity_recognizer_summaries)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_entity_recognizer_summaries)
        """

    def list_entity_recognizers(
        self,
        *,
        Filter: EntityRecognizerFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListEntityRecognizersResponseTypeDef:
        """
        Gets a list of the properties of all entity recognizers that you created,
        including recognizers currently in training.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_entity_recognizers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_entity_recognizers)
        """

    def list_events_detection_jobs(
        self,
        *,
        Filter: EventsDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListEventsDetectionJobsResponseTypeDef:
        """
        Gets a list of the events detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_events_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_events_detection_jobs)
        """

    def list_key_phrases_detection_jobs(
        self,
        *,
        Filter: KeyPhrasesDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListKeyPhrasesDetectionJobsResponseTypeDef:
        """
        Get a list of key phrase detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_key_phrases_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_key_phrases_detection_jobs)
        """

    def list_pii_entities_detection_jobs(
        self,
        *,
        Filter: PiiEntitiesDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListPiiEntitiesDetectionJobsResponseTypeDef:
        """
        Gets a list of the PII entity detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_pii_entities_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_pii_entities_detection_jobs)
        """

    def list_sentiment_detection_jobs(
        self,
        *,
        Filter: SentimentDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListSentimentDetectionJobsResponseTypeDef:
        """
        Gets a list of sentiment detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_sentiment_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_sentiment_detection_jobs)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Lists all tags associated with a given Amazon Comprehend resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_tags_for_resource)
        """

    def list_targeted_sentiment_detection_jobs(
        self,
        *,
        Filter: TargetedSentimentDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListTargetedSentimentDetectionJobsResponseTypeDef:
        """
        Gets a list of targeted sentiment detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_targeted_sentiment_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_targeted_sentiment_detection_jobs)
        """

    def list_topics_detection_jobs(
        self,
        *,
        Filter: TopicsDetectionJobFilterTypeDef = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListTopicsDetectionJobsResponseTypeDef:
        """
        Gets a list of the topic detection jobs that you have submitted.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_topics_detection_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#list_topics_detection_jobs)
        """

    def put_resource_policy(
        self, *, ResourceArn: str, ResourcePolicy: str, PolicyRevisionId: str = ...
    ) -> PutResourcePolicyResponseTypeDef:
        """
        Attaches a resource-based policy to a custom model.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.put_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#put_resource_policy)
        """

    def start_document_classification_job(
        self,
        *,
        DocumentClassifierArn: str,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        JobName: str = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartDocumentClassificationJobResponseTypeDef:
        """
        Starts an asynchronous document classification job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_document_classification_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_document_classification_job)
        """

    def start_dominant_language_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        JobName: str = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartDominantLanguageDetectionJobResponseTypeDef:
        """
        Starts an asynchronous dominant language detection job for a collection of
        documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_dominant_language_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_dominant_language_detection_job)
        """

    def start_entities_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        LanguageCode: LanguageCodeType,
        JobName: str = ...,
        EntityRecognizerArn: str = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartEntitiesDetectionJobResponseTypeDef:
        """
        Starts an asynchronous entity detection job for a collection of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_entities_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_entities_detection_job)
        """

    def start_events_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        LanguageCode: LanguageCodeType,
        TargetEventTypes: Sequence[str],
        JobName: str = ...,
        ClientRequestToken: str = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartEventsDetectionJobResponseTypeDef:
        """
        Starts an asynchronous event detection job for a collection of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_events_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_events_detection_job)
        """

    def start_key_phrases_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        LanguageCode: LanguageCodeType,
        JobName: str = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartKeyPhrasesDetectionJobResponseTypeDef:
        """
        Starts an asynchronous key phrase detection job for a collection of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_key_phrases_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_key_phrases_detection_job)
        """

    def start_pii_entities_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        Mode: PiiEntitiesDetectionModeType,
        DataAccessRoleArn: str,
        LanguageCode: LanguageCodeType,
        RedactionConfig: RedactionConfigTypeDef = ...,
        JobName: str = ...,
        ClientRequestToken: str = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartPiiEntitiesDetectionJobResponseTypeDef:
        """
        Starts an asynchronous PII entity detection job for a collection of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_pii_entities_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_pii_entities_detection_job)
        """

    def start_sentiment_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        LanguageCode: LanguageCodeType,
        JobName: str = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartSentimentDetectionJobResponseTypeDef:
        """
        Starts an asynchronous sentiment detection job for a collection of documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_sentiment_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_sentiment_detection_job)
        """

    def start_targeted_sentiment_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        LanguageCode: LanguageCodeType,
        JobName: str = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartTargetedSentimentDetectionJobResponseTypeDef:
        """
        Starts an asynchronous targeted sentiment detection job for a collection of
        documents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_targeted_sentiment_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_targeted_sentiment_detection_job)
        """

    def start_topics_detection_job(
        self,
        *,
        InputDataConfig: InputDataConfigTypeDef,
        OutputDataConfig: OutputDataConfigTypeDef,
        DataAccessRoleArn: str,
        JobName: str = ...,
        NumberOfTopics: int = ...,
        ClientRequestToken: str = ...,
        VolumeKmsKeyId: str = ...,
        VpcConfig: VpcConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> StartTopicsDetectionJobResponseTypeDef:
        """
        Starts an asynchronous topic detection job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_topics_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#start_topics_detection_job)
        """

    def stop_dominant_language_detection_job(
        self, *, JobId: str
    ) -> StopDominantLanguageDetectionJobResponseTypeDef:
        """
        Stops a dominant language detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_dominant_language_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_dominant_language_detection_job)
        """

    def stop_entities_detection_job(self, *, JobId: str) -> StopEntitiesDetectionJobResponseTypeDef:
        """
        Stops an entities detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_entities_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_entities_detection_job)
        """

    def stop_events_detection_job(self, *, JobId: str) -> StopEventsDetectionJobResponseTypeDef:
        """
        Stops an events detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_events_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_events_detection_job)
        """

    def stop_key_phrases_detection_job(
        self, *, JobId: str
    ) -> StopKeyPhrasesDetectionJobResponseTypeDef:
        """
        Stops a key phrases detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_key_phrases_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_key_phrases_detection_job)
        """

    def stop_pii_entities_detection_job(
        self, *, JobId: str
    ) -> StopPiiEntitiesDetectionJobResponseTypeDef:
        """
        Stops a PII entities detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_pii_entities_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_pii_entities_detection_job)
        """

    def stop_sentiment_detection_job(
        self, *, JobId: str
    ) -> StopSentimentDetectionJobResponseTypeDef:
        """
        Stops a sentiment detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_sentiment_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_sentiment_detection_job)
        """

    def stop_targeted_sentiment_detection_job(
        self, *, JobId: str
    ) -> StopTargetedSentimentDetectionJobResponseTypeDef:
        """
        Stops a targeted sentiment detection job in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_targeted_sentiment_detection_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_targeted_sentiment_detection_job)
        """

    def stop_training_document_classifier(self, *, DocumentClassifierArn: str) -> Dict[str, Any]:
        """
        Stops a document classifier training job while in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_training_document_classifier)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_training_document_classifier)
        """

    def stop_training_entity_recognizer(self, *, EntityRecognizerArn: str) -> Dict[str, Any]:
        """
        Stops an entity recognizer training job while in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.stop_training_entity_recognizer)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#stop_training_entity_recognizer)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Sequence[TagTypeDef]) -> Dict[str, Any]:
        """
        Associates a specific tag with an Amazon Comprehend resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes a specific tag associated with an Amazon Comprehend resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#untag_resource)
        """

    def update_endpoint(
        self,
        *,
        EndpointArn: str,
        DesiredModelArn: str = ...,
        DesiredInferenceUnits: int = ...,
        DesiredDataAccessRoleArn: str = ...
    ) -> Dict[str, Any]:
        """
        Updates information about the specified endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.update_endpoint)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#update_endpoint)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_document_classification_jobs"]
    ) -> ListDocumentClassificationJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_document_classifiers"]
    ) -> ListDocumentClassifiersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_dominant_language_detection_jobs"]
    ) -> ListDominantLanguageDetectionJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_entities_detection_jobs"]
    ) -> ListEntitiesDetectionJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_entity_recognizers"]
    ) -> ListEntityRecognizersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_key_phrases_detection_jobs"]
    ) -> ListKeyPhrasesDetectionJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_sentiment_detection_jobs"]
    ) -> ListSentimentDetectionJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_topics_detection_jobs"]
    ) -> ListTopicsDetectionJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_comprehend/client/#get_paginator)
        """
