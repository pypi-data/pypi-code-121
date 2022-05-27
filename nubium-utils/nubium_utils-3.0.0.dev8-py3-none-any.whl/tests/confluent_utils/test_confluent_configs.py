import pytest
from unittest.mock import patch, MagicMock, call
import os
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.confluent_utils.confluent_configs import *

patch_path = 'nubium_utils.confluent_utils.confluent_configs'


def required_env_vars():
    return {
        "NU_LOGLEVEL": "DEBUG",
        "NU_HOSTNAME": "test-app-0",
        "NU_APP_NAME": "test_app",
        "NU_MP_PROJECT": "none",
        "NU_MP_CLUSTER": "none",
        "NU_DO_METRICS_PUSHING": "false",
        "NU_SCHEMA_REGISTRY_URL": "sr_url",
        "NU_SCHEMA_REGISTRY_USERNAME": "sr_un",
        "NU_SCHEMA_REGISTRY_PASSWORD": "sr_pw",
        "NU_TOPIC_CONFIGS_YAML": '{"test_topic_0": {"cluster": "cluster_0"}, "test_topic_1": {"cluster": "cluster_1"}}',
        "NU_KAFKA_CLUSTERS_CONFIGS_YAML": '{"cluster_0": {"url": "www", "username": "un", "password": "pw"}}',
    }


@pytest.fixture
def set_env_vars(request):
    """
    Allows you to set additional env vars per test, but requires an empty dict if you dont
    """
    evars = required_env_vars()
    evars.update(request.param)
    env_patch = patch.dict('os.environ', evars)
    env_patch.start()
    env_vars._reload()


