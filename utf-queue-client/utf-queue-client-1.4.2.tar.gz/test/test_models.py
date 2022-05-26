from utf_queue_client.models import (
    SqaAppBuildResult,
    SqaTestResult,
    SqaTestSession,
    QueueMessage,
    QueueMessageV1,
    ArtifactUploadRequest,
    ArtifactMetadata,
    ArtifactBuildMetadata,
)
from utf_queue_client.exceptions import SchemaValidationError, ValidationError
from utf_queue_client.models.model_factory import (
    create_model_with_defaults,
)
import pytest


def test_model_factory_no_args_valid():
    # these types support empty initializer
    types_supporting_defaults_or_no_args = [
        ArtifactMetadata,
        ArtifactBuildMetadata,
    ]
    for model_type in types_supporting_defaults_or_no_args:
        create_model_with_defaults(model_type)


def test_model_factory_no_args_invalid():
    # these types do not support creation with empty initializer
    types_requiring_args = [
        QueueMessage,
        QueueMessageV1,
        ArtifactUploadRequest,
        SqaTestSession,
    ]
    for model_type in types_requiring_args:
        with pytest.raises(ValidationError):
            create_model_with_defaults(model_type)





def test_sqa_appbuild_results_record_model_creation(sqa_app_build_result):
    init_dict = {**sqa_app_build_result.dict(), "invalid_attr": True}

    # kwarg creation
    model = SqaAppBuildResult(**init_dict)
    assert "invalid_attr" not in model.dict()

    # dict creation
    model = SqaAppBuildResult(init_dict)
    assert "invalid_attr" not in model.dict()

    with pytest.raises(ValidationError):
        SqaAppBuildResult(dict(invalid_attr=True))


def test_sqa_test_results_record_schema_validation(sqa_test_result):
    model = SqaTestResult(sqa_test_result.dict())
    model.validate_schema()
    model.testResult = "failed"
    model.validate_schema()

    model.testCaseId = 4
    with pytest.raises(SchemaValidationError):
        model.validate_schema()

    model.testResult = "PASS"
    with pytest.raises(SchemaValidationError):
        model.validate_schema()


def test_sqa_test_session_creation(sqa_test_session):
    with pytest.raises(ValidationError):
        _ = SqaTestSession(eventType="TEST_RESULT", invalid_attr=True)


@pytest.fixture()
def artifact_upload_request():
    yield ArtifactUploadRequest(
        name="foop",
        extension=".py",
        metadata={},
        base64Content="6",
        validateMetadata=False,
    )


def test_artifact_upload_request(artifact_upload_request):
    model = artifact_upload_request
    model.validate_schema()
    with pytest.raises(SchemaValidationError):
        model.base64Content = 6
        model.validate_schema()


def test_deserialize_queue_message_v1(artifact_upload_request):
    message = {
        "payload": artifact_upload_request.dict(),
        "recordType": "ARTIFACT_UPLOAD_REQUEST",
        "timestamp": 1649882203,
    }
    queue_message = QueueMessageV1(message)
    if queue_message.recordType == "ARTIFACT_UPLOAD_REQUEST":
        _ = ArtifactUploadRequest(queue_message.payload.dict())


def test_deserialize_queue_message_v2(artifact_upload_request):
    message = {
        "payload": artifact_upload_request.dict(),
        "recordType": "ARTIFACT_UPLOAD_REQUEST",
        "tenantKey": "12345678",
        "recordTimestamp": "2022-03-10T18:50:05Z",
    }
    queue_message = QueueMessage(message)
    if queue_message.recordType == "ARTIFACT_UPLOAD_REQUEST":
        _ = ArtifactUploadRequest(queue_message.payload.dict())
