import json
import logging
import os
from typing import Callable, List, Optional, Union

from kafka import KafkaConsumer


def create_kafka_consumer(
    kafka_uri: str, group_id: Optional[str], topics: Union[str, List[str]]
) -> KafkaConsumer:
    logging.info("Creating Kafka Consumer...")
    kafka_api_version = os.environ.get("KAFKA_API_VERSION", "2.5.0")
    consumer = KafkaConsumer(
        bootstrap_servers=kafka_uri,
        group_id=group_id,
        reconnect_backoff_max_ms=100000,  # TODO: what value to set here?
        # API Version is needed in order to prevent api version guessing leading to an error
        # on startup if Kafka Broker isn't ready yet
        api_version=tuple(
            [int(value) for value in kafka_api_version.split(".")]
        ),
    )
    consumer.subscribe(topics)
    logging.info("Kafka Consumer created")
    return consumer


def consume_kafka(
    kafka_uri: str,
    group_id: Optional[str],
    topics: Union[str, List[str]],
    message_processing_func: Callable[[dict], None],
) -> None:
    consumer = create_kafka_consumer(kafka_uri, group_id, topics)
    logging.info("Ready to consume messages")
    for message in consumer:
        val_utf8 = message.value.decode("utf-8").replace("NaN", "null")
        key = message.key.decode("utf-8")
        data = json.loads(val_utf8)
        message_processing_func(key, data)
