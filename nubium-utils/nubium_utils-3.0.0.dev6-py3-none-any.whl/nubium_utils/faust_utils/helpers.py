import ssl
import logging
from logging.handlers import RotatingFileHandler
from .faust_runtime_vars import env_vars
from faust import SASLCredentials
from nubium_topic_configs.clusters import cluster_topic_map
from nubium_topic_configs.topics import primary_topics

LOGGER = logging.getLogger(__name__)


def get_ssl_context():
    """
    Constructs SASL context based on environment variables
    """
    if env_vars()["RHOSAK_USERNAME"]:
        LOGGER.info('Using SASL-authenticated producers/consumers!')
        return {
            'broker_credentials': SASLCredentials(
                username=env_vars()['RHOSAK_USERNAME'],
                password=env_vars()['RHOSAK_PASSWORD'],
                ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH))
        }
    else:
        LOGGER.info('Authentication/encryption disabled for producers/consumers!')
        return {}


def get_data_store():
    try:
        store = env_vars()['STORE']
    except KeyError:
        if env_vars()['USE_ROCKSDB'].lower() == 'true':
            store = 'rocksdb://'
        else:
            store = 'memory://'
    return {'store': store}


def get_file_logging_handler():
    if env_vars()['KIWF_LOG_FILEPATH']:
        handler = RotatingFileHandler(env_vars()['KIWF_LOG_FILEPATH'], maxBytes=100000, backupCount=1)
        handler.setLevel(env_vars()['LOGLEVEL'])
        handler.setFormatter(logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'))
        return {'loghandlers': [handler]}
    return {}


def get_config():
    """
    Maps environment variables to Faust app config dictionary
    Any environ.get config options are generally considered optional and generaly default to .
    :return: Faust configs
    :rtype: dict
    """
    broker_timeout = int(env_vars()['CONSUMER_HEARTBEAT_TIMEOUT_SECONDS'])
    config = {
        'id': env_vars()['APP_NAME'],
        'broker': cluster_topic_map()[env_vars()['BROKER_TOPIC_NAME']],
        'topic_partitions': int(env_vars()['TOPIC_PARTITIONS']) if env_vars()['TOPIC_PARTITIONS'] else primary_topics[env_vars()['BROKER_TOPIC_NAME'].replace("__TEST", "")].partitions,
        'topic_replication_factor': int(env_vars()['TOPIC_REPLICATION_FACTOR']),
        'processing_guarantee': env_vars()['PROCESSING_GUARANTEE'],
        'stream_recovery_delay': int(env_vars()['STREAM_RECOVERY_DELAY']),
        'consumer_auto_offset_reset': env_vars()['CONSUMER_AUTO_OFFSET_RESET'],
        'broker_max_poll_records': int(env_vars()['BROKER_MAX_POLL_RECORDS']),
        'broker_session_timeout': broker_timeout,
        'broker_request_timeout': broker_timeout * 2,
        'datadir': f"{env_vars()['FAUST_DATADIR_BASE']}/{env_vars()['HOSTNAME']}/"
    }

    config.update(get_data_store())
    config.update(get_ssl_context())
    config.update(get_file_logging_handler())
    return config
