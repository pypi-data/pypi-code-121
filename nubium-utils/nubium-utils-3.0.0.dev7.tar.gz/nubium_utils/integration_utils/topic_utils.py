import json
import logging
from importlib import import_module
from os import environ
from time import sleep

import pytest

from nubium_utils.confluent_utils import KafkaToolbox
from nubium_utils.confluent_utils.dev_toolbox import DudeFinished

LOGGER = logging.getLogger(__name__)


kafka_toolbox = KafkaToolbox()


@pytest.fixture()
def delete_topics(topics):
    LOGGER.info(f"Deleting topics to start fresh...\n{topics}")
    kafka_toolbox.delete_topics(topics.split(","))


@pytest.fixture()
def delete_test_topics():
    kafka_toolbox.delete_topics([v for k, v in environ.items() if '_TOPIC' in k and v.startswith('TEST__')])


@pytest.fixture()
def produce_input(map_kafka_input):
    LOGGER.info("Producing test messages to the input topic...")
    import_path, obj = environ['INPUT_SCHEMA'].rsplit('.', 1)
    kafka_toolbox.produce_messages(
        topic=environ['INPUT_TOPIC'],
        message_list=map_kafka_input,
        schema=getattr(import_module(import_path), obj))
    sleep(10)  # wait for app to process the messages


def format_message(bulk_transaction):
    return [{'key': msg.key(), 'value': msg.value(), 'headers': {key: value.decode("utf-8") for key, value in dict(msg.headers()).items()}} for msg in bulk_transaction.messages()]


@pytest.fixture()
@pytest.mark.xfail(raises=DudeFinished)
def consume_output(tmp_path):
    LOGGER.info("Consuming test messages from the output topic...")
    return kafka_toolbox.consume_messages(topics=environ['OUTPUT_TOPIC'], transform_function=format_message)
