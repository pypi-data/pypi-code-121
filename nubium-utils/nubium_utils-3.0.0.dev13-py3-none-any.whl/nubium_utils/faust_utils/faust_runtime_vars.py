"""
runtime environment variables used by both confluent-kafka and faust implementations
"""

from os import environ
from nubium_utils import general_runtime_vars
from nubium_utils.env_var_generator import env_vars_creator


def default_env_vars():
    """
    Environment variables that have defaults if not specified.
    """
    return {
        'FAUST_DATADIR_BASE': environ.get('FAUST_DATADIR_BASE', '/opt/app-root/data/'),
        'USE_ROCKSDB': environ.get('USE_ROCKSDB', 'true'),
        'KIWF_ERROR_STRINGS': environ.get('KIWF_ERROR_STRINGS', 'StaleMetadata,COMMIT OFFSET NOT ADVANCING'),
        'KIWF_LOG_FILEPATH': environ.get('KIWF_LOG_FILEPATH', '/opt/app-root/log/faust-log-file.log'),

        # faust direct runtime configs
        'TOPIC_REPLICATION_FACTOR': environ.get('TOPIC_REPLICATION_FACTOR', '3'),
        'TOPIC_PARTITIONS': environ.get('TOPIC_PARTITIONS', ''),
        'CONSUMER_AUTO_OFFSET_RESET': environ.get('CONSUMER_AUTO_OFFSET_RESET', 'latest'),
        'STREAM_RECOVERY_DELAY': environ.get('STREAM_RECOVERY_DELAY', '10'),
        'PROCESSING_GUARANTEE': environ.get('PROCESSING_GUARANTEE', 'exactly_once'),
        'F_BLOCKING_TIMEOUT': environ.get('F_BLOCKING_TIMEOUT', '30.0'),
        'F_FORCE_BLOCKING_TIMEOUT': environ.get('F_FORCE_BLOCKING_TIMEOUT', '1'),
        'BROKER_MAX_POLL_RECORDS': environ.get('BROKER_MAX_POLL_RECORDS', '10'),
    }


def required_env_vars():
    """
    Environment variables that require a value (aka no default specified).
    """
    return {
        # faust direct runtime configs
        'BROKER_TOPIC_NAME': environ['BROKER_TOPIC_NAME']
    }


def all_env_vars():
    return {
        **general_runtime_vars.all_env_vars(),
        **default_env_vars(),
        **required_env_vars()
    }


env_vars = env_vars_creator(all_env_vars)
