# runtime environment variables used by both confluent-kafka and faust implementations

from os import environ
from .env_var_generator import EnvVars


def default_env_vars():
    """
    Environment variables that have defaults if not specified.
    """

    return {
        'NU_LOGLEVEL': environ.get('NU_LOGLEVEL', 'INFO'),

        # Kafka Cluster
        'NU_KAFKA_CLUSTERS_CONFIGS_YAML': environ.get('NU_KAFKA_CLUSTERS_CONFIGS_YAML', '/opt/app-root/configmaps/nubium-clusters.yaml'),
        'NU_TOPIC_CONFIGS_YAML': environ.get('NU_TOPIC_CONFIGS_YAML', '/opt/app-root/configmaps/nubium-topics.yaml'),
        
        # Schema Registry
        'NU_SCHEMA_REGISTRY_USERNAME': environ.get('NU_SCHEMA_REGISTRY_USERNAME', ''),
        'NU_SCHEMA_REGISTRY_PASSWORD': environ.get('NU_SCHEMA_REGISTRY_PASSWORD', ''),

        # Metrics Manager
        'NU_DO_METRICS_PUSHING': environ.get('NU_DO_METRICS_PUSHING', 'true'),
        'NU_METRICS_PUSH_RATE': environ.get('NU_METRICS_PUSH_RATE', '10'),
        'NU_METRICS_SERVICE_NAME': environ.get('NU_METRICS_SERVICE_NAME', f'bifrost-metrics-cache-headless.{environ.get("NU_MP_PROJECT", "")}.svc.cluster.local'),
        'NU_METRICS_SERVICE_PORT': environ.get('NU_METRICS_SERVICE_PORT', '8080'),
        'NU_METRICS_POD_PORT': environ.get('NU_METRICS_POD_PORT', '9091'),
    }

def required_env_vars():
    """
    Environment variables that require a value (aka no default specified).
    """
    return {
        'NU_HOSTNAME': environ["NU_HOSTNAME"] if "NU_HOSTNAME" in environ else environ["HOSTNAME"],  # NOTE: Every Openshift pod has a UNIQUE default HOSTNAME (its own pod name).
        'NU_APP_NAME': environ['NU_APP_NAME'],
        'NU_MP_PROJECT': environ['NU_MP_PROJECT'],
        'NU_SCHEMA_REGISTRY_URL': environ['NU_SCHEMA_REGISTRY_URL'],
    }


def derived_env_vars():
    """
    Environment variables with logic surrounding how they are generated.
    """
    if default_env_vars().get('NU_SCHEMA_REGISTRY_USERNAME'):
        schema_registry_server = f"{environ['NU_SCHEMA_REGISTRY_USERNAME']}:{environ['NU_SCHEMA_REGISTRY_PASSWORD']}@{environ['NU_SCHEMA_REGISTRY_URL']}"
    else:
        schema_registry_server = f"{required_env_vars()['NU_SCHEMA_REGISTRY_URL']}"

    return {
        'NU_SCHEMA_REGISTRY_SERVER': schema_registry_server
    }


def all_env_vars():
    return {
        **default_env_vars(),
        **required_env_vars(),
        **derived_env_vars(),
    }


env_vars = EnvVars(all_env_vars)
