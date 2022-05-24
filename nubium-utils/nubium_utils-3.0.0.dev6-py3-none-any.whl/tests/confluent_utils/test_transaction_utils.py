import pytest
from unittest.mock import patch, MagicMock, call
import os
from nubium_utils.confluent_utils.transaction_utils import *

patch_path = 'nubium_utils.confluent_utils.transaction_utils'


@pytest.fixture
def cluster_name():
    return "cluster_0"


@pytest.fixture
def test_topic():
    return "test_topic_0"


@pytest.fixture
def topic_schema_dict(test_topic):
    return {test_topic: {"type": "string"}}


@pytest.fixture
def topic_configs_yaml(cluster_name, test_topic):
    # can be a json as well
    return str({test_topic: {"cluster": cluster_name}, "test_topic_1": {"cluster": cluster_name}})


@pytest.fixture
def cluster_configs_yaml(cluster_name):
    return str({cluster_name: {"url": "www", "username": "un", "password": "pw"}})


@pytest.fixture
def health_filepath(tmp_path_factory):
    return tmp_path_factory.mktemp('health')


@pytest.fixture
def required_env_vars(topic_configs_yaml, cluster_configs_yaml):
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
        "NU_TOPIC_CONFIGS_YAML": topic_configs_yaml,
        "NU_KAFKA_CLUSTERS_CONFIGS_YAML": cluster_configs_yaml,
        "NU_CONSUMER_POLL_TIMEOUT": "5",
        "NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES": "1"
    }


@pytest.fixture(autouse=True)
def set_env_vars(required_env_vars):
    evars = required_env_vars
    env_patch = patch.dict('os.environ', evars)
    env_patch.start()
    env_vars._reload()


class MockTransaction(Transaction):
    def __init__(self, **kwargs):
        kwargs_out = dict(producer=MagicMock(), consumer=MagicMock(), message=MagicMock(), metrics_manager=MagicMock())
        kwargs_out.update(**kwargs)
        super().__init__(**kwargs_out)


class MockGtfoApp(GtfoApp):
    def __init__(self, **kwargs):
        kwargs_out = dict(
            app_function=MagicMock(), consume_topics_list=['test_topic_0'], produce_topic_schema_dict={"test_topic_1": {"type": "string"}}, transaction_type=MockTransaction,
            app_function_arglist=['arg_a', 'arg_b'], metrics_manager=MagicMock(), schema_registry=MagicMock(), cluster_name=None, consumer=MagicMock(), producer=MagicMock())
        kwargs_out.update(**kwargs)
        super().__init__(**kwargs_out)


class TestTransaction:
    def test_original_message_functions(self):
        transaction = MockTransaction()
        transaction.key()
        transaction.message.key.assert_called()
        transaction.value()
        transaction.message.value.assert_called()
        transaction.topic()
        transaction.message.topic.assert_called()
        transaction.partition()
        transaction.message.partition.assert_called()
        transaction.offset()
        transaction.message.offset.assert_called()
        
    def test_headers(self):
        transaction = MockTransaction()
        with patch(f'{patch_path}.parse_headers') as patch_head:
            transaction.headers()
            transaction.message.headers.assert_called()
            patch_head.assert_called_with(transaction.message.headers())

    def test_auto_consume(self):
        with patch.object(MockTransaction, 'consume') as patch_consume:
            MockTransaction()
            patch_consume.assert_not_called()

            MockTransaction(auto_consume=False, message=None)
            patch_consume.assert_not_called()

            MockTransaction(message=None)
            patch_consume.assert_called()

    def test_messages(self):
        transaction = MockTransaction()
        assert transaction.messages() == transaction.message

    def test__init_transaction(self):
        transaction = MockTransaction()
        transaction._init_transaction()
        transaction.producer.begin_transaction.assert_called()
        assert transaction._active_transaction

        transaction = MockTransaction()
        transaction._active_transaction = True
        transaction.producer.begin_transaction.assert_not_called()

        transaction = MockTransaction()
        transaction._committed = True
        transaction.producer.begin_transaction.assert_not_called()

    def test_produce(self):
        transaction = MockTransaction()
        with patch.object(MockTransaction, '_init_transaction') as patch_trans:
            with patch(f'{patch_path}.parse_headers') as patch_head:
                patch_head.return_value = {'header': 'value'}
                with patch(f'{patch_path}.produce_message') as patch_produce:
                    transaction.produce({"test_key": "test_value"})
                    patch_produce.assert_called_with(transaction.producer, {"test_key": "test_value"}, transaction.metrics_manager, {'header': 'value'})
                patch_head.assert_called()
            patch_trans.assert_called()
        transaction.producer.poll.assert_has_calls([call(0), call(0)])

    def test_commit(self):
        with patch(f'{patch_path}.TopicPartition') as TP:
            with patch.object(MockTransaction, 'offset') as offset:
                offset.return_value = 2
                transaction = MockTransaction()
                transaction.commit()
                transaction.producer.send_offsets_to_transaction.assert_called_with([TP(transaction.topic(), transaction.partition(), transaction.offset() + 1)], transaction.consumer.consumer_group_metadata())
                transaction.producer.commit_transaction.assert_called()
                transaction.producer.poll.assert_called_with(0)
                assert transaction._committed
                assert not transaction._active_transaction

    def test_commit__dont_mark_committed(self):
        with patch(f'{patch_path}.TopicPartition') as TP:
            with patch.object(MockTransaction, 'offset') as offset:
                offset.return_value = 2
                transaction = MockTransaction()
                transaction.commit(mark_committed=False)
                transaction.producer.send_offsets_to_transaction.assert_called_with([TP(transaction.topic(), transaction.partition(), transaction.offset() + 1)], transaction.consumer.consumer_group_metadata())
                transaction.producer.commit_transaction.assert_called()
                transaction.producer.poll.assert_called_with(0)
                assert not transaction._committed
                assert transaction._active_transaction

    def test_commit__no_commit(self):
        transaction = MockTransaction()
        transaction._active_transaction = True
        transaction._committed = True
        # just confirm the first function in the block is not called cuz i'm lazy
        transaction.producer.send_offsets_to_transaction.assert_not_called()


