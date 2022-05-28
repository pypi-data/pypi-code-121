import logging
import json
import mmh3
from nubium_utils import parse_headers
from nubium_utils.yaml_parser import load_yaml_fp
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.custom_exceptions import ProduceHeadersException, ProducerTimeoutFailure
from nubium_utils.metrics import MetricsManager
from .confluent_configs import init_producer_configs, get_kafka_configs
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry.avro import AvroSerializer


LOGGER = logging.getLogger(__name__)


def produce_partitioner(producer, producer_kwargs):
    key_hash = mmh3.hash(producer_kwargs['key'])
    partition = key_hash % producer.topic_partitions[producer_kwargs['topic']]
    LOGGER.debug(f'KEY HASH - {key_hash}, PARTITION - {partition}')
    return partition


def producer_serializers(schema_dict, schema_registry):
    return {topic: AvroSerializer(schema_registry, json.dumps(schema)) for topic, schema in schema_dict.items() if
            schema}


def _get_producer(topic_schema_dict, cluster_name, schema_registry, transactional):
    producer = SerializingProducer(
        init_producer_configs(topic_schema_dict, schema_registry, get_kafka_configs(cluster_name)[0], cluster_name, transactional))
    setattr(producer, 'schema_dict', producer_serializers(topic_schema_dict, schema_registry))
    topic_yaml = load_yaml_fp(env_vars()['NU_TOPIC_CONFIGS_YAML'])
    setattr(producer, 'topic_partitions', {topic: int(topic_yaml[topic]['configs']['partitions']) for topic in topic_schema_dict})
    return producer


def get_producers(topic_schema_dict, cluster_name, schema_registry, return_as_singular=True, transactional=False):
    producer_topic_dict = {}
    LOGGER.debug('Setting up Kafka Producer')
    if transactional:
        producer_topic_dict = _get_producer(topic_schema_dict, cluster_name, schema_registry, transactional)
    else:
        for topic, schema in topic_schema_dict.items():
            temp_schema_dict = {topic: schema}
            producer = _get_producer(temp_schema_dict, cluster_name, schema_registry, transactional)
            setattr(producer, 'topic', topic)
            LOGGER.debug(f'Producer configuration for topic {topic} complete.')
            producer_topic_dict[topic] = producer
        if return_as_singular:
            if len(producer_topic_dict) == 1:
                return list(producer_topic_dict.values())[0]
    LOGGER.debug('Producer setup complete.')
    return producer_topic_dict


def produce_message(producer, producer_kwargs: dict, metrics_manager: MetricsManager = None,
                    consumed_msg_headers_passthrough=None):
    """
    Helper for producing a message with confluent_kafka producers; primarily handles headers passthrough and enforcing
    all required headers fields exist before producing.
    You can pass in the previous message headers via 'consumed_msg_headers_passthrough', which extracts the headers.
    Then, if you wish to overwrite any of them, you can provide your own "headers" keyword in 'producer_kwargs'
    which will take that dict and overwrite any matching key in the 'consumed_msg_headers_passthrough' argument.
    You can also provide a None value for a key to remove it entirely.
    :param producer: A confluent_kafka producer
    :type: confluent_kafka.Producer or confluent_kafka.avro.AvroProducer
    :param producer_kwargs: the kwargs to pass into the producer instance
    :type producer_kwargs: dict
    :param metrics_manager: a MetricsManager object instance
    :type metrics_manager: MetricsManager
    :param consumed_msg_headers_passthrough: confluent_kafka Message.headers() from a consumed msg; will add all to new message
    :type consumed_msg_headers_passthrough: list of tuples, or dict
    """
    required_fields = ['guid', 'last_updated_by']

    if 'header' in producer_kwargs:
        raise KeyError('"header" is not the appropriate key for producing message headers; use "headers" instead')

    headers_out = parse_headers(consumed_msg_headers_passthrough)
    headers_out.update(producer_kwargs.get('headers', {}))
    headers_out = {key: value for key, value in headers_out.items() if value is not None}
    missing_required_keys = [key for key in required_fields if key not in headers_out]
    if missing_required_keys:
        raise ProduceHeadersException(f'Message headers are missing the required key(s): {missing_required_keys}')
    producer_kwargs['headers'] = headers_out

    LOGGER.debug('Polling for previous successful produce callbacks before adding additional produces to queue...')
    producer.poll(0)

    # multi-producer management
    if "topic" not in producer_kwargs and hasattr(producer, 'topic'):
        producer_kwargs.update({'topic': producer.topic})
    if "partition" not in producer_kwargs:
        producer_kwargs.update({'partition': produce_partitioner(producer, producer_kwargs)})
    producer._value_serializer = producer.schema_dict[producer_kwargs['topic']]

    LOGGER.debug(f'Adding a message to the produce queue for topic,partition {producer_kwargs["topic"]}, p{producer_kwargs["partition"]} - key {repr(producer_kwargs["key"])}')
    producer.produce(**producer_kwargs)
    if metrics_manager:
        metrics_manager.inc_messages_produced(1, producer_kwargs['topic'])
    LOGGER.info(f'Message added to the produce queue; GUID {headers_out.get("guid")}')


def confirm_produce(producers, attempts=3, timeout=20):
    """
    Ensure that messages are actually produced by forcing synchronous processing. Must manually check the events queue
    and see if it's truly empty since flushing timeouts do not actually raise an exception for some reason.

    NOTE: Only used for synchronous producing, which is dramatically slower than asychnronous.
    """
    if isinstance(producers, dict):
        producers = producers.values()
    else:
        producers = [producers]
    for producer in producers:
        attempt = 1
        while producer.__len__() > 0:
            if attempt <= attempts:
                LOGGER.debug(f"Produce flush attempt: {attempt} of {attempts}")
                producer.flush(timeout=timeout)
                attempt += 1
            else:
                raise ProducerTimeoutFailure
