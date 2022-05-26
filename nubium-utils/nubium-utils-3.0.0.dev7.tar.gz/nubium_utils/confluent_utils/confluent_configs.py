import logging
from nubium_utils.metrics import start_pushing_metrics
from .confluent_runtime_vars import env_vars
from nubium_utils.yaml_parser import load_yaml_fp
from nubium_utils.custom_exceptions import WrappedSignals
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
import json


# fixes a bug in confluent-kafka TODO: keep a look out for this in >1.8.2, should be fixed since I took it from a MR.
def patched_schema_loads(schema_str):
    from confluent_kafka.schema_registry.avro import Schema
    schema_str = schema_str.strip()
    if schema_str[0] != "{" and schema_str[0] != "[":
        schema_str = '{"type":' + schema_str + '}'
    return Schema(schema_str, schema_type='AVRO')
import confluent_kafka
confluent_kafka.schema_registry.avro._schema_loads = patched_schema_loads


LOGGER = logging.getLogger(__name__)
wrapped_signals = WrappedSignals()  # WrappedSignals needs to be initialized (somewhere) to catch signals


def init_sasl_configs(cluster_name):
    cluster_configs = load_yaml_fp(env_vars()['NU_KAFKA_CLUSTERS_CONFIGS_YAML']).get(cluster_name, {})
    if cluster_configs.get('username'):
        LOGGER.info(f'Using SASL-authenticated producers/consumers for {cluster_name}!')
        return {
            "security.protocol": "sasl_ssl",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": cluster_configs['username'],
            "sasl.password": cluster_configs['password']
        }
    else:
        LOGGER.info(f'NO Authentication/encryption for producers/consumers in {cluster_name}!')
    return {}


def init_schema_registry_configs(as_registry_object=False):
    """
    Provides the avro schema config
    :return: dict, None
    """
    config = None
    if as_registry_object:
        url = 'url'
    else:
        url = 'schema.registry.url'
    LOGGER.info(f'Using the schema server at {env_vars()["NU_SCHEMA_REGISTRY_URL"]}')
    # RHOSAK registry
    if env_vars()['NU_SCHEMA_REGISTRY_USERNAME']:
        config = {url: f"https://{env_vars()['NU_SCHEMA_REGISTRY_SERVER']}"}
    else:  # local
        config = {url: f"http://{env_vars()['NU_SCHEMA_REGISTRY_SERVER']}"}

    if as_registry_object:
        return SchemaRegistryClient(config)
    else:
        return config
    

def throwaway():
    return None


def produce_message_callback(error, message):
    """
    Logs the returned message from the Broker after producing
    NOTE: Headers not supported on the message for callback for some reason.
    NOTE: Callback requires these args
    """
    LOGGER.debug('Producer Callback...')
    if error:
        LOGGER.critical(error)
    else:
        LOGGER.debug('Producer Callback - Message produced successfully')


def init_producer_configs(topic_schema_dict, schema_registry, sasl_configs=None, cluster_name=None, transactional=False):
    """
    Sets up a single producer.
    """
    if topic_schema_dict and not cluster_name:
        topic_cluster_map = load_yaml_fp(env_vars()['NU_TOPIC_CONFIGS_YAML'])
        check_topics = set([topic for topic in topic_schema_dict if topic in topic_cluster_map])
        unmapped = set(topic_schema_dict.keys()) - check_topics
        if unmapped:
            LOGGER.warning(f'The topic(s) {unmapped} in the provided producer schema dict mapping are not included in'
                           f' the cluster topic map. There are valid use cases for this, such as dynamically adding'
                           f' new topics at runtime with a predetermined schema, or even just testing a new topic on'
                           f' the fly. Either way, make sure this is not a mistake!')
        cluster_name = set([topic_cluster_map[topic]['cluster'] for topic in check_topics])
        if len(cluster_name) == 1:
            cluster_name = list(cluster_name)[0]
        else:
            raise ValueError('Cluster count for provided producer topics did not equal 1. '
                             f'These topics must be on the same cluster to init their configs. Topics:\n{check_topics}.')
    if not sasl_configs:
        sasl_configs = {}
    config = {
        **sasl_configs,
        "bootstrap.servers": load_yaml_fp(env_vars()['NU_KAFKA_CLUSTERS_CONFIGS_YAML'])[cluster_name]['url'],
        "on_delivery": produce_message_callback,
        "partitioner": "murmur2_random",
        "key.serializer": AvroSerializer(schema_registry, schema_str='{"type": "string"}'),
        "value.serializer": throwaway,
        "enable.idempotence": "true",
        "acks": "all"}
    if transactional: 
        config["transactional.id"] = env_vars()['NU_HOSTNAME']
        config["transaction.timeout.ms"] = (int(env_vars()['NU_CONSUMER_TIMEOUT_LIMIT_MINUTES']) + int(env_vars()['NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES'])) * 60000
    LOGGER.debug(f"Producer config: {json.dumps({k:v for k,v in config.items() if 'sasl' not in k and isinstance(v, str)}, indent=4)}")
    return config


