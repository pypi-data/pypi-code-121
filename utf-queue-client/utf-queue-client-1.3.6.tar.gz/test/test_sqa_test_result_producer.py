from utf_queue_client.clients.sqa_test_result_producer import (
    SqaTestResultProducer,
    SqaTestResultProducerFactory,
    DummySqaTestResultProducer,
)
import pytest
import os


def test_result_producer_empty_url():
    with pytest.raises(RuntimeError):
        _ = SqaTestResultProducer()


def test_result_producer_central_queue(
    request,
    sqa_app_build_result,
    sqa_test_result,
    sqa_test_session,
    amqp_url,
    queue_consumer,
):
    os.environ["UTF_PRODUCER_APP_ID"] = request.node.name
    producer = SqaTestResultProducerFactory.create_producer()
    producer.publish_app_build_result(sqa_app_build_result)
    queue_consumer.expect_messages(1)
    producer.publish_test_session_start(sqa_test_session)
    queue_consumer.expect_messages(2)
    producer.publish_test_session_stop(sqa_test_session)
    queue_consumer.expect_messages(3)
    producer.publish_test_result(sqa_test_result)
    queue_consumer.expect_messages(4)


def test_dummy_producer(sqa_app_build_result, sqa_test_result, sqa_test_session):
    producer = DummySqaTestResultProducer()
    producer.publish_app_build_result(sqa_app_build_result)
    producer.publish_test_session_start(sqa_test_session)
    producer.publish_test_session_stop(sqa_test_session)
    producer.publish_test_result(sqa_test_result)
