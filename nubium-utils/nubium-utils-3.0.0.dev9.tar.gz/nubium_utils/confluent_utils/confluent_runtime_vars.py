"""
confluent-kafka runtime environment variables
"""

from os import environ
from nubium_utils import general_runtime_vars
from nubium_utils.env_var_generator import EnvVars


def default_env_vars():
    """
    Environment variables that have defaults if not specified.
    """
    return {
        'NU_CONSUMER_POLL_TIMEOUT': environ.get('NU_CONSUMER_POLL_TIMEOUT', '8'),
        'NU_CONSUMER_TIMEOUT_LIMIT_MINUTES': environ.get('NU_CONSUMER_TIMEOUT_LIMIT_MINUTES', '2'),
        'NU_CONSUMER_AUTO_OFFSET_RESET': environ.get('NU_CONSUMER_AUTO_OFFSET_RESET', 'latest'),

        # "Retry" functionality ONLY
        'NU_CONSUME_TOPICS': environ.get('NU_CONSUME_TOPICS', ''),
        'NU_PRODUCE_SUCCESS_TOPICS': environ.get('NU_PRODUCE_SUCCESS_TOPICS', ''),
        'NU_PRODUCE_RETRY_TOPICS': environ.get('NU_PRODUCE_RETRY_TOPICS', ''),
        'NU_PRODUCE_FAILURE_TOPICS': environ.get('NU_PRODUCE_FAILURE_TOPICS', ''),
        'NU_RETRY_COUNT_MAX': environ.get('NU_RETRY_COUNT_MAX', '0'),
        'NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES': environ.get('NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES', '0'),

        # GtfoBatchApp
        'NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_COUNT': environ.get('NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_COUNT', '1'),
        'NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_TIME_SECONDS': environ.get('NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_TIME_SECONDS', '15'),
        
        # GtfoTableApp
        'NU_TABLE_PATH': environ.get('NU_TABLE_PATH', '/opt/app-root/data'),
        'NU_SKIP_TABLE_RECOVERY': environ.get('NU_SKIP_TABLE_RECOVERY', 'false'),

        # Performance
        'NU_CONSUMER_AUTO_COMMIT_INTERVAL_SECONDS': str(int(environ.get('NU_CONSUMER_AUTO_COMMIT_INTERVAL_SECONDS', '20'))*1000),
        'NU_CONSUMER_HEARTBEAT_TIMEOUT_SECONDS': str(environ.get('NU_CONSUMER_HEARTBEAT_TIMEOUT_SECONDS', '60')),
        'NU_CONSUMER_MESSAGE_BATCH_MAX_MB': str(int(float(environ.get('NU_CONSUMER_MESSAGE_BATCH_MAX_MB', '2')) * 2 ** 20)),
        'NU_CONSUMER_MESSAGE_TOTAL_MAX_MB': str(int(float(environ.get('NU_CONSUMER_MESSAGE_TOTAL_MAX_MB', '5')) * 2 ** 20)),
        'NU_CONSUMER_MESSAGE_QUEUE_MAX_MB': str(int(float(environ.get('NU_CONSUMER_MESSAGE_QUEUE_MAX_MB', '20')) * 2 ** 10)),
}


def required_env_vars():
    """
    Environment variables that require a value (aka no default specified).
    """
    return {}


def all_env_vars():
    return {
        **general_runtime_vars.all_env_vars(),
        **default_env_vars(),
        **required_env_vars()
    }


env_vars = EnvVars(all_env_vars)