def consume_message_callback(error, partitions):
    """
    Logs the info returned when a successful commit is performed
    NOTE: Callback requires these args
    """
    LOGGER.debug('Consumer Callback...')
    if error:
        LOGGER.critical(error)
    else:
        LOGGER.debug('Consumer Callback - Message consumption committed successfully')


def init_transactional_consumer_configs(topics, schema_registry, sasl_configs=None, cluster_name=None, schema=None):
    """
    Assumes topics are all in the same cluster.
    """
    if not cluster_name:
        topic_configs = load_yaml_fp(env_vars()['NU_TOPIC_CONFIGS_YAML'])
        cluster_name = set([topic_configs[topic]['cluster'] for topic in topics])
        if len(cluster_name) == 1:
            cluster_name = list(cluster_name)[0]
        else:
            raise ValueError('Cluster count for provided consumer topics did not equal 1. '
                             f'Please confirm your topics are on the same cluster. Topics:\n{topics}')
    if not sasl_configs:
        sasl_configs = {}
    max_time_between_consumes_mins = int(env_vars()['NU_CONSUMER_TIMEOUT_LIMIT_MINUTES']) + int(env_vars()['NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES'])
    schema = json.dumps(schema) if schema else None
    config = {
        # Connection Settings
        **sasl_configs,
        "bootstrap.servers": load_yaml_fp(env_vars()['NU_KAFKA_CLUSTERS_CONFIGS_YAML'])[cluster_name]['url'],

        # General Consumer Settings
        "group.id": env_vars()['NU_APP_NAME'],
        "on_commit": consume_message_callback,
        "auto.offset.reset": env_vars()['NU_CONSUMER_AUTO_OFFSET_RESET'],

        # Transaction Settings
        "isolation.level": "read_committed",
        "enable.auto.commit": False,
        "enable.auto.offset.store": False,

        # Registry Serialization Settings
        "key.deserializer": AvroDeserializer(schema_registry, schema_str='{"type": "string"}'),
        "value.deserializer": AvroDeserializer(schema_registry, schema_str=schema),

        # Performance Settings
        "partition.assignment.strategy": 'cooperative-sticky',
        "max.poll.interval.ms": 60000 * max_time_between_consumes_mins,
        "session.timeout.ms": int(env_vars()['NU_CONSUMER_HEARTBEAT_TIMEOUT_SECONDS']) * 1000,
        "message.max.bytes": int(env_vars()['NU_CONSUMER_MESSAGE_BATCH_MAX_MB']),
        "fetch.max.bytes": int(env_vars()['NU_CONSUMER_MESSAGE_TOTAL_MAX_MB']),
        "queued.max.messages.kbytes": int(env_vars()['NU_CONSUMER_MESSAGE_QUEUE_MAX_MB']),
    }
    LOGGER.debug(f"Consumer config: {json.dumps({k:v for k,v in config.items() if 'sasl' not in k and isinstance(v, str)}, indent=4)}")
    return config


def init_metrics_pushing(metrics_manager):
    if env_vars()['NU_DO_METRICS_PUSHING'].lower() == 'true':
        LOGGER.info('Metric pushing to gateway ENABLED')
        start_pushing_metrics(metrics_manager, int(env_vars()['NU_METRICS_PUSH_RATE']))
    else:
        LOGGER.info('Metric pushing to gateway DISABLED')


def get_kafka_configs(cluster_name):
    return init_sasl_configs(cluster_name), init_schema_registry_configs()
