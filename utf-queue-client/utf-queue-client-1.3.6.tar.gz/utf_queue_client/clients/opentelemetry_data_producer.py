from .base_producer import BlockingProducer
from ..models import TelemetryData
from ..models import QueueMessage
from socket import gethostname
from datetime import datetime
import base64
from typing import Optional

__all__ = [
    "OpenTelemetryDataProducer",
    "LocalOpenTelemetryDataProducer",
]


class OpenTelemetryDataProducer:
    def __init__(self, url=None, producer_app_id: str = None):
        self.queue_name = "default"
        self.__client = BlockingProducer(url, producer_app_id)
        self.__client.queue_declare(queue=self.queue_name, durable=True)
        self.producer_app_id = producer_app_id

    def publish_telemetry_data(
        self, data_type: str, telemetry_data: bytes, compression: Optional[str] = None
    ):
        base64_content = base64.b64encode(telemetry_data).decode("utf-8")
        payload = TelemetryData(dataType=data_type, base64ProtobufData=base64_content)
        if compression:
            payload.compression = compression
        self._publish_telemetry_data_payload(payload)

    def _publish_telemetry_data_payload(self, telemetry_payload: TelemetryData):
        queue_message = QueueMessage(
            payload=telemetry_payload,
            recordType="OPENTELEMETRY_DATA",
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


class LocalOpenTelemetryDataProducer(OpenTelemetryDataProducer):
    def __init__(self, url=None, producer_app_id: str = None):
        super().__init__(
            url or "amqp://guest:guest@localhost:5672/%2f",
            producer_app_id or f"LocalOpenTelemetryDataProducer at {gethostname()}",
        )
