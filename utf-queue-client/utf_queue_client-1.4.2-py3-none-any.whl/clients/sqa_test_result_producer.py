import os

from .base_producer import BlockingProducer, ConnectionError
from ..models import SqaAppBuildResult
from ..models import SqaTestResult
from ..models import SqaTestSession
from ..models import QueueMessage
from . import Loggable
from socket import gethostname
from datetime import datetime
from abc import ABC, abstractmethod
from otel_extensions import instrumented

__all__ = [
    "SqaTestResultProducer",
    "LocalSqaTestResultProducer",
    "ConnectionError",
    "SqaTestResultProducerFactory",
]


class BaseSqaTestResultProducer(ABC):
    @abstractmethod
    def publish_test_result(self, test_result: SqaTestResult):
        """publish an SqaTestResult object"""

    @abstractmethod
    def publish_test_session_start(self, test_session: SqaTestSession):
        """publish an SqaTestSession object when starting a test session"""

    @abstractmethod
    def publish_test_session_stop(self, test_session: SqaTestSession):
        """publish an SqaTestSession object when stopping a test session"""

    @abstractmethod
    def publish_app_build_result(
        self,
        app_build_result: SqaAppBuildResult,
    ):
        """publish an SqaAppBuildResult object"""


class SqaTestResultProducer(BaseSqaTestResultProducer):
    RECORD_TYPE = "UTF_TEST_EVENT"

    def __init__(self, url=None, producer_app_id: str = None):
        self.queue_name = "default"
        self.__client = BlockingProducer(url, producer_app_id)
        self.__client.queue_declare(queue=self.queue_name, durable=True)
        self.producer_app_id = producer_app_id

    def _publish_message(self, queue_message: QueueMessage):
        queue_message.validate_schema()
        self.__client.publish(
            exchange="",
            routing_key=self.queue_name,
            payload=queue_message.as_dict(),
            persistent=True,
        )

    @instrumented
    def publish_test_result(self, test_result: SqaTestResult):
        queue_message = QueueMessage(
            payload=test_result,
            recordType=self.RECORD_TYPE,
            recordSubType="TEST_RESULT",
            tenantKey=self.producer_app_id,
            recordTimestamp=datetime.now().isoformat(),
        )
        self._publish_message(queue_message)

    @instrumented
    def publish_test_session(self, subtype: str, test_session: SqaTestSession):
        queue_message = QueueMessage(
            payload=test_session,
            recordType=self.RECORD_TYPE,
            recordSubType=subtype,
            tenantKey=self.producer_app_id,
            recordTimestamp=datetime.now().isoformat(),
        )
        self._publish_message(queue_message)

    @instrumented
    def publish_test_session_start(self, test_session: SqaTestSession):
        self.publish_test_session("SESSION_START", test_session)

    @instrumented
    def publish_test_session_stop(self, test_session: SqaTestSession):
        self.publish_test_session("SESSION_STOP", test_session)

    @instrumented
    def publish_app_build_result(
        self,
        app_build_result: SqaAppBuildResult,
    ):
        queue_message = QueueMessage(
            payload=app_build_result,
            recordType=self.RECORD_TYPE,
            recordSubType="BUILD_RESULT",
            tenantKey=self.producer_app_id,
            recordTimestamp=datetime.now().isoformat(),
        )
        self._publish_message(queue_message)


class LocalSqaTestResultProducer(SqaTestResultProducer):
    def __init__(self):
        super().__init__(
            "amqp://guest:guest@localhost:5672/%2f",
            os.environ.get(
                "UTF_PRODUCER_APP_ID", f"LocalSqaTestResultProducer at {gethostname()}"
            ),
        )


class DummySqaTestResultProducer(BaseSqaTestResultProducer):
    def publish_test_result(self, test_result: SqaTestResult):
        # noqa
        pass

    def publish_test_session_start(self, test_session: SqaTestSession):
        # noqa
        pass

    def publish_test_session_stop(self, test_session: SqaTestSession):
        # noqa
        pass

    def publish_app_build_result(
        self,
        app_build_result: SqaAppBuildResult,
    ):
        # noqa
        pass


class SqaTestResultProducerFactory(Loggable):
    @classmethod
    def create_producer(cls, raise_on_connection_error=False):
        try:
            queue_server_url = os.environ.get("UTF_QUEUE_SERVER_URL")
            if queue_server_url is not None:
                return SqaTestResultProducer(
                    url=queue_server_url,
                    producer_app_id=os.environ.get("UTF_PRODUCER_APP_ID"),
                )
            else:
                return LocalSqaTestResultProducer()
        except ConnectionError as e:
            cls.logger.warning(f"Unable to connect to queue server: {repr(e)}")
            if raise_on_connection_error:
                raise
            return DummySqaTestResultProducer()
