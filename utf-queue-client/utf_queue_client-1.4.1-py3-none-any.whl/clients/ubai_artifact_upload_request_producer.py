import os.path

from .base_producer import BlockingProducer
from ..models import ArtifactUploadRequest, ArtifactMetadata
from ..models import QueueMessage
from socket import gethostname
from datetime import datetime
import base64
import os
from ubai_client.apis import ArtifactApi
from ubai_client.models import ArtifactInput
from otel_extensions import instrumented

__all__ = [
    "UbaiArtifactUploadRequestProducer",
    "LocalUbaiArtifactUploadRequestProducer",
]


MESSAGE_QUEUE_SIZE_LIMIT = 67108864  # 64MB


class UbaiArtifactUploadRequestProducer:
    def __init__(self, url=None, producer_app_id: str = None):
        self.queue_name = "default"
        self.__client = BlockingProducer(url, producer_app_id)
        self.__client.queue_declare(queue=self.queue_name, durable=True)
        self.producer_app_id = producer_app_id

    @instrumented
    def upload_artifact(
        self, artifact_file: str, metadata: dict, validate_metadata: bool = True
    ):
        if validate_metadata:
            required_properties = ["branch", "stack", "build_number", "target"]
            missing_keys = [key for key in required_properties if key not in metadata]
            if len(missing_keys):
                raise RuntimeError(
                    f"metadata is missing the following required properties: {','.join(missing_keys)}"
                )

        name, extension, contents, base64_content = self.extract_payload(artifact_file)
        if len(contents) > MESSAGE_QUEUE_SIZE_LIMIT:
            self.upload_artifact_direct(
                name=name,
                extension=extension,
                base64_content=base64_content,
                metadata=metadata,
                validate_metadata=validate_metadata,
            )
        else:
            artifact_request = ArtifactUploadRequest(
                name=name,
                extension=extension,
                base64Content=base64_content,
                metadata=ArtifactMetadata(**metadata),
                validateMetadata=validate_metadata,
            )
            self.publish_artifact_upload_request(artifact_request)

    @instrumented
    def publish_artifact_upload_request(self, artifact_request: ArtifactUploadRequest):
        queue_message = QueueMessage(
            payload=artifact_request,
            recordType="ARTIFACT_UPLOAD_REQUEST",
            tenantKey=self.producer_app_id,
            recordTimestamp=datetime.now().isoformat(),
        )
        queue_message.validate_schema()

        self.__client.publish(
            exchange="",
            routing_key=self.queue_name,
            payload=queue_message.as_dict(),
            persistent=True,
        )

    @staticmethod
    def extract_payload(artifact_file: str):
        name, extension = os.path.splitext(os.path.split(artifact_file)[1])
        with open(artifact_file, "rb") as f:
            contents = f.read()
            base64_content = base64.b64encode(contents).decode("utf-8")
            return name, extension, contents, base64_content

    @staticmethod
    def upload_artifact_direct(
        name: str,
        extension: str,
        base64_content: str,
        metadata: dict,
        validate_metadata: bool = True,
    ):
        artifact_api = ArtifactApi()
        artifact_input = ArtifactInput(
            name=name,
            extension=extension,
            base64_content=base64_content,
            validate_metadata=validate_metadata,
            metadata=metadata,
        )
        artifact_api.upload_artifact(payload=artifact_input)


class LocalUbaiArtifactUploadRequestProducer(UbaiArtifactUploadRequestProducer):
    def __init__(self):
        super().__init__(
            "amqp://guest:guest@localhost:5672/%2f",
            f"LocalSqaTestResultProducer at {gethostname()}",
        )
