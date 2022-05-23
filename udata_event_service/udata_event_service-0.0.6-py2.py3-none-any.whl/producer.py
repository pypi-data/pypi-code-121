import json
import logging
import os

from kafka import KafkaProducer


class KafkaProducerSingleton:
    __instance = None

    @staticmethod
    def get_instance(kafka_uri: str) -> KafkaProducer:
        if KafkaProducerSingleton.__instance is None:
            kafka_api_version = os.environ.get("KAFKA_API_VERSION", "2.5.0")
            KafkaProducerSingleton.__instance = KafkaProducer(
                bootstrap_servers=kafka_uri,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                api_version=tuple(
                    [int(value) for value in kafka_api_version.split(".")]
                ),
            )
        return KafkaProducerSingleton.__instance


def produce(
    kafka_uri: str,
    topic: str,
    service: str,
    key_id: str,
    document: dict = None,
    meta: dict = None,
) -> None:
    if kafka_uri:
        producer = KafkaProducerSingleton.get_instance(kafka_uri)
        key = key_id.encode("utf-8")
        value = {"service": service, "value": document, "meta": meta}
        producer.send(topic=topic, value=value, key=key)
        producer.flush()
    else:
        logging.warning("No kafka_uri provided")
