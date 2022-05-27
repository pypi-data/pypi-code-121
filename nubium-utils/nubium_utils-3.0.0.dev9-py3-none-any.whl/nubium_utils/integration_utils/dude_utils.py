import logging
import subprocess
from os import environ
from time import sleep

import pytest

LOGGER = logging.getLogger(__name__)


@pytest.fixture()
def dude_delete_topics():
    LOGGER.info(f"Deleting topics to start fresh...\n[{environ['INPUT_TOPIC']},{environ['OUTPUT_TOPIC']}]")
    subprocess.run(f"dude topics delete --topics {environ['INPUT_TOPIC']},{environ['OUTPUT_TOPIC']} --ignore-cluster-maps", shell=True)


@pytest.fixture()
def dude_produce_input():
    LOGGER.info("Producing test messages to the input topic...")
    subprocess.run(f"dude topics produce --topic {environ['INPUT_TOPIC']} --message-file {environ['TEST_DATA_IN']} --schema {environ['TEST_DATA_IN_SCHEMA']}", shell=True)
    sleep(30)  # wait for app to process the messages


@pytest.fixture()
def dude_consume_output():
    LOGGER.info("Consuming test messages from the output topic and dumping them to a file...")
    subprocess.run(f"dude topics consume --topic {environ['OUTPUT_TOPIC']} --message-file {environ['TEST_DATA_OUT']}", shell=True)