class TestConfluentConfigs:
    # @pytest.mark.parametrize('patched_env_vars', [{'NU_KAFKA_CLUSTERS_CONFIGS_YAML': '{"cluster_0": {"url": "www", "username": "un", "password": "pw"}}'}], indirect=True)
    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_sasl_configs(self, set_env_vars):
        assert init_sasl_configs('cluster_0') == {
            "security.protocol": "sasl_ssl",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": 'un',
            "sasl.password": 'pw'
        }

    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_schema_registry_configs__auth(self, set_env_vars):
        assert init_schema_registry_configs() == {"schema.registry.url": "https://sr_un:sr_pw@sr_url"}

        with patch('nubium_utils.confluent_utils.confluent_configs.SchemaRegistryClient') as SRC:
            init_schema_registry_configs(as_registry_object=True)
            SRC.assert_called_with({"url": "https://sr_un:sr_pw@sr_url"})

    @pytest.mark.parametrize('set_env_vars', [{'NU_SCHEMA_REGISTRY_URL': 'localhost', 'NU_SCHEMA_REGISTRY_USERNAME': ''}], indirect=True)
    def test_init_schema_registry_configs__localhost(self, set_env_vars):
        assert init_schema_registry_configs() == {"schema.registry.url": "http://localhost"}
        with patch('nubium_utils.confluent_utils.confluent_configs.SchemaRegistryClient') as SRC:
            init_schema_registry_configs(as_registry_object=True)
            SRC.assert_called_with({"url": "http://localhost"})
    
    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_producer_configs(self, set_env_vars):
        schema_reg_obj = MagicMock()
        sasl_config = {'sasl': 'config'}
        with patch(f'{patch_path}.AvroSerializer') as AS:
            expected = {
                **sasl_config,
                "bootstrap.servers": "www",
                "on_delivery": produce_message_callback,
                "partitioner": "murmur2_random",
                "key.serializer": AS(schema_reg_obj, schema_str='{"type": "string"}'),
                "value.serializer": throwaway,
                "enable.idempotence": "true",
                "acks": "all"
            }
            
            assert init_producer_configs({'test_topic_0': 'schema'}, schema_reg_obj, sasl_config, 'cluster_0', False) == expected
            AS.assert_called_with(schema_reg_obj, schema_str='{"type": "string"}')

            # no cluster provided
            assert init_producer_configs({'test_topic_0': 'schema'}, schema_reg_obj, sasl_config, transactional=False) == expected
            AS.assert_called_with(schema_reg_obj, schema_str='{"type": "string"}')

    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_producer_configs__transactional(self, set_env_vars):
        schema_reg_obj = MagicMock()
        sasl_config = {'sasl': 'config'}
        with patch(f'{patch_path}.AvroSerializer') as AS:
            expected = {
                **sasl_config,
                "bootstrap.servers": "www",
                "on_delivery": produce_message_callback,
                "partitioner": "murmur2_random",
                "key.serializer": AS(schema_reg_obj, schema_str='{"type": "string"}'),
                "value.serializer": throwaway,
                "enable.idempotence": "true",
                "transaction.timeout.ms": 120000,
                "transactional.id": "test-app-0",
                "acks": "all"}

            assert init_producer_configs({'test_topic_0': 'schema'}, schema_reg_obj, sasl_config, 'cluster_0', True) == expected
            AS.assert_called_with(schema_reg_obj, schema_str='{"type": "string"}')
            
    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_producer_configs__bad_topic_dict(self, set_env_vars):
        schema_reg_obj = MagicMock()
        sasl_config = {'sasl': 'config'}
        with patch(f'{patch_path}.AvroSerializer') as AS:
            with pytest.raises(ValueError):
                init_producer_configs({'test_topic_0': 'schema', 'test_topic_1': 'schema'}, schema_reg_obj, sasl_config)

    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_transactional_consumer_configs(self, set_env_vars):
        schema_reg_obj = MagicMock()
        sasl_config = {'sasl': 'config'}

        with patch(f'{patch_path}.AvroDeserializer') as AD:
            expected = {
                **sasl_config,
                "bootstrap.servers": "www",
                "group.id": "test_app",
                "on_commit": consume_message_callback,
                "auto.offset.reset": 'latest',
                "isolation.level": "read_committed",
                "enable.auto.commit": False,
                "enable.auto.offset.store": False,
                "key.deserializer": AD(schema_reg_obj, schema_str='{"type": "string"}'),
                "value.deserializer": AD(schema_reg_obj, schema_str='{"schema": "schema"}'),
                "partition.assignment.strategy": 'cooperative-sticky',
                "max.poll.interval.ms": 60000 * (2+0),
                "session.timeout.ms": 1000 * 90,
                "message.max.bytes": 2 * (2 ** 20),
                "fetch.max.bytes": 3 * (2 ** 20),
                "queued.max.messages.kbytes": 10 * (2 ** 10),
            }

            assert init_transactional_consumer_configs(['test_topic_0'], schema_reg_obj, sasl_config, 'cluster_0', {"schema": "schema"}) == expected
            AD.assert_has_calls([call(schema_reg_obj, schema_str='{"type": "string"}'), call(schema_reg_obj, schema_str='{"schema": "schema"}')])

            # no cluster provided
            assert init_transactional_consumer_configs(['test_topic_0'], schema_reg_obj, sasl_config, schema={"schema": "schema"}) == expected
            AD.assert_has_calls([call(schema_reg_obj, schema_str='{"type": "string"}'), call(schema_reg_obj, schema_str='{"schema": "schema"}')])

    @pytest.mark.parametrize('set_env_vars', [{}], indirect=True)
    def test_init_transactional_consumer_configs__bad_topic_list(self, set_env_vars):
        schema_reg_obj = MagicMock()
        sasl_config = {'sasl': 'config'}
        with patch(f'{patch_path}.AvroDeserializer') as AD:
            with pytest.raises(ValueError):
                init_transactional_consumer_configs(['test_topic_0', 'test_topic_1'], schema_reg_obj, sasl_config)


if __name__ == '__main__':
    pytest.main([__file__])
