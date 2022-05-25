import pytest
from unittest.mock import patch, MagicMock, call
import os
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.confluent_utils.producer_utils import *
from copy import deepcopy


patch_path = 'nubium_utils.confluent_utils.producer_utils'


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
        "NU_CONSUMER_POLL_TIMEOUT": "5",
        "NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES": "1"
    }


@pytest.fixture(autouse=True)
def set_env_vars():
    evars = required_env_vars()
    env_patch = patch.dict('os.environ', evars)
    env_patch.start()
    env_vars._reload()


@pytest.fixture()
def topic_schema_dict():
    return {'test_topic_1': {"type": "string"}, 'test_topic_2': {"type": "string"}, 'test_topic_3': None}


@pytest.fixture()
def producer_serializer():
    return MagicMock()


@pytest.fixture()
def producer(producer_serializer):
    producer = MagicMock()
    producer.schema_dict = {'test_topic_1': producer_serializer}
    return producer


class TestProducerUtils:
    def test_producer_serializers(self, topic_schema_dict):
        schema_reg_object = MagicMock()
        with patch(f'{patch_path}.AvroSerializer') as AS:
            serializer1, serializer2 = MagicMock(), MagicMock()
            AS.side_effect = [serializer1, serializer2]
            assert producer_serializers(topic_schema_dict, schema_reg_object) == {'test_topic_1': serializer1, 'test_topic_2': serializer2}
            AS.assert_has_calls([call(schema_reg_object, '{"type": "string"}'), call(schema_reg_object, '{"type": "string"}')])

    def test_get_producers(self, topic_schema_dict):
        schema_reg_obj = MagicMock()
        cluster_name = 'test_cluster'
        mock_producer_configs = {'producer.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.SerializingProducer') as SP:
            producer1, producer2, producer3 = MagicMock(), MagicMock(), MagicMock()
            SP.side_effect = [producer1, producer2, producer3]
            with patch(f'{patch_path}.init_producer_configs') as producer_configs:
                producer_configs.return_value = mock_producer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    with patch(f'{patch_path}.producer_serializers') as serializer:
                        sdict1, sdict2, sdict3 = {'test_topic_1': MagicMock()}, {'test_topic_2': MagicMock()}, {'test_topic_2': MagicMock()}
                        serializer.side_effect = [sdict1, sdict2, sdict3]
                        expected = {'test_topic_1': producer1, 'test_topic_2': producer2, 'test_topic_3': producer3}
                        result = get_producers(topic_schema_dict, cluster_name, schema_reg_obj)
                        serializer.assert_has_calls(
                            [call({'test_topic_1': {"type": "string"}}, schema_reg_obj),
                             call({'test_topic_2': {"type": "string"}}, schema_reg_obj),
                             call({'test_topic_3': None}, schema_reg_obj)])
                    kafka_configs.assert_has_calls([
                        call(cluster_name),
                        call(cluster_name),
                        call(cluster_name)])
                producer_configs.assert_has_calls([
                    call({'test_topic_1': {"type": "string"}}, schema_reg_obj, mock_kafka_configs, cluster_name, False),
                    call({'test_topic_2': {"type": "string"}}, schema_reg_obj, mock_kafka_configs, cluster_name, False),
                    call({'test_topic_3': None}, schema_reg_obj, mock_kafka_configs, cluster_name, False)])
            SP.assert_has_calls([
                call(mock_producer_configs),
                call(mock_producer_configs),
                call(mock_producer_configs)])
        assert expected == result
        assert result['test_topic_1'] == producer1
        assert result['test_topic_2'] == producer2
        assert result['test_topic_3'] == producer3
        assert producer1.topic == 'test_topic_1'
        assert producer1.schema_dict == sdict1
        assert producer2.topic == 'test_topic_2'
        assert producer2.schema_dict == sdict2
        assert producer3.topic == 'test_topic_3'
        assert producer3.schema_dict == sdict3

    def test_get_producers__singular(self):
        topic_schema_dict = {'test_topic_1': {"type": "string"}}
        schema_reg_obj = MagicMock()
        cluster_name = 'test_cluster'
        mock_producer_configs = {'producer.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.SerializingProducer') as SP:
            producer1 = MagicMock()
            SP.side_effect = [producer1]
            with patch(f'{patch_path}.init_producer_configs') as producer_configs:
                producer_configs.return_value = mock_producer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    with patch(f'{patch_path}.producer_serializers') as serializer:
                        sdict1 = {'test_topic_1': MagicMock()}
                        serializer.side_effect = [sdict1]
                        expected = producer1
                        result = get_producers(topic_schema_dict, cluster_name, schema_reg_obj)
                        serializer.assert_has_calls([call({'test_topic_1': {"type": "string"}}, schema_reg_obj)])
                    kafka_configs.assert_has_calls([call(cluster_name)])
                producer_configs.assert_has_calls([call({'test_topic_1': {"type": "string"}}, schema_reg_obj, mock_kafka_configs, cluster_name, False)])
            SP.assert_has_calls([call(mock_producer_configs)])
        assert expected == result
        assert producer1.topic == 'test_topic_1'
        assert producer1.schema_dict == sdict1

    def test_get_producers__transactional(self):
        topic_schema_dict = {'test_topic_1': {"type": "string"}, 'test_topic_2': {"type": "string"}}
        schema_reg_obj = MagicMock()
        cluster_name = 'test_cluster'
        mock_producer_configs = {'producer.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.SerializingProducer') as SP:
            producer1, producer2, producer3 = MagicMock(), MagicMock(), MagicMock()
            SP.side_effect = [producer1]
            with patch(f'{patch_path}.init_producer_configs') as producer_configs:
                producer_configs.return_value = mock_producer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    with patch(f'{patch_path}.producer_serializers') as serializer:
                        sdict1 = {'test_topic_1': MagicMock()}
                        serializer.side_effect = [sdict1]
                        expected = producer1
                        result = get_producers(topic_schema_dict, cluster_name, schema_reg_obj, transactional=True)
                        serializer.assert_has_calls([call({'test_topic_1': {"type": "string"}, 'test_topic_2': {"type": "string"}}, schema_reg_obj)])
                    kafka_configs.assert_has_calls([call(cluster_name)])
                producer_configs.assert_has_calls([call({'test_topic_1': {"type": "string"}, 'test_topic_2': {"type": "string"}}, schema_reg_obj, mock_kafka_configs, cluster_name, True)])
            SP.assert_has_calls([call(mock_producer_configs)])
        assert expected == result
        assert producer1.schema_dict == sdict1

    def test_get_producers__as_singular_false(self):
        topic_schema_dict = {'test_topic_1': {"type": "string"}}
        schema_reg_obj = MagicMock()
        cluster_name = 'test_cluster'
        mock_producer_configs = {'producer.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.SerializingProducer') as SP:
            producer1, producer2, producer3 = MagicMock(), MagicMock(), MagicMock()
            SP.side_effect = [producer1]
            with patch(f'{patch_path}.init_producer_configs') as producer_configs:
                producer_configs.return_value = mock_producer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    with patch(f'{patch_path}.producer_serializers') as serializer:
                        sdict1 = {'test_topic_1': MagicMock()}
                        serializer.side_effect = [sdict1]
                        expected = {'test_topic_1': producer1}
                        result = get_producers(topic_schema_dict, cluster_name, schema_reg_obj, return_as_singular=False)
                        serializer.assert_has_calls([call({'test_topic_1': {"type": "string"}}, schema_reg_obj)])
                    kafka_configs.assert_has_calls([call(cluster_name)])
                producer_configs.assert_has_calls([call({'test_topic_1': {"type": "string"}}, schema_reg_obj, mock_kafka_configs, cluster_name, False)])
            SP.assert_has_calls([call(mock_producer_configs)])
        assert expected == result
        assert result['test_topic_1'] == producer1
        assert producer1.topic == 'test_topic_1'
        assert producer1.schema_dict == sdict1

    def test_produce_message__with_metric_manager(self, producer, producer_serializer):
        """
        Happy path, check that header passthrough gets the header kw arg updates
        """
        metrics_manager = MagicMock()
        test_input = [
            producer,
            dict(topic='test_topic_1',
                 key='blah_key',
                 value={'blah_value': 'blah_value'},
                 headers={'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}),
            metrics_manager,
            [('guid', b'112233'), ('last_updated_by', b'eloqua')]]
        produce_message(*test_input)
        assert producer._value_serializer == producer_serializer
        metrics_manager.inc_messages_produced.assert_called_with(1, 'test_topic_1')
        producer.produce.assert_called_with(
            **dict(
                topic='test_topic_1',
                key='blah_key',
                value={'blah_value': 'blah_value'},
                headers={'guid': '112233', 'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}))

    def test_produce_message__dict_header_passthrough(self, producer, producer_serializer):
        """
        Happy path, check that header passthrough gets the header kw arg updates
        """
        test_input = [
            producer,
            dict(topic='test_topic_1',
                 key='blah_key',
                 value={'blah_value': 'blah_value'},
                 headers={'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}),
            None,
            {'guid': '112233', 'last_updated_by': 'eloqua'}]
        produce_message(*test_input)
        assert producer._value_serializer == producer_serializer
        producer.produce.assert_called_with(
            **dict(
                topic='test_topic_1',
                key='blah_key',
                value={'blah_value': 'blah_value'},
                headers={'guid': '112233', 'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}))

    def test_produce_message__has_topic_attribute(self, producer, producer_serializer):
        producer.topic = 'test_topic_1'
        test_input = [
            producer,
            dict(key='blah_key',
                 value={'blah_value': 'blah_value'},
                 headers={'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}),
            None,
            [('guid', b'112233'), ('last_updated_by', b'eloqua')]]
        produce_message(*test_input)
        assert producer._value_serializer == producer_serializer
        producer.produce.assert_called_with(
            **dict(
                topic='test_topic_1',
                key='blah_key',
                value={'blah_value': 'blah_value'},
                headers={'guid': '112233', 'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}))

    def test_produce_message__bad_headers(self, producer, producer_serializer):
        test_input = [
            producer,
            dict(
                key='blah_key',
                value={'blah_value': 'blah_value'},
                header={'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}),
            None,
            [('guid', b'112233'), ('last_updated_by', b'eloqua')]]
        with pytest.raises(KeyError):
            produce_message(*test_input)

        test_input = [
            producer,
            dict(
                key='blah_key',
                value={'blah_value': 'blah_value'},
                headers={'last_updated_by': 'sfdc', 'new_header_key': 'new_header_value'}),
            None,
            [('last_updated_by', b'eloqua')]]
        with pytest.raises(ProduceHeadersException):
            produce_message(*test_input)
            
    def test_confirm_produce(self, producer):
        producer.__len__.side_effect = [2, 1, 0]
        confirm_produce(producers=producer)
        producer.flush.assert_has_calls([call(timeout=20)]*2)

        producer.__len__.side_effect = [4, 3, 2, 1, 0]
        with pytest.raises(ProducerTimeoutFailure):
            confirm_produce(producers=producer)

    def test_confirm_produce__multi(self, producer):
        producer2 = deepcopy(producer)
        producer.__len__.side_effect = [2, 1, 0, 2, 1, 0]
        confirm_produce(producers={'test_topic_1': producer, 'test_topic_2': producer2})
        producer.flush.assert_has_calls([call(timeout=20)]*2)
        producer2.flush.assert_has_calls([call(timeout=20)]*2)


if __name__ == '__main__':
    pytest.main([__file__])