class TestGtfoApp:

    def test__get_cluster_name(self, test_topic, cluster_name):
        gtfo_app = MockGtfoApp()
        assert gtfo_app._get_cluster_name([test_topic]) == cluster_name

    def test__get_transactional_producer(self, test_topic, topic_schema_dict, cluster_name):
        schema_reg_obj = MagicMock()
        producer_expected = MagicMock()
        gtfo_app = MockGtfoApp(schema_registry=schema_reg_obj)
        with patch(f'{patch_path}.get_producers') as mock_producer:
            mock_producer.return_value = producer_expected
            producer_actual = gtfo_app._get_transactional_producer(topic_schema_dict, schema_reg_obj, cluster_name)
            producer_actual.init_transactions.assert_called()
            assert producer_expected == producer_actual

    def test__get_transactional_consumer(self, test_topic, cluster_name):
        schema_reg_obj = MagicMock()
        gtfo_app = MockGtfoApp(schema_registry=schema_reg_obj)
        mock_consumer_configs = {'group.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.DeserializingConsumer') as DC:
            consumer = MagicMock()
            DC.side_effect = [consumer]
            consumer_expected = consumer
            with patch(f'{patch_path}.init_transactional_consumer_configs') as consumer_configs:
                consumer_configs.return_value = mock_consumer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    consumer_actual = gtfo_app._get_transactional_consumer([test_topic], schema_reg_obj, cluster_name)
                    kafka_configs.assert_has_calls([call(cluster_name)])
                consumer_configs.assert_has_calls([call([test_topic], schema_reg_obj, mock_kafka_configs, cluster_name, None)])
            DC.assert_has_calls([call(mock_consumer_configs)])
            consumer_actual.subscribe.assert_has_calls([call([test_topic])])
        assert consumer_expected == consumer_actual

    def test__get_transactional_consumer__no_auto_subscribe(self, test_topic, cluster_name):
        schema_reg_obj = MagicMock()
        gtfo_app = MockGtfoApp(schema_registry=schema_reg_obj)
        mock_consumer_configs = {'group.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.DeserializingConsumer') as DC:
            consumer = MagicMock()
            DC.side_effect = [consumer]
            consumer_expected = consumer
            with patch(f'{patch_path}.init_transactional_consumer_configs') as consumer_configs:
                consumer_configs.return_value = mock_consumer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    consumer_actual = gtfo_app._get_transactional_consumer([test_topic], schema_reg_obj, cluster_name, auto_subscribe=False)
                    kafka_configs.assert_has_calls([call(cluster_name)])
                consumer_configs.assert_has_calls([call([test_topic], schema_reg_obj, mock_kafka_configs, cluster_name, None)])
            DC.assert_has_calls([call(mock_consumer_configs)])
            consumer_actual.subscribe.assert_not_called()
        assert consumer_expected == consumer_actual

    def test__get_transactional_consumer__default_schema(self, test_topic, cluster_name, topic_schema_dict):
        schema_reg_obj = MagicMock()
        gtfo_app = MockGtfoApp(schema_registry=schema_reg_obj)
        mock_consumer_configs = {'group.id': 'id'}
        mock_kafka_configs = {'bootstrap.servers': 'url'}
        with patch(f'{patch_path}.DeserializingConsumer') as DC:
            consumer = MagicMock()
            DC.side_effect = [consumer]
            consumer_expected = consumer
            with patch(f'{patch_path}.init_transactional_consumer_configs') as consumer_configs:
                consumer_configs.return_value = mock_consumer_configs
                with patch(f'{patch_path}.get_kafka_configs') as kafka_configs:
                    kafka_configs.return_value = (mock_kafka_configs, 'blah')
                    consumer_actual = gtfo_app._get_transactional_consumer([test_topic], schema_reg_obj, cluster_name, default_schema=topic_schema_dict)
                    kafka_configs.assert_has_calls([call(cluster_name)])
                consumer_configs.assert_has_calls([call([test_topic], schema_reg_obj, mock_kafka_configs, cluster_name, topic_schema_dict)])
            DC.assert_has_calls([call(mock_consumer_configs)])
            consumer_actual.subscribe.assert_has_calls([call([test_topic])])
        assert consumer_expected == consumer_actual

    def test_consume(self):
        gtfo_app = MockGtfoApp()
        with patch.object(gtfo_app, 'transaction_type') as mock_type:
            mock_type.return_value = 'transaction_obj'
            assert gtfo_app.consume("my_arg", kwargs={"mykwargs": "kwarg"}) == 'transaction_obj'
            assert gtfo_app.transaction == 'transaction_obj'
            mock_type.assert_called_with(gtfo_app.producer, gtfo_app.consumer, "my_arg", metrics_manager=gtfo_app.metrics_manager, timeout=10, kwargs={"mykwargs": "kwarg"})

    def test__app_run_loop(self):
        gtfo_app = MockGtfoApp()
        mock_transaction = MockTransaction()
        gtfo_app.transaction = mock_transaction
        with patch.object(mock_transaction, 'commit') as mock_commit:
            with patch.object(gtfo_app, 'consume') as mock_consume:
                gtfo_app._app_run_loop("my_arg", kwargs={"mykwargs": "kwarg"})
                mock_consume.assert_called_with("my_arg", kwargs={"mykwargs": "kwarg"})
                gtfo_app.app_function.assert_called_with(gtfo_app.transaction, *gtfo_app.app_function_arglist)
            mock_commit.assert_called()

    def test__app_run_loop__no_message(self):
        gtfo_app = MockGtfoApp()
        mock_transaction = MockTransaction()
        gtfo_app.transaction = mock_transaction
        with patch.object(mock_transaction, 'commit') as mock_commit:
            with patch.object(gtfo_app, 'consume') as mock_consume:
                mock_consume.side_effect = NoMessageError
                gtfo_app._app_run_loop("my_arg", kwargs={"mykwargs": "kwarg"})
                mock_consume.assert_called_with("my_arg", kwargs={"mykwargs": "kwarg"})
                gtfo_app.app_function.assert_not_called()
            mock_commit.assert_not_called()
        gtfo_app.producer.poll.assert_called()

    def test__app_run_loop__any_nonhandled_error(self):
        gtfo_app = MockGtfoApp()
        mock_transaction = MockTransaction()
        gtfo_app.transaction = mock_transaction
        with patch.object(mock_transaction, 'commit') as mock_commit:
            with patch.object(gtfo_app, 'consume') as mock_consume:
                mock_consume.side_effect = Exception("Uh Oh!")
                with pytest.raises(Exception):
                    gtfo_app._app_run_loop("my_arg", kwargs={"mykwargs": "kwarg"})
                mock_consume.assert_called_with("my_arg", kwargs={"mykwargs": "kwarg"})
                gtfo_app.app_function.assert_not_called()
            mock_commit.assert_not_called()
        gtfo_app.producer.poll.assert_not_called()

    def test_kafka_cleanup(self):
        gtfo_app = MockGtfoApp()
        with patch(f'{patch_path}.shutdown_cleanup') as cleanup:
            gtfo_app.kafka_cleanup()
            cleanup.assert_called_with(consumer=gtfo_app.consumer)

    def test__app_shutdown(self):
        gtfo_app = MockGtfoApp()
        mock_transaction = MockTransaction()
        gtfo_app.transaction = mock_transaction
        with patch.object(gtfo_app, 'kafka_cleanup') as cleanup:
            gtfo_app._app_shutdown()
            gtfo_app.producer.abort_transaction.assert_not_called()
            cleanup.assert_called()

    def test__app_shutdown__abort(self):
        gtfo_app = MockGtfoApp()
        mock_transaction = MockTransaction()
        mock_transaction._active_transaction = True
        gtfo_app.transaction = mock_transaction
        with patch.object(gtfo_app, 'kafka_cleanup') as cleanup:
            gtfo_app._app_shutdown()
            gtfo_app.producer.abort_transaction.assert_called_with(10)
            cleanup.assert_called()

    def test_run__signalraise(self, health_filepath):
        with patch.object(MockGtfoApp, '_app_run_loop') as mock_loop:
            mock_loop.side_effect = SignalRaise(9)
            with patch.object(MockGtfoApp, '_app_shutdown') as mock_shutdown:
                gtfo_app = MockGtfoApp()
                with patch(f'{patch_path}.log_and_raise_error') as mock_log:
                    gtfo_app.run(health_fp=health_filepath)
                    mock_log.assert_not_called()
                    mock_shutdown.assert_called()

    def test_run__exception(self, health_filepath):
        with patch.object(MockGtfoApp, '_app_run_loop') as mock_loop:
            mock_loop.side_effect = Exception
            with patch.object(MockGtfoApp, '_app_shutdown') as mock_shutdown:
                gtfo_app = MockGtfoApp()
                with patch(f'{patch_path}.log_and_raise_error') as mock_log:
                    gtfo_app.run(health_fp=health_filepath)
                    mock_log.assert_called()
                    mock_shutdown.assert_called()


if __name__ == '__main__':
    pytest.main([__file__])
